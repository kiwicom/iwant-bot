import asyncio
from aiohttp import web
from os import getenv
import re
import time
from iwant_bot.slack_communicator import SlackCommunicator
from iwant_bot.iwant_parser import IwantParser


VERIFICATION = getenv('VERIFICATION')
if VERIFICATION is None:
    print('Warning: Unknown "Verification Token".')

BOT_TOKEN = getenv('BOT_TOKEN')
if BOT_TOKEN is None:
    print('Warning: Unknown BOT_TOKEN "Bot User OAuth Access Token".')
elif not re.match('xoxb', BOT_TOKEN):
    print('Warning: "Bot User OAuth Access Token" does not begin with "xoxb".')

SUPER_TOKEN = getenv('SUPER_TOKEN')
if SUPER_TOKEN is None:
    print('Warning: Unknown SUPER_TOKEN "OAuth Access Token".')
elif not re.match('xoxp', SUPER_TOKEN):
    print('Warning: "OAuth Access Token" does not begin with "xoxp".')


_commands = ('/iwant', )
_iwant_activities = ('coffee', )
_iwant_behest = ('list', 'subscribe', 'unsubscribe')


class TokenError(Exception):
    pass


async def handle_get(request):
    """Handle GET request, can be display at http://localhost:8080"""
    text = (f'Server is running at {request.url}.\n'
            f'Try `curl -X POST --data "text=test" {request.url}example`\n')
    return web.Response(text=text)


async def handle_other_posts(request):
    """Handle all other POST requests.
    For testing purpose, `curl -X POST --data "text=test" http://localhost:8080/example`"""
    body = multidict_to_dict(await request.post())
    print(body)
    print(request.match_info['post'])
    return web.json_response({'text': f"POST to /{request.match_info['post']} is not resolved."})


def multidict_to_dict(multidict) -> dict:
    if not len(set(multidict.keys())) == len(multidict):
        print('WARNING: MultiDict contains duplicate keys, last occurrence was used.')
        print(multidict)
    return {key: multidict[key] for key in multidict}


async def handle_slack_iwant(request):
    body = multidict_to_dict(await request.post())
    body['incoming_ts'] = time.time()
    print(body)

    try:
        verify_request_token(body)
    except (KeyError, TokenError) as err:
        print(f'INFO: Invalid token: {err}')
        return web.json_response({'text': 'Unverified message.'})

    if 'command' in body:
        if body['command'] == '/iwant':
            iwant_object = IwantParser(body, _iwant_activities, _iwant_behest)
        else:
            print(f"WARNING: iwant handler handles command '{body['command']}'")
            return web.json_response({'text': 'Something went wrong.'})
    else:
        print("WARNING: Request does not specify 'command'.")
        return web.json_response({'text': 'Something went wrong.'})

    print(iwant_object.data)

    # Check and process the behests
    if len(iwant_object.data['behests']) > 1:
        return web.json_response({'text': "You can use only one at the same time from:\n"
                                          f" {', '.join(_iwant_behest)}"})
    elif len(iwant_object.data['behests']) == 1:
        # list
        if iwant_object.data['behests'][0] == 'list':
            return web.json_response(iwant_object.return_list_of_parameters())
        # other behests
        else:
            return web.json_response({'text': f"{iwant_object.data['behests'][0]}"
                                              " is not implemented yet. Coming soon!"})

    # If no behest, then check and process the activities
    if len(iwant_object.data['activities']) == 0:
        return web.json_response(iwant_help_message())
    elif len(iwant_object.data['activities']) > 0:
        # send to the logic and storage:
        if iwant_object.create_iwant_task():    # produce callback_id
            return web.json_response(iwant_object.create_accepted_response())
        else:
            print('WARNING: Something went wrong between the storage and server.')
            return web.json_response({'text': 'Server problem. Please, try it again.'})

    # If no condition were met, than something is not implemented.
    print('WARNING: /iwant command did nothing.')
    return web.json_response({'text': 'Nothing happened.'})


def verify_request_token(body: dict) -> None:
    """Raise KeyError, if body does not have any key 'token'.
    Raise TokenError, if token does not match."""
    if not body['token'] == VERIFICATION:
        raise TokenError(f"Token {body['token']} is not valid.")


def iwant_help_message() -> dict:
    """Create help message for /iwant command.
    Called by empty command "/iwant" or when no activity is recognized."""
    text = ('This is `/iwant` help.\n'
            'Use `/iwant activity` to let me know, what you want to do.'
            ' I will find someone, who will join you!\n'
            'You can get the list of available activities by `\iwant list`.\n'
            'Some examples:\n'
            '  `/iwant coffee`\n'
            '  `/iwant coffee in 35 min with @alex`'
            ' (I will notify @alex, but everyone can join.)\n'
            'Also, you can be always informed about some activity:\n'
            '`\iwant (un)subscribe table_football`'
            )
    return {'text': text}


app = web.Application()
app.router.add_get(r'/{get:\w*}', handle_get)
app.router.add_post('/slack/iwant', handle_slack_iwant)
app.router.add_post(r'/{post:[\w/]*}', handle_other_posts)

loop = asyncio.get_event_loop()

# Created channel iwant_group10 - id: G65FE8M6K.
# (1..9 were created and archived, but still cannot be recreate and I cannot delete them.)
# So, we should not create to many channels?

# test = SlackCommunicator(SUPER_TOKEN, 'U51RKKATS', 'Create channel')
# loop.run_until_complete(asyncio.gather(test.create_private_channel('iwant_group11'),
#                                        test.invite_people_in_private_channel())
#                         )


# sent_message_to_each can send message even to channels and users
# test1 = SlackCommunicator(BOT_TOKEN, 'G64LXGDPC', 'Message 42.')
# loop.run_until_complete(test1.send_message_to_each())


# sent message to multiparty group of max 7 people + 1 iwant-bot. Does not need SUPER_TOKEN.
# So, this is preferable variant...

test2 = SlackCommunicator(BOT_TOKEN, ['U51RKKATS', 'U52FUHD98', 'U52FU3ZTL'], 'Sorry spam :).')
loop.run_until_complete(test2.send_message_to_multiparty())


if __name__ == '__main__':
    web.run_app(app)

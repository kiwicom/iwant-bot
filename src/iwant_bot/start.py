import asyncio
from aiohttp import web
from os import getenv
import re
import time
import json
from iwant_bot.slack_communicator import SlackCommunicator
from iwant_bot.iwant_process import IwantRequest


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


_iwant_activities = ('coffee', )
_iwant_behest = ('list', 'help')
# other_words are expected words in the user message, which should be removed before dateparse.
_other_words = ('iwant', 'with', 'invite', 'or', 'and')  # uppercase will be problem.
_default_duration = 900.0  # Implicit duration of activity in seconds (15 min).
_max_duration = 43200.0  # 12 hours is maximal duration of any request.
# Expect expanded Slack format like <@U1234|user> <#C1234|general>.
# Turn on 'Escape channels, users, and links sent to your app'.
_slack_user_pattern = '<@([A-Z0-9]+)\|[a-z0-9][-_.a-z0-9]{1,20}>'


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
    print(f"INFO: The post to endpoint /{request.match_info['post']} contained:\n {body}")
    return web.json_response({'text': f"POST to /{request.match_info['post']} is not resolved."})


def multidict_to_dict(multidict) -> dict:
    if not len(set(multidict.keys())) == len(multidict):
        print('WARNING: MultiDict contains duplicate keys, last occurrence was used.')
        print(multidict)
    return {key: multidict[key] for key in multidict}


async def handle_slack_button(request):
    payload = multidict_to_dict(await request.post())
    body = json.loads(payload['payload'])
    print(f'INFO: Button request body:\n{body}.')

    try:
        verify_request_token(body)
    except (KeyError, TokenError) as err:
        print(f'INFO: Invalid token: {err}')
        return web.json_response({'text': 'Unverified message.'})

    if body['actions'][0]['name'] == 'Cancel':
        if 'text' not in body:
            body['text'] = ''
        if 'user_id' not in body:
            body['user_id'] = body['user']['id']
        iwant_object = IwantRequest(body, (), (), _slack_user_pattern)
        iwant_object.cancel_iwant_task()

    return web.json_response({'text': 'Request was cancelled.'})


async def handle_slack_iwant(request):
    body = multidict_to_dict(await request.post())
    body['incoming_ts'] = time.time()
    print(f'INFO: iwant request body:\n{body}.')

    try:
        verify_request_token(body)
    except (KeyError, TokenError) as err:
        print(f'INFO: Invalid token: {err}')
        return web.json_response({'text': 'Unverified message.'})

    if 'command' in body:
        print(f"INFO: iwant handler handles command '{body['command']}'")
    else:
        print("WARNING: Request does not specify 'command'.")
        return web.json_response({'text': 'Tried to handle command, but none found.'})

    iwant_object = IwantRequest(body, _iwant_activities, _iwant_behest, _slack_user_pattern,
                                _other_words, _default_duration, _max_duration)
    print(f'INFO: iwant parsed request:\n{iwant_object.data}')

    # Process behests
    res = solve_iwant_behest(iwant_object)
    if res is not None:
        return web.json_response(res)

    # If no behest, then resolve activities
    return web.json_response(solve_iwant_activity(iwant_object))


def complain(what: str, iwant_object) -> dict:
    print(f'INFO: More than 1 {what} was found.')
    if what == 'behest':
        listing = f"`{'`, `'.join(iwant_object.possible_behests)}`"
    elif what == 'activity':
        listing = f"`{'`, `'.join(iwant_object.possible_activities)}`"
    else:
        print(f'WARNING: Someone complain to "{what}", but unknown meaning.')
        return {'text': 'You cannot want this.'}

    return {'text': f'You can use only one {what} from {listing} at the same time.'}


def solve_iwant_behest(iwant_object) -> dict or None:
    if len(iwant_object.data['behests']) == 1:
        print(f"INFO: iwant request found behest '{iwant_object.data['behests'][0]}'.")
        if iwant_object.data['behests'] == ['list']:
            return iwant_object.return_list_of_parameters()
        elif iwant_object.data['behests'] == ['help']:
            return iwant_object.create_help_message()
        # other behests
        else:
            return {'text': f"{iwant_object.data['behests'][0]} is not implemented yet."}

    elif len(iwant_object.data['behests']) > 1:
        return complain('behest', iwant_object)

    else:
        return None


def solve_iwant_activity(iwant_object) -> dict:
    if len(iwant_object.data['activities']) == 1:
        print(f'INFO: iwant request found activities {iwant_object.data["activities"][0]}.')

        try:
            callback_id = iwant_object.store_iwant_task(iwant_object.data["activities"][0])
            iwant_object.data['callback_id'] = callback_id
        except Exception as e:
            print(f'ERROR: "{iwant_object.data["activities"][0]}" did not get callback_id.')
            print(e)

        print(f"INFO: iwant request obtained callback_id {iwant_object.data['callback_id']}")
        return iwant_object.create_accepted_response()

    elif len(iwant_object.data['activities']) > 1:
        return complain('activity', iwant_object)

    else:
        print('INFO: No activities or behests, return help.')
        return iwant_object.create_help_message()


def verify_request_token(body: dict) -> None:
    """Raise KeyError, if body does not have any key 'token'.
    Raise TokenError, if token does not match."""
    if not body['token'] == VERIFICATION:
        raise TokenError(f"Token {body['token']} is not valid.")


app = web.Application()
app.router.add_get(r'/{get:\w*}', handle_get)
app.router.add_post('/slack/iwant', handle_slack_iwant)
app.router.add_post('/slack/button', handle_slack_button)
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
test1 = SlackCommunicator(BOT_TOKEN, 'U52FUHD98', 'Initial message.')
loop.run_until_complete(test1.send_message_to_each())


# sent message to multiparty group of 2 to 7 people (+ 1 iwant-bot). Need BOT_TOKEN.
# So, this is preferable variant...

# test2 = SlackCommunicator(BOT_TOKEN, ['U51RKKATS', 'U52FUHD98', 'U52FU3ZTL'], 'Sorry spam :).')
# loop.run_until_complete(test2.send_message_to_multiparty())

if __name__ == '__main__':
    web.run_app(app)

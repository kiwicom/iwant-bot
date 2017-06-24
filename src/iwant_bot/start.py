import asyncio
from aiohttp import web
import json
from os import getenv
from re import match
from aioslacker import Slacker

VERIFICATION = getenv('VERIFICATION')
if VERIFICATION is None:
    print('Warning: Unknown "Verification Token".')

BOT_TOKEN = getenv('BOT_TOKEN')
if BOT_TOKEN is None:
    print('Warning: Unknown "Bot User OAuth Access Token".')
elif not match('xoxb', BOT_TOKEN):
    print('Warning: "Bot User OAuth Access Token" does not begin with "xoxb".')

_commands = ('/iwant', '/iwant1')


def format_message(message):
    return f"'{message.text}' by '{message.nickname}' at {message.when}"


async def handle(request):
    name = request.rel_url.query.get('name', 'anonymous')
    message = request.rel_url.query.get('msg', '')

    text = ["We recognize the 'name' and 'msg' GET query attributes,"]
    text += ['so you can do http://localhost:8080/?name=me&msg=message']
    text += [f'Now, we got: {format_message(message)} by {name}']
    text += ['Or you can test POST request by command:']
    text += ['> curl -X POST  --data "user_name=0&channel_id=1&channel_name=2']
    text += ['  team_domain=4&team_id=5&text=6" http://localhost:8080']
    return web.Response(text='\n'.join(text))


def format_response(message='No response.'):
    return json.dumps({'text': message})


def verify_post_request(token):
    """Slack `/commands` carry token, which must be same as VERIFICATION"""
    return token == VERIFICATION


def body_to_dict(body):
    """Try to convert MultiDictProxy to dictionary.
    Not handled ValueError"""
    keys = set(body.keys())
    if len(keys) == len(body):
        body_dict = {}
        for key in keys:
            body_dict[key] = body[key]
    else:
        raise ValueError('MultiDict contains same keys.')
    return body_dict


def trigger_reaction(body, trigger):
    """Commands: /iwant,
    Trigger_words: None"""
    message = format_response(
        f"{body['user_name']} used {body[trigger]} with {body['text']}.")
    return web.json_response(body=message)


async def handle_post(request):
    body = body_to_dict(await request.post())
    print(body)

    if verify_post_request(body['token']):  # error if not 'token'
        """Separation of cases like /iwant commands, responses, etc."""

        triggers = ['command', 'trigger_word']  # stops with the first match
        for key in triggers:
            if key in body:
                return trigger_reaction(body, key)
            else:
                print(f'{key} not found.')
        else:
            message = format_response(f"I don't get it, try {_commands}.")
    else:
        message = format_response('Bad token, we do not listen to you!')

    return web.json_response(body=message)


async def initial_message():
    """ This sends message to the Slack. The message need to carry
    the token BOT_TOKEN for verification by Slack."""
    async with Slacker(BOT_TOKEN) as slack:
        await slack.chat.post_message('#bot-channel',
                                      'Hi, iwant-bot server was initialized')

app = web.Application()
app.router.add_get('/', handle)
app.router.add_post('/', handle_post)

# This sends the initial message to the Slack
loop = asyncio.get_event_loop()
loop.run_until_complete(initial_message())

if __name__ == '__main__':
    web.run_app(app)

import asyncio
from aiohttp import web
from iwant_bot import db
import json
from os import getenv
import re
import time
from dateparser import parse
from datetime import datetime
from aioslacker import Slacker

DB_ACCESS = None

VERIFICATION = getenv('VERIFICATION')
if VERIFICATION is None:
    print('Warning: Unknown "Verification Token".')

BOT_TOKEN = getenv('BOT_TOKEN')
if BOT_TOKEN is None:
    print('Warning: Unknown "Bot User OAuth Access Token".')
elif not re.match('xoxb', BOT_TOKEN):
    print('Warning: "Bot User OAuth Access Token" does not begin with "xoxb".')

_commands = ('/iwant', '/iwant1')
_iwant_activities = ('coffee',)
_duration = 900.0   # Implicit duration of activity in seconds.

class TokenError(Exception):
    pass

def add_numbers(a, b):
    return a + b


def format_message(message):
    return f"'{message.text}' by '{message.nickname}' at {message.when}"


async def handle(request):
    name = request.rel_url.query.get('name', 'anonymous')
    message = request.rel_url.query.get('msg', '')
    DB_ACCESS.save_message(message, name)

    messages_we_got_so_far = DB_ACCESS.load_n_last_messages()
    text = ["We recognize the 'name' and 'msg' GET query attributes,"]
    text += ['so you can do http://localhost:8080/?name=me&msg=message']
    text += ['We got these entries so far:\n']
    text += ['Or you can test POST request by command:']
    text += ['> curl -X POST  --data "user_name=0&channel_id=1&channel_name=2']
    text += ['  team_domain=4&team_id=5&text=6" http://localhost:8080']
    text.extend([format_message(msg) for msg in messages_we_got_so_far])
    return web.Response(text='\n'.join(text))


async def handle_button(request):
    pass



async def handle_iwant(request):
    body = body_to_dict(await request.post())
    body['incoming_ts'] = time.time()
    print(body)

    # Token verification, None or Exception.
    try:
        verify_request_token(body)
    except (KeyError, TokenError) as err:
        print(f'Invalid token: {err}')
        return web.json_response(body=format_response('Invalid token.'))

    # Command iwant do... recognize activity and set its duration.
    # invite WIP
    any_request = iwant_activity(body)

    # Return iwant help, when no activity was selected.
    if any_request:
        return web.json_response(body=format_response('Got it!'))
    else:
        return web.json_response(body=format_response(iwant_help_message()))


def iwant_activity(body: dict) -> bool:
    """Search the text for activities.
    Suppose a lot of assumptions...
    ...nobody with the name @coffee, activity 'invite' etc."""
    any_activity = False
    for activity in _iwant_activities:
        if re.search(activity, body['text'].lower()):
            any_activity = True
            create_iwant_request(body, activity, iwant_duration(body['text']))

    return any_activity

def iwant_duration(text: str) -> float:
    """Remove commands, activities, and invited people.
    Only text with time should leave (and some preposition).
    :return: duration of activity in seconds."""
    activities = '|'.join(_iwant_activities)    # Variable is used in pattern.
    text_time = re.sub(f'(/iwant\w*|{activities}|invite\w*|@\w+)', '', text)
    now_plus_duration = parse(text_time)
    if now_plus_duration is None:
        return _duration  # Implicit value
    else:
        return max((now_plus_duration - datetime.now()).total_seconds(), 1.0)



# asyncio?
def create_iwant_request(body: dict, activity: str, duration: float):
    """Create and pass on request to business logic"""
    print(activity)
    print(body)
    print(duration)


async def handle_post(request):
    """Handle incoming (general) POSTs request from Slack.
    Verify token and parse the commands.
    Likely will become obsolete."""
    body = body_to_dict(await request.post())
    print(body)

    try:
        verify_request_token(body)
    except (KeyError, TokenError) as err:
        print(f'Invalid token: {err}')
        return web.json_response(body=format_response('Invalid token.'))

    # The cause of the request. Take the first match.
    cause = ['command', 'actions', 'trigger_word']
    for key in cause:
        if key in body:
            return trigger_reaction(body, key)

    # Nothing match to the request.
    print(body)
    return format_response('Unknown request.')


def trigger_reaction(body, trigger):
    """Commands: /iwant,
    Trigger_words: None"""
    message = format_response(
        f"{body['user_name']} used {body[trigger]} with {body['text']}.")
    return web.json_response(body=message)


def format_response(message='No response.') -> str:
    return json.dumps({'text': message})


def verify_request_token(body: dict) -> None:
    """Raise KeyError, if body does not have any 'token'.
    Raise TokenError, if token does not match."""
    if body['token'] == VERIFICATION:
        return None
    else:
        raise TokenError(f"Token {body['token']} is not valid.")


def body_to_dict(body):
    """Try to convert MultiDictProxy to dictionary.
    Not handled ValueError."""
    keys = set(body.keys())
    if len(keys) == len(body):
        body_dict = {}
        for key in keys:
            body_dict[key] = body[key]
    else:
        raise ValueError('Slack POST contains same keys.')
    return body_dict





# async def initial_message():
#     """ This sends message to the Slack. The message need to carry
#     the token BOT_TOKEN for verification by Slack."""
#     async with Slacker(BOT_TOKEN) as slack:
        # button = [
        #     {'text': 'Testing ok button',
        #      "callback_id": "test11", 'actions': [
        #             {'name': 'test', 'text': 'ok', 'type': 'button', 'value': 1},
        #             {'name': 'test', 'text': 'no', 'type': 'button', 'value': 0}
        #         ]
        #     },
        #     {'text': 'Test 2 "ok button"',
        #      "callback_id": "test22", 'actions': [
        #         {'name': 'test', 'text': 'OK', 'type': 'button', 'value': 1},
        #         {'name': 'test', 'text': 'NO', 'type': 'button', 'value': 0}
        #     ]
        #     }
        # ]
        # print(json.dumps(button))
        # await slack.chat.post_message('#bot-channel',
        #                               'Hi, iwant-bot server was initialized',
        #                               attachments=json.dumps(button))
        # await slack.chat.post_message('#bot-channel',
        #                               iwant_help_message())

def iwant_help_message() -> str:
    """Create help message response for /iwant command.
    Called by empty command "/iwant".
    Evoked when activity is not recognized "/iwant nonsense"."""
    message = ('This is a `/iwant` help.\n'
               'Use `/iwant` with `activity`, which you want to share with '
               'anyone during a next few minutes. '
               'The activities are `%s`.\nExamples:\n'
               '`/iwant coffee`\n'
               '`/iwant coffee and invite @alex`\n'
               '`/iwant coffee in 15 min @alex @betty`\n'
               )
    return message % ('`, `'.join(_iwant_activities))


app = web.Application()
app.router.add_get('/', handle)
app.router.add_post('/', handle_post)
app.router.add_post('/iwant', handle_iwant)
app.router.add_post('/button', handle_button)

DB_ACCESS = db.DatabaseAccess()

# This sends the initial message to the Slack
# loop = asyncio.get_event_loop()
# loop.run_until_complete(initial_message())

if __name__ == '__main__':
    web.run_app(app)

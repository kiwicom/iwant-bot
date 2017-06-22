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
from slacker import Slacker as Slack

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
_iwant_activities = ('coffee', 'snack')
_duration = 900.0   # Implicit duration of activity in seconds.
_duration_max = 43200   # 12 hours is maximal duration of any request.
_callback_id = 1111     # testing random number


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
    payload = body_to_dict(await request.post())
    #print(payload)
    body = json.loads(payload['payload'])
    actions = body['actions']
    print(actions)

    if actions[0]['name'] == 'Invite' and actions[0]['type'] == 'button' and actions[0]['value'] != '0':
        # upgrade and/or create request with previous `callback_id`
        upgrade_iwant_request(body['callback_id'])
        return web.json_response(body=format_response(f"Add request: {actions[0]['value']}"))
    elif actions[0]['name'] == 'Invite' and actions[0]['type'] == 'button' and actions[0]['value'] == '0':
        return web.json_response(body=format_response(f"Invitation was rejected."))
    elif actions[0]['name'] == 'Time' and actions[0]['type'] == 'button':
        for i in (body['callback_id']):
            upgrade_iwant_request(body['callback_id'])
            print(f"change duration of request to {actions[0]['value']}")
        return web.json_response(body=format_response(
            f"Duration of activity was set to {actions[0]['value']} seconds"))
    else:
        return web.json_response(body=format_response(f"Unknown action."))


def upgrade_iwant_request(callback_id):
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
        time_minutes = round((body['duration_ts'] - body['incoming_ts']) / 60)
        return web.json_response(iwant_duration_buttons(body))
          # body=format_response(
          #   "text": f"{', '.join(body['activity'])}! I am looking for someone for {time_minutes} minutes."
          #    "attachments":json.dumps(iwant_duration_buttons(body))
          # )
       # )

    else:
        return web.json_response(body=format_response(iwant_help_message()))


def iwant_duration_buttons(body):
    """Create message with buttons to adjust request duration"""
    time_minutes = round((body['duration_ts'] - body['incoming_ts']) / 60)
    text = f"{', '.join(body['activity'])}! I am looking for someone for {time_minutes} minutes."
    attachment = [
        {
            'text': 'Would you like to change the duration to:',
            'callback_id': f"{body['callback_id']}",
            'fallback': 'Never mind.',
            #'color' : '#3AA3E3',
            'attachment_type': 'default',
            'actions': [
                {
                    'name': 'Time',
                    'text': '30 min',
                    'type': 'button',
                    'value': '1800'
                },
                {
                    'name': 'Time',
                    'text': '1 hour',
                    'type': 'button',
                    'value': '3600'
                },
                {
                    'name': 'Time',
                    'text': 'Cancel',
                    'type': 'button',
                    'value': '0'
                }
            ]
        }
    ]
    return {'text': text, 'attachments': attachment}



def iwant_activity(body: dict) -> bool:
    """Search the text for activities.
    Suppose a lot of assumptions...
    ...nobody with the name @coffee, activity 'invite' etc."""
    any_activity = False
    body['activity'] = []
    body['callback_id'] = []
    for activity in _iwant_activities:
        if re.search(activity, body['text'].lower()):
            any_activity = True
            body['duration_ts'] = body['incoming_ts'] + iwant_duration(body['text'])
            body['activity'].append(activity)
            body['callback_id'].append(create_iwant_request(body))
            iwant_invite(body)
    return any_activity


def iwant_duration(text: str) -> float:
    """Remove commands, activities, and invited people.
    Only text with time should leave (and some preposition).
    :return: duration of activity in seconds."""
    activities = '|'.join(_iwant_activities)    # Variable is used in pattern.
    text_time = re.sub(f'({activities}|@[a-z0-9][-_.a-z0-9]{{1,20}}|with|or|and|[.!?]\s*$)', '', text)
    print(text_time)
    now_plus_duration = parse(text_time)  #zlobi... odmazat .,; a jine symboly, napsat testy.
    print(now_plus_duration)
    if now_plus_duration is None:
        return _duration  # Implicit value
    else:
        # minimal valid time is 1s and maximal is _duration_max seconds
        return min(max((now_plus_duration - datetime.now()).total_seconds(), 1.0), _duration_max)


def iwant_invite(body: dict):
    """Send notification to mentioned people, that someone wants to do something collectively."""
    slack = Slack(BOT_TOKEN)
    user_names = get_users(slack)
    for name in user_names:
        if re.search(f'@*{name[0]}', body['text']):
            (text, attachment) = iwant_create_invitation(body, name[0], name[1])
            slack.chat.post_message(channel=f'@{name[0]}',
                                    text=text,
                                    attachments=json.dumps(attachment))


def iwant_create_invitation(body, name, name_id):
    """Create message with buttons (accept or reject) for someone,
    who was invited to join to some activity."""
    time_minutes = round((body['duration_ts'] - body['incoming_ts']) / 60)
    text = (f"Hi, @{body['user_name']} invites you to join "
            f"{body['activity'][-1]} in {time_minutes} minutes.")
    attachment = [
        {
            'text': 'Will you join?',
            'callback_id': f"{body['callback_id'][-1]}",
            'fallback': 'You do not want to join.',
            #'color' : '#3AA3E3',
            'attachment_type': 'default',
            'actions': [
                {
                    'name': 'Invite',
                    'text': 'Accept',
                    'type': 'button',
                    'value': f"{name} {name_id} {body['activity'][-1]} in {time_minutes} minutes."
                },
                {
                    'name': 'Invite',
                    'text': 'Reject',
                    'type': 'button',
                    'value': '0'
                }
            ]
        }
    ]
    return (text, attachment)


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



def get_users(slack):
    user_list = []
    for user in slack.users.list().body['members']:
        user_list.append((user['name'], user['id']))
    return user_list


# asyncio?
def create_iwant_request(body: dict) -> str:
    """Create and pass on request to business logic"""
    global _callback_id
    for activity in body['activity']:
            print(activity)
    print(body['incoming_ts'], body['duration_ts'])
    _callback_id += 1
    return _callback_id  # Storage ID of the request


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





async def initial_message():
    """ This sends message to the Slack. The message need to carry
    the token BOT_TOKEN for verification by Slack."""
    async with Slacker(BOT_TOKEN) as slack:
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
        # print(1)
        # slack = Slacker(BOT_TOKEN)
        test = await slack.users.list()
        for i in test.body['members']:
            print(i['name'], i['id'])


def iwant_help_message() -> str:
    """Create help message response for /iwant command.
    Called by empty command "/iwant".
    Evoked when activity is not recognized "/iwant nonsense"."""
    message = ('This is a `/iwant` help.\n'
               'Use `/iwant` with `activity`, which you want to share with '
               'anyone during a next few minutes. '
               'The activities are `%s`.\nExamples:\n'
               '`/iwant coffee`\n'
               '`/iwant snack in 1h 12m @alex`\n'
               '`/iwant coffee and snack in 15 min with @alex and @betty`\n'
               )
    return message % ('`, `'.join(_iwant_activities))


app = web.Application()
app.router.add_get('/', handle)
app.router.add_post('/', handle_post)
app.router.add_post('/slack/iwant', handle_iwant)
app.router.add_post('/slack/button', handle_button)

DB_ACCESS = db.DatabaseAccess()

# This sends the initial message to the Slack
loop = asyncio.get_event_loop()
loop.run_until_complete(initial_message())

if __name__ == '__main__':
    web.run_app(app)

from aiohttp import web
from iwant_bot import db
import json

DB_ACCESS = None


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
    text += ['  &service_id=3&']
    text += ['  team_domain=4&team_id=5&text=6" http://localhost:8080']
    text.extend([format_message(msg) for msg in messages_we_got_so_far])
    return web.Response(text='\n'.join(text))


def format_response(message='No response.'):
    return json.dumps({'text': message})


def verify_post_request(token):
    """Compare the token with the slack bot private token."""
    # compare tokens with '...?' Error or true/false.
    if token:
        return True
    else:
        return False


def body_to_dict(body):
    """Try to convert MultiDictProxy to dictionary.
    Not handled ValueError"""
    keys = set(body.keys())
    if len(keys) == len(body):
        body_dict = {}
        for key in keys:
            body_dict[key] = body[key]
    else:
        raise ValueError("MultiDict contains same keys.")
    return body_dict


def trigger_reaction(body, trigger):
    """Commands: /iwant,
    Trigger_words: None"""
    return web.json_response(body=format_response(
        f"{body['user_name']} used {trigger} {body[trigger]} with {body['text']}."))


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
                print(key + " not found.")
        else:
            return web.json_response(body=format_response("I don't get it, try commands like /iwant."))

    else:
        return web.json_response(body=format_response("iwant-bot does not listen to you!"))


app = web.Application()
app.router.add_get('/', handle)
app.router.add_post('/', handle_post)
DB_ACCESS = db.DatabaseAccess()


if __name__ == '__main__':
    web.run_app(app)

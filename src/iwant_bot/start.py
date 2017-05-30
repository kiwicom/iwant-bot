from aiohttp import web

from iwant_bot import db
#import slacker

DB_ACCESS = None


def add_numbers(a, b):
    return a + b


def format_message(message):
   ret = f"'{message.text}' by '{message.nickname}' at {message.when}"
   return ret


async def handle(request):
    name = request.rel_url.query.get('name', 'anonymous')
    message = request.rel_url.query.get('msg', '')
    DB_ACCESS.save_message(message, name)

    messages_we_got_so_far = DB_ACCESS.load_n_last_messages()
    text = ["We recognize the 'name' and 'msg' GET query attributes,"]
    text += ['so you can do http://localhost:8080/?name=me&msg=message']
    text += ['We got these entries so far:\n']
    text += ['Or you can test POST request by command:']
    text += ['> curl -X POST  --data "user_name=0&channel_id=1&channel_name=2&service_id=3&']
    text += ['  team_domain=4&team_id=5&text=6&timestamp=7&token=9&user_id=9" http://localhost:8080']
             #curl -X POST some_url_like_https://kiwislackbot1.localtunnel.me/\n']
    text.extend([format_message(msg) for msg in messages_we_got_so_far])
    return web.Response(text='\n'.join(text))

def format_response(message="No response."):
    ret = f'{{\n\t"text":"{message}"\n}}\n'
    return ret

def check_post_request(body):
    '''The structure of POST is given by Slack.
    https://api.slack.com/custom-integrations/outgoing-webhooks
    However, "trigger_word" is opional.'''

    expected_fields = {"token", "team_id", "team_domain", "service_id", "channel_id",
                       "channel_name", "timestamp", "user_id", "user_name", "text"}
    obtined_fields = set(body.keys())

    if (expected_fields - obtined_fields):
        print('POST missing these fields: ' + ', '.join(expected_fields - obtined_fields))
        return False

    return True



async def handle_post(request):
    body = await request.post()
    print(body)
    # test of POST body structure
    if check_post_request(body):
        token =         body["token"]
        team_id =       body["team_id"]
        team_domain =   body["team_domain"]
        service_id =    body["service_id"]
        channel_id =    body["channel_id"]
        channel_name =  body["channel_name"]
        timestamp =     body["timestamp"]
        user_id =       body["user_id"]
        user_name =     body["user_name"]
        text =          body["text"]
        try:
            trigger_word = body["trigger_word"]
        except KeyError:
            print("No trigger_word was used.")
            trigger_word = None
    else:
        return web.Response(text='No valid Slack POST request.\n')

    if trigger_word == 'repeat':
        res = web.json_response(body=format_response(user_name + ' wants me to ' + text))
        print(res.headers)
        #res.charset='utf-8'
        #print(res.body.write('sys.stderr'))
        return res
        #return web.json_response(body=format_response(user_name + ' wants me to ' + text))
    elif trigger_word == 'whoami':
        return web.json_response(body=format_response('You are ' + user_name + ' with id ' + user_id))
    else:
        return web.json_response(body=format_response(user_name + ' wrote ' + text))


app = web.Application()
app.router.add_get('/', handle)
app.router.add_post('/', handle_post)
DB_ACCESS = db.DatabaseAccess()

########testing part...#######################
import asyncio
from slacker import Slacker

async def run():
    slack = Slacker('')   
    slack.chat.post_message('#bot-channel', 'docker slacker-asyncio test!')

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
#############################

if __name__ == '__main__':
    web.run_app(app)


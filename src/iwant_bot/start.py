from aiohttp import web

from iwant_bot import db


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
    text.extend([format_message(msg) for msg in messages_we_got_so_far])
    return web.Response(text='\n'.join(text))


app = web.Application()
app.router.add_get('/', handle)
DB_ACCESS = db.DatabaseAccess()

if __name__ == '__main__':
    web.run_app(app)

from aiohttp import web

from iwant_bot import db


DB_ACCESS = None

def format_message(message):
   ret = "'{0.text}' by '{0.nickname}' at {0.when}".format(message)
   return ret


async def handle(request):
    name = request.rel_url.query.get('name', "anonymous")
    message = request.rel_url.query.get('msg', "")
    DB_ACCESS.save_message(message, name)

    messages_we_got_so_far = DB_ACCESS.load_n_last_messages()
    text = ["We got these entries so far:\n"]
    text.extend([format_message(msg) for msg in messages_we_got_so_far])
    return web.Response(text="\n".join(text))


if __name__ == "__main__":
    DB_ACCESS = db.DatabaseAccess()
    app = web.Application()
    app.router.add_get('/', handle)
    web.run_app(app)

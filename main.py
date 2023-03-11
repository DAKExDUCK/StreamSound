import asyncio
import os

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_session import get_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from modules.app import room, user
from modules.app.player import PLayer, Room, stream
from modules.db import Database
from modules.yandex_m_client import YandexMusicClient

routes = web.RouteTableDef()


class HomeHandler(web.View):

    async def get(self):
        router = self.request.app.router
        session = await get_session(self.request)

        if 'user' in session:
            raise web.HTTPFound(router["player"].url_for())
        else:
            raise web.HTTPFound(router["signin"].url_for())


async def make_app():
    app = web.Application()
    app['static_root_url'] = '/static'
    app.router.add_static('/static/', path=os.path.join(os.path.dirname(__file__), 'static'), name='static')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    setup(app,EncryptedCookieStorage(str.encode(os.getenv('COOKIE_KEY'))))

    app.add_routes(routes)
    app.router.add_get('/', HomeHandler, name='home')

    app.router.add_get('/player', PLayer, name='player')
    app.router.add_post('/player', PLayer)
    app.router.add_get('/stream', stream, name='stream')
    app.router.add_get('/room', Room, name='room')

    app.router.add_get('/signin', user.SignInHandler, name='signin')
    app.router.add_get('/sing_up', user.SignUpHandler, name='signup')
    app.router.add_post('/signin', user.SignInHandler)
    app.router.add_post('/sing_up', user.SignUpHandler)

    app.router.add_get('/logout', user.LogoutHandler, name='logout')

    return app


asyncio.run(Database.init_connection())
asyncio.run(YandexMusicClient.init())
web.run_app(make_app())
asyncio.run(Database.close())
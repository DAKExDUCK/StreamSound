import json
import aiohttp
import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session, new_session

from modules.app.additional import _login_required, login_required
from modules.app.room import Room, rooms
from modules.db import Database


@aiohttp_jinja2.template("/player.html")
class PLayer(web.View):

    @login_required
    async def get(self):
        return { 'user': self.request.user }
    
    @login_required
    async def post(self):
        request = self.request
        user = request.user  

        if not user['id'] in rooms:
            room = Room(user['id'])
        else:
            room = rooms[user['id']]
        rooms[user['id']] = room

        data = await request.json()
        print(data)
        cmd = data.get('cmd', None)

        if cmd == None:
            url = data['url']
            await room.add_song(url)
        elif cmd == 'play':
            await room.play_song()
        elif cmd == 'stop':
            await room.stop_song()
        elif cmd == 'stop_full':
            await room.stop_full()
        elif cmd == 'next':
            await room.next_song()
        elif cmd == 'prev':
            await room.prev_song()
        else:
            pass

        return web.json_response( {
            'msg': 'ok'
        } )


@_login_required
async def stream(request):
    user = request.user
    if not user['id'] in rooms:
        room = Room(user['id'])
    else:
        room = rooms[user['id']]
    rooms[user['id']] = room

    return await room.get_stream()


    

# @aiohttp_jinja2.template("/room.html")
# class Room(web.View):

#     # @login_required
#     async def get(self):
#         request = self.request
#         query = request.query
#         ws = rooms[query['room']]
import aiohttp
import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session, new_session

from modules.app.additional import login_required
from modules.db import Database


@aiohttp_jinja2.template("register/signin.html")
class SignInHandler(web.View):

    async def get(self):
        router = self.request.app.router
        session = await get_session(self.request)

        if 'user' in session:
            raise web.HTTPFound(router["player"].url_for())
        else:
            return {}

    async def post(self):
        router = self.request.app.router
        form = await self.request.post()
        username = str(form['username'])
        passwd = str(form['password'])

        if await Database.if_user(form['username']):
            passwd_crypted = await Database._get_key(username, 'password')
            # if passwd_crypted == Database.crypt(passwd, username):
            if passwd_crypted == passwd:
                session = await new_session(self.request)
                session["user"] = form['username']
                raise web.HTTPFound(router["home"].url_for())
            else:
                return { 'error': 'Wrong username or password'}
        else:
            return { 'error': 'Wrong username or password'}
        

@aiohttp_jinja2.template('register/signup.html')
class SignUpHandler(web.View):
    async def get(self):
        session = await get_session(self.request)

        if 'user' in session:
            return aiohttp.web.HTTPFound('/')

        return {}
    
    async def post(self):
        session = await get_session(self.request)
        data = await self.request.post()
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if not username or not password:
            error = 'Please enter a username and password'
            return {'error': error}
        elif username in await Database.get_users_list():
            error = 'Username already exists'
            return {'error': error}
        elif password != confirm_password:
            error = 'Passwords do not match'
            return {'error': error}

        await Database.create_user({'id': username, 'password': password})
        session['user'] = username
        return aiohttp.web.HTTPFound('/')


class LogoutHandler(web.View):
    @login_required
    async def get(self):
        session = await get_session(self.request)
        del session["user"]
        raise web.HTTPSeeOther(location="/")
from typing import Any, Awaitable, Callable

from aiohttp import web
from aiohttp_session import get_session

from ..db import Database

_Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]


def login_required(func: _Handler) -> _Handler:
    async def wrapped(handler: web.View, *args: Any, **kwargs: Any) -> web.StreamResponse:
        app = handler.request.app
        router = app.router
        session = await get_session(handler.request)

        if "user" not in session:
            return web.HTTPFound(router["signin"].url_for())

        user_id = session["user"]
        user = await Database.get_user(user_id)
        handler.request.user = user
        return await func(handler, *args, **kwargs)

    return wrapped


def _login_required(func: _Handler) -> _Handler:
    async def wrapped(request: web.View, *args: Any, **kwargs: Any) -> web.StreamResponse:
        app = request.app
        router = app.router
        session = await get_session(request)

        if "user" not in session:
            return web.HTTPFound(router["signin"].url_for())

        user_id = session["user"]
        user = await Database.get_user(user_id)
        request.user = user
        return await func(request, *args, **kwargs)

    return wrapped
import asyncio
import logging
from typing import Optional

import uvicorn

from .error_renderer import ErrorRenderer, DefaultErrorRenderer
from .exceptions.machine import MachineError
from .scope import Scope
from .path import Path
from .connection import Connection


logger = logging.getLogger('machine')


class Machine:
    def __init__(self, error_renderer: Optional[ErrorRenderer] = None):
        self.__scopes = []
        self.__error_renderer = error_renderer or DefaultErrorRenderer()
        self.__on_startup = []
        self.__on_shutdown = []

    def scope(self, path: Path) -> Scope:
        scope = Scope(path)
        self.__scopes.append(scope)
        return scope

    @property
    def on_startup(self):
        def wrapper(f):
            self.__on_startup.append(f)
            return f

        return wrapper

    @property
    def on_shutdown(self):
        def wrapper(f):
            self.__on_shutdown.append(f)
            return f

        return wrapper

    def add_scope(self, scope: Scope) -> Scope:
        self.__scopes.append(scope)
        return scope

    async def __startup(self):
        coros = [f(self) for f in self.__on_startup]
        coros = [coro for coro in coros if asyncio.iscoroutine(coro)]

        for coro in coros:
            await coro

    async def __shutdown(self):
        coros = [f(self) for f in self.__on_shutdown]
        coros = [coro for coro in coros if asyncio.iscoroutine(coro)]

        for coro in coros:
            await coro

    async def __lifespan(self, scope, receive, send):
        message = await receive()
        assert message["type"] in ["lifespan.startup", "lifespan.shutdown"]

        assert message["type"] == "lifespan.startup"
        await self.__startup()
        await send({"type": "lifespan.startup.complete"})

        message = await receive()
        assert message["type"] == "lifespan.shutdown"
        await self.__shutdown()
        await send({"type": "lifespan.shutdown.complete"})

    async def __call__(self, conn_scope, receive, send):
        conn = Connection(scope=conn_scope, send=send, receive=receive)

        if conn.type == 'lifespan':
            return await self.__lifespan(conn_scope, receive, send)

        try:
            found = False

            for scope in self.__scopes:
                used_conn, params = await scope(conn, {'path': conn.path})

                if used_conn is not None:
                    found = True
                    break

            if not found:
                await self.__error_renderer.render(conn=conn, status_code=404, error='Resource not found')

        except MachineError as e:
            await self.__error_renderer.render(conn, error=e)

        except Exception as e:
            logger.error(f'Got exception while handling request: {e}', exc_info=e)
            await self.__error_renderer.render(conn=conn, status_code=500, error=e)

        if not conn.closed:
            await conn.close()

    def run(self, host: str = '127.0.0.1', port: int = 8000, log_level: str = 'info'):
        uvicorn.run(self, host=host, port=port, log_level=log_level)

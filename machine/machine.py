import asyncio
import logging
from typing import Optional, Union

import uvicorn

from .plugins import options
from .error_renderer import ErrorRenderer, DefaultErrorRenderer
from .exceptions.machine import MachineError
from .connection import Connection
from .types import PluginGenerator

logger = logging.getLogger('machine')


class Machine:
    def __init__(self, error_renderer: Optional[ErrorRenderer] = None):
        self._roots = []
        self._error_renderer = error_renderer or DefaultErrorRenderer()
        self._on_startup = []
        self._on_shutdown = []

    def add_root(self, root: PluginGenerator):
        self._roots.append(root)

    @property
    def on_startup(self):
        def wrapper(f):
            self._on_startup.append(f)
            return f

        return wrapper

    @property
    def on_shutdown(self):
        def wrapper(f):
            self._on_shutdown.append(f)
            return f

        return wrapper

    def __iadd__(self, other):
        return self.add_root(other)

    async def _startup(self):
        coros = [f(self) for f in self._on_startup]
        coros = [coro for coro in coros if asyncio.iscoroutine(coro)]

        for coro in coros:
            await coro

    async def _shutdown(self):
        coros = [f(self) for f in self._on_shutdown]
        coros = [coro for coro in coros if asyncio.iscoroutine(coro)]

        for coro in coros:
            await coro

    async def _lifespan(self, scope, receive, send):
        message = await receive()
        assert message["type"] in ["lifespan.startup", "lifespan.shutdown"]

        assert message["type"] == "lifespan.startup"
        await self._startup()
        await send({"type": "lifespan.startup.complete"})

        message = await receive()
        assert message["type"] == "lifespan.shutdown"
        await self._shutdown()
        await send({"type": "lifespan.shutdown.complete"})

    async def __call__(self, conn_scope, receive, send):
        conn = Connection(scope=conn_scope, send=send, receive=receive)

        if conn.type == 'lifespan':
            return await self._lifespan(conn_scope, receive, send)

        try:
            plugin = options(self._roots)()
            result = await plugin(conn, {})

            if result.is_left():
                await self._error_renderer.render(conn=conn, status_code=404, error='Resource not found')

            await plugin.destruct(conn, {})

        except MachineError as e:
            await self._error_renderer.render(conn, error=e)

        except Exception as e:
            logger.error(f'Got exception while handling request: {e}', exc_info=e)
            await self._error_renderer.render(conn=conn, status_code=500, error=e)

        if not conn.closed:
            await conn.close()

    def run(self, host: str = '127.0.0.1', port: int = 8000, log_level: str = 'info'):
        uvicorn.run(self, host=host, port=port, log_level=log_level)

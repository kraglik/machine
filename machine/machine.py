import logging
from typing import AsyncGenerator

import uvicorn

from .params import Parameters
from .connection import Connection
from .types import PluginGenerator

logger = logging.getLogger('machine')


class Machine:
    def __init__(self):
        self._root = None
        self._on_startup = []
        self._on_shutdown = []

    @property
    def root(self) -> PluginGenerator:
        return self._root

    @property
    def on_startup(self):
        return lambda f: self._on_startup.append(f)

    @property
    def on_shutdown(self):
        return lambda f: self._on_shutdown.append(f)

    @root.setter
    def root(self, new_root: PluginGenerator):
        self._root = new_root

    async def _lifespan(self, receive, send):
        try:
            message = await receive()
            assert message["type"] == "lifespan.startup"
            [await f() for f in self._on_startup]
            await send({"type": "lifespan.startup.complete"})
        except Exception:
            await send({'type': 'lifespan.startup.failed'})

        try:
            message = await receive()
            assert message["type"] == "lifespan.shutdown"
            [await f() for f in self._on_shutdown]
            await send({'type': 'lifespan.shutdown.complete'})
        except Exception:
            await send({'type': 'lifespan.shutdown.failed'})

    async def __call__(self, conn_scope, receive, send):
        conn = Connection(scope=conn_scope, send=send, receive=receive)

        if conn.type == 'lifespan':
            await self._lifespan(receive, send)

        elif self.root is not None:
            try:
                async for _ in self.root()(conn, Parameters.from_conn(conn)):
                    pass

            except StopAsyncIteration:
                pass

            except Exception as e:
                logger.error(f'Got unhandled exception while handling request: {e}', exc_info=e)

    def run(self, host: str = '127.0.0.1', port: int = 8000, log_level: str = 'info'):
        uvicorn.run(self, host=host, port=port, log_level=log_level)

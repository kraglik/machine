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

    @property
    def root(self) -> PluginGenerator:
        return self._root

    @root.setter
    def root(self, new_root: PluginGenerator):
        self._root = new_root

    async def __call__(self, conn_scope, receive, send):
        conn = Connection(scope=conn_scope, send=send, receive=receive)

        try:
            async for _ in self.root()(conn, Parameters.from_conn(conn)):
                pass

        except StopAsyncIteration:
            pass

        except Exception as e:
            logger.error(f'Got unhandled exception while handling request: {e}', exc_info=e)

    def run(self, host: str = '127.0.0.1', port: int = 8000, log_level: str = 'info'):
        uvicorn.run(self, host=host, port=port, log_level=log_level)

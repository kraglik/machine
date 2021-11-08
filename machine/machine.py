import logging
from typing import List, Callable, Optional

import uvicorn

from .params import Parameters
from .connection import Connection
from .types import (
    StartupHandler,
    ShutdownHandler,
    Receive,
    Send,
    Scope,
)
from .plugin import PluginGenerator

logger = logging.getLogger("machine")


class Machine:
    def __init__(self) -> None:
        self._root: Optional[PluginGenerator] = None
        self._on_startup: List[StartupHandler] = []
        self._on_shutdown: List[ShutdownHandler] = []

    @property
    def root(self) -> Optional[PluginGenerator]:
        return self._root

    @root.setter
    def root(self, new_root: PluginGenerator) -> None:
        self._root = new_root

    @property
    def on_startup(self) -> Callable[[StartupHandler], None]:
        return lambda f: self._on_startup.append(f)

    @property
    def on_shutdown(self) -> Callable[[ShutdownHandler], None]:
        return lambda f: self._on_shutdown.append(f)

    async def _lifespan(self, receive: Receive, send: Send) -> None:
        try:
            message = await receive()
            assert message["type"] == "lifespan.startup"
            [await f() for f in self._on_startup]
            await send({"type": "lifespan.startup.complete"})
        except Exception:
            await send({"type": "lifespan.startup.failed"})

        try:
            message = await receive()
            assert message["type"] == "lifespan.shutdown"
            [await f() for f in self._on_shutdown]
            await send({"type": "lifespan.shutdown.complete"})
        except Exception:
            await send({"type": "lifespan.shutdown.failed"})

    async def __call__(
        self, conn_scope: Scope, receive: Receive, send: Send
    ) -> None:
        conn = Connection(scope=conn_scope, send=send, receive=receive)

        if conn.type == "lifespan":
            await self._lifespan(receive, send)

        elif self.root is not None:
            try:
                async for _ in self.root()(conn, Parameters.from_conn(conn)):
                    pass

            except StopAsyncIteration:
                pass

            except Exception as e:
                logger.error(
                    f"Got unhandled exception while handling request: {e}",
                    exc_info=e,
                )

    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        log_level: str = "info",
    ) -> None:
        uvicorn.run(self, host=host, port=port, log_level=log_level)

from typing import Callable

from machine.params import Parameters
from machine.connection import Connection
from machine.exceptions.plugins.accept import UnsupportedResponseTypeError
from machine.plugin import Plugin
from machine.types import PluginResult


class Accepts(Plugin):

    CONTENT_TYPES_MAP = {
        "html": ["text/html", "application/xhtml+xml"],
        "json": ["application/json"],
        "all": ["*/*"],
    }

    def __init__(self, *accepted: str):
        self._accepted = []

        for content_type in accepted:
            self._accepted.extend(
                self.CONTENT_TYPES_MAP.get(content_type, [content_type])
            )

    async def __call__(
        self, conn: Connection, params: Parameters
    ) -> PluginResult:
        if "*/*" in conn.accept or all(
            accepted in conn.accept for accepted in self._accepted
        ):
            yield conn, params
            return

        raise UnsupportedResponseTypeError()


def accepts(*accepted: str) -> Callable[[], Plugin]:
    return lambda: Accepts(*accepted)

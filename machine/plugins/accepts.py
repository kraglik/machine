from typing import List, Callable

from machine.connection import Connection
from machine.exceptions.plugins.accept import UnsupportedResponseTypeError
from machine.plugin import Plugin, PluginResult
from machine.utils import Either, Right


class Accepts(Plugin):

    CONTENT_TYPES_MAP = {
        "html": ["text/html", "application/xhtml+xml"],
        "json": ["application/json"],
        "all": ["*/*"]
    }

    def __init__(self, *accepted: str):
        self._accepted = []

        for content_type in accepted:
            self._accepted.extend(self.CONTENT_TYPES_MAP.get(content_type, [content_type.encode('utf-8')]))

    async def __call__(self, conn: Connection, params: dict) -> Either:
        if "*/*" in conn.accept:
            return Right((conn, params))

        if not all(accepted in conn.accept for accepted in self._accepted):
            raise UnsupportedResponseTypeError()

        return Right((conn, params))


def accepts(*accepted: str) -> Callable[[], Plugin]:
    return lambda: Accepts(*accepted)

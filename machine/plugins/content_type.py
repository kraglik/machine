from typing import Callable

from machine.connection import Connection
from machine.exceptions.machine import UnexpectedContentType
from machine.plugin import Plugin, PluginResult
from machine.utils import Right, Either


class ContentType(Plugin):
    def __init__(self, ct: str):
        self._content_type = ct

    async def __call__(self, conn: Connection, params: dict) -> Either:
        if 'content-type' not in conn.headers \
                or conn.headers['content-type'].decode('utf-8') != self._content_type:
            raise UnexpectedContentType()

        return Right((conn, params))


def content_type(ct: str) -> Callable[[], Plugin]:
    return lambda: ContentType(ct)

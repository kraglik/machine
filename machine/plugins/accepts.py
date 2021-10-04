from typing import List

from machine.connection import Connection
from machine.exceptions.plugins.accept import UnsupportedResponseTypeError
from machine.plugin import Plugin, PluginResult


class accepts(Plugin):

    CONTENT_TYPES_MAP = {
        "html": ["text/html", "application/xhtml+xml"],
        "json": ["application/json"]
    }

    def __init__(self, *accepted: str):
        self.__accepted = []

        for content_type in accepted:
            self.__accepted.extend(self.CONTENT_TYPES_MAP.get(content_type, [content_type.encode('utf-8')]))

    async def __call__(self, conn: Connection, params: dict) -> PluginResult:
        if not all(accepted in conn.accept for accepted in self.__accepted):
            raise UnsupportedResponseTypeError()

        return conn, params

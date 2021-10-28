from typing import Dict

from machine.exceptions.resource import MethodNotAllowedResourceError
from machine.plugin import Plugin
from machine.connection import Connection
from machine.params import Parameters


class MethodSelector(Plugin):
    def __init__(self, handlers: Dict[str, Plugin]):
        self._method_handlers = handlers

    async def __call__(self, conn: Connection, params: Parameters):
        if conn.method.value not in self._method_handlers:
            raise MethodNotAllowedResourceError()

        async for conn, params in self._method_handlers[conn.method.value]()(conn, params):
            yield conn, params


def method_selector(handlers: Dict[str, Plugin]):
    return lambda: MethodSelector(handlers)


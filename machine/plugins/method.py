from machine.connection import Connection
from machine.exceptions.resource import MethodNotAllowedResourceError
from machine.params import Parameters
from machine.plugin import Plugin
from machine.types import PluginGenerator


class Method(Plugin):
    def __init__(self, method: str, allowed: bool = True, only: bool = False):
        self._method = method
        self._allowed = allowed
        self._only = only

    async def __call__(self, conn: Connection, params: Parameters):
        method_match = conn.method.value == self._method

        if not method_match and self._only:
            raise MethodNotAllowedResourceError()

        if method_match and self._allowed:
            yield conn, params
            return

        raise MethodNotAllowedResourceError()


def method(method_name: str, allowed: bool = True, only: bool = False) -> PluginGenerator:
    return lambda: Method(method_name, allowed, only)

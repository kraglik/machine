from machine.connection import Connection
from machine.exceptions.resource import MethodNotAllowedResourceError
from machine.plugin import Plugin
from machine.types import PluginGenerator
from machine.utils import Either, Right, Left


class Method(Plugin):
    def __init__(self, method: str, allowed: bool = True, only: bool = False):
        self._method = method
        self._allowed = allowed
        self._only = only

    async def __call__(self, conn: Connection, params: dict) -> Either:
        method_match = conn.method.value == self._method

        if method_match and self._allowed:
            return Right((conn, params))

        if method_match and not self._allowed:
            raise MethodNotAllowedResourceError()

        if not method_match and self._only:
            raise MethodNotAllowedResourceError()

        return Left()


def method(method_name: str, allowed: bool = True, only: bool = False) -> PluginGenerator:
    return lambda: Method(method_name, allowed, only)

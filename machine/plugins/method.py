from machine.connection import Connection
from machine.exceptions.resource import MethodNotAllowedResourceError
from machine.plugin import Plugin
from machine.types import PluginGenerator
from machine.utils import Either, Right, Left


class Method(Plugin):
    def __init__(self, method: str, allowed: bool = True):
        self._method = method
        self._allowed = allowed

    async def __call__(self, conn: Connection, params: dict) -> Either:
        method_match = conn.method.value == self._method

        if method_match and self._allowed:
            return Right((conn, params))

        if method_match and not self._allowed:
            raise MethodNotAllowedResourceError()

        return Left()


def method(method_name: str, allowed: bool = True) -> PluginGenerator:
    return lambda: Method(method_name, allowed)

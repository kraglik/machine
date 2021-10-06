from machine.connection import Connection
from machine.plugin import Plugin
from machine.types import PluginGenerator
from machine.utils import Either, Right, Left


class Method(Plugin):
    def __init__(self, method: str):
        self._method = method

    async def __call__(self, conn: Connection, params: dict) -> Either:
        if conn.method.value == self._method:
            return Right((conn, params))

        return Left()


def method(method_name: str) -> PluginGenerator:
    return lambda: Method(method_name)

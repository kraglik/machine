from machine.connection import Connection
from machine.plugin import Plugin
from machine.types import PluginGenerator
from machine.utils import Either, Right, Left


class ConnType(Plugin):
    def __init__(self, connection_type: str):
        self._connection_type = connection_type

    async def __call__(self, conn: Connection, params: dict) -> Either:
        if conn.type == self._connection_type:
            return Right((conn, params))

        return Left()


def conn_type(connection_type: str) -> PluginGenerator:
    return lambda: ConnType(connection_type)

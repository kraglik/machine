from machine.connection import Connection
from machine.exceptions.plugins.conn_type import UnsupportedConnectionType
from machine.params import Parameters
from machine.plugin import Plugin
from machine.types import PluginGenerator


class ConnType(Plugin):
    def __init__(self, connection_type: str):
        self._connection_type = connection_type

    async def __call__(self, conn: Connection, params: Parameters):
        if conn.type == self._connection_type:
            yield conn, params
            return

        raise UnsupportedConnectionType()


def conn_type(connection_type: str) -> PluginGenerator:
    return lambda: ConnType(connection_type)

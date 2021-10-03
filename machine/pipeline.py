from typing import List, Optional

from .connection import Connection
from .plugin import Plugin, PluginResult


class Pipeline(Plugin):
    def __init__(self, plugins: Optional[List[Plugin]] = None):
        self.__plugins = plugins or []

    async def __call__(self, conn: Connection, params: dict) -> PluginResult:
        for plugin in self.__plugins:
            if conn is None:
                break

            conn, params = plugin(conn, params)

        return conn, params

    def add(self, plugin: Plugin) -> 'Pipeline':
        self.__plugins.append(plugin)
        return self

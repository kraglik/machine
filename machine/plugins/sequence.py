from typing import List, Tuple

from machine.plugin import Plugin
from machine.connection import Connection
from machine.types import PluginGenerator
from machine.utils import Either, Right


class Sequence(Plugin):
    def __init__(self, plugins: List[PluginGenerator]):
        assert len(plugins) > 0, "Sequence cannot be empty!"
        self._plugins = plugins
        self._applied_plugins = []

    async def __call__(self, conn: Connection, params: dict) -> Either:
        result = Right((conn, params))
        exception = None

        for plugin_gen in self._plugins:
            plugin = plugin_gen()

            try:
                result = await plugin(conn, params)
            except Exception as e:
                exception = e
                break

            if result.is_left():
                break

            self._applied_plugins.append(plugin)
            conn, params = result.value

        for plugin in reversed(self._applied_plugins):
            conn, params = await plugin.destruct(conn, params)

        if exception is not None:
            raise exception

        return result


def sequence(plugins: List[PluginGenerator]) -> PluginGenerator:
    return lambda: Sequence(plugins)

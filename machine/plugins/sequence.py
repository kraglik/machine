from typing import List

from machine.params import Parameters
from machine.plugin import Plugin
from machine.connection import Connection
from machine.plugin import PluginGenerator, PluginResult


class Sequence(Plugin):
    def __init__(self, plugins: List[PluginGenerator]):
        assert len(plugins) > 0, "Sequence cannot be empty!"
        self._plugins = plugins

    async def __call__(
        self, conn: Connection, params: Parameters
    ) -> PluginResult:
        applied_plugins: List[PluginResult] = []

        try:
            for plugin_gen in self._plugins:
                plugin = plugin_gen()(conn, params)

                conn, params = await plugin.__anext__()
                applied_plugins.append(plugin)

            yield conn, params

            for plugin in reversed(applied_plugins):
                try:
                    await plugin.__anext__()
                except StopAsyncIteration:
                    continue

            return

        except Exception as exception:
            error = exception

            while len(applied_plugins) > 0:
                try:
                    plugin = applied_plugins.pop(-1)
                    await plugin.athrow(error)
                    break
                except Exception as e:
                    error = e


def sequence(plugins: List[PluginGenerator]) -> PluginGenerator:
    return lambda: Sequence(plugins)

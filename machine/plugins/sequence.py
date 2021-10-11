from typing import List, AsyncGenerator

from machine.params import Parameters
from machine.plugin import Plugin
from machine.connection import Connection
from machine.types import PluginGenerator


class Sequence(Plugin):
    def __init__(self, plugins: List[PluginGenerator]):
        assert len(plugins) > 0, "Sequence cannot be empty!"
        self._plugins = plugins

    async def __call__(self, conn: Connection, params: Parameters):
        applied_plugins: List[AsyncGenerator] = []

        try:
            for plugin_gen in self._plugins:
                plugin = plugin_gen()(conn, params)

                # for some reason, anext is not defined in some versions of python
                conn, params = await plugin.__anext__()
                applied_plugins.append(plugin)

            yield conn, params
            return

        except Exception as exception:
            error = exception
            for plugin in reversed(applied_plugins):
                try:
                    await plugin.athrow(error)
                    break
                except Exception as e:
                    error = e


def sequence(plugins: List[PluginGenerator]) -> PluginGenerator:
    return lambda: Sequence(plugins)

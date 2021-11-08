from typing import List, Optional

from machine.exceptions.plugins.options import SuitableArmNotFound
from machine.params import Parameters
from machine.plugin import Plugin
from machine.connection import Connection
from machine.types import PluginGenerator, PluginResult


class Options(Plugin):
    def __init__(self, arms: List[PluginGenerator]):
        self._arms = arms

    async def __call__(self, conn: Connection, params: Parameters) -> PluginResult:
        for arm in self._arms:
            try:
                plugin = arm()(conn, params)
                new_conn, new_params = await plugin.__anext__()
                yield new_conn, new_params

                try:
                    await plugin.__anext__()
                except StopAsyncIteration:
                    pass

                return

            except Exception as e:
                pass

        raise SuitableArmNotFound()


def options(arms: List[PluginGenerator]) -> PluginGenerator:
    return lambda: Options(arms)

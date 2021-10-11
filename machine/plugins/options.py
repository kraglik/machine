from typing import List, Optional

from machine.exceptions.plugins.options import SuitableArmNotFound
from machine.params import Parameters
from machine.plugin import Plugin
from machine.connection import Connection
from machine.types import PluginGenerator


class Options(Plugin):
    def __init__(self, arms: List[PluginGenerator]):
        self._arms = arms

    async def __call__(self, conn: Connection, params: Parameters):
        for arm in self._arms:
            try:
                async for new_conn, new_params in arm()(conn, params):
                    yield new_conn, new_params
                    return

            except Exception as e:
                pass

        raise SuitableArmNotFound()


def options(arms: List[PluginGenerator]) -> PluginGenerator:
    return lambda: Options(arms)

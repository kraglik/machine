from typing import List, Optional

from machine.plugin import Plugin, PluginResult
from machine.connection import Connection
from machine.types import PluginGenerator
from machine.utils import Either, Left


class Options(Plugin):
    def __init__(self, arms: List[PluginGenerator]):
        self._arms = arms
        self._applied_arm: Optional[Plugin] = None

    async def __call__(self, conn: Connection, params: dict) -> Either:
        for arm in self._arms:
            plugin = arm()
            result = await plugin(conn, params)

            if result.is_right():
                self._applied_arm = plugin
                return result

        return Left()

    async def destruct(self, conn: Connection, params: dict) -> PluginResult:
        if self._applied_arm:
            conn, params = await self._applied_arm.destruct(conn, params)

        return conn, params


def options(arms: List[PluginGenerator]) -> PluginGenerator:
    return lambda: Options(arms)

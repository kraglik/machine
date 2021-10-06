from typing import Callable, AsyncGenerator

from machine.connection import Connection
from machine.plugin import Plugin, PluginResult
from machine.types import PluginGenerator
from machine.utils import Either, Right

DependencyGenerator = Callable[[], AsyncGenerator[any, None]]


class Dependency(Plugin):
    def __init__(
            self,
            name: str,
            resource_gen: DependencyGenerator
    ):
        self._name = name
        self._resource_gen = resource_gen()

    async def __call__(self, conn: Connection, params: dict) -> Either:
        return Right((conn, {**params, self._name: await self._resource_gen.__anext__()}))

    async def destruct(self, conn: Connection, params: dict) -> PluginResult:
        if self._name not in params:
            raise RuntimeError(f'Cannot find dependency with name "{self._name}" in params')

        params = params.copy()
        del params[self._name]

        try:
            await self._resource_gen.__anext__()
        except StopAsyncIteration:
            return conn, params
        except Exception as e:
            raise e


def dependency(name: str, resource_gen: DependencyGenerator) -> PluginGenerator:
    return lambda: Dependency(name, resource_gen)

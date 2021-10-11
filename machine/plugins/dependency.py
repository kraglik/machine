from typing import Callable, AsyncGenerator

from machine.connection import Connection
from machine.params import Parameters
from machine.plugin import Plugin
from machine.types import PluginGenerator

DependencyGenerator = Callable[[], AsyncGenerator[any, None]]


class Dependency(Plugin):
    def __init__(
            self,
            name: str,
            resource_gen: DependencyGenerator
    ):
        self._name = name
        self._resource_gen = resource_gen()

    async def __call__(self, conn: Connection, params: Parameters):
        async for obj in self._resource_gen:
            yield conn, params.with_new_params({self._name: obj})


def dependency(name: str, resource_gen: DependencyGenerator) -> PluginGenerator:
    return lambda: Dependency(name, resource_gen)

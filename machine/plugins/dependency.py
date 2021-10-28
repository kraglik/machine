from typing import Callable, AsyncGenerator, Union
from inspect import signature

from machine.connection import Connection
from machine.params import Parameters
from machine.plugin import Plugin
from machine.types import PluginGenerator

DependencyGenerator = Union[
    Callable[[], AsyncGenerator[any, None]],
    Callable[[Connection, Parameters], AsyncGenerator[any, None]],
]


class Dependency(Plugin):
    def __init__(
            self,
            name: str,
            resource_gen: DependencyGenerator
    ):
        self._name = name
        self._resource_gen = resource_gen
        self._accepts_conn_and_params = len(signature(resource_gen).parameters) == 2

    async def __call__(self, conn: Connection, params: Parameters):
        gen = self._resource_gen(conn, params) \
            if self._accepts_conn_and_params \
            else self._resource_gen()

        async for obj in gen:
            yield conn, params.with_new_params({self._name: obj})


def dependency(name: str, resource_gen: DependencyGenerator) -> PluginGenerator:
    return lambda: Dependency(name, resource_gen)

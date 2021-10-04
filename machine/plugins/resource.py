from typing import Callable, Tuple, Awaitable

from machine.connection import Connection
from machine.exceptions.machine import UnexpectedContentType
from machine.plugin import Plugin, PluginResult


class resource(Plugin):

    def __init__(
            self,
            name: str,
            constructor: Callable[[Connection, dict], Awaitable[any]],
            destructor: Callable[[Connection, any, dict], Awaitable[Tuple[Connection, dict]]]
    ):
        self.__name = name
        self.__constructor = constructor
        self.__destructor = destructor

    async def __call__(self, conn: Connection, params: dict) -> PluginResult:
        return conn, {**params, self.__name: await self.__constructor(conn, params)}

    async def destruct(self, conn: Connection, params: dict) -> PluginResult:
        if self.__name not in params:
            raise RuntimeError(f'Cannot find parameter with name "{self.__name}" in params')

        params = {**params}

        item = params[self.__name]
        del params[self.__name]

        return await self.__destructor(conn, item, params)



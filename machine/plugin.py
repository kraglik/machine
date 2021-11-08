import typing

from abc import ABC, abstractmethod

from .connection import Connection
from .params import Parameters


PluginResult = typing.AsyncGenerator[
    typing.Tuple[Connection, Parameters], None
]
PluginType = typing.Callable[[Connection, Parameters], PluginResult]
PluginGenerator = typing.Callable[[], PluginType]


class Plugin(ABC):
    @abstractmethod
    async def __call__(
        self, conn: Connection, params: Parameters
    ) -> PluginResult:
        raise NotImplementedError
        yield conn, params

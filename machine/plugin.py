from abc import ABC, abstractmethod

from .connection import Connection
from .params import Parameters
from .types import PluginResult


class Plugin(ABC):
    @abstractmethod
    async def __call__(self, conn: Connection, params: Parameters) -> PluginResult:
        raise NotImplementedError
        yield conn, params

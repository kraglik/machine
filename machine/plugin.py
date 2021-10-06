from abc import ABC, abstractmethod
from typing import Optional, Tuple

from .connection import Connection
from .utils import Either

PluginResult = Tuple[Optional[Connection], dict]


class Plugin(ABC):
    @abstractmethod
    async def __call__(self, conn: Connection, params: dict) -> Either:
        raise NotImplementedError

    async def destruct(self, conn: Connection, params: dict) -> PluginResult:
        return conn, params

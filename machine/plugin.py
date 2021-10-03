from abc import ABC, abstractmethod
from typing import Optional, Tuple

from .connection import Connection


PluginResult = Tuple[Optional[Connection], dict]


class Plugin(ABC):
    @abstractmethod
    async def __call__(self, conn: Connection, params: dict) -> PluginResult:
        raise NotImplementedError


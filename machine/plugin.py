from abc import ABC, abstractmethod
from typing import Tuple, AsyncGenerator

from .connection import Connection
from .params import Parameters


class Plugin(ABC):
    @abstractmethod
    async def __call__(self, conn: Connection, params: Parameters):
        raise NotImplementedError

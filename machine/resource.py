from abc import ABC, abstractmethod
from machine.types import PluginType


class Resource(ABC):
    @abstractmethod
    def __call__(self) -> PluginType:
        raise NotImplementedError

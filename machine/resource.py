from abc import ABC, abstractmethod
from machine.plugin import Plugin


class Resource(ABC):
    @abstractmethod
    def __call__(self) -> Plugin:
        raise NotImplementedError

from abc import ABC, abstractmethod
from typing import Any


class Either(ABC):
    @abstractmethod
    def is_left(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def value(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def is_right(self) -> bool:
        raise NotImplementedError


class Left(Either):
    def __init__(self, value: Any = None):
        self._value = value

    @property
    def value(self) -> Any:
        return self._value

    def is_left(self) -> bool:
        return True

    def is_right(self) -> bool:
        return False


class Right(Either):
    def __init__(self, value: Any):
        self._value = value

    @property
    def value(self) -> Any:
        return self._value

    def is_left(self) -> bool:
        return False

    def is_right(self) -> bool:
        return True

from abc import ABC, abstractmethod


class Either(ABC):
    @abstractmethod
    def is_left(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def value(self):
        raise NotImplementedError

    @abstractmethod
    def is_right(self) -> bool:
        raise NotImplementedError


class Left(Either):

    def __init__(self, value = None):
        self._value = value

    @property
    def value(self):
        return self._value

    def is_left(self) -> bool:
        return True

    def is_right(self) -> bool:
        return False


class Right(Either):

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def is_left(self) -> bool:
        return False

    def is_right(self) -> bool:
        return True

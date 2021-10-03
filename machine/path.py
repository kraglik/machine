import re

from abc import ABC, abstractmethod
from typing import List

from machine.utils import Either, Left, Right


class Directory(ABC):
    @abstractmethod
    def parse(self, path: str) -> Either:
        raise NotImplementedError


class regex(Directory):
    def __init__(self, pattern: str):
        self.__pattern = pattern

    def parse(self, path: str) -> Either:
        match = re.match(self.__pattern, path)

        if match is None:
            return Left(f'{self} is not in the beginning of the path "{path}"')

        start, end = match.span()
        return Right((dict(), path[end:]))

    def __str__(self):
        return self.__pattern.replace('^', '')


# class const(Directory):
#
#     def __init__(self, value: str):
#         self.__value = value
#
#     def parse(self, path: str) -> Either:
#         if path[:len(self.__value)] == self.__value:
#             return Right((dict(), path[len(self.__value):]))
#         else:
#             return Left(f'{self} is not in the beginning of the path "{path}"')
#
#     def __str__(self):
#         return self.__value


class named(Directory):
    def __init__(self, name: str, pattern: str, value_type: type = str):
        self.__name = name
        self.__type = value_type
        self.__pattern = pattern

    def __str__(self):
        return f'<{self.__name}:{self.__type.__name__}>'

    def parse(self, path: str) -> Either:
        match = re.match(self.__pattern, path)

        if match is None:
            return Left(f'{self} is not in the beginning of the path "{path}"')

        start, end = match.span()

        raw_value = path[start: end]

        try:
            value = self.__type(raw_value)
        except Exception:
            return Left(f'Cannot parse "{raw_value}" into object of type {self.__type.__name__}')

        return Right((
            {self.__name: value},
            path[end:]
        ))


const = lambda s: regex(fr'^{s}')
slash = const('/')
dash = const('-')
ground = const('_')

integral = lambda name: named(name=name, pattern=r'^[0-9]+', value_type=int)
slug = lambda name: named(name=name, pattern=r'^[-\w]+', value_type=str)
named_regex = lambda name, pattern: named(name=name, pattern=pattern, value_type=str)


class Path:

    def __init__(self, directories: List[Directory] = []):
        self.__directories = directories

    @property
    def directories(self):
        return self.__directories

    def parse(self, path: str) -> Either:
        params = {}

        for directory in self.__directories:
            result = directory.parse(path)

            if result.is_left():
                return Left('Wrong path')

            result_params, path = result.value

            params.update(result_params)

        return Right((params, path))

    def __add__(self, other):
        if isinstance(other, Path):
            return Path(
                self.__directories + other.directories
            )

        elif isinstance(other, Directory):
            return Path(
                self.__directories + [other]
            )

        elif isinstance(other, str):
            return Path(
                self.__directories + [const(other)]
            )

        raise ValueError('Unexpected argument type')

    def __truediv__(self, other):
        return self + slash + other

    def __str__(self):
        return ''.join(str(d) for d in self.__directories)


start = Path()
end = regex(r'^$')

from abc import ABC
from typing import Union

from machine.path import Path
from machine.plugin import Plugin


class Resource(Plugin, ABC):
    def __init__(self, name: str, path: Union[str, Path]):
        self._name = name
        self._path = path if isinstance(path, Path) else Path(path)

    @property
    def path(self) -> Path:
        return self._path

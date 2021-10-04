from abc import ABC

from machine.path import Path
from machine.plugin import Plugin


class Resource(Plugin, ABC):
    def __init__(self, name: str, path: Path):
        self._name = name
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

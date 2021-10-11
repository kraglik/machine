from typing import Dict, Union

from machine.exceptions.machine import ResourceNotFound
from machine.params import Parameters
from machine.path import Path
from machine.connection import Connection
from machine.plugin import Plugin
from machine.types import PluginGenerator
from machine.utils import Either, Right


class PathPlugin(Plugin):
    def __init__(self, path_string: str):
        self._path = Path(path_string)

    async def __call__(self, conn: Connection, params: Parameters):
        result = self._path.parse(params.path.remaining)

        if result.is_left():
            raise ResourceNotFound()

        yield conn, params.with_updated_path(*result.value)


def path(path_string: str) -> PluginGenerator:
    return lambda: PathPlugin(path_string)

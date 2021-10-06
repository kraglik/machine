from typing import Dict, Union

from machine.path import Path
from machine.connection import Connection
from machine.plugin import Plugin
from machine.types import PluginGenerator
from machine.utils import Either, Right


class PathPlugin(Plugin):
    def __init__(self, path_string: str):
        self._path = Path(path_string)
        self._params = {}

    def _path_map(self, conn: Connection) -> Dict[str, Dict[str, Union[str, Dict[str, str]]]]:
        return {
            '__path__': {
                'remaining': conn.path,
                'params': {}
            }
        }

    def _update_path_map(self, old_path_map, remaining, new_params):
        self._params = new_params
        return {
            '__path__': {
                'remaining': remaining,
                'params': {**old_path_map['__path__']['params'], **self._params}
            }
        }

    async def __call__(self, conn: Connection, params: dict) -> Either:
        if '__path__' not in params:
            params = {**params, **self._path_map(conn)}

        remaining = params['__path__']['remaining']
        result = self._path.parse(remaining)

        if result.is_left():
            return result

        new_params, remaining = result.value

        return Right(
            (
                conn,
                {
                    **params,
                    **self._update_path_map(params, remaining, new_params)
                }
            )
        )


def path(path_string: str) -> PluginGenerator:
    return lambda: PathPlugin(path_string)

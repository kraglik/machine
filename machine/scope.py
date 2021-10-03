from typing import List, Optional, Tuple

from machine.connection import Connection
from machine.path import Path
from machine.pipeline import Pipeline
from machine.plugin import Plugin, PluginResult
from machine.resource import Resource


class Scope(Plugin):
    def __init__(
            self,
            path: Path,
            pipelines: List[Pipeline] = [],
            scopes: List['Scope'] = [],
            resources: List[Resource] = []
    ):
        self._path = path
        self._pipelines = pipelines.copy()
        self._scopes = scopes.copy()
        self._resources = resources.copy()

    @property
    def path(self) -> Path:
        return self._path

    def scope(self, path: Path) -> 'Scope':
        scope = Scope(path)
        self._scopes.append(scope)
        return scope

    def resource(self, name: str, path: Path):
        def wrapper(r):
            self._resources.append(r(name, path))
        return wrapper

    def add_resource(self, r):
        self._resources.append(r)
        return r

    async def __call__(self, conn: Connection, params: dict) -> PluginResult:
        conn, params = await self._iterate_pipelines(conn, params)

        if conn is None:
            return None, {}

        new_conn, new_params = await self._iterate_resources(conn, params)

        if new_conn is not None:
            return new_conn, new_params

        return await self._iterate_scopes(conn, params)

    async def _iterate_pipelines(self, conn: Connection, params: dict) -> PluginResult:
        path = params['path']
        path_result = self._path.parse(path)

        if path_result.is_left():
            return None, {}

        new_variables, path = path_result.value
        params = {**params, **new_variables, 'path': path}

        for pipeline in self._pipelines:
            if conn is None:
                break

            conn, params = await pipeline(conn, params)

        return conn, params

    async def _iterate_scopes(self, conn: Connection, params: dict) -> PluginResult:
        if not self._scopes:
            return conn, params

        for scope in self._scopes:
            return await scope(conn, params)

        return None, {}

    async def _iterate_resources(self, conn: Connection, params: dict) -> PluginResult:
        path = params['path']

        for resource in self._resources:
            path_result = resource.path.parse(path)

            if path_result.is_left():
                continue

            resource_params = {**params, **path_result.value[0]}
            if 'path' in resource_params:
                del resource_params['path']

            return await resource(conn, resource_params)

        return None, {}

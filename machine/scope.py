from typing import List, Optional, Tuple, Callable

from machine.connection import Connection
from machine.path import Path
from machine.pipeline import Pipeline
from machine.plugin import Plugin, PluginResult
from machine.resource import Resource
from machine.utils import Either, Left, Right


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

    def pipeline(self, plugins: List[Plugin] = []) -> Pipeline:
        pipeline = Pipeline(plugins=plugins.copy())

        self._pipelines.append(pipeline)

        return pipeline

    def add_resource(self, r):
        self._resources.append(r)
        return r

    async def __call__(self, conn: Connection, params: dict) -> PluginResult:
        pipelines_result = await self._iterate_pipelines(conn, params)
        conn, params, pipelines = pipelines_result.value

        if pipelines_result.is_left():
            await self._destruct_plugins(conn, params, pipelines)
            return None, {}

        resources_result = await self._iterate_resources(conn, params)
        conn, params, resources = resources_result.value

        if resources_result.is_right():
            return await self._destruct_plugins(conn, params, resources + pipelines)

        scopes_result = await self._iterate_scopes(conn, params)
        conn, params, scopes = scopes_result.value

        new_conn, new_params = await self._destruct_plugins(conn, params, scopes + resources + pipelines)

        return (new_conn, new_params) if scopes_result.is_right() else (None, {})

    async def _destruct_plugins(self, conn: Connection, params: dict, plugins: List[Plugin]) -> PluginResult:
        for plugin in plugins:
            conn, params = await plugin.destruct(conn, params)

        return conn, params

    async def _iterate_pipelines(self, conn: Connection, params: dict) -> Either:
        applied_plugins = []

        path = params['path']
        path_result = self._path.parse(path)

        if path_result.is_left():
            return Left((conn, params, []))

        new_variables, path = path_result.value
        params = {**params, **new_variables, 'path': path}

        for pipeline in self._pipelines:
            conn, params = await pipeline(conn, params)
            if conn is None:
                break

            applied_plugins.insert(0, pipeline)

        return Right((conn, params, applied_plugins))

    async def _iterate_scopes(self, conn: Connection, params: dict) -> Either:
        applied_scopes = []

        if not self._scopes:
            return Left((conn, params, applied_scopes))

        new_conn, new_params = None, {}

        for scope in self._scopes:
            new_conn, new_params = await scope(conn, params)

            if new_conn is not None:
                applied_scopes.append(scope)
                break

        if new_conn is None:
            return Left((conn, params, applied_scopes))

        return Right((new_conn, new_params, applied_scopes))

    async def _iterate_resources(self, conn: Connection, params: dict) -> Either:
        path = params['path']

        for resource in self._resources:
            path_result = resource.path.parse(path)

            if path_result.is_left():
                continue

            resource_params = {**params, **path_result.value[0]}
            if 'path' in resource_params:
                del resource_params['path']

            new_conn, new_params = await resource(conn, resource_params)

            if new_conn is not None:
                return Right((new_conn, new_params, [resource]))

        return Left((conn, params, []))

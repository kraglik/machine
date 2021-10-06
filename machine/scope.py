from typing import List, Union, Callable

from machine.connection import Connection
from machine.path import Path
from machine.pipeline import Pipeline
from machine.plugin import Plugin, PluginResult
from machine.resource import Resource
from machine.utils import Either, Left, Right


class Scope(Plugin):
    def __init__(
            self,
            path: Union[str, Path],
            pipelines: List[Callable[[], Pipeline]] = [],
            scopes: List['Scope'] = [],
            resources: List[Resource] = []
    ):
        self._path = path if isinstance(path, Path) else Path(path)
        self._pipelines = pipelines.copy()
        self._scopes = scopes.copy()
        self._resources = resources.copy()

    @property
    def path(self) -> Path:
        return self._path

    def scope(self, path: Union[str, Path]) -> 'Scope':
        scope = Scope(path)
        self._scopes.append(scope)
        return scope

    def resource(self, name: str, path: Union[str, Path]):
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

    def add(self, other):
        if isinstance(other, Scope):
            self._scopes.append(other)
            return other

        elif isinstance(other, Resource):
            self._resources.append(other)
            return other

        elif isinstance(other, Pipeline):
            self._pipelines.append(other)
            return other

        raise ValueError("Unexpected argument type!")

    def __iadd__(self, other):
        return self.add(other)

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
            pipeline = pipeline()
            conn, params = await pipeline(conn, params)
            if conn is None:
                break

            applied_plugins.insert(0, pipeline)

        return Right((conn, params, applied_plugins))

    async def _iterate_scopes(self, conn: Connection, params: dict) -> Either:
        if not self._scopes:
            return Left((conn, params))

        new_conn, new_params = None, {}

        for scope in self._scopes:
            new_conn, new_params = await scope(conn, params)

            if new_conn is not None:
                break

        if new_conn is None:
            return Left((conn, params))

        return Right((new_conn, new_params))

    async def _iterate_resources(self, conn: Connection, params: dict) -> Either:
        path = params['path']

        for resource in self._resources:
            path_result = resource.path.parse(path)

            if path_result.is_left():
                continue

            resource_params = {**params, **path_result.value[0]}
            if 'path' in resource_params:
                del resource_params['path']

            plugin = resource.plugin()
            new_conn, new_params = await plugin(conn, resource_params)

            if new_conn is not None:
                plugin.destruct(new_conn, new_params)
                return Right((new_conn, new_params))

        return Left((conn, params))


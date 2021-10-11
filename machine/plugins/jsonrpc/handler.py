from typing import List, Dict

from machine.params import Parameters
from machine.plugin import Plugin
from machine.plugins.sequence import sequence
from machine.connection import Connection
from machine.types import PluginGenerator
from machine.exceptions.plugins.jsonrpc import MachineJsonRPCError
from machine.exceptions.plugins.jsonrpc import JsonRPCInternalError
from machine.exceptions.plugins.jsonrpc import JsonRPCMethodNotFoundError
from machine.exceptions.plugins.jsonrpc import BadJsonRPCRequestError


class JsonRPCHandler:
    def __init__(self, plugins: List[PluginGenerator], method):
        self._plugins = plugins
        self._method = method

    @property
    def method(self):
        return self._method

    @property
    def plugins(self):
        return self._plugins


class JsonRPCHandlerPlugin(Plugin):
    def __init__(self, methods: Dict[str, JsonRPCHandler]):
        self._methods = methods

    async def _get_jsonrpc_body(self, conn: Connection) -> dict:
        data = await conn.json()

        if data.get('jsonrpc', None) != '2.0' or 'id' not in data or 'method' not in data:
            raise BadJsonRPCRequestError()

        return {
            'id': data['id'],
            'jsonrpc': '2.0',
            'method': data['method'],
            'params': data.get('params', None)
        }

    async def _execute(self, request_id, method, params, method_params):
        try:
            if method_params is None:
                return await method(**params.params)
            elif not isinstance(method_params, dict):
                return await method(method_params, **params.params)
            else:
                return await method(**{**params.params, **method_params})
        except Exception as exception:
            if isinstance(exception, MachineJsonRPCError):
                raise exception

            raise JsonRPCInternalError(
                request_id=request_id,
                method_name=method,
                message=str(exception)
            )

    async def __call__(self, conn: Connection, params: Parameters):
        body = await self._get_jsonrpc_body(conn)
        method_params = body['params']
        method_name = body['method']
        del body['params']

        if method_name not in self._methods:
            raise JsonRPCMethodNotFoundError(method_name=method_name)

        handler = self._methods[method_name]

        async for conn, params in sequence(handler.plugins)()(conn, params):
            pass

        result = await self._execute(body['id'], handler.method, params, method_params)

        await conn.send_json(
            body={
                **body,
                'result': result
            },
            status_code=200,
            cookies={},
            headers={}
        )

        yield conn, params

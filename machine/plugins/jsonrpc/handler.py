from typing import List

from machine.plugin import Plugin
from machine.connection import Connection
from machine.types import PluginGenerator
from machine.utils import Either, Right, Left
from machine.exceptions.resources.jsonrpc import MachineJsonRPCError, BadJsonRPCRequestError


class JsonRPCHandlerPlugin(Plugin):
    def __init__(self, method):
        self._method = method

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

    async def _execute(self, params, method_params):
        if method_params is None:
            return await self._method(**params)
        elif not isinstance(method_params, dict):
            return await self._method(method_params, **params)
        else:
            return await self._method(**{**params, **method_params})

    async def __call__(self, conn: Connection, params: dict) -> Either:
        body = await self._get_jsonrpc_body(conn)
        method_params = body['params']
        method_name = body['method']

        if method_name != self._method.__name__:
            return Left()

        params = params.copy()
        del params['__path__']

        del body['params']

        try:
            result = await self._execute(params, method_params)
        except MachineJsonRPCError as e:
            body.update({'error': {'status_code': e.status_code, 'message': e.message}})
            await conn.send_json(
                body=body,
                status_code=e.status_code,
                headers={},
                cookies={},
            )
            return Right((conn, params))

        body.update({'result': result})
        await conn.send_json(
            body=body,
            status_code=200,
            headers={},
            cookies={}
        )

        return Right((conn, params))


class JsonRPCHandler:
    def __init__(self, plugins: List[PluginGenerator], handler):
        self._plugins = plugins
        self._handler = handler

    @property
    def handler(self):
        return self._handler

    @property
    def plugins(self):
        return self._plugins

    def __call__(self):
        return lambda: JsonRPCHandlerPlugin(method=self._handler)

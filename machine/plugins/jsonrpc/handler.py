from typing import List, Dict

from machine.plugin import Plugin
from machine.plugins.sequence import sequence
from machine.connection import Connection
from machine.types import PluginGenerator
from machine.utils import Either, Right, Left
from machine.exceptions.resources.jsonrpc import MachineJsonRPCError, BadJsonRPCRequestError, JsonRPCMethodNotFoundError


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

    async def _execute(self, method, params, method_params):
        if method_params is None:
            return await method(**params)
        elif not isinstance(method_params, dict):
            return await method(method_params, **params)
        else:
            return await method(**{**params, **method_params})

    async def __call__(self, conn: Connection, params: dict) -> Either:
        body = await self._get_jsonrpc_body(conn)
        method_params = body['params']
        method_name = body['method']
        del body['params']

        try:
            if method_name not in self._methods:
                raise JsonRPCMethodNotFoundError(method_name=method_name)

            handler = self._methods[method_name]

            if handler.plugins:
                plugin_result = await sequence(handler.plugins)()(conn, params)

                if plugin_result.is_left():
                    return plugin_result

                conn, params = plugin_result.value

            params = params.copy()
            del params['__path__']

            result = await self._execute(handler.method, params, method_params)
        except MachineJsonRPCError as e:
            body.update({'error': {'status_code': e.status_code, 'message': e.message}})
            await conn.send_json(
                body=body,
                status_code=e.status_code,
                headers={},
                cookies={},
            )
            return Right((conn, params))
        except Exception as e:
            raise e

        body.update({'result': result})
        await conn.send_json(
            body=body,
            status_code=200,
            headers={},
            cookies={}
        )

        return Right((conn, params))

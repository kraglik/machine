import json
from dataclasses import dataclass
from typing import Dict

from machine.connection import Connection
from machine.enums import HTTPMethod
from machine.exceptions.resource import BadRequestResourceError, MethodNotAllowedResourceError
from machine.exceptions.resources.jsonrpc import BadJsonRPCRequestError, JsonRPCMethodNotFoundError, \
    MachineJsonRPCError, MethodNotAllowedJsonRPCError, WrongJsonRPCParamsError
from machine.path import Path
from machine.plugin import PluginResult
from machine.resource import Resource
from machine.response import Response


@dataclass(frozen=True)
class JsonRPCMethod:
    method_name: str
    function: callable


class JsonRPCResource(Resource):
    def __init__(self, name: str, path: Path):
        super().__init__(name, path)
        self._methods: Dict[str, JsonRPCMethod] = {}

    @property
    def method(self):
        def wrapper(f):
            self._methods[f.__name__] = JsonRPCMethod(function=f, method_name=f.__name__)

        return wrapper

    async def __call__(self, conn: Connection, params: dict) -> PluginResult:
        status_code = 200
        error_message = None
        result = ''

        try:
            request_id, method_name, params = await self._parse_request(conn)
            method = self._get_method(method_name)

            result = await self._execute_method(method, conn, params)

        except (BadJsonRPCRequestError, WrongJsonRPCParamsError):
            raise BadRequestResourceError()

        except MethodNotAllowedJsonRPCError:
            raise MethodNotAllowedResourceError()

        except MachineJsonRPCError as e:
            status_code = e.status_code
            error_message = e.message
        
        if error_message:
            await self._send_jsonrpc_error(conn, request_id, error_message, method_name, status_code)
        else:
            if isinstance(result, Response):
                status_code = result.status_code
                result = result.body
            elif isinstance(result, (dict, float, int, str, bool, list)):
                status_code = 200

            await self._send_jsonrpc_response(conn, request_id, method_name, result)

        return conn, params
    
    async def _send_jsonrpc_error(self, conn: Connection, request_id: str, reason: str, method: str, status_code: int):
        return await conn.send_json(
            body=json.dumps({
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "error": reason
            }),
            status_code=status_code,
            headers=[]
        )

    async def _send_jsonrpc_response(self, conn: Connection, request_id: str, method: str, result):
        return await conn.send_json(
            body=json.dumps({
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "result": result
            }),
            status_code=200,
            headers=[]
        )

    async def _parse_request(self, conn: Connection):
        if conn.method != HTTPMethod.POST:
            raise MethodNotAllowedJsonRPCError()

        try:
            data = await conn.json()

            assert data['jsonrpc'] == '2.0'
            request_id = data['id']
            method_name = data['method']
            params = data.get('params', None)
        except Exception:
            raise BadJsonRPCRequestError()

        return request_id, method_name, params

    def _get_method(self, method_name):
        if method_name not in self._methods:
            raise JsonRPCMethodNotFoundError(method_name)

        return self._methods[method_name].function

    async def _execute_method(self, method, connection, params):
        if isinstance(params, dict):
            return await method(connection, **params)
        elif isinstance(params, (list, int, float, str, bool)):
            return await method(connection, params)

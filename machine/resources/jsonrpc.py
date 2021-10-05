import json
from dataclasses import dataclass
from typing import Dict, Union

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
    def __init__(self, name: str, path: Union[str, Path]):
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
        request_id = None
        method_name = None
        method_params = None

        try:
            request_id, method_name, method_params = await self._parse_request(conn)
            method = self._get_method(method_name)

            result = await self._execute_method(method, params, method_params)

        except (BadJsonRPCRequestError, WrongJsonRPCParamsError):
            raise BadRequestResourceError()

        except MethodNotAllowedJsonRPCError:
            raise MethodNotAllowedResourceError()

        except MachineJsonRPCError as e:
            status_code = e.status_code
            error_message = e.message
        
        if error_message:
            await self._send_jsonrpc_response(
                conn=conn,
                request_id=request_id,
                method=method_name,
                error=error_message,
                status_code=status_code
            )
        else:
            if isinstance(result, Response):
                assert result.content_type == 'application/json', \
                    "Only json responses are supported in JsonRPCResource"

                status_code = result.status_code
                result = result.body
            elif isinstance(result, (dict, float, int, str, bool, list)) or result is None:
                status_code = 200

            await self._send_jsonrpc_response(
                conn=conn,
                request_id=request_id,
                method=method_name,
                result=result,
                status_code=status_code
            )

        return conn, params

    async def _send_jsonrpc_response(
            self,
            conn: Connection,
            request_id: str,
            method: str,
            status_code: int,
            result: any = None,
            error: any = None
    ):
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
        }

        if error is not None:
            response.update({"error": error})
        else:
            response.update({"result": result})

        return await conn.send_json(
            body=json.dumps(response),
            status_code=status_code,
            headers={'connection': 'close'},
            cookies={}
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

    async def _execute_method(self, method, params, method_params):
        if isinstance(method_params, dict):
            return await method(**{**params, **method_params})
        elif isinstance(method_params, (list, int, float, str, bool)):
            return await method(method_params, **params)
        elif method_params is None:
            return await method(**params)

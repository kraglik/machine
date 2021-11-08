from typing import List, Dict, Callable

from machine.params import Parameters
from machine.plugin import Plugin
from machine.plugins.jsonrpc.types import RequestIDType
from machine.plugins.sequence import sequence
from machine.connection import Connection
from machine.plugin import PluginGenerator, PluginResult
from machine.types import JsonType
from machine.exceptions.plugins.jsonrpc import MachineJsonRPCError
from machine.exceptions.plugins.jsonrpc import JsonRPCInternalError
from machine.exceptions.plugins.jsonrpc import JsonRPCMethodNotFoundError
from machine.exceptions.plugins.jsonrpc import BadJsonRPCRequestError


class JsonRPCHandler:
    def __init__(
        self, plugins: List[PluginGenerator], method: Callable
    ) -> None:
        self._plugins = plugins
        self._method = method

    @property
    def method(self) -> Callable:
        return self._method

    @property
    def plugins(self) -> List[PluginGenerator]:
        return self._plugins


class JsonRPCHandlerPlugin(Plugin):
    def __init__(self, methods: Dict[str, JsonRPCHandler]) -> None:
        self._methods = methods

    async def _get_jsonrpc_body(self, conn: Connection) -> Dict:
        data = await conn.json()

        if (
            not isinstance(data, dict)
            or data.get("jsonrpc", None) != "2.0"
            or "id" not in data
            or "method" not in data
        ):
            raise BadJsonRPCRequestError()

        return {
            "id": data["id"],
            "jsonrpc": "2.0",
            "method": data["method"],
            "params": data.get("params", None),
        }

    async def _execute(
        self,
        request_id: RequestIDType,
        method_name: str,
        method: Callable,
        params: Parameters,
        method_params: Dict,
    ) -> JsonType:
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
                method_name=method_name,
                message=str(exception),
            )

    async def __call__(
        self, conn: Connection, params: Parameters
    ) -> PluginResult:
        body = await self._get_jsonrpc_body(conn)
        method_params = body["params"]
        method_name = body["method"]
        request_id = body["request_id"]
        del body["params"]

        if method_name not in self._methods:
            raise JsonRPCMethodNotFoundError(
                method_name=method_name, request_id=request_id
            )

        handler = self._methods[method_name]

        if handler.plugins:
            async for conn, params in sequence(handler.plugins)()(
                conn, params
            ):
                pass

        result = await self._execute(
            body["id"], method_name, handler.method, params, method_params
        )

        await conn.send_json(
            body={**body, "result": result},
            status_code=200,
            cookies={},
            headers={},
        )

        yield conn, params

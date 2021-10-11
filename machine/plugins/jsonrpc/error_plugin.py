from machine import Plugin, Connection
from machine.exceptions.plugins.jsonrpc import MachineJsonRPCError
from machine.exceptions.plugins.jsonrpc import MachineJsonRPCRequestError, MachineJsonRPCResponseError
from machine.params import Parameters
from machine.types import PluginGenerator


class JsonRPCErrorPlugin(Plugin):
    async def __call__(self, conn: Connection, params: Parameters):
        try:
            yield conn, params
        except MachineJsonRPCError as error:
            if isinstance(error, MachineJsonRPCRequestError):
                await conn.send_text(
                    body=error.message,
                    status_code=error.status_code
                )
            elif isinstance(error, MachineJsonRPCResponseError):
                await conn.send_json(
                    body={
                       "jsonrpc": "2.0",
                       "id": error.request_id,
                       "method": error.method_name,
                       "error": {
                           "message": error.message,
                           "status": error.error_code
                       }
                    },
                    status_code=error.status_code,
                    cookies={},
                    headers={}
                )

            yield conn, params


def jsonrpc_error_plugin() -> PluginGenerator:
    return lambda: JsonRPCErrorPlugin()

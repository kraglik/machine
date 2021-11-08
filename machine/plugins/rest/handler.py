from typing import List, Callable

from machine.plugin import Plugin
from machine.connection import Connection
from machine.types import PluginGenerator, PluginResult
from .request import Request
from .response import Response, TextResponse, JSONResponse
from machine.params import Parameters


class RESTHandlerPlugin(Plugin):
    def __init__(self, method: Callable) -> None:
        self._method = method

    async def __call__(self, conn: Connection, params: Parameters) -> PluginResult:
        request = Request.from_conn(conn, params)
        response = await self._method(request)

        if isinstance(response, (dict, list, int, float, bool)):
            response = JSONResponse(response)
        elif isinstance(response, str):
            response = TextResponse(response)

        assert isinstance(response, Response), "Unexpected return type for rest method"

        await conn.send_content(
            body=response.bytes(encoding=response.encoding),
            status_code=response.status_code,
            headers=response.headers,
            cookies=response.cookies,
            content_type=response.content_type,
        )

        yield conn, params


class RESTHandler:
    def __init__(self, plugins: List[PluginGenerator], handler: Callable):
        self._plugins = plugins
        self._handler = handler

    @property
    def handler(self) -> Callable:
        return self._handler

    @property
    def plugins(self) -> List[PluginGenerator]:
        return self._plugins

    def __call__(self) -> Callable[[], Plugin]:
        return lambda: RESTHandlerPlugin(method=self._handler)

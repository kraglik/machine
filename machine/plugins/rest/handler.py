from typing import List

from machine.plugin import Plugin
from machine.connection import Connection
from machine.types import PluginGenerator
from .request import Request
from .response import Response
from machine.params import Parameters


class RESTHandlerPlugin(Plugin):
    def __init__(self, method):
        self._method = method

    async def __call__(self, conn: Connection, params: Parameters):
        request = Request.from_conn(conn, params)

        response = await self._method(request, params.params)
        assert isinstance(response, Response), "Unexpected return type for rest method"

        await conn.send_content(
            body=response.bytes(encoding=response.encoding),
            status_code=response.status_code,
            headers=response.headers,
            cookies=response.cookies,
            content_type=response.content_type
        )

        yield conn, params


class RESTHandler:
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
        return lambda: RESTHandlerPlugin(method=self._handler)

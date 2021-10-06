from typing import List

from machine.plugin import Plugin
from machine.connection import Connection
from machine.types import PluginGenerator
from machine.utils import Either, Right
from .request import Request
from .response import Response


class RESTHandlerPlugin(Plugin):
    def __init__(self, method):
        self._method = method

    async def __call__(self, conn: Connection, params: dict) -> Either:
        request = Request.from_conn(conn, params)

        method_params = params.copy()
        del method_params['__path__']

        response = await self._method(request, method_params)
        assert isinstance(response, Response), "Unexpected return type for rest method"

        await conn.send_content(
            body=response.bytes(encoding=response.encoding),
            status_code=response.status_code,
            headers=response.headers,
            cookies=response.cookies,
            content_type=response.content_type
        )

        return Right((conn, params))


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

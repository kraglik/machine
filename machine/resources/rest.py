from functools import partial
from typing import Union

from machine.connection import Connection
from machine.exceptions.resource import MethodNotAllowedResourceError
from machine.path import Path
from machine.plugin import PluginResult
from machine.resource import Resource
from machine.response import Response, TextResponse
from machine.request import Request


class HttpResource(Resource):
    def __init__(self, name: str, path: Union[str, Path]):
        super().__init__(name, path)
        self._method_table = {
            'GET': None,
            'POST': None,
            'PUT': None,
            'UPDATE': None,
            'DELETE': None,
            'HEAD': None,
        }

    def _method_setter(self, method: str) -> callable:
        def wrapper(handler):
            self._method_table[method] = handler
            return handler
        return wrapper

    @property
    def get(self):
        return self._method_setter('GET')

    @property
    def post(self):
        return self._method_setter('POST')

    @property
    def put(self):
        return self._method_setter('PUT')

    @property
    def update(self):
        return self._method_setter('UPDATE')

    @property
    def delete(self):
        return self._method_setter('DELETE')

    @property
    def head(self):
        return self._method_setter('HEAD')

    async def __call__(self, conn: Connection, params: dict) -> PluginResult:
        method = self._method_table.get(conn.method.value, None)

        if method is not None:
            result = await method(request=Request.from_conn(conn), **params)

            if isinstance(result, str):
                result = TextResponse(body=result, status_code=200)

            await conn.send_content(
                body=result.bytes(),
                content_type=result.content_type,
                headers={**(result.headers or {}), 'connection': 'close'},
                cookies=result.cookies,
                status_code=result.status_code
            )

            return conn, params

        raise MethodNotAllowedResourceError()

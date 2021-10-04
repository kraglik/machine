from functools import partial
from typing import Union

from machine.connection import Connection
from machine.exceptions.resource import MethodNotAllowedResourceError
from machine.path import Path
from machine.plugin import PluginResult
from machine.resource import Resource
from machine.response import Response
from machine.request import Request


class RESTResource(Resource):
    def __init__(self, name: str, path: Union[str, Path]):
        super().__init__(name, path)
        self._method_table = {
            'GET': partial(self.get),
            'POST': partial(self.post),
            'PUT': partial(self.put),
            'UPDATE': partial(self.update),
            'DELETE': partial(self.delete),
            'HEAD': partial(self.head),
        }

    async def __call__(self, conn: Connection, params: dict) -> PluginResult:
        method = self._method_table.get(conn.method.value, None)

        if method is not None:
            result = await method(request=Request.from_conn(conn), **params)

            if isinstance(result, str):
                await conn.send_text(
                    body=result,
                    status_code=200,
                    headers=[('connection', b'close')]
                )
            elif isinstance(result, Response):
                await conn.send_head(
                    content_type=result.content_type,
                    status_code=result.status_code,
                    headers=[('connection', b'close')]
                )
                await conn.send_body(body=result.bytes())

        return conn, params

    async def get(self, *args, **kwargs) -> Response:
        raise MethodNotAllowedResourceError()

    async def post(self, *args, **kwargs) -> Response:
        raise MethodNotAllowedResourceError()

    async def put(self, *args, **kwargs) -> Response:
        raise MethodNotAllowedResourceError()

    async def update(self, *args, **kwargs) -> Response:
        raise MethodNotAllowedResourceError()

    async def head(self, *args, **kwargs) -> Response:
        raise MethodNotAllowedResourceError()

    async def delete(self, *args, **kwargs) -> Response:
        raise MethodNotAllowedResourceError()

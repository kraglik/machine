from functools import partial

from machine.connection import Connection
from machine.path import Path
from machine.plugin import PluginResult
from machine.resource import Resource
from machine.response import Response


class RESTResource(Resource):
    def __init__(self, name: str, path: Path):
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
            result = await method(conn, params)

            if isinstance(result, str):
                await conn.send_text(body=result, status_code=200, headers=[])
            elif isinstance(result, Response):
                await conn.send_head(content_type=result.content_type, status_code=result.status_code)
                await conn.send_body(body=result.body)

        return conn, params

    async def get(self, conn: Connection, params: dict):
        pass

    async def post(self, conn: Connection, params: dict):
        pass

    async def put(self, conn: Connection, params: dict):
        pass

    async def update(self, conn: Connection, params: dict):
        pass

    async def head(self, conn: Connection, params: dict):
        pass

    async def delete(self, conn: Connection, params: dict):
        pass

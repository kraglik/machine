from example.infrastructure.db.database import Database
from machine import Request
from machine.resources import RESTResource

from example.api.scopes import api_v2
from machine.response import Response


@api_v2.resource(name='hello', path='/hello/{name}')
class SimpleHelloResource(RESTResource):
    async def get(self, request: Request, name: str) -> Response:
        request.conn.put_cookie('Bearer', 'blah')
        return Response.html(
            status_code=200,
            body=f"""
            <h1>Hello, {name}</h1></br>
            """
        )

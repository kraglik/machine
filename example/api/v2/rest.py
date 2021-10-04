from example.infrastructure.db.database import Database
from machine import Request
from machine.resources import RESTResource
from machine import start, slug, end

from example.api.scopes import api_v2
from machine.response import Response


@api_v2.resource(name='hello', path=start/'hello'/slug('name') + end)
class SimpleHelloResource(RESTResource):
    async def get(self, request: Request, name: str) -> Response:
        return Response.html(
            status_code=200,
            body=f"""
            <h1>Hello, {name}</h1></br>
            """
        )

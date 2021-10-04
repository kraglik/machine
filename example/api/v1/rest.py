from example.infrastructure.db.database import Database
from machine import Request
from machine.resources import RESTResource
from machine import start, slug, end

from example.api.scopes import api_v1
from machine.response import Response


@api_v1.resource(name='hello', path=start/'hello'/slug('name') + end)
class HelloResource(RESTResource):
    async def get(self, request: Request, name: str, db: Database) -> Response:
        print(name)
        return Response.html(
            status_code=200,
            body=f"""
            <h1>Hello, {name}</h1></br>
            <div>Items in database:</div></br>
            <div>{str(db.items)}</div>
            """
        )


@api_v1.resource(name='echo', path=start/'echo' + end)
class EchoResource(RESTResource):
    async def post(self, request: Request, db: Database) -> Response:
        return Response(
            content_type=request.content_type,
            status_code=200,
            body=await request.body()
        )

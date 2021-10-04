from example.infrastructure.db.database import Database
from machine import Request
from machine.resources import RESTResource

from example.api.scopes import api_v1
from machine.response import Response


@api_v1.resource(name='hello', path='/hello/{name}$')
class HelloResource(RESTResource):
    async def get(self, request: Request, name: str, db: Database) -> Response:
        return Response.html(
            status_code=200,
            body=f"""
            <h1>Hello, {name}</h1></br>
            <div>Items in database:</div></br>
            <div>{str(db.items)}</div>
            """
        )


@api_v1.resource(name='echo', path='/echo$')
class EchoResource(RESTResource):
    async def post(self, request: Request, db: Database) -> Response:
        return Response(
            content_type=request.content_type,
            status_code=200,
            body=await request.body()
        )


@api_v1.resource(name='query', path='/query_params$')
class QueryParamsResource(RESTResource):
    async def get(self, request: Request, db: Database) -> Response:
        return Response.html(
            status_code=200,
            body=f"""
                <h1>Query params:</h1></br>
                <div>{str(request.query_params)}</div>
            """
        )

from example.infrastructure.db.database import Todos
from machine import Request
from machine.resources import RESTResource

from example.api.scopes import api
from machine.response import Response


@api.resource(name='hello', path='/todo$')
class TodoResource(RESTResource):
    async def get(self, request: Request, db: Todos) -> Response:
        return Response.json(
            {
                "todos": db.all
            },
            status_code=200
        )

    async def post(self, request: Request, db: Todos) -> Response:
        todo = await request.text()

        db.add(todo)

        return Response.json(
            {
                "todo": todo,
                "status": "added"
            },
            status_code=200
        )

    async def delete(self, request: Request, db: Todos) -> Response:
        todo = await request.text()

        db.remove(todo)

        return Response.json(
            {
                "todo": todo,
                "status": "deleted"
            },
            status_code=200
        )

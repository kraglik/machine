from example.infrastructure.db.database import Todos
from machine import Request
from machine.resources import HttpResource

from example.api.scopes import api
from machine.response import Response, JSONResponse


r = api.add_resource(HttpResource(name='hello', path='/todo$'))


@r.get
async def todo_list_get(request: Request, db: Todos) -> Response:
    return JSONResponse(
        {
            "todos": db.all
        },
        status_code=200
    )


@r.post
async def todo_create(request: Request, db: Todos) -> Response:
    todo = await request.text()

    db.add(todo)

    return JSONResponse(
        {
            "todo": todo,
            "status": "added"
        },
        status_code=200
    )


@r.delete
async def todo_delete(request: Request, db: Todos) -> Response:
    todo = await request.text()

    db.remove(todo)

    return JSONResponse(
        {
            "todo": todo,
            "status": "deleted"
        },
        status_code=200
    )

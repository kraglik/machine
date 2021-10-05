from example.infrastructure.db.database import Todos
from machine import Request
from machine.resources import HttpResource

from example.api.scopes import api
from machine.response import Response, JSONResponse


todo_r = api.add(HttpResource(name='todo_rest', path='/todo$'))


@todo_r.get
async def todo_list_get(request: Request, db: Todos) -> Response:
    return JSONResponse(
        {
            "todos": await db.all()
        },
        status_code=200
    )


@todo_r.post
async def todo_create(request: Request, db: Todos) -> Response:
    todo = await request.text()

    await db.add(todo)

    return JSONResponse(
        {
            "todo": todo,
            "status": "added"
        },
        status_code=200
    )


@todo_r.delete
async def todo_delete(request: Request, db: Todos) -> Response:
    todo = await request.text()

    await db.remove(todo)

    return JSONResponse(
        {
            "todo": todo,
            "status": "deleted"
        },
        status_code=200
    )

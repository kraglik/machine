import datetime

from example.infrastructure.db.database import Todos
from example.infrastructure.db.session import session

from machine.plugins.rest.request import Request
from machine.plugins import RESTResource, dependency
from machine.plugins.rest.response import Response, JSONResponse, HTMLResponse


todo_r = RESTResource()
name_r = RESTResource()

db_plugin = dependency("db", session)


@todo_r.get(plugins=[db_plugin])
async def todo_list_get(request: Request) -> Response:
    db: Todos = request.params["db"]
    return JSONResponse({"todos": await db.all()}, status_code=200)


@todo_r.post(plugins=[db_plugin])
async def todo_create(request: Request) -> Response:
    db: Todos = request.params["db"]
    todo = await request.text()

    await db.add(todo)

    return JSONResponse({"todo": todo, "status": "added"}, status_code=200)


@todo_r.delete(plugins=[db_plugin])
async def todo_delete(request: Request) -> Response:
    db: Todos = request.params["db"]
    todo = await request.text()

    await db.remove(todo)

    return JSONResponse({"todo": todo, "status": "deleted"}, status_code=200)


@name_r.get(plugins=[db_plugin])
async def greet(request: Request) -> Response:
    db: Todos = request.params["db"]
    name: str = request.path_params["name"]

    todos = await db.all()

    now = datetime.datetime.now().astimezone().strftime("%d-%m-%Y %T %z")

    return HTMLResponse(
        f"""
            <h1>Hello, {name}!</h1></br>
            <h2>Here are your todos:</h2></br>
            <ul>
        """
        + "".join(f"<li>{todo}</li>" for todo in todos)
        + "</ul>"
        + f"""
        </br>
        Server time is <b>{now}</b>
        """
    )

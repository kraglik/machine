from example.infrastructure.db.database import Todos
from example.infrastructure.db.session import session

from machine.plugins import JsonRPCResource, dependency


public = JsonRPCResource()

db_plugin = dependency('db', session)


@public.method(plugins=[db_plugin])
async def get_todos(db: Todos, *args, **kwargs) -> dict:
    return {
        "todos": await db.all()
    }


@public.method(plugins=[db_plugin])
async def delete_todo(db: Todos, todo: str, *args, **kwargs) -> dict:
    await db.remove(todo)

    return {
        "todo": todo,
        "status": "deleted"
    }


@public.method(plugins=[db_plugin])
async def add_todo(db: Todos, todo: str, *args, **kwargs) -> dict:
    await db.add(todo)

    return {
        "todo": todo,
        "status": "added"
    }

from example.infrastructure.db.database import Todos
from machine.resources import JsonRPCResource

from example.api.scopes import api


rpc = api.add(JsonRPCResource(name='todo_jsonrpc', path='/public/jsonrpc$'))


@rpc.method
async def get_todos(db: Todos, *args, **kwargs) -> dict:
    return {
        "todos": await db.all()
    }


@rpc.method
async def delete_todo(db: Todos, todo: str, *args, **kwargs) -> dict:
    await db.remove(todo)

    return {
        "todo": todo,
        "status": "deleted"
    }


@rpc.method
async def add_todo(db: Todos, todo: str, *args, **kwargs) -> dict:
    await db.add(todo)

    return {
        "todo": todo,
        "status": "added"
    }

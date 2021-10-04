from machine import Connection, PluginResult

from .database import Todos

db = Todos()


async def session_constructor(conn: Connection, params: dict) -> Todos:
    return db


async def session_destructor(conn: Connection, db: Todos, params: dict) -> PluginResult:
    return conn, params

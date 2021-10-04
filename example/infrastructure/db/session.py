from machine import Connection, PluginResult

from .database import Database

db = Database(['a', 'b', 'c'])


async def session_constructor(conn: Connection, params: dict) -> Database:
    return db


async def session_destructor(conn: Connection, db: Database, params: dict) -> PluginResult:
    return conn, params

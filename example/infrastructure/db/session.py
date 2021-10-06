from machine import Connection, PluginResult

from .database import Todos

db = Todos()


async def session():
    yield db

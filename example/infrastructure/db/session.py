from typing import AsyncGenerator

from .database import Todos

db = Todos()


async def session() -> AsyncGenerator[Todos, None]:
    yield db

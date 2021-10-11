from .database import Todos

db = Todos()


async def session():
    yield db

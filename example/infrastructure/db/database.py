import asyncio


class Todos:
    def __init__(self):
        self.__todos = []

    async def add(self, todo: str):
        await asyncio.sleep(0)
        self.__todos.append(todo)

    async def remove(self, todo: str):
        await asyncio.sleep(0)
        self.__todos.remove(todo)

    async def clear(self):
        await asyncio.sleep(0)
        self.__todos.clear()

    async def all(self):
        await asyncio.sleep(0)
        return self.__todos

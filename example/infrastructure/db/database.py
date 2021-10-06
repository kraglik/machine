import asyncio


class Todos:
    def __init__(self):
        self._todos = []

    async def add(self, todo: str):
        await asyncio.sleep(0)
        self._todos.append(todo)

    async def remove(self, todo: str):
        await asyncio.sleep(0)
        self._todos.remove(todo)

    async def clear(self):
        await asyncio.sleep(0)
        self._todos.clear()

    async def all(self):
        await asyncio.sleep(0)
        return self._todos

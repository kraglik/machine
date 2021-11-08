import asyncio
from typing import List


class Todos:
    def __init__(self) -> None:
        self._todos: List[str] = []

    async def add(self, todo: str) -> None:
        await asyncio.sleep(0)
        self._todos.append(todo)

    async def remove(self, todo: str) -> None:
        await asyncio.sleep(0)
        self._todos.remove(todo)

    async def clear(self) -> None:
        await asyncio.sleep(0)
        self._todos.clear()

    async def all(self) -> List[str]:
        await asyncio.sleep(0)
        return self._todos

class Todos:
    def __init__(self):
        self.__todos = []

    def add(self, todo: str):
        self.__todos.append(todo)

    def remove(self, todo: str):
        self.__todos.remove(todo)

    def clear(self):
        self.__todos.clear()

    @property
    def all(self):
        return self.__todos

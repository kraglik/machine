from typing import List, Optional

from machine.connection import Connection
from machine.plugin import Plugin


class accepts(Plugin):

    def __init__(self, protocols: List[str]):
        self.__protocols = protocols

    def __call__(self, conn: Connection) -> Optional[Connection]:

        if connection.type not in self.__protocols:
            return None

        return connection

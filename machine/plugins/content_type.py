from typing import Optional

from machine.connection import Connection
from machine.plugin import Plugin


class content_type(Plugin):

    def __init__(self, ct: str):
        self.__content_type = ct

    def __call__(self, conn: Connection) -> Optional[Connection]:
        if 'content-type' not in connection.headers \
                or connection.headers['content-type'] != self.__content_type:
            return None

        return connection

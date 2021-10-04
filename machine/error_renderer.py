from abc import ABC, abstractmethod
from typing import Union, Optional

from .connection import Connection
from .exceptions.machine import MachineError


class ErrorRenderer(ABC):
    @abstractmethod
    async def render(
            self,
            conn: Connection,
            error: Union[Exception, MachineError, str],
            status_code: Optional[int] = None
    ):
        raise NotImplementedError


class DefaultErrorRenderer(ErrorRenderer):

    NOT_FOUND_404 = """
    <div><h1>404 NOT FOUND: {message}</h1></div>
    """

    INTERNAL_ERROR_500 = """
    <div><h1>500 INTERNAL SERVER ERROR</h1></div>
    """

    METHOD_NOT_ALLOWED_405 = """
    <div><h1>405 METHOD NOT ALLOWED: {message}</h1></div>
    """

    BAD_REQUEST_400 = """
    <div><h1>400 BAD REQUEST: {message}</h1></div>
    """

    FORBIDDEN_403 = """
    <div><h1>403 FORBIDDEN: {message}</h1></div>
    """

    def __init__(self):
        self.__errors = {
            400: self.BAD_REQUEST_400,
            403: self.FORBIDDEN_403,
            404: self.NOT_FOUND_404,
            405: self.METHOD_NOT_ALLOWED_405,
            500: self.INTERNAL_ERROR_500
        }

    async def render(
            self,
            conn: Connection,
            error: Union[Exception, MachineError, str],
            status_code: Optional[int] = None
    ):

        if not status_code and not isinstance(error, MachineError):
            status_code = 500

        status_code = status_code or error.status_code

        message = error if isinstance(error, str) else \
            (error.message if isinstance(error, MachineError) else 'Unexpected error')

        await conn.send_html(
            body=self.__errors[status_code].format(message=message),
            status_code=status_code,
            headers=[]
        )

from abc import ABC, abstractmethod
from typing import Union, Optional

from machine import Connection
from machine.exceptions.machine import MachineError


class ErrorRenderer(ABC):
    @abstractmethod
    async def render(
        self,
        conn: Connection,
        error: Union[Exception, MachineError, str],
        status_code: Optional[int] = None,
    ) -> None:
        raise NotImplementedError


class DefaultErrorRenderer(ErrorRenderer):

    NOT_FOUND_404 = "404 Not Found"
    INTERNAL_ERROR_500 = "500 Internal Server Error"
    METHOD_NOT_ALLOWED_405 = "405 Method Not Allowed"
    BAD_REQUEST_400 = "400 Bad Request"
    FORBIDDEN_403 = "403 Forbidden"
    CONFLICT_409 = "409 Conflict"

    def __init__(self) -> None:
        self._errors = {
            400: self.BAD_REQUEST_400,
            403: self.FORBIDDEN_403,
            404: self.NOT_FOUND_404,
            405: self.METHOD_NOT_ALLOWED_405,
            409: self.CONFLICT_409,
            500: self.INTERNAL_ERROR_500,
        }

    async def render(
        self,
        conn: Connection,
        error: Union[Exception, MachineError, str],
        status_code: Optional[int] = None,
    ) -> None:
        if status_code is None and not isinstance(error, MachineError):
            status_code = 500

        elif isinstance(error, MachineError):
            status_code = status_code or error.status_code

        await conn.send_text(
            body=self._errors[status_code or 500],
            status_code=status_code or 500,
            headers={},
            cookies={},
        )

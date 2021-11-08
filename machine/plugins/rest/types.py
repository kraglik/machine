from typing import Callable, Union, Awaitable

from machine.plugins.rest import Request, Response
from machine.types import BodyType

RESTResponse = Union[BodyType, Response]
RESTMethod = Callable[[Request], Awaitable[RESTResponse]]

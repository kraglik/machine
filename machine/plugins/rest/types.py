from typing import Callable, Union, Awaitable

from machine.plugins.rest.request import Request
from machine.plugins.rest.response import Response

from machine.types import BodyType

RESTResponse = Union[BodyType, Response]
RESTMethod = Callable[[Request], Awaitable[RESTResponse]]

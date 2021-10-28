import typing

from machine.connection import Connection
from machine.params import Parameters

Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]

ASGIApp = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]

PluginType = typing.Callable[[Connection, Parameters], typing.AsyncIterator[typing.Tuple[Connection, Parameters]]]
PluginGenerator = typing.Callable[[], PluginType]

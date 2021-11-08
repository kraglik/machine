import typing

from multidict import MultiDict

from machine.connection import Connection
from machine.params import Parameters

Address = typing.Tuple[str, int]

JsonType = typing.Union[int, float, str, bool, dict, list]
BodyType = typing.Union[JsonType, bytes, MultiDict]

Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[
    [], typing.Coroutine[None, None, typing.Dict[typing.Union[str, bytes], BodyType]]
]
Send = typing.Callable[[BodyType], typing.Coroutine[None, None, None]]

ASGIApp = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]

PluginResult = typing.AsyncGenerator[typing.Tuple[Connection, Parameters], None]
PluginType = typing.Callable[[Connection, Parameters], PluginResult]
PluginGenerator = typing.Callable[[], PluginType]

StartupHandler = typing.Union[typing.Callable[[], typing.Coroutine[None, None, None]]]
ShutdownHandler = typing.Union[typing.Callable[[], typing.Coroutine[None, None, None]]]

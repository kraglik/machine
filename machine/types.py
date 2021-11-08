import typing

from multidict import MultiDict

Address = typing.Tuple[str, int]

JsonType = typing.Union[
    int,
    float,
    str,
    bool,
    typing.Dict[typing.Any, typing.Any],
    typing.List[typing.Any],
]
BodyType = typing.Union[JsonType, bytes, MultiDict]

Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[
    [],
    typing.Coroutine[
        None, None, typing.Dict[typing.Union[str, bytes], BodyType]
    ],
]
Send = typing.Callable[[BodyType], typing.Coroutine[None, None, None]]

ASGIApp = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]

StartupHandler = typing.Union[
    typing.Callable[[], typing.Coroutine[None, None, None]]
]
ShutdownHandler = typing.Union[
    typing.Callable[[], typing.Coroutine[None, None, None]]
]

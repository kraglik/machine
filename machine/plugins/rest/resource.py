from typing import Optional, Dict, List, Callable

from machine.resource import Resource
from machine.plugins.sequence import sequence
from machine.plugins.conn_type import conn_type
from machine.plugins.path import path
from .error_plugin import rest_error_plugin
from .handler import RESTHandler
from machine.plugin import PluginGenerator, PluginType
from .error_renderer import ErrorRenderer, DefaultErrorRenderer
from .method_selector import method_selector
from .types import RESTMethod


class RESTResource(Resource):
    def __init__(
        self, path: Optional[str] = None, error_renderer: ErrorRenderer = None
    ):
        self._method_table: Dict[str, Optional[RESTHandler]] = {
            "GET": None,
            "POST": None,
            "PUT": None,
            "UPDATE": None,
            "DELETE": None,
            "HEAD": None,
        }
        self._path = path
        self._error_renderer = error_renderer or DefaultErrorRenderer()

    def __call__(self) -> PluginType:
        prefix = [] if self._path is None else [path(self._path)]
        prefix += [conn_type("http"), rest_error_plugin(self._error_renderer)]

        return sequence(
            [
                *prefix,
                method_selector(
                    {
                        method_name: sequence([*handler.plugins, handler()])
                        for method_name, handler in self._method_table.items()
                        if handler is not None
                    }
                ),
            ]
        )()

    def _method_setter(
        self, method_name: str, plugins: List[PluginGenerator] = None
    ) -> Callable[[Callable], Callable]:
        def wrapper(handler: Callable) -> Callable:
            self._method_table[method_name] = RESTHandler(
                plugins=plugins or [], handler=handler
            )
            return handler

        return wrapper

    def get(
        self, plugins: List[PluginGenerator] = None
    ) -> Callable[[RESTMethod], RESTMethod]:
        return self._method_setter("GET", plugins or [])

    def post(
        self, plugins: List[PluginGenerator] = None
    ) -> Callable[[RESTMethod], RESTMethod]:
        return self._method_setter("POST", plugins or [])

    def put(
        self, plugins: List[PluginGenerator] = None
    ) -> Callable[[RESTMethod], RESTMethod]:
        return self._method_setter("PUT", plugins or [])

    def update(
        self, plugins: List[PluginGenerator] = None
    ) -> Callable[[RESTMethod], RESTMethod]:
        return self._method_setter("UPDATE", plugins or [])

    def delete(
        self, plugins: List[PluginGenerator] = None
    ) -> Callable[[RESTMethod], RESTMethod]:
        return self._method_setter("DELETE", plugins or [])

    def head(
        self, plugins: List[PluginGenerator] = None
    ) -> Callable[[Callable], Callable]:
        return self._method_setter("HEAD", plugins or [])

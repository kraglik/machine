from typing import Optional, Dict, List

from machine.resource import Resource
from machine.plugin import Plugin
from machine.plugins.options import options
from machine.plugins.sequence import sequence
from machine.plugins.conn_type import conn_type
from machine.plugins.content_type import content_type
from machine.plugins.method import method
from machine.plugins.path import path
from .error_plugin import jsonrpc_error_plugin
from .handler import JsonRPCHandler, JsonRPCHandlerPlugin
from machine.types import PluginGenerator
from ..rest.error_plugin import rest_error_plugin
from ..rest.error_renderer import DefaultErrorRenderer


class JsonRPCResource(Resource):

    _disallowed_methods = ['GET', 'PUT', 'HEAD', 'DELETE', 'UPDATE']

    def __init__(self, path: Optional[str] = None):
        self._method_table: Dict[str, Optional[JsonRPCHandler]] = {}
        self._path = path

    def _handler(self):
        return lambda: JsonRPCHandlerPlugin(methods=self._method_table)

    def __call__(self) -> Plugin:
        prefix = [
            conn_type('http'),
            rest_error_plugin(renderer=DefaultErrorRenderer()),
            method('POST', only=True),
            content_type('application/json'),
            jsonrpc_error_plugin(),
        ]
        prefix += [] if self._path is None else [path(self._path)]

        return sequence([
            *prefix,
            self._handler()
        ])()

    def method(self, plugins: List[PluginGenerator] = None):
        def wrapper(handler):
            self._method_table[handler.__name__] = JsonRPCHandler(plugins=plugins or [], method=handler)
            return handler

        return wrapper

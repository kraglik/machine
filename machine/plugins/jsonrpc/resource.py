from typing import Optional, Dict, List

from machine.resource import Resource
from machine.plugin import Plugin
from machine.plugins.options import options
from machine.plugins.sequence import sequence
from machine.plugins.conn_type import conn_type
from machine.plugins.content_type import content_type
from machine.plugins.method import method
from machine.plugins.path import path
from .handler import JsonRPCHandler
from machine.types import PluginGenerator


class JsonRPCResource(Resource):

    _disallowed_methods = ['GET', 'PUT', 'HEAD', 'DELETE', 'UPDATE']

    def __init__(self, path: Optional[str] = None):
        self._method_table: Dict[str, Optional[JsonRPCHandler]] = {}
        self._path = path

    def __call__(self) -> Plugin:
        prefix = [
            conn_type('http'),
            method('POST', only=True),
            content_type('application/json'),
        ]
        prefix += [] if self._path is None else [path(self._path)]

        forbidden_methods = [
            method(method_name, allowed=False)
            for method_name in self._disallowed_methods
        ]

        return sequence([
            *prefix,
            options([
                sequence([
                    *handler.plugins,
                    handler()
                ])
                for method_name, handler
                in self._method_table.items()
            ] + forbidden_methods)
        ])()

    def method(self, plugins: List[PluginGenerator] = None):
        def wrapper(handler):
            self._method_table[handler.__name__] = JsonRPCHandler(plugins=plugins or [], handler=handler)
            return handler

        return wrapper

from machine.plugin import Plugin
from machine.connection import Connection
from machine.params import Parameters
from .error_renderer import ErrorRenderer
from machine.exceptions.machine import MachineError
from machine.plugin import PluginGenerator, PluginResult


class RESTErrorPlugin(Plugin):
    def __init__(self, renderer: ErrorRenderer):
        self._renderer = renderer

    async def __call__(
        self, conn: Connection, params: Parameters
    ) -> PluginResult:
        try:
            yield conn, params
        except Exception as e:
            status_code = e.status_code if isinstance(e, MachineError) else 500
            await self._renderer.render(conn, status_code=status_code, error=e)
            yield conn, params


def rest_error_plugin(renderer: ErrorRenderer) -> PluginGenerator:
    return lambda: RESTErrorPlugin(renderer=renderer)

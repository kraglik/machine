import logging
import uvicorn

from yarl import URL

from .error_pages import NOT_FOUND_404, INTERNAL_ERROR_500, METHOD_NOT_ALLOWED_405, BAD_REQUEST_400
from .exceptions.machine import MachineError
from .scope import Scope
from .path import Path
from .connection import Connection


ERROR_PAGES = {
    404: NOT_FOUND_404,
    500: INTERNAL_ERROR_500,
    400: BAD_REQUEST_400,
    405: METHOD_NOT_ALLOWED_405

}


logger = logging.getLogger('machine')


class Machine:

    def __init__(self, error_pages: dict = ERROR_PAGES):
        self.__scopes = []
        self.__error_pages = error_pages

    def scope(self, path: Path) -> Scope:
        scope = Scope(path)
        self.__scopes.append(scope)
        return scope

    def add_scope(self, scope: Scope) -> Scope:
        self.__scopes.append(scope)
        return scope

    async def __call__(self, conn_scope, receive, send):
        conn = Connection(scope=conn_scope, send=send, receive=receive)

        if conn.type == 'lifespan':
            return

        try:
            found = False

            for scope in self.__scopes:
                used_conn, params = await scope(conn, {'path': conn.path})

                if used_conn is not None:
                    found = True
                    break

            if not found:
                await conn.send_html_head(status_code=404, headers=[])
                await conn.send_body(self.__error_pages[404])

        except MachineError as e:
            logger.error(f'Got exception while handling request: {e}', exc_info=e)
            await conn.send_html_head(status_code=e.status_code, headers=[])
            await conn.send_body(self.__error_pages[e.status_code])

        except Exception as e:
            logger.error(f'Got exception while handling request: {e}', exc_info=e)
            await conn.send_html_head(status_code=500, headers=[])
            await conn.send_body(self.__error_pages[500])

        if not conn.closed:
            await conn.close()

    def run(self, host: str = '127.0.0.1', port: int = 8000, log_level: str = 'info'):
        uvicorn.run(self, host=host, port=port, log_level=log_level)

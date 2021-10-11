from dataclasses import dataclass
from typing import Dict, Tuple, Union

from machine.connection import Connection
from machine.enums import HTTPMethod
from machine.params import Parameters


@dataclass(frozen=True)
class Request:
    conn: Connection
    url: str
    path: str
    cookies: Dict[str, str]
    headers: Dict[str, str]
    method: HTTPMethod
    host: Tuple[str, int]
    client: Tuple[str, int]
    http_version: str
    content_type: str
    query_params: Dict[str, str]
    path_params: Dict[str, str]

    async def body(self) -> bytes:
        return await self.conn.body()

    async def text(self, encoding: str = 'utf-8') -> str:
        return await self.conn.text(encoding=encoding)

    async def json(self, encoding: str = 'utf-8') -> Union[bool, float, int, str, list, dict]:
        return await self.conn.json(encoding=encoding)

    async def next_chunk(self) -> bytes:
        return await self.conn.next_chunk()

    @property
    def has_next_chunk(self):
        return self.conn.has_next_chunk

    @staticmethod
    def from_conn(conn: Connection, params: Parameters) -> 'Request':
        return Request(
            conn=conn,
            url=conn.url,
            path=conn.path,
            cookies={
                cookie: value.decode('utf-8')
                for cookie, value in conn.request_cookies.items()
            },
            headers={
                header: value.decode('utf-8')
                for header, value in conn.request_headers.items()
            },
            method=conn.method,
            host=(conn.server_host, conn.server_port),
            client=(conn.client_host, conn.client_port),
            http_version=conn.http_version,
            content_type=conn.request_headers.get('content-type', b'text/plain').decode('utf-8'),
            query_params=conn.query_params,
            path_params=params.path.params
        )

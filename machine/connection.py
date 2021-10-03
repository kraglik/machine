import json

from yarl import URL
from typing import Union, Tuple, List, Dict

from .enums import SendEventType, HTTPMethod
from .exceptions import ConnectionClosed


END_EVENT = {
    'http': SendEventType.HTTP_RESPONSE_BODY
}


class Connection:
    def __init__(self, scope, send, receive):
        self.__scope = scope
        self.__send = send
        self.__receive = receive
        self.__body = b''
        self.__has_next_chunk = True
        self.__url = URL(scope.get('path', ''))
        self.__path = self.__url.path
        self.__method = HTTPMethod(scope.get('method', 'UNKNOWN'))
        self.__host = ''.join([str(x) for x in scope.get('server', [])])
        self.__client = ''.join([str(x) for x in scope.get('client', [])])
        self.__http_version = scope.get('http_version')
        self.__type = scope.get('type')
        self.__scheme = scope.get('scheme')
        self.__closed = False
        self.__request_headers = {
            header.decode('utf-8'): value
            for header, value
            in scope.get('headers', [])
            if header != b'cookie'
        }
        self.__response_headers = {}
        self.__request_cookies = {
            cookie[0]: cookie[1]
            for header, cookie in scope.get('headers', [])
            if header == b'cookie'
        }
        self.__response_cookies = {}
        self.__query_params = {k: v for k, v in self.__url.query.items()}
        self.__head_sent = False

    def __check_if_closed(self):
        if self.__closed:
            raise ConnectionClosed()

    async def _send(self, *args, **kwargs):
        self.__check_if_closed()
        return await self.__send(*args, **kwargs)

    async def _receive(self, *args, **kwargs):
        self.__check_if_closed()
        return await self.__receive(*args, **kwargs)

    async def body(self) -> bytes:
        self.__check_if_closed()

        if len(self.__body) > 0:
            return self.__body

        while self.__has_next_chunk:
            self.__body += (await self.__read_next_chunk())

        return self.__body

    async def text(self, encoding: str = 'utf-8') -> str:
        return (await self.body()).decode(encoding=encoding)

    async def json(self, encoding: str = 'utf-8') -> Union[dict, list, float, int, str]:
        return json.loads((await self.text(encoding=encoding)))

    async def __read_next_chunk(self) -> bytes:
        message = await self._receive()
        self.__has_next_chunk = message.get('more_body', False)

        return message.get('body', b'')

    async def next_chunk(self) -> bytes:
        while self.__has_next_chunk:
            return await self.__read_next_chunk()

    @property
    def type(self) -> str:
        return self.__type

    @property
    def path(self) -> str:
        return self.__path

    @property
    def method(self) -> HTTPMethod:
        return self.__method

    @property
    def cookies(self) -> Dict[str, bytes]:
        return {**self.__request_cookies, **self.__response_cookies}

    @property
    def request_cookies(self) -> Dict[str, bytes]:
        return self.__request_cookies

    @property
    def response_cookies(self) -> Dict[str, bytes]:
        return self.__response_cookies

    def put_cookie(self, name: str, value: bytes):
        self.__response_cookies[name] = value

    def remove_cookie(self, name: str):
        if name in self.__response_cookies:
            del self.__response_cookies[name]

    @property
    def headers(self) -> Dict[str, bytes]:
        return {**self.__request_headers, **self.__response_headers}

    @property
    def request_headers(self) -> Dict[str, bytes]:
        return self.__request_headers

    @property
    def response_headers(self) -> Dict[str, bytes]:
        return self.__response_headers

    def put_header(self, name: str, value: bytes):
        self.__response_headers[name] = value

    @property
    def query_params(self):
        return self.__query_params

    def _put_query_param(self, name: str, value: any):
        self.__query_params[name] = value

    async def close(self):
        await self.__send_end(END_EVENT[self.__type])
        self.__closed = True

    @property
    def closed(self) -> bool:
        return self.__closed

    async def __send_chunk(self, chunk: bytes, event_type: str, is_end: bool):
        await self._send({
            'type': event_type,
            'body': chunk,
            'more_body': not is_end
        })

    async def __send_end(self, event_type: str):

        if not self.__head_sent and self.__type == 'http':
            await self.send_html_head(200, [])

        await self._send({
            'type': event_type,
            'body': b'',
            'more_body': False
        })

    async def send_head(self, content_type: str, status_code: int, headers: List[Tuple[str, bytes]] = []):
        self.__response_headers.update({header: value for header, value in headers})

        if not any(header == 'content-type' for header, _ in self.__response_headers.items()):
            self.__response_headers.update({'content-type': content_type.encode('utf-8')})

        response_headers = [
            [header.encode('utf-8'), value]
            for header, value in self.__response_headers.items()
        ]

        response_cookies = [
            [b'cookie', name.encode('utf-8') + b'=' + value]
            for name, value in self.__response_cookies.items()
        ]

        await self._send({
            'type': SendEventType.HTTP_RESPONSE_START,
            'status': status_code,
            'headers': response_headers + response_cookies
        })

        self.__head_sent = True

    async def send_html_head(self, status_code: int, headers: List[Tuple[str, bytes]] = []):
        await self.send_head(status_code=status_code, headers=headers, content_type='text/html')

    async def send_body(self, body: Union[str, bytes], encoding: str = 'utf-8', chunk_size_bytes: int = 512):
        if isinstance(body, str):
            body = body.encode(encoding=encoding)

        position = 0

        while position < len(body):
            chunk = body[position: position + chunk_size_bytes]
            position += len(chunk)

            if len(chunk) == 0:
                break

            await self.__send_chunk(chunk=chunk, event_type=SendEventType.HTTP_RESPONSE_BODY, is_end=False)

    async def send_chunk(self, chunk: bytes, is_end: bool = False, event_type=SendEventType.HTTP_RESPONSE_BODY):
        await self.__send_chunk(chunk=chunk, event_type=event_type, is_end=is_end)

    async def send_json(
            self,
            body: str,
            status_code: int,
            headers: List[Tuple[str, bytes]],
            encoding: str = 'utf-8',
            chunk_size_bytes: int = 512
    ):
        if not any(header == 'content-type' for header, _ in headers):
            headers.append(('content-type', b'application/json'))

        await self._send({
            'type': SendEventType.HTTP_RESPONSE_START,
            'status': status_code,
            'headers': [
                [header.encode('utf-8'), value]
                for header, value in headers
            ]
        })

        self.__head_sent = True

        await self.send_body(body, encoding, chunk_size_bytes)

    async def send_text(
            self,
            body: str,
            status_code: int,
            headers: List[Tuple[str, bytes]],
            encoding: str = 'utf-8',
            chunk_size_bytes: int = 512
    ):
        if not any(header == 'content-type' for header, _ in headers):
            headers.append(('content-type', b'text/plain'))

        await self._send({
            'type': SendEventType.HTTP_RESPONSE_START,
            'status': status_code,
            'headers': [
                [header.encode('utf-8'), value]
                for header, value in headers
            ]
        })

        self.__head_sent = True

        await self.send_body(body, encoding, chunk_size_bytes)

import json

from yarl import URL
from typing import Union, List, Dict, Optional

from .enums import SendEventType, HTTPMethod
from .exceptions import ConnectionClosed
from .types import BodyType, Address, Receive, Send, Scope

END_EVENT = {"http": SendEventType.HTTP_RESPONSE_BODY}


class Connection:
    def __init__(
        self,
        scope: Scope,
        send: Send,
        receive: Receive,
    ) -> None:
        self._scope = scope
        self._send_handler = send
        self._receive_handler = receive
        self._body: bytes = b""
        self._has_next_chunk: bool = True
        self._path: str = scope.get("path", "")
        query_params: str = scope.get("query_string", b"").decode("utf-8")
        self._url: Optional[str] = (
            (self._path + ("?" + query_params) if query_params else "")
            if self._path is not None
            else None
        )
        self._method = HTTPMethod(scope.get("method", "UNKNOWN"))
        self._host: Address = scope.get("server", ("", 0))
        self._client: Address = scope.get("server", ("", 0))
        self._http_version: Optional[str] = scope.get("http_version")
        self._type: str = scope.get("type", "http")
        self._scheme = scope.get("scheme")
        self._closed = False
        self._request_headers = {
            header.decode("utf-8"): value
            for header, value in scope.get("headers", [])
            if header != b"cookie"
        }
        self._response_headers: Dict[str, bytes] = {}
        self._request_cookies: Dict[str, bytes] = {
            cookie: value
            for cookie, value in [
                cookie.split(b"=")
                for cookie in [
                    cookie
                    for header, cookie in scope.get("headers", [])
                    if header == b"cookie"
                ]
            ]
        }
        self._response_cookies: Dict[str, bytes] = {}
        self._query_params: Dict[str, str] = (
            {k: v for k, v in URL(self._url).query.items()} if self._url else {}
        )
        self._head_sent = False
        self._accept = [
            accept.decode("utf-8")
            for accept in self._request_headers.get("accept", b"").split(b",")
        ]

    def _check_if_closed(self) -> bool:
        if self._closed:
            raise ConnectionClosed()

        return True

    async def _send(self, data: BodyType) -> None:
        self._check_if_closed()
        await self._send_handler(data)

    async def _receive(self) -> Dict[Union[str, bytes], BodyType]:
        self._check_if_closed()
        return await self._receive_handler()

    async def body(self) -> bytes:
        self._check_if_closed()

        if len(self._body) > 0:
            return self._body

        while self._has_next_chunk:
            self._body += await self._read_next_chunk()

        return self._body

    async def text(self, encoding: str = "utf-8") -> str:
        return (await self.body()).decode(encoding=encoding)

    async def json(self, encoding: str = "utf-8") -> Union[dict, list, float, int, str]:
        return json.loads((await self.text(encoding=encoding)))

    async def _read_next_chunk(self) -> bytes:
        message = await self._receive()
        self._has_next_chunk = bool(message.get("more_body", False))

        body = message.get("body", b"")
        assert isinstance(body, bytes)

        return body

    async def next_chunk(self) -> Optional[bytes]:
        while self._has_next_chunk:
            return await self._read_next_chunk()

        return None

    @property
    def has_next_chunk(self) -> bool:
        return self._has_next_chunk

    @property
    def accept(self) -> List[str]:
        return self._accept

    @property
    def type(self) -> Optional[str]:
        return self._type

    @property
    def url(self) -> Optional[str]:
        return self._url

    @property
    def path(self) -> Optional[str]:
        return self._path

    @property
    def method(self) -> HTTPMethod:
        return self._method

    @property
    def server_host(self) -> str:
        return self._host[0]

    @property
    def server_port(self) -> int:
        return self._host[1]

    @property
    def client_host(self) -> str:
        return self._client[0]

    @property
    def client_port(self) -> int:
        return self._client[1]

    @property
    def http_version(self) -> Optional[str]:
        return self._http_version

    @property
    def cookies(self) -> Dict[str, bytes]:
        return {**self._request_cookies, **self._response_cookies}

    @property
    def request_cookies(self) -> Dict[str, bytes]:
        return self._request_cookies

    @property
    def response_cookies(self) -> Dict[str, bytes]:
        return self._response_cookies

    def put_cookie(
        self, name: str, value: Union[str, bytes], encoding: str = "utf-8"
    ) -> None:
        if not isinstance(value, bytes):
            value = value.encode(encoding=encoding)

        self._response_cookies[name] = value

    def remove_cookie(self, name: str) -> None:
        if name in self._response_cookies:
            del self._response_cookies[name]

    @property
    def headers(self) -> Dict[str, bytes]:
        return {**self._request_headers, **self._response_headers}

    @property
    def request_headers(self) -> Dict[str, bytes]:
        return self._request_headers

    @property
    def response_headers(self) -> Dict[str, bytes]:
        return self._response_headers

    def put_header(
        self, name: str, value: Union[str, bytes], encoding: str = "utf-8"
    ) -> None:
        if not isinstance(value, bytes):
            value = value.encode(encoding=encoding)

        self._response_headers[name] = value

    @property
    def query_params(self) -> Dict[str, str]:
        return self._query_params

    def _put_query_param(self, name: str, value: str) -> None:
        self._query_params[name] = value

    async def close(self) -> None:
        await self._send_end(END_EVENT[self._type])
        self._closed = True

    @property
    def closed(self) -> bool:
        return self._closed

    async def _send_chunk(self, chunk: bytes, event_type: str, is_end: bool) -> None:
        await self._send({"type": event_type, "body": chunk, "more_body": not is_end})

    async def _send_end(self, event_type: str) -> None:

        if not self._head_sent and self._type == "http":
            await self.send_html_head(200, {})

        await self._send({"type": event_type, "body": b"", "more_body": False})

    async def send_head(
        self,
        content_type: str,
        status_code: int,
        headers: Dict[str, str] = {},
        cookies: Dict[str, str] = {},
    ) -> None:
        self._response_headers.update(
            {k: v.encode("utf-8") for k, v in (headers or {}).items()}
        )
        self._response_cookies.update(
            {k: v.encode("utf-8") for k, v in (cookies or {}).items()}
        )

        if not any(
            header == "content-type" for header, _ in self._response_headers.items()
        ):
            self._response_headers.update(
                {"content-type": content_type.encode("utf-8")}
            )

        response_headers = [
            [header.encode("utf-8"), value]
            for header, value in self._response_headers.items()
        ]

        response_cookies = [
            [b"set-cookie", name.encode("utf-8") + b"=" + value]
            for name, value in self._response_cookies.items()
        ]

        await self._send(
            {
                "type": SendEventType.HTTP_RESPONSE_START,
                "status": status_code,
                "headers": response_headers + response_cookies,
            }
        )

        self._head_sent = True

    async def send_html_head(
        self, status_code: int, headers: Optional[Dict[str, str]] = None
    ) -> None:
        await self.send_head(
            status_code=status_code, headers=headers or {}, content_type="text/html"
        )

    async def send_body(
        self,
        body: Union[str, bytes],
        encoding: str = "utf-8",
        chunk_size_bytes: int = 512,
    ) -> None:
        if isinstance(body, str):
            body = body.encode(encoding=encoding)

        position = 0

        while position < len(body):
            chunk = body[position : position + chunk_size_bytes]
            position += len(chunk)

            if len(chunk) == 0:
                break

            await self._send_chunk(
                chunk=chunk, event_type=SendEventType.HTTP_RESPONSE_BODY, is_end=False
            )

    async def send_chunk(
        self,
        chunk: bytes,
        is_end: bool = False,
        event_type: str = SendEventType.HTTP_RESPONSE_BODY,
    ) -> None:
        await self._send_chunk(chunk=chunk, event_type=event_type, is_end=is_end)

    async def send_content(
        self,
        body: Union[str, bytes],
        status_code: int,
        content_type: str,
        headers: Dict[str, str] = {},
        cookies: Dict[str, str] = {},
        encoding: str = "utf-8",
        chunk_size_bytes: int = 512,
    ) -> None:
        assert isinstance(
            body, (str, bytes)
        ), f"Got incompatible body type: {type(body)}"
        await self.send_head(
            content_type=content_type,
            headers=headers,
            cookies=cookies,
            status_code=status_code,
        )
        await self.send_body(
            body=body, encoding=encoding, chunk_size_bytes=chunk_size_bytes
        )
        await self.close()

    async def send_text(
        self,
        body: str,
        status_code: int,
        headers: Dict[str, str] = {},
        cookies: Dict[str, str] = {},
        encoding: str = "utf-8",
        chunk_size_bytes: int = 512,
    ) -> None:
        await self.send_content(
            body=body,
            status_code=status_code,
            headers=headers,
            cookies=cookies,
            encoding=encoding,
            chunk_size_bytes=chunk_size_bytes,
            content_type="text/plain",
        )

    async def send_html(
        self,
        body: str,
        status_code: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        encoding: str = "utf-8",
        chunk_size_bytes: int = 512,
    ) -> None:
        await self.send_content(
            body=body,
            status_code=status_code,
            headers=headers,
            cookies=cookies,
            encoding=encoding,
            chunk_size_bytes=chunk_size_bytes,
            content_type="text/html",
        )

    async def send_json(
        self,
        body: Union[bytes, str, object],
        status_code: int,
        headers: Dict[str, str],
        cookies: Dict[str, str],
        encoding: str = "utf-8",
        chunk_size_bytes: int = 512,
    ) -> None:
        body = (
            body
            if isinstance(body, bytes)
            else (body if isinstance(body, str) else json.dumps(body)).encode(
                encoding=encoding
            )
        )

        await self.send_content(
            body=body,
            status_code=status_code,
            headers=headers,
            cookies=cookies,
            encoding=encoding,
            chunk_size_bytes=chunk_size_bytes,
            content_type="application/json",
        )

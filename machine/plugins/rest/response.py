import json

from dataclasses import dataclass
from typing import Optional, Dict


class Response:
    def __init__(
            self,
            body: any,
            content_type: str,
            headers: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            status_code: int = 200,
            encoding: str = 'utf-8'
    ):
        self._body = body
        self._content_type = content_type
        self._headers = headers or {}
        self._cookies = cookies or {}
        self._status_code = status_code
        self._encoding = encoding

    @property
    def body(self):
        return self._body

    @property
    def content_type(self):
        return self._content_type

    @property
    def headers(self):
        return self._headers

    @property
    def cookies(self):
        return self._cookies

    @property
    def status_code(self):
        return self._status_code

    @property
    def encoding(self):
        return self._encoding

    def bytes(self, encoding: str = 'utf-8') -> bytes:
        if isinstance(self.body, bytes):
            return self.body

        elif isinstance(self.body, str):
            return self.body.encode(encoding=encoding)

        else:
            return json.dumps(self.body).encode(encoding=encoding)


class HTMLResponse(Response):
    def __init__(
            self,
            body: any,
            content_type: str = 'text/html',
            headers: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            status_code: int = 200,
            encoding: str = 'utf-8'
    ):
        super().__init__(body, content_type, headers, cookies, status_code, encoding)


class JSONResponse(Response):
    def __init__(
            self,
            body: any,
            content_type: str = 'application/json',
            headers: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            status_code: int = 200,
            encoding: str = 'utf-8'
    ):
        super().__init__(body, content_type, headers, cookies, status_code, encoding)


class TextResponse(Response):
    def __init__(
            self,
            body: any,
            content_type: str = 'text/plain',
            headers: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            status_code: int = 200,
            encoding: str = 'utf-8'
    ):
        super().__init__(body, content_type, headers, cookies, status_code, encoding)

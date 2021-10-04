import json

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Response:
    body: any
    status_code: int = 200
    content_type: str = 'text/plain'

    @staticmethod
    def html(body: Union[str, bytes], status_code: int) -> 'Response':
        if isinstance(body, str):
            body = body.encode('utf-8')

        return Response(
            body=body,
            status_code=status_code,
            content_type='text/html'
        )

    @staticmethod
    def text(body: Union[str, bytes], status_code: int) -> 'Response':
        if isinstance(body, str):
            body = body.encode('utf-8')

        return Response(
            body=body,
            status_code=status_code,
            content_type='text/plain'
        )

    @staticmethod
    def json(body: any, status_code: int) -> 'Response':
        return Response(
            body=body,
            status_code=status_code,
            content_type='application/json'
        )

    def bytes(self, encoding: str = 'utf-8') -> bytes:
        if isinstance(self.body, bytes):
            return self.body

        elif isinstance(self.body, str):
            return self.body.encode(encoding=encoding)

        else:
            return json.dumps(self.body).encode(encoding=encoding)


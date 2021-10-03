import json

from dataclasses import dataclass


@dataclass(frozen=True)
class Response:
    body: str
    status_code: int = 200
    content_type: str = 'text/plain'


def html_response(body, status_code):
    return Response(
        body,
        status_code,
        content_type='text/html'
    )


def text_response(body, status_code):
    return Response(
        body,
        status_code
    )


def json_response(obj, status_code):
    return Response(
        json.dumps(obj),
        status_code,
        content_type='application/json'
    )



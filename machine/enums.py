import enum


class SendEventType:
    HTTP_RESPONSE_START = 'http.response.start'
    HTTP_RESPONSE_BODY = 'http.response.body'


class ReceiveEventType:
    HTTP_DISCONNECT = 'http.disconnect'


class HTTPMethod(enum.Enum):
    POST = 'POST'
    GET = 'GET'
    PUT = 'PUT'
    DELETE = 'DELETE'
    UPDATE = 'UPDATE'
    HEAD = 'HEAD'
    UNKNOWN = 'UNKNOWN'

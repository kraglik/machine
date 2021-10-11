from abc import ABC
from machine.exceptions.machine import MachineError


class MachineJsonRPCError(MachineError, ABC):
    status_code: int = 500
    message: str = 'Unexpected error'


class MachineJsonRPCRequestError(MachineJsonRPCError, ABC):
    pass


class MachineJsonRPCResponseError(MachineJsonRPCError, ABC):
    error_code: int = 0

    def __init__(self, request_id, method_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request_id = request_id
        self.method_name = method_name


class BadJsonRPCRequestError(MachineJsonRPCRequestError):
    message = 'Bad JsonRPC request'
    error_code = 400
    status_code = 8000


class WrongJsonRPCParamsError(MachineJsonRPCRequestError):
    message = 'Wrong JsonRPC params'
    status_code = 400
    error_code = 8001


class MethodNotAllowedJsonRPCError(MachineJsonRPCRequestError):
    message = 'Method not allowed'
    status_code = 405
    error_code = 8002


class JsonRPCMethodNotFoundError(MachineJsonRPCResponseError):
    message = 'Method not found'
    status_code = 404
    error_code = 8003

    def __init__(self, method_name: str, *args, **kwargs):
        super().__init__(method_name, *args, **kwargs)
        self.message = f'method with name "{method_name}" not found'


class JsonRPCInternalError(MachineJsonRPCResponseError):
    status_code = 500
    error_code = 8005

    def __init__(self, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message

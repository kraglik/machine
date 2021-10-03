from abc import ABC

from machine.exceptions.resource import MachineResourceError


class MachineJsonRPCError(MachineResourceError, ABC):
    message = 'Abstract jsonrpc resource error'
    status_code = 400


class BadJsonRPCRequestError(MachineJsonRPCError):
    message = 'Bad JsonRPC request'
    status_code = 400


class WrongJsonRPCParamsError(MachineJsonRPCError):
    message = 'Wrong JsonRPC params'
    status_code = 400


class MethodNotAllowedJsonRPCError(MachineJsonRPCError):
    message = 'Method not allowed'
    status_code = 405


class JsonRPCMethodNotFoundError(MachineJsonRPCError):
    message = 'Method not found'
    status_code = 404

    def __init__(self, method_name: str):
        super().__init__()
        self.message = f'Method with name "{method_name}" not found'

from abc import ABC

from machine.exceptions.machine import MachineError


class MachineResourceError(MachineError, ABC):
    message = 'Abstract resource error'
    status_code = 500


class MethodNotAllowedResourceError(MachineResourceError):
    message = 'Method not allowed'
    status_code = 405


class BadRequestResourceError(MachineResourceError):
    message = 'Bad request'
    status_code = 400


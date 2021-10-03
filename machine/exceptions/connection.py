from abc import ABC

from machine.exceptions.machine import MachineError


class MachineConnectionError(MachineError, ABC):
    message = 'Abstract connection error'
    status_code = 500


class ConnectionClosed(MachineConnectionError):
    message = 'Connection is already closed'
    status_code = 500


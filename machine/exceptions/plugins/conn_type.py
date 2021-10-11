from machine.exceptions.machine import MachineError


class UnsupportedConnectionType(MachineError):
    status_code = 500
    message = "Unsupported connection type"

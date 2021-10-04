from machine.exceptions.machine import MachineError


class UnsupportedResponseTypeError(MachineError):
    message = "Client doesn't support required content types"
    status_code = 403

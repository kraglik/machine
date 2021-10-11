from machine.exceptions.machine import MachineError


class SuitableArmNotFound(MachineError):
    message = "SuitableArmNotFound"
    status_code = 500

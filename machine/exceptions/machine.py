from abc import ABC


class MachineError(Exception, ABC):
    message = 'Abstract error'
    status_code = 500

    def __init__(self):
        super().__init__(self.message)


class MachineSuspiciousOperationError(MachineError):
    message = 'Suspicious operation'
    status_code = 500


class DisallowedHostError(MachineSuspiciousOperationError):
    message = 'Disallowed host'
    status_code = 403


class UnexpectedContentType(MachineSuspiciousOperationError):
    message = 'Unexpected content type'
    status_code = 403


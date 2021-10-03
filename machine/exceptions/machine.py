from abc import ABC


class MachineError(ABC, Exception):
    message = 'Abstract error'
    status_code = 500

    def __init__(self):
        super().__init__(self.message)

class OutputError(Exception):
    def __init__(message):
        self.message = message

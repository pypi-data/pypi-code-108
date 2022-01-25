class PyOpenCellException(Exception):
    def __init__(self, message):
        super().__init__(self, message)
        self.description = message

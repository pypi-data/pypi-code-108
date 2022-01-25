class DataIceError(Exception):
    """Base Class for DataIcer Errors"""
    pass

class UnknownTypeError(DataIceError):
    """Raised when the input value is too small"""

    def __init__(self, unknown_type, message="They type: {} is not understood by dataicer, register a plugin for this type."):
        self.unknown_type = unknown_type
        self.message = message.format(self.unknown_type)
        super().__init__(self.message)

class ImportModuleError(DataIceError):
    """Raised when cannot import a module"""
    pass

class DataIceExists(DataIceError):
    """Raised when trying to overwrite saved data file that already exists"""

    def __init__(self, filepath, message="They file: {} already exists, set overwite to True to replace."):
        self.filepath = filepath
        self.message = message.format(self.filepath)
        super().__init__(self.message)

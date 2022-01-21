class InvalidSeperateElement(Exception):
    """Seperate Item is invalid"""

    def __init__(self, sep: str, message: str):
        self._sep = sep
        self._message = message
        super().__init__(self._message)

    # def __str__(self):
    #     return f"sep = {self._sep} : {self._message}"


class LanguageError(Exception):
    """Language is not supported ERROR"""

    def __init__(self, language: str, message: str):
        self._language = language
        self._message = message
        super().__init__(self._message)

    # def __str__(self):
    #     return f"Language {self._language} : {self._message}"


class LoginError(Exception):
    """Username or Password is incorrect."""

    def __init__(self, message: str):
        self._message = message
        super().__init__(self._message)

    # def __str__(self):
    #     return f"Failed to Login: {self._message}"


class AddLevelError(Exception):
    """Add Level Exception Handle"""

    def __init__(self, id: str, message: str):
        self._id = id
        self._message = message
        super().__init__(self._message)

    # def __str__(self):
    #     return f"Course ID {self._id} : {self._message}"


class AddBulkError(Exception):
    """Add Bulk Exception Handle"""

    def __init__(self, id: str, message: str):
        self._id = id
        self._message = message
        super().__init__(self._message)

    # def __str__(self):
    #     return f"Add Bulk Error Item ID {self._id}: {self._message}"


class ConnectionError(Exception):
    ...


class JSONParseError(Exception):
    ...


class InputOutOfRange(Exception):
    """Exception raised for errors in the input option which's out of range.

    Attributes:
        input value -- the number input option
        message -- explanation of the error
    """

    def __init__(self, option: int, message: str):
        self.option = option
        self.message = message
        super().__init__(self.message)

    # def __str__(self):
    #     return f"Input value: {self.option} -> {self.message}"

class Error(Exception):
    """Base class for our exceptions"""

    def __init__(self, message="Error: A runtime error has occurred in the Insight Engine"):
        self.message = message
        super().__init__(self.message)


class ClaimError(Error):
    def __init__(self, message="Error: invalid Claim, check input"):
        super().__init__(message)


class MissingFieldError(ClaimError):
    def __init__(self, message="Error: invalid Claim, missing expected field(s), check input."):
        super().__init__(message)

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        variable -- variable name which caused the error
        explanation -- explanation of the error
    """

    def __init__(self, variable, explanation=None):
        self.variable = variable
        self.explanation = explanation
        self.message = f"input error on variable {self.variable}"
        if self.explanation is not None:
            self.message += f' ({self.explanation})'

        super().__init__(self.message)

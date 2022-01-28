class TectonValidationError(ValueError):
    """
    Exception that indicates a problem in validating user inputs against
    the data in the system. Typically recoverable by the user.
    """


class TectonInternalError(RuntimeError):
    """
    Exception that indicates an unexpected error within Tecton.
    Can be persistent or transient. Recovery typically requires involving
    Tecton support.
    """

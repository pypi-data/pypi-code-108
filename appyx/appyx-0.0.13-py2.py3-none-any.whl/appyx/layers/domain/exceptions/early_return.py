class EarlyReturnBecauseOfErrorsException(Exception):
    """
    This object models an early return from the operation logic because of errors in its execution.
    It is used to stop execution of the logic from inside an object and return no matter where we are.

    Since a method from an object can't delegate the return from itself to a method it invokes
    throwing this exception and returning is used to mimic that behavior.
    """
    pass

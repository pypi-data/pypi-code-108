from appyx.layers.domain.exceptions.early_return import EarlyReturnBecauseOfErrorsException
from appyx.layers.domain.result import Result


class DomainOperation:
    """
    Models an operation from the Domain.
    Answers a Result after executing the operation.
    Can delegate the return from execute() to private methods.

    Subclasses should implement _execute_logic(), calling _return() if they need to return from execute().

    Note: _save_model is a crutch that couples us to Django. Further iterations will remove this coupling.
    """
    def __init__(self) -> None:
        super().__init__()
        self._result = Result()

    def execute(self):
        self._result = Result()

        try:
            self._execute_logic()
        except EarlyReturnBecauseOfErrorsException:
            pass

        return self._result

    def _abort_in_case_of_errors(self):
        # If the result has errors, exit the operation.
        # Otherwise continue executing normally
        if self._result.has_errors():
            self._return_from_operation()

    def _return_from_operation(self):
        raise EarlyReturnBecauseOfErrorsException()

    def _execute_logic(self):
        raise NotImplementedError("Subclass responsibility")

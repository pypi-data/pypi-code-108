from appyx.layers.application.interactions.interaction import Interaction
from appyx.layers.application.interactions.validators.parameters import NoneValidation
from appyx.layers.domain.result import Result


class SimpleInteraction(Interaction):
    """
    Models a simple and basic interaction.
    Defines a minimal protocol that any interaction should have.
    This allows to subclass and implement the bare minimum.

    It is expected that subclasses will override at least _execute_from_successful_result.
    """
    def __init__(self, parameters=None):
        super().__init__()
        self._parameters = parameters or {}

    def set_parameters(self, parameters):
        self._parameters = parameters

    def validate(self):
        """
        Answers a result indicating the validity of the receiver.

        If result has no errors, it means the receiver can be executed (although it may fail if further problems arise).
        If result has errors, then the receiver can not be executed (and the errors explain why)
        """
        result = Result()
        for validator in self._parameters_validator():
            result = validator.validate(self._parameters, result)
        return result

    def execute(self):
        """
        Performs the operation of the receiver and answers the result of the execution.

        :return: result of execution
        """
        result = self.validate()
        if result.has_errors():
            return result
        return self._execute_from_successful_result(result)

    # --- private methods ---

    def _execute_from_successful_result(self, result):
        """
        Execute the command assuming can_execute is successful.
        My subclasses should override me.
        Performs the operation and answers the result of the execution

        :return: result of execution
        """
        return result

    def _parameters_validator(self):
        """
        My subclass should override me. Configures how my parameters must be validated.

        :return: a list of parameter names
        """
        return [NoneValidation()]

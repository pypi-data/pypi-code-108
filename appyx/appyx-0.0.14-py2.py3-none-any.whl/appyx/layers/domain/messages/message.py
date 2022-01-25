class Message:
    def __init__(self, type_of_message, arguments=None, **kwargs) -> None:
        from appyx.layers.domain.errors import BaseErrorFactory
        self._error_factory = BaseErrorFactory()
        self._type = type_of_message

        if arguments is None:
            arguments = {}
        arguments.update(kwargs)
        self._arguments = arguments

        self._assert_arguments_are_present_and_valid()

    def __str__(self):
        return self.text()
    
    def text(self):
        return self._type.text_template().format(**self._arguments)

    # --- private methods ---

    def _assert_arguments_are_present_and_valid(self):
        from appyx.layers.domain.exceptions.message import MessageMissingArgumentsException, \
            MessageWithInvalidArgumentsException
        result = self._type.validate_arguments(self._arguments)

        for error in result.errors():
            error_text = error.text()
            if error.code() == self._error_factory.parameter_missing_error_code():
                raise MessageMissingArgumentsException(error_text)
            if error.code() == self._error_factory.parameter_validation_error_code():
                raise MessageWithInvalidArgumentsException(error_text)

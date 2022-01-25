from appyx.layers.domain.messages.error_messages import ErrorMessages


class ExceptionMessage(Exception):
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return str(self._message)


class CreationError(ExceptionMessage):
    def __init__(self, class_been_instantiated, error_while_instantiating):
        message = ErrorMessages().creation_error_message(class_been_instantiated, error_while_instantiating)
        super(CreationError, self).__init__(message)


class ArgumentNotFound(ExceptionMessage):
    def __init__(self, argument_name):
        message = ErrorMessages().argument_not_found_message(argument_name)
        super(ArgumentNotFound, self).__init__(message)


class ParameterNotFoundException(ExceptionMessage):
    def __init__(self, missing_parameter_name):
        message = ErrorMessages().parameter_name_not_found(missing_parameter_name)
        super(ParameterNotFoundException, self).__init__(message)


class DuplicateParameterException(ExceptionMessage):
    def __init__(self, duplicated_parameter_name):
        message = ErrorMessages().duplicated_parameter_name(duplicated_parameter_name)
        super(DuplicateParameterException, self).__init__(message)


class TypeOfMessageParameterMissingExamplesException(ExceptionMessage):
    """
    This object models a lack of examples in the parameter list of a type of message.
    """
    def __init__(self, parameter_with_missing_example):
        message = ErrorMessages().parameter_example_missing(parameter_with_missing_example)
        super(TypeOfMessageParameterMissingExamplesException, self).__init__(message)

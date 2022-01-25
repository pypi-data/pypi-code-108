class BaseError:
    """
    Models a generic, basic error.
    Provides information on the type of error (code) and details about it (object).

    code: indicates the class or type of error.
    object: provides the details of the error in a way determined by the code.
    """
    def __init__(self, data) -> None:
        super().__init__()
        self._object = data

    def object(self):
        return self._object

    def code(self):
        return self.__class__.__name__

    def __str__(self):
        return f'{self.__class__.__name__}<Data "{str(self.object())}">'

    def __repr__(self):
        return f'{self.__class__.__name__}(_object="{str(self.object())}")'

    def __unicode__(self):
        return self.__str__()


class SimpleError(BaseError):
    """
    Models a simple error.
    Provides the type of error (code) and a description of it (text).

    code: indicates the class or type of error.
    object: provides a description of the error.
    """
    def __init__(self, text, code) -> None:
        super().__init__(text)
        self._code = code

    def code(self):
        return self._code

    def text(self):
        return self.object()

    def __str__(self):
        return f'{self.__class__.__name__}<Code "{self.code()}" | Data "{str(self.object())}">'

    def __repr__(self):
        return f'{self.__class__.__name__}(_code="{self.code()}", _object="{str(self.text())}")'

    def __unicode__(self):
        return self.__str__()

    def __eq__(self, other):
        return super.__eq__(self, other) and self.code() == other.code() and self.text() == other.text()

    def __hash__(self):
        return hash((self._code, self._object))


class UnexpectedError(SimpleError):
    """
    Models an error that has been detected and caught
    but one which the system is not prepared to handle.

    The text of the error is expected to describe what happened and why it wasn't expected.
    """
    pass


class ParameterValidationError(SimpleError):
    """
    Models the invalidity of an argument in the context of a parameter.
    It provides the name of the parameter, the value of the argument
    and the different errors/reasons of why it is invalid.
    """
    def __init__(self, parameter_name, argument, validation_errors, code) -> None:
        self._parameter_name = parameter_name
        self._argument = argument
        self._validation_errors = validation_errors
        super().__init__(self._error_text(), code)

    def parameter_name(self):
        return self._parameter_name

    def argument(self):
        return self._argument

    def validation_errors(self):
        return self._validation_errors

    def validation_errors_text(self):
        return " | ".join(validation_error.text() for validation_error in self._validation_errors)

    def _error_text(self):
        return f'Parameter "{self._parameter_name}" is not valid with argument "{self._argument}". ' \
               f'Reasons: {self.validation_errors_text()}'


class ParametersValidationError(SimpleError):
    """
    Models the invalidity of a set of arguments in the context of a set of parameters.
    It provides the set of arguments, parameters and errors/reasons of the invalidity.
    """

    def __init__(self, parameters_and_arguments, validation_errors, code) -> None:
        self._parameters_and_arguments = parameters_and_arguments
        self._validation_errors = validation_errors
        super().__init__(self._error_text(), code)

    def parameters_and_arguments(self):
        return self._parameters_and_arguments

    def validation_errors(self):
        return self._validation_errors

    def validation_errors_text(self):
        return " | ".join(validation_error.text() for validation_error in self._validation_errors)

    def _error_text(self):
        keys = ", ".join(str(key) for key in self._parameters_and_arguments.keys())
        values = ", ".join(str(value) for value in self._parameters_and_arguments.values())
        return f'Parameters "{keys}" are not valid with arguments "{values}". Reasons: {self.validation_errors_text()}'


class BaseErrorFactory:
    """
    Models a Factory (design pattern) of commonly used errors.
    """
    def simple_error(self, text_or_exception):
        return self._new_error(text_or_exception, SimpleError, self.simple_error_code())

    def unexpected_error(self, text_or_exception):
        return self._new_error(text_or_exception, UnexpectedError, self.unexpected_error_code())

    def parameter_validation_error(self, parameter_name, argument, validation_errors):
        return ParameterValidationError(parameter_name, argument, validation_errors,
                                        self.parameter_validation_error_code())

    def parameters_validation_error(self, parameters_and_arguments, validation_errors):
        return ParametersValidationError(parameters_and_arguments, validation_errors,
                                         self.parameters_validation_error_code())

    def parameter_missing_error(self, text_or_exception):
        return self._new_error(text_or_exception, SimpleError, self.parameter_missing_error_code())

    def _new_error(self, text_or_exception, error_class, error_code):
        error_message = str(text_or_exception)
        return error_class(error_message, error_code)

    def simple_error_code(self):
        return "simple_error_code"

    def unexpected_error_code(self):
        return "unexpected_error_code"

    def parameter_validation_error_code(self):
        return "parameter_validation_error_code"

    def parameter_missing_error_code(self):
        return "parameter_missing_error"

    def parameters_validation_error_code(self):
        return "parameters_validation_error_code"

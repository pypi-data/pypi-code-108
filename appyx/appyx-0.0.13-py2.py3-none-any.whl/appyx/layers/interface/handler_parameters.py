from appyx.layers.domain.messages.exceptions import ParameterNotFoundException


class HttpParameter:  # inherit from parameter? we also need validators? -> yes
    def __init__(self, name, location, example):
        self._name = name
        self._location = location
        self._example = example

    def name(self):
        return self._name

    def location(self):
        return self._location

    def example(self):
        return self._example

    def get_argument_from_request(self, request, kwargs, default=None):
        return self._location.get_argument_from_request(self, request, kwargs, default)


class HandlerParameters:  # Check how this object's protocol relates to SetOfParameters.
    def __init__(self, initial_parameters=None, initial_required_parameter_names=None):
        self._parameters = initial_parameters or []
        self._required_parameter_names = initial_required_parameter_names or set()

    def required_parameter_names(self):
        return self._required_parameter_names

    def parameters(self):
        return self._parameters

    def get_argument_named(self, request, kwargs, parameter_name, default=None):
        parameter = self._parameter_named(parameter_name)
        return parameter.get_argument_from_request(request, kwargs, default)

    def _parameter_named(self, parameter_name):
        for parameter in self.parameters():
            if parameter_name == parameter.name():
                return parameter
        raise ParameterNotFoundException(parameter_name)

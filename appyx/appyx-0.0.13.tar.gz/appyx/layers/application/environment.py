class Mapping:
    def cast_on(self, set_of_parameters):
        raise NotImplementedError('Subclass responsibility')


class OneToOne(Mapping):
    def __init__(self, parameter_name, parameter_source):
        self._parameter_name = parameter_name
        self._parameter_source = parameter_source

    def cast_on(self, set_of_parameters):
        set_of_parameters.set_argument_value(self._parameter_name, self._parameter_source.value())


class Environment:
    CURRENT_APP = None

    def current_app(self):
        if self.__class__.CURRENT_APP is None:
            self.__class__.CURRENT_APP = self._new_application()
        return self.__class__.CURRENT_APP

    def _new_application(self):
        context = self._running_context()
        app_class = self._application_class()
        return app_class(context)

    def reset_current_app(self):
        self.__class__.CURRENT_APP = None

    def _application_class(self):
        raise NotImplementedError('Subclass responsibility')

    def _running_context(self):
        context = self._new_application_context()
        mappings = self._external_parameters_mapped_to_context_parameters()
        self._validate_mappings_cover_all_context_variables(context, mappings)
        self._validate_that_all_context_parameters_have_a_defined_mapping(context, mappings)
        for mapping in mappings:
            mapping.cast_on(context)
        context.validate()
        return context

    def _external_parameters_mapped_to_context_parameters(self):
        raise NotImplementedError('Subclass responsibility')

    def _new_application_context(self):
        raise NotImplementedError('Subclass responsibility')

    def _validate_mappings_cover_all_context_variables(self, context, mappings):
        """not implemented yet"""
        pass

    def _validate_that_all_context_parameters_have_a_defined_mapping(self, context, mappings):
        """not implemented yet"""
        pass

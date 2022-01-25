from string import Formatter

from appyx.layers.domain.messages.exceptions import TypeOfMessageParameterMissingExamplesException, \
    CreationError, ParameterNotFoundException


class TypeOfMessage:
    """
    Notes:
        There are many local imports in this class to avoid circular imports, since it models a base element in the
        domain, and may be imported by some classes it imports.
    """

    def __init__(self, meaning, text_template, parameter_list=None) -> None:
        if parameter_list is None:
            parameter_list = []

        from appyx.layers.application.interactions.parameters.set_of_parameters import SetOfParameters
        parameter_names = [parameter.name() for parameter in parameter_list]
        self._parameters = SetOfParameters(context=self, initial_parameters=parameter_list,
                                           initial_required_parameter_names=parameter_names)
        self._meaning = meaning
        self._text_template = text_template

        self._validate_parameters_and_text_template()

    @classmethod
    def new_with_parametrized_text(cls, meaning, parametrized_text):
        text = cls._text_template_from_parametrized_text_list(parametrized_text)
        parameter_list = cls._extract_parameters_from_parametrized_text(parametrized_text)
        return cls(meaning, text, parameter_list)

    def __str__(self):
        return self.text_template()

    def means(self, meaning_to_compare_to):
        return self._meaning == meaning_to_compare_to

    def has_same_meaning_as(self, another_message):
        return another_message.means(self._meaning)

    def example_text(self):
        argument_examples = self._parameters.argument_examples()
        return self._text_template.format(**argument_examples)

    def parameters(self):
        return self._parameters

    def text_template(self):
        return self._text_template

    def validate_arguments(self, arguments):
        from appyx import Result
        result = Result()
        self._parameters.validate_arguments_existence(arguments, result)
        self._parameters.validate_argument_values(arguments, result)
        return result

    # --- private methods ---

    @classmethod
    def _text_template_from_parametrized_text_list(cls, parametrized_text):
        text_template = ""
        for item in parametrized_text:
            if isinstance(item, str):
                text_template = text_template + item
            else:
                text_template = text_template + "{" + item.name() + "}"
        return text_template

    @classmethod
    def _extract_parameters_from_parametrized_text(cls, parametrized_text):
        return [item for item in parametrized_text if not isinstance(item, str)]

    def _validate_parameters_and_text_template(self):
        self._assert_all_text_template_placeholders_have_a_matching_parameter()
        self._assert_all_parameters_have_an_example_argument()

    def _assert_all_parameters_have_an_example_argument(self):
        parameters_missing_examples = self._parameters.parameters_missing_examples()
        if len(parameters_missing_examples) > 0:
            parameter = parameters_missing_examples[0]
            error = TypeOfMessageParameterMissingExamplesException(parameter)
            raise CreationError(self.__class__, error)

    def _assert_all_text_template_placeholders_have_a_matching_parameter(self):
        try:
            self._parameters.assert_all_parameter_names_are_present(self._parameter_names())
        except ParameterNotFoundException as exception:
            raise CreationError(self.__class__, exception)

    def _parameter_names(self):
        return [field[1] for field in Formatter().parse(self._text_template) if field[1] is not None]

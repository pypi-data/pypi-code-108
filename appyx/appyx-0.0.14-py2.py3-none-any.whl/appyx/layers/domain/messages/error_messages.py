from appyx.layers.application.interactions.parameters.parameter import Parameter


class ErrorMessages:
    def argument_not_found_message(self, missing_argument_name):
        parametrized_text = [
            "Argument named: ",
            Parameter(name="argument_name", example_argument='password'),
            " not found"]
        return self._1_argument_message(parametrized_text, 'argument_not_found', missing_argument_name)

    def parameter_name_not_found(self, missing_parameter_name):
        parametrized_text = [
            "Parameter named: ",
            Parameter(name="parameter_name", example_argument='amount'),
            " not found"]
        return self._1_argument_message(parametrized_text, 'parameter_name_not_found', missing_parameter_name)

    def duplicated_parameter_name(self, duplicated_parameter_name):
        parametrized_text = [
            "Parameter ",
            Parameter(name="parameter_name", example_argument='amount'),
            " is already present"]
        return self._1_argument_message(parametrized_text, 'duplicated_parameter_name', duplicated_parameter_name)

    def parameter_example_missing(self, parameter):
        parametrized_text = [
            "Parameter with name ",
            Parameter(name="parameter_name", example_argument='password'),
            " missing an example argument"]
        return self._1_argument_message(parametrized_text, 'parameter_example_missing', parameter.name())

    def creation_error_message(self, class_been_instantiated, error_while_instantiating):
        parametrized_text = [
            "Cannot create instance of ",
            Parameter(name="class_name_been_instantiated", example_argument=self._example_class().__name__),
            ": ",
            Parameter(name="exception_or_message", example_argument=self._exception_message_example())]
        return self._2_argument_message(parametrized_text, 'argument_not_found',
                                        class_been_instantiated.__name__, error_while_instantiating)

    def _example_class(self):
        class Car:
            pass

        return Car

    def _exception_message_example(self):
        message = self._1_argument_message(["¡Felices ", Parameter('edad', example_argument=12), " años Maxi!"],
                                           'saludo_de_cumple', 16)
        from appyx.layers.domain.messages.exceptions import ExceptionMessage
        return ExceptionMessage(message)

    def _1_argument_message(self, parametrized_text, meaning, single_argument):
        """We assume a parametrized text with the form: [String, Parameter, ...]"""
        arguments = {parametrized_text[1].name(): single_argument}
        message = self._new_message(arguments, meaning, parametrized_text)
        return message

    def _2_argument_message(self, parametrized_text, meaning, argument1, argument2):
        """We assume a parametrized text with the form: [String, Parameter, String, Parameter, ...]"""
        arguments = {parametrized_text[1].name(): argument1, parametrized_text[3].name(): argument2}
        message = self._new_message(arguments, meaning, parametrized_text)
        return message

    def _new_message(self, arguments, meaning, parametrized_text):
        from appyx.layers.domain.messages.message import Message
        from appyx.layers.domain.messages.type_of_message import TypeOfMessage
        type_of_message = TypeOfMessage.new_with_parametrized_text(
            meaning=meaning,
            parametrized_text=parametrized_text)
        message = Message(type_of_message=type_of_message,
                          arguments=arguments)
        return message

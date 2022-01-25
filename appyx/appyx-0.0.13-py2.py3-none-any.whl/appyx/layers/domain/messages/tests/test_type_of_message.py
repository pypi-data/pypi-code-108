from unittest import TestCase

from appyx.layers.application.interactions.parameters.parameter import Parameter
from appyx.layers.application.interactions.validators.generic import IsString, NotEmptyString, IsAnID
from appyx.layers.domain.errors import BaseErrorFactory
from appyx.layers.domain.messages.exceptions import CreationError
from appyx.layers.domain.messages.type_of_message import TypeOfMessage


class TypeOfMessageTest(TestCase):
    def setUp(self):
        super().setUp()
        self._error_factory = BaseErrorFactory()

    def test_it_can_be_queried_for_its_meaning(self):
        # Given a type of message
        service_unavailable_text = "This service is unavailable."
        service_unavailable_meaning = "service_unavailable"
        type_of_message = TypeOfMessage(meaning=service_unavailable_meaning, text_template=service_unavailable_text)

        # When it is queried for its meaning
        has_expected_meaning = type_of_message.means(service_unavailable_meaning)

        # Then it returns its meaning
        self.assertTrue(has_expected_meaning)

    def test_two_can_mean_the_same_with_different_text(self):
        # Given two types of message with the same meaning and different text
        english_text = "This service is unavailable."
        spanish_text = "Este servicio no está disponible."
        meaning = 'service_unavailable'
        english_type_of_message = TypeOfMessage(meaning=meaning, text_template=english_text)
        spanish_type_of_message = TypeOfMessage(meaning=meaning, text_template=spanish_text)

        # When they are compared
        they_are_the_same_message = english_type_of_message.has_same_meaning_as(spanish_type_of_message)

        # Then they are equal
        self.assertTrue(they_are_the_same_message)

    def test_it_can_give_an_example_text(self):
        # Given a type of message
        type_of_message = TypeOfMessage(
            meaning='user_disconnected',
            text_template="The user {name} is disconnected.",
            parameter_list=[Parameter(name="name", example_argument="julian")]
        )

        # When it is queried for a text example
        example_text = type_of_message.example_text()

        # Then it returns a text presentation using example arguments for its parameters
        self.assertEqual("The user julian is disconnected.", example_text)

    def test_it_can_be_defined_with_a_list_of_text_and_parameters(self):
        # Given a type of message
        user_name = Parameter(name="name", example_argument="julian")
        type_of_message = TypeOfMessage.new_with_parametrized_text(
            meaning="user_disconnected",
            parametrized_text=["The user ", user_name, " is disconnected."]
        )

        # When it is queried for a text example
        example_text = type_of_message.example_text()

        # Then it returns a text presentation using example arguments for its parameters
        self.assertEqual("The user julian is disconnected.", example_text)

    def test_it_cannot_be_created_if_parameter_names_dont_match_text_placeholders(self):
        # Given a text with placeholders and a list of parameters with names that don't match the text's placeholders
        text = "There have been {amount} accidents in the workplace this year."
        parameter_list = [Parameter(name="age", example_argument=13)]
        raised_exception = None

        # When it is attempted to create a type of message with that text and those parameters
        try:
            TypeOfMessage(meaning="yearly_workplace_accidents", text_template=text, parameter_list=parameter_list)
        except CreationError as exception:
            raised_exception = exception

        # Then no instance is created and an error is raised informing the mismatch
        self.assertEqual("Cannot create instance of TypeOfMessage: Parameter named: amount not found",
                         str(raised_exception))

    def test_it_cannot_be_created_if_examples_are_missing_from_parameters(self):
        # Given a parametrized text with missing examples
        parametrized_text = ["There have been ", Parameter(name="amount"), "accidents in the workplace this year."]
        raised_exception = None

        # When it is attempted to create a type of message with that text
        try:
            TypeOfMessage.new_with_parametrized_text("yearly_workplace_accidents", parametrized_text)
        except CreationError as exception:
            raised_exception = exception

        # Then no instance is created and an error is raised informing the missing examples
        self.assertEqual(
            "Cannot create instance of TypeOfMessage: Parameter with name amount missing an example argument",
            str(raised_exception))

    def test_it_shows_its_parameters(self):
        # Given a type of message
        parameter = Parameter(name="full_name", example_argument="Julian Arnesino")
        type_of_message = TypeOfMessage(
            meaning="self_declared_pep",
            text_template="The user named {full_name} has declared themselves as politically exposed.",
            parameter_list=[parameter]
        )

        # When it is queried for its parameters
        message_parameters = type_of_message.parameters()

        # Then it returns a set with its parameters
        self.assertEqual(1, message_parameters.size())
        self.assertEqual(parameter, message_parameters.get_parameter_named(parameter.name()))

    def test_it_shows_its_text_template(self):
        # Given a type of message
        actual_text_template = "The user named {full_name} has declared themselves self as politically exposed."
        type_of_message = TypeOfMessage(
            meaning="self_declared_pep",
            text_template=actual_text_template,
            parameter_list=[Parameter(name="full_name", example_argument="Julian Arnesino")]
        )

        # When it is queried for its parameters
        obtained_text_template = type_of_message.text_template()

        # Then it returns a set with its parameters
        self.assertEqual(actual_text_template, obtained_text_template)

    def test_its_string_conversion_is_its_text_template(self):
        # Given a type of message
        actual_text_template = "The user named {full_name} has declared themselves self as politically exposed."
        type_of_message = TypeOfMessage(
            meaning="self_declared_pep",
            text_template=actual_text_template,
            parameter_list=[Parameter(name="full_name", example_argument="Julian Arnesino")]
        )

        # When it is queried for its parameters
        string_representation = str(type_of_message)

        # Then it returns a set with its parameters
        self.assertEqual(actual_text_template, string_representation)

    def test_it_can_validate_argument_existence(self):
        # Given a type of message with validators
        type_of_message = TypeOfMessage(
            "self_declared_pep", "The user named {full_name} has placed an order with id {id}.",
            parameter_list=[
                Parameter(name="full_name", example_argument="John Doe"),
                Parameter(name="id", example_argument="123")
            ]
        )

        # When it is asked to validate some missing arguments
        result = type_of_message.validate_arguments({"id": 123})

        # Then the result of the validation informs of the missing argument
        self.assertIn(self._error_factory.parameter_missing_error("El parámetro full_name es obligatorio"),
                      result.errors())

    def test_it_can_validate_argument_values(self):
        # Given a type of message with validators
        type_of_message = TypeOfMessage(
            "self_declared_pep", "The user named {full_name} has placed an order with id {id}.",
            parameter_list=[
                Parameter(name="full_name", validators=[IsString(), NotEmptyString()], example_argument="John Doe"),
                Parameter(name="id", validators=[IsAnID()], example_argument="123")
            ]
        )
        invalid_id = "0asd"

        # When it is asked to validate some invalid arguments
        result = type_of_message.validate_arguments({"full_name": "Julian Arnesino", "id": invalid_id})

        # Then the result of the validation informs of the invalid argument
        validator_error = self._error_factory.simple_error('Este campo debe ser un ID válido')
        expected_error = self._error_factory.parameter_validation_error("id", invalid_id, [validator_error])
        self.assertIn(expected_error, result.errors())

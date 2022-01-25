from unittest import TestCase

from appyx.layers.application.interactions.parameters.parameter import Parameter
from appyx.layers.application.interactions.validators.generic import NotNone
from appyx.layers.domain.exceptions.message import MessageMissingArgumentsException, \
    MessageWithInvalidArgumentsException
from appyx.layers.domain.messages.message import Message
from appyx.layers.domain.messages.type_of_message import TypeOfMessage


class MessageTest(TestCase):
    def test_it_can_be_displayed_as_text_when_it_does_not_have_arguments(self):
        # Given a message created from a type of message
        operation_failed_text = 'The operation has failed for undisclosed reasons.'
        type_of_message = TypeOfMessage(meaning='operation_failed', text_template=operation_failed_text)
        message = Message(type_of_message)

        # When it is queried for its text presentation
        message_text = message.text()
        message_string = str(message)

        # Then it returns the type's text
        self.assertEqual(operation_failed_text, message_text)
        self.assertEqual(operation_failed_text, message_string)

    def test_it_can_be_displayed_as_text_when_its_parameters_have_arguments(self):
        # Given a message
        parametrized_text = ["There have been ", Parameter(name="amount", example_argument=4), " accidents this year."]
        type_of_message = TypeOfMessage.new_with_parametrized_text('yearly_workplace_accidents', parametrized_text)
        message = Message(type_of_message, arguments={"amount": 15})

        # When it is queried for its text presentation
        message_text = message.text()
        message_string = str(message)

        # Then it returns a human-readable text using the given argument values for its parameters
        self.assertEqual(message_text, "There have been 15 accidents this year.")
        self.assertEqual(message_string, "There have been 15 accidents this year.")

    def test_it_can_be_instantiated_with_argument_names_as_keywords(self):
        # Given a type of message with parameters
        avoidable_amount = Parameter(name="avoidable_amount", example_argument=4)
        total_amount = Parameter(name="total_amount", example_argument=5)

        parametrized_text = ["Approximately ", avoidable_amount, " out of ", total_amount, " accidents were avoidable."]
        type_of_message = TypeOfMessage.new_with_parametrized_text('yearly_workplace_accidents', parametrized_text)

        # When a message of that type is instantiated with arguments as keywords
        message = Message(type_of_message, avoidable_amount=5, total_amount=7)

        # Then it can use them in its text presentation
        self.assertEqual("Approximately 5 out of 7 accidents were avoidable.", message.text())

    def test_it_can_combine_dict_arguments_and_keyword_arguments(self):
        # Given a type of message with parameters
        avoidable_amount = Parameter(name="avoidable_amount", example_argument=4)
        total_amount = Parameter(name="total_amount", example_argument=5)

        parametrized_text = ["Approximately ", avoidable_amount, " out of ", total_amount, " accidents were avoidable."]
        type_of_message = TypeOfMessage.new_with_parametrized_text('yearly_workplace_accidents', parametrized_text)

        # When a message of that type is instantiated with arguments as keywords
        message = Message(type_of_message, arguments={"total_amount": 7}, avoidable_amount=5)

        # Then it can use them in its text presentation
        self.assertEqual("Approximately 5 out of 7 accidents were avoidable.", message.text())

    def test_it_ignores_unused_arguments(self):
        # Given a type of message with parameters
        avoidable_amount = Parameter(name="avoidable_amount", example_argument=4)
        total_amount = Parameter(name="total_amount", example_argument=5)

        parametrized_text = ["Approximately ", avoidable_amount, " out of ", total_amount, " accidents were avoidable."]
        type_of_message = TypeOfMessage.new_with_parametrized_text('yearly_workplace_accidents', parametrized_text)

        # When a message of that type is instantiated with arguments as keywords
        message = Message(type_of_message, avoidable_amount=5, total_amount=7, roberto="roberto")

        # Then it can use them in its text presentation
        self.assertEqual("Approximately 5 out of 7 accidents were avoidable.", message.text())

    def test_it_cannot_be_instantiated_without_required_arguments(self):
        # Given a type of message
        parametrized_text = ["There have been ", Parameter(name="amount", example_argument=4), " accidents this year."]
        type_of_message = TypeOfMessage.new_with_parametrized_text('yearly_workplace_accidents', parametrized_text)
        raised_exception = None

        # When it is attempted to create a message with that type and with missing arguments
        try:
            Message(type_of_message)
        except MessageMissingArgumentsException as exception:
            raised_exception = exception

        # Then it fails to create and raises an exception informing the missing arguments
        self.assertEqual("El parámetro amount es obligatorio", str(raised_exception))

    def test_it_cannot_be_instantiated_with_invalid_arguments(self):
        # Given a type of message
        parametrized_text = ["There have been ", Parameter(name="amount", validators=[NotNone()], example_argument=4),
                             " accidents this year."]
        type_of_message = TypeOfMessage.new_with_parametrized_text('yearly_workplace_accidents', parametrized_text)
        raised_exception = None

        # When it is attempted to create a message with that type and with invalid arguments
        try:
            Message(type_of_message, arguments={"amount": None})
        except MessageWithInvalidArgumentsException as exception:
            raised_exception = exception

        # Then it fails to create and raises an exception informing the missing arguments
        self.assertEqual(
            "Parameter \"amount\" is not valid with argument \"None\". Reasons: Este campo no puede estar vacío",
            str(raised_exception)
        )

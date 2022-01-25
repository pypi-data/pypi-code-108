from unittest import TestCase

from appyx.layers.application.interactions.app_interaction import AppInteraction
from appyx.layers.application.interactions.parameters.test_command_parameters import TestApp


class AppInteractionWhiteBoxTest(TestCase):
    """
    Tests the implementation of the abstract class AppInteraction (ex AppCommand)
    These tests are meant to be run on appyx alone.
    It guarantees that after a refactor in appyx is made, appyx itself can check it's still working properly.
    Subclasses of AppInteraction are not required to run these tests
    since they can override the implementation of the private methods tested here.
    """

    # From here we test the implementation of the template method execute defined in AppInteraction

    def test_the_result_of_execute_is_the_result_from_execute_from_successful_result(self):
        """
            When an interaction has no errors during the validate()
            the result of execute is the result from _execute_from_successful_result()
        """
        # Given
        interaction = self._new_sample_app_interaction()

        # When
        result = interaction.execute()

        # Then
        self.assertTrue(result.is_successful())
        self.assertEqual(result.get_object(), self._hello_world())

    def _new_sample_app_interaction(self):
        hello_world = self._hello_world()

        class HelloWorldInteraction(AppInteraction):
            def _execute_from_successful_parameter_validation(self, result):
                result = super()._execute_from_successful_parameter_validation(result)
                result.set_object(hello_world)
                return result

        return HelloWorldInteraction(TestApp())

    def _hello_world(self):
        return "Hello World"

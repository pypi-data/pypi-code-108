from unittest import TestCase

from appyx.layers.application.interactions.simple_interaction import SimpleInteraction


class InteractionTest(TestCase):

    def test_the_execution_of_an_interaction_answers_a_result(self):
        # Given an interaction
        interaction = SimpleInteraction()

        # When we execute it
        result = interaction.execute()

        # Then we get a result
        self.assertTrue(result.is_successful() or result.has_errors())

    def test_before_executing_it_we_can_validate_an_interaction(self):
        # Given an interaction
        interaction = SimpleInteraction()

        # When we validate it
        result = interaction.validate()

        # Then we get a result
        self.assertTrue(result.is_successful() or result.has_errors())

    def test_if_the_interaction_isnt_valid_the_execution_will_fail(self):
        # Given an invalid interaction
        interaction = self._invalid_interaction()
        result = interaction.validate()
        self.assertFalse(result.is_successful())

        # When we know it's invalid
        execution_result = interaction.execute()

        # Then the execution fails
        self.assertFalse(execution_result.is_successful())

    def _invalid_interaction(self):
        class InvalidInteraction(SimpleInteraction):
            def validate(self):
                result = super().validate()
                result.add_error("I am invalid")
                return result

        return InvalidInteraction()

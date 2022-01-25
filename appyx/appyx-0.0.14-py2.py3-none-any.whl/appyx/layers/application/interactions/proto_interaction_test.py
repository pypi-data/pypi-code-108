from unittest import TestCase


class AppyxTest:
    """
    This class acts as a wrapper for the abstract test classes below.
    This allows us to define abstract test methods that don't get executed by the testing framework.
    """
    class ProtoInteractionTest(TestCase):
        """
        This class provides tests for the behavior defined at the ProtoInteraction level.
        If you create a TestCase to test a ProtoInteraction subclass, you should inherit from this class
        to guarantee that the abstract behavior is still followed by the concrete class.
        """
        def test_a_proto_interaction_does_not_raise_an_exception_when_executed(self):
            # Given a sample proto interaction
            interaction = self._new_sample_proto_interaction()
            exception_not_raised = True

            # When we execute it
            try:
                interaction.execute()
            except:
                exception_not_raised = False

            # Then it does not raise an exception
            self.assertTrue(exception_not_raised, "Proto interactions should not raise exceptions during execution")

        def test_proto_interaction_answers_a_result_when_executed(self):
            # Given a sample proto interaction
            interaction = self._new_sample_proto_interaction()

            # When we execute it
            result = interaction.execute()

            # Then we get a result
            self.assertTrue(result.is_successful() or result.has_errors())

        def _new_sample_proto_interaction(self):
            raise NotImplementedError("Subclass responsibility")

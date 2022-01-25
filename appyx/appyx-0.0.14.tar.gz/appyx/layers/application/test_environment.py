from unittest import TestCase

from appyx.layers.application.environment import Environment


class TestEnvironment(Environment):

    def _application_class(self):
        from appyx.layers.application.interactions.parameters.test_command_parameters import TestApp
        return TestApp

    def _running_context(self):
        return 'a running context'


class EnvironmentTest(TestCase):

    def test_01_answers_the_same_application(self):
        first_asked_app = TestEnvironment().current_app()

        second_asked_app = TestEnvironment().current_app()

        self.assertIs(first_asked_app, second_asked_app)

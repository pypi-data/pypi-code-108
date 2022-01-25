from unittest import TestCase


class ApplicationTest(TestCase):

    def test_01_answers_the_same_business(self):
        from appyx.layers.application.test_environment import TestEnvironment
        first_asked_business = TestEnvironment().current_app().current_business()

        second_asked_business = TestEnvironment().current_app().current_business()

        self.assertIs(first_asked_business, second_asked_business)

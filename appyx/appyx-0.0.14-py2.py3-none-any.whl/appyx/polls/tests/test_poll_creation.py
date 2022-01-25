from unittest import TestCase

from appyx.layers.application.environment import Environment


class PollCreation(TestCase):
    def test_01_our_business_can_show_the_latest_polls(self):
        business = self._new_poll_station()

        latest_questions = business.latest_questions()

        self.assertEqual(0, len(latest_questions))

    def test_02_questions_can_be_created_and_published(self):
        business = self._new_poll_station()

        business.create_question_with_choices("What's up", ["Not much", "The sky", "Just hacking again"])

        latest_questions = business.latest_questions()
        self.assertEqual(1, len(latest_questions))

    def test_03_questions_have_the_correct_text(self):
        business = self._new_poll_station()

        question_text = "What's up"
        business.create_question_with_choices(question_text, ["Not much", "The sky", "Just hacking again"])

        latest_question = business.latest_questions()[0]
        self.assertEqual(question_text, latest_question.text())

    def test_04_questions_have_the_correct_creation_time(self):
        business = self._new_poll_station()
        clock = business.clock()
        question_creation_time = clock.current_time()

        business.create_question_with_choices("What's up", ["Not much", "The sky", "Just hacking again"])
        clock.advance_1_day()

        latest_question = business.latest_questions()[0]
        self.assertEqual(question_creation_time, latest_question.creation_time())

    def test_05_questions_have_the_correct_choices(self):
        business = self._new_poll_station()

        choices_texts = ["Not much", "The sky", "Just hacking again"]
        business.create_question_with_choices("What's up", choices_texts)
        latest_question = business.latest_questions()[0]
        self.assertEqual(choices_texts, latest_question.choices_texts())

    def test_06_a_newly_created_question_has_0_votes_on_its_choices(self):
        business = self._new_poll_station()
        business.create_question_with_choices("What's up", ["Not much", "The sky", "Just hacking again"])
        latest_question = business.latest_questions()[0]

        self.assertEqual(0, latest_question.choices()[0].amount_of_votes())
        self.assertEqual(0, latest_question.choices()[1].amount_of_votes())
        self.assertEqual(0, latest_question.choices()[2].amount_of_votes())

    def test_07_a_vote_can_be_casted_on_a_question_choice(self):
        business = self._new_poll_station()
        business.create_question_with_choices("What's up", ["Not much", "The sky", "Just hacking again"])
        latest_question = business.latest_questions()[0]

        business.vote(latest_question, latest_question.choices()[1])

        latest_question = business.latest_questions()[0]
        self.assertEqual(0, latest_question.choices()[0].amount_of_votes())
        self.assertEqual(1, latest_question.choices()[1].amount_of_votes())
        self.assertEqual(0, latest_question.choices()[2].amount_of_votes())

    # --- private methods ---

    def _new_poll_station(self):
        business = Environment().current_app().current_business()
        return business

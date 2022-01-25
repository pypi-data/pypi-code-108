class PollStation:
    def __init__(self, clock, questions_archive):
        self._clock = clock
        self._questions = questions_archive

    def clock(self):
        return self._clock

    def latest_questions(self):
        return self._questions.latest(5)

    def create_question_with_choices(self, question_text, choices_texts):
        new_question = Question(question_text, choices_texts, self._clock.current_time())
        self._questions.add(new_question)

    def vote(self, question, choice):
        if choice not in question.choices():
            raise AssertionError('Choice must belong to question')
        choice.increment_votes()


class Choice:
    def __init__(self, text, votes):
        self._text = text
        self._votes = votes

    def text(self):
        return self._text

    def amount_of_votes(self):
        return self._votes

    def increment_votes(self):
        self._votes = self._votes + 1


class Question:
    def __init__(self, text, choices_texts, creation_time):
        self._text = text
        self._choices = [Choice(text, 0) for text in choices_texts]
        self._creation_time = creation_time

    def text(self):
        return self._text

    def choices(self):
        return self._choices

    def choices_texts(self):
        return [choice.text() for choice in self.choices()]

    def creation_time(self):
        return self._creation_time


class FakeClock:
    def __init__(self):
        self._current_time = 1

    def current_time(self):
        return self._current_time

    def advance_1_day(self):
        self._current_time = self._current_time + 1


class QuestionsArchive:
    def __init__(self):
        self._objects = []

    def latest(self, an_amount):
        answer_list = self._objects.copy()
        answer_list.sort(key=lambda question: question.creation_time())
        return answer_list[:an_amount]

    def add(self, question):
        self._objects.append(question)

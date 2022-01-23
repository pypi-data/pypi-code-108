from copy import deepcopy
import csv
from io import StringIO
import logging
import datetime

from nerddiary.bot.model import Poll, Question, ValueLabel, User

from typing import Dict, List, Tuple, cast

logger = logging.getLogger("nerddiary.bot.workflow")


class BotWorkflow:
    def __init__(self, poll: Poll, user: User) -> None:
        if not isinstance(poll, Poll):
            raise ValueError("Poll must be an instance of `Poll` class")

        # deepcopy poll to prevent config reloads impacting ongoing polls
        self._poll = deepcopy(poll)
        self._answers_raw: Dict[str, Tuple[str, ValueLabel]] = {}
        self._poll_iterator = iter(self._poll.questions)
        self._user = user
        self._current_question: str | None = None

        user_timezone = user.timezone
        if self._poll.hours_over_midgnight:
            now = datetime.datetime.now(user_timezone)
            check = now - datetime.timedelta(hours=self._poll.hours_over_midgnight)
            if check.date() < now.date():
                self._poll_start_timestamp = check
            else:
                self._poll_start_timestamp = datetime.datetime.now(user_timezone)
        else:
            self._poll_start_timestamp = datetime.datetime.now(user_timezone)
        self._poll_created_utc_timestamp = datetime.datetime.now()
        self._delayed = False
        self._all_set = False

    @property
    def all_set(self) -> bool:
        return self._all_set

    @property
    def delayed(self) -> bool:
        return self._delayed

    @property
    def started(self) -> bool:
        return self._current_question is not None

    @property
    def poll_start_timestamp(self) -> datetime.datetime:
        return self._poll_start_timestamp

    @property
    def questions(self) -> Dict[str, Question]:
        return self._poll.questions

    @property
    def answers(self) -> List[ValueLabel]:
        return [
            val[1]
            for q, val in self._answers_raw.items()
            if not self._poll.questions[q].ephemeral
        ]

    def _add_answer(self, val: ValueLabel, question: str, key: str):
        self._answers_raw[question] = (key, val)

    def add_answer(self, key: str) -> bool:
        assert self._current_question is not None

        question = self._poll.questions[self._current_question]

        if (
            question.delay_on and key in question.delay_on  # type:ignore
        ):
            self._delayed = True
            return False

        value = None
        depends_on = question.depends_on

        if depends_on:
            dep_key, dep_value = self._answers_raw[depends_on]
            value = question.get_raw_value(key, dep_key, dep_value, self._user)
        else:
            value = question.get_raw_value(key, user=self._user)

        self._add_answer(value, self._current_question, key)

        return True

    def get_next_question(self) -> str | None:
        if self._delayed:
            self._delayed = False

            return self._current_question
        else:
            try:
                new_question = self._current_question = next(self._poll_iterator)

                if self._poll.questions[new_question].auto:
                    # If auto question - store value and recursively proceed to the next
                    self._process_auto_question()
                    return self.get_next_question()

                return new_question
            except StopIteration:
                self._all_set = True
                return None

    def _process_auto_question(self) -> None:
        assert self._current_question is not None
        question = self._poll.questions[self._current_question]

        depends_on = question.depends_on

        if depends_on:
            dep_key, dep_value = self._answers_raw[depends_on]
            value = question.get_raw_value(
                dep_key=dep_key, dep_value=dep_value, user=self._user
            )
        else:
            value = question.get_raw_value(user=self._user)

        self._add_answer(
            value,
            self._current_question,
            self._current_question,
        )

    def _get_select_raw(self) -> Dict[str, ValueLabel]:
        cur_question = None

        if self._current_question is None:
            raise ValueError(
                "Tried to get select list before starting to poll questions"
            )
        else:
            cur_question = self._poll.questions[self._current_question]

        depends_on = cur_question.depends_on

        ret = {}
        if depends_on:
            dep_key, dep_value = self._answers_raw[depends_on]

            ret = deepcopy(cur_question.get_select(dep_key, dep_value, self._user))  # type: ignore
        else:
            ret = deepcopy(cur_question.get_select(user=self._user))

        return ret  # type: ignore

    def get_select(self) -> Dict[str, str]:
        raw = self._get_select_raw()

        ret = {}

        for sel_key, sel_val in raw.items():
            sel_val = cast(ValueLabel, sel_val)
            ret[sel_key] = sel_val.label

        return ret

    def get_save_data(self) -> str:

        if self.all_set is False:
            logger.warn("Save data requested before finishing all questions")

        ret = []
        ret.append(self._poll_start_timestamp)

        for q_key, (key, value) in self._answers_raw.items():
            question = self.questions[q_key]

            if question.ephemeral:
                continue

            ret.append(question.get_save_value(value))

        csv_str = StringIO()
        writer = csv.writer(csv_str, dialect="excel", quoting=csv.QUOTE_ALL)
        writer.writerow(ret)

        return csv_str.getvalue()

    def get_delay_time(self) -> datetime.timedelta:
        assert self._current_question

        delay = self._poll.questions[self._current_question].delay_time
        if not delay:
            delay = datetime.timedelta(seconds=0)

        return delay


if __name__ == "__main__":
    pass

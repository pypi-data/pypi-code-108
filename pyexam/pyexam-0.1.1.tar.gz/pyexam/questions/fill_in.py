from typing import Literal

from pydantic import root_validator

from . import Question, QuestionType


class FillIn(Question):
    type: Literal[QuestionType.fill_in] = QuestionType.fill_in

    @root_validator
    def check_text_separator(cls, values):
        text = values.get('text')
        count = text.count('\\fillin[')
        if count == 0:
            raise ValueError('unused separator')
        return values

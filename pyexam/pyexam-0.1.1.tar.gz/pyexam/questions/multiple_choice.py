from typing import Annotated, Literal

from pydantic import BaseModel, Field, root_validator

from . import Question, QuestionType


class MultipleChoiceOption(BaseModel):
    text: Annotated[str, Field(strip_whitespace=True, min_length=1)]
    correct: bool = False


class MultipleChoice(Question):
    type: Literal[QuestionType.multiple_choice] = QuestionType.multiple_choice
    options: Annotated[list[MultipleChoiceOption], Field(min_items=2)]

    @property
    def correct_choices(self) -> list[str]:
        return [x.text for x in self.options if x.correct]

    @root_validator
    def check_correct_option(cls, values):
        options = values.get('options')
        if not any(map(lambda x: x.correct, options)):
            raise ValueError('at least 1 option must be correct')
        return values

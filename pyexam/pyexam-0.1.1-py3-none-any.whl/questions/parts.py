from typing import Annotated, Literal, Union

from pydantic import Field

from . import FillIn, LongAnswer, MultipleChoice, Question, QuestionType

PartsQuestionType = Annotated[Union[LongAnswer, MultipleChoice, FillIn], Field(discriminator='type')]


class Parts(Question):
    type: Literal[QuestionType.parts] = QuestionType.parts
    parts: Annotated[list[PartsQuestionType], Field(min_items=1)]

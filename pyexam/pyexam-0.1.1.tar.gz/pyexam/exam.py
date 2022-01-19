from typing import Annotated, Optional, Union

from pydantic import BaseModel, Field, root_validator

from .questions import FillIn, LongAnswer, MultipleChoice, Parts

QuestionType = Annotated[Union[Parts, LongAnswer, MultipleChoice, FillIn], Field(discriminator='type')]


class Section(BaseModel):
    name: Annotated[str, Field(strip_whitespace=True, min_length=1)]
    questions: Annotated[list[QuestionType], Field(min_items=1)]
    # could remove type and have implicit conversion -> list[Union[LongAnswer, MultipleChoice, FillIn]]


class Exam(BaseModel):
    name: Annotated[str, Field(strip_whitespace=True, min_length=1)]
    version: int = 0
    header: str = ''
    questions: Optional[list[QuestionType]]
    sections: Optional[list[Section]]

    @root_validator
    def check_exam_questions(cls, values):
        questions, sections = values.get('questions'), values.get('sections')
        arr = [x for x in [questions, sections] if x is not None]
        if len(arr) != 1:
            raise ValueError('a single root key questions or sections required')
        if len(arr[0]) == 0:
            raise ValueError('questions/sections cannot be empty')
        return values

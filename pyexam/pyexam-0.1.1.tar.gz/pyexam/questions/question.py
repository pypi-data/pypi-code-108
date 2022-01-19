from enum import Enum
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    long_answer = 'long-answer'
    multiple_choice = 'multiple-choice'
    fill_in = 'fill-in'
    parts = 'parts'


class Question(BaseModel):
    type: Literal[QuestionType.long_answer,
                  QuestionType.multiple_choice,
                  QuestionType.fill_in,
                  QuestionType.parts]
    text: Annotated[str, Field(strip_whitespace=True, min_length=1)]
    points: Annotated[Optional[int], Field(ge=0)]

    class Config:
        use_enum_values = True

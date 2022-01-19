from typing import Annotated, Literal

from pydantic import Field, root_validator, validator

from . import Question, QuestionType


def norm_size(size: str) -> str:
    if not (size.endswith('in') or size.endswith('cm')):
        raise ValueError('height must be cm/in')
    if not size[:-2].isnumeric:
        raise ValueError('invalid numeric height')
    return size


class LongAnswer(Question):
    type: Literal[QuestionType.long_answer] = QuestionType.long_answer
    answer: Annotated[str, Field(strip_whitespace=True, min_length=1)]
    lines: str = ''
    spaces: str = ''

    _normalize_sizes = validator('lines', 'spaces', allow_reuse=True)(norm_size)

    @root_validator
    def check_height_sizes(cls, values):
        lines, spaces = values.get('lines'), values.get('spaces')
        if (lines == '' and spaces == '') or (lines != '' and spaces != ''):
            raise ValueError('a single key lines or spaces required')
        return values

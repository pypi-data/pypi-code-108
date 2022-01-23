""" Poll models """

from __future__ import annotations
from pydantic import BaseModel, validator
import logging
from pydantic.fields import Field, PrivateAttr
import datetime
from typing import Any, Dict, List, Optional
from .type import (
    QuestionType,
    SelectType,
    DependantSelectType,
)

logger = logging.getLogger(__name__)


def _custom_serialize_type(type: QuestionType):
    """Serialize named types back into name string"""
    return type.type


class Question(BaseModel):
    """Represents a single question within a poll"""

    type: str | SelectType | DependantSelectType | QuestionType = Field(
        description="Question type name or an inline unnamed type (must be either a SelectType or DependantSelectType)"
    )
    """Question type name or an inline unnamed type (must be either a SelectType or DependantSelectType)
    """

    code: str = Field(
        description="Question mandatory short code name. Use it in depends_on"
    )
    """Question mandatory short code name. Use it in depends_on
    """

    name: Optional[str] = Field(
        description="Question optional long name. Will be assigned the value of code if not given"
    )
    """Question optional long name. Will be assigned the value of code if not given
    """

    description: Optional[str] = Field(description="Question optional long description")
    """Question optional long description
    """

    ephemeral: Optional[bool] = Field(
        default=False,
        description="Whether the answer to this question should not end up in the stored data. Use for branching/delaying without storing the question-answer itself",
    )
    """Whether the answer to this question should not end up in the stored data. Use for branching/delaying without storing the question-answer itself"""

    depends_on: Optional[str] = Field(
        description="Question name on which this question select or value depends"
    )
    delay_time: Optional[datetime.timedelta] = Field(
        description="If `delay_on` is set => this is the timedelta for reminder"
    )
    """ If `delay_on` is set => this is the timedelta for reminder """

    delay_on: Optional[List[str]] = Field(
        description="Answer that will trigger a reminder and pause poll. Works only for questions with simple select"
    )
    """ Answer that will trigger a reminder and pause poll """

    _order: int = PrivateAttr(default=-1)

    class Config:
        json_encoders = {
            type: _custom_serialize_type
            for type in QuestionType.supported_types.values()
        }

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        # Replace type name with actual type object
        if isinstance(self.type, str):
            self.type = QuestionType.supported_types[self.type]()

        if self.name is None:
            self.name = self.code

    @validator("delay_on")
    def check_delay_time_if_delay_on(cls, v, values: Dict[str, Any]):
        if not values["delay_time"] and v:
            raise ValueError("`dalay_time` must be set for `delay_on` questions")

        return v

    @validator("delay_on")
    def check_delay_on_value_exist(cls, v, values: Dict[str, Any]):
        # Type has not been substitued yet, so have to get it from supported_types
        if isinstance(values["type"], str):
            type_cls = QuestionType.supported_types.get(values["type"])
            type = type_cls() if type_cls else None
        else:
            type = values["type"]

        if type:
            pos_values = type.get_possible_values()
            if not isinstance(pos_values, list):
                raise ValueError(
                    f"`dalay_on` value is not compatible with <{type.type}>"
                )
            if any(dep not in pos_values for dep in v):
                raise ValueError(
                    f"`dalay_on` value doesn't exist for the type {type.__class__}"
                )

        return v

    @validator("type")
    def validate_named_type_exists(cls, v: str | SelectType | DependantSelectType):
        if isinstance(v, str) and v not in QuestionType.supported_types:
            raise ValueError(f"Type <{v}> is not supported")

        return v

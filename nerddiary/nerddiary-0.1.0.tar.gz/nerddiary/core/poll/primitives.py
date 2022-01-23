""" Model primitives """

from __future__ import annotations

from pydantic import BaseModel, validator, root_validator
import pytz
import datetime

from typing import Any, Dict


class TimeZone(datetime.tzinfo):
    """Custom pydantic type wrapper for timezone"""

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="TzInfo",
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")
        try:
            tz = pytz.timezone(v)
        except pytz.UnknownTimeZoneError:
            raise ValueError("invalid timezone code")

        return tz

    def __repr__(self):
        return f"TzInfo({super().__repr__()})"


class ValueLabel(BaseModel):
    label: str
    value: Any = None

    @root_validator(pre=True)
    def check_and_convert_value_label_dict(cls, values: Dict[Any, Any]):
        if len(values) > 2:
            raise ValueError(
                'Valuelabel may only be defined in either {"value": value, "label": label} or {"value": "label"} formats'
            )

        if len(values) == 1 and "label" not in values and "value" not in values:
            val, lab = next(iter(values.items()))

            assert isinstance(lab, str), "Label must be a string"
            values = {"value": val, "label": lab}

        return values

    @validator(
        "value",
        always=True,
    )
    def set_value_to_label_if_empty(
        cls,
        v: str,
        values: Dict[str, Any],
    ):
        return v if v is not None else values.get("label")

from datetime import datetime, timezone

from ...backport.fromisoformat import fromisoformat


class DatetimeField:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, str):
            value = fromisoformat(value)

        if isinstance(value, int):
            value = datetime.fromtimestamp(value)

        if isinstance(value, float):
            value = datetime.fromtimestamp(value)

        if isinstance(value, datetime):
            return value.astimezone(tz=timezone.utc)
        else:
            raise TypeError("invalid type; expected datetime, string, int or float")


class DateISO8601Field:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        value_as_datetime = DatetimeField.validate(value)

        return value_as_datetime.isoformat()

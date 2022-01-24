from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

from tortoise import fields
from tortoise.fields import DatetimeField
from tortoise.fields.relational import ManyToManyRelation
from tortoise.models import Model

from ..json import fast_dumps
from ..json import loads as json_loads


class LocalDatetimeField(DatetimeField):
    def to_db_value(
        self, value: Optional[datetime], instance: Union[Type[Model], Model]
    ) -> Optional[datetime]:
        value = super().to_db_value(value, instance)
        if (
            value
            and value.tzinfo is not None
            and value.tzinfo.utcoffset(value) is not None
        ):
            value = value.astimezone()
        return value


class JSONField(fields.JSONField):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)  # type: ignore
        self.encoder = fast_dumps
        self.decoder = json_loads

    def to_db_value(
        self,
        value: Optional[Union[Dict[Any, Any], List[Any], str]],
        instance: "Union[Type[Model], Model]",
    ) -> Optional[str]:
        self.validate(value)
        return None if value is None else self.encoder(value)

    def to_python_value(  # type: ignore
        self, value: Optional[Union[str, Dict[Any, Any], List[Any]]]
    ) -> Optional[Union[str, Dict[Any, Any], List[Any]]]:
        if isinstance(value, str):
            return self.decoder(value)
        self.validate(value)
        return value


def ManyToManyField(
    model_name: str,
    through: Optional[str] = None,
    forward_key: Optional[str] = None,
    backward_key: str = "",
    related_name: str = "",
    on_delete: str = fields.CASCADE,
    db_constraint: bool = True,
    **kwargs: Any,
) -> ManyToManyRelation[Any]:
    return fields.ManyToManyField(  # type: ignore
        model_name=model_name,
        through=through,
        forward_key=forward_key,
        backward_key=backward_key,
        related_name=related_name,
        on_delete=on_delete,
        db_constraint=db_constraint,
        **kwargs,
    )

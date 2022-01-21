import sqlalchemy as sa
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy_jsonfield import JSONField as _JSONField
from sqlalchemy_utc import UtcDateTime as _UtcDateTime

from eztea import json

__all__ = (
    "JSONField",
    "UtcDateTime",
)


class JSONField(_JSONField):
    __doc__ = _JSONField.__doc__

    # https://sqlalche.me/e/14/cprf
    cache_ok = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            enforce_string=True,
            enforce_unicode=True,
            json=json,
            *args,
            **kwargs
        )

    def load_dialect_impl(self, dialect: DefaultDialect) -> TypeEngine:
        """Select impl by dialect.

        :return: dialect implementation depends of decoding method
        :rtype: TypeEngine
        """
        if dialect.name == "mysql":
            return dialect.type_descriptor(LONGTEXT)
        return dialect.type_descriptor(sa.UnicodeText)


class UtcDateTime(_UtcDateTime):
    __doc__ = _UtcDateTime.__doc__
    # https://sqlalche.me/e/14/cprf
    cache_ok = True

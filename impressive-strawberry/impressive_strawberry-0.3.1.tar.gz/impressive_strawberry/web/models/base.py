from __future__ import annotations

import abc
import datetime
import uuid

import pydantic

import impressive_strawberry.database.tables

__all__ = (
    "StrawberryModel",
    "StrawberryORMModel",
)


class StrawberryModel(pydantic.BaseModel, metaclass=abc.ABCMeta):
    """
    Base model for :mod:`impressive_strawberry`\\ 's :mod:`pydantic` models.
    """

    class Config(pydantic.BaseModel.Config):
        json_encoders = {
            uuid.UUID:
                lambda obj: str(obj),
            datetime.datetime:
                lambda obj: obj.timestamp(),
            impressive_strawberry.database.tables.Alloy:
                lambda obj: obj.value,
            impressive_strawberry.database.tables.WebhookKind:
                lambda obj: obj.value,
        }


class StrawberryORMModel(StrawberryModel, metaclass=abc.ABCMeta):
    """
    Extension to :class:`.StrawberryModel` which enables the :attr:`.StrawberryModel.Config.orm_mode`.
    """

    class Config(StrawberryModel.Config):
        orm_mode = True

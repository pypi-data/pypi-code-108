# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

from pydantic import BaseModel, Field, ValidationError
from pydantic.generics import GenericModel

__all__ = ["IntrospectableObject", "Field", "ValidationError", "GenericModel"]


class IntrospectableObject(BaseModel):
    """Introspectable object based on pydantic"""

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

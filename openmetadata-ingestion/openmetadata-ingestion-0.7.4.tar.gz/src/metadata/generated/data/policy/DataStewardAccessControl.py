# generated by datamodel-codegen:
#   filename:  data/policy/DataStewardAccessControl.json
#   timestamp: 2022-01-19T08:15:11+00:00

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Model(BaseModel):
    __root__: Any = Field(
        ...,
        description='Policy for Data Steward Role to perform operations on metadata entities',
    )

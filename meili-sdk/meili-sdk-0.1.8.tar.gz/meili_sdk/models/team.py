import typing as t

from meili_sdk.exceptions import ValidationError
from meili_sdk.models.base import BaseModel


class Team(BaseModel):
    uuid: t.Optional[str] = None
    title: str
    slug: t.Optional[str] = None
    description: t.Optional[str] = None
    operation_type: t.Optional[str] = None

    def validate_operation_type(self):
        if self.operation_type not in ["indoor", "outdoor"]:
            raise ValidationError(
                f"Invalid operation type set for team: {self.operation_type}"
            )
        return self.operation_type

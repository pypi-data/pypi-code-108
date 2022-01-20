from datetime import datetime
from typing import Optional, Union, List
from uuid import UUID

from datalogue.errors import DtlError
from datalogue.dtl_utils import map_option, _parse_uuid, _parse_datetime


class Tag:
    """
    A unique tag of metadata that can be applied to datastores for targeted collection, viewing, and action orchestrations
    """

    def __init__(
        self,
        name: str,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        created_by: Optional[UUID] = None,
    ):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.created_by = created_by

    def __eq__(self, other):
        return (
            (self.name == other.name)
            and (self.created_at == other.created_at)
            and (self.created_by == other.created_by)
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(\n"
            f"id= {self.id!r},\n "
            f"name= {self.name!r},\n"
            f"created_at= {self.created_at!r},\n"
            f"created_by= UUID({self.created_by!r})\n"
            f")"
        )

    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "Tag"]:
        name = payload.get("name")
        if name is None:
            return DtlError("'name' is missing for a tag")

        id = map_option(payload.get("id"), _parse_uuid)
        created_at = payload.get("createdAt")
        created_by = payload.get("createdBy")
        if isinstance(created_at, DtlError):
            return created_at

        return Tag(name, id, created_at, created_by)

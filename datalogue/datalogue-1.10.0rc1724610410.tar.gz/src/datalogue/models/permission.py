from typing import Union

from datalogue.errors import DtlError, _enum_parse_error
from datalogue.dtl_utils import SerializableStringEnum
from datalogue.models.scope_level import Scope
from uuid import UUID


class Permission(SerializableStringEnum):
    """
    Class that handles all permission types
    """

    Share = "Share"
    Write = "Write"
    Read = "Read"

    @staticmethod
    def parse_error(s: str) -> str:
        return DtlError(_enum_parse_error("permission type", s))

    @staticmethod
    def from_string(string: str) -> Union[DtlError, "Permission"]:
        return SerializableStringEnum.from_str(Permission)(string)


# TODO change to the standard Permission Model (write, read, share)
class OntologyPermission(SerializableStringEnum):
    """
    Class that handles Ontology permission types
    """

    Write = "Write"
    Read = "Read"

    @staticmethod
    def parse_error(s: str) -> str:
        return DtlError(_enum_parse_error("Ontology permission type", s))

    @staticmethod
    def from_string(string: str) -> Union[DtlError, "OntologyPermission"]:
        return SerializableStringEnum.from_str(OntologyPermission)(string)


# TODO change to the standard Permission Model (write, read, share)
class CredentialPermission(SerializableStringEnum):
    """
    Class that handles Credential permission types
    """

    Write = "Write"
    Use = "Use"
    Read = "Read"

    @staticmethod
    def parse_error(s: str) -> str:
        return DtlError(_enum_parse_error("permission type", s))

    @staticmethod
    def from_string(string: str) -> Union[DtlError, "CredentialPermission"]:
        return SerializableStringEnum.from_str(CredentialPermission)(string)


class ObjectType(SerializableStringEnum):
    """
    Class that handles object types
    """

    Regex = "Regex"
    Classifier = "Classifier"
    Tag = "Tag"
    PipelineTemplate = "PipelineTemplate"
    DataProduct = "DataProduct"

    @staticmethod
    def parse_error(s: str) -> str:
        return DtlError(_enum_parse_error("object type", s))

    @staticmethod
    def from_string(string: str) -> Union[DtlError, "ObjectType"]:
        return SerializableStringEnum.from_str(ObjectType)(string)


class SharePermission:
    """
    This is a class that represents an object permission.

    Attributes:
        target_id (UUID): the uuid of the User, Group or Organization..
        target_type (Scope): the target you are sharing with. It can be a User, Group or Organization.
        permission (Permission): the type of permission you want to grant. It can be Read, Write or Share.
    """

    def __init__(
        self, object_type: ObjectType, target_id: UUID = None, target_type: Scope = None, permission: Permission = None,
    ):
        """
        The constructor for Share class.

        Parameters:
            object_type (ObjectType): the type of object
            target_id (UUID): the uuid of the User, Group or Organization..
            target_type (Scope): the target you are sharing with. It can be a User, Group or Organization.
            permission (Permission): the type of permission you want to grant. It can be Read, Write or Share.
        """

        self.object_type = object_type
        self.target_id = target_id
        self.target_type = target_type
        self.permission = permission

    def __repr__(self):
        return (
            f"{self.permission!r} permissions for this {self.object_type!r} are extended to "
            f"target= {self.target_type!r} "
            f"with id= {self.target_id!r}"
        )

    def from_payload(self, payload: dict) -> Union[DtlError, "SharePermission"]:

        target_id = payload.get("targetId")
        if target_id is None or not isinstance(target_id, str):
            return DtlError("'targetId' is missing or not a string")

        target_type = payload.get("targetType")
        if target_type is None or not isinstance(target_type, str):
            return DtlError("'targetType' is missing or not a string")

        permission = payload.get("permission")
        if permission is None or not isinstance(permission, str):
            return DtlError("'permission' is missing or not a string")

        return SharePermission(self.object_type, target_id, target_type, permission)


class UnsharePermission:
    """
    This is a class that represents an object permission removal.
    Attributes:
        target_id (UUID): the uuid of the User, Group or Organization..
        target_type (Scope): the target you are unsharing with. It can be a User, Group or Organization.
        permission (Permission): the type of permission you want to remove. It can be Read, Write or Share.
    """

    def __init__(
        self, object_type: ObjectType, target_id: UUID = None, target_type: Scope = None, permission: Permission = None,
    ):
        """
        The constructor for Unshare class.
        Parameters:
            object_type (ObjectType): the type of object
            target_id (UUID): the uuid of the User, Group or Organization..
            target_type (Scope): the target you are unsharing with. It can be a User, Group or Organization.
            permission (Permission): the type of permission you want to remove. It can be Read, Write or Share.
        """

        self.object_type = object_type
        self.target_id = target_id
        self.target_type = target_type
        self.permission = permission

    def __repr__(self):
        return (
            f"{self.permission!r} permissions for this {self.object_type!r} are withdrawn from "
            f"target= {self.target_type!r} "
            f"with id= {self.target_id!r}"
        )

    def from_payload(self, payload: dict) -> Union[DtlError, "UnsharePermission"]:

        target_id = payload.get("targetId")
        if target_id is None or not isinstance(target_id, str):
            return DtlError("'targetId' is missing or not a string")

        target_type = payload.get("targetType")
        if target_type is None or not isinstance(target_type, str):
            return DtlError("'targetType' is missing or not a string")

        permission = payload.get("permission")
        if permission is None or not isinstance(permission, str):
            return DtlError("'permission' is missing or not a string")

        return UnsharePermission(self.object_type, target_id, target_type, permission)

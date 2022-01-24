# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
from typing import Union

from ops.model import Application, Relation, Unit


class BaseException(Exception):
    """Base exception for exceptions from this library."""


class InvalidRoleError(BaseException):
    """The specified role is not one of "provides", "requires", or "peer".

    The following property is available:

        * role: The role which was invalid.
    """

    def __init__(self, role):
        super().__init__(role)
        self.role = role


class SchemaError(BaseException):
    """Base class for errors with the schema."""


class SchemaParseError(SchemaError):
    """There was an error parsing the schemas YAML."""


class InvalidSchemaError(SchemaError):
    """An invalid schema (not a valid JSONSchema) was found in the schema doc.

    The following property is available:

        * version: The version of the schema which was invalid.
    """

    def __init__(self, version):
        super().__init__(version)
        self.version = version


class InvalidSchemaVersionError(InvalidSchemaError):
    """An invalid version (not an int, nor str of form "vX" where X is an int) was found
    in the schema doc.

    The following property is available:

        * version: The schema version which was invalid.
    """


class RelationException(BaseException):
    """Base exception for relation exceptions from this library."""

    def __init__(self, relation: Relation):
        super().__init__(f"{relation.name}:{relation.id}")
        self.relation = relation


class UnversionedRelation(RelationException):
    """The relation is not yet complete due to missing remote version info."""


class IncompleteRelation(RelationException):
    """The relation is not yet complete due to missing remote data."""


class RelationError(RelationException):
    """Base class for actual errors from this library."""


class IncompatibleVersionsError(RelationError):
    """The remote application does not support any common schema versions."""


class RelationParseError(RelationError):
    """An error was encountered parsing data from the relation."""

    def __init__(self, relation: Relation, entity: Union[Application, Unit], key: str):
        super().__init__(relation)
        self.args = (f"{relation.name}:{relation.id} {entity.name} '{key}'",)
        self.entity = entity
        self.key = key


class RelationDataError(RelationError):
    """An error was encountered validating data against the schema."""

    def __init__(self, relation: Relation, entity: Union[Application, Unit]):
        super().__init__(relation)
        self.args = (f"{relation.name}:{relation.id} {entity.name}",)
        self.entity = entity


class RelationPermissionError(RelationDataError):
    """An attempt to write data to a disallowed bucket."""

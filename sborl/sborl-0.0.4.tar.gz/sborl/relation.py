# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
import logging
from functools import cached_property
from pathlib import Path
from typing import Dict, Union

import jsonschema
import yaml
from ops.charm import CharmBase
from ops.framework import Object
from ops.model import (
    ActiveStatus,
    Application,
    BlockedStatus,
    Relation,
    Unit,
    WaitingStatus,
)

from . import errors
from .events import EndpointWrapperEvents

try:
    from functools import cache
except ImportError:
    # create shim for functools.cache in 3.8
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


log = logging.getLogger(__name__)


VERSION_KEY = "_supported_versions"
ROLE_MAP = {
    "provides": ("provides", "requires"),
    "requires": ("requires", "provides"),
    "peers": ("peers", "peers"),
}


class EndpointWrapper(Object):
    """Base class for schema-based operator relation libraries.

    Class Attributes:

        * ROLE: Relation role which this class implements.
          Must be set by subclass.

        * INTERFACE: Interface protocol name.
          Must be set by subclass.

        * SCHEMA: A pathlib.Path pointing to the schemas YAML file,
          or schemas data structure. Must be set by subclass.

        * LIMIT: Limit, if any, for relation endpoint connections.

    Attributes:

        * auto_data: Data to be automatically passed to `wrap()` as
          soon as possible for any relation. Must work with any supported
          version which could be negotiated.

        * ignored_fields: Set of field names from remote relation data which
          should be ignored as not part of the schema. The default is the supported
          versions field, and the fields automatically populated by Juju.

    """

    ROLE = None
    INTERFACE = None
    SCHEMA = None
    LIMIT = None

    on = EndpointWrapperEvents()

    def __init__(self, charm: CharmBase, endpoint: str = None):
        """Constructor for EndpointWrapper.

        Args:
            charm: The charm that is instantiating the library.
            endpoint: The name of the relation endpoint to bind to
                (defaults to the INTERFACE).
        """
        if not endpoint:
            endpoint = self.INTERFACE
        super().__init__(charm, f"relation-{endpoint}")
        self.charm = charm
        self.endpoint = endpoint
        self.auto_data = getattr(self, "auto_data", None)
        self.ignored_fields = getattr(
            self,
            "ignored_fields",
            {
                VERSION_KEY,
                "egress-subnets",
                "ingress-address",
                "private-address",
            },
        )

        if self.ROLE not in ROLE_MAP:
            raise errors.InvalidRoleError(self.ROLE)
        self._role, self._remote_role = ROLE_MAP[self.ROLE]

        self._schemas = self._load_schema()

        self._validate_schema()
        self._validate_relation_meta()

        rel_events = charm.on[endpoint]
        self.framework.observe(rel_events.relation_created, self._handle_relation)
        self.framework.observe(rel_events.relation_changed, self._handle_relation)
        self.framework.observe(rel_events.relation_broken, self._handle_relation_broken)
        self.framework.observe(charm.on.leader_elected, self._handle_upgrade_or_leader)
        self.framework.observe(charm.on.upgrade_charm, self._handle_upgrade_or_leader)

    @property
    def app(self):
        return self.charm.app

    @property
    def unit(self):
        return self.charm.unit

    def _load_schema(self):
        if isinstance(self.SCHEMA, dict):
            return self.SCHEMA
        elif isinstance(self.SCHEMA, Path):
            try:
                return yaml.safe_load(self.SCHEMA.read_text())
            except (OSError, yaml.YAMLError) as e:
                raise errors.SchemaParseError() from e
        else:
            raise errors.SchemaError(
                f"SCHEMA type must be Path or dict, not {type(self.SCHEMA)}"
            )

    def _validate_schema(self):
        self._parse_versions(self._schemas.keys())  # verify versions can be parsed
        for version, schema in self._schemas.items():
            try:
                jsonschema.validators.validator_for(schema).check_schema(schema)
            except jsonschema.SchemaError as e:
                raise errors.InvalidSchemaError(version) from e

    def _validate_relation_meta(self):
        """Validate that the relation is setup properly in the metadata."""
        # This should really be done as a build-time hook, if that were possible.
        cls_name = type(self).__name__
        assert (
            self.endpoint in self.charm.meta.relations
        ), f"Relation {self.endpoint} not found"
        rel_meta = self.charm.meta.relations[self.endpoint]
        assert (
            self.ROLE == rel_meta.role.name
        ), f"{cls_name} must be used on a '{self.ROLE}' relation"
        assert (
            rel_meta.interface_name == self.INTERFACE
        ), f"{cls_name} must be used on an '{self.INTERFACE}' relation endpoint"
        if self.LIMIT is not None:
            assert (
                rel_meta.limit == 1
            ), f"{cls_name} must be used on a 'limit: {self.LIMIT}' relation endpoint"

    @property
    def versions(self):
        return set(self._schemas.keys())

    def _parse_versions(self, versions):
        parsed = {}
        for version in versions:
            if isinstance(version, int):
                parsed[version] = version
            elif isinstance(version, str) and version.startswith("v"):
                try:
                    parsed[int(version[1:])] = version
                except ValueError as e:
                    raise errors.InvalidSchemaVersionError(version) from e
            else:
                raise errors.InvalidSchemaVersionError(version)
        return parsed

    @cached_property
    def max_version(self):
        """The maximum version supported by this instance."""
        parsed = self._parse_version(self.versions)
        max_version = max(parsed.keys())
        return parsed[max_version]

    def _get_version(self, relation: Relation):
        """Get the maximum compatible version for a given Relation.

        Can raise:
            * UnversionedRelation
            * RelationParseError
            * IncompatibleVersionsError
        """
        local_versions = self._parse_versions(self.versions)
        remote_versions_raw = relation.data[relation.app].get(VERSION_KEY)
        if not remote_versions_raw:
            raise errors.UnversionedRelation(relation)
        try:
            if not isinstance(remote_versions_raw, str):
                raise TypeError(f"should be str, not {type(remote_versions_raw)}")
            remote_versions = self._parse_versions(yaml.safe_load(remote_versions_raw))
        except (TypeError, yaml.YAMLError) as e:
            raise errors.RelationParseError(
                relation, relation.app, "_supported_versions"
            ) from e
        compatible_versions = local_versions.keys() & remote_versions.keys()
        if not compatible_versions:
            raise errors.IncompatibleVersionsError(relation)
        return local_versions[max(compatible_versions)]

    def _get_entity_schema(
        self, version: Union[int, str], entity: Union[Application, Unit]
    ):
        if entity is self.app:
            return self._schemas[version][self._role].get("app", {})
        elif entity is self.unit:
            return self._schemas[version][self._role].get("unit", {})
        elif isinstance(entity, Application):
            return self._schemas[version][self._remote_role].get("app", {})
        elif isinstance(entity, Unit):
            return self._schemas[version][self._remote_role].get("unit", {})

    @cached_property
    def relations(self):
        """The list of Relation instances associated with this endpoint."""
        return list(self.charm.model.relations[self.endpoint])

    @cache
    def get_status(self, relation):
        if self.is_failed(relation):
            return BlockedStatus(f"Error handling relation: {relation.name}")
        elif not self.is_available(relation):
            if relation.units:
                # If we have remote units but still no version, then there's
                # probably something wrong and we should be blocked.
                return BlockedStatus(f"Missing relation versions: {relation.name}")
            else:
                # Otherwise, we might just not have seen the versions yet.
                return WaitingStatus(f"Waiting on relation: {relation.name}")
        elif not self.is_ready(relation):
            return WaitingStatus(f"Waiting on relation: {relation.name}")
        return ActiveStatus()

    @cache
    def is_available(self, relation: Relation = None):
        """Checks whether the given relation, or any relation if not specified,
        is available.

        A given relation is available if the version negotation has succeeded.
        """
        if relation is None:
            return any(self.is_available(relation) for relation in self.relations)
        try:
            self._get_version(relation)
        except errors.RelationException:
            return False
        else:
            return True

    @cache
    def is_ready(self, relation: Relation = None):
        """Checks whether the given relation, or any relation if not specified,
        is ready.

        A given relation is ready if the remote side has sent valid data.
        """
        if relation is None:
            return any(self.is_ready(relation) for relation in self.relations)
        try:
            data = self.unwrap(relation)
        except errors.RelationException:
            return False
        else:
            return any(
                data[entity]
                for entity in data
                if entity not in (self.app, self.unit)
            )

    @cache
    def is_failed(self, relation: Relation = None):
        """Checks whether the given relation, or any relation if not specified,
        has an error.
        """
        if relation is None:
            return any(self.is_failed(relation) for relation in self.relations)
        try:
            self.unwrap(relation)
        except errors.RelationError as e:
            log.exception(f"Error handling relation: {e}")
            return True
        except errors.UnversionedRelation:
            if relation.units:
                # If we have remote units but still no version, then there's
                # probably something wrong.
                return True
            else:
                return False
        except errors.RelationException:
            return False
        else:
            return False

    def _handle_relation(self, event):
        self._send_versions(event.relation)
        self._send_auto_data(event.relation)
        if self.is_ready(event.relation):
            self.on.ready.emit(event.relation)
        elif self.is_available(event.relation):
            self.on.available.emit(event.relation)
        elif self.is_failed(event.relation):
            self.on.failed.emit(event.relation)

    def _handle_relation_broken(self, event):
        self.on.broken.emit(event.relation)

    def _handle_upgrade_or_leader(self, event):
        for relation in self.relations:
            self._send_versions(relation)
            self._send_auto_data(relation)

    @property
    def _is_leader(self):
        # This is wrapped primarily to aid in testing, so that the
        # MockRemoteRelationMixin can override it.
        return self.unit.is_leader()

    def _send_versions(self, relation):
        if self._is_leader:
            serialized = yaml.safe_dump(list(self.versions))
            relation.data[self.app][VERSION_KEY] = serialized

    def _send_auto_data(self, relation):
        if self.auto_data and self.is_available(relation):
            self.wrap(relation, self.auto_data)

    def unwrap(self, relation: Relation):
        """Deserialize and validate the data from the relation.

        Deserialize and validate all available data from the relation. The returned
        dictionary has the same keys as `relation.data` (i.e., the local and remote
        Applications and Units).

        If the current unit is not the leader, the data for the current Application
        will always be an empty dict.  See: https://bugs.launchpad.net/juju/+bug/1958530

        Can raise:
            * IncompleteRelation
            * IncompatibleVersionsError
            * RelationParseError
            * RelationDataError
        """
        version = self._get_version(relation)
        unwrapped = {}
        for entity, data in relation.data.items():
            if entity is self.app and not self._is_leader:
                unwrapped[entity] = {}
                continue
            entity_schema = self._get_entity_schema(version, entity)
            deserialized = {}
            for key, value in data.items():
                if key in self.ignored_fields:
                    continue
                try:
                    deserialized[key] = yaml.safe_load(value)
                except yaml.YAMLError as e:
                    raise errors.RelationParseError(relation, entity, key) from e
            if deserialized:
                try:
                    jsonschema.validate(instance=deserialized, schema=entity_schema)
                except jsonschema.ValidationError as e:
                    raise errors.RelationDataError(relation, entity) from e
            unwrapped[entity] = deserialized
        return unwrapped

    def wrap(self, relation: Relation, data: Dict[Union[Application, Unit], dict]):
        """Validate and serialize the data and put it into the relation.

        Validates that the local app and / or unit data is valid against the schema,
        and if so, serializes it and returns it.

        Can raise:
            * ModelError (when setting app data and not leader)
            * UnversionedRelation (when relation not available)
            * RelationParseError (when relation not available)
            * IncompatibleVersionsError (when relation not available)
            * RelationDataError (when given data is invalid)

        Example:

                self.wrap(relation, {self.app: {"foo": "bar"}})
        """
        if data.get(self.app) and not self._is_leader:
            raise errors.RelationPermissionError(relation, self.app)
        old_data = self.unwrap(relation)
        version = self._get_version(relation)
        for entity in data:
            if not data[entity]:
                continue
            if entity not in (self.app, self.unit):
                if data[entity] != old_data[entity]:
                    raise errors.RelationPermissionError(relation, entity)
                continue
            entity_schema = self._get_entity_schema(version, entity)
            if not entity_schema:
                raise errors.RelationDataError(relation, entity)
            try:
                jsonschema.validate(instance=data[entity], schema=entity_schema)
            except jsonschema.ValidationError as e:
                raise errors.RelationDataError(relation, entity) from e
            else:
                for field, value in data[entity].items():
                    relation.data[entity][field] = yaml.safe_dump(value)
                for removed_field in set.difference(
                    set(relation.data[entity].keys()),
                    set(data[entity].keys()),
                    self.ignored_fields,
                ):
                    del relation.data[entity][field]

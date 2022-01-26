# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
"""Helper for testing libraries based on sborl."""

from contextlib import contextmanager
from functools import cached_property
from inspect import getmembers
from typing import Dict, Union

from ops.charm import CharmBase, CharmEvents, CharmMeta
from ops.model import Application, Relation, Unit

from .relation import EndpointWrapper


class MockRemoteRelationMixin:
    """A mix-in class to help with unit testing relation endpoints."""

    def __init__(self, harness):
        """Initialize the mock provider / requirer."""

        class MRRMTestEvents(CharmEvents):
            __name__ = self.app_name

        class MRRMTestCharm(CharmBase):
            __name__ = self.app_name
            on = MRRMTestEvents()
            meta = CharmMeta(
                {
                    self.ROLE: {
                        self.INTERFACE: {
                            "role": self.ROLE,
                            "interface": self.INTERFACE,
                            "limit": self.LIMIT,
                        },
                    },
                }
            )
            app = harness.model.get_app(self.app_name)
            unit = harness.model.get_unit(self.unit_name)

        if harness.model.name is None:
            harness._backend.model_name = "test-model"

        super().__init__(MRRMTestCharm(harness.framework))
        self.harness = harness
        self.relation_id = None
        self.num_units = 0
        self._remove_caching()

    def _remove_caching(self):
        # We use the cacheing helpers from functools to save recalculations, but during
        # tests they can interfere with seeing the updated state, so we strip them off.
        is_ew = lambda v: isinstance(v, EndpointWrapper)  # noqa: E731
        is_cp = lambda v: isinstance(v, cached_property)  # noqa: E731
        is_cf = lambda v: hasattr(v, "cache_clear")  # noqa: E731
        classes = [
            EndpointWrapper,
            type(self),
            *[type(instance) for _, instance in getmembers(self.harness.charm, is_ew)],
        ]
        for cls in classes:
            for attr, prop in getmembers(cls, lambda v: is_cp(v) or is_cf(v)):
                if is_cp(prop):
                    setattr(cls, attr, property(prop.func))
                else:
                    setattr(cls, attr, prop.__wrapped__)

    @property
    def app_name(self):
        """The name of the mock app."""
        return f"{self.INTERFACE}-remote"

    @property
    def unit_name(self):
        """The name of the mock unit."""
        return f"{self.app_name}/0"

    @property
    def relation(self):
        """The Relation instance, if created."""
        return self.harness.model.get_relation(self.endpoint, self.relation_id)

    @property
    def _is_leader(self):
        return True

    def relate(self, endpoint: str = None):
        """Create a relation to the charm under test.

        Starts the version negotiation, and returns the Relation instance.
        """
        if not endpoint:
            endpoint = self.endpoint
        self.relation_id = self.harness.add_relation(endpoint, self.app_name)
        self._send_versions(self.relation)
        self.add_unit()
        return self.relation

    @contextmanager
    def _remote_relation_set(self, relation: Relation):
        # Remote relation data normally cannot be written, for obvious reasons.
        # To force it, we have to make the appropriate buckets are marked as
        # writable and also make the testing backend think that we're on the
        # remote side as well.
        for entity, entity_data in relation.data.items():
            if getattr(entity, "app", entity) is self.app:
                entity_data._is_mutable = lambda: True
        backend = self.harness._backend
        app_name, unit_name = backend.app_name, backend.unit_name
        backend.app_name, backend.unit_name = self.app.name, getattr(
            self.unit, "name", None
        )
        try:
            yield
        finally:
            backend.app_name, backend.unit_name = app_name, unit_name
            for entity, entity_data in relation.data.items():
                if getattr(entity, "app", entity) is self.app:
                    entity_data._is_mutable = lambda: False

    def _send_versions(self, relation: Relation):
        with self._remote_relation_set(relation):
            super()._send_versions(relation)
        # Updating the relation data directly doesn't trigger hooks, so we have
        # to call update_relation_data explicitly to trigger them.
        self.harness.update_relation_data(
            self.relation_id,
            self.app_name,
            dict(relation.data[relation.app]),
        )

    def add_unit(self):
        unit_name = f"{self.app_name}/{self.num_units}"
        self.harness.add_relation_unit(self.relation_id, unit_name)
        self.num_units += 1

    def _get_version(self, relation: Relation):
        # Normally, relation.app and relation.unit are the remote entities, but
        # we're operating *as* the remote, so we need to fake that perspective
        # for this call by patching the relation's app.
        app = relation.app
        relation.app = self.harness.charm.app
        try:
            return super()._get_version(relation)
        finally:
            relation.app = app

    def wrap(self, relation: Relation, data: Dict[Union[Application, Unit], dict]):
        with self._remote_relation_set(relation):
            super().wrap(relation, data)
        # Updating the relation data directly doesn't trigger hooks, so we have
        # to call update_relation_data explicitly to trigger them.
        for entity in (self.charm.app, self.charm.unit):
            if entity in data:
                self.harness.update_relation_data(
                    relation.id,
                    self.charm.app.name,
                    dict(relation.data[entity]),
                )

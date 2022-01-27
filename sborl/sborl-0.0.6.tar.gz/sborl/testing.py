# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
"""Helper for testing libraries based on sborl."""

from contextlib import contextmanager
from functools import cached_property
from inspect import getmembers
from typing import Dict, Union
from unittest.mock import patch

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
    def remote_context(self, relation: Relation):
        """Temporarily change the context to the remote side of the relation.

        The test runs within the context of the local charm under test.  This
        means that the relation data on the remote side cannot be written, the
        app and units references are from the local charm's perspective, etc.
        This temporarily patches things to behave as if we were running on the
        remote charm instead.
        """
        with patch.multiple(
            self.harness._backend,
            app_name=self.app.name,
            unit_name=getattr(self.unit, "name", None),
            is_leader=lambda: True,
        ):
            with patch.multiple(
                relation, app=self.harness.charm.app, units={self.harness.charm.unit}
            ):
                with patch.object(self.unit, "_is_our_unit", True):
                    yield

    def _send_versions(self, relation: Relation):
        with self.remote_context(relation):
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
        with self.remote_context(relation):
            return super()._get_version(relation)

    def is_available(self, relation: Relation = None):
        if relation is None:
            return any(self.is_available(relation) for relation in self.relations)
        with self.remote_context(relation):
            return super().is_available(relation)

    def is_ready(self, relation: Relation = None):
        if relation is None:
            return any(self.is_ready(relation) for relation in self.relations)
        with self.remote_context(relation):
            return super().is_ready(relation)

    def is_failed(self, relation: Relation = None):
        if relation is None:
            return any(self.is_failed(relation) for relation in self.relations)
        with self.remote_context(relation):
            return super().is_failed(relation)

    def wrap(self, relation: Relation, data: Dict[Union[Application, Unit], dict]):
        with self.remote_context(relation):
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

    def unwrap(self, relation: Relation):
        with self.remote_context(relation):
            return super().unwrap(relation)

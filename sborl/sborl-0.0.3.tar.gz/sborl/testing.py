# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
from functools import cached_property
from inspect import getmembers
from typing import Dict, Union

from ops.charm import CharmBase, CharmEvents, CharmMeta
from ops.model import Application, Relation, Unit

from .relation import EndpointWrapper


class MockRemoteRelationMixin:
    """A mix-in class to help with unit testing relation endpoints."""

    def __init__(self, harness):
        class MRRMTestEvents(CharmEvents):
            __name__ = self.app_name

        class MRRMTestCharm(CharmBase):
            __name__ = self.app_name
            on = MRRMTestEvents()
            meta = CharmMeta(
                {
                    "provides": {
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

    def _clear_caches(self):
        icp = lambda v: isinstance(v, cached_property)  # noqa: E731
        icf = lambda v: hasattr(v, "cache_clear")  # noqa: E731
        isr = lambda v: isinstance(v, EndpointWrapper)  # noqa: E731
        for attr, prop in getmembers(type(self), lambda v: icp(v) or icf(v)):
            if icp(prop):
                try:
                    self.__delattr__(attr)
                except AttributeError:
                    pass  # happens if not populated
            else:
                getattr(getattr(self, attr), "cache_clear")()
        for attr, instance in getmembers(self.harness.charm, isr):
            for attr, prop in getmembers(type(instance), icp):
                try:
                    instance.__delattr__(attr)
                except AttributeError:
                    pass  # happens if not populated

    @property
    def app_name(self):
        return f"{self.INTERFACE}-remote"

    @property
    def unit_name(self):
        return f"{self.app_name}/0"

    @property
    def relation(self):
        return self.harness.model.get_relation(self.endpoint, self.relation_id)

    @property
    def _is_leader(self):
        return True

    def relate(self, endpoint: str = None):
        if not endpoint:
            endpoint = self.endpoint
        self.relation_id = self.harness.add_relation(endpoint, self.app_name)
        self._send_versions(self.relation)
        self._clear_caches()
        self.add_unit()
        return self.relation

    def _ensure_writable(self, relation: Relation):
        # Force our remote entities to be writable, since they normally aren't.
        for entity, entity_data in relation.data.items():
            if entity.name.startswith(self.app_name):
                entity_data._is_mutable = lambda: True

    def _send_versions(self, relation: Relation):
        self._ensure_writable(relation)
        super()._send_versions(relation)
        self._clear_caches()
        # Updating the relation data directly doesn't trigger hooks, so we have
        # to call update_relation_data explicitly to trigger them.
        self.harness.update_relation_data(
            self.relation_id,
            self.app_name,
            dict(relation.data[relation.app]),
        )
        self._clear_caches()

    def add_unit(self):
        unit_name = f"{self.app_name}/{self.num_units}"
        self.harness.add_relation_unit(self.relation_id, unit_name)
        self.num_units += 1
        self._clear_caches()

    def wrap(self, relation: Relation, data: Dict[Union[Application, Unit], dict]):
        self._ensure_writable(relation)
        super().wrap(relation, data)
        self._clear_caches()
        # Updating the relation data directly doesn't trigger hooks, so we have
        # to call update_relation_data explicitly to trigger them.
        for entity in (self.charm.app, self.charm.unit):
            if entity in data:
                self.harness.update_relation_data(
                    relation.id,
                    self.charm.app.name,
                    dict(relation.data[entity]),
                )
        self._clear_caches()

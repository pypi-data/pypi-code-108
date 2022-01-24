# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
from ops.charm import RelationEvent
from ops.framework import EventSource, ObjectEvents


class RelationAvailableEvent(RelationEvent):
    """Event triggered when a relation is ready for requests."""


class RelationFailedEvent(RelationEvent):
    """Event triggered when something went wrong with a relation."""


class RelationReadyEvent(RelationEvent):
    """Event triggered when a remote relation has the expected data."""


class RelationBrokenEvent(RelationEvent):
    """Event triggered when a remote relation has the expected data."""


class EndpointWrapperEvents(ObjectEvents):
    available = EventSource(RelationAvailableEvent)
    ready = EventSource(RelationReadyEvent)
    failed = EventSource(RelationFailedEvent)
    broken = EventSource(RelationBrokenEvent)

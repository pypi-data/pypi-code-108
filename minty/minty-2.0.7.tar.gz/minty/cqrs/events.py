# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

from .. import Base
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Union
from uuid import UUID, uuid4


class EntityChange(TypedDict):
    key: str
    old_value: Any
    new_value: Any


def event(name: str, extra_fields: Optional[List[str]] = None):
    """Event decorator to capture entity changes and publish events to the event_service.

    :param name: Name of event to publish
    :type name: str
    :param extra_fields: extra fields to capture publish with event, defaults to None
    :type extra_fields: List, optional
    :return: wrapped_entity
    :rtype: func
    """

    def register_event(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            wrapped_entity = args[0]

            if extra_fields is not None:
                wrapped_entity.capture_field_values(fields=extra_fields)

            wrapped_entity.event_service.log_event(
                entity_type=wrapped_entity.__class__.__name__,
                entity_id=wrapped_entity.entity_id,
                event_name=name,
                changes=wrapped_entity.change_log,
                entity_data=wrapped_entity.entity_data,
            )

            wrapped_entity.clear_entity_data()
            wrapped_entity.clear_change_log()

        return wrapper

    return register_event


@dataclass
class Event:
    uuid: UUID
    created_date: datetime

    correlation_id: UUID
    domain: str
    context: str
    user_uuid: UUID

    entity_type: str
    # Moving to "fully UUID" requires some careful versioning and planning, as
    # dependent code may need to be adjusted.
    entity_id: Union[str, UUID]

    event_name: str
    changes: List[EntityChange]
    entity_data: dict

    def format_changes(self) -> dict:
        """Format changes into more workable format.

        :return: dict with changes
        :rtype: dict
        """
        changes = {}
        for change in self.changes:
            changes[change["key"]] = change["new_value"]
        return changes

    def previous_value(self, key):
        """Returns the "old value" from the changelog for the given attribute

        :return: value containing the old value
        :rtype: str
        """
        values = [
            change["old_value"]
            for change in self.changes
            if change["key"] == key
        ]
        return values[0]

    def new_value(self, key):
        """Returns the "new value" from the changelog for the given attribute

        :return: value containing the old value
        :rtype: str
        """
        values = [
            change["new_value"]
            for change in self.changes
            if change["key"] == key
        ]
        return values[0]


class EventService(Base):
    __slots__ = [
        "event_list",
        "correlation_id",
        "domain",
        "context",
        "user_uuid",
    ]

    def __init__(
        self, correlation_id: UUID, domain: str, context: str, user_uuid: UUID
    ):
        self.correlation_id = correlation_id
        self.domain = domain
        self.context = context
        self.user_uuid = user_uuid
        self.event_list: List[Event] = []

    def log_event(
        self,
        entity_type: str,
        entity_id: Union[str, UUID],
        event_name: str,
        changes: List[EntityChange],
        entity_data: Dict[str, Any],
    ):
        """Register a new event with the event serivce

        This will create a new event using the `EventFactory` configured on
        initialization and append it to the `event_list`.

        :param event_name: Name of the event that happened
        :type event_name: str
        :param parameters: Dictionary containing the event parameters (like
            entity state pre-event and post-event)
        :type parameters: dict
        """

        uuid = uuid4()
        created_date = datetime.utcnow()

        event = Event(
            uuid=uuid,
            created_date=created_date,
            correlation_id=self.correlation_id,
            domain=self.domain,
            context=self.context,
            user_uuid=self.user_uuid,
            entity_type=entity_type,
            entity_id=entity_id,
            event_name=event_name,
            changes=changes,
            entity_data=entity_data,
        )

        self.logger.info(f"Created Event: {event}")

        self.event_list.append(event)

    def get_events_by_type(self, entity_type: str) -> List[Event]:
        """Get all events for given `entity_type`.

        :param entity_type: entity_type
        :type entity_type: str
        :return: list of events
        :rtype: typing.List[Event]
        """
        events = [
            ev for ev in self.event_list if ev.entity_type == entity_type
        ]
        return events

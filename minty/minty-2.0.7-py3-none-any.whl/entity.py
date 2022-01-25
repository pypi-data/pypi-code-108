# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import functools
from .cqrs import EventService
from .cqrs.events import EntityChange
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from minty import exceptions
from minty.object import Field, IntrospectableObject
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    TypeVar,
)
from uuid import UUID


class EntityBase(ABC):
    _event_service: Optional[EventService]
    _changes: List[EntityChange]
    _entity_data: Dict[str, Any]

    @property
    @abstractmethod
    def entity_id(self):
        raise NotImplementedError

    @property
    def event_service(self):
        return self._event_service

    @event_service.setter
    def event_service(self, event_service):
        super().__setattr__("_event_service", event_service)

    @property
    def change_log(self):
        try:
            self._changes
        except AttributeError:
            self.clear_change_log()
        return self._changes

    def clear_change_log(self):
        super().__setattr__("_changes", [])

    @property
    def entity_data(self):
        try:
            self._entity_data
        except AttributeError:
            self.clear_entity_data()
        return self._entity_data

    def clear_entity_data(self):
        super().__setattr__("_entity_data", {})

    def __setattr__(self, attr, value):
        try:
            old_value = self.__getattribute__(attr)
            change: EntityChange = {
                "key": attr,
                "old_value": _reflect(old_value),
                "new_value": _reflect(value),
            }

            self.change_log.append(change)
        except AttributeError:
            pass
        super().__setattr__(attr, value)

    def capture_field_values(self, fields: List):
        for field in fields:
            value = self.__getattribute__(field)
            self.entity_data[field] = _reflect(value)


def _reflect(value):
    """Reflect on attribute type and return JSON parse-able type.

    :param attr: attribute
    :return: converted object to correct type
    :rtype: str, int or None
    """
    if (
        (value is None)
        or isinstance(value, bool)
        or isinstance(value, int)
        or isinstance(value, float)
    ):
        return value

    if isinstance(value, EntityBase):
        return {
            "type": value.__class__.__name__,
            "entity_id": str(value.entity_id),
        }

    if isinstance(value, Entity):
        return {k: _reflect(v) for k, v in value.entity_dict().items()}
    elif isinstance(value, IntrospectableObject):
        return {k: _reflect(v) for k, v in value.dict().items()}

    if isinstance(value, List):
        return [_reflect(i) for i in value]

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {k: _reflect(v) for k, v in value.items()}

    if isinstance(value, datetime):
        return value.isoformat()

    return str(value)


class ValueObject(IntrospectableObject):
    pass


def _event_decorator(
    event_name: str,
    extra_fields: Optional[List[str]] = None,
):
    def _build_decorator(wrapped: Callable[..., Any]):
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs):
            instance = args[0]

            # Clear the changelog when we are not a class method
            if isinstance(instance, Entity):
                instance.entity_changelog = []

            rv = wrapped(*args, **kwargs)

            changelog: List[EntityChange]

            if isinstance(instance, Entity):
                # When used with a regular method, use the regular
                changelog = instance.entity_changelog
                wrapped_entity = instance
            else:
                if not isinstance(rv, Entity):
                    raise exceptions.ConfigurationConflict(
                        "Return value of class method is not an entity."
                    )

                # When called as a class method (to create a new entity)
                # everything is considered a change
                dict_of_changes = rv.entity_dict()

                changelog = []
                for field in dict_of_changes.keys():
                    value = dict_of_changes[field]

                    changelog.append(
                        {
                            "key": field,
                            "old_value": None,
                            "new_value": _reflect(value),
                        }
                    )

                wrapped_entity = rv

            if extra_fields is not None:
                wrapped_entity.capture_field_values(fields=extra_fields)

            if wrapped_entity._event_service:
                wrapped_entity._event_service.log_event(
                    entity_type=wrapped_entity.__class__.__name__,
                    entity_id=str(wrapped_entity.entity_id),
                    event_name=event_name,
                    changes=changelog,
                    entity_data=wrapped_entity.entity_data,
                )
            else:
                raise exceptions.ConfigurationConflict(
                    "Wrapped entity does not have _event_service attribute. "
                    "Possible cause: repository did not inject it."
                )

            return wrapped_entity

        return wrapper

    return _build_decorator


class Entity(IntrospectableObject):
    """
    Pydantic based Entity object

    Entity object based on pydantic and the "new way" of creating entities in
    our minty platform. It has the same functionality as the EntityBase object,
    but does not depend on it. Migrationpaths are unsure.
    """

    entity_type: str = Field(
        ...,
        title="Type of Entity",
        description="Unique name of object within the system",
    )
    entity_id: UUID = Field(
        None,
        title="Identifier of Entity",
        description="Globally unique identifier of this entity",
    )
    entity_meta_summary: str = Field(
        None,
        title="Summary of the subject",
        description="Human readable summary of the content of the object",
    )

    entity_relationships: list = Field(
        [],
        title="Names of attributes containing relationships",
        description="Identifies which attributes relate to other entities",
    )

    entity_meta__fields: list = Field(
        ["entity_meta_summary"],
        title="Names of attributes containing meta fields",
        description="Identifies which attributes contain fields for meta info",
    )

    entity_id__fields: list = Field(
        [],
        title="Names of attributes containing meta fields",
        description="Identifies which attributes are moved to entity_id",
    )

    entity_changelog: list = []
    entity_data: dict = {}

    _event_service: Optional[EventService] = None

    def __init__(self, **kwargs):
        """Initialized an Entity object

        Initialized an entity object and calls super().__init__ on the pydantic
        based IntrospectableObject model. Allows the setting of _event_service
        for the event_service engine
        """

        super().__init__(**kwargs)
        if "_event_service" in kwargs:
            object.__setattr__(
                self, "_event_service", kwargs["_event_service"]
            )

    def entity_dict(self):
        """Generates a python dict containing the values of this entity

        Just as the pydantic.dict() method, it returns a dict containing the
        key/values of the attributes of this object.

        The difference is that it will not return private attributes
        (starting with a _) and attributes starting with "entity_". It walks
        recursively over all the related objects.
        """
        rv = {}
        for k, v in dict(self).items():
            if isinstance(v, Entity):
                rv[k] = v.entity_dict()
            elif isinstance(v, IntrospectableObject):
                rv[k] = v.dict()
            else:
                if k.startswith("_") or k.startswith("entity_"):
                    continue

                rv[k] = v

        return rv

    def __setattr__(self, attr, value):
        old_value = self.__getattribute__(attr)

        rv = super().__setattr__(attr, value)

        if not (attr.startswith("_") or attr.startswith("entity_")):
            change = {
                "key": attr,
                "old_value": _reflect(old_value),
                "new_value": _reflect(value),
            }

            self.entity_changelog.append(change)

        return rv

    def capture_field_values(self, fields: List):
        for field in fields:
            value = self.__getattribute__(field)
            self.entity_data[field] = _reflect(value)

    @staticmethod
    def event(name: str, extra_fields: Optional[List[str]] = None):
        """
        Decorator to defined events on entities.

        Captures entity changes and saves them to the event_service as events.

        If specified, the contents of fields named in `extra_fields` are
        also included in the event.

        When applying this to a class method, the `@classmethod` decorator
        should be the topmost one:

        ```
            @classmethod
            @Entity.event("EventNamed")
            def event_name(cls):
                pass
        ```
        """
        return _event_decorator(event_name=name, extra_fields=extra_fields)


E = TypeVar("E", bound=Entity)


class EntityCollection(Generic[E]):
    """Multiple entities."""

    total_results: Optional[int]
    entities: Iterable[E]

    def __init__(
        self, entities: Iterable[E], total_results: Optional[int] = None
    ):
        self.entities = entities
        self.total_results = total_results

    def __iter__(self) -> Iterator[E]:
        return iter(self.entities)

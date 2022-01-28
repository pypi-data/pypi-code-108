import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.event_base_schema import EventBaseSchema
from ..models.stage_entry import StageEntry
from ..models.stage_entry_updated_review_record_event_event_type import (
    StageEntryUpdatedReviewRecordEventEventType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="StageEntryUpdatedReviewRecordEvent")


@attr.s(auto_attribs=True, repr=False)
class StageEntryUpdatedReviewRecordEvent:
    """  """

    _entry: Union[Unset, StageEntry] = UNSET
    _event_type: Union[Unset, StageEntryUpdatedReviewRecordEventEventType] = UNSET
    _updates: Union[Unset, List[str]] = UNSET
    _created_at: Union[Unset, datetime.datetime] = UNSET
    _deprecated: Union[Unset, bool] = UNSET
    _excluded_properties: Union[Unset, List[str]] = UNSET
    _id: Union[Unset, str] = UNSET
    _schema: Union[Unset, None, EventBaseSchema] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entry={}".format(repr(self._entry)))
        fields.append("event_type={}".format(repr(self._event_type)))
        fields.append("updates={}".format(repr(self._updates)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("deprecated={}".format(repr(self._deprecated)))
        fields.append("excluded_properties={}".format(repr(self._excluded_properties)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "StageEntryUpdatedReviewRecordEvent({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entry: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._entry, Unset):
            entry = self._entry.to_dict()

        event_type: Union[Unset, int] = UNSET
        if not isinstance(self._event_type, Unset):
            event_type = self._event_type.value

        updates: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._updates, Unset):
            updates = self._updates

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        deprecated = self._deprecated
        excluded_properties: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._excluded_properties, Unset):
            excluded_properties = self._excluded_properties

        id = self._id
        schema: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._schema, Unset):
            schema = self._schema.to_dict() if self._schema else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entry is not UNSET:
            field_dict["entry"] = entry
        if event_type is not UNSET:
            field_dict["eventType"] = event_type
        if updates is not UNSET:
            field_dict["updates"] = updates
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if deprecated is not UNSET:
            field_dict["deprecated"] = deprecated
        if excluded_properties is not UNSET:
            field_dict["excludedProperties"] = excluded_properties
        if id is not UNSET:
            field_dict["id"] = id
        if schema is not UNSET:
            field_dict["schema"] = schema

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entry() -> Union[Unset, StageEntry]:
            entry: Union[Unset, StageEntry] = UNSET
            _entry = d.pop("entry")
            if not isinstance(_entry, Unset):
                entry = StageEntry.from_dict(_entry)

            return entry

        entry = get_entry() if "entry" in d else cast(Union[Unset, StageEntry], UNSET)

        def get_event_type() -> Union[Unset, StageEntryUpdatedReviewRecordEventEventType]:
            event_type = None
            _event_type = d.pop("eventType")
            if _event_type is not None and _event_type is not UNSET:
                try:
                    event_type = StageEntryUpdatedReviewRecordEventEventType(_event_type)
                except ValueError:
                    event_type = StageEntryUpdatedReviewRecordEventEventType.of_unknown(_event_type)

            return event_type

        event_type = (
            get_event_type()
            if "eventType" in d
            else cast(Union[Unset, StageEntryUpdatedReviewRecordEventEventType], UNSET)
        )

        def get_updates() -> Union[Unset, List[str]]:
            updates = cast(List[str], d.pop("updates"))

            return updates

        updates = get_updates() if "updates" in d else cast(Union[Unset, List[str]], UNSET)

        def get_created_at() -> Union[Unset, datetime.datetime]:
            created_at: Union[Unset, datetime.datetime] = UNSET
            _created_at = d.pop("createdAt")
            if _created_at is not None and not isinstance(_created_at, Unset):
                created_at = isoparse(cast(str, _created_at))

            return created_at

        created_at = get_created_at() if "createdAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_deprecated() -> Union[Unset, bool]:
            deprecated = d.pop("deprecated")
            return deprecated

        deprecated = get_deprecated() if "deprecated" in d else cast(Union[Unset, bool], UNSET)

        def get_excluded_properties() -> Union[Unset, List[str]]:
            excluded_properties = cast(List[str], d.pop("excludedProperties"))

            return excluded_properties

        excluded_properties = (
            get_excluded_properties() if "excludedProperties" in d else cast(Union[Unset, List[str]], UNSET)
        )

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_schema() -> Union[Unset, None, EventBaseSchema]:
            schema = None
            _schema = d.pop("schema")
            if _schema is not None and not isinstance(_schema, Unset):
                schema = EventBaseSchema.from_dict(_schema)

            return schema

        schema = get_schema() if "schema" in d else cast(Union[Unset, None, EventBaseSchema], UNSET)

        stage_entry_updated_review_record_event = cls(
            entry=entry,
            event_type=event_type,
            updates=updates,
            created_at=created_at,
            deprecated=deprecated,
            excluded_properties=excluded_properties,
            id=id,
            schema=schema,
        )

        stage_entry_updated_review_record_event.additional_properties = d
        return stage_entry_updated_review_record_event

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def entry(self) -> StageEntry:
        """ A notebook entry used for execution of one or more stage runs in a legacy workflow. """
        if isinstance(self._entry, Unset):
            raise NotPresentError(self, "entry")
        return self._entry

    @entry.setter
    def entry(self, value: StageEntry) -> None:
        self._entry = value

    @entry.deleter
    def entry(self) -> None:
        self._entry = UNSET

    @property
    def event_type(self) -> StageEntryUpdatedReviewRecordEventEventType:
        if isinstance(self._event_type, Unset):
            raise NotPresentError(self, "event_type")
        return self._event_type

    @event_type.setter
    def event_type(self, value: StageEntryUpdatedReviewRecordEventEventType) -> None:
        self._event_type = value

    @event_type.deleter
    def event_type(self) -> None:
        self._event_type = UNSET

    @property
    def updates(self) -> List[str]:
        """These properties have been updated, causing this message"""
        if isinstance(self._updates, Unset):
            raise NotPresentError(self, "updates")
        return self._updates

    @updates.setter
    def updates(self, value: List[str]) -> None:
        self._updates = value

    @updates.deleter
    def updates(self) -> None:
        self._updates = UNSET

    @property
    def created_at(self) -> datetime.datetime:
        if isinstance(self._created_at, Unset):
            raise NotPresentError(self, "created_at")
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        self._created_at = value

    @created_at.deleter
    def created_at(self) -> None:
        self._created_at = UNSET

    @property
    def deprecated(self) -> bool:
        if isinstance(self._deprecated, Unset):
            raise NotPresentError(self, "deprecated")
        return self._deprecated

    @deprecated.setter
    def deprecated(self, value: bool) -> None:
        self._deprecated = value

    @deprecated.deleter
    def deprecated(self) -> None:
        self._deprecated = UNSET

    @property
    def excluded_properties(self) -> List[str]:
        """These properties have been dropped from the payload due to size."""
        if isinstance(self._excluded_properties, Unset):
            raise NotPresentError(self, "excluded_properties")
        return self._excluded_properties

    @excluded_properties.setter
    def excluded_properties(self, value: List[str]) -> None:
        self._excluded_properties = value

    @excluded_properties.deleter
    def excluded_properties(self) -> None:
        self._excluded_properties = UNSET

    @property
    def id(self) -> str:
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def schema(self) -> Optional[EventBaseSchema]:
        if isinstance(self._schema, Unset):
            raise NotPresentError(self, "schema")
        return self._schema

    @schema.setter
    def schema(self, value: Optional[EventBaseSchema]) -> None:
        self._schema = value

    @schema.deleter
    def schema(self) -> None:
        self._schema = UNSET

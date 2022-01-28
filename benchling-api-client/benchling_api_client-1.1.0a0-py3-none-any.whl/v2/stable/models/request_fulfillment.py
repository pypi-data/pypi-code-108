import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.sample_group import SampleGroup
from ..models.sample_group_status import SampleGroupStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestFulfillment")


@attr.s(auto_attribs=True, repr=False)
class RequestFulfillment:
    """A request fulfillment represents work that is done which changes the status of a request or a sample group within that request.
    Fulfillments are created when state changes between IN_PROGRESS, COMPLETED, or FAILED statuses. Fulfillments do not capture a PENDING state because all requests or request sample groups are considered PENDING until the first corresponding fulfillment is created.
    """

    _created_at: Union[Unset, datetime.datetime] = UNSET
    _entry_id: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _request_id: Union[Unset, str] = UNSET
    _sample_group: Union[Unset, None, SampleGroup] = UNSET
    _status: Union[Unset, SampleGroupStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("entry_id={}".format(repr(self._entry_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("request_id={}".format(repr(self._request_id)))
        fields.append("sample_group={}".format(repr(self._sample_group)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestFulfillment({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        entry_id = self._entry_id
        id = self._id
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        request_id = self._request_id
        sample_group: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._sample_group, Unset):
            sample_group = self._sample_group.to_dict() if self._sample_group else None

        status: Union[Unset, int] = UNSET
        if not isinstance(self._status, Unset):
            status = self._status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if entry_id is not UNSET:
            field_dict["entryId"] = entry_id
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if request_id is not UNSET:
            field_dict["requestId"] = request_id
        if sample_group is not UNSET:
            field_dict["sampleGroup"] = sample_group
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_created_at() -> Union[Unset, datetime.datetime]:
            created_at: Union[Unset, datetime.datetime] = UNSET
            _created_at = d.pop("createdAt")
            if _created_at is not None and not isinstance(_created_at, Unset):
                created_at = isoparse(cast(str, _created_at))

            return created_at

        created_at = get_created_at() if "createdAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_entry_id() -> Union[Unset, str]:
            entry_id = d.pop("entryId")
            return entry_id

        entry_id = get_entry_id() if "entryId" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_modified_at() -> Union[Unset, datetime.datetime]:
            modified_at: Union[Unset, datetime.datetime] = UNSET
            _modified_at = d.pop("modifiedAt")
            if _modified_at is not None and not isinstance(_modified_at, Unset):
                modified_at = isoparse(cast(str, _modified_at))

            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_request_id() -> Union[Unset, str]:
            request_id = d.pop("requestId")
            return request_id

        request_id = get_request_id() if "requestId" in d else cast(Union[Unset, str], UNSET)

        def get_sample_group() -> Union[Unset, None, SampleGroup]:
            sample_group = None
            _sample_group = d.pop("sampleGroup")
            if _sample_group is not None and not isinstance(_sample_group, Unset):
                sample_group = SampleGroup.from_dict(_sample_group)

            return sample_group

        sample_group = (
            get_sample_group() if "sampleGroup" in d else cast(Union[Unset, None, SampleGroup], UNSET)
        )

        def get_status() -> Union[Unset, SampleGroupStatus]:
            status = None
            _status = d.pop("status")
            if _status is not None and _status is not UNSET:
                try:
                    status = SampleGroupStatus(_status)
                except ValueError:
                    status = SampleGroupStatus.of_unknown(_status)

            return status

        status = get_status() if "status" in d else cast(Union[Unset, SampleGroupStatus], UNSET)

        request_fulfillment = cls(
            created_at=created_at,
            entry_id=entry_id,
            id=id,
            modified_at=modified_at,
            request_id=request_id,
            sample_group=sample_group,
            status=status,
        )

        request_fulfillment.additional_properties = d
        return request_fulfillment

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
    def created_at(self) -> datetime.datetime:
        """ Date and time the fulfillment was created """
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
    def entry_id(self) -> str:
        """ ID of the entry this fulfillment was executed in, if any """
        if isinstance(self._entry_id, Unset):
            raise NotPresentError(self, "entry_id")
        return self._entry_id

    @entry_id.setter
    def entry_id(self, value: str) -> None:
        self._entry_id = value

    @entry_id.deleter
    def entry_id(self) -> None:
        self._entry_id = UNSET

    @property
    def id(self) -> str:
        """ ID of the request fulfillment """
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
    def modified_at(self) -> datetime.datetime:
        """ DateTime the Request Fulfillment was last modified """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: datetime.datetime) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

    @property
    def request_id(self) -> str:
        """ ID of the request this fulfillment fulfills """
        if isinstance(self._request_id, Unset):
            raise NotPresentError(self, "request_id")
        return self._request_id

    @request_id.setter
    def request_id(self, value: str) -> None:
        self._request_id = value

    @request_id.deleter
    def request_id(self) -> None:
        self._request_id = UNSET

    @property
    def sample_group(self) -> Optional[SampleGroup]:
        """ Represents a sample group that is an input to a request. A sample group is a set of samples upon which work in the request should be done. """
        if isinstance(self._sample_group, Unset):
            raise NotPresentError(self, "sample_group")
        return self._sample_group

    @sample_group.setter
    def sample_group(self, value: Optional[SampleGroup]) -> None:
        self._sample_group = value

    @sample_group.deleter
    def sample_group(self) -> None:
        self._sample_group = UNSET

    @property
    def status(self) -> SampleGroupStatus:
        """ Status of a sample group """
        if isinstance(self._status, Unset):
            raise NotPresentError(self, "status")
        return self._status

    @status.setter
    def status(self, value: SampleGroupStatus) -> None:
        self._status = value

    @status.deleter
    def status(self) -> None:
        self._status = UNSET

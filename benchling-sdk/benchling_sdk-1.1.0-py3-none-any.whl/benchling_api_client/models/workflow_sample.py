import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowSample")


@attr.s(auto_attribs=True, repr=False)
class WorkflowSample:
    """  """

    _batch_id: Union[Unset, str] = UNSET
    _container_ids: Union[Unset, List[str]] = UNSET
    _created_at: Union[Unset, datetime.datetime] = UNSET
    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("batch_id={}".format(repr(self._batch_id)))
        fields.append("container_ids={}".format(repr(self._container_ids)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowSample({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batch_id = self._batch_id
        container_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._container_ids, Unset):
            container_ids = self._container_ids

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        id = self._id
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if batch_id is not UNSET:
            field_dict["batchId"] = batch_id
        if container_ids is not UNSET:
            field_dict["containerIds"] = container_ids
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_batch_id() -> Union[Unset, str]:
            batch_id = d.pop("batchId")
            return batch_id

        batch_id = get_batch_id() if "batchId" in d else cast(Union[Unset, str], UNSET)

        def get_container_ids() -> Union[Unset, List[str]]:
            container_ids = cast(List[str], d.pop("containerIds"))

            return container_ids

        container_ids = get_container_ids() if "containerIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_created_at() -> Union[Unset, datetime.datetime]:
            created_at: Union[Unset, datetime.datetime] = UNSET
            _created_at = d.pop("createdAt")
            if _created_at is not None and not isinstance(_created_at, Unset):
                created_at = isoparse(cast(str, _created_at))

            return created_at

        created_at = get_created_at() if "createdAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        workflow_sample = cls(
            batch_id=batch_id,
            container_ids=container_ids,
            created_at=created_at,
            id=id,
            name=name,
        )

        workflow_sample.additional_properties = d
        return workflow_sample

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
    def batch_id(self) -> str:
        """ ID of the batch """
        if isinstance(self._batch_id, Unset):
            raise NotPresentError(self, "batch_id")
        return self._batch_id

    @batch_id.setter
    def batch_id(self, value: str) -> None:
        self._batch_id = value

    @batch_id.deleter
    def batch_id(self) -> None:
        self._batch_id = UNSET

    @property
    def container_ids(self) -> List[str]:
        """ Array of IDs of containers """
        if isinstance(self._container_ids, Unset):
            raise NotPresentError(self, "container_ids")
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value

    @container_ids.deleter
    def container_ids(self) -> None:
        self._container_ids = UNSET

    @property
    def created_at(self) -> datetime.datetime:
        """ DateTime at which the the sample was created """
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
    def id(self) -> str:
        """ ID of the sample """
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
    def name(self) -> str:
        """ Name of the sample """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

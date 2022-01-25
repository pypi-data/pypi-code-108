from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestSampleWithBatch")


@attr.s(auto_attribs=True, repr=False)
class RequestSampleWithBatch:
    """  """

    _batch_id: str
    _container_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("batch_id={}".format(repr(self._batch_id)))
        fields.append("container_id={}".format(repr(self._container_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestSampleWithBatch({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batch_id = self._batch_id
        container_id = self._container_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "batchId": batch_id,
            }
        )
        if container_id is not UNSET:
            field_dict["containerId"] = container_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_batch_id() -> str:
            batch_id = d.pop("batchId")
            return batch_id

        batch_id = get_batch_id() if "batchId" in d else cast(str, UNSET)

        def get_container_id() -> Union[Unset, str]:
            container_id = d.pop("containerId")
            return container_id

        container_id = get_container_id() if "containerId" in d else cast(Union[Unset, str], UNSET)

        request_sample_with_batch = cls(
            batch_id=batch_id,
            container_id=container_id,
        )

        request_sample_with_batch.additional_properties = d
        return request_sample_with_batch

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
        if isinstance(self._batch_id, Unset):
            raise NotPresentError(self, "batch_id")
        return self._batch_id

    @batch_id.setter
    def batch_id(self, value: str) -> None:
        self._batch_id = value

    @property
    def container_id(self) -> str:
        if isinstance(self._container_id, Unset):
            raise NotPresentError(self, "container_id")
        return self._container_id

    @container_id.setter
    def container_id(self, value: str) -> None:
        self._container_id = value

    @container_id.deleter
    def container_id(self) -> None:
        self._container_id = UNSET

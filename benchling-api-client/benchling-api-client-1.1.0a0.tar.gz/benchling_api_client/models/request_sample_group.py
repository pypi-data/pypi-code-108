from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.request_sample_group_samples import RequestSampleGroupSamples
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestSampleGroup")


@attr.s(auto_attribs=True, repr=False)
class RequestSampleGroup:
    """  """

    _id: Union[Unset, str] = UNSET
    _samples: Union[Unset, RequestSampleGroupSamples] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("samples={}".format(repr(self._samples)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestSampleGroup({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        samples: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._samples, Unset):
            samples = self._samples.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if samples is not UNSET:
            field_dict["samples"] = samples

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_samples() -> Union[Unset, RequestSampleGroupSamples]:
            samples: Union[Unset, RequestSampleGroupSamples] = UNSET
            _samples = d.pop("samples")
            if not isinstance(_samples, Unset):
                samples = RequestSampleGroupSamples.from_dict(_samples)

            return samples

        samples = get_samples() if "samples" in d else cast(Union[Unset, RequestSampleGroupSamples], UNSET)

        request_sample_group = cls(
            id=id,
            samples=samples,
        )

        request_sample_group.additional_properties = d
        return request_sample_group

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
    def samples(self) -> RequestSampleGroupSamples:
        """The key for each RequestSample should match one of the samplesSchema[n].name property in the request schema json."""
        if isinstance(self._samples, Unset):
            raise NotPresentError(self, "samples")
        return self._samples

    @samples.setter
    def samples(self, value: RequestSampleGroupSamples) -> None:
        self._samples = value

    @samples.deleter
    def samples(self) -> None:
        self._samples = UNSET

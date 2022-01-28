from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.request_sample_group_samples import RequestSampleGroupSamples
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestSampleGroupCreate")


@attr.s(auto_attribs=True, repr=False)
class RequestSampleGroupCreate:
    """  """

    _samples: RequestSampleGroupSamples
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("samples={}".format(repr(self._samples)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestSampleGroupCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        samples = self._samples.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "samples": samples,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_samples() -> RequestSampleGroupSamples:
            samples = RequestSampleGroupSamples.from_dict(d.pop("samples"))

            return samples

        samples = get_samples() if "samples" in d else cast(RequestSampleGroupSamples, UNSET)

        request_sample_group_create = cls(
            samples=samples,
        )

        request_sample_group_create.additional_properties = d
        return request_sample_group_create

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
    def samples(self) -> RequestSampleGroupSamples:
        """The key for each RequestSample should match one of the samplesSchema[n].name property in the request schema json."""
        if isinstance(self._samples, Unset):
            raise NotPresentError(self, "samples")
        return self._samples

    @samples.setter
    def samples(self, value: RequestSampleGroupSamples) -> None:
        self._samples = value

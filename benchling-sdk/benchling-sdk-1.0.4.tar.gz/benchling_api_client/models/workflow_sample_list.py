from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_sample import WorkflowSample
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowSampleList")


@attr.s(auto_attribs=True, repr=False)
class WorkflowSampleList:
    """  """

    _samples: Union[Unset, List[WorkflowSample]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("samples={}".format(repr(self._samples)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowSampleList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        samples: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._samples, Unset):
            samples = []
            for samples_item_data in self._samples:
                samples_item = samples_item_data.to_dict()

                samples.append(samples_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if samples is not UNSET:
            field_dict["samples"] = samples

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_samples() -> Union[Unset, List[WorkflowSample]]:
            samples = []
            _samples = d.pop("samples")
            for samples_item_data in _samples or []:
                samples_item = WorkflowSample.from_dict(samples_item_data)

                samples.append(samples_item)

            return samples

        samples = get_samples() if "samples" in d else cast(Union[Unset, List[WorkflowSample]], UNSET)

        workflow_sample_list = cls(
            samples=samples,
        )

        workflow_sample_list.additional_properties = d
        return workflow_sample_list

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
    def samples(self) -> List[WorkflowSample]:
        if isinstance(self._samples, Unset):
            raise NotPresentError(self, "samples")
        return self._samples

    @samples.setter
    def samples(self, value: List[WorkflowSample]) -> None:
        self._samples = value

    @samples.deleter
    def samples(self) -> None:
        self._samples = UNSET

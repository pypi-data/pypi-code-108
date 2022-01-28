from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.sample_group_status_update import SampleGroupStatusUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="SampleGroupsStatusUpdate")


@attr.s(auto_attribs=True, repr=False)
class SampleGroupsStatusUpdate:
    """ Specification to update status of sample groups on the request which were executed. """

    _sample_groups: List[SampleGroupStatusUpdate]

    def __repr__(self):
        fields = []
        fields.append("sample_groups={}".format(repr(self._sample_groups)))
        return "SampleGroupsStatusUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        sample_groups = []
        for sample_groups_item_data in self._sample_groups:
            sample_groups_item = sample_groups_item_data.to_dict()

            sample_groups.append(sample_groups_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "sampleGroups": sample_groups,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_sample_groups() -> List[SampleGroupStatusUpdate]:
            sample_groups = []
            _sample_groups = d.pop("sampleGroups")
            for sample_groups_item_data in _sample_groups:
                sample_groups_item = SampleGroupStatusUpdate.from_dict(sample_groups_item_data)

                sample_groups.append(sample_groups_item)

            return sample_groups

        sample_groups = (
            get_sample_groups() if "sampleGroups" in d else cast(List[SampleGroupStatusUpdate], UNSET)
        )

        sample_groups_status_update = cls(
            sample_groups=sample_groups,
        )

        return sample_groups_status_update

    @property
    def sample_groups(self) -> List[SampleGroupStatusUpdate]:
        if isinstance(self._sample_groups, Unset):
            raise NotPresentError(self, "sample_groups")
        return self._sample_groups

    @sample_groups.setter
    def sample_groups(self, value: List[SampleGroupStatusUpdate]) -> None:
        self._sample_groups = value

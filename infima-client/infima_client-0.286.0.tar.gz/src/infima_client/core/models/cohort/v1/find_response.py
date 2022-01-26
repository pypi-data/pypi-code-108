from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from attr import define, field

from infima_client.core.models.cohort.v1.find_response_cohorts import (
    CohortV1FindResponseCohorts,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1FindResponse")


@define(auto_attribs=True)
class CohortV1FindResponse:
    """
    Attributes:
        cohorts (Union[Unset, CohortV1FindResponseCohorts]): Mapping of cohort name to cohort object.
    """

    cohorts: Union[Unset, CohortV1FindResponseCohorts] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cohorts: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cohorts, Unset):
            cohorts = self.cohorts.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cohorts is not UNSET:
            field_dict["cohorts"] = cohorts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _cohorts = d.pop("cohorts", UNSET)
        cohorts: Union[Unset, CohortV1FindResponseCohorts]
        if isinstance(_cohorts, Unset):
            cohorts = UNSET
        else:
            cohorts = CohortV1FindResponseCohorts.from_dict(_cohorts)

        cohort_v1_find_response = cls(
            cohorts=cohorts,
        )

        cohort_v1_find_response.additional_properties = d
        return cohort_v1_find_response

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

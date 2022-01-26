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

from infima_client.core.models.cohort.v1.get_actual_prepayments_response_prepayments import (
    CohortV1GetActualPrepaymentsResponsePrepayments,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1GetActualPrepaymentsResponse")


@define(auto_attribs=True)
class CohortV1GetActualPrepaymentsResponse:
    """
    Attributes:
        prepayments (Union[Unset, CohortV1GetActualPrepaymentsResponsePrepayments]):
    """

    prepayments: Union[Unset, CohortV1GetActualPrepaymentsResponsePrepayments] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        prepayments: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.prepayments, Unset):
            prepayments = self.prepayments.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if prepayments is not UNSET:
            field_dict["prepayments"] = prepayments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _prepayments = d.pop("prepayments", UNSET)
        prepayments: Union[Unset, CohortV1GetActualPrepaymentsResponsePrepayments]
        if isinstance(_prepayments, Unset):
            prepayments = UNSET
        else:
            prepayments = CohortV1GetActualPrepaymentsResponsePrepayments.from_dict(
                _prepayments
            )

        cohort_v1_get_actual_prepayments_response = cls(
            prepayments=prepayments,
        )

        cohort_v1_get_actual_prepayments_response.additional_properties = d
        return cohort_v1_get_actual_prepayments_response

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

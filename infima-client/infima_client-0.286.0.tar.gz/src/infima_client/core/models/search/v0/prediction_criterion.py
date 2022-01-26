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

from infima_client.core.models.core.positive_range import CorePositiveRange
from infima_client.core.models.core.range import CoreRange
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="SearchV0PredictionCriterion")


@define(auto_attribs=True)
class SearchV0PredictionCriterion:
    """
    Attributes:
        pred_1_m_cpr_delta_range (Union[Unset, CoreRange]):
        pred_1_m_cpr_range (Union[Unset, CorePositiveRange]):
        pred_3_m_cpr_range (Union[Unset, CorePositiveRange]):
        pred_6_m_cpr_range (Union[Unset, CorePositiveRange]):
    """

    pred_1_m_cpr_delta_range: Union[Unset, CoreRange] = UNSET
    pred_1_m_cpr_range: Union[Unset, CorePositiveRange] = UNSET
    pred_3_m_cpr_range: Union[Unset, CorePositiveRange] = UNSET
    pred_6_m_cpr_range: Union[Unset, CorePositiveRange] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pred_1_m_cpr_delta_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pred_1_m_cpr_delta_range, Unset):
            pred_1_m_cpr_delta_range = self.pred_1_m_cpr_delta_range.to_dict()

        pred_1_m_cpr_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pred_1_m_cpr_range, Unset):
            pred_1_m_cpr_range = self.pred_1_m_cpr_range.to_dict()

        pred_3_m_cpr_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pred_3_m_cpr_range, Unset):
            pred_3_m_cpr_range = self.pred_3_m_cpr_range.to_dict()

        pred_6_m_cpr_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.pred_6_m_cpr_range, Unset):
            pred_6_m_cpr_range = self.pred_6_m_cpr_range.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pred_1_m_cpr_delta_range is not UNSET:
            field_dict["pred1mCprDeltaRange"] = pred_1_m_cpr_delta_range
        if pred_1_m_cpr_range is not UNSET:
            field_dict["pred1mCprRange"] = pred_1_m_cpr_range
        if pred_3_m_cpr_range is not UNSET:
            field_dict["pred3mCprRange"] = pred_3_m_cpr_range
        if pred_6_m_cpr_range is not UNSET:
            field_dict["pred6mCprRange"] = pred_6_m_cpr_range

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _pred_1_m_cpr_delta_range = d.pop("pred1mCprDeltaRange", UNSET)
        pred_1_m_cpr_delta_range: Union[Unset, CoreRange]
        if isinstance(_pred_1_m_cpr_delta_range, Unset):
            pred_1_m_cpr_delta_range = UNSET
        else:
            pred_1_m_cpr_delta_range = CoreRange.from_dict(_pred_1_m_cpr_delta_range)

        _pred_1_m_cpr_range = d.pop("pred1mCprRange", UNSET)
        pred_1_m_cpr_range: Union[Unset, CorePositiveRange]
        if isinstance(_pred_1_m_cpr_range, Unset):
            pred_1_m_cpr_range = UNSET
        else:
            pred_1_m_cpr_range = CorePositiveRange.from_dict(_pred_1_m_cpr_range)

        _pred_3_m_cpr_range = d.pop("pred3mCprRange", UNSET)
        pred_3_m_cpr_range: Union[Unset, CorePositiveRange]
        if isinstance(_pred_3_m_cpr_range, Unset):
            pred_3_m_cpr_range = UNSET
        else:
            pred_3_m_cpr_range = CorePositiveRange.from_dict(_pred_3_m_cpr_range)

        _pred_6_m_cpr_range = d.pop("pred6mCprRange", UNSET)
        pred_6_m_cpr_range: Union[Unset, CorePositiveRange]
        if isinstance(_pred_6_m_cpr_range, Unset):
            pred_6_m_cpr_range = UNSET
        else:
            pred_6_m_cpr_range = CorePositiveRange.from_dict(_pred_6_m_cpr_range)

        search_v0_prediction_criterion = cls(
            pred_1_m_cpr_delta_range=pred_1_m_cpr_delta_range,
            pred_1_m_cpr_range=pred_1_m_cpr_range,
            pred_3_m_cpr_range=pred_3_m_cpr_range,
            pred_6_m_cpr_range=pred_6_m_cpr_range,
        )

        search_v0_prediction_criterion.additional_properties = d
        return search_v0_prediction_criterion

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

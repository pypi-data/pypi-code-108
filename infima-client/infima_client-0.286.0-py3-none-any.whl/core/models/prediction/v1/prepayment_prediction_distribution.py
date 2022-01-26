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
)

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PredictionV1PrepaymentPredictionDistribution")


@define(auto_attribs=True)
class PredictionV1PrepaymentPredictionDistribution:
    """
    Attributes:
        cpr_high (Union[Unset, float]):
        cpr_low (Union[Unset, float]):
        smm_high (Union[Unset, float]):
        smm_low (Union[Unset, float]):
    """

    cpr_high: Union[Unset, float] = UNSET
    cpr_low: Union[Unset, float] = UNSET
    smm_high: Union[Unset, float] = UNSET
    smm_low: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cpr_high = self.cpr_high
        cpr_low = self.cpr_low
        smm_high = self.smm_high
        smm_low = self.smm_low

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cpr_high is not UNSET:
            field_dict["cprHigh"] = cpr_high
        if cpr_low is not UNSET:
            field_dict["cprLow"] = cpr_low
        if smm_high is not UNSET:
            field_dict["smmHigh"] = smm_high
        if smm_low is not UNSET:
            field_dict["smmLow"] = smm_low

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cpr_high = d.pop("cprHigh", UNSET)

        cpr_low = d.pop("cprLow", UNSET)

        smm_high = d.pop("smmHigh", UNSET)

        smm_low = d.pop("smmLow", UNSET)

        prediction_v1_prepayment_prediction_distribution = cls(
            cpr_high=cpr_high,
            cpr_low=cpr_low,
            smm_high=smm_high,
            smm_low=smm_low,
        )

        prediction_v1_prepayment_prediction_distribution.additional_properties = d
        return prediction_v1_prepayment_prediction_distribution

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

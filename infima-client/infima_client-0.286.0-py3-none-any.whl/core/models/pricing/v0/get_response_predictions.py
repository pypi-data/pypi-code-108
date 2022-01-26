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
    cast,
)

from attr import define, field

from infima_client.core.models.pricing.v0.pricing_prediction import (
    PricingV0PricingPrediction,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PricingV0GetResponsePredictions")


@define(auto_attribs=True)
class PricingV0GetResponsePredictions:
    """Mapping of prediction."""

    additional_properties: Dict[str, PricingV0PricingPrediction] = field(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pricing_v0_get_response_predictions = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = PricingV0PricingPrediction.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        pricing_v0_get_response_predictions.additional_properties = (
            additional_properties
        )
        return pricing_v0_get_response_predictions

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> PricingV0PricingPrediction:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: PricingV0PricingPrediction) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

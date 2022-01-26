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

from infima_client.core.models.pricing.v0.get_response_predictions import (
    PricingV0GetResponsePredictions,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PricingV0GetResponse")


@define(auto_attribs=True)
class PricingV0GetResponse:
    """
    Attributes:
        predictions (Union[Unset, PricingV0GetResponsePredictions]): Mapping of prediction.
    """

    predictions: Union[Unset, PricingV0GetResponsePredictions] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        predictions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.predictions, Unset):
            predictions = self.predictions.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if predictions is not UNSET:
            field_dict["predictions"] = predictions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _predictions = d.pop("predictions", UNSET)
        predictions: Union[Unset, PricingV0GetResponsePredictions]
        if isinstance(_predictions, Unset):
            predictions = UNSET
        else:
            predictions = PricingV0GetResponsePredictions.from_dict(_predictions)

        pricing_v0_get_response = cls(
            predictions=predictions,
        )

        pricing_v0_get_response.additional_properties = d
        return pricing_v0_get_response

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

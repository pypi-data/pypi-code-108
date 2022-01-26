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

from infima_client.core.models.prediction.v1.prepayment_prediction_ahead_slice import (
    PredictionV1PrepaymentPredictionAheadSlice,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PredictionV1GetOneMonthAheadResponsePredictions")


@define(auto_attribs=True)
class PredictionV1GetOneMonthAheadResponsePredictions:
    """Mapping of symbol (ie, CUSIP or cohort name) to predictions."""

    additional_properties: Dict[
        str, PredictionV1PrepaymentPredictionAheadSlice
    ] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        prediction_v1_get_one_month_ahead_response_predictions = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = PredictionV1PrepaymentPredictionAheadSlice.from_dict(
                prop_dict
            )

            additional_properties[prop_name] = additional_property

        prediction_v1_get_one_month_ahead_response_predictions.additional_properties = (
            additional_properties
        )
        return prediction_v1_get_one_month_ahead_response_predictions

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> PredictionV1PrepaymentPredictionAheadSlice:
        return self.additional_properties[key]

    def __setitem__(
        self, key: str, value: PredictionV1PrepaymentPredictionAheadSlice
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

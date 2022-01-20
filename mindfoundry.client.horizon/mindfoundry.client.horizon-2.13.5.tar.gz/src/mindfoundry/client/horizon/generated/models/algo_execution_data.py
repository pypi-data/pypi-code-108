import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.algo_execution_data_featurehistory import AlgoExecutionDataFeaturehistory
from ..models.algo_execution_data_latesttargetallocations import (
    AlgoExecutionDataLatesttargetallocations,
)
from ..models.algo_execution_data_targetpredictions import AlgoExecutionDataTargetpredictions
from ..models.algo_execution_data_targetpredictionslowerbound import (
    AlgoExecutionDataTargetpredictionslowerbound,
)
from ..models.algo_execution_data_targetpredictionsupperbound import (
    AlgoExecutionDataTargetpredictionsupperbound,
)
from ..models.algo_execution_data_targetpricehistory import AlgoExecutionDataTargetpricehistory
from ..types import UNSET, Unset

T = TypeVar("T", bound="AlgoExecutionData")


@attr.s(auto_attribs=True)
class AlgoExecutionData:
    """All the inputs an Algo expects when executed

    Algos are executed at particular points in time, at which they are given
    recent history of all assets, predictions made by Horizon, and recent allocations.
    Predictions (and bounds) correspond to what Horizon predicts the value of each
    target will be in the future (how far in the future depends on the underlying
    pipeline making the prediction)."""

    target_price_history: Union[Unset, AlgoExecutionDataTargetpricehistory] = UNSET
    target_predictions: Union[Unset, AlgoExecutionDataTargetpredictions] = UNSET
    target_predictions_upper_bound: Union[
        Unset, AlgoExecutionDataTargetpredictionsupperbound
    ] = UNSET
    target_predictions_lower_bound: Union[
        Unset, AlgoExecutionDataTargetpredictionslowerbound
    ] = UNSET
    feature_history: Union[Unset, AlgoExecutionDataFeaturehistory] = UNSET
    dates: Union[Unset, List[datetime.datetime]] = UNSET
    latest_target_allocations: Union[Unset, AlgoExecutionDataLatesttargetallocations] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        target_price_history: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.target_price_history, Unset):
            target_price_history = self.target_price_history.to_dict()

        target_predictions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.target_predictions, Unset):
            target_predictions = self.target_predictions.to_dict()

        target_predictions_upper_bound: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.target_predictions_upper_bound, Unset):
            target_predictions_upper_bound = self.target_predictions_upper_bound.to_dict()

        target_predictions_lower_bound: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.target_predictions_lower_bound, Unset):
            target_predictions_lower_bound = self.target_predictions_lower_bound.to_dict()

        feature_history: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.feature_history, Unset):
            feature_history = self.feature_history.to_dict()

        dates: Union[Unset, List[str]] = UNSET
        if not isinstance(self.dates, Unset):
            dates = []
            for dates_item_data in self.dates:
                dates_item = dates_item_data.isoformat()

                dates.append(dates_item)

        latest_target_allocations: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.latest_target_allocations, Unset):
            latest_target_allocations = self.latest_target_allocations.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if target_price_history is not UNSET:
            field_dict["targetPriceHistory"] = target_price_history
        if target_predictions is not UNSET:
            field_dict["targetPredictions"] = target_predictions
        if target_predictions_upper_bound is not UNSET:
            field_dict["targetPredictionsUpperBound"] = target_predictions_upper_bound
        if target_predictions_lower_bound is not UNSET:
            field_dict["targetPredictionsLowerBound"] = target_predictions_lower_bound
        if feature_history is not UNSET:
            field_dict["featureHistory"] = feature_history
        if dates is not UNSET:
            field_dict["dates"] = dates
        if latest_target_allocations is not UNSET:
            field_dict["latestTargetAllocations"] = latest_target_allocations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _target_price_history = d.pop("targetPriceHistory", UNSET)
        target_price_history: Union[Unset, AlgoExecutionDataTargetpricehistory]
        if isinstance(_target_price_history, Unset):
            target_price_history = UNSET
        else:
            target_price_history = AlgoExecutionDataTargetpricehistory.from_dict(
                _target_price_history
            )

        _target_predictions = d.pop("targetPredictions", UNSET)
        target_predictions: Union[Unset, AlgoExecutionDataTargetpredictions]
        if isinstance(_target_predictions, Unset):
            target_predictions = UNSET
        else:
            target_predictions = AlgoExecutionDataTargetpredictions.from_dict(_target_predictions)

        _target_predictions_upper_bound = d.pop("targetPredictionsUpperBound", UNSET)
        target_predictions_upper_bound: Union[Unset, AlgoExecutionDataTargetpredictionsupperbound]
        if isinstance(_target_predictions_upper_bound, Unset):
            target_predictions_upper_bound = UNSET
        else:
            target_predictions_upper_bound = (
                AlgoExecutionDataTargetpredictionsupperbound.from_dict(
                    _target_predictions_upper_bound
                )
            )

        _target_predictions_lower_bound = d.pop("targetPredictionsLowerBound", UNSET)
        target_predictions_lower_bound: Union[Unset, AlgoExecutionDataTargetpredictionslowerbound]
        if isinstance(_target_predictions_lower_bound, Unset):
            target_predictions_lower_bound = UNSET
        else:
            target_predictions_lower_bound = (
                AlgoExecutionDataTargetpredictionslowerbound.from_dict(
                    _target_predictions_lower_bound
                )
            )

        _feature_history = d.pop("featureHistory", UNSET)
        feature_history: Union[Unset, AlgoExecutionDataFeaturehistory]
        if isinstance(_feature_history, Unset):
            feature_history = UNSET
        else:
            feature_history = AlgoExecutionDataFeaturehistory.from_dict(_feature_history)

        dates = []
        _dates = d.pop("dates", UNSET)
        for dates_item_data in _dates or []:
            dates_item = isoparse(dates_item_data)

            dates.append(dates_item)

        _latest_target_allocations = d.pop("latestTargetAllocations", UNSET)
        latest_target_allocations: Union[Unset, AlgoExecutionDataLatesttargetallocations]
        if isinstance(_latest_target_allocations, Unset):
            latest_target_allocations = UNSET
        else:
            latest_target_allocations = AlgoExecutionDataLatesttargetallocations.from_dict(
                _latest_target_allocations
            )

        algo_execution_data = cls(
            target_price_history=target_price_history,
            target_predictions=target_predictions,
            target_predictions_upper_bound=target_predictions_upper_bound,
            target_predictions_lower_bound=target_predictions_lower_bound,
            feature_history=feature_history,
            dates=dates,
            latest_target_allocations=latest_target_allocations,
        )

        algo_execution_data.additional_properties = d
        return algo_execution_data

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

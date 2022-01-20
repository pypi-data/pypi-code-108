from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.trading_column_meaning import TradingColumnMeaning
from ..models.trading_specification_stage_config_algoparamvalues import (
    TradingSpecificationStageConfigAlgoparamvalues,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="TradingSpecificationStageConfig")


@attr.s(auto_attribs=True)
class TradingSpecificationStageConfig:
    """ Properties for a stage  """

    prediction_pipeline_id: int
    algo_id: int
    target_data_meaning: TradingColumnMeaning
    algo_param_values: TradingSpecificationStageConfigAlgoparamvalues
    type: Union[Unset, str] = "trading_specification"
    prediction_pipeline_horizon: Union[Unset, int] = -1
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        prediction_pipeline_id = self.prediction_pipeline_id
        algo_id = self.algo_id
        target_data_meaning = self.target_data_meaning.value

        algo_param_values = self.algo_param_values.to_dict()

        type = self.type
        prediction_pipeline_horizon = self.prediction_pipeline_horizon

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "predictionPipelineId": prediction_pipeline_id,
                "algoId": algo_id,
                "targetDataMeaning": target_data_meaning,
                "algoParamValues": algo_param_values,
            }
        )
        if type is not UNSET:
            field_dict["type"] = type
        if prediction_pipeline_horizon is not UNSET:
            field_dict["predictionPipelineHorizon"] = prediction_pipeline_horizon

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        prediction_pipeline_id = d.pop("predictionPipelineId")

        algo_id = d.pop("algoId")

        target_data_meaning = TradingColumnMeaning(d.pop("targetDataMeaning"))

        algo_param_values = TradingSpecificationStageConfigAlgoparamvalues.from_dict(
            d.pop("algoParamValues")
        )

        type = d.pop("type", UNSET)

        prediction_pipeline_horizon = d.pop("predictionPipelineHorizon", UNSET)

        trading_specification_stage_config = cls(
            prediction_pipeline_id=prediction_pipeline_id,
            algo_id=algo_id,
            target_data_meaning=target_data_meaning,
            algo_param_values=algo_param_values,
            type=type,
            prediction_pipeline_horizon=prediction_pipeline_horizon,
        )

        trading_specification_stage_config.additional_properties = d
        return trading_specification_stage_config

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

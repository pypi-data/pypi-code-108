from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.backtest_stage_config import BacktestStageConfig
from ..models.classification_backtest_config import ClassificationBacktestConfig
from ..models.classification_discovery_config import ClassificationDiscoveryConfig
from ..models.classification_specification_config import ClassificationSpecificationConfig
from ..models.feature_generation_stage_config import FeatureGenerationStageConfig
from ..models.filter_stage_config import FilterStageConfig
from ..models.lstm_backtest_stage_config import LstmBacktestStageConfig
from ..models.lstm_prediction_stage_config import LstmPredictionStageConfig
from ..models.prediction_stage_config import PredictionStageConfig
from ..models.problem_specification_config import ProblemSpecificationConfig
from ..models.refinement_stage_config import RefinementStageConfig
from ..models.stage_type import StageType
from ..models.stationarisation_stage_config import StationarisationStageConfig
from ..models.trading_simulation_stage_config import TradingSimulationStageConfig
from ..models.trading_specification_stage_config import TradingSpecificationStageConfig
from ..types import UNSET, Unset

T = TypeVar("T", bound="StageSpecification")


@attr.s(auto_attribs=True)
class StageSpecification:
    """  """

    stage_type: StageType
    config: Union[
        BacktestStageConfig,
        ClassificationBacktestConfig,
        ClassificationDiscoveryConfig,
        ClassificationSpecificationConfig,
        FeatureGenerationStageConfig,
        FilterStageConfig,
        LstmBacktestStageConfig,
        LstmPredictionStageConfig,
        PredictionStageConfig,
        ProblemSpecificationConfig,
        RefinementStageConfig,
        StationarisationStageConfig,
        TradingSimulationStageConfig,
        TradingSpecificationStageConfig,
        Unset,
    ] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        stage_type = self.stage_type.value

        config: Union[Dict[str, Any], Unset]
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, ProblemSpecificationConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, StationarisationStageConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, FeatureGenerationStageConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, FilterStageConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, RefinementStageConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, BacktestStageConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, PredictionStageConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, TradingSpecificationStageConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, TradingSimulationStageConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, ClassificationSpecificationConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, ClassificationDiscoveryConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, ClassificationBacktestConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        elif isinstance(self.config, LstmBacktestStageConfig):
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        else:
            config = UNSET
            if not isinstance(self.config, Unset):
                config = self.config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stageType": stage_type,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        stage_type = StageType(d.pop("stageType"))

        def _parse_config(
            data: object,
        ) -> Union[
            BacktestStageConfig,
            ClassificationBacktestConfig,
            ClassificationDiscoveryConfig,
            ClassificationSpecificationConfig,
            FeatureGenerationStageConfig,
            FilterStageConfig,
            LstmBacktestStageConfig,
            LstmPredictionStageConfig,
            PredictionStageConfig,
            ProblemSpecificationConfig,
            RefinementStageConfig,
            StationarisationStageConfig,
            TradingSimulationStageConfig,
            TradingSpecificationStageConfig,
            Unset,
        ]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_0 = data
                config_type_0: Union[Unset, ProblemSpecificationConfig]
                if isinstance(_config_type_0, Unset):
                    config_type_0 = UNSET
                else:
                    config_type_0 = ProblemSpecificationConfig.from_dict(_config_type_0)

                return config_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_1 = data
                config_type_1: Union[Unset, StationarisationStageConfig]
                if isinstance(_config_type_1, Unset):
                    config_type_1 = UNSET
                else:
                    config_type_1 = StationarisationStageConfig.from_dict(_config_type_1)

                return config_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_2 = data
                config_type_2: Union[Unset, FeatureGenerationStageConfig]
                if isinstance(_config_type_2, Unset):
                    config_type_2 = UNSET
                else:
                    config_type_2 = FeatureGenerationStageConfig.from_dict(_config_type_2)

                return config_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_3 = data
                config_type_3: Union[Unset, FilterStageConfig]
                if isinstance(_config_type_3, Unset):
                    config_type_3 = UNSET
                else:
                    config_type_3 = FilterStageConfig.from_dict(_config_type_3)

                return config_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_4 = data
                config_type_4: Union[Unset, RefinementStageConfig]
                if isinstance(_config_type_4, Unset):
                    config_type_4 = UNSET
                else:
                    config_type_4 = RefinementStageConfig.from_dict(_config_type_4)

                return config_type_4
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_5 = data
                config_type_5: Union[Unset, BacktestStageConfig]
                if isinstance(_config_type_5, Unset):
                    config_type_5 = UNSET
                else:
                    config_type_5 = BacktestStageConfig.from_dict(_config_type_5)

                return config_type_5
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_6 = data
                config_type_6: Union[Unset, PredictionStageConfig]
                if isinstance(_config_type_6, Unset):
                    config_type_6 = UNSET
                else:
                    config_type_6 = PredictionStageConfig.from_dict(_config_type_6)

                return config_type_6
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_7 = data
                config_type_7: Union[Unset, TradingSpecificationStageConfig]
                if isinstance(_config_type_7, Unset):
                    config_type_7 = UNSET
                else:
                    config_type_7 = TradingSpecificationStageConfig.from_dict(_config_type_7)

                return config_type_7
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_8 = data
                config_type_8: Union[Unset, TradingSimulationStageConfig]
                if isinstance(_config_type_8, Unset):
                    config_type_8 = UNSET
                else:
                    config_type_8 = TradingSimulationStageConfig.from_dict(_config_type_8)

                return config_type_8
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_9 = data
                config_type_9: Union[Unset, ClassificationSpecificationConfig]
                if isinstance(_config_type_9, Unset):
                    config_type_9 = UNSET
                else:
                    config_type_9 = ClassificationSpecificationConfig.from_dict(_config_type_9)

                return config_type_9
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_10 = data
                config_type_10: Union[Unset, ClassificationDiscoveryConfig]
                if isinstance(_config_type_10, Unset):
                    config_type_10 = UNSET
                else:
                    config_type_10 = ClassificationDiscoveryConfig.from_dict(_config_type_10)

                return config_type_10
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_11 = data
                config_type_11: Union[Unset, ClassificationBacktestConfig]
                if isinstance(_config_type_11, Unset):
                    config_type_11 = UNSET
                else:
                    config_type_11 = ClassificationBacktestConfig.from_dict(_config_type_11)

                return config_type_11
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _config_type_12 = data
                config_type_12: Union[Unset, LstmBacktestStageConfig]
                if isinstance(_config_type_12, Unset):
                    config_type_12 = UNSET
                else:
                    config_type_12 = LstmBacktestStageConfig.from_dict(_config_type_12)

                return config_type_12
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            _config_type_13 = data
            config_type_13: Union[Unset, LstmPredictionStageConfig]
            if isinstance(_config_type_13, Unset):
                config_type_13 = UNSET
            else:
                config_type_13 = LstmPredictionStageConfig.from_dict(_config_type_13)

            return config_type_13

        config = _parse_config(d.pop("config", UNSET))

        stage_specification = cls(
            stage_type=stage_type,
            config=config,
        )

        stage_specification.additional_properties = d
        return stage_specification

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

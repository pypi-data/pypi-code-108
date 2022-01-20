from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.backtest_stage import BacktestStage
from ..models.classification_backtest_stage import ClassificationBacktestStage
from ..models.classification_discovery_stage import ClassificationDiscoveryStage
from ..models.classification_specification_stage import ClassificationSpecificationStage
from ..models.dataset import Dataset
from ..models.feature_generation_stage import FeatureGenerationStage
from ..models.filter_stage import FilterStage
from ..models.lstm_backtest_stage import LstmBacktestStage
from ..models.lstm_prediction_stage import LstmPredictionStage
from ..models.pipeline_summary import PipelineSummary
from ..models.prediction_stage import PredictionStage
from ..models.problem_specification_stage import ProblemSpecificationStage
from ..models.refinement_stage import RefinementStage
from ..models.stationarisation_stage import StationarisationStage
from ..models.trading_simulation_stage import TradingSimulationStage
from ..models.trading_specification_stage import TradingSpecificationStage

T = TypeVar("T", bound="Pipeline")


@attr.s(auto_attribs=True)
class Pipeline:
    """A Pipeline consists of a sequence of stages, which can be run to perform analysis,
    generate features, or make predictions from a dataset.

    Each stage produces an output, which is fed to the next stage.
    It also produces Insights, which can be retrieved separately via the API.
    Pipelines are linear. Stages within the list are in order."""

    summary: PipelineSummary
    stages: List[
        Union[
            BacktestStage,
            ClassificationBacktestStage,
            ClassificationDiscoveryStage,
            ClassificationSpecificationStage,
            FeatureGenerationStage,
            FilterStage,
            LstmBacktestStage,
            LstmPredictionStage,
            PredictionStage,
            ProblemSpecificationStage,
            RefinementStage,
            StationarisationStage,
            TradingSimulationStage,
            TradingSpecificationStage,
        ]
    ]
    dataset: Dataset
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        summary = self.summary.to_dict()

        stages = []
        for stages_item_data in self.stages:
            if isinstance(stages_item_data, ProblemSpecificationStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, StationarisationStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, FeatureGenerationStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, FilterStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, RefinementStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, BacktestStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, PredictionStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, TradingSpecificationStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, TradingSimulationStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, ClassificationSpecificationStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, ClassificationDiscoveryStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, ClassificationBacktestStage):
                stages_item = stages_item_data.to_dict()

            elif isinstance(stages_item_data, LstmBacktestStage):
                stages_item = stages_item_data.to_dict()

            else:
                stages_item = stages_item_data.to_dict()

            stages.append(stages_item)

        dataset = self.dataset.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "summary": summary,
                "stages": stages,
                "dataset": dataset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        summary = PipelineSummary.from_dict(d.pop("summary"))

        stages = []
        _stages = d.pop("stages")
        for stages_item_data in _stages:

            def _parse_stages_item(
                data: object,
            ) -> Union[
                BacktestStage,
                ClassificationBacktestStage,
                ClassificationDiscoveryStage,
                ClassificationSpecificationStage,
                FeatureGenerationStage,
                FilterStage,
                LstmBacktestStage,
                LstmPredictionStage,
                PredictionStage,
                ProblemSpecificationStage,
                RefinementStage,
                StationarisationStage,
                TradingSimulationStage,
                TradingSpecificationStage,
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_0 = ProblemSpecificationStage.from_dict(data)

                    return stages_item_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_1 = StationarisationStage.from_dict(data)

                    return stages_item_type_1
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_2 = FeatureGenerationStage.from_dict(data)

                    return stages_item_type_2
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_3 = FilterStage.from_dict(data)

                    return stages_item_type_3
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_4 = RefinementStage.from_dict(data)

                    return stages_item_type_4
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_5 = BacktestStage.from_dict(data)

                    return stages_item_type_5
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_6 = PredictionStage.from_dict(data)

                    return stages_item_type_6
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_7 = TradingSpecificationStage.from_dict(data)

                    return stages_item_type_7
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_8 = TradingSimulationStage.from_dict(data)

                    return stages_item_type_8
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_9 = ClassificationSpecificationStage.from_dict(data)

                    return stages_item_type_9
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_10 = ClassificationDiscoveryStage.from_dict(data)

                    return stages_item_type_10
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_11 = ClassificationBacktestStage.from_dict(data)

                    return stages_item_type_11
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    stages_item_type_12 = LstmBacktestStage.from_dict(data)

                    return stages_item_type_12
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                stages_item_type_13 = LstmPredictionStage.from_dict(data)

                return stages_item_type_13

            stages_item = _parse_stages_item(stages_item_data)

            stages.append(stages_item)

        dataset = Dataset.from_dict(d.pop("dataset"))

        pipeline = cls(
            summary=summary,
            stages=stages,
            dataset=dataset,
        )

        pipeline.additional_properties = d
        return pipeline

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

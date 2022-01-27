from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from mindfoundry.client.horizon.generated.models import (
    ClassificationDiscoveryConfig as GeneratedClassificationDiscoveryConfig,
)
from mindfoundry.client.horizon.generated.models import (
    CorrelationMethod as GeneratedCorrelationMethod,
)
from mindfoundry.client.horizon.generated.models import (
    FeatureGenerationStageConfig as GeneratedFeatureGenerationStageConfig,
)
from mindfoundry.client.horizon.generated.models import (
    FeatureGeneratorType as GeneratedFeatureGeneratorType,
)
from mindfoundry.client.horizon.generated.models import (
    FilterStageConfig as GeneratedFilterStageConfig,
)
from mindfoundry.client.horizon.generated.models import (
    RefinementStageConfig as GeneratedRefinementStageConfig,
)
from mindfoundry.client.horizon.generated.models import RegressorType as GeneratedRegressorType
from mindfoundry.client.horizon.generated.models import (
    StationarisationStageConfig as GeneratedStationarisationStageConfig,
)
from mindfoundry.client.horizon.generated.models import (
    StationarisationStrategy as GeneratedStationarisationStrategy,
)
from mindfoundry.client.horizon.generated.models import (
    TargetTransformType as GeneratedTargetTransformType,
)

from .base import ValidatedConfig, assert_not_empty_if_provided
from .values import (
    CorrelationMethod,
    FeatureGeneratorType,
    RegressorType,
    StationarizationStrategy,
    TargetTransformType,
)


@dataclass
class StationarizationConfig(ValidatedConfig):
    """ Configure the stationarization stage of a forecasting model. """

    strategy: Optional[StationarizationStrategy] = None
    """
    What strategy should be used to handle columns that support / do not support stationarization?
    Default is `keep_fail`.
    """

    target_transform: Optional[TargetTransformType] = None
    """
    Whether the target should undergo a lag transformation as well. Default is `HorizonLagDiff`.
    """

    adf_threshold: Optional[float] = None
    """
    Running stationarisation of features runs an ADF test on all the features. An ADF test
    is a statistical test that assigns a score between 0 and 1 to each feature, where scores
    closer to zero are more likely stationary, and scores closer to 1 are more likely non
    stationary. The score itself is a statistical p-value, and this threshold specifies
    the p-value above which a feature is considered non stationary.
    Default is 0.03.
    """

    def validate(self) -> None:
        if self.adf_threshold is not None:
            assert (
                0 <= self.adf_threshold <= 1
            ), "The adf_threshold of the stationarization stage must be between 0 and 1"

    def to_stage_config(self) -> GeneratedStationarisationStageConfig:
        default_stage_config = self.default_stage_config()
        return GeneratedStationarisationStageConfig(
            adf_threshold=self.adf_threshold or default_stage_config.adf_threshold,
            strategy=(
                GeneratedStationarisationStrategy(self.strategy)
                if self.strategy is not None
                else default_stage_config.strategy
            ),
            target_transform=(
                GeneratedTargetTransformType(self.target_transform)
                if self.target_transform is not None
                else default_stage_config.target_transform
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy,
            "target_transform": self.target_transform,
            "adf_threshold": self.adf_threshold,
        }

    @staticmethod
    def from_dict(dictionary: Dict[str, Any]) -> StationarizationConfig:
        return StationarizationConfig(
            strategy=dictionary["strategy"],
            target_transform=dictionary["target_transform"],
            adf_threshold=dictionary["adf_threshold"],
        )

    @staticmethod
    def default() -> StationarizationConfig:
        return StationarizationConfig(
            adf_threshold=0.03,
            strategy=StationarizationStrategy.KEEP_FAILED,
            target_transform=TargetTransformType.HORIZON_LAG_DIFF,
        )

    @staticmethod
    def default_stage_config() -> GeneratedStationarisationStageConfig:
        return GeneratedStationarisationStageConfig(
            adf_threshold=0.03,
            strategy=GeneratedStationarisationStrategy.KEEP_FAIL,
            target_transform=GeneratedTargetTransformType.HORIZONLAGDIFF,
        )


@dataclass
class FeatureGenerationConfig(ValidatedConfig):
    """ Configure the feature generation stage of a forecasting model. """

    max_features: Optional[int] = None
    """ Upper bound on the number of features to generate per horizon. Default is 500. """

    generators: Optional[List[FeatureGeneratorType]] = None
    """
    List of all feature generation strategies to be used in this stage. By default, all
    generators will be used.
    """

    def validate(self) -> None:
        if self.max_features is not None:
            assert self.max_features > 0, (
                "The max_features parameter of the feature generation stage must be "
                "greater than zero"
            )

        if self.generators is not None:
            assert len(self.generators) > 0, (
                "When specifying generators used in the feature generation stage, at least "
                "one generator must be provided"
            )

            # fmt: off
            assert len(set(self.generators)) == len(self.generators), (
                "The list of generators should not contain any duplicate item."
            )
            # fmt: on

    def to_stage_config(self) -> GeneratedFeatureGenerationStageConfig:
        default_stage_config = self.default_stage_config()
        return GeneratedFeatureGenerationStageConfig(
            max_n_features=self.max_features or default_stage_config.max_n_features,
            feature_generators=(
                [GeneratedFeatureGeneratorType(g) for g in self.generators]
                if self.generators is not None
                else default_stage_config.feature_generators
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_features": self.max_features,
            "generators": self.generators,
        }

    @staticmethod
    def from_dict(dictionary: Dict[str, Any]) -> FeatureGenerationConfig:
        return FeatureGenerationConfig(
            max_features=dictionary["max_features"],
            generators=dictionary["generators"],
        )

    @staticmethod
    def default() -> FeatureGenerationConfig:
        return FeatureGenerationConfig(
            max_features=500,
            generators=[
                FeatureGeneratorType.LAG,
                FeatureGeneratorType.EWMA,
                FeatureGeneratorType.AUTO_LAG,
                FeatureGeneratorType.CALENDAR,
                FeatureGeneratorType.LOGARITHM,
                FeatureGeneratorType.NUMBER_OF_PEAKS,
                FeatureGeneratorType.ONE_HOT_ENCODING,
                FeatureGeneratorType.PERCENT_CHANGE,
                FeatureGeneratorType.ROLLING_AVERAGE,
            ],
        )

    @staticmethod
    def default_stage_config() -> GeneratedFeatureGenerationStageConfig:
        return GeneratedFeatureGenerationStageConfig(
            max_n_features=500,
            feature_generators=[
                GeneratedFeatureGeneratorType.LAG,
                GeneratedFeatureGeneratorType.EWMA,
                GeneratedFeatureGeneratorType.AUTOLAG,
                GeneratedFeatureGeneratorType.CALENDAR,
                GeneratedFeatureGeneratorType.LOGARITHM,
                GeneratedFeatureGeneratorType.NUM_PEAKS,
                GeneratedFeatureGeneratorType.ONE_HOT_ENCODE,
                GeneratedFeatureGeneratorType.PERC_CHANGE,
                GeneratedFeatureGeneratorType.ROLLING_AVERAGE,
            ],
        )


@dataclass
class FilteringConfig(ValidatedConfig):
    """ Configure the filtering stage of a forecasting model. """

    max_features: Optional[int] = None
    """ Upper bound on the number of remaining features per horizon. Default is 30. """

    correlation_method: Optional[CorrelationMethod] = None
    """
    Correlation method to be used to determine the most appropriate features to be filtered out
    and the most useful features to keep. Default is `pearson`.
    """

    def validate(self) -> None:
        if self.max_features is not None:
            assert (
                self.max_features > 0
            ), "The max_features parameter of the filtering stage must be greater than zero"

    def to_stage_config(self) -> GeneratedFilterStageConfig:
        default_stage_config = self.default_stage_config()
        return GeneratedFilterStageConfig(
            max_n_features=self.max_features or default_stage_config.max_n_features,
            method=(
                GeneratedCorrelationMethod(self.correlation_method)
                if self.correlation_method is not None
                else default_stage_config.method
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_features": self.max_features,
            "correlation_method": self.correlation_method,
        }

    @staticmethod
    def from_dict(dictionary: Dict[str, Any]) -> FilteringConfig:
        return FilteringConfig(
            max_features=dictionary["max_features"],
            correlation_method=dictionary["correlation_method"],
        )

    @staticmethod
    def default() -> FilteringConfig:
        return FilteringConfig(
            max_features=30,
            correlation_method=CorrelationMethod.PEARSON,
        )

    @staticmethod
    def default_stage_config() -> GeneratedFilterStageConfig:
        return GeneratedFilterStageConfig(
            max_n_features=30,
            method=GeneratedCorrelationMethod.PEARSON,
        )


@dataclass
class RefinementConfig(ValidatedConfig):
    """ Configure the refinement stage of a forecasting model. """

    max_features: Optional[int] = None
    """ Upper bound on number of remaining features per horizon. Default is 20. """

    min_features: Optional[int] = None
    """ Lower bound on the number of remaining features per horizon. Default is 5. """

    early_stopping_sensitivity: Optional[float] = None
    """
    This must be a value between 0 and 1. If closer to 1 then the stage will run faster,
    but will result in a larger feature set. Default is `0`.
    """

    deep_search: Optional[bool] = None
    """
    Whether to try dropping each feature at every iteration, or only a subset (50%).
    Default is `false`.
    """

    regressor: Optional[RegressorType] = None
    """ Regressor to be used for the refinement. Default is `RandomForest`. """

    def validate(self) -> None:
        if self.early_stopping_sensitivity is not None:
            assert 0 <= self.early_stopping_sensitivity <= 1, (
                "The early_stopping_sensitivity parameter of the refinement stage must be "
                "between 0 and 1 (bounds included)"
            )

        if self.min_features is not None:
            assert (
                self.min_features > 0
            ), "The min_features parameter of the refinement stage must be greater than zero"

        if self.max_features is not None:
            assert (
                self.max_features > 0
            ), "The max_features parameter of the refinement stage must be greater than zero"

        if self.max_features is not None and self.min_features is not None:
            assert 0 < self.min_features <= self.max_features, (
                "The min_features parameter of the refinement stage must be greater than "
                "zero and less than (or equal to) max_features"
            )

    def to_stage_config(self) -> GeneratedRefinementStageConfig:
        default_stage_config = self.default_stage_config()
        return GeneratedRefinementStageConfig(
            max_features=self.max_features or default_stage_config.max_features,
            min_features=self.min_features or default_stage_config.min_features,
            early_stopping_sensitivity=(
                self.early_stopping_sensitivity
                if self.early_stopping_sensitivity is not None
                else default_stage_config.early_stopping_sensitivity
            ),
            deep_search=(
                self.deep_search
                if self.deep_search is not None
                else default_stage_config.deep_search
            ),
            regressor=(
                GeneratedRegressorType(self.regressor)
                if self.regressor is not None
                else default_stage_config.regressor
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_features": self.max_features,
            "min_features": self.min_features,
            "early_stopping_sensitivity": self.early_stopping_sensitivity,
            "deep_search": self.deep_search,
            "regressor": self.regressor,
        }

    @staticmethod
    def from_dict(dictionary: Dict[str, Any]) -> RefinementConfig:
        return RefinementConfig(
            max_features=dictionary["max_features"],
            min_features=dictionary["min_features"],
            early_stopping_sensitivity=dictionary["early_stopping_sensitivity"],
            deep_search=dictionary["deep_search"],
            regressor=dictionary["regressor"],
        )

    @staticmethod
    def default() -> RefinementConfig:
        return RefinementConfig(
            max_features=20,
            min_features=5,
            early_stopping_sensitivity=0,
            deep_search=False,
            regressor=RegressorType.RANDOM_FOREST,
        )

    @staticmethod
    def default_stage_config() -> GeneratedRefinementStageConfig:
        return GeneratedRefinementStageConfig(
            max_features=20,
            min_features=5,
            early_stopping_sensitivity=0,
            deep_search=False,
            regressor=GeneratedRegressorType.RANDOMFOREST,
        )


@dataclass
class ClassificationDiscoveryConfig(ValidatedConfig):
    """ Configure the discovery stage of a classification model. """

    max_features: Optional[int] = None
    """ Upper bound on the number of features to generate per horizon. Default is 100. """

    timeout_seconds: Optional[float] = None
    """ Maximum time allowed for running this stage. Default is `60` seconds. """

    excluded_columns: Optional[List[str]] = None
    """
    List of column names to exclude from feature generation.
    By default, no column will be excluded.
    """

    feature_generation_enabled: Optional[bool] = None
    """
    Discovery can run either with or without feature generation. In the latter case, only the
    original columns will be taken into account and Horizon will not generate any artificial
    feature. Default is True.
    """

    def validate(self) -> None:
        assert_not_empty_if_provided("excluded_columns", self.excluded_columns, True)

        if self.timeout_seconds is not None:
            assert self.timeout_seconds > 0, "Timeout must be a positive value"

    def to_stage_config(self) -> GeneratedClassificationDiscoveryConfig:
        default_stage_config = self.default_stage_config()
        return GeneratedClassificationDiscoveryConfig(
            max_n_features=self.max_features or default_stage_config.max_n_features,
            timeout_seconds=self.timeout_seconds or default_stage_config.timeout_seconds,
            columns_to_not_generate_features_from=(
                self.excluded_columns or default_stage_config.columns_to_not_generate_features_from
            ),
            feature_generation_enabled=(
                self.feature_generation_enabled
                if self.feature_generation_enabled is not None
                else default_stage_config.feature_generation_enabled
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_features": self.max_features,
            "timeout_seconds": self.timeout_seconds,
            "excluded_columns": self.excluded_columns,
            "feature_generation_enabled": self.feature_generation_enabled,
        }

    @staticmethod
    def from_dict(dictionary: Dict[str, Any]) -> ClassificationDiscoveryConfig:
        return ClassificationDiscoveryConfig(
            max_features=dictionary["max_features"],
            timeout_seconds=dictionary["timeout_seconds"],
            excluded_columns=dictionary["excluded_columns"],
            feature_generation_enabled=dictionary["feature_generation_enabled"],
        )

    @staticmethod
    def default() -> ClassificationDiscoveryConfig:
        return ClassificationDiscoveryConfig(
            max_features=100,
            timeout_seconds=60,
            excluded_columns=[],
            feature_generation_enabled=True,
        )

    @staticmethod
    def default_stage_config() -> GeneratedClassificationDiscoveryConfig:
        return GeneratedClassificationDiscoveryConfig(
            timeout_seconds=60,
            feature_generation_enabled=True,
            columns_to_not_generate_features_from=[],
            max_n_features=100,
        )

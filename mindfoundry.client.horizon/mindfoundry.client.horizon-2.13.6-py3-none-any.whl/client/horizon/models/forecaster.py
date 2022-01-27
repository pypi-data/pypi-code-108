from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from mindfoundry.client.horizon.client.horizon_client import Connection, HorizonClient
from mindfoundry.client.horizon.generated.models import (
    IndividualDataset,
    Pipeline,
    PredictResponse,
    ProblemSpecificationConfig,
)
from mindfoundry.client.horizon.generated.models import RegressorType as GeneratedRegressorType
from mindfoundry.client.horizon.generated.models import StageType
from mindfoundry.client.horizon.models.config import (
    CorrelationMethod,
    FeatureGenerationConfig,
    FeatureGeneratorType,
    FilteringConfig,
    ModelConfig,
    RefinementConfig,
    RegressorType,
    StationarizationConfig,
    StationarizationStrategy,
    TargetTransformType,
    assert_not_empty_if_provided,
)

from .base import (
    FeatureSet,
    FlexibleInputData,
    HorizonModel,
    ModelPrediction,
    ReportingCallback,
    ReportingFacility,
)
from .config.base import assert_no_missing_columns


@dataclass
class ForecasterConfig(ModelConfig):
    """ Configures an HorizonForecaster model. """

    target: Optional[str] = None
    """
    Name of the column to be used as target for the forecasting. If not provided in the initial
    config, a target will be required when `.fit()` is invoked.
    Mutually exclusive with `targets` (use one or the other but not both).
    """

    targets: Optional[List[str]] = None
    """
    List of column names to be used as targets for the forecasting. If not provided in the initial
    config, one or more targets will be required when `.fit()` is invoked.
    Mutually exclusive with `target` (use one or the other but not both).
    """

    horizons: Optional[List[int]] = None
    """
    List of horizons to use for training and prediction. A horizon is a number that describes
    how many time steps ahead to predict. One time step is equal to the cadence of the
    data (e.g. daily, hourly, monthly, etc...).
    By default, horizons = [1, 2, 3, 4, 5].
    """

    stationarization: Optional[Union[bool, StationarizationConfig]] = None
    """
    Configuration for the stationarization stage. This is the first stage in the model building
    process. It aims at removing trivial trends in data so as to only leave a stationary process
    which can be more effectively learnt.

    This field can be a boolean that indicates whether the stage should be enabled. It can
    also be a `StationarizationConfig` object in case you need to define finer details about
    the stage itself.

    By default, the stage is enabled.
    """

    feature_generation: Optional[Union[bool, FeatureGenerationConfig]] = None
    """
    Configuration for the feature generation stage. This is the second stage in the model building
    process. It produces artificial features based on existing columns by exploiting a number of
    different augmentation techniques.

    This field can be a boolean that indicates whether the stage should be enabled. It can
    also be a `FeatureGenerationConfig` object in case you need to define finer details about
    the stage itself.

    By default, the stage is enabled.
    """

    filtering: Optional[Union[bool, FilteringConfig]] = None
    """
    Configuration for the filtering stage. This is the third stage in the model building
    process. It reduces the number of total features by computing a relevance score for each
    one and only keeping a selected top N of best performing features.

    This field can be a boolean that indicates whether the stage should be enabled. It can
    also be a `FilteringConfig` object in case you need to define finer details about
    the stage itself.

    By default, the stage is enabled.
    """

    refinement: Optional[Union[bool, RefinementConfig]] = None
    """
    Configuration for the refinement stage. This is the fourth stage in the model building
    process. It further trims down the total number of features by temporarily removing
    specific subsets of features and checking how partial models perform. Those features whose
    removal is the most impactful are assumed to be more important for the prediction.

    This field can be a boolean that indicates whether the stage should be enabled. It can
    also be a `RefinementConfig` object in case you need to define finer details about
    the stage itself.

    By default, the stage is enabled. Beware! this a very computationally intensive stage.
    """

    def validate(self) -> None:
        super().validate()

        assert self.target is None or self.targets is None, (
            "target and targets cannot be specified together at the same time."
            "Use one or the other"
        )

        assert_not_empty_if_provided("target", self.target)
        assert_not_empty_if_provided("targets", self.targets, True)
        assert_not_empty_if_provided("horizons", self.horizons, True)

        if isinstance(self.feature_generation, FeatureGenerationConfig):
            self.feature_generation.validate()

        if isinstance(self.filtering, FilteringConfig):
            self.filtering.validate()

        if isinstance(self.stationarization, StationarizationConfig):
            self.stationarization.validate()

        if isinstance(self.refinement, RefinementConfig):
            self.refinement.validate()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "inputs": self.inputs,
            "exclude_from_input": self.exclude_from_input,
            "target": self.target,
            "targets": self.targets,
            "horizons": self.horizons,
            "stationarization": (
                self.stationarization.to_dict()
                if isinstance(self.stationarization, StationarizationConfig)
                else self.stationarization
            ),
            "feature_generation": (
                self.feature_generation.to_dict()
                if isinstance(self.feature_generation, FeatureGenerationConfig)
                else self.feature_generation
            ),
            "filtering": (
                self.filtering.to_dict()
                if isinstance(self.filtering, FilteringConfig)
                else self.filtering
            ),
            "refinement": (
                self.refinement.to_dict()
                if isinstance(self.refinement, RefinementConfig)
                else self.refinement
            ),
        }

    @staticmethod
    def from_dict(dictionary: Dict[str, Any]) -> ForecasterConfig:
        return ForecasterConfig(
            name=dictionary["name"],
            inputs=dictionary["inputs"],
            exclude_from_input=dictionary["exclude_from_input"],
            target=dictionary["target"],
            targets=dictionary["targets"],
            horizons=dictionary["horizons"],
            stationarization=(
                StationarizationConfig.from_dict(dictionary["stationarization"])
                if isinstance(dictionary["stationarization"], dict)
                else bool(dictionary["stationarization"])
            ),
            feature_generation=(
                FeatureGenerationConfig.from_dict(dictionary["feature_generation"])
                if isinstance(dictionary["feature_generation"], dict)
                else bool(dictionary["feature_generation"])
            ),
            filtering=(
                FilteringConfig.from_dict(dictionary["filtering"])
                if isinstance(dictionary["filtering"], dict)
                else bool(dictionary["filtering"])
            ),
            refinement=(
                RefinementConfig.from_dict(dictionary["refinement"])
                if isinstance(dictionary["refinement"], dict)
                else bool(dictionary["refinement"])
            ),
        )


class HorizonForecaster(HorizonModel):
    def __init__(
        self,
        connection: Connection,
        name: Optional[str] = None,
        target: Optional[str] = None,
        targets: Optional[List[str]] = None,
        inputs: Optional[List[str]] = None,
        exclude_from_input: Optional[List[str]] = None,
        horizons: Optional[List[int]] = None,
        stationarization: Optional[bool] = None,
        stationarization_strategy: Optional[StationarizationStrategy] = None,
        stationarization_target_transform: Optional[TargetTransformType] = None,
        stationarization_adf_threshold: Optional[float] = None,
        feature_generation: Optional[bool] = None,
        feature_generation_max_features: Optional[int] = None,
        feature_generation_generators: Optional[List[FeatureGeneratorType]] = None,
        filtering: Optional[bool] = None,
        filtering_max_features: Optional[int] = None,
        filtering_correlation_method: Optional[CorrelationMethod] = None,
        refinement: Optional[bool] = None,
        refinement_max_features: Optional[int] = None,
        refinement_min_features: Optional[int] = None,
        refinement_early_stopping_sensitivity: Optional[float] = None,
        refinement_deep_search: Optional[bool] = None,
        refinement_regressor: Optional[RegressorType] = None,
    ):
        """
        Create a new Horizon forecasting model.

        :param connection:
            Connection object to the instance you are using, including api key.
        :param name:
            Name of the model. Although not necessary, it is advised to give models a
            name so that multiple models can be easily told apart. If not provided, the model will
            be given a random name.
        :param target:
            Name of the column to be used as target for the forecasting. If not
            provided in the initial config, a target will be required when `.fit()` is invoked.
            Mutually exclusive with `targets` (use one or the other but not both).
        :param targets:
            List of column names to be used as targets for the forecasting.
            If not provided in the initial config, one or more targets will be required when
            `.fit()` is invoked.
            Mutually exclusive with `target` (use one or the other but not both).
        :param inputs:
            List of column names to be used as feature for the forecasting. Only the specified
            columns will be processed and analyzed. Any column that is not in this list will
            be ignored.
            By default, all columns will be used.
            Mutually exclusive with `exclude_from_input` (use one or the other but not both).
        :param exclude_from_input:
            List of column names to be ignored in the forecasting. Every other column that is
            present in the data but not specified in this list will be used as feature.
            By default, no column will be excluded.
            Mutually exclusive with `inputs` (use one or the other but not both).
        :param horizons:
            List of horizons to use for training and prediction. A horizon is a number that
            describe how many time steps ahead in time to predict. One time step is equal to
            the cadence of the data (e.g. daily, hourly, monthly, etc...).
            By default, horizons = [1, 2, 3, 4, 5].
        :param stationarization:
            Whether the stationarization stage is enabled. This is the first stage in the model
            building process. It aims at removing trivial trends in data so as to only leave a
            stationary process which can be more effectively learnt.
            By default, the stage is enabled. If disabled, all other parameters relating to
            stationarization will be ignored.
        :param stationarization_strategy:
            What strategy should be used to handle columns that support / do not support
            stationarization? Default is `keep_fail`.
        :param stationarization_target_transform:
            Whether the target should undergo a lag transformation as well.
            Default is `HorizonLagDiff`.
        :param stationarization_adf_threshold:
            Running stationarisation of features runs an ADF test on all the features. An ADF test
            is a statistical test that assigns a score between 0 and 1 to each feature, where
            scores closer to zero are more likely stationary, and scores closer to 1 are more
            likely non stationary. The score itself is a statistical p-value, and this
            threshold specifies the p-value above which a feature is considered non stationary.
            Default is 0.03.
        :param feature_generation:
            Whether the feature generation stage is enabled. This is the second stage in the model
            building process. It produces artificial features based on existing columns by
            exploiting a number of different augmentation techniques.
            By default, the stage is enabled. If disabled, all other parameters relating to
            feature generation will be ignored.
        :param feature_generation_max_features:
            Upper bound on the number of features to generate per horizon. Default is 500.
        :param feature_generation_generators:
            List of all feature generation strategies to be used in this stage. By default, all
            generators will be used.
        :param filtering:
            Whether the filtering stage is enabled. This is the third stage in the model building
            process. It reduces the number of total features by computing a relevance score for
            each one and only keeping a selected top N of best performing features.
            By default, the stage is enabled. If disabled, all other parameters relating to
            filtering will be ignored.
        :param filtering_max_features:
            Upper bound on the number of remaining features per horizon. Default is 30.
        :param filtering_correlation_method:
            Correlation method to be used to determine the most appropriate features to be
            filtered out and the most useful to instead keep. Default is `pearson`.
        :param refinement:
            Whether the refinement stage is enabled. This is the fourth stage in the model building
            process. It further trims down the total number of features by temporarily removing
            specific subsets of features and checking how partial models perform. Those features
            whose removal is the most impactful are assumed to be more important for the
            prediction.
            By default, the stage is enabled. If disabled, all other parameters relating to
            refinement will be ignored. Beware! this a very computationally intensive stage.
        :param refinement_max_features:
            Upper bound on number of remaining features per horizon. Default is 20.
        :param refinement_min_features:
            Lower bound on the number of remaining features per horizon. Default is 5.
        :param refinement_early_stopping_sensitivity:
            This must be a value between 0 and 1. If closer to 1 then the stage will run faster,
            but will result in a larger feature set. Default is `0`.
        :param refinement_deep_search:
            Whether to try dropping each feature at every iteration, or only a subset (50%).
            Default is `false`.
        :param refinement_regressor:
            Regressor to be used for the refinement. Default is `RandomForest`.
        """
        super().__init__(HorizonClient(connection))
        self._config = ForecasterConfig(
            name=name,
            target=target,
            targets=targets,
            inputs=inputs,
            exclude_from_input=exclude_from_input,
            horizons=horizons,
            stationarization=(
                stationarization
                if stationarization is False
                else StationarizationConfig(
                    strategy=stationarization_strategy,
                    target_transform=stationarization_target_transform,
                    adf_threshold=stationarization_adf_threshold,
                )
            ),
            feature_generation=(
                feature_generation
                if feature_generation is False
                else FeatureGenerationConfig(
                    max_features=feature_generation_max_features,
                    generators=feature_generation_generators,
                )
            ),
            filtering=(
                filtering
                if filtering is False
                else FilteringConfig(
                    max_features=filtering_max_features,
                    correlation_method=filtering_correlation_method,
                )
            ),
            refinement=(
                refinement
                if refinement is False
                else RefinementConfig(
                    max_features=refinement_max_features,
                    min_features=refinement_min_features,
                    early_stopping_sensitivity=refinement_early_stopping_sensitivity,
                    deep_search=refinement_deep_search,
                    regressor=refinement_regressor,
                )
            ),
        )

        self._config.validate()

    @property
    def config(self) -> ForecasterConfig:
        return self._config

    @staticmethod
    def load(file_path: str, connection: Connection) -> HorizonForecaster:
        """
        Load a forecaster model from a file.

        :param file_path:
            Path to a json file that contains a serialized forecaster model. The file must
            have been produced using the `.save()` method.
        :param connection:
            Connection to the Horizon instance to use. Beware that this connection must refer
            to the same Horizon instance that the saved model used.
        """
        with open(file_path, "r+") as file:
            serialized_model = json.loads(file.read())

        assert (
            serialized_model["base_url"] == connection.base_url
        ), "base_url from serialized model does not match base_url from connection"

        # pylint:disable=protected-access
        forecaster = HorizonForecaster(connection)
        forecaster._config = ForecasterConfig.from_dict(serialized_model["config"])
        forecaster._pipeline_id = serialized_model["pipeline_id"]
        forecaster._dataset_id = serialized_model["dataset_id"]
        forecaster._persisted = True

        return forecaster

    def save(self, file_path: str) -> None:
        """
        Save the current forecaster model to a file so it can be loaded at a later time.
        The process persists the following information:
            - configuration of the forecaster;
            - if the `.fit()` method was invoked, a reference to the remote model being built
              after data has been fitted;
            - Horizon instance being used.

        :param file_path:
            Path to a json file where the model will be persisted.
        """
        # pylint:disable=protected-access
        serialized_model = {
            "base_url": self._client._connection.base_url,
            "config": self.config.to_dict(),
            "pipeline_id": self._pipeline_id,
            "dataset_id": self._dataset_id,
        }

        with open(file_path, "w+") as file:
            file.write(json.dumps(serialized_model))

        self._persisted = True

    def fit(
        self,
        training_data: FlexibleInputData,
        target: Optional[str] = None,
        targets: Optional[List[str]] = None,
        reporting_callback: Optional[ReportingCallback] = None,
    ) -> None:
        """
        Create a forecasting model on the given training data. Calling this method a second time
        will delete any previously existing model and create a new one.

        :param training_data:
            A dataframe, series or numpy array. If a series or a one-dimensional numpy array is
            given, Horizon will automatically generate a time index for the time series. We
            anyway recommend to always include a datetime column in your data to be used as
            time index with proper granularity.
            Also notice you should not time-shift your target column when passing it to `.fit`.
            The system will take care of rearranging your data to match the prediction horizon(s).
        :param target:
            Name of the column to use as target. If not specified, the target(s) provided in the
            initial configuration will be used.
            Mutually exclusive with `targets` (use one or the other but not both).
        :param targets:
            Names of the columns to use as targets. If not specified, the target(s) provided in the
            initial configuration will be used.
            Mutually exclusive with `target` (use one or the other but not both).
        :param reporting_callback:
            Function used to report progress of this method. If not provided, a default message
            will be printed to stdout using `print`. Call arguments: current step (int),
            number of total steps (int), description of the current step (str).
        :return:
            The method will wait for the data to be uploaded to Horizon and for the model
            building pipeline to complete. When its coroutine returns, Horizon will have
            completed data fitting.
        """
        self._check_environment()

        reporting_facility = ReportingFacility(
            reporting_callback=reporting_callback,
            steps_count=10,
        )

        reporting_facility.report("Removing pre-existing model")
        self.delete_model()

        input_df = self._make_input_data_frame(training_data)
        dataset_name = self.config.resolve_dataset_name()
        reporting_facility.report(f"Uploading data of shape {input_df.shape} to {dataset_name}")
        dataset = self._client.datasets.upload(df=input_df, name=dataset_name)

        reporting_facility.report(f"Creating new forecasting pipeline for {dataset_name}")
        target_names = self._resolve_targets(dataset, target, targets)
        assert_no_missing_columns(dataset, target_names)

        pipeline = self._client.pipelines.create_custom(
            dataset_id=dataset.summary.id,
            name=self.config.resolve_pipeline_name(),
        )

        reporting_facility.report(f"Configuring forecasting problem for {target_names}")
        target_features = [str(cp.id) for cp in dataset.analysis if cp.name in target_names]
        pipeline = self._add_problem_specification_stage(
            pipeline=pipeline,
            dataset=dataset,
            target_features=target_features,
        )

        reporting_facility.report("Configuring stationarization")
        pipeline = self._add_stationarization_stage(pipeline)

        reporting_facility.report("Configuring feature generation")
        pipeline = self._add_feature_generation_stage(pipeline)

        reporting_facility.report("Configuring filtering")
        pipeline = self._add_filtering_stage(pipeline)

        reporting_facility.report("Configuring refinement")
        pipeline = self._add_refinement_stage(pipeline)

        self._dataset_id = dataset.summary.id
        self._pipeline_id = pipeline.summary.id

        reporting_facility.report("Running forecasting pipeline")
        self._client.pipelines.run(pipeline.summary.id, wait_for_completion=True)

        reporting_facility.report("Finalizing forecasting model")
        self._client.pipelines.lock(pipeline.summary.id)

    def predict(
        self,
        new_data: Optional[FlexibleInputData] = None,
        regressor: Optional[RegressorType] = None,
        target: Optional[str] = None,
        targets: Optional[List[str]] = None,
        reporting_callback: Optional[ReportingCallback] = None,
    ) -> ModelPrediction:
        """
        Predict the future value of target columns using the model obtained by fitting training
        data with the `.fit()` method.

        :param new_data:
            Optional new test data to use. If not provided, the outcome of this invocation will
            be the predicted future values of target columns after the last training data point
            has been processed. If provided, Horizon will feed the new data into the model and
            predict the future values of the targets after the last new data point has been
            processed. Note that this data is not persisted anywhere: it is treated as ephemeral
            data and lost after the prediction is performed.
        :param regressor:
            Regressor to use for modelling. Default is Random Forests.
        :param target:
            Name of the column to use as target. If not specified, the target(s) provided in the
            initial configuration will be used. Must belong to the set of learned targets.
            Mutually exclusive with `targets` (use one or the other but not both).
        :param targets:
            Names of the columns to use as targets. If not specified, the target(s) provided in the
            initial configuration will be used. Must be a subset of learned targets.
            Mutually exclusive with `target` (use one or the other but not both).
        :param reporting_callback:
            Function used to report progress of this method. If not provided, a default message
            will be printed to stdout using `print`. Call arguments: current step (int),
            number of total steps (int), description of the current step (str).
        :return:
            A `ModelPrediction` object that contains all predictions for all horizons (specified
            in the configuration provided in the class constructor) and all target columns.
            For more information on how to interpret results, please read the documentation
            of `ModelPrediction`.
        """
        assert (
            self._pipeline_id is not None and self._dataset_id is not None
        ), "You need to invoke HorizonForecaster.fit() first"

        self._check_environment()

        resolved_horizons = self._resolve_horizons()
        reporting_facility = ReportingFacility(
            reporting_callback=reporting_callback,
            steps_count=2 + len(resolved_horizons),
        )

        reporting_facility.report("Obtaining training information")
        training_dataset = self._client.datasets.get(self._dataset_id)
        resolved_targets = self._resolve_targets(
            dataset=training_dataset,
            target=target,
            targets=targets,
        )
        resolved_new_data = self._make_input_data_frame(new_data) if new_data is not None else None

        prediction_responses_by_horizon: Dict[int, List[PredictResponse]] = {}
        for horizon in resolved_horizons:
            reporting_facility.report(f"Predicting results for horizon = {horizon}")
            prediction_responses_by_horizon[horizon] = self._client.pipelines.predict_forecast(
                pipeline_id=self._pipeline_id,
                horizon=horizon,
                new_data=resolved_new_data,
                filter_target_names=resolved_targets,
                regressor=(
                    GeneratedRegressorType(regressor)
                    if regressor is not None
                    else GeneratedRegressorType.RANDOMFOREST
                ),
            )

        reporting_facility.report("Converting predictions into suitable format")
        assert isinstance(training_dataset.summary.cadence, (int, float))
        return ModelPrediction(
            prediction_responses_by_horizon,
            cadence_seconds=float(training_dataset.summary.cadence),
        )

    def update(
        self,
        new_data: FlexibleInputData,
        retrain: Optional[bool] = None,
        reporting_callback: Optional[ReportingCallback] = None,
    ) -> None:
        """
        Append new data onto the existing data specified during `.fit()` (or previous calls
        to this method). Appending data will not cause the model to be learnt again. However,
        subsequent invocations to `.predict()` will take into account any new data.

        :param new_data:
            This data should comply to the following requirements:
                - New data must contain exactly the same columns of the same types
                  w.r.t. existing data currently stored in the dataset;
                - ALL new data points must be at least as recent as the most recent row
                  in the dataset;
                - If the dataset has unique indices, then new data must also have unique indices;
                - New data must have the same cadence as existing data;
                - The oldest data points in the new data must be exactly 0 or 1 cadence away from
                  the most recent row in the dataset.
            If any of the conditions above is violated, the update will fail.
        :param retrain:
            If true, the model will be retrain after new_data has been uploaded.
            Retraining regenerates all features used for prediction.
        :param reporting_callback:
            Function used to report progress of this method. If not provided, a default message
            will be printed to stdout using `print`. Call arguments: current step (int),
            number of total steps (int), description of the current step (str).
        """
        assert (
            self._pipeline_id is not None and self._dataset_id is not None
        ), "You need to invoke HorizonForecaster.fit() first"

        self._check_environment()

        resolved_new_data = self._make_input_data_frame(new_data)
        reporting_facility = ReportingFacility(
            reporting_callback=reporting_callback,
            steps_count=1,
        )

        reporting_facility.report("Uploading new data to Horizon")
        self._client.datasets.append(
            dataset_id=self._dataset_id,
            df=resolved_new_data,
        )

        if retrain is True:
            self._client.pipelines.restart(pipeline_id=self._pipeline_id, wait_for_completion=True)

    def get_features(self) -> FeatureSet:
        """
        Obtain the set of generated features for the current model. Can only be called once
        `.fit` has been invoked.

        The output may omit the initial rows/timestamps from your training data, because some
        features are derived from historic data, and therefore cannot be computed for those rows.
        """
        assert (
            self._pipeline_id is not None and self._dataset_id is not None
        ), "You need to invoke HorizonForecaster.fit() first"

        horizons = self._resolve_horizons()
        materialized_data: Dict[int, pd.DataFrame] = {
            horizon: self._client.pipelines.download_features(
                pipeline_id=self._pipeline_id,
                horizon=horizon,
                include_targets=True,
            )
            for horizon in horizons
        }

        feature_graph = self._client.pipelines.get_feature_graph(self._pipeline_id)

        return FeatureSet(
            materialized_data=materialized_data,
            nodes_and_links=feature_graph,
        )

    def _add_problem_specification_stage(
        self,
        pipeline: Pipeline,
        dataset: IndividualDataset,
        target_features: List[str],
    ) -> Pipeline:
        return self._add_stage(
            pipeline=pipeline,
            stage_type=StageType.PROBLEM_SPECIFICATION,
            skip=False,
            config=ProblemSpecificationConfig(
                target_features=target_features,
                horizons=self._resolve_horizons(),
                data_split=1,
                active_columns=self.config.resolve_active_columns(dataset),
                scale_factor_multiplier=1,
                used_in_lstm=False,
            ),
        )

    def _add_stationarization_stage(
        self,
        pipeline: Pipeline,
    ) -> Pipeline:
        return self._add_stage(
            pipeline=pipeline,
            stage_type=StageType.STATIONARISATION,
            skip=self.config.stationarization is False,
            config=(
                self.config.stationarization.to_stage_config()
                if isinstance(self.config.stationarization, StationarizationConfig)
                else StationarizationConfig.default_stage_config()
            ),
        )

    def _add_feature_generation_stage(
        self,
        pipeline: Pipeline,
    ) -> Pipeline:
        return self._add_stage(
            pipeline=pipeline,
            stage_type=StageType.FEATURE_GENERATION,
            skip=self.config.feature_generation is False,
            config=(
                self.config.feature_generation.to_stage_config()
                if isinstance(self.config.feature_generation, FeatureGenerationConfig)
                else FeatureGenerationConfig.default_stage_config()
            ),
        )

    def _add_filtering_stage(
        self,
        pipeline: Pipeline,
    ) -> Pipeline:
        return self._add_stage(
            pipeline=pipeline,
            stage_type=StageType.FILTERING,
            skip=self.config.filtering is False,
            config=(
                self.config.filtering.to_stage_config()
                if isinstance(self.config.filtering, FilteringConfig)
                else FilteringConfig.default_stage_config()
            ),
        )

    def _add_refinement_stage(
        self,
        pipeline: Pipeline,
    ) -> Pipeline:
        return self._add_stage(
            pipeline=pipeline,
            stage_type=StageType.REFINEMENT,
            skip=self.config.refinement is False,
            config=(
                self.config.refinement.to_stage_config()
                if isinstance(self.config.refinement, RefinementConfig)
                else RefinementConfig.default_stage_config()
            ),
        )

    def _resolve_targets(
        self,
        dataset: IndividualDataset,
        target: Optional[str] = None,
        targets: Optional[List[str]] = None,
    ) -> List[str]:
        assert target is None or targets is None, (
            "target and targets cannot be specified together at the same time."
            "Use one or the other"
        )

        if target is not None:
            return [target]

        if targets is not None:
            return targets

        if self.config.target is not None:
            return [self.config.target]

        if self.config.targets is not None:
            return self.config.targets

        numeric_columns = [cp.name for cp in dataset.analysis if not cp.is_text]
        assert len(numeric_columns) > 0, "Expected at least one numeric column to use as target"
        return numeric_columns[0:1]

    def _resolve_horizons(self) -> List[int]:
        return self.config.horizons or [1, 2, 3, 4, 5]

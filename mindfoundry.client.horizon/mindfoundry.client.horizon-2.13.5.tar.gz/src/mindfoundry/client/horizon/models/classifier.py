from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from mindfoundry.client.horizon.client.horizon_client import Connection, HorizonClient
from mindfoundry.client.horizon.generated.models import (
    ClassificationPredictionResult,
    ClassificationSpecificationConfig,
    ClassificationSpecificationStage,
    IndividualDataset,
    Pipeline,
    StageType,
)
from mindfoundry.client.horizon.models.config import (
    ClassificationDiscoveryConfig,
    ModelConfig,
    assert_not_empty_if_provided,
)

from .base import FlexibleInputData, HorizonModel, ReportingCallback, ReportingFacility

SeriesOrArray = Union[pd.Series, np.ndarray]


@dataclass
class ClassifierConfig(ModelConfig):
    target: Optional[str] = None
    """
    Name of the column to be used as target for the classification. If not provided in the initial
    config, a target will be required when `.fit()` is invoked.
    """

    label_to_predict: Optional[str] = None
    """
    Single value belonging to the target column domain. This indicates what the classifier will
    attempt to predict. The default is the first value available in the training data.
    """

    discovery: Optional[ClassificationDiscoveryConfig] = None
    """
    Configuration for the discovery stage. This is the first stage in the model building
    process. It produces artificial features based on existing columns by exploiting a number of
    different augmentation techniques.

    This field can be a boolean that indicates whether the stage should be enabled. It can
    also be a `ClassificationDiscoveryConfig` object in case you need to define finer details about
    the stage itself.

    By default, the stage is enabled.
    """

    def validate(self) -> None:
        super().validate()

        assert_not_empty_if_provided("target", self.target)
        assert_not_empty_if_provided("label_to_predict", self.label_to_predict)

        if isinstance(self.discovery, ClassificationDiscoveryConfig):
            self.discovery.validate()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "inputs": self.inputs,
            "exclude_from_input": self.exclude_from_input,
            "target": self.target,
            "label_to_predict": self.label_to_predict,
            "discovery": (
                self.discovery.to_dict()
                if isinstance(self.discovery, ClassificationDiscoveryConfig)
                else self.discovery
            ),
        }

    @staticmethod
    def from_dict(dictionary: Dict[str, Any]) -> ClassifierConfig:
        return ClassifierConfig(
            name=dictionary["name"],
            inputs=dictionary["inputs"],
            exclude_from_input=dictionary["exclude_from_input"],
            target=dictionary["target"],
            label_to_predict=dictionary["label_to_predict"],
            discovery=(
                ClassificationDiscoveryConfig.from_dict(dictionary["discovery"])
                if isinstance(dictionary["discovery"], dict)
                else dictionary["discovery"]
            ),
        )


class HorizonClassifier(HorizonModel):
    def __init__(
        self,
        connection: Connection,
        name: Optional[str] = None,
        target: Optional[str] = None,
        inputs: Optional[List[str]] = None,
        exclude_from_input: Optional[List[str]] = None,
        label_to_predict: Optional[str] = None,
        discovery_max_features: Optional[int] = None,
        discovery_timeout_seconds: Optional[float] = None,
        discovery_excluded_columns: Optional[List[str]] = None,
        discovery_feature_generation_enabled: Optional[bool] = None,
    ):
        """
        Create a new Horizon classification model.
        :param connection:
            Connection object to the instance you are using, including api key.
        :param name:
            Name of the model. Although not necessary, it is advised to give models a
            name so that multiple models can be easily told apart. If not provided, the model will
            be given a random name.
        :param target:
            Name of the column to be used as target for the classification. If not
            provided in the initial config, a target will be required when `.fit()` is invoked.
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
        :param discovery_max_features:
            Upper bound on the number of features to generate per horizon. Default is 100.
        :param discovery_timeout_seconds:
            Maximum time allowed for running this stage. Default is `60` seconds.
        :param discovery_excluded_columns:
            List of column names to exclude from feature generation. This is the first stage
            in the model building process. It produces artificial features based on existing
            columns by exploiting a number of different augmentation techniques.
            By default, no column will be excluded.
        :param discovery_feature_generation_enabled:
            Discovery can run either with or without feature generation. In the latter case,
            only the original columns will be taken into account and Horizon will not generate
            any artificial feature. Default is True.

        """
        super().__init__(HorizonClient(connection))

        self._config = ClassifierConfig(
            name=name,
            inputs=inputs,
            exclude_from_input=exclude_from_input,
            target=target,
            label_to_predict=label_to_predict,
            discovery=ClassificationDiscoveryConfig(
                max_features=discovery_max_features,
                timeout_seconds=discovery_timeout_seconds,
                excluded_columns=discovery_excluded_columns,
                feature_generation_enabled=discovery_feature_generation_enabled,
            ),
        )

        self._config.validate()

    @property
    def config(self) -> ClassifierConfig:
        return self._config

    @staticmethod
    def load(file_path: str, connection: Connection) -> HorizonClassifier:
        """
        Load a classifier model from a file.

        :param file_path:
            Path to a json file that contains a serialized classifier model. The file must
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
        classifier = HorizonClassifier(connection)
        classifier._config = ClassifierConfig.from_dict(serialized_model["config"])
        classifier._pipeline_id = serialized_model["pipeline_id"]
        classifier._dataset_id = serialized_model["dataset_id"]
        classifier._persisted = True

        return classifier

    def save(self, file_path: str) -> None:
        """
        Save the current classifier model to a file so it can be loaded at a later time.
        The process persists the following information:
            - configuration of the classifier;
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
        x: FlexibleInputData,
        y: SeriesOrArray,
        reporting_callback: Optional[ReportingCallback] = None,
    ) -> None:
        """
        Create a classification model on the given training data. Calling this method a second time
        will delete any previously existing model and create a new one.

        :param x:
            Features to be used for classification.
            A dataframe, series or numpy array. If a series or a one-dimensional numpy array is
            given, Horizon will automatically generate a time index for the time series. We
            anyway recommend to always include a datetime column in your data to be used as
            time index with proper granularity.
        :param y:
            Class to be used for classification. Must be of the same length as x.
            Can only contain two distinct values. Any more will result in an error.
        :param reporting_callback:
            Function used to report progress of this method. If not provided, a default message
            will be printed to stdout using `print`. Call arguments: current step (int),
            number of total steps (int), description of the current step (str).
        :return:
            The method will wait for the data to be uploaded to Horizon and for the model
            building pipeline to complete. When its coroutine returns, Horizon will have
            completed data fitting.
        """
        reporting_facility = ReportingFacility(
            reporting_callback=reporting_callback,
            steps_count=7,
        )

        self._check_environment()

        reporting_facility.report("Removing pre-existing model")
        self.delete_model()

        training_data, target_name = self._make_combined_data_frame(x, y)

        dataset_name = self.config.resolve_dataset_name()
        reporting_facility.report(
            f"Uploading data of shape {training_data.shape} to {dataset_name}"
        )
        dataset = self._client.datasets.upload(df=training_data, name=dataset_name)

        reporting_facility.report(f"Creating new classification pipeline for {dataset_name}")
        pipeline = self._client.pipelines.create_custom(
            dataset_id=dataset.summary.id,
            name=self.config.resolve_pipeline_name(),
        )

        reporting_facility.report(f"Configuring classification problem for {target_name}")
        pipeline = self._add_problem_specification_stage(pipeline, dataset, target_name)

        reporting_facility.report("Configuring feature discovery")
        pipeline = self._add_discovery_stage(pipeline)

        self._dataset_id = dataset.summary.id
        self._pipeline_id = pipeline.summary.id

        reporting_facility.report("Running classification pipeline")
        self._client.pipelines.run(pipeline.summary.id, wait_for_completion=True)

        reporting_facility.report("Finalizing classification model")
        self._client.pipelines.lock(pipeline.summary.id)

    def predict(
        self,
        x: FlexibleInputData,
        reporting_callback: Optional[ReportingCallback] = None,
    ) -> ClassificationPredictionResult:
        """
        Predict the value of target columns using the model obtained by fitting training
        data with the `.fit()` method.

        :param x:
            Data to use for the prediction. Must have the same columns as the training data.
            We recommend that you do not skip any date/times, i.e. the first date/time should be
            immediately after the last date/time in the training data. This is because some
            architectures construct features using historic data, so using non-contiguous data may
            result in unstable or unexpected predictions and performance.
        :param reporting_callback:
            Function used to report progress of this method. If not provided, a default message
            will be printed to stdout using `print`. Call arguments: current step (int),
            number of total steps (int), description of the current step (str).
        :return:
            A `ClassificationPredictionResult` object that contains all predictions for all rows.
        """
        assert (
            self._pipeline_id is not None and self._dataset_id is not None
        ), "You need to invoke HorizonClassifier.fit() first"

        self._check_environment()

        reporting_facility = ReportingFacility(
            reporting_callback=reporting_callback,
            steps_count=2,
        )

        reporting_facility.report("Retrieving target label")
        pipeline = self._client.pipelines.get(self._pipeline_id)
        spec_stage = pipeline.stages[0]
        if not isinstance(spec_stage, ClassificationSpecificationStage):
            raise RuntimeError(
                f"Expected first stage of pipeline to be Classification Specification "
                f"but was {spec_stage.type}"
            )
        target_label = spec_stage.config.label_to_predict

        reporting_facility.report("Predicting results")
        prediction_result = self._client.pipelines.predict_classification(
            pipeline_id=self._pipeline_id,
            data=self._make_input_data_frame(x),
            target_label=target_label,
        )
        return prediction_result

    def update(
        self,
        new_x: FlexibleInputData,
        new_y: SeriesOrArray,
        reporting_callback: Optional[ReportingCallback] = None,
    ) -> None:
        """
        Append new data onto the existing data specified during `.fit()` (or previous calls
        to this method). Appending data will not cause the model to be learnt again. However,
        subsequent invocations to `.predict()` will take into account any new data.

        :param new_x:
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
        :param reporting_callback:
            Function used to report progress of this method. If not provided, a default message
            will be printed to stdout using `print`. Call arguments: current step (int),
            number of total steps (int), description of the current step (str).
        """
        assert (
            self._pipeline_id is not None and self._dataset_id is not None
        ), "You need to invoke HorizonClassifier.fit() first"

        self._check_environment()

        resolved_new_data, _ = self._make_combined_data_frame(new_x, new_y)

        reporting_facility = ReportingFacility(
            reporting_callback=reporting_callback,
            steps_count=1,
        )

        reporting_facility.report("Uploading new data to Horizon")
        self._client.datasets.append(
            dataset_id=self._dataset_id,
            df=resolved_new_data,
        )

    def _add_problem_specification_stage(
        self,
        pipeline: Pipeline,
        dataset: IndividualDataset,
        target_name: str,
    ) -> Pipeline:
        matching_target_ids = [cp.id for cp in dataset.analysis if cp.name == target_name]
        assert len(matching_target_ids) == 1, "Dataset must contain one and only one target column"

        if self.config.label_to_predict is not None:
            label_to_predict = self.config.label_to_predict
        else:
            target = next(cp for cp in dataset.analysis if cp.name == target_name)
            assert isinstance(target.binary_labels, list)
            label_to_predict = target.binary_labels[0]

        return self._add_stage(
            pipeline=pipeline,
            stage_type=StageType.CLASSIFICATION_SPECIFICATION,
            skip=False,
            config=ClassificationSpecificationConfig(
                target_id=str(matching_target_ids[0]),
                last_train_timestamp_millisec=dataset.summary.last_index_timestamp,
                label_to_predict=label_to_predict,
                active_columns=self.config.resolve_active_columns(dataset),
            ),
        )

    def _add_discovery_stage(self, pipeline: Pipeline) -> Pipeline:
        return self._add_stage(
            pipeline=pipeline,
            stage_type=StageType.CLASSIFICATION_DISCOVERY,
            skip=False,
            config=(
                self.config.discovery.to_stage_config()
                if self.config.discovery is not None
                else ClassificationDiscoveryConfig.default_stage_config()
            ),
        )

    def _make_combined_data_frame(
        self, x: FlexibleInputData, y: SeriesOrArray
    ) -> Tuple[pd.DataFrame, str]:
        training_data = self._make_input_data_frame(x).copy()  # Don't mutate the original X!
        target_name = self._find_name_for_target_column(training_data, y)
        training_data[target_name] = y
        return training_data, target_name

    def _find_name_for_target_column(self, training_data: pd.DataFrame, y: SeriesOrArray) -> str:
        if self.config.target:
            return self.config.target

        if isinstance(y, pd.Series) and y.name:
            return str(y.name)

        return next(
            f"target_{i}" for i in range(0, 100) if f"target_{i}" not in set(training_data.columns)
        )

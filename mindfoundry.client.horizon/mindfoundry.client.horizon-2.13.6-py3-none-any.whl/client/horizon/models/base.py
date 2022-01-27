import abc
from types import TracebackType
from typing import Any, Callable, Dict, List, Optional, Type, Union

import numpy as np
import pandas as pd

from mindfoundry.client.horizon.client.horizon_client import HorizonClient
from mindfoundry.client.horizon.generated.models import (
    NodeAndLink,
    Pipeline,
    PredictResponse,
    StageSpecification,
    StageType,
)

ReportingCallback = Callable[[int, int, str], None]

FlexibleInputData = Union[pd.DataFrame, pd.Series, np.ndarray]


class ReportingFacility:
    def __init__(self, reporting_callback: Optional[ReportingCallback], steps_count: int):
        self._reporting_callback = reporting_callback or self._default_reporting_callback
        self._steps_count = steps_count
        self._current_step = 1

    def report(self, message: str) -> None:
        self._reporting_callback(self._current_step, self._steps_count, message)
        self._current_step = self._current_step + 1

    @staticmethod
    def _default_reporting_callback(current_step: int, max_steps: int, info: str) -> None:
        print(f"[Step {current_step}/{max_steps}]: {info}")


class HorizonModel(abc.ABC):
    def __init__(self, client: HorizonClient):
        self._client = client
        self._persisted = False
        self._dataset_id: Optional[int] = None
        self._pipeline_id: Optional[int] = None
        self._show_notebook_warning = _is_running_in_notebook()

    def __del__(self) -> None:
        if self._persisted is False:
            self.delete_model()

    def __enter__(self) -> "HorizonModel":
        self._show_notebook_warning = False
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.__del__()

    def _add_stage(
        self,
        pipeline: Pipeline,
        stage_type: StageType,
        skip: bool,
        config: Any,
    ) -> Pipeline:
        if skip:
            return pipeline
        else:
            return self._client.pipelines.add_stage(
                pipeline_id=pipeline.summary.id,
                spec=StageSpecification(
                    stage_type=stage_type,
                    config=config,
                ),
            )

    def _check_environment(self) -> None:
        if self._show_notebook_warning:
            print(
                "[WARN] Running the Horizon client in a Jupyter notebook may impede its "
                "natural cleanup process. To ensure the best experience, please enclose your "
                "model in a with clause. "
                "\n\n"
                f"with {self.__class__.__name__}(...) as my_model:\n"
                "    my_model.fit(data)\n"
                "    # ... some more code\n"
            )
            self._show_notebook_warning = False

    def delete_model(self) -> None:
        """
        Delete the current model from Horizon. All training data will be deleted.
        All generated features will be deleted as well. Has no effect if `.fit()`
        was never called.
        """
        if self._pipeline_id is not None:
            try:
                self._client.pipelines.unlock(self._pipeline_id)
                self._client.pipelines.delete(self._pipeline_id)
            finally:
                self._pipeline_id = None

        if self._dataset_id is not None:
            try:
                self._client.datasets.delete(self._dataset_id)
            finally:
                self._dataset_id = None

    @staticmethod
    def _make_input_data_frame(training_data: FlexibleInputData) -> pd.DataFrame:
        if isinstance(training_data, pd.DataFrame):
            return training_data

        if isinstance(training_data, pd.Series):
            return pd.DataFrame(data=[training_data])

        if isinstance(training_data, np.ndarray):
            return pd.DataFrame(data=training_data)

        raise ValueError("Training data format not supported")


class ModelPrediction:
    """ Contains all predictions obtained by calling `.predict()` on an Horizon model. """

    def __init__(
        self,
        prediction_responses_by_horizon: Dict[int, List[PredictResponse]],
        cadence_seconds: float,
        warnings: Optional[List[str]] = None,
    ):
        sorted_horizons = sorted(prediction_responses_by_horizon.keys())
        target_names = {
            r.target_original_column_name
            for prediction_responses in prediction_responses_by_horizon.values()
            for r in prediction_responses
        }

        arbitrary_horizon = sorted_horizons[0]
        arbitrary_response = prediction_responses_by_horizon[arbitrary_horizon][0]
        index_dtype = arbitrary_response.predictions.mean.index_dtype
        assert index_dtype == "datetime64[ns]", f"Datetime index not supported: {index_dtype}"

        data: Dict[str, pd.Series] = {}

        for target_name in target_names:
            time_index = [
                r.predictions.mean.index[0] + horizon * cadence_seconds * 1e9
                for horizon in sorted_horizons
                for r in prediction_responses_by_horizon[horizon]
                if r.target_original_column_name == target_name
            ]
            mean = [
                r.predictions.mean.data[0]
                for horizon in sorted_horizons
                for r in prediction_responses_by_horizon[horizon]
                if r.target_original_column_name == target_name
            ]
            lower_bound = [
                r.predictions.cb_low.data[0]
                for horizon in sorted_horizons
                for r in prediction_responses_by_horizon[horizon]
                if r.target_original_column_name == target_name
            ]
            higher_bound = [
                r.predictions.cb_high.data[0]
                for horizon in sorted_horizons
                for r in prediction_responses_by_horizon[horizon]
                if r.target_original_column_name == target_name
            ]

            time_index = pd.DatetimeIndex(data=time_index, dtype=index_dtype)
            data[f"{target_name} (mean)"] = pd.Series(data=mean, index=time_index)
            data[f"{target_name} (lower bound)"] = pd.Series(data=lower_bound, index=time_index)
            data[f"{target_name} (higher bound)"] = pd.Series(data=higher_bound, index=time_index)

        self._df = pd.DataFrame(data=data)
        self._warnings = warnings or []

    def as_df(self) -> pd.DataFrame:
        """
        Return predictions formatted as a Pandas data frame.
        :return:
            For forecasting, the format of the returned data frame is the following:
              - the number of rows is the same as the number of requested horizons. Each row
                refers to a prediction for a specific horizon in the future.
              - the index of the data frame is a DatetimeIndex. The date contained in each row
                refers to the date a given prediction is bound to occur.
              - each requested target column produces three output columns in the resulting data
                frame: one for the mean, one for the lower confidence bound and one for the
                higher confidence bound. If the target name is X, then these columns are
                respectively named "X (mean)", "X (lower bound)" and "X (higher bound)".
        """
        return self._df

    @property
    def values(self) -> np.ndarray:  # type: ignore
        """
        Return the raw prediction values of this set of prediction as a numpy array.
        Same as calling `.as_df().values`, so please consult the documentation of `.as_df()`
        to know about the format and arrangement of rows and columns.
        """
        values: np.ndarray = self._df.values  # type: ignore
        return values

    @property
    def warnings(self) -> List[str]:
        """ List any error that occurred during prediction. """
        return self._warnings


class FeatureExplanation:
    """ Concise summary that explains the origin of a Horizon-generated feature. """

    feature_name: str
    """ Name of the generated feature. """

    feature_id: str
    """ Id of the generated feature. """

    explanation: str
    """
    Natural language explanation of how this feature was generated and why it may be
    relevant for prediction.
    """

    formula: str
    """
    Human-readable pseudo-code representation of the transformer heuristic Horizon used
    to generate this feature.
    """

    horizon: int
    """
    Time-steps horizon to which the feature refers to. Some features may be more relevant
    for one horizon rather than another.
    """

    pearson_correlation_with_target: float
    """ Pearson correlation of the generated feature with the original target. """

    def __init__(self, node_and_link: NodeAndLink):
        self.feature_name = node_and_link.name
        self.feature_id = node_and_link.feature_id
        self.horizon = node_and_link.horizon
        self.explanation = node_and_link.transform.explanation
        self.pearson_correlation_with_target = node_and_link.pearson_correlation_with_target

        if node_and_link.transform.transform_category == "fake":
            self.formula = node_and_link.original_column_names[0]
        else:
            formula_params = node_and_link.original_column_names
            extra_params = {
                name: value
                for name, value in node_and_link.transform.params.additional_properties.items()
                if name not in {"n_parents", "name"}
            }

            for name, value in extra_params.items():
                formula_params.append(f"{name}={value}")

            self.formula = (
                f"{node_and_link.transform.transform_category}" f"({', '.join(formula_params)})"
            )

    def __str__(self) -> str:
        return self.formula


class FeatureSet:
    def __init__(
        self,
        materialized_data: Dict[int, pd.DataFrame],
        nodes_and_links: List[NodeAndLink],
    ):
        self._materialized_data = materialized_data
        self._explanations = [
            FeatureExplanation(node_and_link) for node_and_link in nodes_and_links
        ]

    def for_horizon(self, horizon: int) -> pd.DataFrame:
        """
        Return a dataframe containing the numeric values of each generated feature
        for the given horizon.

        :return:
            The returned dataframe will contain more columns than the original data.
            Each column is a new feature that Horizon found to have high predictive power.
            It may also contain less rows, since some features require aggregating more than
            one time steps. Original targets are included as well; beware they may appear as
            artificially generated features, created by stationarization.
        """
        return self._materialized_data[horizon]

    @property
    def explanations(self) -> List[FeatureExplanation]:
        """ Return a collection of feature explanations. """
        return self._explanations


def _is_running_in_notebook() -> bool:
    try:
        shell_type = get_ipython().__class__.__name__  # type: ignore
        return bool(shell_type == "ZMQInteractiveShell")
    except NameError:
        return False

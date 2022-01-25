#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import copy
from typing import List, Union

from ibm_watson_machine_learning.preprocessing import DataJoinGraph
from ibm_watson_machine_learning.utils.autoai.enums import (
    TShirtSize, ClassificationAlgorithms, RegressionAlgorithms, ForecastingAlgorithms, PredictionType, Metrics, \
    Transformers, DataConnectionTypes, PipelineTypes, PositiveLabelClass, ClassificationAlgorithmsCP4D,
    RegressionAlgorithmsCP4D, ForecastingAlgorithmsCP4D, SamplingTypes, ImputationStrategy)
from ibm_watson_machine_learning.utils.autoai.errors import LocalInstanceButRemoteParameter, MissingPositiveLabel, \
    NonForecastPredictionColumnMissing, ForecastPredictionColumnsMissing, ForecastingCannotBeRunAsLocalScenario, \
    TSNotSupported, ParamOutOfRange, ImputationListNotSupported
from ibm_watson_machine_learning.utils.autoai.utils import check_dependencies_versions, \
    validate_additional_params_for_optimizer, validate_optimizer_enum_values, \
    translate_imputation_string_strategy_to_enum
from ibm_watson_machine_learning.workspace import WorkSpace
from .engines import WMLEngine
from .optimizers import LocalAutoPipelines, RemoteAutoPipelines
from .runs import AutoPipelinesRuns, LocalAutoPipelinesRuns
from ..base_experiment.base_experiment import BaseExperiment

__all__ = [
    "AutoAI"
]


class AutoAI(BaseExperiment):
    """
    AutoAI class for pipeline models optimization automation.

    Parameters
    ----------
    wml_credentials: dictionary, required
        Credentials to Watson Machine Learning instance.

    project_id: str, optional
        ID of the Watson Studio project.

    space_id: str, optional
        ID of the Watson Studio Space.

    verify: Union[bool, str], optional
        User can pass verify the path to a CA_BUNDLE file or directory with certificates of trusted CAs.
        If set to True, default path to truststore will be taken.
        If set to False, no verification will be made.

    Example
    -------
    >>> from ibm_watson_machine_learning.experiment import AutoAI
    >>>
    >>> experiment = AutoAI(
    >>>        wml_credentials={
    >>>              "apikey": "...",
    >>>              "iam_apikey_description": "...",
    >>>              "iam_apikey_name": "...",
    >>>              "iam_role_crn": "...",
    >>>              "iam_serviceid_crn": "...",
    >>>              "instance_id": "...",
    >>>              "url": "https://us-south.ml.cloud.ibm.com"
    >>>            },
    >>>         project_id="...",
    >>>         space_id="...")
    """
    # note: initialization of AutoAI enums as class properties

    # note: Enums with estimators can be overwritten  in _init based on environment type (CPD or Cloud)
    ClassificationAlgorithms = ClassificationAlgorithms
    RegressionAlgorithms = RegressionAlgorithms
    ForecastingAlgorithms = ForecastingAlgorithms
    # end note
    TShirtSize = TShirtSize
    PredictionType = PredictionType
    Metrics = Metrics
    Transformers = Transformers
    DataConnectionTypes = DataConnectionTypes
    PipelineTypes = PipelineTypes

    def __init__(self,
                 wml_credentials: Union[dict, 'WorkSpace'] = None,
                 project_id: str = None,
                 space_id: str = None,
                 verify=None) -> None:
        # note: as workspace is not clear enough to understand, there is a possibility to use pure
        # wml credentials with project and space IDs, but in addition we
        # leave a possibility to use a previous WorkSpace implementation, it could be passed as a first argument
        if wml_credentials is None:
            self._workspace = None
            self.runs = LocalAutoPipelinesRuns()

        else:
            if isinstance(wml_credentials, WorkSpace):
                self._workspace = wml_credentials
            else:
                self._workspace = WorkSpace(wml_credentials=wml_credentials.copy(),
                                            project_id=project_id,
                                            space_id=space_id,
                                            verify=verify)

            self.project_id = self._workspace.project_id
            self.space_id = self._workspace.space_id
            self.runs = AutoPipelinesRuns(engine=WMLEngine(self._workspace))
            self.runs._workspace = self._workspace

        self._init_estimator_enums()

        self._20_class_limit_removal_test = False
        # --- end note

    def runs(self, *, filter: str) -> Union['AutoPipelinesRuns', 'LocalAutoPipelinesRuns']:
        """
        Get the historical runs but with WML Pipeline name filter (for remote scenario).
        Get the historical runs but with experiment name filter (for local scenario).

        Parameters
        ----------
        filter: str, required
            WML Pipeline name to filter the historical runs.
            or experiment name to filter the local historical runs.

        Returns
        -------
        AutoPipelinesRuns or LocalAutoPipelinesRuns

        Example
        -------
        >>> from ibm_watson_machine_learning.experiment import AutoAI
        >>> experiment = AutoAI(...)
        >>>
        >>> experiment.runs(filter='Test').list()
        """

        if self._workspace is None:
            return LocalAutoPipelinesRuns(filter=filter)

        else:
            return AutoPipelinesRuns(engine=WMLEngine(self._workspace.wml_client), filter=filter)

    def optimizer(self,
                  name: str,
                  *,
                  prediction_type: 'PredictionType',
                  prediction_column: str = None,
                  prediction_columns: List[str] = None,
                  timestamp_column_name: str = None,
                  scoring: 'Metrics' = None,
                  desc: str = None,
                  test_size: float = None, # deprecated
                  holdout_size: float = 0.1,
                  max_number_of_estimators: int = 2,
                  train_sample_rows_test_size: float = None,
                  include_only_estimators: List[Union['ClassificationAlgorithms', 'RegressionAlgorithms',
                                                      'ForecastingAlgorithms']] = None,
                  daub_include_only_estimators: List[Union['ClassificationAlgorithms', 'RegressionAlgorithms']] = None, # deprecated
                  backtest_num: int = None,
                  lookback_window: int = None,
                  forecast_window: int = None,
                  backtest_gap_length: int = None,
                  cognito_transform_names: List['Transformers'] = None,
                  data_join_graph: 'DataJoinGraph' = None,
                  csv_separator: Union[List[str], str] = ',',
                  excel_sheet: Union[str, int] = 0,
                  encoding: str = 'utf-8',
                  positive_label: str = None,
                  data_join_only: bool = False,
                  drop_duplicates: bool = True,
                  text_processing: bool = None,
                  word2vec_feature_number: int = None,
                  daub_give_priority_to_runtime: float = None,
                  fairness_info: dict = None,
                  # sampling_type: 'SamplingTypes' = None, #TODO: Uncomment to add sampling_type support
                  n_parallel_data_connections: int = None,
                  categorical_imputation_strategy: ImputationStrategy = None,
                  numerical_imputation_strategy: ImputationStrategy = None,
                  numerical_imputation_value: float = None,
                  imputation_threshold: float = None,
                  retrain_on_holdout: int = True,
                  **kwargs) -> Union['RemoteAutoPipelines', 'LocalAutoPipelines']:
        """
        Initialize an AutoAi optimizer.

        Parameters
        ----------
        name: str, required
            Name for the AutoPipelines

        prediction_type: PredictionType, required
            Type of the prediction.

        prediction_column: str, required for multiclass, binary and regression prediction types
            Name of the target/label column

        prediction_columns: List[str], required for forecasting prediction type
            Names of the target/label columns.

        timestamp_column_name: str, optional, used only for forecasting prediction type
            Name of timestamp column for time series forecasting.

        scoring: Metrics, optional
            Type of the metric to optimize with. Not used for forecasting.

        desc: str, optional
            Description

        test_size: deprecated
            Use `holdout_size` instead.

        holdout_size: float, optional
            Percentage of the entire dataset to leave as a holdout. Default 0.1

        max_number_of_estimators: int, optional
            Maximum number (top-K ranked by DAUB model selection) of the selected algorithm, or estimator types,
            for example LGBMClassifierEstimator, XGBoostClassifierEstimator, or LogisticRegressionEstimator
            to use in pipeline composition.  The default is 2, where only the highest ranked by model
            selection algorithm type is used. (min 1, max 4)

        train_sample_rows_test_size: float, optional
            Training data sampling percentage

        daub_include_only_estimators: deprecated
            Use `include_only_estimators` instead.

        include_only_estimators: List[Union['ClassificationAlgorithms', 'RegressionAlgorithms', 'ForecastingAlgorithms']], optional
            List of estimators to include in computation process.
            See: AutoAI.ClassificationAlgorithms, AutoAI.RegressionAlgorithms or AutoAI.ForecastingAlgorithms

        backtest_num: int, optional
            Used for forecasting prediction type. Configure number of backtests. Default value: 4
            Value from range [0, 20]

        lookback_window: int, optional
            Used for forecasting prediction type. Configure length of lookback window. Default value: 10
            If set to -1 lookback window will be auto-detected

        forecast_window: int, optional
            Used for forecasting prediction type. Configure length of forecast window. Default value: 1
            Value from range [1, 60]

        backtest_gap_length: int, optional
            Used for forecasting prediction type. Configure gap between backtests. Default value: 0
            Value from range [0, data length / 4]

        cognito_transform_names: List['Transformers'], optional
            List of transformers to include in feature enginnering computation process.
            See: AutoAI.Transformers

        csv_separator: Union[List[str], str], optional
            The separator, or list of separators to try for separating
            columns in a CSV file.  Not used if the file_name is not a CSV file.
            Default is ','.

        excel_sheet: Union[str, int], optional
            Name or number of the excel sheet to use. Only use when xlsx file is an input.
            Default is 0.

        encoding: str, optional
            Encoding type for CSV training file.

        positive_label: str, optional
            The positive class to report when binary classification.
            When multiclass or regression, this will be ignored.

        t_shirt_size: TShirtSize, optional
            The size of the remote AutoAI POD instance (computing resources). Only applicable to a remote scenario.
            See: AutoAI.TShirtSize

        data_join_graph: DataJoinGraph, optional
            A graph object with definition of join structure for multiple input data sources.
            Data preprocess step for multiple files.

        data_join_only: bool, optional
            If True only preprocessing will be executed.

        drop_duplicates: bool, optional
            If True duplicated rows in data will be removed before further processing. Default is True.

        text_processing: bool, optional
            If True text processing will be enabled. Default is True. Applicable only on Cloud.

        word2vec_feature_number: int, optional
            Number of features which will be generated from text column. Will be applied only if `text_processing`
            is True. If `None` the default value will be taken.

        daub_give_priority_to_runtime: float, optional
            The importance of run time over score for pipelines ranking. Can take values between 0 and 5.
            If set to 0.0 only score is used. If set to 1 equally score and runtime are used.
            If set to value higher than 1 the runtime gets higher importance over score.

        fairness_info: dict, optional
            Dictionary that  specifies metadata needed for measuring fairness. It contains three key values:
            favorable_labels, unfavorable_labels and protected_attributes. The favorable_labels attribute indicates that
            when the class column contains one of the value from list, that is considered a positive outcome.
            The unfavorable_labels is oposite to the favorable_labels and is obigatory for regression learning type.
            A protected attribute is a list of features that partition the population into groups whose outcome should
            have parity, if protected attribute is empty list then automatic detection of protected attributes will be run.
            If passed fairness metric will be calculated.

        n_parallel_data_connections: int, optional
            Number of maximum parallel connection to data source.
            Supported only for IBM Cloud Pak® for Data 4.0.1 and above.

        categorical_imputation_strategy: ImputationStrategy, optional
            Missing values imputation strategy for categorical columns.

            Possible values (only non-forecasting scenario):
            - ImputationStrategy.MEAN
            - ImputationStrategy.MEDIAN
            - ImputationStrategy.MOST_FREQUENT (default)


        numerical_imputation_strategy: ImputationStrategy, optional
            Missing values imputation strategy for numerical columns.

            Possible values (non-forecasting scenario):
            - ImputationStrategy.MEAN
            - ImputationStrategy.MEDIAN (default)
            - ImputationStrategy.MOST_FREQUENT

            Possible values (forecasting scenario):
            - ImputationStrategy.MEAN
            - ImputationStrategy.MEDIAN
            - ImputationStrategy.BEST_OF_DEFAULT_IMPUTERS (default)
            - ImputationStrategy.VALUE
            - ImputationStrategy.FLATTEN_ITERATIVE
            - ImputationStrategy.LINEAR
            - ImputationStrategy.CUBIC
            - ImputationStrategy.PREVIOUS
            - ImputationStrategy.NEXT
            - ImputationStrategy.NO_IMPUTATION


        numerical_imputation_value: float, optional
            Value for filling missing values if numerical_imputation_strategy is set to ImputationStrategy.VALUE.
            For forecasting only.

        imputation_threshold: float, optional
            Maximum threshold of missing values imputation.
            For forecasting only.

        retrain_on_holdout: bool, optional
            If True final pipelines will be train also on holdout data.

        Returns
        -------
        RemoteAutoPipelines or LocalAutoPipelines, depends on how you initialize the AutoAI object.

        Example
        -------
        >>> from ibm_watson_machine_learning.experiment import AutoAI
        >>> experiment = AutoAI(...)
        >>>
        >>> fairness_info = {
        >>>            "protected_attributes": [
        >>>                {"feature": "Sex", "reference_group": ['male'], "monitored_group": ['female']},
        >>>                {"feature": "Age", "reference_group": [[50,60]], "monitored_group": [[18, 49]]}
        >>>            ],
        >>>            "favorable_labels": ["No Risk"],
        >>>            "unfavorable_labels": ["Risk"],
        >>>            }
        >>>
        >>> optimizer = experiment.optimizer(
        >>>        name="name of the optimizer.",
        >>>        prediction_type=AutoAI.PredictionType.BINARY,
        >>>        prediction_column="y",
        >>>        scoring=AutoAI.Metrics.ROC_AUC_SCORE,
        >>>        desc="Some description.",
        >>>        holdout_size=0.1,
        >>>        max_num_daub_ensembles=1,
        >>>        fairness_info= fairness_info,
        >>>        cognito_transform_names=[AutoAI.Transformers.SUM,AutoAI.Transformers.MAX],
        >>>        train_sample_rows_test_size=1,
        >>>        include_only_estimators=[AutoAI.ClassificationAlgorithms.LGBM, AutoAI.ClassificationAlgorithms.XGB],
        >>>        t_shirt_size=AutoAI.TShirtSize.L
        >>>    )
        >>>
        >>> optimizer = experiment.optimizer(
        >>>        name="name of the optimizer.",
        >>>        prediction_type=AutoAI.PredictionType.MULTICLASS,
        >>>        prediction_column="y",
        >>>        scoring=AutoAI.Metrics.ROC_AUC_SCORE,
        >>>        desc="Some description.",
        >>>    )
        """

        # TODO: Pass the sampling_type doc description, when adding support for that
        # sampling_type: str, optional
        #     Type of sampling data for training. One of SamplingTypes enum values.
        #     Default is SamplingTypes.FIRST_N_RECORDS.
        #     Supported only for IBM Cloud Pak® for Data 4.0.1 and above.

        if prediction_type == PredictionType.FORECASTING and self._workspace.wml_client.ICP and \
                (self._workspace.wml_client.wml_credentials['version'].startswith('2.5') or \
                        self._workspace.wml_client.wml_credentials['version'].startswith('3.0') or \
                        self._workspace.wml_client.wml_credentials['version'].startswith('3.5')):
            raise TSNotSupported()

        if prediction_type == PredictionType.FORECASTING:
            if not numerical_imputation_strategy and type(numerical_imputation_strategy) is not list:
                numerical_imputation_strategy = ImputationStrategy.BEST_OF_DEFAULT_IMPUTERS
            elif not numerical_imputation_strategy and type(numerical_imputation_strategy) is list:
                numerical_imputation_strategy = ImputationStrategy.NO_IMPUTATION

            if prediction_column is not None or prediction_columns is None:
                raise ForecastPredictionColumnsMissing()
        else:
            if prediction_column is None or prediction_columns is not None:
                raise NonForecastPredictionColumnMissing(prediction_type)

        if test_size:
            print('Note: Using `test_size` is deprecated. Use `holdout_size` instead.')
            if not holdout_size:
                holdout_size = test_size
            test_size = None

        if daub_include_only_estimators:
            print('Note: Using `daub_include_only_estimators` is deprecated. Use `include_only_estimators` instead.')
            if not include_only_estimators:
                include_only_estimators = daub_include_only_estimators
            daub_include_only_estimators = None

        def translate_str_imputation_param(x):
            if type(x) is list and prediction_type != PredictionType.FORECASTING:
                raise ImputationListNotSupported()

            if type(x) == str or (type(x) == list and type(x[0]) == str):
                return translate_imputation_string_strategy_to_enum(x, prediction_type)
            else:
                return x

        categorical_imputation_strategy = translate_str_imputation_param(categorical_imputation_strategy)
        numerical_imputation_strategy = translate_str_imputation_param(numerical_imputation_strategy)

        validate_optimizer_enum_values(
            prediction_type=prediction_type,
            daub_include_only_estimators=daub_include_only_estimators,
            include_only_estimators=include_only_estimators,
            cognito_transform_names=cognito_transform_names,
            imputation_strategies=[x for y in list(filter(None, [categorical_imputation_strategy, numerical_imputation_strategy])) for x in (y if type(y) is list else [y])],
            scoring=scoring,
            t_shirt_size=kwargs.get("t_shirt_size", TShirtSize.M),
            is_cpd=self._workspace.wml_client.ICP
        )

        if daub_give_priority_to_runtime is not None:
            if daub_give_priority_to_runtime < 0.0 or daub_give_priority_to_runtime > 5.0:
                raise ParamOutOfRange('daub_give_priority_to_runtime', daub_give_priority_to_runtime, 0.0, 5.0)

        if data_join_graph:
            data_join_graph.problem_type = prediction_type
            data_join_graph.target_column = prediction_column

        if (prediction_type == PredictionType.BINARY and scoring in vars(PositiveLabelClass).values()
                and positive_label is None):
            raise MissingPositiveLabel(scoring, reason=f"\"{scoring}\" needs a \"positive_label\" "
                                                       f"parameter to be defined when used with binary classification.")

        if self._workspace is None and kwargs.get('t_shirt_size'):
            raise LocalInstanceButRemoteParameter(
                "t_shirt_size",
                reason="During LocalOptimizer initialization, \"t_shirt_size\" parameter was provided. "
                       "\"t_shirt_size\" parameter is only applicable to the RemoteOptimizer instance."
            )
        elif self._workspace is None:
            if prediction_type == PredictionType.FORECASTING:
                raise ForecastingCannotBeRunAsLocalScenario()

            reduced_kwargs = copy.copy(kwargs)

            for n in ['_force_local_scenario']:
                if n in reduced_kwargs:
                    del reduced_kwargs[n]

            validate_additional_params_for_optimizer(reduced_kwargs)

            return LocalAutoPipelines(
                name=name,
                prediction_type='classification' if prediction_type in ['binary', 'multiclass'] else prediction_type,
                prediction_column=prediction_column,
                scoring=scoring,
                desc=desc,
                holdout_size=holdout_size,
                max_num_daub_ensembles=max_number_of_estimators,
                train_sample_rows_test_size=train_sample_rows_test_size,
                include_only_estimators=include_only_estimators,
                cognito_transform_names=cognito_transform_names,
                positive_label=positive_label,
                _force_local_scenario=kwargs.get('_force_local_scenario', False),
                **reduced_kwargs
            )

        else:
            reduced_kwargs = copy.copy(kwargs)

            for n in ['t_shirt_size', 'notebooks', 'autoai_pod_version', 'obm_pod_version']:
                if n in reduced_kwargs:
                    del reduced_kwargs[n]

            validate_additional_params_for_optimizer(reduced_kwargs)

            engine = WMLEngine(self._workspace)

            if self._20_class_limit_removal_test:
                engine._20_class_limit_removal_test = True

            optimizer = RemoteAutoPipelines(
                name=name,
                prediction_type=prediction_type,
                prediction_column=prediction_column,
                prediction_columns=prediction_columns,
                timestamp_column_name=timestamp_column_name,
                scoring=scoring,
                desc=desc,
                holdout_size=holdout_size,
                max_num_daub_ensembles=max_number_of_estimators,
                t_shirt_size=self._workspace.restrict_pod_size(t_shirt_size=kwargs.get(
                    't_shirt_size', TShirtSize.M if self._workspace.wml_client.ICP else TShirtSize.L)
                ),
                train_sample_rows_test_size=train_sample_rows_test_size,
                include_only_estimators=include_only_estimators,
                backtest_num=backtest_num,
                lookback_window=lookback_window,
                forecast_window=forecast_window,
                backtest_gap_length=backtest_gap_length,
                cognito_transform_names=cognito_transform_names,
                data_join_graph=data_join_graph,
                drop_duplicates=drop_duplicates,
                text_processing=text_processing,
                word2vec_feature_number=word2vec_feature_number,
                csv_separator=csv_separator,
                excel_sheet=excel_sheet,
                encoding=encoding,
                positive_label=positive_label,
                data_join_only=data_join_only,
                engine=engine,
                daub_give_priority_to_runtime=daub_give_priority_to_runtime,
                notebooks=kwargs.get('notebooks', True),
                autoai_pod_version=kwargs.get('autoai_pod_version', None),
                obm_pod_version=kwargs.get('obm_pod_version', None),
                fairness_info=fairness_info,
                # sampling_type=sampling_type, #TODO: Uncomment to add sampling_type support
                n_parallel_data_connections=n_parallel_data_connections,
                categorical_imputation_strategy=categorical_imputation_strategy,
                numerical_imputation_strategy=numerical_imputation_strategy,
                numerical_imputation_value=numerical_imputation_value,
                imputation_threshold=imputation_threshold,
                retrain_on_holdout=retrain_on_holdout,
                **reduced_kwargs
            )
            optimizer._workspace = self._workspace
            return optimizer

    def _init_estimator_enums(self):
        if self._workspace and self._workspace.wml_client.ICP:
            self.ClassificationAlgorithms = ClassificationAlgorithmsCP4D
            self.RegressionAlgorithms = RegressionAlgorithmsCP4D
            self.ForecastingAlgorithms = ForecastingAlgorithmsCP4D
        else:
            self.ClassificationAlgorithms = ClassificationAlgorithms
            self.RegressionAlgorithms = RegressionAlgorithms
            self.ForecastingAlgorithms = ForecastingAlgorithms

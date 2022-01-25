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

import os

from copy import deepcopy
from typing import TYPE_CHECKING, List, Union
from warnings import warn
from contextlib import redirect_stdout

from numpy import ndarray
from pandas import DataFrame

from ibm_watson_machine_learning.helpers.connections import (
    DataConnection, S3Location, FSLocation, AssetLocation, WSDAssetLocation, ContainerLocation)
from ibm_watson_machine_learning.preprocessing import DataJoinPipeline
from ibm_watson_machine_learning.utils.autoai.enums import (
    RunStateTypes, PipelineTypes, TShirtSize, ClassificationAlgorithms, RegressionAlgorithms, DataConnectionTypes)
from ibm_watson_machine_learning.utils.autoai.errors import (
    FitNotCompleted, MissingDataPreprocessingStep, WrongDataJoinGraphNodeName, DataSourceSizeNotSupported,
    TrainingDataSourceIsNotFile, NoneDataConnection, PipelineNotLoaded, OBMForNFSIsNotSupported,
    ForecastingUnsupportedOperation, LibraryNotCompatible, InvalidDataAsset, TestDataNotPresent)
from ibm_watson_machine_learning.utils.autoai.utils import try_import_lale, all_logging_disabled
from ibm_watson_machine_learning.utils.autoai.wsd_ui import (
    save_computed_pipelines_for_ui, save_experiment_for_ui, save_metadata_for_ui)
from ibm_watson_machine_learning.utils.autoai.connection import validate_source_data_connections, \
    validate_results_data_connection
from ibm_watson_machine_learning.utils import DisableWarningsLogger
from .base_auto_pipelines import BaseAutoPipelines

if TYPE_CHECKING:
    from ibm_watson_machine_learning.experiment.autoai.engines import WMLEngine
    from ibm_watson_machine_learning.utils.autoai.enums import Metrics, PredictionType, Transformers
    from ibm_watson_machine_learning.preprocessing import DataJoinGraph
    from sklearn.pipeline import Pipeline

__all__ = [
    "RemoteAutoPipelines"
]


class RemoteAutoPipelines(BaseAutoPipelines):
    """
    RemoteAutoPipelines class for pipeline operation automation on WML.

    Parameters
    ----------
    name: str, required
        Name for the AutoPipelines

    prediction_type: PredictionType, required
        Type of the prediction.

    prediction_column: str, required
        name of the target/label column

    scoring: Metrics, required
        Type of the metric to optimize with.

    desc: str, optional
        Description

    holdout_size: float, optional
        Percentage of the entire dataset to leave as a holdout. Default 0.1

    max_num_daub_ensembles: int, optional
        Maximum number (top-K ranked by DAUB model selection) of the selected algorithm, or estimator types,
        for example LGBMClassifierEstimator, XGBoostClassifierEstimator, or LogisticRegressionEstimator
        to use in pipeline composition.  The default is 1, where only the highest ranked by model
        selection algorithm type is used.

    train_sample_rows_test_size: float, optional
        Training data sampling percentage

    include_only_estimators: List[Union['ClassificationAlgorithms', 'RegressionAlgorithms']], optional
        List of estimators to include in computation process.

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

    engine: WMLEngine, required
        Engine for remote work on WML.

    data_join_graph: DataJoinGraph, optional
        A graph object with definition of join structure for multiple input data sources.
        Data preprocess step for multiple files.

    """

    def __init__(self,
                 name: str,
                 prediction_type: 'PredictionType',
                 prediction_column: str,
                 prediction_columns: List[str],
                 timestamp_column_name: str,
                 engine: 'WMLEngine',
                 scoring: 'Metrics' = None,
                 desc: str = None,
                 holdout_size: float = 0.1,
                 max_num_daub_ensembles: int = 1,
                 t_shirt_size: 'TShirtSize' = TShirtSize.M,
                 train_sample_rows_test_size: float = None,
                 include_only_estimators: List[Union['ClassificationAlgorithms', 'RegressionAlgorithms']] = None,
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
                 text_processing: bool = True,
                 word2vec_feature_number: int = None,
                 daub_give_priority_to_runtime: float = None,
                 notebooks=False,
                 autoai_pod_version=None,
                 obm_pod_version=None,
                 text_columns_names=None,
                 n_parallel_data_connections=None,
                 test_data_csv_separator: Union[List[str], str] = ',',
                 test_data_excel_sheet: Union[str, int] = 0,
                 test_data_encoding: str = 'utf-8',
                 # sampling_type=None,  #TODO: Uncomment to add sampling_type support
                 categorical_imputation_strategy=None,
                 numerical_imputation_strategy=None,
                 numerical_imputation_value=None,
                 imputation_threshold=None,
                 fairness_info: dict = None,
                 retrain_on_holdout: bool = True,
                 **kwargs):
        
        if data_join_graph is not None:
            data_join_graph.fairness_info = fairness_info

        self.params = {
            'name': name,
            'desc': desc if desc else '',
            'prediction_type': prediction_type if prediction_type != 'timeseries' else 'forecasting',
            'prediction_column': prediction_column,
            'prediction_columns': prediction_columns,
            'timestamp_column_name': timestamp_column_name,
            'scoring': scoring,
            'holdout_size': holdout_size,
            'max_num_daub_ensembles': max_num_daub_ensembles,
            't_shirt_size': t_shirt_size,
            'train_sample_rows_test_size': train_sample_rows_test_size,
            'include_only_estimators': include_only_estimators,
            'backtest_num': backtest_num,
            'lookback_window': lookback_window,
            'forecast_window': forecast_window,
            'backtest_gap_length': backtest_gap_length,
            'cognito_transform_names': cognito_transform_names,
            'data_join_graph': data_join_graph or False,
            'csv_separator': csv_separator,
            'excel_sheet': excel_sheet,
            'encoding': encoding,
            'positive_label': positive_label,
            'data_join_only': data_join_only,
            'drop_duplicates': drop_duplicates,
            'notebooks': notebooks,
            'autoai_pod_version': autoai_pod_version,
            'obm_pod_version': obm_pod_version,
            'text_processing': text_processing,
            'word2vec_feature_number': word2vec_feature_number,
            'daub_give_priority_to_runtime': daub_give_priority_to_runtime,
            'text_columns_names': text_columns_names,
            # 'sampling_type': sampling_type, #TODO: Uncomment to add sampling_type support
            'n_parallel_data_connections': n_parallel_data_connections,
            'test_data_csv_separator': test_data_csv_separator,
            'test_data_excel_sheet': test_data_excel_sheet,
            'test_data_encoding': test_data_encoding,
            'categorical_imputation_strategy': categorical_imputation_strategy,
            'numerical_imputation_strategy': numerical_imputation_strategy,
            'numerical_imputation_value': numerical_imputation_value,
            'imputation_threshold': imputation_threshold,
            'retrain_on_holdout': retrain_on_holdout
        }

        if fairness_info:
            self.params['fairness_info'] = fairness_info

        self._engine: 'WMLEngine' = engine
        self._engine.initiate_remote_resources(params=self.params, **kwargs)
        self.best_pipeline = None
        self._workspace = None

    def _get_engine(self) -> 'WMLEngine':
        """Return WMLEngine for development purposes."""
        return self._engine

    ####################################################
    #   WML Pipeline Part / Parameters for AUtoAI POD  #
    ####################################################
    def get_params(self) -> dict:
        """
        Get configuration parameters of AutoPipelines.

        Returns
        -------
        Dictionary with AutoPipelines parameters.

        Example
        -------
        >>> from ibm_watson_machine_learning.experiment import AutoAI
        >>> experiment = AutoAI(credentials, ...)
        >>> remote_optimizer = experiment.optimizer(...)
        >>>
        >>> remote_optimizer.get_params()
            {
                'name': 'test name',
                'desc': 'test description',
                'prediction_type': 'classification',
                'prediction_column': 'y',
                'scoring': 'roc_auc',
                'holdout_size': 0.1,
                'max_num_daub_ensembles': 1,
                't_shirt_size': 'm',
                'train_sample_rows_test_size': 0.8,
                'include_only_estimators': ["ExtraTreesClassifierEstimator",
                                            "GradientBoostingClassifierEstimator",
                                            "LGBMClassifierEstimator",
                                            "LogisticRegressionEstimator",
                                            "RandomForestClassifierEstimator",
                                            "XGBClassifierEstimator"]
            }
        """
        _params = self._engine.get_params().copy()
        del _params['autoai_pod_version']
        del _params['obm_pod_version']
        del _params['notebooks']
        del _params['data_join_only']

        return _params

    ###########################################################
    #   WML Training Part / Parameters for AUtoAI Experiment  #
    ###########################################################
    def fit(self,
            train_data: 'DataFrame' = None,
            *,
            training_data_reference: List['DataConnection'] = None,
            training_results_reference: 'DataConnection' = None,
            background_mode=False,
            test_data_references: List['DataConnection'] = None,
            training_data_references: List['DataConnection'] = None) -> dict:
        """
        Run a training process on WML of autoai on top of the training data referenced by DataConnection.

        Parameters
        ----------
        training_data_reference: List[DataConnection], optional
            Data storage connection details to inform where training data is stored. (Old parameter)

        training_data_references: List[DataConnection], required
            Data storage connection details to inform where training data is stored.
            New version of `training_data_reference`

        training_results_reference: DataConnection, optional
            Data storage connection details to store pipeline training results. Not applicable on CP4D.

        background_mode: bool, optional
            Indicator if fit() method will run in background (async) or (sync).

        test_data_references: List[DataConnection], optional
            Data storage connection details to inform where test / holdout data is stored.

        Returns
        -------
        Dictionary with run details.

        Example
        -------
        >>> from ibm_watson_machine_learning.experiment import AutoAI
        >>> from ibm_watson_machine_learning.helpers import DataConnection, S3Connection, S3Location
        >>>
        >>> experiment = AutoAI(credentials, ...)
        >>> remote_optimizer = experiment.optimizer(...)
        >>>
        >>> remote_optimizer.fit(
        >>>     training_data_connection=[DataConnection(
        >>>         connection=S3Connection(
        >>>             endpoint_url="https://s3.us.cloud-object-storage.appdomain.cloud",
        >>>             access_key_id="9c92n0scodfa",
        >>>             secret_access_key="0ch827gf9oiwdn0c90n20nc0oms29j"),
        >>>         location=S3Location(
        >>>             bucket='automl',
        >>>             path='german_credit_data_biased_training.csv')
        >>>         )
        >>>     )],
        >>>     DataConnection(
        >>>         connection=S3Connection(
        >>>             endpoint_url="https://s3.us.cloud-object-storage.appdomain.cloud",
        >>>             access_key_id="9c92n0scodfa",
        >>>             secret_access_key="0ch827gf9oiwdn0c90n20nc0oms29j"),
        >>>         location=S3Location(
        >>>             bucket='automl',
        >>>             path='')
        >>>         )
        >>>     ),
        >>>     background_mode=False)
        """
        if training_data_references is not None:
            training_data_reference = training_data_references

        if training_data_reference is None or not training_data_reference:
            raise NoneDataConnection('training_data_references')

        for conn in training_data_reference:
            if self._workspace.wml_client.project_type == 'local_git_storage':
                conn.location.userfs = 'true'
            conn._wml_client = self._workspace.wml_client
            # TODO: remove S3 implementation
            if conn.type == DataConnectionTypes.S3:
                conn._validate_cos_resource()

        training_data_reference = [new_conn for conn in training_data_reference for new_conn in
                                   conn._subdivide_connection()]

        if isinstance(test_data_references, list):
            for conn in test_data_references:
                # Update test data ref with client object, experiment parameters
                if isinstance(conn, DataConnection):
                    if self._workspace.wml_client.project_type == 'local_git_storage':
                        conn.location.userfs = 'true'
                    conn._wml_client = self._workspace.wml_client
                    # TODO: remove S3 implementation
                    if conn.type == DataConnectionTypes.S3:
                        conn._validate_cos_resource()

                    conn.auto_pipeline_params = self._engine._auto_pipelines_parameters

        # note: check if DataJoinGraph node names are correct and equivalent
        # to training DataConnections IDs/data_join_node_names
        if self.params['data_join_graph']:
            # note: If the location does not have path attribute it is either S3Location or DatabaseLocation
            if any(filter(lambda x: x.type == DataConnectionTypes.CA and hasattr(x.location, "path"), training_data_reference)):
                raise OBMForNFSIsNotSupported()
            # --- end note

            data_join_graph = self.params['data_join_graph']
            data_connection_ids = [connection.id for connection in training_data_reference]
            for node_name in [node.table.name for node in data_join_graph.nodes]:
                if node_name not in data_connection_ids:
                    raise WrongDataJoinGraphNodeName(
                        node_name,
                        reason=f"Please make sure that each particular node name in data_join_graph is the same as "
                               f"\"data_join_node_name\" parameter in particular equivalent training DataConnection. "
                               f"The default names are taken as a DataConnection.location.path.")
        # --- end note

        # note: update each training data connection with pipeline parameters for holdout split recreation
        for data_connection in training_data_reference:
            data_connection.auto_pipeline_params = self._engine._auto_pipelines_parameters

        if isinstance(train_data, DataFrame):
            training_data_reference[0].write(data=train_data,
                                             remote_name=training_data_reference[0].location.path)
        elif train_data is None:
            pass

        else:
            raise TypeError("train_data should be of type pandas.DataFrame")

        # self._validate_training_data_size(training_data_reference)

        training_data_reference = validate_source_data_connections(training_data_reference, workspace=self._workspace,
                                                                   deployment=False)

        # note: for FSLocation we are creating asset and changing location to AssetLocation
        # so href is not set properly, setter on wml_client will resolve that issue
        for conn in training_data_reference:
            conn._wml_client = self._workspace.wml_client
        # --- end note

        # note: if user did not provide results storage information, use default ones
        if training_results_reference is None:
            if isinstance(training_data_reference[0].location, S3Location) and not self._workspace.wml_client.ICP:
                training_results_reference = DataConnection(
                    connection=training_data_reference[0].connection,
                    location=S3Location(bucket=training_data_reference[0].location.bucket,
                                        path=".")
                )

            elif isinstance(training_data_reference[0].location, AssetLocation) and not self._workspace.wml_client.ICP:
                connection_id = training_data_reference[0].location._get_connection_id(self._workspace.wml_client)

                if connection_id is not None:
                    training_results_reference = DataConnection(
                        connection_asset_id=connection_id,
                        location=S3Location(
                            bucket=training_data_reference[0].location._get_bucket(self._workspace.wml_client),
                            path="default_autoai_out")
                    )

                else:   # set container output location when default DAta Asset is as a train ref
                    training_results_reference = DataConnection(
                        location=ContainerLocation(path="default_autoai_out"))

            elif isinstance(training_data_reference[0].location, ContainerLocation) and not self._workspace.wml_client.ICP:
                training_results_reference = DataConnection(location=ContainerLocation(path="default_autoai_out"))

            else:
                location = FSLocation()
                if self._workspace.WMLS:
                    location.path = location.path.format(option='spaces',
                                                         id=self._engine._wml_client.default_space_id)
                else:
                    if self._workspace.wml_client.default_project_id is None:
                        location.path = location.path.format(option='spaces',
                                                             id=self._engine._wml_client.default_space_id)

                    else:
                        location.path = location.path.format(option='projects',
                                                             id=self._engine._wml_client.default_project_id)
                training_results_reference = DataConnection(
                    connection=None,
                    location=location
                )
        # -- end note
        if isinstance(training_results_reference.location, AssetLocation):
            if training_results_reference.location._get_connection_id(self._workspace.wml_client) is None:
                raise InvalidDataAsset(
                    reason="Please specify Data Asset pointing to connection e.g. COS as an output.")

        # note: results can be stored only on FS or COS
        if not isinstance(training_results_reference.location, (S3Location, FSLocation, AssetLocation, ContainerLocation)):
            raise TypeError('Unsupported results location type. Results referance can be stored'
                            ' only on S3Location or FSLocation or AssetLocation.')
        # -- end

        # note: only if we are going with OBM + KB scenario, add ID to results DataConnection
        if self.params.get('data_join_graph'):
            training_results_reference.id = 'outputData'
        # --- end note

        run_params = self._engine.fit(training_data_reference=training_data_reference,
                                      training_results_reference=training_results_reference,
                                      background_mode=background_mode,
                                      test_data_references=test_data_references)

        for conn in training_data_reference:
            metrics = run_params['entity']['status'].get('metrics', [])
            if metrics and metrics[-1]['context'].get('fairness'):
                conn.auto_pipeline_params['fairness_info'] = metrics[-1]['context']['fairness'].get('info')

        if isinstance(training_data_reference[0].location, WSDAssetLocation) or (
                isinstance(training_data_reference[0].location, AssetLocation
                           ) and training_data_reference[0].location._wsd):
            try:
                wml_pipeline_details = self._workspace.wml_client.pipelines.get_details(
                    run_params['entity']['pipeline']['id'])
                save_experiment_for_ui(wml_pipeline_details,
                                       run_params,
                                       training_data_reference[0].location._local_asset_path,
                                       training_data_reference[0].location._asset_id,
                                       training_data_reference[0].location._asset_name)
                save_computed_pipelines_for_ui(self._workspace.wml_client,
                                               self._engine._current_run_id)
                save_metadata_for_ui(wml_pipeline_details, run_params)

            except Exception as e:
                print(f"Cannot save experiment locally. It will not be visible in the WSD UI. Error: {e}")
                warn(f"Cannot save experiment locally. It will not be visible in the WSD UI. Error: {e}")

        return run_params

    #####################
    #   Run operations  #
    #####################
    def get_run_status(self) -> str:
        """
        Check status/state of initialized AutoPipelines run if ran in background mode

        Returns
        -------
        Dictionary with run status details.

        Example
        -------
        >>> from ibm_watson_machine_learning.experiment import AutoAI
        >>> experiment = AutoAI(credentials, ...)
        >>> remote_optimizer = experiment.optimizer(...)
        >>>
        >>> remote_optimizer.get_run_status()
            'completed'
        """
        return self._engine.get_run_status()

    def get_run_details(self, include_metrics: bool = False) -> dict:
        """
        Get fit/run details.

        Parameters
        ----------
        include_metrics: bool, optional
            Indicates to include metrics in the training details output. Default False.

        Returns
        -------
        Dictionary with AutoPipelineOptimizer fit/run details.

        Example
        -------
        >>> from ibm_watson_machine_learning.experiment import AutoAI
        >>> experiment = AutoAI(credentials, ...)
        >>> remote_optimizer = experiment.optimizer(...)
        >>>
        >>> remote_optimizer.get_run_details()
        """
        return self._engine.get_run_details(include_metrics=include_metrics)

    def cancel_run(self) -> None:
        """Cancels an AutoAI run."""
        self._engine.cancel_run()

    #################################
    #   Pipeline models operations  #
    #################################
    def summary(self) -> 'DataFrame':
        """
        Prints AutoPipelineOptimizer Pipelines details (autoai trained pipelines).

        Returns
        -------
        Pandas DataFrame with computed pipelines and ML metrics.

        Example
        -------
        >>> from ibm_watson_machine_learning.experiment import AutoAI
        >>> experiment = AutoAI(credentials, ...)
        >>> remote_optimizer = experiment.optimizer(...)
        >>>
        >>> remote_optimizer.summary()
                           training_normalized_gini_coefficient  ...  training_f1
            Pipeline Name                                        ...
            Pipeline_3                                 0.359173  ...     0.449197
            Pipeline_4                                 0.359173  ...     0.449197
            Pipeline_1                                 0.358124  ...     0.449057
            Pipeline_2                                 0.358124  ...     0.449057
        """
        return self._engine.summary()

    def get_pipeline_details(self, pipeline_name: str = None) -> dict:
        """
        Fetch specific pipeline details, eg. steps etc.

        Parameters
        ----------
        pipeline_name: str, optional
            Pipeline name eg. Pipeline_1, if not specified, best pipeline parameters will be fetched

        Returns
        -------
        Dictionary with pipeline parameters.

        Example
        -------
        >>> from ibm_watson_machine_learning.experiment import AutoAI
        >>> experiment = AutoAI(credentials, ...)
        >>> remote_optimizer = experiment.optimizer(...)
        >>>
        >>> remote_optimizer.get_pipeline_details()
        >>> remote_optimizer.get_pipeline_details(pipeline_name='Pipeline_4')
            {
                'composition_steps': ['TrainingDataset_full_4521_16', 'Split_TrainingHoldout',
                                      'TrainingDataset_full_4068_16', 'Preprocessor_default', 'DAUB'],
                'pipeline_nodes': ['PreprocessingTransformer', 'GradientBoostingClassifierEstimator']
            }
        """
        return self._engine.get_pipeline_details(pipeline_name=pipeline_name)

    def get_pipeline(self,
                     pipeline_name: str = None,
                     astype: 'PipelineTypes' = PipelineTypes.LALE,
                     persist: 'bool' = False) -> Union['Pipeline', 'TrainablePipeline']:
        """
        Download specified pipeline from WML.

        Parameters
        ----------
        pipeline_name: str, optional
            Pipeline name, if you want to see the pipelines names, please use summary() method.
            If this parameter is None, the best pipeline will be fetched.

        astype: PipelineTypes, optional
            Type of returned pipeline model. If not specified, lale type is chosen.

        persist: bool, optional
            Indicates if selected pipeline should be stored locally.

        Returns
        -------
        Scikit-Learn pipeline.

        See also
        --------
        RemoteAutoPipelines.summary()

        Example
        -------
        >>> from ibm_watson_machine_learning.experiment import AutoAI
        >>> experiment = AutoAI(credentials, ...)
        >>> remote_optimizer = experiment.optimizer(...)
        >>>
        >>> pipeline_1 = remote_optimizer.get_pipeline(pipeline_name='Pipeline_1')
        >>> pipeline_2 = remote_optimizer.get_pipeline(pipeline_name='Pipeline_1', astype=AutoAI.PipelineTypes.LALE)
        >>> pipeline_3 = remote_optimizer.get_pipeline(pipeline_name='Pipeline_1', astype=AutoAI.PipelineTypes.SKLEARN)
        >>> type(pipeline_3)
            <class 'sklearn.pipeline.Pipeline'>
        >>> pipeline_4 = remote_optimizer.get_pipeline(pipeline_name='Pipeline_1', persist=True)
            Selected pipeline stored under: "absolute_local_path_to_model/model.pickle"

        """
        try:
            if pipeline_name is None:
                pipeline_model, check_lale = self._engine.get_best_pipeline(persist=persist)

            else:
                pipeline_model, check_lale = self._engine.get_pipeline(pipeline_name=pipeline_name, persist=persist)

        except ForecastingUnsupportedOperation as e:
            raise e

        except LibraryNotCompatible as e:
            raise e

        except Exception as e:
            raise PipelineNotLoaded(pipeline_name if pipeline_name is not None else 'best pipeline',
                                    reason=f"Pipeline with such a name probably does not exist. "
                                           f"Please make sure you specify correct pipeline name. Error: {e}")

        if astype == PipelineTypes.SKLEARN:
            return pipeline_model

        elif astype == PipelineTypes.LALE:
            if check_lale:
                try_import_lale()
            from lale.helpers import import_from_sklearn_pipeline
            with all_logging_disabled():
                # note: join preprocessing step to final pipeline (enables wider visualization and pretty print)
                try:
                    import numpy as np
                    preprocessing_object = self.get_preprocessing_pipeline()
                    preprocessing_pipeline = preprocessing_object.lale_pipeline

                    # note: fake fit for preprocessing pipeline to be able to predict
                    preprocessing_pipeline = preprocessing_pipeline.fit(np.array([[1, 2, 3], [2, 3, 4]]), np.array([1, 2]))
                    return preprocessing_pipeline >> import_from_sklearn_pipeline(pipeline_model)

                except MissingDataPreprocessingStep:
                    return import_from_sklearn_pipeline(pipeline_model)

                except BaseException as e:
                    message = f"Cannot load preprocessing step. Error: {e}"
                    print(message)
                    warn(message)
                    return import_from_sklearn_pipeline(pipeline_model)
                # --- end note

        else:
            raise ValueError('Incorrect value of \'astype\'. '
                             'Should be either PipelineTypes.SKLEARN or PipelineTypes.LALE')

    # note: predict on top of the best computed pipeline, best pipeline is downloaded for the first time
    def predict(self, X: Union['DataFrame', 'ndarray']) -> 'ndarray':
        """
        Predict method called on top of the best fetched pipeline.

        Parameters
        ----------
        X: numpy.ndarray or pandas.DataFrame, required
            Test data for prediction

        Returns
        -------
        Numpy ndarray with model predictions.
        """
        if self.best_pipeline is None:
            # note: automatically download the best computed pipeline
            if self.get_run_status() == RunStateTypes.COMPLETED:
                self.best_pipeline, _ = self._engine.get_best_pipeline()
            else:
                raise FitNotCompleted(self._engine._current_run_id,
                                      reason="Please check the run status with run_status() method.")
            # --- end note

        if isinstance(X, DataFrame) or isinstance(X, ndarray):
            return self.best_pipeline.predict(X if isinstance(X, ndarray) else X.values)
        else:
            raise TypeError("X should be either of type pandas.DataFrame or numpy.ndarray")

    # --- end note

    def get_data_connections(self) -> List['DataConnection']:
        """
        Create DataConnection objects for further user usage
            (eg. to handle data storage connection or to recreate autoai holdout split).

        Returns
        -------
        List['DataConnection'] with populated optimizer parameters
        """
        user_holdout_exists = True
        try:
            with DisableWarningsLogger():
                with redirect_stdout(open(os.devnull, "w")):
                    self.get_test_data_connections()

        except TestDataNotPresent:
            user_holdout_exists = False

        optimizer_parameters = self.get_params()
        training_data_references = self.get_run_details()['entity']['training_data_references']

        data_connections = [
            DataConnection._from_dict(_dict=data_connection) for data_connection in training_data_references]

        run_details = self.get_run_details(include_metrics=True)

        for data_connection in data_connections:  # note: populate DataConnections with optimizer params
            data_connection.auto_pipeline_params = deepcopy(optimizer_parameters)
            data_connection._wml_client = self._engine._wml_client
            data_connection._run_id = self._engine._current_run_id
            data_connection._user_holdout_exists = user_holdout_exists

            metrics = run_details['entity']['status'].get('metrics', [])
            if metrics and metrics[-1]['context'].get('fairness'):
                data_connection.auto_pipeline_params['fairness_info'] = metrics[-1]['context']['fairness'].get('info')

        return data_connections

    def get_test_data_connections(self) -> List['DataConnection']:
        """
        Create DataConnection objects for further user usage
            (To recreate autoai holdout that user specified).

        Returns
        -------
        List['DataConnection'] with populated optimizer parameters
        """
        optimizer_parameters = self.get_params()
        run_details = self.get_run_details()

        if not run_details['entity'].get('test_data_references'):
            raise TestDataNotPresent(reason="User specified test data was not present in this experiment. "
                                            "Try to use 'with_holdout_split' parameter for original "
                                            "training_data_references to retrieve test data.")

        test_data_references = run_details['entity']['test_data_references']

        data_connections = [
            DataConnection._from_dict(_dict=data_connection) for data_connection in test_data_references]

        for data_connection in data_connections:  # note: populate DataConnections with optimizer params
            data_connection.auto_pipeline_params = deepcopy(optimizer_parameters)
            data_connection._wml_client = self._engine._wml_client
            data_connection._run_id = self._engine._current_run_id
            data_connection._test_data = True
            data_connection._user_holdout_exists = True

        return data_connections

    def _validate_training_data_size(self, training_data_reference: List['DataConnection']) -> None:
        """
        Check size of dataset in training data connection
        """

        for training_connection in training_data_reference:
            t_shirt_size = self._engine._auto_pipelines_parameters.get('t_shirt_size')

            if isinstance(training_connection.location, S3Location):
                size = training_connection.location._get_file_size(training_connection._init_cos_client())
            elif isinstance(training_connection.location, WSDAssetLocation):
                size = training_connection.location._get_file_size()
            else:
                size = training_connection.location._get_file_size(self._workspace)

            if size is None:
                raise TrainingDataSourceIsNotFile(training_connection.location)

            if self._workspace.WMLS:
                if t_shirt_size in (TShirtSize.S, TShirtSize.M) and size > 100 * 1024 * 1024:
                    raise DataSourceSizeNotSupported()
                elif t_shirt_size in (TShirtSize.ML, TShirtSize.L) and size > 1024 * 1024 * 1024:
                    raise DataSourceSizeNotSupported()
            else:
                pass  # note: data source size checking for other environment is not implemented

    def get_preprocessed_data_connection(self) -> 'DataConnection':
        """
        Create DataConnection object for further user usage (with OBM output)
            (eg. to handle data storage connection or to recreate autoai holdout split).

        Returns
        -------
        DataConnection with populated optimizer parameters
        """
        optimizer_parameters = self.get_params()

        if optimizer_parameters['data_join_graph']:
            details = self._engine._wml_client.training.get_details(
                training_uid=self._engine._current_run_id)

            path = details['entity']['results_reference']['location'].get(
                'path',
                details['entity']['results_reference']['location'].get('file_name'))

            if path == '':
                path = f"{self._engine._current_run_id}/data/obm/features/part"

            else:
                path = f"{path}/{self._engine._current_run_id}/data/obm/features/part"

            results_connection = DataConnection._from_dict(_dict=details['entity']['results_reference'])
            results_connection.auto_pipeline_params = deepcopy(optimizer_parameters)
            results_connection._wml_client = self._engine._wml_client
            results_connection._run_id = self._engine._current_run_id
            results_connection._obm = True  # indicator for OBM output data
            results_connection._obm_cos_path = path

            return results_connection

        else:
            raise MissingDataPreprocessingStep(
                reason="Cannot get preprocessed data as preprocessing step was not performed.")

    def get_preprocessed_test_data_connection(self) -> 'DataConnection':
        """
        Create DataConnection object for further user usage (with OBM output)
            (eg. to handle data storage connection or to recreate autoai holdout split).

        Returns
        -------
        DataConnection with populated optimizer parameters
        """
        raise NotImplementedError("This functionality is not yet implemented.")

    def get_preprocessing_pipeline(self) -> 'DataJoinPipeline':
        """
        Returns preprocessing pipeline object for further usage.
            (eg. to visualize preprocessing pipeline as graph).

        Returns
        -------
        DataJoinPipeline
        """
        optimizer_parameters = self.get_params()

        if optimizer_parameters['data_join_graph']:
            return DataJoinPipeline(preprocessed_data_connection=self.get_preprocessed_data_connection(),
                                    optimizer=self)

        else:
            raise MissingDataPreprocessingStep(
                reason="Cannot get preprocessed pipeline as preprocessing step was not performed.")


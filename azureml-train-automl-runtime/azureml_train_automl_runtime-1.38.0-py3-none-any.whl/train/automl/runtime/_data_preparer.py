# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, cast, Dict, List, Optional, Tuple

import azureml.dataprep as dprep
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.runtime._data_definition import RawExperimentData

from azureml.automl.core import dataprep_utilities
from azureml.automl.core.shared import constants
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientMemory, MalformedJsonString
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import AutoMLException, ConfigException, ResourceException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime import dataprep_utilities as dataprep_runtime_utilities
from azureml.automl.runtime import training_utilities
from azureml.automl.runtime.dataprep_utilities import dataprep_error_handler
from azureml.core import Run, Dataset
from azureml.dataprep import DataPrepException as DprepException
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.exceptions import ClientException

from ._data_characteristics_calculator import DataCharacteristicsCalculator, DataCharacteristics


logger = logging.getLogger(__name__)


class DatasetType:
    FitParams = 'FitParams'
    Test = 'Test'


class DataPreparer(ABC):

    def __init__(self, dataprep_json_obj: Dict[str, Any]):
        """
        :param dataprep_json_obj: The JSON that represents the data location and metadata
        """
        self.data_characteristics = None     # type: Optional[DataCharacteristics]
        self._original_training_data = None  # type: Optional[dprep.Dataflow]
        with logging_utilities.log_activity(logger=logger, activity_name='ParsingDataprepJSON'):
            self._parse(dataprep_json_obj)

        with logging_utilities.log_activity(logger=logger, activity_name="BuildingDataCharacteristics"):
            self._build_data_characterstics()

    @abstractmethod
    def _parse(self, dataprep_json_obj: Dict[str, Any]) -> None:
        """
        Parse the JSON and cache the results for future use
        :param dataprep_json_obj:The JSON that represents the data location and metadata
        """
        raise NotImplementedError

    @abstractmethod
    def _get_fit_params(self, automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
        """
        Return the fit data params
        :param automl_settings_obj: automl settings
        :return: dictionary containing fit data params
        """
        raise NotImplementedError

    @abstractmethod
    def _get_test_data(self, automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
        """
        Return the test dataset
        :param automl_settings_obj: automl settings
        :return: dictionary containing test datasets
        """
        raise NotImplementedError

    def has_test_data(self) -> bool:
        """
        Returns whether or not this DataPreparer has test data.
        :return: bool
        """
        return False

    def prepare_raw_experiment_data(self,
                                    automl_settings_obj: AzureAutoMLSettings,
                                    dataset_types: Optional[List[str]] = None) -> RawExperimentData:
        """
        Prepare data and return the specified datasets.
        :param automl_settings_obj: automl settings
        :param dataset_types: A list of DatasetTypes that should be returned.
            If this is not specified or None then only FitParams will be returned.
        :return: RawExperimentData
        """
        if not dataset_types:
            dataset_types = [DatasetType.FitParams]

        datasets = {}

        try:
            if DatasetType.FitParams in dataset_types:
                fit_params = self._get_fit_params(automl_settings_obj)
                datasets.update(fit_params)

            if DatasetType.Test in dataset_types:
                test_data = self._get_test_data(automl_settings_obj)
                datasets.update(test_data)

        except DprepException as e:
            logging_utilities.log_traceback(e, logger)
            dataprep_runtime_utilities.dataprep_error_handler(e)
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            reference_code_for_ex = 'prepare'
            if isinstance(e, MemoryError):
                raise ResourceException._with_error(
                    AzureMLError.create(
                        InsufficientMemory,
                        reference_code=reference_code_for_ex,
                    ), inner_exception=e) from e
            elif not isinstance(e, AutoMLException):
                generic_msg = 'Failed to get data from DataPrep. Exception Type: {}'.format(type(e))
                logger.error(generic_msg)
                raise ClientException.from_exception(e, reference_code=reference_code_for_ex).with_generic_msg(
                    generic_msg) from e
            else:
                raise

        return RawExperimentData.create(
            datasets,
            automl_settings_obj.label_column_name,
            automl_settings_obj.weight_column_name,
            automl_settings_obj.validation_size,
            automl_settings_obj.n_cross_validations)

    def _build_data_characterstics(self):
        """
        Build data characteristics of the original training data and cache it for future use
        :return:
        """
        if self._original_training_data is not None:
            try:
                logger.info('Starting data characteristics calculation. This might take a while...')
                self.data_characteristics = DataCharacteristicsCalculator.calc_data_characteristics(
                    self._original_training_data)
            except Exception:
                # this is best effort based - hence log as info
                logger.info('data characteristics calculation failed')


class DataPreparerFromDataSet(DataPreparer):
    """
    Used to prepare the data when the input to training_data is a Dataset object.
    """

    def __init__(self, dataprep_json_obj: Dict[str, Any]):
        super().__init__(dataprep_json_obj)

    def _parse(self, dataprep_json_obj: Dict[str, Any]) -> None:
        logger.info('Creating dataflow from datasets for training_data, validation_data and/or test_data.')

        self.training_dataflow = None
        self.validation_dataflow = None
        self.test_dataflow = None

        ws = Run.get_context().experiment.workspace

        from azureml.data._dataset_deprecation import silent_deprecation_warning
        with silent_deprecation_warning():
            training_data = dataprep_json_obj.get('training_data')

            if training_data:
                training_dataset_id = training_data['datasetId']  # mandatory
                training_dataset = Dataset.get_by_id(ws, id=training_dataset_id)
                self.training_dataflow = training_dataset._dataflow
                self._original_training_data = self.training_dataflow

            validation_data = dataprep_json_obj.get('validation_data')
            if validation_data:
                validation_dataset_id = validation_data['datasetId']  # mandatory
                validation_dataset = Dataset.get_by_id(ws, id=validation_dataset_id)
                self.validation_dataflow = validation_dataset._dataflow

            test_data = dataprep_json_obj.get('test_data')
            if test_data:
                test_dataset_id = test_data['datasetId']  # mandatory
                test_dataset = Dataset.get_by_id(ws, id=test_dataset_id)
                self.test_dataflow = test_dataset._dataflow

    def has_test_data(self) -> bool:
        return self.test_dataflow is not None

    def _get_fit_params(self, automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
        if self.data_characteristics is None or not self.data_characteristics:
            training_data_row_count = 0
        else:
            training_data_row_count = self.data_characteristics.num_rows

        fit_params = {}

        if self.training_dataflow:
            fit_params = DataPreparerUtils._get_dict_from_dataflows(self.training_dataflow,
                                                                    self.validation_dataflow,
                                                                    automl_settings_obj,
                                                                    training_data_row_count)
        return fit_params

    def _get_test_data(self, automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
        """
        Return the test dataset
        :param automl_settings_obj: automl settings
        :return: dictionary containing test datasets
        """
        test_data = {}

        if self.test_dataflow:
            test_data = DataPreparerUtils._get_dict_from_test_dataflow(self.test_dataflow,
                                                                       automl_settings_obj)
        return test_data


class DataPreparerFromSerializedDataflows(DataPreparer):
    """
    Used to prepare the data when the input to training_data/X is a dataflow object.
    """

    def __init__(self, dataprep_json_obj: Dict[str, Any]):
        super().__init__(dataprep_json_obj)

    def _parse(self, dataprep_json_obj: Dict[str, Any]) -> None:
        logger.info('Deserializing dataflow.')

        dataflow_dict = dataprep_utilities.load_dataflows_from_json_dict(dataprep_json_obj)
        self._original_training_data = dataflow_dict.get('training_data')

        self.test_dataflow_dict = {'test_data': dataflow_dict.pop('test_data', None)}
        self.fit_params_dataflow_dict = dataflow_dict

    def has_test_data(self) -> bool:
        return self.test_dataflow_dict['test_data'] is not None

    def _get_fit_params(self, automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
        if self.data_characteristics is not None:
            training_data_row_count = self.data_characteristics.num_rows
        else:
            training_data_row_count = 0

        fit_params = {}

        if self.fit_params_dataflow_dict:
            fit_params = DataPreparerUtils._helper_get_data_from_dict(self.fit_params_dataflow_dict,
                                                                      automl_settings_obj,
                                                                      training_data_row_count)
        return fit_params

    def _get_test_data(self, automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
        """
        Return the test dataset
        :param automl_settings_obj: automl settings
        :return: dictionary containing test datasets
        """
        test_data = {}

        if self.test_dataflow_dict:
            test_data = DataPreparerUtils._helper_get_test_data_from_dict(self.test_dataflow_dict,
                                                                          automl_settings_obj)
        return test_data


# TODO: This class is deprecated. The only client that currently leverages this is AutoML.NET, and it's not entirely
#       clear where the changes need to be made to update it, nor there are any clear owners of that feature that can
#       take the necessary actions to update it.
class DataPreparerFromDatasetOptions(DataPreparer):
    """
    The dataprep JSON in this case is expected to contain the following keys:
        - datasetId: The dataset id for training data
        - label: The target column
        - features: Optional, the features to use in model training
    """

    def __init__(self, dataprep_json_obj: Dict[str, Any]):
        super().__init__(dataprep_json_obj)

    def _parse(self, dataprep_json_obj: Dict[str, Any]) -> None:
        logger.info('Creating dataflow from dataset.')
        dataset_id = dataprep_json_obj['datasetId']  # mandatory
        self.label_column = dataprep_json_obj['label']  # mandatory
        self.feature_columns = dataprep_json_obj.get('features', [])

        ws = Run.get_context().experiment.workspace
        from azureml.data._dataset_deprecation import silent_deprecation_warning
        with silent_deprecation_warning():
            dataset = Dataset.get(ws, id=dataset_id)
        self._original_training_data = dataset.definition

    def _get_fit_params(self, automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
        if self.data_characteristics is None or not self.data_characteristics:
            training_data_row_count = 0
        else:
            training_data_row_count = self.data_characteristics.num_rows
        return DataPreparerUtils._get_dict_from_dataflow(self._original_training_data,
                                                         automl_settings_obj,
                                                         self.feature_columns,
                                                         self.label_column,
                                                         training_data_row_count)

    def _get_test_data(self, automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
        """
        Return the test dataset
        :param automl_settings_obj: automl settings
        :return: dictionary containing test datasets
        """
        raise NotImplementedError


class DataPreparerFactory:
    """
    A factory class that can return the appropriate preparer based on JSON contents
    """

    @staticmethod
    def get_preparer(dataprep_json: str) -> DataPreparer:
        """
        Return a preparer based on JSON contents
        :param dataprep_json: JSON representing input data location and metadata
        :return: Datapreparer that can handle the data
        """
        try:
            logger.info('Resolving dataflows using dprep json.')
            logger.info('DataPrep version: {}'.format(dprep.__version__))
            try:
                from azureml._base_sdk_common import _ClientSessionId
                logger.info('DataPrep log client session id: {}'.format(_ClientSessionId))
            except Exception:
                logger.info('Cannot get DataPrep log client session id')

            dataprep_json_obj = json.loads(dataprep_json)

            data_preparer = None    # type: Optional[DataPreparer]
            if 'activities' in dataprep_json_obj:
                data_preparer = DataPreparerFromSerializedDataflows(dataprep_json_obj)
            elif 'datasetId' in dataprep_json_obj:
                data_preparer = DataPreparerFromDatasetOptions(dataprep_json_obj)
            elif 'datasets' in dataprep_json_obj:
                data_preparer = DataPreparerFromDataSet(dataprep_json_obj)

            Contract.assert_true(
                data_preparer is not None,
                "data_preparer cannot be initialized, an unsupported json string was passed with keys: {}".format(
                    list(dataprep_json_obj.keys())))

            logger.info('Successfully retrieved data using {}.'.format(data_preparer.__class__.__name__))
            return cast(DataPreparer, data_preparer)
        except json.JSONDecodeError as je:
            logging_utilities.log_traceback(je, logger)
            raise ConfigException._with_error(
                AzureMLError.create(MalformedJsonString, target="dataprep_json", json_decode_error=str(je))
            )
        except DprepException as de:
            logging_utilities.log_traceback(de, logger)
            dataprep_error_handler(de)
        except AutoMLException:
            raise
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            raise ClientException.from_exception(e, target="dataprep_json", reference_code="_get_data_from_dataprep").\
                with_generic_msg("Encountered an unknown exception of type {} while fetching data from Dataprep "
                                 "json.".format(type(e)))


class DataPreparerUtils:
    """
    A set of utilities that can build fit data params
    and test data given a dataflow
    """
    @staticmethod
    def _get_dict_from_dataflows(training_dflow: Any,
                                 validation_dflow: Any,
                                 automl_settings_obj: AzureAutoMLSettings,
                                 train_data_row_count: int) -> Dict[str, Any]:
        fit_iteration_parameters_dict = DataPreparerUtils._set_dict_from_dataflow(training_dflow,
                                                                                  validation_dflow,
                                                                                  automl_settings_obj)

        return DataPreparerUtils._helper_get_data_from_dict(fit_iteration_parameters_dict,
                                                            automl_settings_obj,
                                                            train_data_row_count)

    @staticmethod
    def _get_dict_from_test_dataflow(test_dflow: Any,
                                     automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
        data_dict = {'test_data': test_dflow}

        columns_list = []
        if automl_settings_obj.label_column_name is not None:
            columns_list.append(automl_settings_obj.label_column_name)
        if automl_settings_obj.weight_column_name is not None:
            columns_list.append(automl_settings_obj.weight_column_name)

        # fill in x and y here so that other stuff works.
        data_dict['X_test'] = test_dflow.drop_columns(columns_list)
        data_dict['y_test'] = test_dflow.keep_columns(
            automl_settings_obj.label_column_name) \
            if automl_settings_obj.label_column_name is not None else None

        return DataPreparerUtils._helper_get_test_data_from_dict(data_dict,
                                                                 automl_settings_obj)

    @staticmethod
    def _get_dict_from_dataflow(dflow: Any,
                                automl_settings_obj: AzureAutoMLSettings,
                                feature_columns: List[str],
                                label_column: str,
                                train_data_row_count: int) -> Dict[str, Any]:
        feature_columns = list(filter(None, feature_columns))
        fit_iteration_parameters_dict = {}  # type: Dict[str, Any]
        if not automl_settings_obj.enable_streaming:
            if len(feature_columns) == 0:
                X = dflow.drop_columns(label_column) \
                    if label_column is not None else dflow
            else:
                X = dflow.keep_columns(feature_columns)

            y = dflow.keep_columns(label_column) \
                if label_column is not None else None
            if automl_settings_obj.task_type == constants.Tasks.REGRESSION:
                y = y.to_number(label_column)

            _X = dataprep_runtime_utilities.materialize_dataflow(X)
            _y = dataprep_runtime_utilities.materialize_dataflow(y, as_numpy=True)

            fit_iteration_parameters_dict = {
                "X": _X,
                "y": _y,
                "sample_weight": None,
                "x_raw_column_names": _X.columns.values,
                "X_valid": None,
                "y_valid": None,
                "sample_weight_valid": None,
                "X_test": None,
                "y_test": None,
                "cv_splits_indices": None,
            }
        else:
            if len(feature_columns) > 0:
                feature_columns_with_label = feature_columns
                if label_column is not None:
                    feature_columns_with_label.append(label_column)
                dflow1 = dflow.keep_columns(feature_columns_with_label)
                training_data = dflow1
            else:
                training_data = dflow

            validation_data, training_data = DataPreparerUtils._split_data_train_valid(
                training_data, train_data_row_count, automl_settings_obj.validation_size)

            fit_iteration_parameters_dict = DataPreparerUtils._set_dict_from_dataflow(
                training_data, validation_data, automl_settings_obj)
        return fit_iteration_parameters_dict

    @staticmethod
    def _helper_get_data_from_dict(dataflow_dict: Dict[str, Any],
                                   automl_settings_obj: AzureAutoMLSettings,
                                   train_data_row_count: int) -> Dict[str, Any]:
        if automl_settings_obj.enable_streaming:
            if 'training_data' not in dataflow_dict \
                    or automl_settings_obj.label_column_name is None:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentBlankOrEmpty, target="training_data/label_column_name",
                        argument_name="training_data/label_column_name"
                    )
                )

            columns_list = []
            if automl_settings_obj.label_column_name is not None:
                columns_list.append(automl_settings_obj.label_column_name)
            if automl_settings_obj.weight_column_name is not None:
                columns_list.append(automl_settings_obj.weight_column_name)
            if automl_settings_obj.cv_split_column_names is not None:
                # CV Splits is not supported for streaming right now, these columns are dropped and not used
                columns_list.extend(automl_settings_obj.cv_split_column_names)

            fit_iteration_parameters_dict = dataflow_dict.copy()

            Contract.assert_value(fit_iteration_parameters_dict.get('training_data'), "training_data")
            training_data = cast(dprep.Dataflow, fit_iteration_parameters_dict.get('training_data'))
            validation_data = fit_iteration_parameters_dict.get('validation_data')  # type: Optional[dprep.Dataflow]

            if validation_data is not None:
                if train_data_row_count > 0:
                    # Attempt to calculate validation row count only if training row count has succeeded
                    # we're going to subsample the validation set to ensure we can compute the metrics in memory
                    data_profile = validation_data.get_profile()
                    validation_samples_count = data_profile.row_count
                    max_validation_size = training_utilities.LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE
                    if validation_samples_count > max_validation_size:
                        sample_probability = max_validation_size / validation_samples_count
                        logger.warning(
                            'Subsampling the validation from {} samples with a probability of {}.'
                            .format(validation_samples_count, sample_probability))
                        validation_data = validation_data.take_sample(probability=sample_probability, seed=42)

                # Some of the validation code downstream expects 'X_valid' and 'y_valid'. Hence populate that.
                fit_iteration_parameters_dict['X_valid'] = validation_data.drop_columns(columns_list)
                fit_iteration_parameters_dict['y_valid'] = validation_data.keep_columns(
                    automl_settings_obj.label_column_name) \
                    if automl_settings_obj.label_column_name is not None else None
            else:
                # since the validation data is not provided, we create one ourselves by splitting the training_data
                # Validations on this can be skipped (since it's a part of training data itself)
                validation_data, training_data = DataPreparerUtils._split_data_train_valid(
                    training_data, train_data_row_count, automl_settings_obj.validation_size)

            fit_iteration_parameters_dict['training_data'] = training_data
            fit_iteration_parameters_dict['validation_data'] = validation_data

            # Across SDK, we have a mixed use of ['X' or 'X_valid'] and 'training_data'.
            # Hence, fill in the other values so that other stuff works.
            fit_iteration_parameters_dict['X'] = training_data.drop_columns(columns_list)
            fit_iteration_parameters_dict['y'] = training_data.keep_columns(
                automl_settings_obj.label_column_name) \
                if automl_settings_obj.label_column_name is not None else None

            fit_iteration_parameters_dict['x_raw_column_names'] = fit_iteration_parameters_dict['X'].take(
                1).to_pandas_dataframe().columns.values

            if automl_settings_obj.weight_column_name is not None:
                fit_iteration_parameters_dict['sample_weight'] = training_data.keep_columns(
                    automl_settings_obj.weight_column_name) \
                    if automl_settings_obj.weight_column_name is not None else None
                if automl_settings_obj.validation_size == 0:
                    # User provided a custom validation data
                    fit_iteration_parameters_dict['sample_weight_valid'] = validation_data.keep_columns(
                        automl_settings_obj.weight_column_name) \
                        if automl_settings_obj.weight_column_name is not None else None

        else:
            cv_splits_indices = None
            if 'training_data' in dataflow_dict and automl_settings_obj.label_column_name is not None:
                df = dataflow_dict.get('training_data')  # type: dprep.Dataflow
                X, y, sample_weight, cv_splits_indices = training_utilities._extract_data_from_combined_dataflow(
                    df, automl_settings_obj.label_column_name, automl_settings_obj.weight_column_name,
                    automl_settings_obj.cv_split_column_names
                )
                dataflow_dict['X'] = X
                dataflow_dict['y'] = y
                dataflow_dict['sample_weight'] = sample_weight
                dataflow_dict.pop('training_data')

            if 'validation_data' in dataflow_dict and automl_settings_obj.label_column_name is not None:
                df = dataflow_dict.get('validation_data')
                X_valid, y_valid, sample_weight_valid, _ = training_utilities._extract_data_from_combined_dataflow(
                    df, automl_settings_obj.label_column_name,
                    sample_weight_column_name=automl_settings_obj.weight_column_name)
                dataflow_dict['X_valid'] = X_valid
                dataflow_dict['y_valid'] = y_valid
                dataflow_dict['sample_weight_valid'] = sample_weight_valid
                dataflow_dict.pop('validation_data')
            data_columns = ['sample_weight', 'sample_weight_valid']
            label_columns = ['y', 'y_valid']

            fit_iteration_parameters_dict = {
                k: dataprep_runtime_utilities.materialize_dataflow(dataflow_dict.get(k), as_numpy=True)
                for k in data_columns
            }

            Contract.assert_value(dataflow_dict.get('X'), 'X', reference_code=ReferenceCodes._DATA_PREPARER_X_IS_NONE)

            X = dataprep_runtime_utilities.materialize_dataflow(dataflow_dict.get('X'))
            X_valid = dataprep_runtime_utilities.materialize_dataflow(dataflow_dict.get('X_valid'))
            fit_iteration_parameters_dict['x_raw_column_names'] = X.columns.values
            fit_iteration_parameters_dict['X'] = X
            fit_iteration_parameters_dict['X_valid'] = X_valid

            for k in label_columns:
                fit_iteration_parameters_dict[k] = dataprep_runtime_utilities.materialize_dataflow(
                    dataflow_dict.get(k), as_numpy=True)

            if cv_splits_indices and automl_settings_obj.cv_split_column_names:
                # cv_splits_indices derived from cv_split_column_names
                fit_iteration_parameters_dict['cv_splits_indices'] = cv_splits_indices
            else:
                cv_splits_dataflows = []
                i = 0
                while 'cv_splits_indices_{0}'.format(i) in dataflow_dict:
                    cv_splits_dataflows.append(
                        dataflow_dict['cv_splits_indices_{0}'.format(i)])
                    i = i + 1

                fit_iteration_parameters_dict['cv_splits_indices'] = None if len(cv_splits_dataflows) == 0 \
                    else dataprep_runtime_utilities.resolve_cv_splits_indices(cv_splits_dataflows)

        return fit_iteration_parameters_dict

    @staticmethod
    def _helper_get_test_data_from_dict(dataflow_dict: Dict[str, Any],
                                        automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:
        data_dict = {}

        if 'test_data' in dataflow_dict and automl_settings_obj.label_column_name is not None:
            df = dataflow_dict.pop('test_data')

            X_test, y_test, _, _ = training_utilities._extract_data_from_combined_dataflow(
                df,
                automl_settings_obj.label_column_name,
                automl_settings_obj.weight_column_name,
                validate_columns_exist=False)

            dataflow_dict['X_test'] = X_test

            X_test = dataprep_runtime_utilities.materialize_dataflow(X_test)
            data_dict['X_test'] = X_test

            if y_test and y_test.row_count:
                dataflow_dict['y_test'] = y_test
                data_dict['y_test'] = dataprep_runtime_utilities.materialize_dataflow(y_test, as_numpy=True)
            else:
                dataflow_dict['y_test'] = None
                data_dict['y_test'] = None

        return data_dict

    @staticmethod
    def _split_data_train_valid(
            train_data: dprep.Dataflow,
            train_data_row_count: int,
            validation_size: float = 0.0
    ) -> Tuple[dprep.Dataflow, dprep.Dataflow]:
        logger.info('Splitting input dataset into train & validation datasets')
        # sample_probability is a conservative estimate of what we think as a fair size of validation data
        # without running into memory errors, especially during metric calculation, which is currently
        # non-streaming
        sample_probability = 0.1   # type: float
        if train_data_row_count > 0:
            num_validation_rows = min(
                0.1 * train_data_row_count,
                training_utilities.LargeDatasetLimit.MAX_ROWS_TO_SUBSAMPLE)
            sample_probability = num_validation_rows / train_data_row_count

        if 0 < validation_size <= sample_probability:
            # User has provided a custom % for validation data, so pick the minimum of
            # 'validation_size' or 'sample_probability'
            ret = train_data.random_split(validation_size, seed=42)  # type: Tuple[dprep.Dataflow, dprep.Dataflow]
        else:
            if validation_size > 0 and validation_size > sample_probability:
                logger.warning(
                    "Overriding 'validation_size' to {} due to large data limits.".format(sample_probability))
            else:
                logger.info("'validation_size' was not specified. Using {}% of training data as validation data.".
                            format(sample_probability * 100))

            ret = train_data.random_split(sample_probability, seed=42)

        return ret

    @staticmethod
    def _set_dict_from_dataflow(training_data: Any,
                                validation_data: Any,
                                automl_settings_obj: AzureAutoMLSettings) -> Dict[str, Any]:

        fit_iteration_parameters_dict = dict()  # type: Dict[str, Any]

        fit_iteration_parameters_dict['training_data'] = training_data
        if validation_data is not None:
            fit_iteration_parameters_dict['validation_data'] = validation_data

        columns_list = []
        if automl_settings_obj.label_column_name is not None:
            columns_list.append(automl_settings_obj.label_column_name)
        if automl_settings_obj.weight_column_name is not None:
            columns_list.append(automl_settings_obj.weight_column_name)

        # fill in x and y here so that other stuff works.
        fit_iteration_parameters_dict['X'] = training_data.drop_columns(columns_list)
        fit_iteration_parameters_dict['y'] = training_data.keep_columns(
            automl_settings_obj.label_column_name) \
            if automl_settings_obj.label_column_name is not None else None

        # Some of the data validation code downstream expects 'X_valid' and 'y_valid'. Hence populate that.
        # If user provided a custom 'validation_size', the validation data is just a split of training data.
        # As such, no validations are needed in that case.
        if automl_settings_obj.validation_size == 0:
            fit_iteration_parameters_dict['X_valid'] = validation_data.drop_columns(columns_list) \
                if validation_data is not None else None

            fit_iteration_parameters_dict['y_valid'] = validation_data.keep_columns(
                automl_settings_obj.label_column_name) \
                if validation_data is not None and automl_settings_obj.label_column_name is not None else None

        fit_iteration_parameters_dict['x_raw_column_names'] = fit_iteration_parameters_dict['X'].take(
            1).to_pandas_dataframe().columns.values

        if automl_settings_obj.weight_column_name is not None:
            fit_iteration_parameters_dict['sample_weight'] = training_data.keep_columns(
                automl_settings_obj.weight_column_name) \
                if automl_settings_obj.weight_column_name is not None else None
            if automl_settings_obj.validation_size == 0:
                # User provided a custom validation data
                fit_iteration_parameters_dict['sample_weight_valid'] = validation_data.keep_columns(
                    automl_settings_obj.weight_column_name) \
                    if validation_data is not None and automl_settings_obj.weight_column_name is not None else None

        return fit_iteration_parameters_dict

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holding the data context classes."""
from typing import Any, Dict, List, Optional, Union
import logging
import os

from azureml.dataprep import Dataflow
from sklearn.base import TransformerMixin

from azureml.automl.core.shared import constants
from azureml.automl.core.shared.dataflow_utilities import PicklableDataflow
from azureml.automl.core.shared.utilities import _get_ts_params_dict
from azureml.automl.runtime._runtime_params import ExperimentControlSettings, ExperimentDataSettings
from azureml.automl.runtime.shared.utilities import _check_if_column_has_single_occurrence_value
from azureml.automl.runtime.shared import memory_utilities
from azureml.automl.runtime.shared._cv_splits import _CVSplits
from azureml.automl.runtime.shared.memory_cache_store import MemoryCacheStore
from azureml.automl.core import inference
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings


class DataContextParams:

    def __init__(self, automl_settings: AutoMLBaseSettings):
        self.control_params = ExperimentControlSettings(automl_settings)
        self.data_params = ExperimentDataSettings(automl_settings)

        self.timeseries_param_dict = _get_ts_params_dict(automl_settings)


class BaseDataContext:
    """Base data context class for input raw data and output transformed data."""

    def __init__(self,
                 X,
                 y=None,
                 X_valid=None,
                 y_valid=None,
                 sample_weight=None,
                 sample_weight_valid=None,
                 x_raw_column_names=None,
                 cv_splits_indices=None,
                 num_cv_folds=None,
                 n_step=None,
                 validation_size=None,
                 training_data=None,
                 label_column_name=None,
                 weight_column_name=None,
                 cv_split_column_names=None,
                 validation_data=None,
                 X_raw_cleaned=None,
                 y_raw_cleaned=None,
                 X_valid_raw_cleaned=None,
                 y_valid_raw_cleaned=None,
                 data_snapshot_str=""):
        """
        Construct the BaseDataContext class.

        :param X: Input training data.
        :type X: pandas.DataFrame or Dataflow
        :param y: Input training labels.
        :type y: numpy.ndarray or pandas.DataFrame or Dataflow
        :param X_valid: validation data.
        :type X_valid: pandas.DataFrame or Dataflow
        :param y_valid: validation labels.
        :type y_valid: numpy.ndarray or pandas.DataFrame or Dataflow
        :param sample_weight: Sample weights for training data.
        :type sample_weight: numpy.ndarray or pandas.DataFrame or Dataflow
        :param sample_weight_valid: validation set sample weights.
        :type sample_weight_valid: numpy.ndarray or pandas.DataFrame or Dataflow
        :param x_raw_column_names: raw feature names of X data.
        :type x_raw_column_names: numpy.ndarray
        :param cv_splits_indices: Custom indices by which to split the data when running cross validation.
        :type cv_splits_indices: numpy.ndarray or pandas.DataFrame
        :param num_cv_folds: Number of cross validation folds
        :type num_cv_folds: integer
        :param n_step: Stepsize of cross validation in forecasting
        :type n_step: integer
        :param validation_size: Percentage of data to be held out for validation
        :type validation_size: float
        :param training_data: Input training data.
        :type training_data: numpy.ndarray or pandas.DataFrame or Dataflow
        :param label_column_name: Label column name.
        :type label_column_name: string
        :param weight_column_name: Weight column name.
        :type weight_column_name: string
        :param cv_split_column_names: List of column names containing cv splits
        :type cv_split_column_names: List[str]
        :param validation_data: Validation data.
        :type validation_data: numpy.ndarray or pandas.DataFrame or Dataflow
        :param X_raw_cleaned: Cleaned input training data.
        :type X_raw_cleaned: numpy.ndarray or pandas.DataFrame
        :param y_raw_cleaned: Cleaned input training labels.
        :type y_raw_cleaned: numpy.ndarray or pandas.DataFrame
        :param X_valid_raw_cleaned: Cleaned input validation data.
        :type X_valid_raw_cleaned: numpy.ndarray or pandas.DataFrame
        :param y_valid_raw_cleaned: Cleaned input validation labels.
        :type y_valid_raw_cleaned: numpy.ndarray or pandas.DataFrame
        :param data_snapshot_str: The input data snapshot string.
        :type data_snapshot_str: str
        """
        self.X = X
        self.y = y
        self.X_valid = X_valid
        self.y_valid = y_valid
        self.sample_weight = sample_weight
        self.sample_weight_valid = sample_weight_valid
        self.x_raw_column_names = x_raw_column_names
        self.cv_splits_indices = cv_splits_indices
        self.num_cv_folds = num_cv_folds
        self.n_step = n_step
        self.validation_size = validation_size
        self.training_data = training_data
        self.validation_data = validation_data
        self.label_column_name = label_column_name
        self.weight_column_name = weight_column_name
        self.cv_split_column_names = cv_split_column_names
        self.X_raw_cleaned = X_raw_cleaned
        self.y_raw_cleaned = y_raw_cleaned
        self.X_valid_raw_cleaned = X_valid_raw_cleaned
        self.y_valid_raw_cleaned = y_valid_raw_cleaned
        self.data_snapshot_str = data_snapshot_str

    def _get_memory_size(self):
        """Get total memory size of raw data."""
        total_size = 0

        for k in self.__dict__:

            _get_memory_size = getattr(self.__dict__.get(k), '_get_memory_size', None)
            if _get_memory_size is None:
                total_size += memory_utilities.get_data_memory_size(self.__dict__.get(k))
            else:
                total_size += self.__dict__.get(k)._get_memory_size()  # type: ignore

        return total_size


class RawDataContext(BaseDataContext):
    """User provided data context."""

    def __init__(self,
                 data_context_params,  # AutoMLBaseSettings
                 X,  # DataFlow or DataFrame
                 y=None,  # DataFlow or DataFrame
                 X_valid=None,  # DataFlow
                 y_valid=None,  # DataFlow
                 sample_weight=None,
                 sample_weight_valid=None,
                 x_raw_column_names=None,
                 cv_splits_indices=None,
                 training_data=None,  # DataFlow or DataFrame
                 validation_data=None,  # DataFlow or DataFrame
                 data_snapshot_str=""  # str
                 ):
        """
        Construct the RawDataContext class.

        :param automl_settings_obj: User settings specified when creating AutoMLConfig.
        :type automl_settings_obj: AutoMLBaseSettings
        :param X: Input training data.
        :type X: pandas.DataFrame or Dataflow
        :param y: Input training labels.
        :type y: numpy.ndarray or pandas.DataFrame
        :param X_valid: validation data.
        :type X_valid: pandas.DataFrame or Dataflow
        :param y_valid: validation labels.
        :type y_valid: numpy.ndarray or pandas.DataFrame
        :param sample_weight: Sample weights for training data.
        :type sample_weight: numpy.ndarray or pandas.DataFrame
        :param sample_weight_valid: validation set sample weights.
        :type sample_weight_valid: numpy.ndarray or pandas.DataFrame
        :param x_raw_column_names: raw feature names of X data.
        :type x_raw_column_names: numpy.ndarray
        :param cv_splits_indices: Custom indices by which to split the data when running cross validation.
        :type cv_splits_indices: numpy.ndarray or pandas.DataFrame
        :param data_snapshot_str: The input data snapshot string.
        :type data_snapshot_str: str
        """
        self.featurization = data_context_params.control_params.featurization
        self.task_type = data_context_params.control_params.task_type
        self.timeseries = data_context_params.control_params.is_timeseries
        self.timeseries_param_dict = data_context_params.timeseries_param_dict

        if data_context_params.timeseries_param_dict:
            self.lag_length = data_context_params.timeseries_param_dict.get("lag_length", None)
        else:
            self.lag_length = None

        num_cv_folds = data_context_params.data_params.n_cross_validations
        n_step = data_context_params.data_params.cv_step_size
        validation_size = data_context_params.data_params.validation_size
        label_column_name = data_context_params.data_params.label_column_name
        weight_column_name = data_context_params.data_params.weight_column_name
        cv_split_column_names = data_context_params.data_params.cv_split_column_names

        if data_context_params.control_params.enable_streaming:
            # streaming doesn't support cv splits yet
            training_columns_to_drop = []
            validation_columns_to_drop = []
            if label_column_name is not None:
                training_columns_to_drop.append(label_column_name)
                validation_columns_to_drop.append(label_column_name)
            if weight_column_name is not None:
                training_columns_to_drop.append(weight_column_name)
                validation_columns_to_drop.append(weight_column_name)
            if cv_split_column_names is not None:
                column_names = list(filter(None, cv_split_column_names))  # type: List[str]
                training_columns_to_drop.append(column_names)

            X = training_data.drop_columns(training_columns_to_drop)
            y = training_data.keep_columns(label_column_name) \
                if label_column_name is not None else None
            sample_weight = training_data.keep_columns(weight_column_name) \
                if weight_column_name is not None else None
            X_valid = validation_data.drop_columns(validation_columns_to_drop) \
                if validation_data is not None else None
            y_valid = validation_data.keep_columns(label_column_name) \
                if validation_data is not None and label_column_name is not None else None
            sample_weight_valid = validation_data.keep_columns(weight_column_name) \
                if validation_data is not None and weight_column_name is not None else None

        super().__init__(X=X, y=y,
                         X_valid=X_valid,
                         y_valid=y_valid,
                         sample_weight=sample_weight,
                         sample_weight_valid=sample_weight_valid,
                         x_raw_column_names=x_raw_column_names,
                         cv_splits_indices=cv_splits_indices,
                         num_cv_folds=num_cv_folds,
                         n_step=n_step,
                         validation_size=validation_size,
                         training_data=training_data,
                         label_column_name=label_column_name,
                         validation_data=validation_data,
                         weight_column_name=weight_column_name,
                         cv_split_column_names=cv_split_column_names,
                         data_snapshot_str=data_snapshot_str)


class TransformedDataContext(BaseDataContext):
    """
    The user provided data with applied transformations.

    If there is no featurization done this will be the same as the RawDataContext.
    This class will also hold the necessary transformers used.
    """

    FEATURIZED_CV_SPLIT_KEY_INITIALS = 'featurized_cv_split_'
    FEATURIZED_TRAIN_TEST_VALID_KEY_INITIALS = 'featurized_train_test_valid'

    def __init__(self,
                 X,  # DataFrame
                 y=None,  # DataFrame
                 X_valid=None,  # DataFrame
                 y_valid=None,  # DataFrame
                 sample_weight=None,
                 sample_weight_valid=None,
                 x_raw_column_names=None,
                 cv_splits_indices=None,
                 num_cv_folds=None,
                 n_step=None,
                 validation_size=None,
                 timeseries=False,
                 timeseries_param_dict=None,
                 cache_store=None,
                 logger=logging.getLogger(__name__),
                 task_type=None,
                 X_raw_cleaned=None,
                 y_raw_cleaned=None,
                 X_valid_raw_cleaned=None,
                 y_valid_raw_cleaned=None,
                 data_snapshot_str=""):
        """
        Construct the TransformerDataContext class.

        :param X: Input training data.
        :type X: pandas.DataFrame
        :param y: Input training labels.
        :type y: numpy.ndarray or pandas.DataFrame
        :param X_valid: validation data.
        :type X_valid: pandas.DataFrame
        :param y_valid: validation labels.
        :type y_valid: numpy.ndarray or pandas.DataFrame
        :param sample_weight: Sample weights for training data.
        :type sample_weight: numpy.ndarray or pandas.DataFrame
        :param sample_weight_valid: validation set sample weights.
        :type sample_weight_valid: numpy.ndarray or pandas.DataFrame
        :params x_raw_column_names: raw feature names of X data.
        :type x_raw_column_names: numpy.ndarray
        :param cv_splits_indices: Custom indices by which to split the data when running cross validation.
        :type cv_splits_indices: numpy.ndarray or pandas.DataFrame
        :param num_cv_folds: Number of cross validation folds
        :type num_cv_folds: integer
        :param n_step: Stepsize of cross validation in forecasting
        :type n_step: integer
        :param validation_size: Fraction of data to be held out for validation
        :type validation_size: Float
        :param cache_store: cache store to use for caching transformed data. None means don't cache.
        :type cache_store: CacheStore
        :param logger: module logger
        :type logger: logger
        :param X_raw_cleaned: Cleaned input training data.
        :type X_raw_cleaned: numpy.ndarray or pandas.DataFrame
        :param y_raw_cleaned: Cleaned input training labels.
        :type y_raw_cleaned: numpy.ndarray or pandas.DataFrame
        :param X_valid_raw_cleaned: Cleaned input validation data.
        :type X_valid_raw_cleaned: numpy.ndarray or pandas.DataFrame
        :param y_valid_raw_cleaned: Cleaned input validation labels.
        :type y_valid_raw_cleaned: numpy.ndarray or pandas.DataFrame
        :param data_snapshot_str: The input data snapshot string.
        :type data_snapshot_str: str
        """
        super().__init__(X=X,
                         y=y,
                         X_valid=X_valid,
                         y_valid=y_valid,
                         sample_weight=sample_weight,
                         sample_weight_valid=sample_weight_valid,
                         x_raw_column_names=x_raw_column_names,
                         cv_splits_indices=cv_splits_indices,
                         num_cv_folds=num_cv_folds,
                         n_step=n_step,
                         validation_size=validation_size,
                         X_raw_cleaned=X_raw_cleaned,
                         y_raw_cleaned=y_raw_cleaned,
                         X_valid_raw_cleaned=X_valid_raw_cleaned,
                         y_valid_raw_cleaned=y_valid_raw_cleaned,
                         data_snapshot_str=data_snapshot_str)
        self.cache_store = cache_store
        self.module_logger = logger
        if self.module_logger is None:
            self.module_logger = logging.getLogger(__name__)
            self.module_logger.propagate = False

        self._pickle_keys = ["X", "y", "X_valid", "y_valid",
                             "X_raw_cleaned", "y_raw_cleaned", "X_valid_raw_cleaned", "y_valid_raw_cleaned",
                             "sample_weight", "sample_weight_valid",
                             "x_raw_column_names", "cv_splits_indices", "transformers",
                             "cv_splits", "_on_demand_pickle_keys", "timeseries", "timeseries_param_dict",
                             'data_snapshot_str', 'output_snapshot_str',
                             "dataset_categoricals_dict", "learner_columns_mapping"]
        self._on_demand_pickle_keys = []    # type: List[str]
        self._num_workers = os.cpu_count()
        self.transformers = {}  # type: Dict[str, TransformerMixin]
        self.timeseries = timeseries
        self.timeseries_param_dict = timeseries_param_dict
        self.cv_splits = None  # type: Optional[_CVSplits]
        self.task_type = task_type

        # Initialize transformers and data_snapshot_str.
        # Currently, these are tightly coupled with other model wrappers. If this is
        # not set, many downstream assumptions will fail as they expect all keys to be present
        # and corresponding values to be none.
        self.output_snapshot_str = ""    # type: Optional[str]
        self._set_transformer(None, None, None)

        # This is the dataset_categoricals for the whole uber transformed dataset
        # This contains both label encoder and one hot encoder data. The keys will be different
        # types - X, X_valid, or CV.
        self.dataset_categoricals_dict = {}  # type: Dict[str, List[int]]

        # Mapping of learners and column indices for X, X_valid, CV
        self.learner_columns_mapping = {}  # type: Dict[str, Dict[str, List[int]]]

    def _get_picklable(self, data):
        """Wrap data to make it picklable if it is a Dataflow object."""
        if isinstance(data, Dataflow):
            return PicklableDataflow(data)
        return data

    def _unwrap_picklable(self, data):
        """Unwrap picklable data in case it is a DataFlow object."""
        if isinstance(data, PicklableDataflow):
            return data.get_dataflow()
        return data

    def __getstate__(self):
        """
        Get this transform data context's state, removing unserializable objects in the process.

        :return: a dict containing serializable state.
        """
        # Dataflow is currently unpickle-able. Convert it into a pickelable dataflow before persisting
        return {'X': self._get_picklable(self.X),
                'y': self.y,
                'X_valid': self._get_picklable(self.X_valid),
                'y_valid': self.y_valid,

                'X_raw_cleaned': self._get_picklable(self.X_raw_cleaned),
                'y_raw_cleaned': self.y_raw_cleaned,
                'X_valid_raw_cleaned': self._get_picklable(self.X_valid_raw_cleaned),
                'y_valid_raw_cleaned': self.y_valid_raw_cleaned,

                'sample_weight': self.sample_weight,
                'sample_weight_valid': self.sample_weight_valid,
                'x_raw_column_names': self.x_raw_column_names,
                'cv_splits_indices': self.cv_splits_indices,
                'num_cv_folds': self.num_cv_folds,
                'n_step': self.n_step,
                'validation_size': self.validation_size,
                'timeseries': self.timeseries,
                'timeseries_param_dict': self.timeseries_param_dict,

                '_pickle_keys': self._pickle_keys,
                'transformers': self.transformers,
                'cv_splits': self.cv_splits,
                '_on_demand_pickle_keys': self._on_demand_pickle_keys,
                'dataset_categoricals_dict': self.dataset_categoricals_dict,
                'learner_columns_mapping': self.learner_columns_mapping,
                '_num_workers': self._num_workers,
                'data_snapshot_str': self.data_snapshot_str,
                'output_snapshot_str': self.output_snapshot_str,

                'cache_store': self.cache_store,
                'module_logger': None,
                'task_type': self.task_type}

    def __setstate__(self, state):
        """
        Deserialize this transform data context's state, using the default logger.

        :param state: dictionary containing object state
        :type state: dict
        """
        # X and X_valid could be of type Dataflows in case of streaming, in which case make sure to convert the
        # picklable Dataflow object back to Dataflow
        self.X = self._unwrap_picklable(state.get('X'))
        self.X_valid = self._unwrap_picklable(state.get('X_valid'))
        self.X_raw_cleaned = self._unwrap_picklable(state.get('X_raw_cleaned'))
        self.X_valid_raw_cleaned = self._unwrap_picklable(state.get('X_valid_raw_cleaned'))

        self.y = state['y']
        self.y_valid = state['y_valid']
        self.y_raw_cleaned = state['y_raw_cleaned']
        self.y_valid_raw_cleaned = state['y_valid_raw_cleaned']

        self.sample_weight = state['sample_weight']
        self.sample_weight_valid = state['sample_weight_valid']
        self.x_raw_column_names = state['x_raw_column_names']
        self.cv_splits_indices = state['cv_splits_indices']
        self.num_cv_folds = state['num_cv_folds']
        self.n_step = state['n_step']
        self.validation_size = state['validation_size']
        self.timeseries = state['timeseries']
        self.timeseries_param_dict = state['timeseries_param_dict']

        self._pickle_keys = state['_pickle_keys']
        self.transformers = state['transformers']
        self.cv_splits = state['cv_splits']
        self._on_demand_pickle_keys = state['_on_demand_pickle_keys']
        self._num_workers = state['_num_workers']
        self.data_snapshot_str = state['data_snapshot_str']
        self.output_snapshot_str = state['output_snapshot_str']

        self.module_logger = logging.getLogger(__name__)
        self.cache_store = state['cache_store']
        self.task_type = state['task_type']
        self.dataset_categoricals_dict = state.get('dataset_categoricals_dict')
        self.learner_columns_mapping = state.get('learner_columns_mapping')

    def _set_raw_data_snapshot_str(self, data_snapshot_str: Optional[str]) -> None:
        """Set the data snapshot for the raw data."""
        self.data_snapshot_str = data_snapshot_str

    def _get_raw_data_snapshot_str(self) -> Any:
        """Set the data snapshot for the raw data."""
        return self.data_snapshot_str

    def _set_output_snapshot_str(self, output_snapshot_str: str) -> None:
        """Set the output snapshot for the raw data."""
        self.output_snapshot_str = output_snapshot_str

    def _get_output_snapshot_str(self) -> Any:
        """Set the output snapshot for the raw data."""
        return self.output_snapshot_str

    def _get_raw_data_type(self) -> Optional[str]:
        if not self.data_snapshot_str:
            return None

        if 'pd.DataFrame' in self.data_snapshot_str:
            return inference.PandasParameterType
        elif 'np.array' in self.data_snapshot_str:
            return inference.NumpyParameterType
        else:
            return None

    def _set_transformer(self, x_transformer=None, y_transformer=None, ts_transformer=None):
        """
        Set the x and y transformers.

        :param x_transformer: transformer for x transformation.
        :param y_transformer: transformer for y transformation.
        :param ts_transformer: transformer for timeseries data transformation.
        """
        self.transformers[constants.Transformers.X_TRANSFORMER] = x_transformer
        self.transformers[constants.Transformers.Y_TRANSFORMER] = y_transformer
        self.transformers[constants.Transformers.TIMESERIES_TRANSFORMER] = ts_transformer

    def _set_dataset_categoricals(self, data_type: str, dataset_categoricals: List[int]) -> None:
        self.module_logger.info('in _set_dataset_categoricals type : {} len dataset categoricals {}'.format(
            data_type, len(dataset_categoricals)))

        self.dataset_categoricals_dict[data_type] = dataset_categoricals
        if self.transformers[constants.Transformers.X_TRANSFORMER] is not None:
            import numpy as np
            data_transformer = self.transformers[constants.Transformers.X_TRANSFORMER]
            if data_transformer._get_categorical_indicators_label_featured_columns():
                indices_to_consider_cat = np.nonzero(data_transformer._columns_to_consider_for_cat_learners)[0]
                indices_to_consider_non_cat = np.nonzero(data_transformer._columns_to_consider_for_non_cat_learners)[0]
                self._set_columns_to_keep(constants.LearnerColumns.CatIndicatorLearners, data_type,
                                          list(indices_to_consider_cat))
                self._set_columns_to_keep(constants.LearnerColumns.DefaultLearners, data_type,
                                          list(indices_to_consider_non_cat))

    def _get_dataset_categoricals(self, data_type: str) -> Optional[List[int]]:
        if self.dataset_categoricals_dict.get(data_type):
            return self.dataset_categoricals_dict.get(data_type)
        else:
            return None

    def _set_columns_to_keep(self, learner: str, data_type: str, columns: List[int]) -> None:
        self.module_logger.info('Learner {}  for data type {} number of columns to consider {} '.format(
            learner, data_type, len(columns)))

        if not self.learner_columns_mapping.get(learner):
            self.learner_columns_mapping[learner] = {}

        self.learner_columns_mapping[learner][data_type] = columns

    def _get_columns_to_keep(self, learner: str) -> Optional[Dict[str, List[int]]]:
        if self.learner_columns_mapping.get(learner):
            return self.learner_columns_mapping.get(learner)
        else:
            return None

    def _is_cross_validation_scenario(self) -> bool:
        """Return 'True' if cross-validation was configured by user."""
        return self.X_valid is None

    def _is_autofeaturization_scenario(self) -> bool:
        # Return 'True' if no cross-validation was configured by user.
        # and no validation dataset was given
        # If 'True' The given run is an autofeaturization run
        return self.num_cv_folds is None \
            and self.cv_splits_indices is None \
            and self.X_valid is None

    def _get_engineered_feature_names(self):
        """Get the enigneered feature names available in different transformer."""
        if self.transformers[constants.Transformers.TIMESERIES_TRANSFORMER] is not None:
            return self.transformers[constants.Transformers.TIMESERIES_TRANSFORMER].get_engineered_feature_names()
        elif self.transformers[constants.Transformers.X_TRANSFORMER] is not None:
            return self.transformers[constants.Transformers.X_TRANSFORMER].get_engineered_feature_names()
        else:
            return self.x_raw_column_names

    def _refit_transformers(self, X, y):
        """Refit raw training data on the transformers."""
        if self.transformers[constants.Transformers.X_TRANSFORMER] is not None:
            self.transformers[constants.Transformers.X_TRANSFORMER].fit(X, y)

    def _clear_cache(self) -> None:
        """Clear the in-memory cached data to lower the memory consumption."""
        self.X = None
        self.y = None
        self.X_valid = None
        self.y_valid = None
        self.X_raw_cleaned = None
        self.y_raw_cleaned = None
        self.X_valid_raw_cleaned = None
        self.y_valid_raw_cleaned = None
        self.sample_weight = None
        self.sample_weight_valid = None
        self.x_raw_column_names = None
        self.cv_splits_indices = None
        self.transformers = {}
        self.cv_splits = None
        self.data_snapshot_str = None
        self.output_snapshot_str = None
        self._on_demand_pickle_keys = []
        self.dataset_categoricals_dict = {}
        self.learner_columns_mapping = {}

    def _update_cache(self) -> None:
        """Update the cache based on run id."""
        keys = []   # type: List[str]
        values = []     # type: List[Any]
        for k in self._pickle_keys:
            keys.append(k)
            values.append(self.__dict__.get(k))
        self.cache_store.add(keys, values)

    def _update_cache_with_featurized_data(self, featurized_data_key: str, featurized_data: Any) -> None:
        """
        Update the cache with the featurized data.

        :param featurized_data_key: pickle key
        :param featurized_data: featurized data
        """
        self._on_demand_pickle_keys.append(featurized_data_key)

        self._add_to_cache(featurized_data_key, featurized_data)
        if self.module_logger:
            self.module_logger.info('Adding pickle key: {}'.format(featurized_data_key))

    def _add_to_cache(self, k: str, value: Optional[Any] = None) -> None:
        """
        Add the contents of transformed data to cache.

        :param k: pickle key
        :param value: data to be added to the cache
        """
        if k in self.__dict__:
            self.cache_store.add([k], [self.__dict__.get(k)])
        elif value is not None:
            self.cache_store.add([k], [value])

    def _get_num_cv_splits(self) -> int:
        if self._on_demand_pickle_keys is None:
            n_cv = 0
        else:
            n_cv = sum([1 if "cv" in key else 0 for key in self._on_demand_pickle_keys])
        return n_cv

    def cleanup(self) -> None:
        """Clean up the cache."""
        try:
            # unload deletes the files
            self.cache_store.unload()
        except IOError:
            self.module_logger.warning("Failed to unload the cache store.")

    def _check_if_y_label_has_single_occurrence_class(self) -> bool:
        single_occurrence_class_detected = False
        if self.task_type == constants.Tasks.CLASSIFICATION:
            self.module_logger.info("Checking single occurrence class condition for entire training data")
            try:
                single_occurrence_class_detected |= \
                    _check_if_column_has_single_occurrence_value(
                        self.y, logger=self.module_logger)
            except Exception:
                pass

            if self.cv_splits is not None and self.cv_splits.get_cv_split_indices() is not None:
                cv_index = 0
                for train_ind, test_ind in self.cv_splits.get_cv_split_indices():
                    self.module_logger.info(
                        "Checking single occurrence class condition for cross validation {0} training data".format(
                            cv_index))
                    try:
                        single_occurrence_class_detected |= \
                            _check_if_column_has_single_occurrence_value(self.y[train_ind],
                                                                         logger=self.module_logger)
                    except Exception:
                        pass

                    cv_index += 1

        return single_occurrence_class_detected

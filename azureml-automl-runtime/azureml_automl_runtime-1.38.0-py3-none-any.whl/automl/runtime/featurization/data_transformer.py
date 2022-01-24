# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Preprocessing class that can be added in pipeline for input."""
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

import json
import logging
import os

import numpy as np
import pandas as pd
import pandas.api as api

from scipy import sparse
from sklearn.pipeline import Pipeline
from sklearn_pandas import DataFrameMapper

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty

from azureml.automl.core import _codegen_utilities
from azureml.automl.core._experiment_observer import (
    ExperimentStatus,
    ExperimentObserver,
    NullExperimentObserver,
)
from azureml.automl.core.constants import TextNeuralNetworks
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.shared import constants, logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    DatasetsFeatureCountMismatch,
    FeaturizationConfigParamOverridden,
    InconsistentColumnTypeInTrainValid,
    InsufficientMemory,
    MissingColumnsInData
)
from azureml.automl.core.shared.exceptions import (
    AutoMLException,
    ConfigException,
    DataException,
    FitException,
    ResourceException,
    TransformException,
)
from azureml.automl.core.shared.pickler import DefaultPickler
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.transformer_runtime_exceptions import DataTransformerUnknownTaskException
from azureml.automl.runtime._engineered_feature_names import (
    _GenerateEngineeredFeatureNames,
)
from azureml.automl.runtime.column_purpose_detection import StatsAndColumnPurposeType
from azureml.automl.runtime.featurization import data_transformer_utils
from azureml.automl.runtime.featurization_info_provider import FeaturizationInfoProvider
from azureml.automl.runtime.featurizer.transformer.categorical import LabelEncoderTransformer
from azureml.automl.runtime.shared import memory_utilities, utilities as runtime_utilities
from azureml.automl.runtime.shared.types import (
    DataInputType,
    DataSingleColumnInputType,
    FeaturizationSummaryType,
)

from ._featurized_data_combiners import FeaturizedDataCombiners
from ._featurizer_container import FeaturizerContainer
from .generic_transformer import GenericTransformer
from .text_transformer import TextTransformer
from .transformer_and_mapper import TransformerAndMapper
from ..featurizer.transformer import AutoMLTransformer, featurization_utilities
from ..stats_computation import PreprocessingStatistics as _PreprocessingStatistics

_logger = logging.getLogger(__name__)


class DataTransformer(AutoMLTransformer, FeaturizationInfoProvider):
    """
    Preprocessing class that can be added in pipeline for input.

    This class does the following:
    1. Numerical inputs treated as it is.
    2. For dates: year, month, day and hour are features
    3. For text, tfidf features
    4. Small number of unique values for a column that is not float become
        categoricals

    :param task: 'classification' or 'regression' depending on what kind of
    ML problem to solve.
    :param is_onnx_compatible: if works in onnx compatible mode.
    """

    DEFAULT_DATA_TRANSFORMER_TIMEOUT_SEC = 3600 * 24  # 24 hours
    UNSUPPORTED_PARAMETER_WARNING_MSG = (
        "Unsupported parameter passed to {t}, proceeding with default values"
    )
    FIT_FAILURE_MSG = "Failed while fitting learned transformations."
    TRANSFORM_FAILURE_MSG = "Failed while applying learned transformations."

    def __init__(
            self,
            task: Optional[str] = constants.Tasks.CLASSIFICATION,
            is_onnx_compatible: bool = False,
            observer: Optional[ExperimentObserver] = None,
            enable_feature_sweeping: bool = False,
            enable_dnn: bool = True,
            force_text_dnn: bool = False,
            feature_sweeping_timeout: int = DEFAULT_DATA_TRANSFORMER_TIMEOUT_SEC,
            featurization_config: Optional[FeaturizationConfig] = None,
            is_cross_validation: bool = False,
            feature_sweeping_config: Dict[str, Any] = {},
            working_dir: Optional[str] = None,
            enable_categorical_indicators: bool = False
    ) -> None:
        """
        Initialize for data transformer for pre-processing raw user data.

        :param task: 'classification' or 'regression' depending on what kind
        of ML problem to solve.
        :type task: str or azureml.train.automl.constants.Tasks
        :param is_onnx_compatible: If works in onnx compatible mode.
        :param enable_feature_sweeping: Whether to run feature sweeping or not.
        :param enable_dnn: Flag to enable neural networks for forecasting and natural language processing.
        :param force_text_dnn: Flag to force add dnn's for natural language processing via feature sweeping.
        :param feature_sweeping_timeout: Max time to run feature sweeping.
        :param featurization_config: Configuration used for custom featurization.
        :param is_cross_validation: Whether to do the cross validation.
        :param feature_sweeping_config: Feature sweeping config.
        :param working_dir: the working directory to use for temporary files.
        """
        super().__init__()
        self._is_inference_time = False
        self._has_fit_been_called_and_succeeded = False
        if task not in constants.Tasks.ALL:
            raise DataTransformerUnknownTaskException(
                "Unknown task",
                has_pii=False,
                reference_code=ReferenceCodes._DATA_TRANSFORMER_UNKNOWN_TASK,
            )

        self.working_directory = working_dir or os.getcwd()
        self._task_type = task or constants.Tasks.CLASSIFICATION
        self._is_onnx_compatible = is_onnx_compatible
        self._is_text_dnn = False
        # mapper is retained for backward compatibility because previously DataTransformer used it
        # when ONNX was enabled.
        self.mapper = None  # type: Optional[DataFrameMapper]
        # list of TransformerAndMapper objects
        self.transformer_and_mapper_list = []  # type: List[TransformerAndMapper]
        # Maintain a list of raw feature names
        self._raw_feature_names = []  # type: List[str]
        # Maintain engineered feature name class
        self._engineered_feature_names_class = _GenerateEngineeredFeatureNames()
        # Maintain statistics about the pre-processing stage
        self._pre_processing_stats = None  # type: Optional[_PreprocessingStatistics]
        # Text transformer
        self._text_transformer = None  # type: Optional[TextTransformer]
        # Stats and column purpose
        self.stats_and_column_purposes = (
            None
        )  # type: Optional[List[StatsAndColumnPurposeType]]

        # Enable categorical indicators feature
        self._enable_categorical_indicators = enable_categorical_indicators

        # Dict that maps raw categorical feature name to the number of unique values in that column
        self._raw_categorical_features_unique_count_dict = {}  # type: Dict[str, int]

        # Following is a list of cat columns label encoder feature names
        self._categorical_indicators_label_feature_column_names = []  # type: Optional[List[str]]

        # Following is a list of cat columns non label encoder feature names
        self._categorical_indicators_nonlabel_feature_column_names = []  # type: Optional[List[str]]

        # Indicating what columns need to be considered for categorical and non categorical learners.
        # This is to filter from the transformed data that has both one hot and label encoder.
        # This is used for the column transfomer in the pipeline.
        self._columns_to_consider_for_cat_learners = []   # type: Optional[List[int]]
        self._columns_to_consider_for_non_cat_learners = []  # type: Optional[List[int]]

        # Generic transformer
        # TODO Need to enable this later
        self._generic_transformer = None  # type: Optional[GenericTransformer]
        self._observer = observer or NullExperimentObserver()  # type: ExperimentObserver
        self._enable_feature_sweeping = enable_feature_sweeping
        self._enable_dnn = enable_dnn
        self._force_text_dnn = force_text_dnn
        self._feature_sweeping_config = feature_sweeping_config
        self._feature_sweeping_timeout = feature_sweeping_timeout
        self._is_cross_validation = is_cross_validation

        _logger.info("Feature sweeping enabled: {}".format(self._enable_feature_sweeping))
        _logger.info("Feature sweeping timeout: {}".format(self._feature_sweeping_timeout))

        # Used for injecting test transformers.
        self._test_transforms = []  # type: List[Any]
        self._columns_types_mapping = None  # type: Optional[Dict[str, np.dtype]]
        self._featurization_config = featurization_config
        self._feature_sweeped = False
        from azureml.automl.runtime.sweeping.meta_sweeper import MetaSweeper

        self._feature_sweeper = None  # type: Optional[MetaSweeper]
        # empty featurizer list
        self._featurizer_container = FeaturizerContainer(featurizer_list=[])

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        return {
            "task": self._task_type,
            "is_onnx_compatible": self._is_onnx_compatible,
            "enable_feature_sweeping": self._enable_feature_sweeping,
            "enable_dnn": self._enable_dnn,
            "force_text_dnn": self._force_text_dnn,
            "feature_sweeping_timeout": self._feature_sweeping_timeout,
            "featurization_config": self._featurization_config,
            "is_cross_validation": self._is_cross_validation,
            "feature_sweeping_config": self._feature_sweeping_config,
            "observer": None,
            "working_dir": self.working_directory
        }

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        params.pop("observer", None)
        params.pop("working_dir", None)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    @logging_utilities.function_debug_log_wrapped()
    def fit(
            self, df: DataInputType, y: Optional[DataSingleColumnInputType] = None
    ) -> "DataTransformer":
        """
        Perform the raw data validation and identify the transformations to apply.

        :param df: The input data object representing text, numerical or categorical input.
        :param y: The target column data.
        :return: The DataTransformer object.
        :raises: FitException if fitting the learned transformations fail.
        """
        self._is_inference_time = False
        self._has_fit_been_called_and_succeeded = False
        runtime_utilities.check_input(df)
        if isinstance(df, np.ndarray):
            df = pd.DataFrame(df)

        fitted_featurizer_indices = {
            featurizer.index
            for featurizer in self._featurizer_container
            if featurizer.is_cached
        }

        if self.mapper is not None and not self.transformer_and_mapper_list:
            try:
                fitted_featurizers = {}
                for index in range(len(self.mapper.features)):
                    if index in fitted_featurizer_indices:
                        featurizer = self.mapper.features[index]
                        fitted_featurizers[index] = featurizer
                        # replace the featurizer in the mapper with a copy that will not be re-fitted.
                        self.mapper.features[
                            index
                        ] = data_transformer_utils.get_feature_that_avoids_refitting(
                            featurizer
                        )
                self.mapper.fit(df, y)
                for index in fitted_featurizers:
                    # restore the mapper with the previously fitted featurizers.
                    self.mapper.features[index] = fitted_featurizers[index]
            except AutoMLException:
                raise
            except MemoryError as e:
                raise ResourceException._with_error(
                    AzureMLError.create(
                        InsufficientMemory,
                        target="MapperFit",
                        reference_code=ReferenceCodes._DATA_TRANSFORMER_FIT_MAPPER_MEMORYERROR,
                    ),
                    inner_exception=e,
                ) from e
            except Exception as ex:
                fit_exception = FitException.from_exception(
                    ex,
                    msg=self.FIT_FAILURE_MSG,
                    target="DataTransformer",
                    has_pii=False,
                    reference_code=ReferenceCodes._DATA_TRANSFORMER_FIT_ONNX_COMPATIBLE,
                )  # type: Exception
                raise fit_exception
            return self

        if not self.transformer_and_mapper_list:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty,
                    target="transformer_and_mapper_list",
                    argument_name="transformer_and_mapper_list",
                    reference_code=ReferenceCodes._DATA_TRANSFORMER_FIT_FEATCONFIG_NONE,
                )
            )

        for index in range(len(self.transformer_and_mapper_list)):
            transformer_mapper = self.transformer_and_mapper_list[index]
            self._set_is_text_dnn_if_available(transformer_mapper)
            if index not in fitted_featurizer_indices:  # we haven't already fitted
                self.fit_individual_transformer_mapper(transformer_mapper, df, y)

        # TODO: Replace with sklearn.utils.validation.check_is_fitted
        self._has_fit_been_called_and_succeeded = True

        if self._enable_categorical_indicators:
            if isinstance(df, np.ndarray):
                df = pd.DataFrame(df)

            # This is a workaround to get the transformer names without having to do this in transform
            for index in range(len(self.transformer_and_mapper_list)):
                transformer_mapper = self.transformer_and_mapper_list[index]
                transformer_mapper.mapper.transform(df.iloc[:1])
            self._set_categorical_indicators_featured_columns()

        return self

    def fit_individual_transformer_mapper(
            self,
            transformer_mapper: TransformerAndMapper,
            df: DataInputType,
            y: Optional[DataSingleColumnInputType] = None,
    ) -> None:
        is_text_dnn = self._get_is_text_dnn()
        if is_text_dnn:
            self._observer.report_status(
                ExperimentStatus.TextDNNTraining,
                "Training a deep learning text model, this may take a while.",
            )

            has_observer = not isinstance(self._observer, NullExperimentObserver)

            # pt_dnn transformers require an instance of the current run to log progress
            if self._get_is_BERT(transformer_mapper) and has_observer:
                pt_dnn = transformer_mapper.transformers.steps[-1][-1]  # type: ignore
                pt_dnn.observer = self._observer

        try:
            transformer_mapper.mapper.fit(df, y)
        except AutoMLException:
            raise
        except MemoryError as e:
            raise ResourceException._with_error(
                AzureMLError.create(
                    InsufficientMemory,
                    target="TransformerMapperFit",
                    reference_code=ReferenceCodes._DATA_TRANSFORMER_FIT_DATAFRAME_MAPPER_MEMORYERROR,
                ),
                inner_exception=e,
            ) from e
        except Exception as ex:
            if isinstance(ex, ValueError) and (
                    "After pruning, no terms remain. Try a lower min_df or a higher max_df."
                    in ex.args[0]
            ):
                # TODO: Below is fix for bug #611949.
                #  Need to have a complete solution for TfIdf parameter adjustments: Work item #617820
                _logger.info(
                    "TfIdf ValueError caused by adjusted min_df or max_df. Retrying fit with default value."
                )
                try:
                    from sklearn.feature_extraction.text import TfidfVectorizer

                    for tr in transformer_mapper.mapper.features[0][1]:
                        if isinstance(tr, TfidfVectorizer):
                            if tr.max_df < 1.0:
                                tr.max_df = 1.0
                            if tr.min_df != 1:
                                tr.min_df = 1
                    transformer_mapper.mapper.fit(df, y)
                except Exception:
                    fit_exception = FitException.from_exception(
                        ex,
                        msg="Re-running fit using default min_df and max_df failed.",
                        target="DataTransformer",
                        has_pii=False,
                        reference_code=ReferenceCodes._DATA_TRANSFORMER_FIT_RERUN,
                    )
                    raise fit_exception from None
            else:
                self._check_transformer_param_error(
                    ex, True, transformer_mapper, self._featurization_config
                )
                raise FitException.from_exception(
                    ex,
                    msg=self.FIT_FAILURE_MSG,
                    target="DataTransformer.fit",
                    has_pii=False,
                    reference_code=ReferenceCodes._DATA_TRANSFORMER_FIT_LEARNED,
                )

        if is_text_dnn:
            self._observer.report_status(
                ExperimentStatus.TextDNNTrainingCompleted,
                "Completed training a deep learning text model.",
            )

        steps = (
            transformer_mapper.transformers.steps
            if isinstance(transformer_mapper.transformers, Pipeline)
            else transformer_mapper.transformers
        )

        transform_count = len(steps)
        if transform_count == 0:
            return
        # Only last transformer gets applied, all other are input to next transformer.
        last_transformer = steps[transform_count - 1]
        last_transformer = (
            last_transformer[1]
            if isinstance(last_transformer, tuple) and len(last_transformer) > 1
            else last_transformer
        )
        memory_estimate = (
            0
            if not issubclass(type(last_transformer), AutoMLTransformer)
            else last_transformer.get_memory_footprint(df, y)
        )
        transformer_mapper.memory_footprint_estimate = memory_estimate

    @logging_utilities.function_debug_log_wrapped()
    def transform(
            self, df: DataInputType
    ) -> Union[pd.DataFrame, np.ndarray, sparse.spmatrix]:
        """
        Transform the input raw data with the transformations idetified in fit stage.

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: numpy.ndarray or pandas.DataFrame
        :return: Numpy array.
        """
        if not self._has_fit_been_called_and_succeeded:
            raise TransformException(
                "fit not called",
                has_pii=False,
                reference_code=ReferenceCodes._DATA_TRANSFORMER_TRANSFROM_NOT_CALL_FIT,
            )

        runtime_utilities.check_input(df)
        if isinstance(df, np.ndarray):
            df = pd.DataFrame(df)

        if self._columns_types_mapping is not None:
            df = self._check_columns_names_and_convert_types(
                df, self._columns_types_mapping
            )

        features = []  # type: List[Any]
        try:
            features = self._apply_transforms(df)
        except AutoMLException:
            raise
        except MemoryError as e:
            raise ResourceException._with_error(
                AzureMLError.create(
                    InsufficientMemory,
                    target="ApplyTransforms",
                    reference_code=ReferenceCodes._DATA_TRANSFORMER_TRANSFORM_MEMORYERROR,
                ),
                inner_exception=e,
            ) from e
        except Exception as ex:
            raise TransformException.from_exception(
                ex,
                msg=self.TRANSFORM_FAILURE_MSG,
                target="DataTransformer.transform",
                reference_code=ReferenceCodes._DATA_TRANSFORMER_TRANSFROM_LEARNED,
                has_pii=False,
            )

        if self._engineered_feature_names_class is not None:
            if (
                    not self._engineered_feature_names_class.are_engineered_feature_names_available()
            ):
                # Generate engineered feature names if they are not already generated
                if self.mapper is not None:
                    self._engineered_feature_names_class.parse_raw_feature_names(
                        self.mapper.transformed_names_
                    )
                else:
                    names = []  # type: List[str]
                    # TODO: Why do engineered feature names need `transform` to happen? `fit` should be sufficient!
                    for transformer_mapper in self.transformer_and_mapper_list:
                        names.extend(transformer_mapper.mapper.transformed_names_)
                    self._engineered_feature_names_class.parse_raw_feature_names(names)

        is_there_a_sparse_column = any(sparse.issparse(fea) for fea in features)
        combiner = FeaturizedDataCombiners.get(
            is_there_a_sparse_column,
            self._is_inference_time,
            memory_utilities._is_low_memory(),
        )

        ret = combiner(
            features,
            **{"working_directory": self.working_directory, "pickler": DefaultPickler()}
        )  # type: Union[pd.DataFrame, np.ndarray, sparse.spmatrix]
        return ret

    def _get_is_text_dnn(self) -> bool:
        return self._is_text_dnn

    def _set_is_text_dnn_if_available(self, transformer_mapper: TransformerAndMapper) -> bool:
        # determine if a transform is a text dnn or not
        try:
            cname = transformer_mapper.transformers.steps[-1][-1].__class__.__name__  # type: ignore
            if cname in TextNeuralNetworks.ALL_CLASS_NAMES:
                self._is_text_dnn = True
        except Exception:
            pass
        return self._is_text_dnn

    @staticmethod
    def _get_is_BERT(transformer_mapper: TransformerAndMapper) -> bool:

        is_text_dnn = False
        try:
            text_dnn = transformer_mapper.transformers.steps[-1][-1]          # type: ignore
            is_text_dnn = (text_dnn.__class__.__name__ is TextNeuralNetworks.BERT_CLASS_NAME)
        except Exception:
            pass
        return is_text_dnn

    @staticmethod
    def _get_is_label_encoder(transformer_mapper: TransformerAndMapper) -> bool:
        is_cat = False
        try:
            cat = transformer_mapper.transformers[-1]        # type: DataTransformer
            is_cat = isinstance(cat, LabelEncoderTransformer)
        except Exception:
            pass
        return is_cat

    def _apply_transforms(
            self, df: pd.DataFrame
    ) -> List[Union[np.ndarray, pd.DataFrame, sparse.spmatrix]]:
        features = []

        if self.mapper is not None:
            transformed_data = self.mapper.transform(df)
            features.append(transformed_data)
        else:
            total_ram = memory_utilities.get_all_ram()
            _logger.info(
                "Starting to apply transforms. Total ram: {} bytes".format(total_ram)
            )
            for transformer_mapper in self.transformer_and_mapper_list:
                current_available_physical_memory = (
                    memory_utilities.get_available_physical_memory()
                )
                transform_memory_footprint = (
                    transformer_mapper.memory_footprint_estimate
                )
                _logger.info(
                    "Transform memory estimate: {} bytes, Current available memory: {} bytes".format(
                        transform_memory_footprint, current_available_physical_memory
                    )
                )
                apply_transform = (transform_memory_footprint < current_available_physical_memory)

                transformer_list = featurization_utilities.get_transform_names(
                    transformer_mapper.transformers
                )
                transformer_names = ",".join(transformer_list)
                if apply_transform:
                    _logger.info("{}: Applying transform.".format(transformer_names))
                    try:
                        transform_output = transformer_mapper.mapper.transform(df)
                        features.append(transform_output)
                    except Exception as ex:
                        self._check_transformer_param_error(
                            ex,
                            False,
                            transformer_mapper=transformer_mapper,
                            featurization_config=self._featurization_config,
                        )
                        raise
                    _logger.info(
                        "{transformers}: Finished applying transform. Shape {shape}".format(
                            shape=transform_output.shape, transformers=transformer_names
                        )
                    )
                else:
                    _logger.info(
                        "{}: Transform not applied due to memory constraints.".format(
                            transformer_names
                        )
                    )
            _logger.info("Finished applying transforms")

        return features

    def _set_categorical_indicators_featured_columns(self) -> None:
        if not self.stats_and_column_purposes:
            return

        for x in self.stats_and_column_purposes:
            if x[1] == "Categorical":
                self._raw_categorical_features_unique_count_dict[x[2]] = x[0].num_unique_vals

        (self._categorical_indicators_label_feature_column_names,
         self._categorical_indicators_nonlabel_feature_column_names) = \
            self._get_categorical_indicators_featured_columns()

        self._columns_to_consider_for_cat_learners = self._get_columns_for_learners(cat_learners=True)
        self._columns_to_consider_for_non_cat_learners = self._get_columns_for_learners(cat_learners=False)

    def _get_categorical_indicators_label_featured_columns(self) -> Optional[List[str]]:
        return self._categorical_indicators_label_feature_column_names

    def _get_categorical_indicators_nonlabel_featured_columns(self) -> Optional[List[str]]:
        return self._categorical_indicators_nonlabel_feature_column_names

    def _get_dataset_categoricals(self) -> Optional[List[int]]:
        """ Helper method to denote categorical columns that are label encoded.
         This information will be used only for categorical indicators learners.
         0's denote non categorical and the non zero denotes categorical columns

         Returns dataset categoricals list or None
         """
        dataset_categoricals = []  # type: List[int]
        if len(self._raw_categorical_features_unique_count_dict) <= 0:
            return dataset_categoricals

        if self._enable_categorical_indicators:
            # get the list of categorical indicators
            for transformer_mapper in self.transformer_and_mapper_list:
                if(self._get_is_label_encoder(transformer_mapper)):
                    raw_column_name = transformer_mapper.mapper.features[0][0]

                    if raw_column_name in self._raw_categorical_features_unique_count_dict.keys():
                        unique_cat = self._raw_categorical_features_unique_count_dict[raw_column_name]
                        dataset_categoricals.extend([unique_cat]
                                                    * len(transformer_mapper.mapper.transformed_names_))
                    else:
                        dataset_categoricals.extend([0] * len(transformer_mapper.mapper.transformed_names_))
                else:
                    dataset_categoricals.extend([0] * len(transformer_mapper.mapper.transformed_names_))

            return dataset_categoricals
        else:
            return dataset_categoricals

    def _get_categorical_indicators_featured_columns(self) -> Tuple[Optional[List[str]], Optional[List[str]]]:
        """
            Helper method to get the categorical column feature names for cat indicators and non cat indicator learners
        """
        if self._enable_categorical_indicators:
            categorical_feature_names = []  # type: List[str]
            categorical_feature_names_to_drop = []  # type: List[str]
            raw_categorical_feature_names = list(self._raw_categorical_features_unique_count_dict.keys())

            # get the list of categorical indicators
            for transformer_mapper in self.transformer_and_mapper_list:
                if(self._get_is_label_encoder(transformer_mapper)):
                    categorical_feature_names.extend(transformer_mapper.mapper.transformed_names_)
                elif (not self._get_is_label_encoder(transformer_mapper) and transformer_mapper.mapper.features[0][0]
                      in raw_categorical_feature_names):
                    categorical_feature_names_to_drop.extend(transformer_mapper.mapper.transformed_names_)

            return categorical_feature_names, categorical_feature_names_to_drop
        else:
            return None, None

    def _get_columns_for_learners(self, cat_learners: bool = True) -> List[int]:
        """ This is helper method to get list of ints that denote what columns the learner should consider.
            It is a list of 0 and 1 and used in drop column transformer later.
        """
        columns_to_consider = []

        drop_columns_set = None  # type: Any
        if cat_learners:
            if self._categorical_indicators_nonlabel_feature_column_names:
                drop_columns_set = set(self._categorical_indicators_nonlabel_feature_column_names)
        else:
            if self._categorical_indicators_label_feature_column_names:
                drop_columns_set = set(self._categorical_indicators_label_feature_column_names)

        for transformer_mapper in self.transformer_and_mapper_list:
            if self._categorical_indicators_label_feature_column_names and \
                    self._categorical_indicators_nonlabel_feature_column_names:
                if set(transformer_mapper.mapper.transformed_names_).issubset(drop_columns_set):
                    columns_to_consider.extend([0] * len(transformer_mapper.mapper.transformed_names_))
                else:
                    columns_to_consider.extend([1] * len(transformer_mapper.mapper.transformed_names_))
            else:
                columns_to_consider.extend([1] * len(transformer_mapper.mapper.transformed_names_))
        return columns_to_consider

    def set_cached_featurizers(
            self, featurizer_index_mapping: Mapping[int, Any]
    ) -> None:
        """
        Overwrite featurizers in mapper.features or transformer_and_mapper_list that have
        already been fitted.

        :param featurizer_index_mapping: A mapping of indices to fitted featurizers that were pulled from the cache.
        :return: None.
        """
        if self.mapper is not None:
            for index in featurizer_index_mapping:
                self.mapper.features[index] = featurizer_index_mapping[index]
        else:
            for index in featurizer_index_mapping:
                self.transformer_and_mapper_list[index] = featurizer_index_mapping[
                    index
                ]

    def get_engineered_feature_names(self) -> List[str]:
        """
        Get the engineered feature names.

        Return the list of engineered feature names as string after data transformations on the
        raw data have been finished.

        :return: The list of engineered fearure names as strings
        """
        if self._engineered_feature_names_class is None:
            self._engineered_feature_names_class = _GenerateEngineeredFeatureNames()
        return self._engineered_feature_names_class._engineered_feature_names

    def _get_json_str_for_engineered_feature_name(
            self, engineered_feature_name: str
    ) -> Optional[str]:
        """
        Return JSON string for engineered feature name.

        :param engineered_feature_name: Engineered feature name for whom JSON string is required
        :return: JSON string for engineered feature name
        """
        if self._engineered_feature_names_class is None:
            self._engineered_feature_names_class = _GenerateEngineeredFeatureNames()

        # fmt: off
        engineered_feature_name_json_obj = self._engineered_feature_names_class. \
            get_json_object_for_engineered_feature_name(engineered_feature_name)
        # fmt: on

        # If the JSON object is not valid, then return None
        if engineered_feature_name_json_obj is None:
            _logger.info("Engineered feature name json object is None.")
            return None

        # Convert JSON into string and return
        return json.dumps(engineered_feature_name_json_obj)

    def get_stats_feature_type_summary(
            self, raw_column_name_list: Optional[List[str]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Return column stats and feature type summary.
        :param raw_column_name_list: List of raw column names.
        :return: List of stats and feature type summary for each input raw column.
        """

        if self.stats_and_column_purposes is None:
            return None
        else:
            filtered_stats_and_column_purposes = self.stats_and_column_purposes
            if raw_column_name_list is not None:
                filtered_stats_and_column_purposes = [
                    x
                    for x in self.stats_and_column_purposes
                    if x[2] in raw_column_name_list
                ]
            return list(
                map(
                    lambda x: dict(
                        (
                            ("statistic", x[0].__str__()),
                            ("feature type", x[1]),
                            ("column name", x[2]),
                        )
                    ),
                    filtered_stats_and_column_purposes,
                )
            )

    def get_featurization_summary(self, **kwargs: Any) -> FeaturizationSummaryType:
        """
        Return the featurization summary for all the input features seen by DataTransformer.
        :param kwargs:
            See below
        :Keyword Arguments:
            * is_user_friendly (``bool``) --
                If True, return individual transformer params as well,
                otherwise, only return the detailed featurization summary.
        :return: List of featurization summary for each input feature.
        """
        is_user_friendly = kwargs.get('is_user_friendly', True)
        if self._engineered_feature_names_class is None:
            self._engineered_feature_names_class = _GenerateEngineeredFeatureNames()
        return (
            self._engineered_feature_names_class.get_raw_features_featurization_summary(
                is_user_friendly
            )
        )

    @property
    def get_column_names_and_types(self) -> Optional[Dict[str, np.dtype]]:
        """
        Return the column name and the dtype mapping for each input raw column.
        """
        return self._columns_types_mapping

    @staticmethod
    def _check_columns_names_and_convert_types(
            df: pd.DataFrame, columns_types_mapping: Dict[str, np.dtype]
    ) -> pd.DataFrame:
        """
        Check given data to see if column names and number of features line up
        with fitted data before going through data transformation

        :param df: input data to check.
        :param columns_types_mapping: column types from fitted data
        :return data to be used on transformation
        """
        curr_columns_types_mapping = (
            data_transformer_utils.get_pandas_columns_types_mapping(df)
        )
        if len(curr_columns_types_mapping) != len(columns_types_mapping):
            raise DataException._with_error(
                AzureMLError.create(
                    DatasetsFeatureCountMismatch,
                    target="X",
                    first_dataset_name="fitted data",
                    first_dataset_shape=len(columns_types_mapping),
                    second_dataset_name="input data",
                    second_dataset_shape=len(curr_columns_types_mapping),
                    reference_code=ReferenceCodes._DATA_TRANSFORMER_TRANSFROM_WRONG_COLUMN,
                )
            )

        for curr_col, curr_col_type in curr_columns_types_mapping.items():
            if curr_col not in columns_types_mapping:
                raise DataException._with_error(
                    AzureMLError.create(
                        MissingColumnsInData,
                        target="X",
                        columns=curr_col,
                        data_object_name="fitted data",
                        reference_code=ReferenceCodes._DATA_TRANSFORMER_TRANSFROM_COLUMN_NOT_FOUND,
                    )
                )

            col_type = columns_types_mapping[curr_col]
            if curr_col_type != col_type:
                # Try and see if the columns are convertible
                try:
                    if api.types.is_numeric_dtype(col_type) and not api.types.is_numeric_dtype(curr_col_type):
                        # if training data is numeric but valid data contains non-numeric values,
                        # then make those non-numeric values to be NaNs
                        df[curr_col] = pd.to_numeric(df[curr_col], errors='coerce')
                        if df[curr_col].isna().values.all(axis=0):
                            raise Exception("Attempted to convert non-numeric column to numeric to match"
                                            " fitted data column type but none of the data contained numeric value")
                        else:
                            _logger.warning("Data passed in to transform contains non-numeric column that do not match"
                                            " fitted data column type. Converted to numeric and marking NaN for"
                                            " the ones that cannot be converted.")
                    else:
                        df[curr_col] = df[curr_col].astype(col_type)
                except Exception:
                    raise DataException._with_error(
                        AzureMLError.create(
                            InconsistentColumnTypeInTrainValid,
                            target="X",
                            reference_code=ReferenceCodes._DATA_TRANSFORMER_TRANSFROM_WRONG_COLUMN_TYPE,
                            column_name=curr_col,
                            train_dtype=col_type,
                            validation_dtype=curr_col_type,
                        )
                    )

        return df

    @staticmethod
    def _check_transformer_param_error(
            ex: BaseException,
            is_fit: bool,
            transformer_mapper: TransformerAndMapper,
            featurization_config: Optional[FeaturizationConfig] = None,
    ) -> None:
        if not featurization_config:
            return

        if featurization_utilities.is_transformer_param_overridden(
                featurization_config
        ):
            # there was a transformer parameter override that could have led to failure
            # Ideally transformer should throw error during initialization (e.g. CountVectorizer)
            # but some transformers verify the input later in the process
            # during fit or transform (e.g. Imputer).
            columns = list(transformer_mapper.mapper._selected_columns)

            try:
                for transformer in transformer_mapper.transformers:
                    if hasattr(transformer, "_transformer_name"):
                        transformer_name = transformer._transformer_name
                    else:
                        transformer_name = transformer.__class__.__name__
                    if featurization_utilities.get_transformer_params_by_column_names(
                            transformer_name, columns, featurization_config
                    ):
                        stage = "fitting" if is_fit else "applying"
                        raise ConfigException._with_error(
                            AzureMLError.create(
                                FeaturizationConfigParamOverridden,
                                target="DataTransformer",
                                stage=stage,
                                reference_code=ReferenceCodes._DATA_TRANSFORMER_TRANSFORMER_PARAM_ERROR,
                            )
                        )
            except AutoMLException:
                raise
            except Exception as e:
                # if check fails, then we raise Fit / Transform Exception instead from caller.
                logging_utilities.log_traceback(e, _logger, is_critical=False)

    def __getstate__(self):
        """
        Get state picklable objects.

        :return: state
        """
        base_sanitized_state = super(DataTransformer, self).__getstate__()
        state = dict(base_sanitized_state)
        state["_is_inference_time"] = True
        fit_been_called_key = '_has_fit_been_called_and_succeeded'
        if hasattr(self, fit_been_called_key):
            state[fit_been_called_key] = self._has_fit_been_called_and_succeeded
        else:
            is_mapper_not_none = self.mapper is not None
            tr_map_list = self.transformer_and_mapper_list
            state[fit_been_called_key] = is_mapper_not_none or (tr_map_list is not None and len(tr_map_list) > 0)

        # Remove the unpicklable entries.
        del state["_observer"]
        del state["_feature_sweeping_config"]
        del state["_featurizer_container"]
        del state["stats_and_column_purposes"]
        return state

    def __setstate__(self, state):
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        state["_observer"] = NullExperimentObserver()
        state["_feature_sweeping_config"] = {}
        working_dir = state.get("working_directory")
        if working_dir is None or not os.path.exists(working_dir):
            state["working_directory"] = os.getcwd()

        # In case new fields are added in later versions of the SDK, this will add those new fields only to the
        # `state`.
        new_data_transformer = DataTransformer()

        # In older versions of the SDK, We assume that `fit` has been called when _has_fit_been_called_and_succeeded
        # doesn't exist in the `state` and set the variable accordingly.
        fit_been_called_key = '_has_fit_been_called_and_succeeded'
        if fit_been_called_key not in state:
            is_mapper_not_none = state.get('mapper') is not None
            tr_map_list = state.get('transformer_and_mapper_list')
            state[fit_been_called_key] = is_mapper_not_none or (tr_map_list is not None and len(tr_map_list) > 0)

        for k, v in new_data_transformer.__dict__.items():
            if k not in state:
                state[k] = v

        # Rehydrate the object with the loaded state.
        super(DataTransformer, self).__setstate__(state)

    @classmethod
    def _wrap_in_lst(cls, x):
        """
        For back compatibility for models trained <=1.19.0: Wrap an element in list.

        :param x: Element like string or integer.
        """
        return [x]

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Preprocessing class for input backed by streaming supported NimbusML transformers."""
import logging
from typing import Dict, List, Optional, Tuple

from azureml._common._error_definition import AzureMLError
from azureml.automl.runtime._engineered_feature_names import (
    FeatureNamesHelper, _FeatureTransformers, _GenerateEngineeredFeatureNames, _Transformer)
from azureml.automl.runtime.column_purpose_detection import ColumnPurposeDetector, ColumnPurposeSweeper
from azureml.automl.runtime.column_purpose_detection.types import StatsAndColumnPurposeType
from azureml.automl.runtime.featurization.streaming import NimbusMLStreamingEstimator, StreamingEstimatorBase
from azureml.automl.runtime.featurizer.transformer import (
    CategoricalFeaturizers, GenericFeaturizers, TextFeaturizers)
from azureml.automl.runtime.stats_computation import RawFeatureStats, \
    PreprocessingStatistics as _PreprocessingStatistics
from azureml.dataprep import Dataflow
from azureml.dataprep.api.engineapi.typedefinitions import FieldType
from nimbusml.internal.core.base_pipeline_item import BasePipelineItem as NimbusMLPipelineItem

from azureml.automl.core._experiment_observer import ExperimentStatus, ExperimentObserver, NullExperimentObserver
from azureml.automl.core.constants import FeatureType as _FeatureType, _OperatorNames
from azureml.automl.core.constants import SupportedTransformersInternal as _SupportedTransformersInternal
from azureml.automl.core.constants import _TransformerOperatorMappings
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal, NoFeatureTransformationsAdded
)
from azureml.automl.core.shared._diagnostics.automl_error_definitions import StreamingInconsistentFeatures
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.exceptions import (
    AutoMLException, ClientException, DataException)
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from .streaming_featurization_transformer import StreamingFeaturizationTransformer
from ...featurizer.transformer import featurization_utilities


logger = logging.getLogger(__name__)


class StreamingFeaturizer:
    # TODO: ONNX

    MAX_ROWS_TO_SUBSAMPLE = 100000
    MAX_NUM_BITS_FOR_ONE_HOT_HASH = 30

    # Activity names used for logging (for tracking how long each operation takes)
    FIT_ACTIVITY_NAME = 'StreamingFit'
    PARSE_FEATURE_NAMES_ACTIVITY_NAME = 'StreamingParseFeatureNames'

    def __init__(self,
                 training_data: Dataflow,
                 label_column: str,
                 weight_column: Optional[str] = None,
                 observer: Optional[ExperimentObserver] = None,
                 featurization_config: Optional[FeaturizationConfig] = None):
        self._training_data = training_data
        self._label_column = label_column
        self._weight_column = weight_column
        self._observer = observer or NullExperimentObserver()

        # Set of column names that aren't features (ie label and weight column).
        self._non_feature_column_names = set([self._label_column])
        if self._weight_column:
            self._non_feature_column_names.add(self._weight_column)

        # Instantiate features metadata helper.
        # Note: When instantiating the helper, we block non-feature column names from surfacing as aliases
        # of feature columns. Since the alias of a feature column serves as its column name in the transformed data,
        # this avoids conflicts in the transformed data between feature column and non-feature column names.
        self._features_metadata_helper = _GenerateEngineeredFeatureNames(self._non_feature_column_names)

        self._estimator = None  # type: Optional[StreamingEstimatorBase]
        # Set of columns (other than the label column) that the raw training data is comprised of
        self._all_training_columns = frozenset(
            set(self._training_data.head(1).columns.values.tolist()) - {label_column} - {weight_column})
        # Maintain a list of columns that end up being selected for featurization
        self._training_columns = []   # type: List[str]
        self._dropped_columns = []  # type: List[str]

        # Maintain statistics about the pre-processing stage
        self._pre_processing_stats = _PreprocessingStatistics()

        # Stats and column purpose
        self.stats_and_column_purposes = None  # type: Optional[List[StatsAndColumnPurposeType]]

        # Featurization Customization
        self._featurization_config = featurization_config

        self._validate_inputs()

    def _validate_inputs(self):
        Validation.validate_non_empty(self._label_column, "label_column")
        Validation.validate_type(self._training_data, "training_data", expected_types=Dataflow)

    def get_transformers(self) -> StreamingEstimatorBase:
        """
        Get the final streaming estimator for the streaming featurizer.

        :return: StreamingEstimatorBase
        """
        if self._estimator is None:
            logger.warning('Transformers are unavailable, learning the transformers first.')
            self.learn_transformations()
        assert self._estimator is not None
        return self._estimator

    @logging_utilities.function_debug_log_wrapped()
    def learn_transformations(self) -> StreamingFeaturizationTransformer:
        """
        Learn the transformations on a subsample of the training data, and then fit on the whole.

        :return: StreamingFeaturizationTransformer
        """
        # Dataprep seems to populate invalid values in the cells with a 'DataPrepError' message, which later manifests
        # into various errors while fitting. Replace the invalid cells by a 'None' value instead by using the
        # `extended_types` flag set to False. Note that this option is not available in dprep.head().. hence using
        # the take() and to_pandas_dataframe(on_error='null') semantics.

        columns_to_drop = []
        if self._label_column is not None:
            columns_to_drop.append(self._label_column)
        if self._weight_column is not None:
            columns_to_drop.append(self._weight_column)

        subsampled_input = self._training_data.\
            take(StreamingFeaturizer.MAX_ROWS_TO_SUBSAMPLE).\
            drop_columns(columns=columns_to_drop).\
            to_pandas_dataframe(extended_types=False, on_error='null')

        len_subsampled_input_columns = len(subsampled_input.columns.values)
        len_training_data_columns = len(self._all_training_columns)

        if len_subsampled_input_columns != len_training_data_columns:
            raise DataException._with_error(AzureMLError.create(
                StreamingInconsistentFeatures, target="training_data", original_column_count=len_training_data_columns,
                new_column_count=len_subsampled_input_columns)
            )

        self._observer.report_status(ExperimentStatus.DatasetEvaluation, "Gathering dataset statistics.")

        self.stats_and_column_purposes = ColumnPurposeDetector.get_raw_stats_and_column_purposes(subsampled_input)
        self._update_customized_feature_types()

        self._observer.report_status(ExperimentStatus.FeaturesGeneration, "Generating features for the dataset.")

        try:
            transformations = self._get_transformations()
        except AutoMLException:
            raise
        except Exception as e:
            logger.error('Streaming: Failed to learn the transformations. Encountered an exception of type: '
                         '{}'.format(type(e)))
            raise DataException._with_error(AzureMLError.create(
                AutoMLInternal, target="learn_transformations", error_details=str(e)),
                inner_exception=e
            ) from e

        # todo this should be generalized, we will be getting non-nimbus estimators as well in the near future
        estimator = NimbusMLStreamingEstimator(transformations)

        with logging_utilities.log_activity(logger=logger,
                                            activity_name=StreamingFeaturizer.FIT_ACTIVITY_NAME):
            estimator.fit(self._training_data)

        self._update_metadata_using_transformed_column_names(estimator)
        self._estimator = estimator

        return StreamingFeaturizationTransformer(self._estimator, self._features_metadata_helper)

    def get_transformed_vector_column_names(self) -> List[str]:
        """
        Get the transformed engineered feature names.

        :return: List of feature names.
        """
        all_aliased_columns = list(self._features_metadata_helper.alias_raw_feature_name_transformation_mapping.keys())
        trained_aliased_columns = [col for col in all_aliased_columns if col in self._training_columns]
        return trained_aliased_columns

    def _update_customized_feature_types(self):
        if self._featurization_config is None:
            return
        assert self.stats_and_column_purposes is not None
        featurization_utilities.update_customized_feature_types(
            self.stats_and_column_purposes,
            self._featurization_config
        )
        logger.info("Updated column purposes using customized feature type settings.")

    def _update_metadata_using_transformed_column_names(self, estimator: NimbusMLStreamingEstimator) -> None:
        # All the columns have been aliased by now, so we filter out the label and weight columns
        # from the transformed column names
        transformed_column_names = set(estimator.pipeline.get_output_columns())
        transformed_feature_column_names = list(transformed_column_names - self._non_feature_column_names)

        with logging_utilities.log_activity(logger=logger,
                                            activity_name=StreamingFeaturizer.PARSE_FEATURE_NAMES_ACTIVITY_NAME):
            self._features_metadata_helper.parse_raw_feature_names(
                transformed_feature_column_names,
                FeatureNamesHelper.get_regular_exp_for_parsing_raw_feature_names_streaming())

    def _get_transformations(self) -> List[NimbusMLPipelineItem]:
        column_groups = {}  # type: Dict[str, List[Tuple[str, RawFeatureStats]]]
        if self.stats_and_column_purposes is not None:
            for raw_stats, column_purpose, column in self.stats_and_column_purposes:
                column_groups.setdefault(column_purpose, []).append((column, raw_stats))

        transforms = [self._get_transforms_for_column_purpose(column_purpose, column_name_with_stats)
                      for column_purpose, column_name_with_stats in column_groups.items()]
        flattened_transforms = [transform for sublist in transforms for transform in sublist]

        if not flattened_transforms:
            raise DataException._with_error(
                AzureMLError.create(NoFeatureTransformationsAdded, target="learn_transformations")
            )

        # drop original, non-aliased columns
        columns_to_drop = list(
            set(self._all_training_columns) - set(self.get_transformed_vector_column_names())
            - set(self._dropped_columns))
        if len(columns_to_drop) > 0:
            flattened_transforms.append(GenericFeaturizers.nimbus_column_selector(
                columns=columns_to_drop,
                drop_columns=columns_to_drop))

        # Log stats_computation about raw data
        logger.info(self._pre_processing_stats.get_raw_data_stats())

        return flattened_transforms

    def _get_transforms_for_column_purpose(self,
                                           column_purpose: str,
                                           column_name_with_stats: List[Tuple[str, RawFeatureStats]]) ->\
            List[NimbusMLPipelineItem]:
        # todo for all transforms, figure out right set of params
        result = []  # type: List[NimbusMLPipelineItem]
        training_columns = self._training_data.head(1).columns
        columns_to_transform = [column for column, _ in column_name_with_stats]
        indices_to_transform = [training_columns.get_loc(col_index) for col_index in columns_to_transform]
        featurizer_names = []  # type: List[str]
        featurized_logging_template = 'Identified column(s) {} as type {}, featurizing using {}.'

        if column_purpose == _FeatureType.Numeric:
            if self._featurization_config is not None and self._featurization_config.transformer_params is not None:
                column_transform_groups = featurization_utilities.get_transformer_column_groups(
                    _SupportedTransformersInternal.Imputer, columns_to_transform,
                    self._featurization_config.transformer_params)
            else:
                column_transform_groups = [columns_to_transform]

            for column_transform_group in column_transform_groups:
                missing_value_transform = self._get_numeric_transforms(column_transform_group)
                result.append(missing_value_transform)

            featurizer_names = [type(missing_value_transform).__name__]

        elif column_purpose == _FeatureType.Categorical:
            aliases_to_raw_col_names = self._get_new_col_aliases_to_raw_col_names(
                columns_to_transform, _SupportedTransformersInternal.OneHotEncoder,
                None, _FeatureType.Categorical
            )
            # todo see if we could use label_encoding (nimbus's ToKey transformer) for unique_vals <= 2
            onehot_transform = CategoricalFeaturizers.nimbusml_onehotencoder(columns=aliases_to_raw_col_names)
            result.append(onehot_transform)
            self._training_columns.extend(list(aliases_to_raw_col_names.keys()))
            featurizer_names = [type(onehot_transform).__name__]

        elif column_purpose == _FeatureType.CategoricalHash:
            if self._featurization_config is not None and self._featurization_config.transformer_params is not None:
                column_transform_groups = featurization_utilities.get_transformer_column_groups(
                    _SupportedTransformersInternal.HashOneHotEncoder, columns_to_transform,
                    self._featurization_config.transformer_params)
            else:
                column_transform_groups = [columns_to_transform]

            for column_transform_group in column_transform_groups:
                onehothash_transform = self._get_categorical_hash_transforms(column_transform_group)
                result.append(onehothash_transform)

            featurizer_names = [type(onehothash_transform).__name__]

        elif column_purpose == _FeatureType.Text:
            ngram_transforms = self._get_text_transforms(column_name_with_stats)
            result.extend(ngram_transforms)
            featurizer_names = [type(tx).__name__ for tx in ngram_transforms]

        elif column_purpose == _FeatureType.DateTime:
            logger.warning('Featurization of DateTime columns are currently not supported for large datasets. '
                           'They will be ignored during model training.')
            aliases_to_raw_col_names = self._get_new_col_aliases_to_raw_col_names(
                columns_to_transform, _SupportedTransformersInternal.Drop,
                None, _FeatureType.Ignore
            )
            drop_columns_transform = GenericFeaturizers.nimbus_column_selector(
                columns=columns_to_transform,
                drop_columns=columns_to_transform)

            result.append(drop_columns_transform)
            featurizer_names = [type(drop_columns_transform).__name__]
            self._dropped_columns.extend(columns_to_transform)

        elif column_purpose in _FeatureType.DROP_SET:
            # If this is the only column in the dataset, attempt an alternate column purpose and featurize
            if len(self._all_training_columns) == 1:
                assert len(column_name_with_stats) == 1, \
                    "Training data had just one column, while received {} columns to transform".format(
                        len(columns_to_transform))
                col, col_idx, stats = columns_to_transform[0], indices_to_transform[0], column_name_with_stats[0][1]
                if self._training_data.dtypes[col] == FieldType.STRING:
                    alternate_column_purpose = ColumnPurposeSweeper.safe_convert_on_feature_type(column_purpose)

                    if alternate_column_purpose:
                        assert alternate_column_purpose != column_purpose, \
                            "previous and alternate column purposes can't be same."

                        logger.info('Featurizing column index: {}, currently identified as: {}, '
                                    'with new column purpose: {}'.
                                    format(col_idx, column_purpose, alternate_column_purpose))

                        column_stats_with_alternate_purpose = [(col, stats)]

                        return self._get_transforms_for_column_purpose(
                            alternate_column_purpose, column_stats_with_alternate_purpose)

            # Alternate column purpose not found / required, drop the columns in column_to_transform
            aliases_to_raw_col_names = self._get_new_col_aliases_to_raw_col_names(
                columns_to_transform, _SupportedTransformersInternal.Drop,
                None, column_purpose
            )
            drop_columns_transform = GenericFeaturizers.nimbus_column_selector(
                columns=columns_to_transform,
                drop_columns=columns_to_transform)
            result.append(drop_columns_transform)
            featurizer_names = [type(drop_columns_transform).__name__]
            self._dropped_columns.extend(columns_to_transform)
        else:
            error_msg = 'Cannot featurize columns {} due to unsupported feature type: {}'
            logger.error(error_msg)
            raise ClientException(
                error_msg.format(columns_to_transform, column_purpose),
                reference_code=ReferenceCodes._STREAMING_FEATURIZER_GET_TRANSFORMER
            ).with_generic_msg(error_msg.format('[Masked]', '[Masked]'))

        self._pre_processing_stats.update_raw_feature_stats(column_purpose, len(columns_to_transform))

        assert featurizer_names, 'Should have already thrown an exception for empty featurizer_names'
        logger.info(featurized_logging_template.format(
            indices_to_transform, column_purpose, featurizer_names
        ))

        return result

    def _get_new_col_aliases_to_raw_col_names(
        self,
        raw_col_names: List[str],
        transformation_fnc_name: str,
        operator: Optional[str],
        feature_type: str
    ) -> Dict[str, str]:
        aliases_to_raw_col_names = {}
        for raw_col_name in raw_col_names:
            feature_transformers = _FeatureTransformers(
                [_Transformer(
                    parent_feature_list=[raw_col_name],
                    transformation_fnc=transformation_fnc_name,
                    operator=operator,
                    feature_type=feature_type,
                    should_output=True)])
            json_obj = feature_transformers.encode_transformations_from_list()
            alias = self._features_metadata_helper.get_raw_feature_alias_name(json_obj)
            aliases_to_raw_col_names[alias] = raw_col_name
        return aliases_to_raw_col_names

    def _get_numeric_transforms(self, column_transform_group: List[str]) -> NimbusMLPipelineItem:
        transformer_params = featurization_utilities.get_transformer_params_by_column_names(
            _SupportedTransformersInternal.Imputer,
            [column_transform_group[0]],
            self._featurization_config
        )
        operator = _TransformerOperatorMappings.NimbusImputer.get(
            str(transformer_params.get('strategy'))) if transformer_params else _OperatorNames.Mean
        if not operator:
            logger.warning("Unsupported parameter passed, proceeding with default values")
            operator = _OperatorNames.Mean
        aliases_to_raw_col_names = self._get_new_col_aliases_to_raw_col_names(
            column_transform_group, _SupportedTransformersInternal.Imputer,
            operator,
            _FeatureType.Numeric
        )
        self._training_columns.extend(list(aliases_to_raw_col_names.keys()))
        # todo add indicator column for missing values based on threshold
        # concat = False drops the indicator column
        return GenericFeaturizers.nimbus_missing_values_handler(
            columns=aliases_to_raw_col_names,
            replace_with=transformer_params.get("strategy")
            if operator != _OperatorNames.Mean else _OperatorNames.Mean,
            concat=False)

    def _get_categorical_hash_transforms(self, column_transform_group: List[str]) -> NimbusMLPipelineItem:
        transformer_params = featurization_utilities.get_transformer_params_by_column_names(
            _SupportedTransformersInternal.HashOneHotEncoder,
            [column_transform_group[0]],
            self._featurization_config
        )

        aliases_to_raw_col_names = self._get_new_col_aliases_to_raw_col_names(
            column_transform_group, _SupportedTransformersInternal.HashOneHotEncoder,
            None, _FeatureType.CategoricalHash
        )
        self._training_columns.extend(list(aliases_to_raw_col_names.keys()))

        try:
            return CategoricalFeaturizers.nimbusml_hash_onehotencoder(
                **{
                    'columns': aliases_to_raw_col_names,
                    **transformer_params
                }
            )
        except Exception:
            logger.warning("Unsupported parameter passed, proceeding with default values")
            logger.debug("Creating {t} with customized parameter failed with error."
                         .format(t=_SupportedTransformersInternal.HashOneHotEncoder))
            return CategoricalFeaturizers.nimbusml_hash_onehotencoder(
                **{
                    'columns': aliases_to_raw_col_names
                }
            )

    def _get_text_transforms(self, column_name_with_stats: List[Tuple[str, RawFeatureStats]]) ->\
            List[NimbusMLPipelineItem]:
        ngram_transforms = []  # type: List[NimbusMLPipelineItem]
        aliases = []    # type: List[str]
        for raw_column_name, _ in column_name_with_stats:
            # todo Figure out right params for ngram featurizer
            # Currently, having random ngrams can lead to explosion of columns. Currently we fit and transform a small
            # batch of training data to get the transformed column names. This column explosion can in turn lead to
            # large usage of memory / potential failures. Hence, fix on an ngram value (to 2) and max_terms (to 200k).
            # Note that this could lead to lower accuracies, hence this is not a long term solution.
            # ngram_length = max(int(get_ngram_len(raw_stats.lengths)), 1)
            ngram_length = 2
            alias_to_raw_col_name = self._get_new_col_aliases_to_raw_col_names(
                [raw_column_name], _SupportedTransformersInternal.TfIdf,
                None, _FeatureType.Text
            )
            ngram_transforms.append(TextFeaturizers.nimbus_ngram_featurizer(
                columns=alias_to_raw_col_name,
                ngram_word_length=ngram_length))

            assert len(alias_to_raw_col_name.keys()) == 1, 'Expected to featurize text columns one at a time'
            aliases.append(list(alias_to_raw_col_name.keys())[0])

        self._training_columns.extend(aliases)
        return ngram_transforms

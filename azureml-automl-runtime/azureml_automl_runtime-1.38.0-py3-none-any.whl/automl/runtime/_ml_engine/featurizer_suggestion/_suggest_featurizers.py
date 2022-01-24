# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Suggest featurizers API module."""

from typing import Any, Dict, List, Optional, Tuple, Union

import logging
import os

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from azureml._common._error_definition import AzureMLError

from azureml.automl.core._experiment_observer import ExperimentObserver, ExperimentStatus, NullExperimentObserver
from azureml.automl.core.constants import FeatureType, SupportedTransformersInternal
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import UnrecognizedFeatures
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import AutoMLDefaultTimeouts
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime._engineered_feature_names import (
    _GenerateEngineeredFeatureNames, _Transformer, _FeatureTransformers
)

from azureml.automl.runtime.column_purpose_detection import (StatsAndColumnPurposeType, ColumnPurposeSweeper,
                                                             ColumnPurposeDetector)
from azureml.automl.runtime.column_purpose_detection._utilities import get_column_purposes_user_friendly
from azureml.automl.runtime.featurization import data_transformer_utils, TransformerAndMapper
from azureml.automl.runtime.featurizer.transformer import (featurization_utilities,
                                                           get_ngram_len, TFIDF_VECTORIZER_CONFIG, GenericFeaturizers)
from azureml.automl.runtime.featurizer.transformer.categorical.labelencoder_transformer import LabelEncoderTransformer
from azureml.automl.runtime.shared import utilities as runtime_utilities
from azureml.automl.runtime.shared.types import DataSingleColumnInputType, TransformerType
from azureml.automl.runtime.stats_computation import PreprocessingStatistics

from .dynamic_suggestions import perform_feature_sweeping
from .static_suggestions import (suggest_featurizers_for_categorical_hash_data,
                                 suggest_featurizers_for_datetime_data, suggest_featurizers_for_categorical_data,
                                 suggest_featurizers_for_numeric_data, suggest_featurizers_for_text_data)

logger = logging.getLogger(__name__)

UNSUPPORTED_PARAMETER_WARNING_MSG = "Unsupported parameter passed to {t}, proceeding with default values"


# TODO: Make stats and column purposes a structured object rather than a collection of Tuples.
# TODO: 'FeatureType' vs 'ColumnPurpose'
def suggest_featurizers(
    task: str,
    X: pd.DataFrame,
    y: DataSingleColumnInputType = None,
    featurization_config: Optional[FeaturizationConfig] = None,
    is_onnx_compatible: bool = False,
    observer: ExperimentObserver = NullExperimentObserver(),
    enable_feature_sweeping: bool = True,
    feature_sweeping_timeout_seconds: int = AutoMLDefaultTimeouts.DEFAULT_FEATSWEEP_TIMEOUT_SECONDS,
    is_cross_validation: bool = True,
    enable_dnn: bool = False,
    force_text_dnn: bool = False,
    feature_sweeping_config: Dict[str, Any] = {},
    enable_categorical_indicators: bool = False,
    working_dir: Optional[str] = None,
    _test_transforms: Optional[List[Any]] = None,
    _feature_sweeper: Optional[Any] = None) -> Tuple[List[str],
                                                     PreprocessingStatistics,
                                                     List[StatsAndColumnPurposeType],
                                                     _GenerateEngineeredFeatureNames,
                                                     List[TransformerAndMapper]]:
    """
    Identify the transformations for all the columns in the dataframe.

    :param task: Experiment task.
    :param X: Input training data.
    :param y: Optional label data.
    :param featurization_config: Featurization configuration if provided by the user.
    :param is_onnx_compatible: If the model needs to be ONNX compatible.
    :param observer: Experiment observer.
    :param enable_feature_sweeping: If feature sweeping is enabled.
    :param feature_sweeping_timeout_seconds: Feature sweeping timeout in seconds.
    :param is_cross_validation: If the current experiment is cross validation based.
    :param enable_dnn: If DNN is enabled.
    :param force_text_dnn: If DNN should be forced.
    :param feature_sweeping_config: Feature sweeping configuration.
    :param enable_categorical_indicators: If categorical indicators supported.
    :param working_dir: Working directory
    :param _test_transforms: (Internal only)Any test transforms that need to be added.
    :param _feature_sweeper: (Internal only)Custom feature sweeper for testing.
    :return: A Tuple with Raw feature names, pre-processing statistics, statistics and column purposes,
    engineered feature names generator and holder, list of transformer and mappers.
    """
    observer.report_status(ExperimentStatus.DatasetEvaluation, "Gathering dataset statistics.")
    stats_and_column_purposes = ColumnPurposeDetector.get_raw_stats_and_column_purposes(X)
    _update_customized_feature_types(featurization_config=featurization_config,
                                     stats_and_column_purposes=stats_and_column_purposes)

    runtime_utilities.check_input(X)
    efgh = _GenerateEngineeredFeatureNames()
    data_profile = PreprocessingStatistics()

    working_dir = working_dir or os.getcwd()
    transforms = []  # type: List[TransformerType]
    all_columns = X.columns
    dtypes = X.dtypes

    featuretype_to_setofcolumns = {}  # type: Dict[str, List[str]]
    for _, feature_type, column in stats_and_column_purposes:
        featuretype_to_setofcolumns.setdefault(feature_type, []).append(column)

    raw_feature_names, all_new_column_names = data_transformer_utils.generate_new_column_names(all_columns)

    observer.report_status(ExperimentStatus.FeaturesGeneration, "Generating features for the dataset.")

    # Get default transformers based on column purpose
    for feature_type in featuretype_to_setofcolumns.keys():
        current_column_transforms = _get_transforms_per_column_purpose(
            current_featuretype_columns=featuretype_to_setofcolumns[feature_type],
            columns=all_columns,
            dtypes=dtypes,
            new_column_names=all_new_column_names,
            detected_column_purpose=feature_type,
            stats_and_column_purposes=stats_and_column_purposes,
            is_onnx_compatible=is_onnx_compatible,
            featurization_config=featurization_config,
            data_profile=data_profile,
            engineered_featurenames_generator_and_holder=efgh,
            enable_categorical_indicators=enable_categorical_indicators
        )

        if current_column_transforms:
            transforms.extend(current_column_transforms)
        else:
            # skip if hashes or ignore case
            logger.info("No transforms available for {}. Either hashes, single value column, \
                or transformer is blocked.".format(feature_type))

    # Experiment with different featurization pipelines through feature sweeping.
    sweeping_added_transformers = []  # type: List[Tuple[Union[str, List[str]], Pipeline]]
    if enable_feature_sweeping:
        with logging_utilities.log_activity(logger=logger, activity_name="FeatureSweeping"):
            sweeping_added_transformers = perform_feature_sweeping(
                task=task,
                X=X,
                y=y,
                stats_and_column_purposes=stats_and_column_purposes,
                featurization_config=featurization_config,
                feature_sweeping_timeout_seconds=feature_sweeping_timeout_seconds,
                is_cross_validation=is_cross_validation,
                enable_dnn=enable_dnn,
                force_text_dnn=force_text_dnn,
                feature_sweeping_config=feature_sweeping_config,
                working_dir=working_dir,
                feature_sweeper=_feature_sweeper
            )
    else:
        logger.info("Feature sweeping disabled")

    if sweeping_added_transformers:
        # Generate engineered feature names
        cols_list = []  # type: List[str]
        feature_type = ''
        for cols, tfs in sweeping_added_transformers:
            cols_for_aliasing = cols if not isinstance(cols, str) else [cols]
            for col in cols_for_aliasing:
                stats_and_column_purpose = next((x for x in stats_and_column_purposes if x[2] == col))
                # Assumption here is that all the columns in the list will be of one type
                feature_type = stats_and_column_purpose[1]
                index = stats_and_column_purposes.index(stats_and_column_purpose)
                new_column_name = all_new_column_names[index]
                cols_list.append(new_column_name)

            alias_column_name = efgh._record_metadata_and_create_alias(cols_list, tfs, feature_type)
            transforms.append((cols, tfs, {'alias': str(alias_column_name)}))

    # TODO: Do not allow column purpose sweep if type is set in featurizer config.
    transforms.extend(sweep_column_purpose_and_get_transforms(
        transforms=transforms,
        columns=all_columns,
        dtypes=dtypes,
        stats_and_column_purposes=stats_and_column_purposes,
        new_column_names=all_new_column_names,
        column_groups=featuretype_to_setofcolumns,
        engineered_featurenames_generator_and_holder=efgh,
        is_onnx_compatible=is_onnx_compatible,
        featurization_config=featurization_config,
        data_profile=data_profile))

    if not transforms:
        # can happen when we get all hashes
        logger.warning("No features could be identified or generated. Please inspect your data.")

        column_drop_reasons = get_column_purposes_user_friendly(stats_and_column_purposes)
        raise DataException._with_error(AzureMLError.create(
            UnrecognizedFeatures, target="X", column_drop_reasons="\n".join(column_drop_reasons),
            reference_code=ReferenceCodes._DATA_TRANSFORMER_TRANSFROM_NO_FEATURE)
        )

    # Log the transformations done for raw data into the logs
    logger.info(human_readable_featurizers(all_columns, transforms))
    logger.info(data_profile.get_raw_data_stats())

    logger.info("End getting transformers.")

    # Used for testing only
    if _test_transforms:
        transforms.extend(_test_transforms)

    transformer_and_mapper_list = []  # type: List[TransformerAndMapper]
    for transformers in transforms:
        from sklearn_pandas import DataFrameMapper
        transform_and_mapper = TransformerAndMapper(transformers=transformers[1],
                                                    mapper=DataFrameMapper([transformers],
                                                                           input_df=True, sparse=True))
        transformer_and_mapper_list.append(transform_and_mapper)

    return raw_feature_names, data_profile, stats_and_column_purposes, efgh, transformer_and_mapper_list


def _get_transforms_per_column_purpose(
    current_featuretype_columns: List[str],
    columns: pd.Index,
    dtypes: pd.Series,
    new_column_names: List[str],
    detected_column_purpose: str,
    stats_and_column_purposes: List[StatsAndColumnPurposeType],
    engineered_featurenames_generator_and_holder: _GenerateEngineeredFeatureNames,
    data_profile: PreprocessingStatistics,
    is_onnx_compatible: bool = False,
    featurization_config: Optional[FeaturizationConfig] = None,
    enable_categorical_indicators: bool = False
) -> List[TransformerType]:
    """
    Obtain transformations based on column purpose and feature stats.

    :param current_featuretype_columns: Set of columns in the data corresponding to `detected_column_purpose`
    :param columns: Column indices.
    :param dtypes: Pandas dtypes.
    :param new_column_names: Set of old and new column names.
    :param detected_column_purpose: Column purpose/Feature type of the set of columns.
    :param stats_and_column_purposes: Statistics and column purposes.
    :param engineered_featurenames_generator_and_holder: Engineered feature name generator and holder.
    :param data_profile: Preprocessing statistics.
    :param is_onnx_compatible: If the model needs to be ONNX compatible.
    :param featurization_config: Featurization configuration.
    :param enable_categorical_indicators: Enable/disable categorical indicators
    :return: A list of transformers that must be applied on various columns.
    """
    alias_key = 'alias'
    featurization_config = featurization_config or FeaturizationConfig()
    efgh = engineered_featurenames_generator_and_holder  # Shorter name
    Contract.assert_type(value=efgh,
                         name='engineered_featurenames_generator_and_holder',
                         expected_types=_GenerateEngineeredFeatureNames,
                         reference_code=ReferenceCodes._ENGINEERED_FEATURE_UNEXPECTED_TYPE
                         )

    transformers = []  # type: List[TransformerType]

    logger.info("enable_categorical_indicators in get_transforms flag is set to {}".format(
        enable_categorical_indicators))
    blocked_transformers = featurization_config.blocked_transformers if featurization_config is not None else None
    for column in current_featuretype_columns:
        for index, stats_and_column_purpose in enumerate(stats_and_column_purposes):
            # TODO: Optimize this by maintaining a dictionary.
            if stats_and_column_purpose[2] != column:
                continue

            raw_stats, _, _ = stats_and_column_purposes[index]
            new_column_name = new_column_names[index]
            current_column_transformers = []  # type: List[TransformerType]
            # TODO: Refactor this to be a dictionary based lookup.
            if detected_column_purpose == FeatureType.Numeric:
                numeric_transformers = suggest_featurizers_for_numeric_data(
                    column=column,
                    featurization_config=featurization_config)

                if numeric_transformers:
                    alias_column_name = efgh._record_metadata_and_create_alias(
                        columns=[new_column_name],
                        transformers=numeric_transformers,
                        column_purpose=FeatureType.Numeric)

                    current_column_transformers = [(
                        [column],
                        numeric_transformers,
                        {
                            alias_key: str(alias_column_name)
                        }
                    )]

                    # if there are lot of imputed values, add an imputation marker
                    if raw_stats.num_na > 0.01 * raw_stats.total_number_vals:
                        imputation_marker_transformers = [GenericFeaturizers.imputation_marker()]
                        alias_column_name = efgh._record_metadata_and_create_alias(
                            columns=[new_column_name],
                            transformers=imputation_marker_transformers,
                            column_purpose=FeatureType.Numeric)

                        current_column_transformers.append((
                            [column],
                            imputation_marker_transformers,
                            {
                                alias_key: str(alias_column_name)
                            }
                        ))

            elif detected_column_purpose == FeatureType.DateTime:
                datetime_transformers = suggest_featurizers_for_datetime_data(
                    column=column,
                    featurization_config=featurization_config
                )

                if datetime_transformers:
                    alias_column_name = efgh._record_metadata_and_create_alias(
                        columns=[new_column_name],
                        transformers=datetime_transformers,
                        column_purpose=FeatureType.DateTime)

                    current_column_transformers = [(
                        column,
                        datetime_transformers,
                        {
                            alias_key: str(alias_column_name)
                        }
                    )]

            elif detected_column_purpose == FeatureType.CategoricalHash:
                required_transformers = {SupportedTransformersInternal.StringCast,
                                         SupportedTransformersInternal.HashOneHotEncoder}
                required_transformers_that_are_blocked = required_transformers.intersection(
                    featurization_config.blocked_transformers or {}
                )

                if required_transformers_that_are_blocked:
                    logger.info("Excluding blocked transformer(s): {0}".format(required_transformers_that_are_blocked))
                    continue

                cathash_transformers = suggest_featurizers_for_categorical_hash_data(
                    column=column,
                    num_unique_categories=raw_stats.num_unique_vals,
                    featurization_config=featurization_config
                )

                if cathash_transformers:
                    alias_column_name = efgh._record_metadata_and_create_alias(
                        columns=[new_column_name],
                        transformers=cathash_transformers,
                        column_purpose=FeatureType.CategoricalHash)

                    current_column_transformers = [(
                        column,
                        cathash_transformers,
                        {
                            alias_key: str(alias_column_name)
                        }
                    )]

            elif detected_column_purpose == FeatureType.Categorical:

                # Get the categorical featurizers for the regular pipleine
                cat_transformers = suggest_featurizers_for_categorical_data(
                    column=column,
                    num_unique_categories=raw_stats.num_unique_vals,
                    featurization_config=featurization_config,
                    is_onnx_compatible=is_onnx_compatible,
                    enable_categorical_indicators=False
                )

                if cat_transformers:
                    alias_column_name = efgh._record_metadata_and_create_alias(
                        columns=[new_column_name],
                        transformers=cat_transformers,
                        column_purpose=FeatureType.Categorical)

                    current_column_transformers = [(
                        column,
                        cat_transformers,
                        {
                            alias_key: str(alias_column_name)
                        }
                    )]

                    if enable_categorical_indicators and not any(isinstance(transformer, LabelEncoderTransformer)
                                                                 for transformer in cat_transformers):

                        # Get the categroical featurizers for the catboost/tabnet pipleine
                        cat_transformers_indicators = suggest_featurizers_for_categorical_data(
                            column=column,
                            num_unique_categories=raw_stats.num_unique_vals,
                            featurization_config=featurization_config,
                            is_onnx_compatible=is_onnx_compatible,
                            enable_categorical_indicators=enable_categorical_indicators
                        )

                        alias_column_name = efgh._record_metadata_and_create_alias(
                            columns=[new_column_name],
                            transformers=cat_transformers_indicators,
                            column_purpose=FeatureType.Categorical)

                        current_column_transformers.append((
                            column,
                            cat_transformers_indicators,
                            {
                                alias_key: str(alias_column_name)
                            }
                        ))

            elif detected_column_purpose == FeatureType.Text:
                text_transformers = suggest_featurizers_for_text_data(
                    column=column,
                    ngram_len=get_ngram_len(raw_stats.lengths),
                    blocked_list=blocked_transformers,
                    featurization_config=featurization_config,
                    is_onnx_compatible=is_onnx_compatible
                )

                current_column_transformers = []
                if text_transformers:
                    for t in text_transformers:
                        alias_column_name = efgh._record_metadata_and_create_alias(
                            columns=[new_column_name],
                            transformers=t,
                            column_purpose=FeatureType.Text)

                        current_column_transformers.append((
                            column,
                            t,
                            {
                                alias_key: str(alias_column_name)
                            }
                        ))

            elif detected_column_purpose in FeatureType.DROP_SET:
                _record_dropped_columns(column_name=new_column_name,
                                        dtype=detected_column_purpose,
                                        efgh=efgh)

            if current_column_transformers:
                transformers.extend(current_column_transformers)

            column_loc = columns.get_loc(column)
            logger.info("Preprocess transformer for col {}, datatype: {}, detected datatype {}, \
                no. of transformers added {}".format(
                column_loc,
                str(dtypes.values[index]),
                str(detected_column_purpose),
                len(current_column_transformers)
            ))

            # Update pre-processing stats_computation
            data_profile.update_raw_feature_stats(detected_column_purpose)

    return transformers


def human_readable_featurizers(columns: pd.Index, transforms: List[TransformerType]) -> str:
    """
    Get the data transformations recorded for raw columns as strings.

    :param columns: List of column indices.
    :param transforms: List of trnasforms applied on those columns.
    :return: String representation of column indices and the transforms.
    """
    transformation_str = 'Transforms: '
    list_of_transforms_as_list = []

    num_transforms = len(transforms)
    # Walk all columns in the input dataframe
    for column in columns:
        # Get all the indexes of transformations for the current column
        column_matches_transforms = [i for i in range(
            num_transforms) if transforms[i][0] == column]

        # If no matches for column name is found, then look for list having
        # this column name
        if len(column_matches_transforms) == 0:
            column_matches_transforms = [i for i in range(
                num_transforms) if transforms[i][0] == [column]]

        # look for list of columns having this column name
        column_matches_transforms = \
            [i for i in range(0, len(transforms))
             if isinstance(transforms[i][0], list) and column in transforms[i][0]]

        # Walk all the transformations found for the current column and add
        # to a string
        for transform_index in column_matches_transforms:

            transformers_list = transforms[transform_index][1]
            if isinstance(transformers_list, Pipeline):
                transformers_list = [t[1] for t in transformers_list.steps]

            some_str = 'col {} transformers: {}'.format(
                columns.get_loc(column), ', '.join([tf.__class__.__name__ for tf in transformers_list]))

            list_of_transforms_as_list.append(some_str)

    transformation_str += ' ; '.join(list_of_transforms_as_list)

    # Return the string representation of all the transformations
    return transformation_str


# TODO: We should be doing this before feature sweeping so that additional columns are considered.
def sweep_column_purpose_and_get_transforms(
        transforms: List[TransformerType],
        columns: pd.Index,
        dtypes: pd.Series,
        stats_and_column_purposes: List[StatsAndColumnPurposeType],
        new_column_names: List[str],
        column_groups: Dict[str, List[str]],
        engineered_featurenames_generator_and_holder: _GenerateEngineeredFeatureNames,
        data_profile: PreprocessingStatistics,
        is_onnx_compatible: bool = False,
        featurization_config: Optional[FeaturizationConfig] = None) -> List[TransformerType]:
    """
    Perform column purpose sweeping and return appropriate transforms.

    :param transforms: List of transforms currently generated to be applied on the set of columns.
    :param columns: Column indices.
    :param dtypes: Set of dtypes of the columns.
    :param stats_and_column_purposes: Statistics and column purposes.
    :param new_column_names: Set of new column names and old merged.
    :param column_groups: Set of column groups based on column purpose.
    :param engineered_featurenames_generator_and_holder: Engineered feature names generator and holder.
    :param is_onnx_compatible: If the output models needs to be ONNX compatible.
    :param featurization_config: Feature configuration.
    :param data_profile: Preprocessing statistics.
    :return:
    """
    if not transforms and len(columns) == 1:
        column_index = 0
        if not np.issubdtype(dtypes[column_index], np.number):
            raw_stats, feature_type, column = stats_and_column_purposes[column_index]
            alternate_column_purpose = ColumnPurposeSweeper.safe_convert_on_feature_type(feature_type)
            if alternate_column_purpose:
                return _get_alternate_transformer(
                    column_index=column_index,
                    columns=columns,
                    dtypes=dtypes,
                    new_column_names=new_column_names,
                    alternate_feature_type=alternate_column_purpose,
                    stats_and_column_purposes=stats_and_column_purposes,
                    is_onnx_compatible=is_onnx_compatible,
                    featurization_config=featurization_config,
                    data_profile=data_profile,
                    engineered_featurenames_generator_and_holder=engineered_featurenames_generator_and_holder)

    columns_with_transformers = [x[0] for x in transforms if not isinstance(x[0], list)]
    columns_with_transformers_set = set(columns_with_transformers)
    for feature_type in column_groups.keys():
        if feature_type == FeatureType.Numeric:
            continue

        for column in column_groups[feature_type]:
            # Check if any transforms are available for this column.
            # If not, see if column type sweeping can be made.
            if column not in columns_with_transformers_set:
                stats_and_column_purpose = next(
                    (x for x in stats_and_column_purposes if x[2] == column))
                column_index = stats_and_column_purposes.index(stats_and_column_purpose)
                raw_stats, _, _ = stats_and_column_purposes[column_index]
                alternate_column_purpose = ColumnPurposeSweeper.safe_convert_on_data_type(feature_type,
                                                                                          raw_stats.column_type)
                if alternate_column_purpose:
                    return _get_alternate_transformer(
                        column_index=column_index,
                        columns=columns,
                        dtypes=dtypes,
                        new_column_names=new_column_names,
                        alternate_feature_type=alternate_column_purpose,
                        stats_and_column_purposes=stats_and_column_purposes,
                        is_onnx_compatible=is_onnx_compatible,
                        featurization_config=featurization_config,
                        data_profile=data_profile,
                        engineered_featurenames_generator_and_holder=engineered_featurenames_generator_and_holder)

    return []


def _get_alternate_transformer(
        column_index: int,
        columns: pd.Index,
        dtypes: pd.Series,
        new_column_names: List[str],
        alternate_feature_type: str,
        stats_and_column_purposes: List[StatsAndColumnPurposeType],
        engineered_featurenames_generator_and_holder: _GenerateEngineeredFeatureNames,
        data_profile: PreprocessingStatistics,
        is_onnx_compatible: bool = True,
        featurization_config: Optional[FeaturizationConfig] = None
) -> List[TransformerType]:
    """
    Return alternate transformer for given alternate column purpose

    :param column_index: Index of the column for which alternative is being considered.
    :param columns: All column indices.
    :param dtypes: Pandas dtypes.
    :param new_column_names: Set of old and new column names.
    :param alternate_feature_type: Column purpose/Feature type of the set of the column.
    :param stats_and_column_purposes: Statistics and column purposes.
    :param engineered_featurenames_generator_and_holder: Engineered feature name generator and holder.
    :param data_profile: Preprocessing statistics.
    :param is_onnx_compatible: If the model needs to be ONNX compatible.
    :param featurization_config: Featurization configuration.
    :return: A list of transformers that must be applied on the current column.
    """
    raw_stats, original_feature_type, column = stats_and_column_purposes[column_index]
    msg = "Column index: {0}, current column purpose: {1}, Alternate column purpose: {2}".format(
        column_index, original_feature_type, alternate_feature_type)

    logger.info(msg)

    stats_and_column_purposes[column_index] = raw_stats, alternate_feature_type, column
    return _get_transforms_per_column_purpose(
        current_featuretype_columns=[columns[column_index]],
        columns=columns,
        dtypes=dtypes,
        new_column_names=new_column_names,
        detected_column_purpose=alternate_feature_type,
        stats_and_column_purposes=stats_and_column_purposes,
        is_onnx_compatible=is_onnx_compatible,
        featurization_config=featurization_config,
        data_profile=data_profile,
        engineered_featurenames_generator_and_holder=engineered_featurenames_generator_and_holder
    )


def _update_customized_feature_types(featurization_config: Optional[FeaturizationConfig],
                                     stats_and_column_purposes: List[StatsAndColumnPurposeType]) -> None:
    """
    Update the feature types based on what the user has provided.

    :param featurization_config: Featurization config provided by the user.
    :param stats_and_column_purposes: Statistics and column purposes for the data.
    :return: None. Column purposes are updated in place.
    """
    if featurization_config is None:
        return

    logger.info("Start updating column purposes using customized feature type settings.")
    if stats_and_column_purposes is not None:
        featurization_utilities.update_customized_feature_types(
            stats_and_column_purposes,
            featurization_config
        )
    logger.info("End updating column purposes using customized feature type settings.")


def _record_dropped_columns(column_name: str, dtype: str, efgh: _GenerateEngineeredFeatureNames) -> None:
    drop_transformer = _Transformer(parent_feature_list=[str(column_name)],
                                    transformation_fnc=SupportedTransformersInternal.Drop,
                                    operator=None,
                                    feature_type=dtype,
                                    should_output=True)
    feature_transformers = _FeatureTransformers([drop_transformer])
    json_obj = feature_transformers.encode_transformations_from_list()
    efgh.get_raw_feature_alias_name(json_obj)

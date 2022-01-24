# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Static featurizer suggestions."""

from typing import Any, List, Optional

import logging
import math

from sklearn.base import TransformerMixin

from azureml.automl.core.constants import (
    _OperatorNames,
    _TransformerOperatorMappings,
    FeatureType,
    SupportedTransformersInternal)
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared import constants, logging_utilities
from azureml.automl.runtime.featurizer.transformer import (AutoMLTransformer, CategoricalFeaturizers,
                                                           DateTimeFeaturizers, DateTimeFeaturesTransformer,
                                                           featurization_utilities, GenericFeaturizers, get_ngram_len,
                                                           max_ngram_len, TextFeaturizers, TFIDF_VECTORIZER_CONFIG)

UNSUPPORTED_PARAMETER_WARNING_MSG = "Unsupported parameter passed to {t}, proceeding with default values"

logger = logging.getLogger(__name__)


def suggest_featurizers_for_categorical_hash_data(
        column: str,
        num_unique_categories: int,
        featurization_config: Optional[FeaturizationConfig] = None) -> List[TransformerMixin]:
    """
    Suggest featurizers for categorical hash data.

    :param column: Column name.
    :param num_unique_categories: Number of unique categories seen in the column.
    :param featurization_config: Custom featurization configuration provided by the customer to override featurizer
    parameters as necessary.
    :return: List of transformers.
    """
    hashing_seed_val_key = 'hashing_seed_val'
    num_cols_key = 'num_cols'
    # TODO: VSO: 1106675
    # FEATCATALOG This should move to Featurizer catalog as well where we disable a featurizer if any invalid
    # param values are provided for customization.
    customized_params = featurization_utilities.get_transformer_params_by_column_names(
        SupportedTransformersInternal.HashOneHotEncoder, [column], featurization_config
    )

    default_n_bits = int(math.log(num_unique_categories, 2))
    default_n_cols = pow(2, default_n_bits)
    hashonehot_vectorizer = None
    try:
        n_cols = None
        if "number_of_bits" in customized_params:
            n_bits = int(customized_params.pop("number_of_bits"))
            n_cols = pow(2, n_bits)

        hashonehot_vectorizer = CategoricalFeaturizers.hashonehot_vectorizer(
            **{
                hashing_seed_val_key: constants.hashing_seed_value,
                num_cols_key: int(n_cols or default_n_cols)
            }
        )

        if len(customized_params) > 0:
            logger.warning("Ignoring unsupported parameters.")
    except Exception as e:
        logging_utilities.log_traceback(e, logger, is_critical=False)
        logger.warning(
            UNSUPPORTED_PARAMETER_WARNING_MSG.format(t=SupportedTransformersInternal.HashOneHotEncoder)
        )
    finally:
        hashonehot_vectorizer = hashonehot_vectorizer or CategoricalFeaturizers.hashonehot_vectorizer(
            **{
                hashing_seed_val_key: constants.hashing_seed_value,
                num_cols_key: int(default_n_cols)
            })

    return [TextFeaturizers.string_cast(), hashonehot_vectorizer]


def suggest_featurizers_for_datetime_data(
        column: str,
        featurization_config: Optional[FeaturizationConfig] = None,
) -> List[TransformerMixin]:
    """
    Suggest featurizers for datetime column data.

    :param column: The column in the data frame.
    :param featurization_config: Custom featurization configuration.
    :return: List of transformers to be applied.
    """
    cat_imputer_params = {
        **featurization_utilities.get_transformer_params_by_column_names(
            SupportedTransformersInternal.CatImputer, [column], featurization_config)
    }

    return [CategoricalFeaturizers.cat_imputer(**cat_imputer_params),
            TextFeaturizers.string_cast(),
            DateTimeFeaturizers.datetime_transformer()]


def suggest_featurizers_for_categorical_data(
        column: str,
        num_unique_categories: int,
        featurization_config: Optional[FeaturizationConfig] = None,
        is_onnx_compatible: bool = False,
        enable_categorical_indicators: bool = False
) -> List[TransformerMixin]:
    """
    Create a list of transforms for categorical data.

    :param column: The column in the data frame.
    :param num_unique_categories: Number of unique categories.
    :param featurization_config: Custom featurization configuration.
    :param is_onnx_compatible: If the model is expected to be ONNX compatible.
    :return: List of transformers to be applied.
    """
    operator_name_key = 'operator_name'
    if num_unique_categories <= 2 or enable_categorical_indicators:
        transformer_fncs = [SupportedTransformersInternal.CatImputer,
                            SupportedTransformersInternal.StringCast,
                            SupportedTransformersInternal.LabelEncoder]

        # Check whether the transformer functions are in blocked list
        if featurization_config is not None:
            transformers_in_blocked_list = featurization_utilities.transformers_in_blocked_list(
                transformer_fncs, featurization_config.blocked_transformers)
            if transformers_in_blocked_list:
                logger.info("Excluding blocked transformer(s): {0}".format(transformers_in_blocked_list))
                return []

        cat_two_category_imputer = CategoricalFeaturizers.cat_imputer(
            **{
                **featurization_utilities.get_transformer_params_by_column_names(
                    SupportedTransformersInternal.CatImputer, [column], featurization_config),
                operator_name_key: _OperatorNames.Mode
            })
        cat_two_category_string_cast = TextFeaturizers.string_cast()
        cat_two_category_labelencoder = CategoricalFeaturizers.labelencoder(
            **{
                'hashing_seed_val': constants.hashing_seed_value,
                **featurization_utilities.get_transformer_params_by_column_names(
                    SupportedTransformersInternal.LabelEncoder, [column], featurization_config)
            })

        return [cat_two_category_imputer, cat_two_category_string_cast, cat_two_category_labelencoder]
    else:
        transformer_fncs = [SupportedTransformersInternal.StringCast,
                            SupportedTransformersInternal.CountVectorizer]

        # Check whether the transformer functions are in blocked list
        if featurization_config is not None:
            transformers_in_blocked_list = featurization_utilities \
                .transformers_in_blocked_list(transformer_fncs, featurization_config.blocked_transformers)
            if transformers_in_blocked_list:
                logger.info("Excluding blocked transformer(s): {0}".format(transformers_in_blocked_list))
                return []

        # Add the transformations to be done and get the alias name
        # for the hashing one hot encode transform.
        cat_multiple_category_string_cast = TextFeaturizers.string_cast()
        count_vect_lowercase = not is_onnx_compatible
        from azureml.automl.runtime.featurization.data_transformer import DataTransformer
        cat_multiple_category_count_vectorizer = \
            TextFeaturizers.count_vectorizer(
                **{
                    'tokenizer': DataTransformer._wrap_in_lst,
                    'binary': True,
                    'lowercase': count_vect_lowercase,
                    **featurization_utilities.get_transformer_params_by_column_names(
                        SupportedTransformersInternal.CountVectorizer, [column], featurization_config),
                    operator_name_key: _OperatorNames.CharGram
                })

        # use CountVectorizer for both Hash and CategoricalHash for now
        return [cat_multiple_category_string_cast, cat_multiple_category_count_vectorizer]


def suggest_featurizers_for_numeric_data(
        column: str,
        featurization_config: Optional[FeaturizationConfig] = None,
) -> List[TransformerMixin]:
    """
    Create a list of transforms for numeric data.

    :param column: The column in the data frame.
    :param featurization_config: Custom featurization configuration.
    :return: List of transformers to be applied.
    """
    params = featurization_utilities.get_transformer_params_by_column_names(SupportedTransformersInternal.Imputer,
                                                                            [column], featurization_config)

    imputation_strategy = params.get('strategy', None)
    params['strategy'] = imputation_strategy
    try:
        imputer = GenericFeaturizers.imputer(**params)
    except Exception as e:
        logging_utilities.log_traceback(e, logger, is_critical=False)
        logger.warning(
            UNSUPPORTED_PARAMETER_WARNING_MSG.format(t=SupportedTransformersInternal.Imputer)
        )
        imputer = GenericFeaturizers.imputer()

    return [imputer]


def suggest_featurizers_for_text_data(
        column: str,
        ngram_len: int,
        featurization_config: Optional[FeaturizationConfig] = None,
        is_onnx_compatible: bool = False,
        blocked_list: List[str] = []) -> List[TransformerMixin]:
    """
    Create a list of transforms for text data.

    :param column: Column name in the data frame.
    :param ngram_len: Continuous length of characters or number of words.
    :param featurization_config: Featurization configuration for customization.
    :param is_onnx_compatible: Should the model be ONNX compatible.
    :param blocked_list: List of transformers to exclude.
    :return: Text transformations to use.
    """
    transformer_fncs = [SupportedTransformersInternal.StringCast, SupportedTransformersInternal.TfIdf]
    transformers_in_blocked_list = featurization_utilities.transformers_in_blocked_list(transformer_fncs,
                                                                                        blocked_list)
    if transformers_in_blocked_list:
        logger.info("Excluding blocked transformer(s): {0}".format(transformers_in_blocked_list))
        return []

    transformers = []  # type: List[List[TransformerMixin]]
    ngram_len = min(max_ngram_len, ngram_len)
    logger.info("N-gram length for text column is: {0}".format(ngram_len))

    # Only allow char-gram features if the ngram_len is equal to or greater than
    # the AutoML default char gram range
    allow_chargram = ngram_len >= min(TFIDF_VECTORIZER_CONFIG.CHAR_NGRAM_RANGE)
    if allow_chargram and not is_onnx_compatible:
        # The trichar transform is currently not ONNX compatible.
        logger.info("Char-gram based features will be added.")
        text_trichar_string_cast = TextFeaturizers.string_cast()
        try:
            logger.info("Creating tfidf transformer with customized parameters")
            text_trichar_tfidf = TextFeaturizers.tfidf_vectorizer(
                **{
                    'use_idf': False,
                    'norm': TFIDF_VECTORIZER_CONFIG.NORM,
                    'max_df': TFIDF_VECTORIZER_CONFIG.MAX_DF,
                    'analyzer': TFIDF_VECTORIZER_CONFIG.CHAR_ANALYZER,
                    'ngram_range': TFIDF_VECTORIZER_CONFIG.CHAR_NGRAM_RANGE,
                    **featurization_utilities.get_transformer_params_by_column_names(
                        SupportedTransformersInternal.TfIdf, [column], featurization_config),
                    'operator_name': _OperatorNames.CharGram
                })
        except ValueError as e:  # this happens when customers pass in wrong invalid values for some parameters.
            logging_utilities.log_traceback(e, logger, is_critical=False)
            message = "Failed to create tfidf transformer with customized parameters.\n"
            message += "Creating tfidf transformer without customized parameters"
            logger.warning(message)
            text_trichar_tfidf = TextFeaturizers.tfidf_vectorizer(
                **{
                    'use_idf': False,
                    'norm': TFIDF_VECTORIZER_CONFIG.NORM,
                    'max_df': TFIDF_VECTORIZER_CONFIG.MAX_DF,
                    'analyzer': TFIDF_VECTORIZER_CONFIG.CHAR_ANALYZER,
                    'ngram_range': TFIDF_VECTORIZER_CONFIG.CHAR_NGRAM_RANGE,
                    'operator_name': _OperatorNames.CharGram
                })

        transformers.append([text_trichar_string_cast, text_trichar_tfidf])

    # sklearn's TFIDF vectorizer's default regexp selects tokens of 2 or more alphanumeric characters.
    # Hence if all strings in a text column are only 1 character long, the transformer will throw an
    # error. The below check avoids the error.
    if ngram_len >= TFIDF_VECTORIZER_CONFIG.MIN_WORD_NGRAM:
        # Add the transformations to be done and get the alias name for the bigram word transform
        text_biword_string_cast = TextFeaturizers.string_cast()
        tfidf_vect_lowercase = not is_onnx_compatible
        text_biword_tfidf = TextFeaturizers.tfidf_vectorizer(
            **{
                'use_idf': False,
                'norm': TFIDF_VECTORIZER_CONFIG.NORM,
                'analyzer': TFIDF_VECTORIZER_CONFIG.WORD_ANALYZER,
                'ngram_range': TFIDF_VECTORIZER_CONFIG.WORD_NGRAM_RANGE,
                'lowercase': tfidf_vect_lowercase,
                **featurization_utilities.get_transformer_params_by_column_names(
                    SupportedTransformersInternal.TfIdf, [column], featurization_config),
                'operator_name': _OperatorNames.WordGram
            })

        transformers.append([text_biword_string_cast, text_biword_tfidf])

    return transformers


def wrap_into_a_list(x: Any) -> List[Any]:
    """
    Wrap an element in list. For backward compatibility in 1.20.0 and 1.21.0.

    :param x: Element like string or integer.
    """
    return [x]

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for featurizers."""
from typing import Any, Callable, Dict, FrozenSet, ItemsView, List, Optional, Tuple, TypeVar, Union
import importlib
import logging

from azureml.automl.runtime.column_purpose_detection.types import StatsAndColumnPurposeType
from azureml.automl.core.constants import (
    TransformerNameMappings as _TransformerNameMappings,
    _FeaturizersType,
    FeatureType as _FeatureType,
    FeaturizationConfigMode as _FeaturizationConfigMode
)
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared.constants import NumericalDtype
from .automltransformer import AutoMLTransformer
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)
ReturnFeaturizerT = TypeVar('ReturnFeaturizerT', bound=AutoMLTransformer)


def if_package_exists(feature_name: str, packages: List[str]) \
        -> 'Callable[..., Callable[..., Optional[ReturnFeaturizerT]]]':
    """
    Check if package is installed.

    If exists then make call to the function wrapped.
    Else log the error and return None.

    :param feature_name: Feature name that wil be enabled or disabled based on packages availability.
    :param packages: Packages to check
    :return: Wrapped function call.
    """
    def func_wrapper(function: 'Callable[..., ReturnFeaturizerT]') -> 'Callable[..., Optional[ReturnFeaturizerT]]':

        def f_wrapper(*args: Any, **kwargs: Any) -> Optional[ReturnFeaturizerT]:
            package = None
            try:
                for package in packages:
                    importlib.import_module(name=package)
                return function(*args, **kwargs)

            except ImportError:
                logger.warning(
                    "'{}' package not found, '{}' will be disabled.".format(package, feature_name))
                return None

        return f_wrapper

    return func_wrapper


def update_customized_feature_types(
        stats_and_column_purposes: List[StatsAndColumnPurposeType],
        featurization_config: FeaturizationConfig
) -> None:
    log_featurization_config(featurization_config)
    for i, stats_and_column_purpose in enumerate(stats_and_column_purposes):
        if featurization_config.column_purposes is not None \
                and stats_and_column_purposes[i][2] in featurization_config.column_purposes:
            # We have already validated that the user's column purpose can be used
            # to convert the column (from inferred_feature_type). However, we still need to
            # validate numeric and datetime features have correct dtypes.
            user_configured_feature_purpose = featurization_config.column_purposes[stats_and_column_purpose[2]]
            inferred_feature_type = stats_and_column_purpose[1]
            inferred_dtype = stats_and_column_purpose[0].column_type

            # If numeric column is the desired user column purpose make sure it is one of numeric type.
            is_numeric_convertible = user_configured_feature_purpose == _FeatureType.Numeric and \
                inferred_dtype in NumericalDtype.CONVERTIBLE

            if user_configured_feature_purpose != _FeatureType.Numeric or is_numeric_convertible:
                stats_and_column_purposes[i] = (stats_and_column_purpose[0],
                                                user_configured_feature_purpose,
                                                stats_and_column_purpose[2])
                logger.info("Updating column number {} to {}.".format(i, user_configured_feature_purpose))
            else:
                logger.warning(
                    "Could not update column number {i} to {new_feature_type} "
                    "since since data is either all one value, too high of cardinality, "
                    "or all None. Setting back to {feature_type}. Please check your "
                    "column before overriding feature type.".format(
                        i=i,
                        new_feature_type=user_configured_feature_purpose,
                        feature_type=inferred_feature_type
                    )
                )
        if featurization_config.drop_columns is not None \
                and stats_and_column_purposes[i][2] in featurization_config.drop_columns:
            new_feature_type = _FeatureType.Ignore
            stats_and_column_purposes[i] = (stats_and_column_purpose[0],
                                            new_feature_type,
                                            stats_and_column_purpose[2])
            logger.info("Updating column number {} to {}.".format(i, new_feature_type))


def log_featurization_config(featurization_config: FeaturizationConfig) -> None:
    """
    Log PII-free parts of featurization config

    Print names of transformers with updated parameters
    Print names of blocked transformers

    Columns with type overridden and dropped columns are printed
    when they actually get updated in update_customized_feature_types()

    :param featurization_config:
    :return:
    """
    # Print Customized Transformer Names
    if featurization_config.transformer_params is not None:
        for transformer in featurization_config.transformer_params:
            logger.info("Customized Transformer: {}".format(transformer))

    # Print Blocked Transformers
    if featurization_config.blocked_transformers is not None:
        for transformer in featurization_config.blocked_transformers:
            logger.info("Blocked Transformer: {}".format(transformer))


def get_transform_names(transforms: Any = None) -> List[str]:
    """
    Get transform names as list of string.

    :param: Transforms which can be Pipeline or List.
    :return: List of transform names.
    """
    if transforms is None:
        return [""]
    transformer_list = []
    if isinstance(transforms, Pipeline):
        for tr in transforms.steps:
            transform = tr[1]
            if hasattr(transform, "steps"):
                for substep in transform.steps:
                    transformer_list.append(type(substep[1]).__name__)
            else:
                transformer_list.append(type(transform).__name__)
    else:
        transformer_list = [type(tr).__name__ for tr in transforms]

    return transformer_list


def does_property_hold_for_featurizer(featurizer: Union[Pipeline, List[Any]],
                                      prop: str) -> bool:
    """
    Returns whether or not the featurizer contains an element with the provided property enabled.

    :param featurizer: The featurizer to check.
    :param prop: The property we're checking for, such as is_distributable.
    :return: Boolean flag indicating if the property is true for the featurizer.
    """
    if isinstance(featurizer, Pipeline):
        for step in featurizer.steps:
            transform = step[1]
            if hasattr(transform, "steps") and does_property_hold_for_featurizer(transform, prop):
                return True
            elif getattr(transform, prop, False):
                return True
        return False
    else:
        return any([getattr(transform, prop, False) for transform in featurizer])


def get_transformer_column_groups(
        transformer: str, columns_to_transform: List[str],
        transformer_params: Dict[str, Any]) -> List[List[Any]]:
    """
    Get list of columns grouped based on transformer parameters
    :param transformer: name of the transformer
    :param columns_to_transform: list of columns to transform using this transformer
    :param transformer_params: parameter dictionary where key is transformer name and value is param info
    :return: list of column groups to be transformed together
    """
    column_groups = []
    param_dict = dict()  # type: Dict[Any, List[Any]]

    if transformer not in transformer_params:
        return [columns_to_transform]

    for col_list, params in transformer_params[transformer]:
        # currently supports single input column only
        # if column passed in is not part of the columns to be transformed, ignore
        if len(col_list) != 1 or col_list[0] not in columns_to_transform:
            continue
        if frozenset(params.items()) not in param_dict:
            param_dict[frozenset(params.items())] = [col_list[0]]
        else:
            param_dict[frozenset(params.items())].append(col_list[0])

    for params, cols in param_dict.items():
        column_groups.append(cols)

    columns_for_customization = [x for col_group in column_groups for x in col_group]
    columns_for_default_transform = list(set(columns_to_transform) - set(columns_for_customization))

    if len(columns_for_default_transform) > 0:
        column_groups.append(columns_for_default_transform)

    return column_groups


def get_transformer_params_by_column_names(transformer: str,
                                           cols: Optional[List[str]] = None,
                                           featurization_config: Any = None) -> Dict[str, Any]:
    """
    Get transformer parameters to customize for specified columns.

    :param transformer: Transformer name.
    :param cols: Columns names; empty list if customize for all columns.
    :param featurization_config: Featurization configuration object.
    :return: transformer params settings
    """
    if featurization_config is not None:
        params = featurization_config.get_transformer_params(transformer, cols) \
            if cols is not None else dict()  # type: Dict[str, Any]
        if len(params) == 0:
            # retrieve global transformer params setting
            params = featurization_config.get_transformer_params(transformer, [])
        return params
    return dict()


def get_transformers_method_mappings(transformer_list: List[str]) -> List[Tuple[str, str]]:
    factory_methods_types_mapping = []
    for transformer in transformer_list:
        factory_method_type = get_transformer_factory_method_and_type(transformer)
        if factory_method_type is not None:
            factory_methods_types_mapping.append(factory_method_type)
    return factory_methods_types_mapping


def get_transformer_factory_method_and_type(transformer: str) -> Optional[Tuple[str, str]]:
    if transformer in _TransformerNameMappings.CustomerFacingTransformerToTransformerMapCategoricalType:
        return ((
            str(_TransformerNameMappings.CustomerFacingTransformerToTransformerMapCategoricalType.get(transformer)),
            _FeaturizersType.Categorical
        ))
    elif transformer in _TransformerNameMappings.CustomerFacingTransformerToTransformerMapDateTimeType:
        return ((
            str(_TransformerNameMappings.CustomerFacingTransformerToTransformerMapDateTimeType.get(transformer)),
            _FeaturizersType.DateTime
        ))
    elif transformer in _TransformerNameMappings.CustomerFacingTransformerToTransformerMapGenericType:
        return ((
            str(_TransformerNameMappings.CustomerFacingTransformerToTransformerMapGenericType.get(transformer)),
            _FeaturizersType.Generic
        ))
    elif transformer in _TransformerNameMappings.CustomerFacingTransformerToTransformerMapNumericType:
        return ((
            str(_TransformerNameMappings.CustomerFacingTransformerToTransformerMapNumericType.get(transformer)),
            _FeaturizersType.Numeric
        ))
    elif transformer in _TransformerNameMappings.CustomerFacingTransformerToTransformerMapText:
        return ((
            str(_TransformerNameMappings.CustomerFacingTransformerToTransformerMapText.get(transformer)),
            _FeaturizersType.Text
        ))
    else:
        return None


def is_transformer_param_overridden(featurization_config: Any) -> Any:
    return featurization_config and featurization_config.transformer_params


def transformers_in_blocked_list(transformer_fncs: List[str], blocked_list: List[str]) -> List[str]:
    if blocked_list is None or len(blocked_list) == 0:
        return []

    blocked_transformers = []
    for fnc in transformer_fncs:
        if fnc in blocked_list:
            blocked_transformers.append(fnc)
    return blocked_transformers


def transformer_fnc_to_customer_name(transformer_fnc: str, featurizer_type: str) -> str:
    if featurizer_type == _FeaturizersType.Generic:
        return _fnc_to_customer_name(_TransformerNameMappings.
                                     CustomerFacingTransformerToTransformerMapGenericType.items(),
                                     transformer_fnc)
    if featurizer_type == _FeaturizersType.Numeric:
        return _fnc_to_customer_name(_TransformerNameMappings.
                                     CustomerFacingTransformerToTransformerMapNumericType.items(),
                                     transformer_fnc)
    if featurizer_type == _FeaturizersType.Categorical:
        return _fnc_to_customer_name(_TransformerNameMappings.
                                     CustomerFacingTransformerToTransformerMapCategoricalType.items(),
                                     transformer_fnc)
    if featurizer_type == _FeaturizersType.DateTime:
        return _fnc_to_customer_name(_TransformerNameMappings.
                                     CustomerFacingTransformerToTransformerMapDateTimeType.items(),
                                     transformer_fnc)
    if featurizer_type == _FeaturizersType.Text:
        return _fnc_to_customer_name(_TransformerNameMappings.
                                     CustomerFacingTransformerToTransformerMapText.items(),
                                     transformer_fnc)
    return ""


def skip_featurization(featurization_setting: Union[str, FeaturizationConfig], is_timeseries: bool = False) -> bool:
    if featurization_setting == _FeaturizationConfigMode.Off and not is_timeseries:
        return True
    return False


def get_prediction_transform_type(featurization_config: Any) -> Any:
    if featurization_config is None or \
            (isinstance(featurization_config, str)
                and featurization_config in (_FeaturizationConfigMode.Off, _FeaturizationConfigMode.Auto)):
        return None
    return featurization_config.prediction_transform_type


def _fnc_to_customer_name(mappings: ItemsView[str, str], fnc_name_to_find: str) -> str:
    for customer_name, fnc_name in mappings:
        if fnc_name == fnc_name_to_find:
            return customer_name
    return ""

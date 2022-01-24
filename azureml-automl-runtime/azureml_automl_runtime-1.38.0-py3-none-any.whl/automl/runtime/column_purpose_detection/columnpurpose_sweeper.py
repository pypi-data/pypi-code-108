# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods and classes used during an AutoML experiment to sweep through column purposes."""
from typing import List, Optional, Type, Union, Dict

from azureml.automl.core.shared.constants import NumericalDtype, TextOrCategoricalDtype, DatetimeDtype
from azureml.automl.core.constants import FeatureType as _FeatureType


class ColumnPurposeSweeper:
    """Methods and classes used during an AutoML experiment to sweep through column purposes."""

    # Possible safe conversions between types
    _SAFE_FEATURE_TYPE_CONVERSIONS = {_FeatureType.Hashes: _FeatureType.Text}  # type: Dict[str, str]
    _DTYPE_TO_FEATURE_TYPE_MAPPING = {
        _FeatureType.Categorical:
            {
                NumericalDtype.Integer: _FeatureType.Numeric,
                TextOrCategoricalDtype.Categorical: _FeatureType.Text,
                TextOrCategoricalDtype.String: _FeatureType.Text
            },
        _FeatureType.Text:
            {
                TextOrCategoricalDtype.String: _FeatureType.Categorical
            },
        _FeatureType.Numeric:
            {
                NumericalDtype.Integer: _FeatureType.Categorical
            }
    }   # type: Dict[str, Dict[str, str]]
    _FEATURE_TYPE_TO_ALLOWED_DTYPE_CONVERSIONS = {
        _FeatureType.Numeric: [
            NumericalDtype.Integer,
            NumericalDtype.Decimal,
            NumericalDtype.Empty,
            NumericalDtype.Floating,
            NumericalDtype.MixedIntegerFloat
        ],
        _FeatureType.DateTime: [
            DatetimeDtype.Date,
            DatetimeDtype.Datetime,
            DatetimeDtype.Datetime64,
            TextOrCategoricalDtype.String
        ]
    }   # type: Dict[str, List[str]]

    @classmethod
    def safe_convert_on_feature_type(cls: 'Type[ColumnPurposeSweeper]',
                                     feature_type: str) -> Optional[str]:
        """
        Provide possible safe type column conversion options for feature type.

        :param feature_type: Feature type of the current column.
        :return: Possible column purposes that are compatible and safe to use.
        """
        # Safe conversion between feature types
        if feature_type in cls._SAFE_FEATURE_TYPE_CONVERSIONS:
            return cls._SAFE_FEATURE_TYPE_CONVERSIONS[feature_type]

        return None

    @classmethod
    def safe_convert_on_data_type(cls: 'Type[ColumnPurposeSweeper]',
                                  feature_type: str,
                                  data_type: str = '') -> Optional[str]:
        """
        Provide possible safe type column conversion options for data type.

        :param feature_type: Feature type of the current column.
        :param data_type: Data type inferred from infer_dtype().
        :return: Possible column purposes that are compatible and safe to use.
        """
        # Safe conversion based on specific data type
        # (e.g. Numeric feature type can include integer, float, and others but only integer is used as categorical.
        if feature_type in cls._DTYPE_TO_FEATURE_TYPE_MAPPING:
            if data_type in cls._DTYPE_TO_FEATURE_TYPE_MAPPING[feature_type]:
                return cls._DTYPE_TO_FEATURE_TYPE_MAPPING[feature_type][data_type]

        return None

    @classmethod
    def is_feature_type_convertible(
        cls: 'Type[ColumnPurposeSweeper]',
        feature_type: str,
        data_type: str = ''
    ) -> bool:
        """
        Whether feature type conversion is supported.

        Currently Automated ML transformation for Numerical or Datetime may fail if they are of an unsupported dtype
        e.g.1 Numerical type will go through Numerical transformation.
        If string column is being forced to be Numerical feature type, it should block the conversion.
        e.g.2 Datetime type will go through Datetime transformation.
        If value does not contain a valid datetime format, it may fail transformer so conversion should be blocked.

        :param feature_type: Feature type to be set.
        :param data_type: Data type inferred from infer_dtype().
        :return: boolean True if column can be converted to new feature type based on inferred data type.
        """
        if feature_type in cls._FEATURE_TYPE_TO_ALLOWED_DTYPE_CONVERSIONS:
            if data_type in cls._FEATURE_TYPE_TO_ALLOWED_DTYPE_CONVERSIONS[feature_type]:
                return True
            else:
                return False
        return True

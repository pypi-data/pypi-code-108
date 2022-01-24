# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for interacting with azureml.automl.core"""
from azureml.automl.core.constants import (TransformerNameMappings as _TransformerNameMappings,
                                           _FeaturizersType)


def get_transformer_factory_method_and_type(transformer):
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

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Container class used for passing feature sweeped state around during data transformation."""
from typing import Optional, List, Union, cast

import numpy as np
from azureml.automl.core.shared._diagnostics.contract import Contract
from sklearn import preprocessing
from sklearn_pandas import DataFrameMapper

from azureml.automl.runtime.data_context import TransformedDataContext
from azureml.automl.runtime.featurization import DataTransformer, TransformerAndMapper
from azureml.automl.runtime._engineered_feature_names import _GenerateEngineeredFeatureNames
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType


class FeatureSweepedStateContainer:
    """
    Lightweight container class holding a group of objects
    frequently passed around together during data transformation.
    """
    def __init__(self,
                 data_transformer: DataTransformer,
                 transformed_data_context: TransformedDataContext,
                 y_transformer: Optional[preprocessing.LabelEncoder],
                 x: DataInputType,
                 y: np.ndarray):
        """
        Initialize a state container to describe the state of feature sweeping.

        :param data_transformer: The data_transformer generated in feature sweeping.
        :param transformed_data_context: The (unfinished) transformed data context
            that was created during feature sweeping.
        :param y_transformer: The y_transformer object that was created during feature sweeping.
        :param x: The input data used during data transformation.
        :param y: The input data used during data transformation.
        """
        self.data_transformer = data_transformer
        self.transformed_data_context = transformed_data_context
        self.y_transformer = y_transformer
        self.X = x
        self.y = y

        # validations
        Contract.assert_value(self.data_transformer, "data_transformer")

    def get_feature_config(self) -> Union[List[TransformerAndMapper], DataFrameMapper]:
        """
        Get the feature config, which is stored in the data transformer.
        This is needed to reconstruct the data transformer in the featurization run.

        :raises ValidationException: If DataTransformer is missing.
        :return: The list of transformers and mappers to perform full featurization on.
        """
        feature_config = self.data_transformer.transformer_and_mapper_list

        Contract.assert_value(feature_config, "feature_config")

        return feature_config

    def get_engineered_feature_names(self) -> _GenerateEngineeredFeatureNames:
        """
        Get the engineered feature names class, which is stored in the data transformer.
        This is needed to reconstruct the data transformer in the featurization run.

        :raises ValidationException: If DataTransformer is missing.
        :return: The engineered feature names class that is used to generate the engineered feature names.
        """
        engineered_feature_names_class = self.data_transformer._engineered_feature_names_class
        Contract.assert_value(engineered_feature_names_class, "engineered_feature_names_class")
        return engineered_feature_names_class

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
import logging

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared._diagnostics.contract import Contract
from sklearn_pandas import DataFrameMapper

from azureml.automl.core.constants import FeaturizationRunConstants
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType, TransformerType

if TYPE_CHECKING:
    from . import DataTransformer, TransformerAndMapper  # conditional import to avoid circular dependency issues

logger = logging.getLogger(__name__)


class FeaturizerFactory:
    """
    Class for generating different featurizers based on the json properties available.
    """
    @staticmethod
    def get_featurizer(properties: Dict[str, Any], is_onnx_compatible: bool = False) -> "BaseFeaturizer":
        """
        The factory method for building featurizers.

        :param properties: The property dict obtained from the featurization JSON corresponding to this featurizer.
        :param is_onnx_compatible: Boolean flag specifying if we are using onnx for the
        :return: A featurizer.
        """
        return ComputedFeaturizer(index=properties[FeaturizationRunConstants.INDEX_KEY],
                                  is_cached=properties.get(FeaturizationRunConstants.CACHED, False),
                                  is_distributable=properties.get(FeaturizationRunConstants.IS_DISTRIBUTABLE, False),
                                  is_separable=properties.get(FeaturizationRunConstants.IS_SEPARABLE, False),
                                  transformers=properties[FeaturizationRunConstants.TRANSFORMERS_KEY])


class BaseFeaturizer(ABC):
    """
    Base class representing a featurizer.
    """
    def __init__(self,
                 index: int,
                 transformers: List[str],
                 is_cached: bool,
                 is_distributable: bool,
                 is_separable: bool,
                 *args: Any, **kwargs: Any):
        """
        Initialize a featurizer to be fitted.

        :param index: The index of the featurizer in the DataTransformer's transformer_and_mapper_list or
        mapper.features, depending on whether or not we're using onnx.
        :param is_cached: Whether this featurizer has already been fitted and cached.
        :param is_distributable: Whether this featurizer is distributable or not.
        :param is_separable: Whether this featurizer can be scheduled and processed separately
        from the rest of featurization.
        :param transformers: The transformers associated with this featurizer.
        """
        self.index = index
        self.is_cached = is_cached
        self.is_distributable = is_distributable
        self.is_separable = is_separable
        self.transformers = transformers

    def fit(self,
            data_transformer: 'DataTransformer',
            df: DataInputType,
            y: Optional[DataSingleColumnInputType],
            **kwargs: Any) -> Any:
        """
        Log information about the featurizer and then fit it.

        :param data_transformer: The DataTransformer that we will use to fit the featurizer.
        :param df: The input data.
        :param y: The input label data.
        :return: The fitted featurizer to be cached.
        """
        logger.info("Fitting individual featurizer with {} components.".format(self.transformers))

        Contract.assert_value(data_transformer, "data_transformer")
        Contract.assert_value(df, "input_data")

        with logging_utilities.log_activity(logger=logger,
                                            activity_name="FitIndividualFeaturizer"):
            return self._fit(data_transformer=data_transformer,
                             df=df,
                             y=y,
                             **kwargs)

    @abstractmethod
    def _fit(self,
             data_transformer: 'DataTransformer',
             df: DataInputType,
             y: Optional[DataSingleColumnInputType],
             **kwargs: Any) -> Any:
        """
        Abstract method for fitting an individual featurizer.

        :param data_transformer: The DataTransformer whose self.index's featurizer we will be fitting.
        :param df: The input data we will be fitting on.
        :param y: The input label data to be used.
        :return: The fitted featurizer to be cached.
        """
        raise NotImplementedError


class ComputedFeaturizer(BaseFeaturizer):
    """
    Class representing a basic featurizer chosen during feature sweeping. Currently not expected to be used for
    any special code paths, such as streaming or forecasting. Any custom logic specific to basic individual
    featurizers can reside in this class.
    """
    def __init__(self,
                 index: int,
                 transformers: List[str],
                 is_cached: bool = False,
                 is_distributable: bool = False,
                 is_separable: bool = False,
                 **kwargs: Any):
        """
        Initialize a sweeped featurizer.

        :param index: The integer index of the featurizer in the DataTransformer's transformer_and_mapper_list.
        :param is_cached: Whether this featurizer has already been fitted and cached.
        :param is_distributable: Whether this featurizer is distributable or not.
        :param is_separable: Whether this featurizer can be scheduled and processed separately
        from the rest of featurization.
        :param transformers: The transformers associated with this featurizer.
        """
        super(ComputedFeaturizer, self).__init__(index=index,
                                                 transformers=transformers,
                                                 is_cached=is_cached,
                                                 is_distributable=is_distributable,
                                                 is_separable=is_separable,
                                                 **kwargs)

    def _fit(self,
             data_transformer: 'DataTransformer',
             df: DataInputType,
             y: Optional[DataSingleColumnInputType],
             **kwargs: Any) -> 'TransformerAndMapper':
        """
        The method used to fit this featurizer, only called in an independent featurizer run.

        :param data_transformer: The DataTransformer whose self.index's featurizer we will be fitting.
        :param df: The input data we will be fitting on.
        :param y: The input label data to be used.
        :return: The fitted featurizer to be cached.
        """
        featurizer = data_transformer.transformer_and_mapper_list[self.index]  # type: 'TransformerAndMapper'
        data_transformer._set_is_text_dnn_if_available(featurizer)
        data_transformer.fit_individual_transformer_mapper(
            transformer_mapper=featurizer,
            df=df,
            y=y
        )
        return featurizer

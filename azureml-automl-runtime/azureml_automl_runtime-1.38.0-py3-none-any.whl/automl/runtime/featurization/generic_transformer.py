# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generic transformer."""
from typing import Dict, List, Optional
import logging

from azureml.automl.runtime.shared.types import TransformerType
from azureml.automl.core.constants import (FeatureType as _FeatureType,
                                           SupportedTransformersInternal as _SupportedTransformersInternal,
                                           _TransformerOperatorMappings,
                                           _OperatorNames)
from azureml.automl.runtime._engineered_feature_names import _GenerateEngineeredFeatureNames, _FeatureTransformers, \
    _Transformer, _TransformerParamsHelper
from ..featurizer.transformer import featurization_utilities
from ..featurizer.transformer.automltransformer import AutoMLTransformer
from ..featurizer.transformer.generic.generic_featurizers import GenericFeaturizers


logger = logging.getLogger(__name__)


class GenericTransformer(AutoMLTransformer):
    """Class for generic transformer."""
    def __init__(self,
                 is_onnx_compatible: bool = False):
        """
        Construct the GenericTransformer.
        :param logger: Logger to be injected to usage in this class.
        :param is_onnx_compatible: if works in onnx compatible mode
        """
        super().__init__()
        self.is_onnx_compatible = is_onnx_compatible

    def get_transforms(self,
                       column_groups: Dict[str, List[str]],
                       engineering_feature_name_class: _GenerateEngineeredFeatureNames,
                       blocked_list: List[str] = []) -> \
            List[TransformerType]:
        """
        Create a list of transforms for generic transforms.
        :param column_groups: Dictionary of column purpose and list of column labels for that purpose.
        :param engineering_feature_name_class: Existing engineered feature names.
        :param blocked_list: List of transformers to exclude.
        :return: Generic Transformations to use in a list.
        """
        return self.get_minibatchkmeans_transforms(column_groups, engineering_feature_name_class, blocked_list)

    def get_minibatchkmeans_transforms(self,
                                       column_groups: Dict[str, List[str]],
                                       engineering_feature_name_class: _GenerateEngineeredFeatureNames,
                                       blocked_list: List[str] = []) -> \
            List[TransformerType]:
        """
        Create a list of transforms for minibatch kmeans.
        :param column_groups: Dictionary of column purpose and list of column labels for that purpose.
        :param engineering_feature_name_class: Existing engineered feature names.
        :param blocked_list: List of transformers to exclude.
        :return: MiniBatch Kmeans Transformations to use in a list.
        """
        # Check if this needs to be revisited once it is Onnx compatible
        tr = []  # type: List[TransformerType]
        transformer_fncs = [_SupportedTransformersInternal.Imputer,
                            _SupportedTransformersInternal.MaxAbsScaler,
                            _SupportedTransformersInternal.MiniBatchKMeans]
        transformers_in_blocked_list = featurization_utilities\
            .transformers_in_blocked_list(transformer_fncs, blocked_list)
        if transformers_in_blocked_list:
            logger.info("Excluding blocked transformer(s): {0}".format(transformers_in_blocked_list))
            return tr

        if self.is_onnx_compatible:
            logger.info("MiniBatchKMeans is not onnx_commpatbile")
            return tr
        # do not apply if only one numeric column
        if _FeatureType.Numeric in column_groups and len(column_groups[_FeatureType.Numeric]) < 2:
            logger.info(
                "MiniBatchKMeans transformer not applied as dataset does not contain 2 or more Numeric features")
            return tr
        imputer = GenericFeaturizers.imputer()
        maxabsscaler = GenericFeaturizers.maxabsscaler()
        minibatchkmeans_transformer = GenericFeaturizers.minibatchkmeans_featurizer()
        clusters = minibatchkmeans_transformer.n_clusters
        features = ":".join([str(col) for col in column_groups[_FeatureType.Numeric]])
        CNAME = "MiniBatchKMeans_" + str(clusters) + ":" + features

        numeric_transformer = _Transformer(
            parent_feature_list=[str(CNAME)],
            transformation_fnc=transformer_fncs[0],
            operator=_TransformerOperatorMappings.Imputer.get(imputer.strategy, _OperatorNames.Mean),
            feature_type=_FeatureType.Numeric,
            should_output=True,
            transformer_params=_TransformerParamsHelper.to_dict(imputer))
        numeric_maxabsscaler_transformer = _Transformer(
            parent_feature_list=[1],
            transformation_fnc=transformer_fncs[1],
            operator=None,
            feature_type=_FeatureType.Numeric,
            should_output=False,
            transformer_params=_TransformerParamsHelper.to_dict(maxabsscaler))
        generic_minibatchkmeans_transformer = _Transformer(
            parent_feature_list=[2],
            transformation_fnc=transformer_fncs[2],
            operator=None,
            feature_type=_FeatureType.Numeric,
            should_output=True,
            transformer_params=_TransformerParamsHelper.to_dict(minibatchkmeans_transformer))
        feature_transformers = \
            _FeatureTransformers(
                [numeric_transformer, numeric_maxabsscaler_transformer, generic_minibatchkmeans_transformer])
        json_obj = feature_transformers.encode_transformations_from_list()
        alias_column_name = engineering_feature_name_class.get_raw_feature_alias_name(json_obj)
        tr = [(
            column_groups[_FeatureType.Numeric],
            [imputer, maxabsscaler, minibatchkmeans_transformer],
            {'alias': alias_column_name}
        )]
        return tr

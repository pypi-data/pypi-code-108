# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Transformer that featurizes a dataset in the streaming scenario."""
import json
from typing import List, Optional, Any

from nimbusml import Pipeline
from nimbusml.internal.core.base_pipeline_item import BasePipelineItem

from azureml.automl.core.shared.types import FeaturizationSummaryType
from azureml.automl.runtime._engineered_feature_names import _GenerateEngineeredFeatureNames
from azureml.automl.runtime.featurization_info_provider import FeaturizationInfoProvider
from azureml.automl.runtime.featurization.streaming import NimbusMLStreamingEstimator


class StreamingFeaturizationTransformer(BasePipelineItem, FeaturizationInfoProvider):
    """Transformer that featurizes a dataset in the streaming scenario."""
    def __init__(
            self,
            transformer: NimbusMLStreamingEstimator,
            features_metadata_helper: _GenerateEngineeredFeatureNames):
        self._transformer = transformer
        self._features_metadata_helper = features_metadata_helper

        # set type to satisfy BasePipelineItem requirement
        self.type = 'transform'

    @property
    def pipeline(self) -> Pipeline:
        return self._transformer.pipeline

    def fit(self, training_data, **kwargs):
        self.pipeline.fit(training_data, None, **kwargs)
        return self

    def fit_transform(self, training_data):
        self.pipeline.fit(training_data, None)
        return self.pipeline.transform(training_data)

    def get_engineered_feature_names(self) -> List[str]:
        """
        Get the engineered feature names.

        Return the list of engineered feature names as string after data transformations on the
        raw data have been finished.

        :return: The list of engineered fearure names as strings
        """
        return self._features_metadata_helper._engineered_feature_names

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
        return self._features_metadata_helper.get_raw_features_featurization_summary(is_user_friendly)

    def get_params(self):
        """Scikit-learn API with same params, returns all parameters."""
        return self._transformer.pipeline.get_params()

    def transform(self, X, **kwargs):
        return self.pipeline.transform(X, **kwargs)

    def _get_json_str_for_engineered_feature_name(self,
                                                  engineered_feature_name: str) -> Optional[str]:
        """
        Return JSON string for engineered feature name.

        :param engineered_feature_name: Engineered feature name for
                                        whom JSON string is required
        :return: JSON string for engineered feature name
        """
        engineered_feature_name_json_obj = self._features_metadata_helper \
            .get_json_object_for_engineered_feature_name(engineered_feature_name)
        if engineered_feature_name_json_obj is None:
            return None
        return json.dumps(engineered_feature_name_json_obj)

    def _get_node(self, **all_args):
        pass

    def __str__(self) -> str:
        return "{}(steps={})".format(
            self.__class__.__name__,
            str(self.pipeline.steps)
        )

    __repr__ = __str__

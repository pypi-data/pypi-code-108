# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for objects that provide featurization info."""
from abc import ABC, abstractmethod
from typing import List, Optional, Any

from azureml.automl.core.shared.types import FeaturizationSummaryType


class FeaturizationInfoProvider(ABC):
    """Base class for objects that provide featurization info."""

    @abstractmethod
    def get_engineered_feature_names(self) -> Optional[List[str]]:
        """
        Get the engineered feature names.

        Return the list of engineered feature names as string after data transformations on the
        raw data have been finished.

        :return: The list of engineered fearure names as strings
        """
        raise NotImplementedError  # PII safe to raise directly

    @abstractmethod
    def get_featurization_summary(self, **kwargs: Any) -> FeaturizationSummaryType:
        """
        Return the featurization summary for all the input features seen by DataTransformer.

        :return: List of featurization summary for each input feature.
        """
        raise NotImplementedError  # PII safe to raise directly

    def get_json_strs_for_engineered_feature_names(self,
                                                   engi_feature_name_list: Optional[List[str]] = None) -> List[str]:
        """
        Return JSON string list for engineered feature names.

        :param engi_feature_name_list: Engineered feature names for
                                       whom JSON strings are required
        :return: JSON string list for engineered feature names
        """
        engineered_feature_names_json_str_list = []

        if engi_feature_name_list is None:
            engi_feature_name_list = self.get_engineered_feature_names()

        if engi_feature_name_list is None:
            return []

        # Walk engineering feature name list and get the corresponding
        # JSON string
        for engineered_feature_name in engi_feature_name_list:

            json_str = self._get_json_str_for_engineered_feature_name(
                engineered_feature_name)

            if json_str is not None:
                engineered_feature_names_json_str_list.append(json_str)

        # Return the list of JSON strings for engineered feature names
        return engineered_feature_names_json_str_list

    @abstractmethod
    def _get_json_str_for_engineered_feature_name(self,
                                                  engineered_feature_name: str) -> Optional[str]:
        """
        Return JSON string for engineered feature name.

        :param engineered_feature_name: Engineered feature name for
                                        whom JSON string is required
        :return: JSON string for engineered feature name
        """
        raise NotImplementedError  # PII safe to raise directly

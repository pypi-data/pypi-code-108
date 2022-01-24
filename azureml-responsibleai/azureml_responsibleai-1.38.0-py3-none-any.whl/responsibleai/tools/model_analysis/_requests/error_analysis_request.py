# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, List

from azureml.responsibleai.tools._common.base_request import BaseRequest


class ErrorAnalysisRequest(BaseRequest):
    def __init__(self,
                 max_depth: Optional[int] = None,
                 num_leaves: Optional[int] = None,
                 filter_features: Optional[List[str]] = None,
                 comment: Optional[str] = None):
        """Initialize the ErrorAnalysisRequest.

        Must be pickleable. And ideally JSON-able
        """
        super(ErrorAnalysisRequest, self).__init__()
        self._comment = comment
        self._max_depth = max_depth
        self._num_leaves = num_leaves
        self._filter_features = filter_features

    @property
    def max_depth(self) -> Optional[int]:
        return self._max_depth

    @property
    def num_leaves(self) -> Optional[int]:
        return self._num_leaves

    @property
    def filter_features(self) -> Optional[List[str]]:
        return self._filter_features

    @property
    def comment(self) -> Optional[str]:
        return self._comment

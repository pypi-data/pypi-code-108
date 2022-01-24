# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional
import uuid

from azureml.responsibleai.tools._common.constants import AnalysisTypes
from azureml.responsibleai.tools.model_analysis._requests.causal_request import CausalRequest
from azureml.responsibleai.tools.model_analysis._requests.counterfactual_request import CounterfactualRequest
from azureml.responsibleai.tools.model_analysis._requests.error_analysis_request import ErrorAnalysisRequest
from azureml.responsibleai.tools.model_analysis._requests.explain_request import ExplainRequest


class RequestDTO:
    """Pickleable object for transmitting the requests to remote compute.

    Ideally we ought to be able to convert this to JSON as well."""

    def __init__(self,
                 *,
                 causal_requests: Optional[List[CausalRequest]] = None,
                 counterfactual_requests: Optional[List[CounterfactualRequest]] = None,
                 error_analysis_requests: Optional[List[ErrorAnalysisRequest]] = None,
                 explanation_requests: Optional[List[ExplainRequest]] = None):
        self._causal_requests = causal_requests if causal_requests is not None else []
        self._counterfactual_requests = counterfactual_requests if counterfactual_requests is not None else []
        self._explain_requests = explanation_requests if explanation_requests is not None else []
        self._error_analysis_requests = error_analysis_requests if error_analysis_requests is not None else []

    @property
    def causal_requests(self) -> List[CausalRequest]:
        return self._causal_requests

    @property
    def error_analysis_requests(self) -> List[ErrorAnalysisRequest]:
        return self._error_analysis_requests

    @property
    def explanation_requests(self) -> List[ExplainRequest]:
        return self._explain_requests

    @property
    def counterfactual_requests(self) -> List[CounterfactualRequest]:
        return self._counterfactual_requests

    def _get_rai_computation_name(self):
        rai_computation_name = ''
        if len(self.causal_requests) > 0:
            rai_computation_name = AnalysisTypes.CAUSAL_TYPE
        elif len(self.counterfactual_requests) > 0:
            rai_computation_name = AnalysisTypes.COUNTERFACTUAL_TYPE
        elif len(self.error_analysis_requests) > 0:
            rai_computation_name = AnalysisTypes.ERROR_ANALYSIS_TYPE
        else:
            rai_computation_name = AnalysisTypes.EXPLANATION_TYPE

        rai_computation_name += '-' + str(uuid.uuid4())[:8]
        return rai_computation_name

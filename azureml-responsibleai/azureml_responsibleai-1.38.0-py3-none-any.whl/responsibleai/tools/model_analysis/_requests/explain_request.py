# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azureml.responsibleai.tools._common.base_request import BaseRequest


class ExplainRequest(BaseRequest):
    def __init__(self,
                 comment: Optional[str]):
        """Initialize the ExplainRequest.

        Must be pickleable. And ideally JSON-able
        """
        super(ExplainRequest, self).__init__()
        self._comment = comment

    @property
    def comment(self) -> Optional[str]:
        return self._comment

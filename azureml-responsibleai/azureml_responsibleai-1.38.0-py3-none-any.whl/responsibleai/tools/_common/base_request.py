# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC


class BaseRequest(ABC):
    def __init__(self):
        """Initialize the BaseRequest.

        All implementations must be pickleable. And ideally JSON-able
        """
        super(BaseRequest, self).__init__()

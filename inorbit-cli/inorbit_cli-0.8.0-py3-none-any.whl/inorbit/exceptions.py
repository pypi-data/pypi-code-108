# Copyright (c) 2021, InOrbit, Inc.
# All rights reserved.

from typing import Optional, Union

class InOrbitError(Exception):
    def __init__(
        self,
        error_message: Union[str, dict] = "",
        response_code: Optional[int] = None,
        response_body: Optional[dict] = None,
    ) -> None:

        Exception.__init__(self, error_message)
        # Http status code
        self.response_code = response_code
        # Full http response
        self.response_body = response_body

class InOrbitAuthenticationError(InOrbitError):
    pass

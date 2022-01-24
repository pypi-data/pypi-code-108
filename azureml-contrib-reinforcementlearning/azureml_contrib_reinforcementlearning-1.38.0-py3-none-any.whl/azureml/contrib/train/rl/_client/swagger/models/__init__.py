# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

try:
    from .run_details_py3 import RunDetails
    from .inner_error_response_py3 import InnerErrorResponse
    from .root_error_py3 import RootError
    from .error_response_py3 import ErrorResponse, ErrorResponseException
except (SyntaxError, ImportError):
    from .run_details import RunDetails
    from .inner_error_response import InnerErrorResponse
    from .root_error import RootError
    from .error_response import ErrorResponse, ErrorResponseException

__all__ = [
    'RunDetails',
    'InnerErrorResponse',
    'RootError',
    'ErrorResponse', 'ErrorResponseException'
]

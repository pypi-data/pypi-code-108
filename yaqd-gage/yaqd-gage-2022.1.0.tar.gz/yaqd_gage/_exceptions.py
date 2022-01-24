"""Python Exceptions for Gage codes."""

from typing import Any, Dict


from ._constants import error_codes


class CompuScopeException(Exception):
    def __init__(self, error_code):
        if error_code in error_codes:
            message = f"{error_code}: {error_codes[error_code]}"
        else:
            message = f"{error_code}: unrecognized error code"
        super().__init__(message)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module holding the StatusRecord class."""
from typing import cast, List, Optional
import inspect

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.exceptions import UserException


class StatusRecord(object):
    """
    Helper class tracking status of calls by group.
    """
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    USER_ERROR = "UserError"
    SYSTEM_ERROR = "SystemError"

    def __init__(
            self,
            data: List[str],
            status: str,
            input_source: str,
            output_source: Optional[str] = None,
            error_type: Optional[str] = None,
            error_message: Optional[str] = None,
    ) -> None:
        # These args name should be the same for the serialization and deserialization.
        self.data = data
        self.status = status
        self.input_source = input_source
        self.output_source = output_source
        self.error_message = error_message
        self.error_type = error_type

        if self.status == self.SUCCEEDED:
            Contract.assert_true(
                self.error_type is None and self.error_message is None,
                reference_code=ReferenceCodes._HTS_STATUS_RECORD_SUCCESS_WITH_ERROR,
                message="StatusRecord does not support success with error."
            )

    def __eq__(self, other: object) -> bool:
        Contract.assert_type(other, "other", StatusRecord, ReferenceCodes._HTS_STATUS_TYPE_ERROR)
        other = cast(StatusRecord, other)
        return self.data == other.data and\
            self.status == other.status and\
            self.input_source == other.input_source and\
            self.output_source == other.output_source and\
            self.error_message == other.error_message and\
            self.error_type == other.error_type

    @staticmethod
    def get_args_list() -> List[str]:
        """Return the list of arguments for this class."""
        return inspect.getfullargspec(StatusRecord).args[1:]

    @staticmethod
    def get_error_type(exception: BaseException) -> str:
        return StatusRecord.USER_ERROR if isinstance(exception, UserException) else StatusRecord.SYSTEM_ERROR

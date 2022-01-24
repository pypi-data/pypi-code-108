# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holding the execution context class."""
import re


class ExecutionContext:
    """
    Class containing the information needed for ClientRunner execution context.

    This class object is passed to subprocess, so it should be serializable.
    """

    def __init__(self, run_id: str):
        """
        Construct ExecutionContext object.

        :param run_id: client run id
        """
        self.run_id = run_id

    @property
    def parent_run_id(self) -> str:
        """
        Get the parent run id for this execution context.

        :return: the parent run id
        """
        match = re.fullmatch(r'(.*?)_(?:setup|[0-9]+)', self.run_id)
        if match is None:
            return self.run_id
        return match.group(1)

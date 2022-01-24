# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor base."""

from .accessories.open_dataset_base import OpenDatasetBase


class NoParameterOpenDatasetBase(OpenDatasetBase):
    """US labor base class."""

    def __init__(
            self,
            enable_telemetry: bool = True):
        """
        Initialize.

        :param enable_telemetry: whether to send telemetry
        :type enable_telemetry: bool
        """

        super(NoParameterOpenDatasetBase, self).__init__(
            cols=None, enable_telemetry=enable_telemetry)

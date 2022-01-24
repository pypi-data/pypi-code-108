# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Errors for the package."""
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal
from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings


class AutoMLVisionInternal(AutoMLInternal):
    """Top level unknown system error."""
    @property
    def message_format(self) -> str:
        """Non-formatted error message"""
        return AutoMLErrorStrings.AUTOML_VISION_INTERNAL  # type: ignore[no-any-return]

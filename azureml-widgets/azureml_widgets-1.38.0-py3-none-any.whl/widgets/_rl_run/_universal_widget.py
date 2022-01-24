# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.widgets._universal_widgets import _RunWidgetBase


class _RLWidget(_RunWidgetBase):
    """RL Run widget object."""

    runType = "reinforcementlearning"

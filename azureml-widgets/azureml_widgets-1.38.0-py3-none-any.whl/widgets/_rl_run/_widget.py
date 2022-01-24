# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ipywidgets import register as register_widget
from traitlets import Unicode
from azureml.widgets._widgets import _RunWidgetBase


@register_widget
class _RLWidget(_RunWidgetBase):
    """RL Jupyter Widget."""

    _view_name = Unicode('ShowRLRunsView').tag(sync=True)
    _model_name = Unicode('ShowRLRunsModel').tag(sync=True)

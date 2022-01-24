# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from multiprocessing.dummy import Pool

from azureml.widgets.run_details import PLATFORM
# noinspection PyProtectedMember
from azureml.widgets._userrun._run_details import _UserRunDetails
# noinspection PyProtectedMember
from azureml.widgets._pipeline._transformer import _PipelineGraphTransformer
# noinspection PyProtectedMember
from azureml.widgets._telemetry_logger import _TelemetryLogger

_logger = _TelemetryLogger.get_telemetry_logger(__name__)

if PLATFORM == 'JUPYTER':
    # noinspection PyProtectedMember
    from azureml.widgets._userrun._widget import _UserRunWidget
    # noinspection PyProtectedMember
    from azureml.widgets._pipeline._widget import _PipelineWidget
    from azureml.widgets._utils import _update_multirun_widget_refresh_sleep_time as _refresh_sleep_time_updater
else:
    assert PLATFORM == "DATABRICKS"
    # noinspection PyProtectedMember
    from azureml.widgets._userrun._universal_widget import _UserRunWidget
    # noinspection PyProtectedMember
    from azureml.widgets._pipeline._universal_widget import _PipelineWidget
    from azureml.widgets._utils import _update_databricks_widget_refresh_sleep_time as _refresh_sleep_time_updater


class _StepRunDetails(_UserRunDetails):
    """StepRun run details widget."""

    def __init__(self, run_instance):
        """
        Initialize a StepRun widget call.
        """
        _logger.info("Creating worker pool")
        self._pool = Pool()
        super().__init__(run_instance, "Pipeline", widget=_UserRunWidget, rehydrate_runs=True,
                         refresh_sleep_time_updater=_refresh_sleep_time_updater)

    def __del__(self):
        """Destructor for the widget."""
        _logger.info("Closing worker pool")
        self._pool.close()
        if super().__del__:
            super().__del__()

    def _create_transformer(self):
        return _PipelineGraphTransformer()


class _PipelineRunDetails(_UserRunDetails):
    """Pipeline run details widget."""

    def __init__(self, run_instance):
        """
        Initialize a Pipeline widget call.
        """
        super().__init__(run_instance, "Pipeline", widget=_PipelineWidget, rehydrate_runs=True,
                         refresh_sleep_time_updater=_refresh_sleep_time_updater)

    def get_widget_data(self, widget_settings=None):
        widget_data = super().get_widget_data(widget_settings)
        graph = self.transformer._transform_graph(self.run_instance.get_graph(),
                                                  list(self._run_cache.values()))
        widget_data['child_runs'] = graph['child_runs']
        widget_data['graph'] = graph
        self.widget_instance.child_runs = graph['child_runs']
        self.widget_instance.graph = graph
        return widget_data

    def _create_transformer(self):
        return _PipelineGraphTransformer()

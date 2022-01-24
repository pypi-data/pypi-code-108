# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import datetime
import json

from azureml.widgets.run_details import PLATFORM
# noinspection PyProtectedMember
from azureml.core._metrics import INLINE_METRICS
# noinspection PyProtectedMember
from azureml.widgets._userrun._run_details import _UserRunDetails


if PLATFORM == 'JUPYTER':
    # noinspection PyProtectedMember
    from azureml.widgets._rl_run._widget import _RLWidget
    from azureml.widgets._utils import _update_multirun_widget_refresh_sleep_time as _refresh_sleep_time_updater
else:
    assert PLATFORM == "DATABRICKS"
    # noinspection PyProtectedMember
    from azureml.widgets._rl_run._universal_widget import _RLWidget
    from azureml.widgets._utils import _update_databricks_widget_refresh_sleep_time as _refresh_sleep_time_updater


class _RLRunDetails(_UserRunDetails):
    """RL run details widget."""

    def __init__(self, run_instance):
        """Initialize a RL run widget call.

        :param run_instance: The RL run instance.
        :type run_instance: RLRun
        """
        super().__init__(run_instance, "reinforcementlearning", widget=_RLWidget,
                         refresh_sleep_time_updater=_refresh_sleep_time_updater)

        self.rl_run_last_metric_retrieval_time = None
        self._rl_run_metrics_cache = []

    def _add_additional_properties(self, run_properties):

        super()._add_additional_properties(run_properties)
        tags = run_properties['tags']
        if 'cluster_coordination_timeout_seconds' in tags:
            run_properties['cluster_coordination_timeout_seconds'] = tags['cluster_coordination_timeout_seconds']

    def _get_child_runs(self):
        _child_runs = super()._get_child_runs()
        prepRunSuccess = None
        for run in _child_runs:
            run_id = run['run_id']
            run_type = run['run_type']
            run_status = run['status']
            if run_type == 'preparation' and run_status != 'Failed':
                prepRunSuccess = run
                continue

            if run_id in self.tags:
                arguments = json.loads(self.tags[run_id])
                if arguments:
                    for name, value in arguments.items():
                        run['param_' + name] = value

        if prepRunSuccess is not None:
            _child_runs.remove(prepRunSuccess)

        return _child_runs

    # For RL run, the parent run metrics should be the metrics of the first child run.
    # RL run can have atmost 3 child runs - Trainer, worker and simulator
    # Trainer and worker runs have the same result for get_metrics()
    # Simulator run has no metrics logged.
    def _get_run_metrics(self):
        transformed_run_metrics = []
        _child_runs = super()._get_child_runs()
        if len(_child_runs) > 0:
            child_run_id = _child_runs[0]['run_id']

            last_metric_retrieval_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)
            unmerged_metrics = self.metrics_client._get_all_metrics(
                run_ids=[child_run_id], use_batch=True, metric_types=INLINE_METRICS,
                after_timestamp=self.rl_run_last_metric_retrieval_time,
                merge_strategy_type="None")
            self.rl_run_last_metric_retrieval_time = last_metric_retrieval_time

            unmerged_metrics = unmerged_metrics[child_run_id]
            self._rl_run_metrics_cache.extend(unmerged_metrics)

            run_metrics = copy.deepcopy(self._rl_run_metrics_cache)
            run_metrics = self.metrics_client.dto_to_metrics_dict(run_metrics)
            run_metrics = self.metrics_client._metric_conversion_for_widgets(run_metrics)

            for key, value in run_metrics.items():
                metric_data = {
                    'name': key,
                    'run_id': self.run_instance.id,
                    # get_metrics can return array or not based on metrics being series or scalar value
                    'categories': list(range(len(value))) if isinstance(value, list) else [0],
                    'series': [{'data': value if isinstance(value, list) else [value]}]}
                transformed_run_metrics.append(metric_data)

            model_explanation_metric = self._get_model_explanation_metric()
            if (model_explanation_metric):
                transformed_run_metrics.append(model_explanation_metric)

        return transformed_run_metrics

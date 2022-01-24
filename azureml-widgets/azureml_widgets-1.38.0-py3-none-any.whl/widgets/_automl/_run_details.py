# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import json
import math

from azureml.widgets.run_details import PLATFORM
# noinspection PyProtectedMember
from azureml.widgets._userrun._run_details import _UserRunDetails
# noinspection PyProtectedMember
from azureml.widgets._automl._transformer import _AutoMLDataTransformer

if PLATFORM == 'JUPYTER':
    # noinspection PyProtectedMember
    from azureml.widgets._automl._widget import _AutoMLWidget
    from azureml.widgets._utils import _update_automl_widget_refresh_sleep_time as _refresh_sleep_time_updater
else:
    assert PLATFORM == "DATABRICKS"
    # noinspection PyProtectedMember
    from azureml.widgets._automl._universal_widget import _AutoMLWidget
    from azureml.widgets._utils import _update_databricks_widget_refresh_sleep_time as _refresh_sleep_time_updater


class _AutoMLRunDetails(_UserRunDetails):
    """AutoML run details widget."""

    def __init__(self, run_instance):
        """Initialize a Run Details widget call.

        :param run_instance: automl run instance.
        :type run_instance: AutoMLRun
        """
        super().__init__(run_instance, "automl", widget=_AutoMLWidget,
                         refresh_sleep_time_updater=_refresh_sleep_time_updater)

    def _update_children_with_metrics(self, child_runs, metrics):
        # for each child run add their corresponding primary metric values amd best metric reached so far

        if metrics and metrics['series']:
            child_runs_local = copy.deepcopy(child_runs)

            pmc = self._get_primary_config()['name']
            pmc_goal = self._get_primary_config()['goal']
            goal_name = '_min' if pmc_goal == 'minimize' else '_max'
            primary_metric = {}
            best_metric = {}

            for _key, dataList in metrics['series'].items():
                for x in dataList:
                    if x['name'] == pmc:
                        primary_metric = dict(zip(x['categories'], x['data']))
                    elif x['name'] == pmc + goal_name:
                        best_metric = dict(zip(x['categories'], x['data']))

            for num in range(0, len(child_runs_local)):
                itr = child_runs_local[num]
                if ('iteration' not in itr):
                    continue
                iteration = itr['iteration']
                if iteration in primary_metric:
                    itr['primary_metric'] = round(primary_metric[iteration], 8) \
                        if iteration in primary_metric \
                        and not math.isnan(float(primary_metric[iteration])) else None
                    itr['best_metric'] = round(best_metric[iteration], 8) \
                        if iteration in best_metric \
                        and not math.isnan(float(best_metric[iteration])) else None

            return child_runs_local

    def _get_mapped_metrics(self, metrics, child_runs):
        run_number_mapper = {c['run_id']: c['iteration'] for c in child_runs if 'iteration' in c}
        return {run_number_mapper[k]: v for k, v in metrics.items()}

    def _get_metrics(self, child_runs):
        metrics = super()._get_metrics(child_runs)

        pmc = self._get_primary_config()['name']
        goal_name = '_min' if self._get_primary_config()['goal'] == 'minimize' else '_max'

        # Automl currently populates the max field; remove that to resolve conflict
        for run_id in metrics:
            metrics[run_id].pop(pmc + goal_name, None)

        return metrics

    def _get_primary_config(self):
        config_settings = json.loads(self.properties['AMLSettingsJsonString'])
        config = {
            'name': config_settings['primary_metric'],
            'goal': config_settings['metric_operation']
        }
        return config

    def _create_transformer(self):
        return _AutoMLDataTransformer()

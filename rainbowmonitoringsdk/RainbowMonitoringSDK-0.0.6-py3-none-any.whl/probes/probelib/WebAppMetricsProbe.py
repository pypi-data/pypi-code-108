import json
import logging
import os
import random
import time
from os.path import exists

import requests

from RainbowMonitoringSDK.probes.Metric import SimpleMetric, CounterMetric, DiffMetric, TimerMetric
from RainbowMonitoringSDK.probes.Probe import Probe


class WebAppMetricsProbe(Probe):

    def __init__(self,
                 periodicity, debug=False, _logging=False,
                 **kwargs):
        Probe.__init__(self, "WebAppLevelMetrics", periodicity,  debug, _logging )
        self.config = kwargs

    def get_desc(self):
        return "The monitoring probe of user defined metrics"

    def collect(self):
        json_metrics = self.retrieve_metrics()
        for _metric in json_metrics:
            metric = self.__metric_from_dictionary(_metric)
            self.add_metric(metric)

    @staticmethod
    def __metric_from_dictionary(collected):
        metric = SimpleMetric(collected.get('name'), collected.get('units'), collected.get('desc'))
        metric.set_val(collected.get('val'))
        metric.set_group(collected.get('group'))
        return metric

    def retrieve_metrics(self):
        res = []
        paths = self.config['sources']

        for path in paths:
            try:
                response = requests.get(path).json()
                for name, val in response.items():
                    res.append({
                        'name': name,
                        'val': float(val),
                        'units': 'NaN',
                        'desc': f'Metric for {name}.',
                        'group': 'WebAppMetricsProbe'
                        })
            except Exception as e:
                print(e)
        return res




    def get_metrics(self):
        self.collect()
        return Probe.get_metrics(self)

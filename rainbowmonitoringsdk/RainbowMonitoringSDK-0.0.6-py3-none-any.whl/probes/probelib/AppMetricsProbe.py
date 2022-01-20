import json
import logging
import os
import random
import time
from os.path import exists
from RainbowMonitoringSDK.probes.Metric import SimpleMetric, CounterMetric, DiffMetric, TimerMetric
from RainbowMonitoringSDK.probes.Probe import Probe


class AppMetricsProbe(Probe):

    def __init__(self,
                 periodicity, debug=False, _logging=False,
                 **kwargs):
        Probe.__init__(self, "AppLevelMetrics", periodicity,  debug, _logging )
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
        # metric.set_timestamp()
        metric.set_group(collected.get('group'))
        return metric

    def retrieve_metrics(self):
        res = []
        paths = self.config['sources']

        for path in paths:
            path_exists = path and exists(path)

            if path_exists and os.path.isdir(path):
                path = path + "rainbow.metrics.jsonl"
            path_exists = path and exists(path)

            if path_exists:
                set_of_metrics = self.__read_metrics_from_file(path)
                res.extend(set_of_metrics)
                self.__remove_file(path)
        return res

    @staticmethod
    def __read_metrics_from_file(path):
        res = []
        with open(path, 'r') as json_file:
            for line in json_file.readlines():
                try:
                    data = json.loads(line)
                    res.append(data)
                except Exception:
                    logging.error("An error occured at loading json line", exc_info=True)
                    continue
        return res

    @staticmethod
    def __remove_file(path):
        os.remove(path)

    def get_metrics(self):
        self.collect()
        return Probe.get_metrics(self)

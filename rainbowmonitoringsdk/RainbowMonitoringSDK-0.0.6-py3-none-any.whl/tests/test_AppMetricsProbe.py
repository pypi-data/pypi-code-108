import unittest

from RainbowMonitoringSDK.probes.probelib.AppMetricsProbe import AppMetricsProbe
from unittest.mock import patch


class TestAppMetricsProbe(unittest.TestCase):

    def setUp(self):
        self.configs = {"sources":["/test"]}
        self.app_probe = AppMetricsProbe(5, **self.configs)

    def test_init(self):
        self.assertEqual(self.app_probe.get_name(),"AppLevelMetrics")
        self.assertEqual(self.app_probe.get_periodicity(), 5)
        self.assertEqual(self.app_probe.config, self.configs)

    @patch.object(AppMetricsProbe, 'retrieve_metrics')
    def test_collect(self,retrieve_metrics):
        vals = [
            {"name": "name-1", "units": "unit-1", "desc": "desc-1", "val": 1},
            {"name": "name-2", "units": "unit-2", "desc": "desc-2", "val": 2}
            ]
        retrieve_metrics.return_value = vals
        prob = AppMetricsProbe(5, **self.configs)
        prob.collect()
        self.assertEqual(["name-1", "name-2"], list(prob.metrics.keys()))

    @patch.object(AppMetricsProbe, 'retrieve_metrics')
    def test_get_metrics(self, retrieve_metrics):
        vals = [{"name": "name-1", "units": "unit-1", "desc": "desc-1", "val": 1},
            {"name": "name-2", "units": "unit-2", "desc": "desc-2", "val": 2}]
        retrieve_metrics.return_value = vals
        prob = AppMetricsProbe(5, **self.configs)
        prob.collect()
        self.assertEqual(["name-1", "name-2"], list(prob.get_metrics().keys()))

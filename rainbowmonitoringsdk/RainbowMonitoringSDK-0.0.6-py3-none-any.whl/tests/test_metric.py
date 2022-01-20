import unittest
import uuid
from datetime import datetime
from queue import Queue
from unittest.mock import patch

from RainbowMonitoringSDK.probes.Metric import Metric
from RainbowMonitoringSDK.probes.Probe import Probe, ProbeStatus


class TestMetric(unittest.TestCase):

    @patch.multiple(Probe, __abstractmethods__=set())
    def setUp(self):
        self.metric = Metric("metric-1", "units", "desc")  # dummy metric for test


    def test_name(self):
        self.assertEqual(self.metric.get_name(),"metric-1")
        self.metric.set_name("metric-2")
        self.assertEqual(self.metric.get_name(), "metric-2")

    def test_units(self):
        self.assertEqual(self.metric.get_units(), "units")
        self.metric.set_units("units-2")
        self.assertEqual(self.metric.get_units(), "units-2")

    def test_desc(self):
        self.assertEqual(self.metric.get_desc(), "desc")
        self.metric.set_desc("desc-2")
        self.assertEqual(self.metric.get_desc(), "desc-2")

    def test_higherIsBetter(self):
        self.assertEqual(self.metric.get_higherisbetter(), True)
        self.metric.set_higherisbetter(False)
        self.assertEqual(self.metric.get_higherisbetter(), False)
        self.assertEqual(Metric("metric-1", "units", "desc", higherIsBetter=False).get_higherisbetter(), False)


    def test_minVal(self):
        self.assertEqual(self.metric.get_minval(), None)
        self.metric.set_minval(0.0)
        self.assertEqual(self.metric.get_minval(), 0.0)
        self.assertEqual(Metric("metric-1", "units", "desc", minVal=0.0).get_minval(), 0.0)

    def test_maxVal(self):
        self.assertEqual(self.metric.get_maxval(), None)
        self.metric.set_maxval(0.0)
        self.assertEqual(self.metric.get_maxval(), 0.0)
        self.assertEqual(Metric("metric-1", "units", "desc", maxVal=0.0).get_maxval(), 0.0)

    def test_group(self):
        self.assertEqual(self.metric.get_group(), None)
        self.metric.set_group("test-group")
        self.assertEqual(self.metric.get_group(), "test-group")

    def test_val(self):
        self.assertEqual(self.metric.get_val(), None)
        self.metric.set_val(0.0)
        self.assertEqual(self.metric.get_val(), 0.0)
        self.metric.set_val(1.0)
        self.assertEqual(self.metric.get_val(), 1.0)

    def test_timestamp(self):
        self.assertEqual(self.metric.get_timestamp(), None)
        first_timestamp = datetime.now().timestamp()
        self.metric.set_timestamp(first_timestamp)
        self.assertEqual(self.metric.get_timestamp(), first_timestamp)
        second_timestamp = datetime.now().timestamp()
        self.metric.set_timestamp(second_timestamp)
        self.assertEqual(self.metric.get_timestamp(), second_timestamp)



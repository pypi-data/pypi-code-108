import unittest
import uuid
from queue import Queue
from unittest.mock import patch

from RainbowMonitoringSDK.probes.Metric import Metric
from RainbowMonitoringSDK.probes.Probe import Probe, ProbeStatus


class TestProbe(unittest.TestCase):

    @patch.multiple(Probe, __abstractmethods__=set())
    def setUp(self):
        self.basic_probe = Probe("test-probe", 5)
        self.metric = Metric("metric-1", "units", "desc")  # dummy metric for test

    def test_set_logging(self):
        self.assertFalse(self.basic_probe.logging)
        self.assertIsNone(self.basic_probe.logger)
        self.basic_probe.set_logging("test/logging")
        self.assertTrue(self.basic_probe.logging)
        self.assertIsNotNone(self.basic_probe.logger)


    def test_attach_queue(self):
        queue = self.basic_probe.attachQueue()
        self.assertEqual(queue.maxsize, 1000000)
        queue = self.basic_probe.attachQueue()
        test_queue = Queue(maxsize=1000000)
        queue = self.basic_probe.attachQueue(test_queue)
        self.assertEqual(test_queue, queue)

    def test_dettach_queue(self):
        self.basic_probe.attachQueue()
        self.basic_probe.dettachQueue()
        self.assertIsNone(self.basic_probe.queue)
    #
    def test_get_probeid(self):
        self.assertEqual(type(self.basic_probe.get_probeid()), uuid.UUID)

    def test_get_name(self):
        self.assertEqual(self.basic_probe.get_name(), "test-probe")
    #
    def test_set_name(self):
        self.basic_probe.set_name("test-probe-2")
        self.assertEqual(self.basic_probe.get_name(), "test-probe-2")

    #
    def test_get_periodicity(self):
        self.assertEqual(self.basic_probe.periodicity, 5)
    #
    def test_set_periodicity(self):
        self.basic_probe.set_periodicity(10)
        self.assertEqual(self.basic_probe.periodicity, 10)
    #
    def test_get_probestatus(self):
        self.assertEqual(self.basic_probe.get_probestatus(), ProbeStatus.INACTIVE)


    def test_set_probestatus(self):
        self.assertEqual(self.basic_probe.get_probestatus(), ProbeStatus.INACTIVE)
        self.basic_probe.set_probestatus(ProbeStatus.TERM)
        self.assertEqual(self.basic_probe.get_probestatus(), ProbeStatus.TERM)
        self.basic_probe.set_probestatus(ProbeStatus.INACTIVE)
        self.assertEqual(self.basic_probe.get_probestatus(), ProbeStatus.INACTIVE)
    #
    def test_add_metric(self):
        self.basic_probe.add_metric(self.metric)
        self.assertEqual({self.metric.get_name(): self.metric}, self.basic_probe.metrics)
    #
    def test_get_metric(self):
        self.assertEqual(dict(),self.basic_probe.get_metrics())
    #
    def test_get_metrics(self):
        self.assertEqual(dict(), self.basic_probe.get_metrics())
    #
    def test_get_metrics_as_list(self):
        self.basic_probe.add_metric(self.metric)
        self.assertEqual([self.metric], list(self.basic_probe.get_metrics_as_list()))

    #
    def test_debugmode(self):
        self.assertFalse(self.basic_probe.get_debugmode())
        self.basic_probe.set_debugmode(True)
        self.assertTrue(self.basic_probe.get_debugmode())

    #
    def test_probe_lifecycle(self):
        self.basic_probe.activate()
        self.assertEqual(self.basic_probe.get_probestatus(), ProbeStatus.ACTIVE)
        self.basic_probe.deactivate()
        self.assertEqual(self.basic_probe.get_probestatus(), ProbeStatus.INACTIVE)
        self.basic_probe.terminate()
        self.assertEqual(self.basic_probe.get_probestatus(), ProbeStatus.TERM)
        self.basic_probe.run()

#




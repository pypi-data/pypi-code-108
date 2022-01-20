import unittest
from unittest import TestCase

from RainbowMonitoringSDK.exporters.Exporter import Exporter, ExporterStatus


class TestExporters(TestCase):

    def setUp(self):
        self.exporter = Exporter("test-exporter")

    def test_update(self):
        data = {"test": "test"}
        self.assertEqual(self.exporter.update(data), data,
                         "Wrong dissimination rate of data")

    def test_get_name(self):
        self.assertEqual(self.exporter.get_name(), "test-exporter")

    def test_set_name(self):
        self.exporter.set_name("test-exporter-2")
        self.assertEqual(self.exporter.get_name(), "test-exporter-2")

    def test_get_exporter_status(self):
        self.assertEqual(self.exporter.get_exporter_status(), ExporterStatus.INACTIVE)

    def test_set_exporter_status(self):
        self.assertEqual(self.exporter.get_exporter_status(), ExporterStatus.INACTIVE)
        self.exporter.set_exporter_status(ExporterStatus.TERM)
        self.assertEqual(self.exporter.get_exporter_status(), ExporterStatus.TERM)
        self.exporter.set_exporter_status(ExporterStatus.ACTIVE)
        self.assertEqual(self.exporter.get_exporter_status(), ExporterStatus.ACTIVE)

    def test_probe_lifecycle(self):
        self.exporter.activate()
        self.assertEqual(self.exporter.get_exporter_status(), ExporterStatus.ACTIVE)
        self.exporter.deactivate()
        self.assertEqual(self.exporter.get_exporter_status(), ExporterStatus.INACTIVE)
        self.exporter.terminate()
        self.assertEqual(self.exporter.get_exporter_status(), ExporterStatus.TERM)


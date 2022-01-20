import os
import utils
from unittest import TestCase
from unittest.mock import patch

from RainbowMonitoringSDK.controller import Controller
from RainbowMonitoringSDK.probes.probelib.NetDataProbe import NetDataProbe
from RainbowMonitoringSDK.probes.Probe import ProbeStatus
from RainbowMonitoringSDK.exporters.exporterlib.IgniteExporter import IgniteExporter
from RainbowMonitoringSDK.exporters.Exporter import ExporterStatus


class TestExporters(TestCase):

    def setUp(self):
        configs = {"sensing-units": {"DefaultMonitoring": {"periodicity": "2m"}},
                   "dissemination-units": {"IgniteExporter": {"hostname": "test", "port": "1999"}}}
        mock_node_id_environ = patch.dict(os.environ, {"NODE_ID": "test_node_id"})
        mock_node_id_environ.start()
        self.controller = Controller(configs)
        self.empty_controller = Controller()

    def test_instantiate_sensing_units(self):
        self.empty_controller.instantiate_sensing_units()
        self.assertEqual(len(self.empty_controller.sensing_units), 0, "Sensing Units should be empty")

        self.controller.instantiate_sensing_units()
        self.assertEqual(len(self.controller.sensing_units), 1, "Sensing Units should have one unit")
        self.assertEqual(type(self.controller.sensing_units["DefaultMonitoring"]), NetDataProbe,
                         "Sensing Units should be NetData")

    def test_instantiate_dissemination_units(self):
        self.empty_controller.instantiate_dissemination_units()
        self.assertEqual(len(self.empty_controller.dissemination_units), 0, "Dissemination Units should be empty")

        self.controller.instantiate_dissemination_units()
        self.assertEqual(len(self.controller.dissemination_units), 1, "Dissemination Units should have one unit")
        self.assertEqual(type(self.controller.dissemination_units["IgniteExporter"]), IgniteExporter,
                         "Dissemination Units should be IgniteExporter")

    @patch('subprocess.Popen')
    def test_start_sensing_units(self, mock_subproc_popen):
        self.controller.start_sensing_units()
        self.assertEqual(self.controller.sensing_units["DefaultMonitoring"].get_probestatus(), ProbeStatus.ACTIVE,
                         "ProbeStatus should be activated")
        self.controller.sensing_units["DefaultMonitoring"].terminate()

    def test_start_dissemination_units(self):
        self.controller.start_dissemination_units()
        self.assertEqual(self.controller.dissemination_units["IgniteExporter"].get_exporter_status(),
                         ExporterStatus.ACTIVE, "ExporterStatus should be activated")
        self.controller.dissemination_units["IgniteExporter"].terminate()


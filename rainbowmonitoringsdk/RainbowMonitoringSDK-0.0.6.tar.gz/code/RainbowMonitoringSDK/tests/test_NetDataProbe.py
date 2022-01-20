
import unittest
from time import sleep

import requests
from RainbowMonitoringSDK.probes.Probe import ProbeStatus
from RainbowMonitoringSDK.probes.probelib.AppMetricsProbe import AppMetricsProbe
from unittest.mock import MagicMock, patch

from RainbowMonitoringSDK.probes.probelib.NetDataProbe import NetDataProbe
from requests.models import Response

def mocked_requests_get(*args, **kwargs):
    f = open("netdata_response.txt", "r")
    text = f.read()
    response = Response()
    response.status_code = 200
    response._content = str.encode(text)
    return response

class TestAppMetricsProbe(unittest.TestCase):

    def setUp(self):
        self.periodicity = 5
        self.prefix = "_test"
        self.ip_address = 'localhost'
        self.port = '19999'
        self.netdata_probe = NetDataProbe(periodicity=self.periodicity,
                                      prefix=self.prefix,
                                      ip_address=self.ip_address,
                                      port=self.port)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_collect(self, mock_get):
        self.netdata_probe.collect()
        self.assertGreater(len(self.netdata_probe.metrics),0)

import os
from unittest import TestCase
from unittest.mock import patch

from RainbowMonitoringSDK.exporters.exporterlib.RestAPIExporter import RestAPIExporter


# This method will be used by the mock to replace requests.post
def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, status_code, text):
            self.text = text
            self.status_code = status_code

    return MockResponse(200, "ok")


class TestExporters(TestCase):

    def setUp(self):
        self.path = "/path"
        self.port = 8080
        self.exporter = RestAPIExporter(self.port, self.path)
        self.app = self.exporter.app.test_client()
        mock_node_id_environ = patch.dict(os.environ, {"NODE_ID": "test_node_id"})
        mock_node_id_environ.start()

    @patch('requests.post', side_effect=mocked_requests_post)
    def test_update(self, mock_post):

        metrics = {"metric1": {"name": "testing_name1", "units": "", "desc": ""}}
        self.exporter.update(metrics)
        response = self.app.get(self.path, headers={"Content-Type": "application/json"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(metrics, response.json)

        metrics_2 = {"metric2": {"name": "_CGROUP_testing_name1", "units": "", "desc": ""}}
        metrics.update(metrics_2)
        self.exporter.update(metrics)
        response = self.app.get(self.path, headers={"Content-Type": "application/json"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(metrics, response.json)

        metrics_2 = {"metric2": {"name": "_CGROUP_testing_name2", "units": "", "desc": ""}}
        metrics.update(metrics_2)
        self.exporter.update(metrics)
        response = self.app.get(self.path, headers={"Content-Type": "application/json"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(metrics, response.json)

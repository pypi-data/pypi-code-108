import os
from unittest import TestCase
from unittest.mock import patch

from RainbowMonitoringSDK.exporters.exporterlib.IgniteExporter import IgniteExporter
from RainbowMonitoringSDK.probes.Metric import Metric, SimpleMetric


# This method will be used by the mock to replace requests.post
def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, status_code, text):
            self.text = text
            self.status_code = status_code

    return MockResponse(200, "ok")


class TestExporters(TestCase):

    def setUp(self):
        self.hostname = "_test"
        self.port = '19999'
        self.exporter = IgniteExporter(self.hostname, self.port)
        mock_node_id_environ = patch.dict(os.environ, {"NODE_ID": "test_node_id"})
        mock_node_id_environ.start()

    # find a way to check input of post request and find the correct input
    @patch('requests.post', side_effect=mocked_requests_post)
    def test_update(self, mock_post):
        metric = SimpleMetric(name="_CGROUP_testing_name1", units="", desc="")
        metrics = {"metrics": {"metric1": metric}}
        with self.assertLogs() as captured:
            self.exporter.update(metrics)
        self.assertEqual(len(captured.records), 1)  # check that there is only one log message

    @patch('requests.post', side_effect=mocked_requests_post)
    def test_extract_metric_representation(self, mock_post):
        # case: entity is a fog node
        metric = SimpleMetric(name="testing_name1", units="", desc="")
        metrics = {"metrics": {"metric1": metric}}
        expected_result = [{'desc': '',
                            'entityID': 'test_node_id',
                            'entityType': 'FOG_NODE',
                            'metricID': 'testing_name1',
                            'name': 'testing_name1'
                            }]
        self.exporter.update(metrics)
        self.assertEqual(expected_result[0]["desc"], self.exporter.metric_repr[0]["desc"], "Wrong desc for fog node")
        self.assertEqual(expected_result[0]["entityID"], self.exporter.metric_repr[0]["entityID"], "Wrong entityId for fog node")
        self.assertEqual(expected_result[0]["entityType"], self.exporter.metric_repr[0]["entityType"], "Wrong entityType for fog node")
        self.assertEqual(expected_result[0]["metricID"], self.exporter.metric_repr[0]["metricID"], "Wrong metricID for fog node")
        self.assertEqual(expected_result[0]["name"], self.exporter.metric_repr[0]["name"], "Wrong testing_name1 for fog node")

        # case: entity is a container
        metric = SimpleMetric(name="_CGROUP_testing_name1", units="", desc="")
        metrics = {"metrics": {"metric1": metric}}
        self.exporter.update(metrics)
        expected_result = [{'desc': '',
                            'entityID': 'testing_name',
                            'entityType': 'CONTAINER',
                            'metricID': '_CGROUP_testing_name1',
                            'name': '_CGROUP_testing_name1'
                            }]
        self.assertEqual(expected_result[0]["desc"], self.exporter.metric_repr[0]["desc"], "Wrong desc for container")
        self.assertEqual(expected_result[0]["entityID"], self.exporter.metric_repr[0]["entityID"], "Wrong entityId for container")
        self.assertEqual(expected_result[0]["entityType"], self.exporter.metric_repr[0]["entityType"], "Wrong entityType for container")
        self.assertEqual(expected_result[0]["metricID"], self.exporter.metric_repr[0]["metricID"], "Wrong metricID for container")
        self.assertEqual(expected_result[0]["name"], self.exporter.metric_repr[0]["name"], "Wrong name for container")

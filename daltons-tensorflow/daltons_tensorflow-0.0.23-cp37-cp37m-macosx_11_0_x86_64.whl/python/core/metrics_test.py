import unittest
import socket
import urllib.request
import time
import uuid 
from prometheus_client.parser import text_string_to_metric_families

from daltons_tensorflow.python.core.metrics import enable_metrics, disable_metrics, Counter, Gauge

         
def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port

port = get_free_port()

class TestMetrics(unittest.TestCase):
    def setUp(self):
        self._modelId = uuid.uuid1().hex

        enable_metrics(":{}".format(port))
        time.sleep(1)

    def tearDown(self):
        disable_metrics()
    
    def test_counter(self):
        counter = Counter("policy_id", self._modelId, "some_counter")
        counter.add(123)
        self.assertEqual(self.get_metric(
            "daltons_model_counter_metric_sum_total",
        ), 123)

        counter.add(1)
        self.assertEqual(self.get_metric(
            "daltons_model_counter_metric_sum_total", 
        ), 124)

    def test_gauge(self):
        gauge = Gauge("policy_id", self._modelId, "some_counter")
        gauge.set(123)

        self.assertEqual(self.get_metric(
            "daltons_model_gauge_metric", 
        ), 123)

        gauge.set(1)

        self.assertEqual(self.get_metric(
            "daltons_model_gauge_metric", 
        ), 1)

    def get_metric(self, metric):
        url = f'http://localhost:{port}/metrics'
        f = urllib.request.urlopen(url)
        
        contents = f.read().decode('utf-8')
        for family in text_string_to_metric_families(contents):
            for sample in family.samples:
                if sample.name == metric and sample.labels['model_id'] == self._modelId:
                    return sample.value

from nehushtan.httpd.NehushtanHTTPRequestController import NehushtanHTTPRequestController
from tests.httpd.TestRequestHandler import TestRequestHandler


class TestMQ(NehushtanHTTPRequestController):

    def product(self, queue_name: str, item: str):
        TestRequestHandler.mq.enqueue(item, queue_name)
        self._reply_with_ok("done")

    def consume(self, queue_name: str):
        x = TestRequestHandler.mq.dequeue(queue_name)
        if x is None:
            self._reply_with_ok({"mq_empty": True})
        else:
            self._reply_with_ok({"mq_empty": False, 'message': x})

    def statAll(self):
        x = TestRequestHandler.mq.stat_for_all()
        self._reply_with_ok({"mq_stat": x})

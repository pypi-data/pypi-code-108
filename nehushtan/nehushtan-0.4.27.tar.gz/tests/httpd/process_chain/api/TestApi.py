from nehushtan.httpd.NehushtanHTTPRequestController import NehushtanHTTPRequestController


class TestApi(NehushtanHTTPRequestController):
    def hi(self, x):
        self._reply_with_ok({"x": x})

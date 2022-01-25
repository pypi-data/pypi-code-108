import unittest
import io

from dslibrary import DSLibrary
from dslibrary.transport.http_to_dsl import HttpToDsl, RequestInfo


class TestHttpToDsl(unittest.TestCase):

    def test_rw_resource(self):
        files = {"a": io.BytesIO(b'abc')}
        class MyDsl(DSLibrary):
            def open_resource(self, resource_name: str, mode: str='rb', **kwargs):
                if mode == 'wb':
                    stream = io.BytesIO()
                    stream.close = lambda: None
                    files[resource_name] = stream
                    return stream
                if mode == 'rb':
                    return files[resource_name]
        xlt = HttpToDsl(MyDsl(), base_path="api")
        r = xlt.translate(RequestInfo("get", "/api/resources?resource_name=a"))
        assert r.content == b'abc'
        r = xlt.translate(RequestInfo("put", "/api/resources?resource_name=a", post_data=b'def'))
        assert r.content == {}
        assert files["a"].getvalue() == b'def'

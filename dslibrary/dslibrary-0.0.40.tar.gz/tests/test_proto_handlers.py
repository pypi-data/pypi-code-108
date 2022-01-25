import os
import io
import unittest

from dslibrary import DSLibrary, instance
from dslibrary.proto_handlers import load_protocol_handler, ProtocolHandler


class TestProtoHandlers(unittest.TestCase):

    def test_load_protocol_handler(self):
        """
        The basic idea: set an environment variable telling us how to handle a given protocol.
        """
        os.environ["DSLIBRARY_PROTO_ZZZ"] = "tests.test_proto_handlers.MyProtoZZZ:v=hello"
        handler = load_protocol_handler("zzz://host/etc")
        assert handler
        assert handler.open_resource("x", "rb").read() == b'hello'

    def test_through_open_resource(self):
        os.environ["DSLIBRARY_PROTO_ZZZ"] = "tests.test_proto_handlers.MyProtoZZZ:v=hello2"
        with DSLibrary().open_resource("x", "rb", uri="zzz://x") as f:
            assert f.read() == b'hello2'

    def test_through_get_filesystem(self):
        os.environ["DSLIBRARY_PROTO_ZZZ"] = "tests.test_proto_handlers.MyProtoZZZ:v=hello2"
        fs = DSLibrary().get_filesystem_connection("zzz://x")
        with fs.open("x") as f_r:
            assert f_r.read() == b'from_fs'

    def test_through_dslibrary_instance__with_custom_env(self):
        dsl = instance({"DSLIBRARY_PROTO_ZZZ": "tests.test_proto_handlers.MyProtoZZZ:v=hello3"})
        r = dsl.read_resource("zzz://x")
        assert r == b'hello3'


class MyProtoZZZ(ProtocolHandler):
    def __init__(self, v="zzz"):
        self.v = v

    def open_resource(self, url: str, mode: str, **kwargs):
        return io.BytesIO(self.v.encode("utf-8"))

    def get_system_connection(self, system_type, uri: str, for_write: bool=False, **kwargs):
        class MyFS(object):
            def open(self, name):
                return io.BytesIO(b'from_fs')
        return MyFS()
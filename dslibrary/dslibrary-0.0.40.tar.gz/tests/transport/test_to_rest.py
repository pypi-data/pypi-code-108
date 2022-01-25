import unittest
import mock

from dslibrary.transport.to_rest import DSLibraryViaREST


class TestToRest(unittest.TestCase):

    def test_metadata_and_parameters(self):
        log = []
        class MyDSL(DSLibraryViaREST):
            def _do_comm(self, method: str, path: str, params: dict=None, data=None, as_json: bool=True):
                log.append((method, path, params))
                return {"metadata": {}, "parameters": {"x": 1}}
        dsl = MyDSL("URL")
        assert dsl.get_parameter("x") == 1

    # TODO resources
    # TODO sql

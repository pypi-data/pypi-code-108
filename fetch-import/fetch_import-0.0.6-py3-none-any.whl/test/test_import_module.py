from pprint import pprint
import unittest

from example import sets
from fetch_import import im_fetch, _im_fetch

_fetch_module = {}

url = "https://fastly.jsdelivr.net/gh/zmaplex/fetch_import@main/example/sets.py"


class TestImportMethods(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self._g = globals()
        super(TestImportMethods, self).__init__(*args, **kwargs)

    def _attribute_comparison(self, standard: dict, fetch: dict):
        standard_import_attr = {k: v for k, v in standard.items() if not k.startswith("_")}
        fetch_import_attr = {k: v for k, v in fetch.items() if not k.startswith("_")}

        for attr_name in standard_import_attr:
            self.assertIn(attr_name, fetch_import_attr)

    @im_fetch(url, _globals=_fetch_module)
    def test_import_module(self):
        self._attribute_comparison(sets.__dict__, _fetch_module["sets"].__dict__)

    def test__import_module(self):
        ___fetch_module = {}
        _im_fetch(url, _globals=___fetch_module)

        self._attribute_comparison(sets.__dict__, ___fetch_module["sets"].__dict__)

    def test__import_module_alisa(self):
        ___fetch_module = {}
        _im_fetch(url, _globals=___fetch_module, alias="remote_sets")
        self.assertIn("remote_sets", ___fetch_module)
        self._attribute_comparison(sets.__dict__, ___fetch_module["remote_sets"].__dict__)


if __name__ == '__main__':
    unittest.main()

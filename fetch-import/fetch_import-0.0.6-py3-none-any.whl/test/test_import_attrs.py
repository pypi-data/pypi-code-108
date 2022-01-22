from pprint import pprint
import unittest

from example.sets import AbstractClass, TypeClass, var_int
from fetch_import import im_fetch, _im_fetch

_fetch_module = {}

url = "https://fastly.jsdelivr.net/gh/zmaplex/fetch_import@main/example/sets.py"


class TestImportAllAttrs(unittest.TestCase):

    def _attribute_comparison(self, standard: dict, fetch: dict):
        standard_import_attr = {k: v for k, v in standard.items() if not k.startswith("_")}
        fetch_import_attr = {k: v for k, v in fetch.items() if not k.startswith("_")}

        for attr_name in fetch_import_attr:
            self.assertIn(attr_name, standard_import_attr)

    @im_fetch(url, ["AbstractClass", "TypeClass", "var_int"], _globals=_fetch_module, )
    def test_import_attrs(self):
        self._attribute_comparison(globals(), _fetch_module)

    def test__import_attrs(self):
        __fetch_module = {}
        _im_fetch(url, ["AbstractClass", "TypeClass", "var_int"], _globals=_fetch_module)
        self._attribute_comparison(globals(), __fetch_module)


if __name__ == '__main__':
    unittest.main()

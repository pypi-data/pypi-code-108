from pprint import pprint
import unittest

from fetch_import import _im_fetch

from example.sets import *
from fetch_import import im_fetch

_fetch_module = {}

url = "https://fastly.jsdelivr.net/gh/zmaplex/fetch_import@main/example/sets.py"


class TestImportAllAttrs(unittest.TestCase):

    def _attribute_comparison(self,standard:dict,fetch:dict):
        standard_import_attr = {k: v for k, v in standard.items() if not k.startswith("_")}
        fetch_import_attr = {k: v for k, v in fetch.items() if not k.startswith("_")}

        for attr_name in fetch_import_attr:
            self.assertIn(attr_name, standard_import_attr)

    @im_fetch(url, ["*"], _globals=_fetch_module, )
    def test_import_all_attrs(self):
        self._attribute_comparison(globals(),_fetch_module)

    def test__import_all_attrs(self):
        _tmp_dict = {}
        _im_fetch(url,["*"],_globals=_tmp_dict)
        self._attribute_comparison(globals(), _tmp_dict)

if __name__ == '__main__':
    unittest.main()

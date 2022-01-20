import os.path
import unittest2 as unittest

from yangsuite.paths import set_base_path
from ysyangtree import YSContext
from ysfilemanager import YSYangSet
from ysgnmi.yangtree import YSGnmiYangtree


class TestGnmiYangtree(unittest.TestCase):
    """Test cases for YSGnmiYangtree class."""

    basedir = os.path.join(os.path.dirname(__file__), 'data')

    @classmethod
    def setUpClass(cls):
        """Test setup method called before each test case."""
        set_base_path(cls.basedir)
        cls.maxDiff = None
        cls.ctx = YSContext(YSYangSet.load('test', 'test'),
                            None, ['openconfig-interfaces'])

    def test_construction(self):
        """Basic positive test."""
        yt = YSGnmiYangtree('openconfig-interfaces', '2016-05-26', self.ctx)
        self.assertEqual('openconfig-interfaces', yt.name)
        self.assertEqual(self.ctx, yt.ctx)

    def test_model_prefixes(self):
        """Make sure the model_prefixes attribute is populated correctly."""
        yt = YSGnmiYangtree('openconfig-interfaces', '2016-05-26', self.ctx)
        self.assertEqual({
            'ianaift': 'iana-if-type',
            'if': 'ietf-interfaces',
            'oc-eth': 'openconfig-if-ethernet',
            'oc-ext': 'openconfig-extensions',
            'oc-if': 'openconfig-interfaces',
            'oc-lag': 'openconfig-if-aggregate',
            'oc-vlan': 'openconfig-vlan',
            'oc-vlan-types': 'openconfig-vlan-types',
            'yang': 'ietf-yang-types',
        }, yt.model_prefixes)

    def test_identityrefs(self):
        """Ensure identityrefs are prefixed with module name, not prefix."""
        yt = YSGnmiYangtree('openconfig-interfaces', '2016-05-26', self.ctx)
        type_leaf = (yt.tree['children'][0]['children'][0]
                     ['children'][1]['children'][0])
        self.assertEqual('type', type_leaf['text'])
        self.assertIn('ianaift:ethernetCsmacd',  type_leaf['data']['options'])

# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Unit test cases for ysyangtree.ymodels."""

from __future__ import unicode_literals
import logging
import os.path
import unittest2 as unittest

import pyang

from .. import ymodels, YSYangModels, YSContext
from yangsuite.paths import set_base_path
from yangsuite.logs import get_logger
from ysfilemanager import YSYangSet, repository_path
from ysyangtree.ymodels import ALL_NODETYPES


class YModelTestBase(unittest.TestCase):

    basedir = os.path.join(os.path.dirname(__file__), 'data')

    @classmethod
    def setUpClass(cls):
        get_logger('ysyangtree').setLevel(logging.ERROR)
        get_logger('ysfilemanager').setLevel(logging.ERROR)
        set_base_path(cls.basedir)


class TestYSYangModels(YModelTestBase):
    """Test cases for the YSYangModels class."""

    def setUp(self):
        self.maxDiff = None
        self.ctx = YSContext(YSYangSet.load('test', 'testyangset'), None,
                             ['openconfig-interfaces'])

    def test_basics(self):
        """Basic functionality."""
        ym = YSYangModels(self.ctx, ['openconfig-interfaces',
                                     'openconfig-if-ethernet'])
        # Same nodeid iterator should be shared amongst each parser
        self.assertIs(ym.nodeid, ym.yangs['openconfig-interfaces'].nodeid)
        self.assertIs(ym.nodeid, ym.yangs['openconfig-if-ethernet'].nodeid)
        # Make sure tree contains data from both
        tree = ym.jstree
        self.assertEqual(2, len(tree['data']))
        self.assertEqual('openconfig-interfaces', tree['data'][0]['text'])
        self.assertEqual('openconfig-if-ethernet', tree['data'][1]['text'])
        self.assertNotEqual(tree['data'][0]['id'], tree['data'][1]['id'])
        self.assertEqual(sorted(ymodels.DEFAULT_INCLUDED_NODETYPES),
                         tree['included_nodetypes'])

    def test_missing_modules(self):
        """Error handling when requesting nonexistent modules."""
        ym = YSYangModels(self.ctx, ['openconfig-interfaces', 'foobar'])
        # Valid module should still be loaded, invalid module should be None
        self.assertEqual(['openconfig-interfaces', 'foobar'],
                         list(ym.yangs.keys()))
        self.assertEqual(None, ym.yangs['foobar'])
        # Tree should be an error node for the invalid module
        tree = ym.jstree
        self.assertEqual(2, len(tree['data']))
        self.assertEqual('openconfig-interfaces', tree['data'][0]['text'])
        self.assertGreater(len(tree['data'][0]['children']), 0)

        self.assertEqual('foobar', tree['data'][1]['text'])
        self.assertEqual('Module not found or loading failed',
                         tree['data'][1]['data']['error'])

    def test_store_get_forget_instance(self):
        """Test instance caching with [store|get|forget]_instance methods."""
        ym = YSYangModels(self.ctx, ['openconfig-interfaces',
                                     'openconfig-if-ethernet'])
        YSYangModels.store_instance(ym, "mykey")
        self.assertEqual(ym, YSYangModels.get_instance("mykey"))
        self.assertEqual(None, YSYangModels.get_instance("nosuchkey"))

        ym2 = YSYangModels(self.ctx, ['openconfig-interfaces'])
        self.assertNotEqual(ym, ym2)
        YSYangModels.store_instance(ym2, "mykey2")
        self.assertEqual(ym, YSYangModels.get_instance("mykey"))
        self.assertEqual(ym2, YSYangModels.get_instance("mykey2"))

        # Overwrite existing instance - bump up verbosity to inspect message
        get_logger('ysyangtree').setLevel(logging.INFO)
        YSYangModels.store_instance(ym2, "mykey")
        self.assertEqual(ym2, YSYangModels.get_instance("mykey"))
        self.assertEqual(ym2, YSYangModels.get_instance("mykey2"))
        get_logger('ysyangtree').setLevel(logging.ERROR)

        self.assertRaises(TypeError, YSYangModels.store_instance, 1, 'somekey')
        self.assertEqual(None, YSYangModels.get_instance('somekey'))

        YSYangModels.forget_instance("mykey")
        self.assertEqual(None, YSYangModels.get_instance("mykey"))
        self.assertEqual(ym2, YSYangModels.get_instance("mykey2"))
        YSYangModels.forget_instance("mykey2")

        # No-op
        YSYangModels.forget_instance("mykey")
        YSYangModels.forget_instance("nosuchkey")


class TestYSYangModelsImplicitLoading(YModelTestBase):
    """Test implicit loading of related modules."""

    def setUp(self):
        self.maxDiff = None

    NSP = {
        'eth': 'http://openconfig.net/yang/interfaces/ethernet',
        'ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type',
        'if': 'urn:ietf:params:xml:ns:yang:ietf-interfaces',
        'ift': 'urn:ietf:params:xml:ns:yang:iana-if-type',
        'ocif': 'http://openconfig.net/yang/interfaces',
        'yang': 'urn:ietf:params:xml:ns:yang:ietf-yang-types',
    }

    MODS = [
        ('iana-if-type', '2015-06-12'),
        ('ietf-interfaces', '2014-05-08'),
        ('ietf-yang-types', '2013-07-15'),
        ('openconfig-if-ethernet', '2015-11-20'),
        ('openconfig-interfaces', '2015-11-20'),
    ]

    # Regardless of what we initially load, if we request the base model
    # (openconfig-interfaces), we get the base model.

    def test_init_none_base(self):
        """Context init with no models, YM init with base model."""
        ctx = YSContext(YSYangSet.load('test', 'testyangset'), None, [])
        ym = YSYangModels(ctx, ['openconfig-interfaces'])
        self.assertEqual(['openconfig-interfaces'], sorted(ym.yangs.keys()))
        psy = ym.yangs['openconfig-interfaces']
        self.assertNotEqual(None, psy)
        self.assertEqual(self.NSP, psy.tree['data']['namespace_prefixes'])
        self.assertEqual(self.MODS, sorted(ctx.modules.keys()))

    def test_init_all_base(self):
        """Context init with all models, YM init with base model."""
        ctx = YSContext(YSYangSet.load('test', 'testyangset'), None)
        ym = YSYangModels(ctx, ['openconfig-interfaces'])
        self.assertEqual(['openconfig-interfaces'], sorted(ym.yangs.keys()))
        psy = ym.yangs['openconfig-interfaces']
        self.assertEqual(self.NSP, psy.tree['data']['namespace_prefixes'])
        # ctx.modules will have ALL modules in the yangset
        # self.assertEqual(self.MODS, sorted(ctx.modules.keys()))

    def test_init_base_base(self):
        """Context init with base model, YM init with base model."""
        ctx = YSContext(YSYangSet.load('test', 'testyangset'), None,
                        ['openconfig-interfaces'])
        ym = YSYangModels(ctx, ['openconfig-interfaces'])
        self.assertEqual(['openconfig-interfaces'], sorted(ym.yangs.keys()))
        psy = ym.yangs['openconfig-interfaces']
        self.assertEqual(self.NSP, psy.tree['data']['namespace_prefixes'])
        self.assertEqual(self.MODS, sorted(ctx.modules.keys()))

    def test_init_aug_base(self):
        """Context init with augmenter model, YM init with base model."""
        ctx = YSContext(YSYangSet.load('test', 'testyangset'), None,
                        ['openconfig-if-ethernet'])
        ym = YSYangModels(ctx, ['openconfig-interfaces'])
        self.assertEqual(['openconfig-interfaces'], sorted(ym.yangs.keys()))
        psy = ym.yangs['openconfig-interfaces']
        self.assertEqual(self.NSP, psy.tree['data']['namespace_prefixes'])
        self.assertEqual(self.MODS, sorted(ctx.modules.keys()))

    # Regardless of what we initially load, if we request the augmenting model
    # (openconfig-if-ethernet), we get it as well as the base model.

    def test_init_none_aug(self):
        """Context init with no models, YM init with augmenting model."""
        ctx = YSContext(YSYangSet.load('test', 'testyangset'), None, [])
        ym = YSYangModels(ctx, ['openconfig-if-ethernet'])
        self.assertEqual(['openconfig-if-ethernet', 'openconfig-interfaces'],
                         sorted(ym.yangs.keys()))
        psy = ym.yangs['openconfig-interfaces']
        self.assertNotEqual(None, psy)
        self.assertEqual(self.NSP, psy.tree['data']['namespace_prefixes'])
        self.assertEqual(self.MODS, sorted(ctx.modules.keys()))

    def test_init_all_aug(self):
        """Context init with all models, YM init with augmenting model."""
        ctx = YSContext(YSYangSet.load('test', 'testyangset'), None)
        ym = YSYangModels(ctx, ['openconfig-if-ethernet'])
        self.assertEqual(['openconfig-if-ethernet', 'openconfig-interfaces'],
                         sorted(ym.yangs.keys()))
        psy = ym.yangs['openconfig-interfaces']
        self.assertEqual(self.NSP, psy.tree['data']['namespace_prefixes'])
        # ctx.modules will be ALL modules in the yangset
        # self.assertEqual(self.MODS, sorted(ctx.modules.keys()))

    def test_init_base_aug(self):
        """Context init with base model, YM init with augmenting model."""
        ctx = YSContext(YSYangSet.load('test', 'testyangset'), None,
                        ['openconfig-interfaces'])
        ym = YSYangModels(ctx, ['openconfig-if-ethernet'])
        self.assertEqual(['openconfig-if-ethernet', 'openconfig-interfaces'],
                         sorted(ym.yangs.keys()))
        psy = ym.yangs['openconfig-interfaces']
        self.assertEqual(self.NSP, psy.tree['data']['namespace_prefixes'])
        self.assertEqual(self.MODS, sorted(ctx.modules.keys()))

    def test_init_aug_aug(self):
        """Context init with augmenting model, YM init with same."""
        ctx = YSContext(YSYangSet.load('test', 'testyangset'), None,
                        ['openconfig-if-ethernet'])
        ym = YSYangModels(ctx, ['openconfig-if-ethernet'])
        self.assertEqual(['openconfig-if-ethernet', 'openconfig-interfaces'],
                         sorted(ym.yangs.keys()))
        psy = ym.yangs['openconfig-interfaces']
        self.assertEqual(self.NSP, psy.tree['data']['namespace_prefixes'])
        self.assertEqual(self.MODS, sorted(ctx.modules.keys()))


class TestYSYangModelsDependencies(YModelTestBase):
    """Test the YSYangModels class with auto augmentation from dependencies."""
    def setUp(self):
        self.maxDiff = None
        self.ctx = YSContext(YSYangSet.load('test', 'dependencies'), None,
                             ['supermodule', 'sub-module',
                              'augmentation-target', 'sub-aug-target'])

    def test_auto_inclusion_submodule_default(self):
        """By default, supermodules and augmentation targets are included."""
        ym = YSYangModels(self.ctx, ['sub-module'])
        # requested module(s) are first, followed by others in sorted order
        self.assertEqual(
            ['sub-module',
             'augmentation-target', 'sub-aug-target', 'supermodule'],
            list(ym.yangs.keys()))
        self.assertEqual(
            ['sub-module',
             'augmentation-target', 'sub-aug-target', 'supermodule'],
            [node['text'] for node in ym.jstree['data']])

    def test_auto_inclusion_default(self):
        """Include augmentation targets of modules and their submodules."""
        ym = YSYangModels(self.ctx, ['supermodule'])
        # requested module(s) are first, followed by others in sorted order
        # submodule itself is not included
        self.assertEqual(
            ['supermodule',
             'augmentation-target', 'sub-aug-target'],
            list(ym.yangs.keys()))
        self.assertEqual(
            ['supermodule',
             'augmentation-target', 'sub-aug-target'],
            [node['text'] for node in ym.jstree['data']])
        self.assertEqual({
            'at': 'urn:augmentation-target',
            'sat': 'urn:sub-aug-target',
            'supermodule': 'urn:supermodule',
        }, ym.jstree['data'][0]['data']['namespace_prefixes'])

    def test_no_augment_inclusion(self):
        ym = YSYangModels(self.ctx, ['supermodule'], include_augmentees=False)
        self.assertEqual(['supermodule'], list(ym.yangs.keys()))
        self.assertEqual('supermodule', ym.jstree['data'][0]['text'])

    def test_no_augment_inclusion_submodule(self):
        ym = YSYangModels(self.ctx, ['sub-module'], include_augmentees=False)
        self.assertEqual(['sub-module', 'supermodule'], list(ym.yangs.keys()))
        self.assertEqual(['sub-module', 'supermodule'],
                         [node['text'] for node in ym.jstree['data']])

    def test_no_supermodule_inclusion_submodule(self):
        ym = YSYangModels(self.ctx, ['sub-module'], include_supermodules=False)
        self.assertEqual(
            ['sub-module', 'sub-aug-target'],
            list(ym.yangs.keys()))
        self.assertEqual(
            ['sub-module', 'sub-aug-target'],
            [node['text'] for node in ym.jstree['data']])

    def test_non_yangset_repository(self):
        """Dependencies can't be discovered if ctx.repo isn't a YangSet."""
        ctx = YSContext(
            pyang.FileRepository(path=repository_path('test', 'dependencies'),
                                 use_env=False),
            None,
            ['supermodule', 'sub-module',
             'augmentation-target', 'sub-aug-target'])
        self.assertRaises(ValueError, YSYangModels, ctx, ['supermodule'])

        # The below shouldn't raise an error, but it also may not work much
        YSYangModels(ctx, ['supermodule'],
                     include_augmentees=False, include_supermodules=False)


class TestParseYangOpenconfigInterfaces(YModelTestBase):
    """Test cases for the ParseYang class using YANG openconfig-interfaces."""

    def setUp(self):
        self.maxDiff = None
        self.ctx = YSContext(YSYangSet.load('test', 'testyangset'), None,
                             ['openconfig-interfaces'])
        # No revision specified - automatically find latest
        self.psy = ymodels.ParseYang('openconfig-interfaces', '', self.ctx)

    def test_instance_properties(self):
        """Test basic properties of a ParseYang instance."""
        # Validate the instance properties
        self.assertEqual('openconfig-interfaces', self.psy.name)
        self.assertEqual(self.ctx, self.psy.ctx)
        self.assertIsInstance(self.psy.module, pyang.statements.Statement)
        # self.assertEqual(count(2), self.psy.nodeid)
        self.assertEqual('ocif', self.psy.pfx)
        self.assertEqual('http://openconfig.net/yang/interfaces',
                         self.psy.namespace)
        self.assertEqual('2015-11-20', self.psy.revision)

    def test_tree(self):
        """Inspect contents of a ParseYang.tree."""
        root_node = self.psy.tree
        self.assertIsInstance(root_node, dict)
        self.assertEqual(1, root_node['id'])
        self.assertEqual('openconfig-interfaces', root_node['text'])

        root_data = root_node['data']
        self.assertEqual([
            'ietf-interfaces',
            'ietf-yang-types',
            'openconfig-extensions',
        ], sorted(root_data['imports']))
        expected = {
            'ocif': 'http://openconfig.net/yang/interfaces',
            'if': 'urn:ietf:params:xml:ns:yang:ietf-interfaces',
            'yang': 'urn:ietf:params:xml:ns:yang:ietf-yang-types',
            # Namespace for identity derivative
            'ianaift': 'urn:ietf:params:xml:ns:yang:iana-if-type',
            # Some modules use this prefix instead of ianaift:
            'ift': 'urn:ietf:params:xml:ns:yang:iana-if-type',
            # openconfig-extensions module is missing, so we don't know its ns
            # 'oc-ext': 'http://openconfig.net/yang/openconfig-ext',
        }
        if hasattr(self.psy.ctx.repository, 'modules_augmenting'):
            # Namespace for augmenting module in this yangset
            expected['eth'] = 'http://openconfig.net/yang/interfaces/ethernet'
        self.assertEqual(expected, root_data['namespace_prefixes'])
        self.assertEqual('module', root_data['modtype'])
        self.assertEqual('openconfig-interfaces', root_data['module'])
        self.assertEqual('http://openconfig.net/yang/interfaces',
                         root_data['namespace'])
        self.assertEqual(['edit-config', 'get', 'get-config'],
                         root_data['operations'])
        self.assertEqual('http://openconfig.net/yang/interfaces',
                         root_data['namespace'])
        self.assertEqual('ocif', root_data['prefix'])

        child_node = root_node['children'][0]
        self.assertEqual(2, child_node['id'])
        self.assertEqual('interfaces', child_node['text'])

        child_data = child_node['data']
        self.assertEqual('interfaces', child_data['name'])
        self.assertEqual('ocif', child_data.get('prefix'), child_data)
        self.assertEqual('openconfig-interfaces', child_data['module'])
        self.assertEqual('2015-11-20', child_data['revision'])
        self.assertEqual('/ocif:interfaces', child_data['xpath_pfx'])
        self.assertEqual('/interfaces', child_data['xpath'])
        self.assertEqual('/interfaces', child_data['schema_node_id'])
        self.assertEqual('read-write', child_data['access'])

        # Node interfaces/interface/name
        leaf_node = child_node['children'][0]['children'][0]
        self.assertEqual('name', leaf_node['text'])
        leaf_data = leaf_node['data']
        self.assertEqual('name', leaf_data['name'])
        self.assertEqual('leaf', leaf_data['nodetype'])
        self.assertEqual('leafref', leaf_data['datatype'])
        self.assertEqual('/ocif:interfaces/ocif:interface/ocif:name',
                         leaf_data['xpath_pfx'])
        self.assertEqual('/interfaces/interface/name', leaf_data['xpath'])
        self.assertEqual('/interfaces/interface/name',
                         leaf_data['schema_node_id'])
        self.assertEqual('read-write', leaf_data['access'])
        self.assertEqual('true', leaf_data['key'])

    def test_leaf_leafref(self):
        """Inspect a leafref leaf node of a ParseYang.tree."""
        leaf_node = self.psy.tw.get_node_by_xpath(
            "/interfaces/interface/subinterfaces/subinterface/" +
            "config/unnumbered")
        self.assertEqual('unnumbered', leaf_node['text'])
        leaf_data = leaf_node['data']
        self.assertEqual('unnumbered', leaf_data['name'])
        self.assertEqual('leaf', leaf_data['nodetype'])
        self.assertEqual('leafref', leaf_data['datatype'])
        self.assertEqual('../../index', leaf_data['leafref_path'])
        # Derived from the target leaf
        self.assertEqual('uint32', leaf_data['basetype'])
        self.assertEqual('0', leaf_data['min'])
        self.assertEqual('4294967295', leaf_data['max'])

    def test_leaf_boolean(self):
        """Inspect a boolean leaf node of a ParseYang.tree."""
        leaf_node = self.psy.tw.get_node_by_xpath(
            "/interfaces/interface/config/enabled")
        self.assertEqual('enabled', leaf_node['text'])
        leaf_data = leaf_node['data']
        self.assertEqual('enabled', leaf_data['name'])
        self.assertEqual('leaf', leaf_data['nodetype'])
        self.assertEqual('boolean', leaf_data['datatype'])
        self.assertEqual(['true', 'false'], leaf_data['options'])

    def test_leaf_identityref(self):
        """Inspect an identityref leaf node of a ParseYang.tree."""
        leaf_node = self.psy.tw.get_node_by_xpath(
            "/interfaces/interface/config/type")
        self.assertEqual('type', leaf_node['text'])
        leaf_data = leaf_node['data']
        self.assertEqual('type', leaf_data['name'])
        self.assertEqual('leaf', leaf_data['nodetype'])
        self.assertEqual('identityref', leaf_data['datatype'])

        self.assertEqual('if:interface-type', leaf_data['base'])
        # iana-if-type which has if:interface-type as a base
        # adds dozens of possible options to this identity.
        # Let's spot-check a few
        self.assertIn('ianaift:ethernetCsmacd', leaf_data['options'])
        self.assertIn('ianaift:gigabitEthernet', leaf_data['options'])
        self.assertEqual(len(leaf_data['options']), 276)

    def test_leaf_enumeration(self):
        """Inspect an enumeration leaf node of a ParseYang.tree."""
        leaf_node = self.psy.tw.get_node_by_xpath(
            "/interfaces/interface/state/admin-status")
        self.assertEqual('admin-status', leaf_node['text'])
        leaf_data = leaf_node['data']
        self.assertEqual('admin-status', leaf_data['name'])
        self.assertEqual('leaf', leaf_data['nodetype'])
        self.assertEqual('enumeration', leaf_data['datatype'])
        self.assertEqual(["UP", "DOWN", "TESTING"], leaf_data['options'])

        # Check legacy data for yangsuite-netconf
        leaf_typespec = leaf_data['typespec']
        self.assertEqual('enumeration', leaf_typespec['name'])
        self.assertEqual([("UP", 0), ("DOWN", 1), ("TESTING", 2)],
                         leaf_typespec['values'])

    def test_leaf_uint16(self):
        """Inspect a uint16 leaf node of a ParseYang.tree."""
        leaf_node = self.psy.tw.get_node_by_xpath(
            "/interfaces/interface/config/mtu")
        self.assertEqual('mtu', leaf_node['text'])
        leaf_data = leaf_node['data']
        self.assertEqual('mtu', leaf_data['name'])
        self.assertEqual('leaf', leaf_data['nodetype'])
        self.assertEqual('uint16', leaf_data['datatype'])
        self.assertEqual('0', leaf_data['min'])
        self.assertEqual('65535', leaf_data['max'])

        # Check legacy data for yangsuite-netconf
        leaf_typespec = leaf_data['typespec']
        self.assertEqual('uint16', leaf_typespec['name'])
        self.assertEqual('0', leaf_typespec['min'])
        self.assertEqual('65535', leaf_typespec['max'])

    def test_grouping_node(self):
        """Inspect a grouping node of a ParseYang.tree."""
        # By default, such nodes are not included in the tree
        grouping_node = next((child for child in self.psy.tree['children']
                              if child['text'] == "interface-common-config"),
                             None)
        self.assertIsNone(grouping_node)

        # Let's change that
        self.psy.included_nodetypes = ymodels.ALL_NODETYPES

        grouping_node = next((child for child in self.psy.tree['children']
                              if child['text'] == "interface-common-config"),
                             None)
        self.assertIsNotNone(grouping_node)
        self.assertEqual('grouping', grouping_node['data']['nodetype'])

    def test_typedef_node(self):
        """Inspect a typedef node of a ParseYang.tree."""
        # By default, such nodes are not included in the tree
        typedef_node = next((child for child in self.psy.tree['children']
                             if child['text'] == "interface-ref"),
                            None)
        self.assertIsNone(typedef_node)

        # Let's change that
        self.psy.included_nodetypes = ymodels.ALL_NODETYPES

        typedef_node = next((child for child in self.psy.tree['children']
                             if child['text'] == "interface-ref"),
                            None)
        self.assertIsNotNone(typedef_node)
        self.assertEqual('typedef', typedef_node['data']['nodetype'])
        self.assertEqual('leafref', typedef_node['data']['basetype'])


class TestParseYangDatatypesValidation(YModelTestBase):
    """Test cases for an artificial YANG model exercising various datatypes."""

    def setUp(self):
        self.maxDiff = None
        self.ctx = YSContext(YSYangSet.load('test', 'datatypes_validation'))
        self.psy = ymodels.ParseYang('datatypes_validation', '2018-02-19',
                                     self.ctx)

    def test_leaf_union(self):
        """Inspect a union leaf node."""
        leaf_node = self.psy.tw.get_node_by_xpath("/union")
        self.assertEqual('union', leaf_node['text'])
        leaf_data = leaf_node['data']
        self.assertEqual('union', leaf_data['name'])
        self.assertEqual('leaf', leaf_data['nodetype'])
        self.assertEqual('union', leaf_data['datatype'])
        self.assertEqual({
            'datatype': 'enumeration',
            'options': ['yes', 'no']
        }, leaf_data['members'].pop(0))
        self.assertEqual({
            'datatype': 'uint16',
            'min': '0',
            'max': '65535',
        }, leaf_data['members'].pop(0))
        self.assertEqual({
            'datatype': 'int8',
            'min': '-128',
            'max': '127',
        }, leaf_data['members'].pop(0))
        self.assertEqual({
            'datatype': 'enumeration',
            'options': ['alpha', 'beta']
        }, leaf_data['members'].pop(0))
        self.assertEqual({
            'datatype': 'bits',
            'bits': ['SYN', 'ACK']
        }, leaf_data['members'].pop(0))
        self.assertEqual({
            'datatype': 'string',
        }, leaf_data['members'].pop(0))
        self.assertEqual([], leaf_data['members'])


class TestParseYangOpenconfigIfEthernet(YModelTestBase):
    """Test cases for the ParseYang class using YANG openconfig-if-ethernet."""

    def setUp(self):
        self.maxDiff = None
        self.ctx = YSContext(YSYangSet.load('test', 'testyangset'))
        self.psy = ymodels.ParseYang('openconfig-if-ethernet', '2015-11-20',
                                     self.ctx)

    def test_instance_properties(self):
        """Test basic properties of a ParseYang instance."""
        # Validate the instance properties
        self.assertEqual('openconfig-if-ethernet', self.psy.name)
        self.assertEqual(self.ctx, self.psy.ctx)
        self.assertIsInstance(self.psy.module, pyang.statements.Statement)
        # self.assertEqual(count(2), self.psy.nodeid)
        self.assertEqual('eth', self.psy.pfx)
        self.assertEqual('http://openconfig.net/yang/interfaces/ethernet',
                         self.psy.namespace)
        self.assertEqual('2015-11-20', self.psy.revision)

    def test_identity_node(self):
        """Inspect an identity node in the ParseYang.tree."""
        # By default, such nodes are not included in the tree
        identity_node = next((child for
                              child in self.psy.tree.get('children', [])
                              if child['text'] == "ethernet-speed"),
                             None)
        self.assertIsNone(identity_node)

        # Let's change that
        self.psy.included_nodetypes = ymodels.ALL_NODETYPES

        identity_node = next((child for
                              child in self.psy.tree.get('children', [])
                              if child['text'] == "ethernet-speed"),
                             None)
        self.assertIsNotNone(identity_node)
        self.assertEqual('ethernet-speed', identity_node['text'])
        self.assertEqual('identity', identity_node['data']['nodetype'])
        # No base for this identity
        self.assertNotIn('base', identity_node['data'])

        identity_node = next((child for
                              child in self.psy.tree.get('children', [])
                              if child['text'] == "SPEED_100Mb"),
                             None)
        self.assertIsNotNone(identity_node)
        self.assertEqual('SPEED_100Mb', identity_node['text'])
        self.assertEqual('identity', identity_node['data']['nodetype'])
        # This identity is derived from the ethernet-speed identity
        self.assertEqual('ethernet-speed', identity_node['data']['base'])


class TestParseYangXENative(YModelTestBase):
    """Test cases for the ParseYang class using YANG XE-interfaces."""

    def setUp(self):
        self.maxDiff = None
        self.ctx = YSContext(YSYangSet.load('test', 'xe-16-10-1'), None,
                             ['Cisco-IOS-XE-native'])
        # No revision specified - automatically find latest
        self.psy = ymodels.ParseYang('Cisco-IOS-XE-native', '', self.ctx)

    def test_leafref_no_target(self):
        """Make sure a leafref with no i_target_node doesn't cause errors."""
        node = self.psy.tw.get_node_by_xpath(
            '/native/interface/GigabitEthernet/ip-vrf/ip/vrf/forwarding')
        self.assertEqual('leafref', node['data']['datatype'])
        # basetype is derived from the target node; no target -> no basetype
        self.assertNotIn('basetype', node['data'])


class TestParseYangUTF8(YModelTestBase):
    """Test parsing a yang file that contains utf-8 characters"""

    def setUp(self):
        self.ctx = YSContext(YSYangSet.load('test', 'testyangset'))
        self.psy = ymodels.ParseYang('utf8module', '', self.ctx)

    def test_instance_properties(self):
        """Test basic properties of a ParseYang instance."""
        # Validate the instance properties
        self.assertEqual('utf8module', self.psy.name)
        self.assertEqual(self.ctx, self.psy.ctx)
        self.assertIsInstance(self.psy.module, pyang.statements.Statement)
        self.assertEqual('utf8module', self.psy.pfx)
        self.assertEqual("urn:test:utf8module", self.psy.namespace)


class TestParseYangRPC(YModelTestBase):
    """Test parsing of a YANG file with RPCs."""

    def setUp(self):
        self.ctx = YSContext(YSYangSet.load('test', 'monitoring'))
        self.psy = ymodels.ParseYang('ietf-netconf-monitoring', '2010-10-04',
                                     self.ctx)

    def test_tree(self):
        """Inspect data nodes."""
        root_node = self.psy.tree
        # Input and output are part of rpc, so are not reported separately
        # at the module-level 'operations' data.
        self.assertEqual(['get', 'rpc'], root_node['data']['operations'])

        rpc_node = root_node['children'][1]
        self.assertEqual('get-schema', rpc_node['text'])

        input_node = rpc_node['children'][0]
        self.assertEqual('input', input_node['text'])
        input_data = input_node['data']
        self.assertEqual('write', input_data['access'])
        self.assertEqual(('input',), input_data['operations'])
        # Input nodes are in the schema path but not the data path
        self.assertEqual('/get-schema', input_data['xpath'])
        self.assertEqual('/ncm:get-schema', input_data['xpath_pfx'])
        self.assertEqual('/get-schema/input', input_data['schema_node_id'])

        identifier_node = input_node['children'][0]
        self.assertEqual('identifier', identifier_node['text'])
        identifier_data = identifier_node['data']
        self.assertEqual('write', identifier_data['access'])
        self.assertEqual(('input',), identifier_data['operations'])
        self.assertEqual('/get-schema/identifier', identifier_data['xpath'])
        self.assertEqual('/ncm:get-schema/ncm:identifier',
                         identifier_data['xpath_pfx'])
        self.assertEqual('/get-schema/input/identifier',
                         identifier_data['schema_node_id'])

        output_node = rpc_node['children'][1]
        self.assertEqual('output', output_node['text'])
        output_data = output_node['data']
        self.assertEqual('read-only', output_data['access'])
        self.assertEqual(('output',), output_data['operations'])
        # Output nodes are in the schema path but not the data path
        self.assertEqual('/get-schema', output_data['xpath'])
        self.assertEqual('/ncm:get-schema', output_data['xpath_pfx'])
        self.assertEqual('/get-schema/output', output_data['schema_node_id'])

        data_node = output_node['children'][0]
        self.assertEqual('data', data_node['text'])
        data_data = data_node['data']    # I heard you like data, so...
        self.assertEqual('read-only', data_data['access'])
        self.assertEqual(('output',), data_data['operations'])
        self.assertEqual('/get-schema/data', data_data['xpath'])
        self.assertEqual('/ncm:get-schema/ncm:data', data_data['xpath_pfx'])
        self.assertEqual('/get-schema/output/data',
                         data_data['schema_node_id'])


class TestParseYangMalformed(YModelTestBase):
    """Test parsing of a yang file that's malformed but still parsable."""

    def setUp(self):
        self.ctx = YSContext(YSYangSet.load('badfiles', 'badfiles'))
        self.psy = ymodels.ParseYang('no-namespaces', '', self.ctx)

    def test_instance_properties(self):
        """Test basic instance properties."""
        self.assertEqual('no-namespaces', self.psy.name)
        self.assertEqual(self.ctx, self.psy.ctx)
        self.assertEqual('', self.psy.pfx)
        self.assertEqual('', self.psy.namespace)

    def test_tree(self):
        """Test constructed node data."""
        root_node = self.psy.tree
        self.assertIsInstance(root_node, dict)
        self.assertEqual('no-namespaces', root_node['text'])

        root_data = root_node['data']
        self.assertEqual(['ietf-yang-types'],
                         sorted(root_data['imports']))
        self.assertEqual({
            'fw': 'urn:ietf:params:xml:ns:yang:ietf-yang-types',
        }, root_data['namespace_prefixes'])
        self.assertEqual('module', root_data['modtype'])
        self.assertEqual('no-namespaces', root_data['module'])
        self.assertEqual('', root_data['namespace'])
        self.assertEqual([], root_data['operations'])
        self.assertEqual('', root_data['prefix'])

    def test_list_keys(self):
        """Test special case logic enforcing list key order."""
        psy = ymodels.ParseYang('key-order', '2001-01-01', self.ctx)
        root_node = psy.tree
        list_node = root_node['children'][0]
        self.assertEqual(['first-key', 'second-key', 'third-key'],
                         list_node['data']['keys'])
        # Regardless of order in the yang file, we ensure that the
        # list key nodes are ordered and first in the list of children.
        # Ordering of all non-key nodes is preserved as in the yang file.
        self.assertEqual(
            ['first-key', 'second-key', 'third-key',
             'non-key', 'another-non-key', 'yet-another-non-key'],
            [node['text'] for node in list_node['children']])


class TestParseYangNamespaces(YModelTestBase):
    """Test parsing some more complex YANG models including namespaces."""

    def setUp(self):
        self.maxDiff = None
        self.ctx = YSContext(YSYangSet.load('test', 'namespaces'))
        self.ctx.load_module_files(['openconfig-interfaces',
                                    'openconfig-vlan'])
        self.py_ocif = ymodels.ParseYang('openconfig-interfaces', '', self.ctx)
        self.py_vlan = ymodels.ParseYang('openconfig-vlan', '', self.ctx)

    def test_choice_case(self):
        """Inspect some choice and case nodes for correctness."""
        node = self.py_ocif.tw.get_node_by_xpath(
            "/interfaces/interface/subinterfaces/subinterface/" +
            "vlan:vlan/vlan:config")
        # This node has child 'choice local-global' with children
        # 'case global' and 'case local'
        choice_node = node['children'][0]
        case_global_node = choice_node['children'][0]
        # case global has a leaf child of type vlan-ref
        vlan_ref_node = case_global_node['children'][0]

        self.assertEqual(choice_node['data']['operations'], ())
        self.assertEqual(case_global_node['data']['operations'], ())
        self.assertEqual(vlan_ref_node['data']['operations'],
                         ('edit-config', 'get-config', 'get'))

        self.assertEqual(choice_node['data']['nodetype'], 'choice')
        self.assertEqual(case_global_node['data']['nodetype'], 'case')
        self.assertEqual(vlan_ref_node['data']['nodetype'], 'leaf')
        self.assertEqual(vlan_ref_node['data']['datatype'], 'vlan-ref')
        self.assertEqual(vlan_ref_node['data']['basetype'], 'union')

        self.assertEqual(['global', 'local'], choice_node['data']['options'])

        # The xpath and xpath_pfx are data node paths and so don't include the
        # case/choice nodes in the schema tree
        self.assertEqual('/interfaces/interface/subinterfaces/subinterface/'
                         'vlan:vlan/vlan:config',
                         choice_node['data']['xpath'])
        self.assertEqual('/interfaces/interface/subinterfaces/subinterface/'
                         'vlan:vlan/vlan:config',
                         case_global_node['data']['xpath'])
        self.assertEqual('/interfaces/interface/subinterfaces/subinterface/'
                         'vlan:vlan/vlan:config/vlan:global-vlan-id',
                         vlan_ref_node['data']['xpath'])

        self.assertEqual('/ocif:interfaces/ocif:interface/ocif:subinterfaces/'
                         'ocif:subinterface/vlan:vlan/vlan:config',
                         choice_node['data']['xpath_pfx'])
        self.assertEqual('/ocif:interfaces/ocif:interface/ocif:subinterfaces/'
                         'ocif:subinterface/vlan:vlan/vlan:config',
                         case_global_node['data']['xpath_pfx'])
        self.assertEqual('/ocif:interfaces/ocif:interface/ocif:subinterfaces/'
                         'ocif:subinterface/vlan:vlan/vlan:config/'
                         'vlan:global-vlan-id',
                         vlan_ref_node['data']['xpath_pfx'])

        # The schema_node_id *does* include these nodes.
        self.assertEqual('/interfaces/interface/subinterfaces/subinterface/'
                         'vlan:vlan/vlan:config/vlan:local-global',
                         choice_node['data']['schema_node_id'])
        self.assertEqual('/interfaces/interface/subinterfaces/subinterface/'
                         'vlan:vlan/vlan:config/vlan:local-global/vlan:global',
                         case_global_node['data']['schema_node_id'])
        self.assertEqual('/interfaces/interface/subinterfaces/subinterface/'
                         'vlan:vlan/vlan:config/vlan:local-global/vlan:global/'
                         'vlan:global-vlan-id',
                         vlan_ref_node['data']['schema_node_id'])

    def test_choice_case_augment(self):
        """Verify that cases added via augmentation are recognized."""
        ctx = YSContext(YSYangSet.load('test', 'ietf-event-notifications'))
        psy = ymodels.ParseYang('ietf-event-notifications', '', ctx)
        list_node = psy.tw.get_node_by_xpath(
            '/subscription-config/subscription')
        choice_node = list_node['children'][3]
        self.assertEqual('filter-type', choice_node['text'])
        self.assertEqual(['rfc5277', 'by-reference', 'yp:update-filter'],
                         choice_node['data']['options'])

    def test_key_non_key(self):
        """Inspect sibling nodes, one of which is a key and the other isn't."""
        key_node = self.py_vlan.tw.get_node_by_xpath(
            "/vlans/vlan/vlan-id")
        non_key_node = self.py_vlan.tw.get_node_by_xpath(
            "/vlans/vlan/config")

        self.assertTrue(key_node['data']['key'])
        self.assertFalse(non_key_node['data'].get('key', False))


class TestTreeWalker(YModelTestBase):
    """Test cases for the TreeWalker class."""

    def setUp(self):
        self.maxDiff = None
        self.ctx = YSContext(YSYangSet.load('test', 'testyangset'), None,
                             ['openconfig-interfaces'])
        # No revision specified - automatically find latest
        self.psy = ymodels.ParseYang('openconfig-interfaces', '', self.ctx)
        self.tw = self.psy.tw

    def test_get_node_by_xpath_without_prefix_1(self):
        """Get a node by its xpath when no_prefix=True. Prefixes in input xpath
        are ignored."""
        longpath = '/ocif:interfaces/ocif:interface/ocif:state/ocif:counters' \
                   '/abc:out-unicast-pkts'
        node = self.tw.get_node_by_xpath(longpath, no_prefix=True)
        self.assertNotEqual(node, None)

    def test_get_node_by_xpath_without_prefix_2(self):
        """Get a node by its xpath when no_prefix=True."""
        longpath = '/interfaces/interface/state/counters/out-unicast-pkts'
        node = self.tw.get_node_by_xpath(longpath, no_prefix=True)
        self.assertNotEqual(node, None)

    def test_get_node_by_xpath_with_prefix(self):
        """Get a node by its xpath when no_prefix=False."""
        longpath = '/interfaces/interface/state/counters/out-unicast-pkts'
        node = self.tw.get_node_by_xpath(longpath, no_prefix=False)
        self.assertNotEqual(node, None)

    def test_get_node_by_xpath_negative(self):
        parents = []
        node = self.tw.get_node_by_xpath("/foo/bar", parents=parents)
        self.assertEqual(None, node)
        self.assertEqual([], parents)

    def test_get_node_by_id_negative(self):
        parents = []
        node = self.tw.get_node_by_id("10000", parents)
        self.assertEqual(None, node)
        self.assertEqual([], parents)

    def test_get_dataset_list(self):
        """Get a dataset of xpath, nodetype, and 'datatype'."""
        dataset = self.tw.get_dataset(
            self.tw.tree, [], 'nodetype', 'datatype')
        # should be 100 records.
        self.assertEqual(len(dataset), 100)
        # Check the first record and the last record
        longpath = '/interfaces/interface/eth:ethernet/eth:state/eth:counters/\
eth:out-8021q-frames'
        self.assertEqual(dataset[0], ['/interfaces', 'container', ''])
        self.assertEqual(dataset[99], [longpath, 'leaf', 'yang:counter64'])

    def test_get_dataset_set(self):
        """Get a dataset of xpath, nodetype, and 'datatype'."""
        dataset = self.tw.get_dataset(
            self.tw.tree, set(), 'nodetype', 'datatype')
        dataset2 = self.tw.get_dataset(
            self.tw.tree, set(), 'nodetype', 'datatype')
        # should be 100 records.
        self.assertEqual(len(dataset), 100)
        self.assertEqual(len(dataset2), 100)
        self.assertEqual(dataset, dataset2)


class TestNestedModels(YModelTestBase):
    """Test cases for multiple level importing class."""

    def setUp(self):
        self.maxDiff = None
        self.ctx = YSContext(YSYangSet.load('test', 'testnesting'), None,
                             ['test-deep-nesting',
                              'test-nesting2',
                              'test-nesting3',
                              'test-nesting4'])

    def test_nested_prefix(self):
        """Prefix nested 3 levels down in test-deep-nesting.yang."""
        ym = YSYangModels(self.ctx, ['test-deep-nesting'])
        parseyang = ym.yangs['test-deep-nesting']
        self.assertIn('test-nst4',
                      parseyang.tree['data']['namespace_prefixes'])


class TestDatasetKey(YModelTestBase):
    """Test cases for building dataset for submodule."""

    def setUp(self):
        self.maxDiff = None
        self.ctx = YSContext(YSYangSet.load('test', 'xe-16-10-1'), None,
                             ['Cisco-IOS-XE-interfaces'])
        ym = YSYangModels(self.ctx, ['Cisco-IOS-XE-interfaces'],
                          included_nodetypes=ALL_NODETYPES)
        self.tw = None
        for m, parser in ym.yangs.items():
            if m == 'Cisco-IOS-XE-interfaces':
                self.tw = parser.tw

    def test_get_dataset_key(self):
        """Get a dataset of xpath, status, module, and nodetype."""
        dataset = self.tw.get_dataset_using_key(
            self.tw.tree, 'name', [], '/', 'status', 'module', 'nodetype')
        self.assertEqual(dataset[0][-1], 'submodule')

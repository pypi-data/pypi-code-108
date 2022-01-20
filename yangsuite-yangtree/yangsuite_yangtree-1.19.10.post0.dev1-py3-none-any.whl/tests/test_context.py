# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Test cases for ysyangtree.context module and YSContext class."""

import logging
import os
import time
import unittest2 as unittest

import pyang
import os.path
import shutil
import tempfile

from .. import context, ymodels
from ..context import YSContext
from yangsuite.paths import get_path, set_base_path
from yangsuite.logs import get_logger
from ysfilemanager import (
    YSYangSet, YSMutableYangSet, merge_user_set, yangset_path,
)


class TestYSContextModule(unittest.TestCase):
    """Test the ysyangtree.context module."""

    basedir = os.path.join(os.path.dirname(__file__), 'data')

    @classmethod
    def setUpClass(cls):
        """Quiet down the loggers and hide messages INFO and WARNING."""
        get_logger('ysyangtree').setLevel(logging.ERROR)
        get_logger('ysfilemanager').setLevel(logging.ERROR)
        set_base_path(cls.basedir)
        cls.ys = YSYangSet.load('test', 'testyangset')

    def setUp(self):
        """Setup function called before each test case."""
        set_base_path(self.basedir)
        self.maxDiff = None

    def tearDown(self):
        """Make sure cache is empty after each test."""
        self.assertEqual({}, YSContext._instances, 'Cache not emptied')

    def test_get_reset_parse_yang(self):
        """Test [get|reset]_parse_yang APIs."""
        self.assertEqual(None, context.get_parse_yang('mykey'))

        ctx = YSContext(self.ys, None, ['openconfig-if-ethernet'])
        parser = ctx.get_yang_parser('openconfig-if-ethernet')

        context.reset_parse_yang(parser, 'mykey')
        self.assertIs(parser, context.get_parse_yang('mykey'))

        self.assertRaises(TypeError, context.reset_parse_yang, None, 'akey')

    def test_get_reset_result_stream(self):
        """Test [get|reset]_result_stream APIs."""
        stream1 = context.get_result_stream('mykey')
        stream1.append("Hello\n")
        self.assertEqual("Hello\n", stream1.popleft())

        stream2 = context.get_result_stream('mykey')
        self.assertIs(stream1, stream2)
        stream2.append("Hello\n")
        stream2.append("Goodbye\n")
        self.assertEqual("Hello\n", stream2.popleft())
        self.assertEqual("Goodbye\n", stream2.popleft())

        context.reset_result_stream('nosuchkey')
        stream3 = context.get_result_stream('mykey')
        stream1.append("Hello\n")
        self.assertIs(stream1, stream3)
        self.assertEqual("Hello\n", stream3.popleft())

        context.reset_result_stream('mykey')
        stream4 = context.get_result_stream('mykey')
        self.assertIsNot(stream1, stream4)
        self.assertEqual(0, len(stream4))

    def test_set_result_stream(self):
        """Test general object setting for result stream."""
        class MyLog(object):
            def __init__(self, myq=[]):
                self.q = myq

            def append(self, msg):
                self.q.append(msg)

            def popleft(self):
                msg = self.q[0]
                self.q = self.q[1:]
                return msg

            def __len__(self):
                return len(self.q)

        mylog = MyLog()
        context.set_result_stream('test', mylog)
        slog = context.get_result_stream('test')
        slog.append('one')
        slog.append('two')
        slog.append('three')
        while(len(slog)):
            one = slog.popleft()
            two = slog.popleft()
            three = slog.popleft()

        self.assertEqual(one, 'one')
        self.assertEqual(two, 'two')
        self.assertEqual(three, 'three')

    def test_context_creation_no_key(self):
        """Call YSContext() constructor without specifying a key."""
        # TODO - capture and check print/log output.

        # Path must exist and be a directory, JSON file, or YSYangSet
        self.assertRaises(ValueError, YSContext, __file__)
        self.assertRaises(ValueError, YSContext, None)

        ctx = YSContext(self.ys, None, ['ietf-inet-types', 'iana-if-type',
                                        'Cisco-IOS-XR-lib-keychain-act'])
        self.assertIsInstance(ctx, YSContext)
        self.assertIsInstance(ctx, pyang.Context)

        self.assertIsNotNone(ctx.get_module('ietf-inet-types'))
        self.assertIn('ietf-inet-types', ctx.revs)
        self.assertIn(('ietf-inet-types', '2013-07-15'), ctx.modules)
        # We get a LOT of identities from iana-if-type/iana-interface-type
        # and its base is ietf-interfaces/interface-type so we should have
        # the same identities wherever the base is used.
        self.assertIn('ietf-interfaces', ctx.identities)
        self.assertIn('interface-type', ctx.identities['ietf-interfaces'])
        # Do a quick spot check on one of the 200+ idnetities
        self.assertIn('ianaift:hyperchannel',
                      ctx.identities['ietf-interfaces']['interface-type'])

        # Cisco-IOS-XR-lib-keychain-act fails parsing, so should be absent:
        self.assertIsNone(ctx.get_module('Cisco-IOS-XR-lib-keychain-act'))
        # pyang.Context.revs includes entries for files that failed parsing
        # self.assertNotIn('Cisco-IOS-XR-lib-keychain-act', ctx.revs)
        self.assertNotIn(('Cisco-IOS-XR-lib-keychain-act', '2017-04-17'),
                         ctx.modules)

        # Since we specified a list of modules, we should have loaded these
        # modules and their dependencies, but not unrelated modules in the set.
        self.assertGreater(len(ctx.modules),
                           len(['ietf-inet-types', 'iana-if-type',
                                'Cisco-IOS-XR-lib-keychain-act']))
        self.assertLess(len(ctx.modules), len(self.ys.modules))

    def test_ctx_caching(self):
        """Call YSContext() with a key and check caching."""
        ctx = YSContext(self.ys, 'mykey', [])

        self.assertIsInstance(ctx, YSContext)
        self.assertEqual(True, ctx.ready)
        # Since we requested no modules, none should have been auto-loaded
        self.assertEqual(0, len(ctx.modules))

        ctx2 = YSContext.get_private_instance('mykey')
        self.assertIs(ctx2, ctx)

        YSContext.discard_instance('mykey')
        self.assertIsNone(YSContext.get_private_instance('mykey'))

        # No-op
        YSContext.discard_instance('mykey')

    def test_ctx_caching_multiple(self):
        """Test coexistence of multiple contexts."""
        ctx1 = YSContext(self.ys, 'myref', [])
        ctx2 = YSContext(self.ys, 'myref2', [])

        self.assertIsNot(ctx1, ctx2)

        self.assertIs(ctx1, YSContext.get_private_instance('myref'))

        YSContext.discard_instance('myref')
        self.assertIsNone(YSContext.get_private_instance('myref'))
        self.assertIs(ctx2, YSContext.get_private_instance('myref2'))

        YSContext.discard_instance('myref2')
        self.assertIsNone(YSContext.get_private_instance('myref2'))

    def test_ctx_caching_shared(self):
        """Test multiple references to one context."""
        ys_as_key = merge_user_set(self.ys.owner, self.ys.setname)

        ctx1 = YSContext.get_instance('ref1', ys_as_key)
        ctx2 = YSContext.get_instance('ref2', ys_as_key)
        ctx3 = YSContext.get_instance('ref3', ys_as_key)

        # now one instance is cached with 3 references

        self.assertIs(ctx1, ctx2)
        self.assertIs(ctx1, ctx3)

        ctx = YSContext.get_instance('ref1', ys_as_key)
        self.assertTrue('ref2' in ctx.reference)
        self.assertTrue('ref1' in ctx.reference)
        self.assertTrue('ref3' in ctx.reference)

        YSContext.discard_instance(ys_as_key, 'ref2')
        ctx = YSContext.get_instance('ref1', ys_as_key)
        self.assertNotIn('ref2', ctx.reference)
        self.assertEqual({'ref1', 'ref3'}, ctx.reference)

        YSContext.discard_instance(ys_as_key, 'ref1')
        YSContext.discard_instance(ys_as_key, 'ref3')

    def test_opaque_object_as_ref(self):
        """Test random object used as reference."""
        ys_as_key = merge_user_set(self.ys.owner, self.ys.setname)

        class RefObj(object):
            def __init__(self, tag):
                self.tag = tag

        ref = RefObj("Ref tag")
        self.assertEqual("Ref tag", ref.tag)

        ctx = YSContext.get_instance(ref, ys_as_key)
        self.assertIsInstance(ctx, YSContext)
        ctx2 = YSContext.get_instance(ref, ys_as_key)

        self.assertIs(ctx, ctx2)
        self.assertIn(ref, ctx2.reference)

        YSContext.discard_instance(ys_as_key, ref)
        YSContext.discard_instance(ys_as_key, ref)

    def test_ctx_caching_shared_and_private(self):
        """Test coexistence of shared and private contexts."""
        ys_as_key = merge_user_set(self.ys.owner, self.ys.setname)

        ctx1 = YSContext.get_instance('ref1', ys_as_key)
        ctx2 = YSContext.get_private_instance('private')
        ctx3 = YSContext.get_instance('ref3', ys_as_key)
        # now one instance with 2 references and one private

        self.assertIsNot(ctx1, ctx2)
        self.assertIs(ctx1, ctx3)

        ctx = YSContext.get_instance('ref1', ys_as_key)
        self.assertTrue('ref1' in ctx.reference)
        self.assertTrue('ref3' in ctx.reference)
        self.assertTrue('private' not in ctx.reference)

        ctx = YSContext.get_private_instance('private')
        self.assertIs(ctx, ctx2)

        YSContext.discard_instance('private')
        self.assertIsNone(YSContext.get_private_instance('private'))

        ctx = YSContext.get_instance('ref1', ys_as_key)
        self.assertTrue('ref1' in ctx.reference)
        self.assertTrue('ref3' in ctx.reference)

        YSContext.discard_instance(ys_as_key, 'ref1')
        ctx = YSContext.get_instance('ref3', ys_as_key)
        self.assertNotIn('ref1', ctx.reference)
        self.assertIn('ref3', ctx.reference)

        YSContext.discard_instance(ys_as_key, 'ref3')

    def test_get_ready_instance(self):
        """Make sure ready is set."""
        ys_as_key = merge_user_set(self.ys.owner, self.ys.setname)

        to = 3
        while True:
            ctx = YSContext.get_instance('ref1', ys_as_key)
            self.assertIsInstance(ctx, YSContext)
            if ctx.ready:
                break
            time.sleep(5)
            to -= 1
            if to <= 0:
                break

        self.assertFalse(to == 0)
        self.assertTrue(ctx.ready)
        YSContext.discard_instance(ys_as_key, 'ref1')

    def test_get_instance_refresh(self):
        """Test get_instance() loading from cache with and without yangset."""
        ctx = YSContext(self.ys, 'cacheme', [])

        # No yangset - just get cached
        ctx2 = YSContext.get_private_instance('cacheme')
        self.assertIs(ctx, ctx2)

        # Same yangset - get cached
        ctx2 = YSContext.get_private_instance(
            'cacheme',
            merge_user_set(self.ys.owner, self.ys.setname))

        self.assertIs(ctx, ctx2)

        # Different yangset - reset cached
        ctx2 = YSContext.get_private_instance('cacheme', 'multiversion:a')
        self.assertIsNot(ctx, ctx2)

        # Discard cache
        YSContext.discard_instance('cacheme')
        ctx = None
        ctx2 = None

        # No yangset - return cached, even if none
        ctx = YSContext.get_private_instance('cacheme')
        self.assertIsNone(ctx)

        # Yangset - create and cache
        ctx = YSContext.get_private_instance('cacheme',
                                             merge_user_set(self.ys.owner,
                                                            self.ys.setname))
        self.assertIsNotNone(ctx)
        self.assertEqual(self.ys, ctx.repository)

        temp_path = tempfile.mkdtemp()
        try:
            shutil.rmtree(temp_path)
            shutil.copytree(self.basedir, temp_path)
            set_base_path(temp_path)

            # Yangset module set is changed - reset cache
            mys = YSMutableYangSet.load(self.ys.owner, self.ys.setname)
            mys.modules = mys.modules[1:]
            mys.write()

            ctx2 = YSContext.get_private_instance(
                'cacheme',
                merge_user_set(self.ys.owner, self.ys.setname))
            self.assertIsNot(ctx, ctx2)

            # Modules don't change, but data is otherwise stale - reset cache
            # This is the equivalent to 'touch yangset_path' in Python, btw.
            os.utime(yangset_path(self.ys.owner, self.ys.setname), None)

            ctx3 = YSContext.get_private_instance(
                'cacheme',
                merge_user_set(self.ys.owner, self.ys.setname))
            self.assertIsNot(ctx2, ctx3)
        finally:
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
            set_base_path(self.basedir)

            YSContext.discard_instance('cacheme')

    def test_get_yang_parser_positive(self):
        """Positive test of get_yang_parser()."""
        ctx = YSContext(self.ys, None, ['openconfig-if-ethernet'])

        parser = ctx.get_yang_parser('openconfig-if-ethernet')
        self.assertIsInstance(parser, ymodels.ParseYang)
        # ParseYang class will be tested in test_ymodels.py

        # make sure cache is empty
        self.assertEqual({}, YSContext._instances)

    def test_get_yang_parser_negative(self):
        """Negative test of get_yang_parser()."""
        ctx = YSContext(self.ys, None, ['openconfig-if-ethernet',
                                        'Cisco-IOS-XR-lib-keychain-act'])

        self.assertRaises(ValueError, ctx.get_yang_parser, None)
        self.assertRaises(ValueError, ctx.get_yang_parser, None, None)
        self.assertRaises(ValueError, ctx.get_yang_parser,
                          'openconfig-if-ethernet', '1999-12-31')
        self.assertRaises(ValueError, ctx.get_yang_parser, 'foo')

        # in the yangset, but not among those loaded thus far
        # TODO: should we auto-load this module on request thus?
        self.assertRaises(ValueError, ctx.get_yang_parser,
                          'Cisco-IOS-XR-ipv4-bgp-oc-oper')
        # requested to load, but it failed parsing
        self.assertRaises(RuntimeError, ctx.get_yang_parser,
                          'Cisco-IOS-XR-lib-keychain-act')

    def test_validate_positive(self):
        """Positive test for validate()."""
        result = YSContext(self.ys).validate()
        # Note that the reported results are expected to be alphabetical
        # by module name and then by revision.

        utfmodule_yang_path = os.path.join('...', 'users', 'test',
                                           'repositories', 'testrepo',
                                           'utf8module@unknown.yang')
        self.assertEqual([
            {'name': 'Cisco-IOS-XR-ipv4-bgp-datatypes',
             'revision': '2015-08-27',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': None},
            # Example of a module that loads but reports several warnings.
            # We want *all* of the warnings, not just the latest one
            {'name': 'Cisco-IOS-XR-ipv4-bgp-oc-oper',
             'revision': '2015-11-09',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': [
                 'WARNING line 14: imported module Cisco-IOS-XR-types '
                 'not used',
                 'WARNING line 16: imported module '
                 'Cisco-IOS-XR-ipv4-bgp-datatypes not used']},
            {'name': 'Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1',
             'revision': '2015-11-09',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': [
                 'WARNING line 13: imported module Cisco-IOS-XR-types '
                 'not used',
             ]},
            # Example of a module that cannot be loaded at all.
            # We expect usable == False in this case.
            {'name': 'Cisco-IOS-XR-lib-keychain-act',
             'revision': '2017-04-17',
             'found': True,
             'usable': False,
             'errors': [
                 'CRITICAL ERROR line 40: unterminated statement definition '
                 'for keyword "description", looking at t'],
             'warnings': None},
            {'name': 'Cisco-IOS-XR-types',
             'revision': '2015-06-29',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': None},
            {'name': 'iana-if-type',
             'revision': '2015-06-12',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': None},
            {'name': 'ietf-inet-types',
             'revision': '2013-07-15',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': None},
            {'name': 'ietf-interfaces',
             'revision': '2014-05-08',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': None},
            {'name': 'ietf-yang-types',
             'revision': '2013-07-15',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': None},
            # Missing dependency
            {'name': 'openconfig-extensions',
             'revision': 'unknown',
             'found': False,
             'usable': False,
             'errors': None,
             'warnings': None},
            {'name': 'openconfig-if-ethernet',
             'revision': '2015-11-20',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': None},
            # Example of a module that is successfully loaded but reports
            # errors - note that it is still 'usable'.
            {'name': 'openconfig-interfaces',
             'revision': '2015-11-20',
             'found': True,
             'usable': True,
             'errors': [
                 'CRITICAL ERROR line 13: module "openconfig-extensions" not '
                 'found in search path'],
             'warnings': None},
            {'name': 'utf8module',
             'revision': 'unknown',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': [
                 'WARNING line 1: filename "' + utfmodule_yang_path +
                 '" suggests invalid revision "unknown",' +
                 ' should match "YYYY-MM-DD"'
             ]},
        ], result)

    def test_validate_bad_files(self):
        """Validate some invalid files, such as might be provided by a user."""
        ctx = YSContext(os.path.join(self.basedir,
                                     'users', 'badfiles',
                                     'yangsets', 'badfiles'))
        result = ctx.validate()
        nomodule_yang_path = os.path.join('...', 'users', 'badfiles',
                                          'repositories', 'badrepo',
                                          'nomodule@unknown.yang')
        self.assertEqual([
            # empty.yang - can't even parse the name/revision from an empty
            # file, but we can at least report on it based on filename
            {'name': 'empty',
             'revision': 'unknown',
             'found': True,
             'usable': False,
             'errors': ['CRITICAL ERROR line 0: premature end of file'],
             'warnings': None},
            # ietf-yang-types - no errors itself
            {'name': 'ietf-yang-types',
             'revision': '2010-09-24',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': None},
            # key-order - used for other tests, but includes an undefined type
            {'name': 'key-order',
             'revision': '2001-01-01',
             'found': True,
             'usable': True,
             'errors': [
                 'CRITICAL ERROR line 20: type "undefined-type" not found'
                 ' in module key-order',
             ],
             'warnings': None},
            # no-namespaces.yang - missing mandatory 'namespace' and 'prefix'
            {'name': 'no-namespaces',
             'revision': '2010-09-24',
             'found': True,
             'usable': True,
             'errors': [
                 'CRITICAL ERROR line 2: unexpected keyword "import", '
                 'expected "namespace"',
                 'CRITICAL ERROR line 2: unexpected keyword "import", '
                 'expected "prefix"'],
             'warnings': None},
            # nomodule.yang - no 'module' or 'submodule' statement present
            {'name': 'nomodule',
             'revision': 'unknown',
             'found': True,
             'usable': False,
             'errors': [
                 'MAJOR ERROR line 1: unexpected modulename "firewall" in ' +
                 nomodule_yang_path + ', should be nomodule'],
             'warnings': None},
            # truncated.yang - has module and revision, but ends unexpectedly
            {'name': 'openconfig-if-ethernet',
             'revision': '2015-11-20',
             'found': True,
             'usable': False,
             'errors': ['CRITICAL ERROR line 35: premature end of file'],
             'warnings': None},
        ], result)

    def test_loading_multiversion(self):
        """Test for issues with yangset that requires older schema versions.

        - Yangset multiversion:a includes a@2010-09-08 and z@2001-01-01.
        - A depends on this version of Z but does not explicitly specify
          the revision number (bad A!).
        - There is a newer version of Z (2017-09-01) in multiversion's repo
          which A is not compatible with.
        - Make sure that we get the correct version of Z when loading and
          validating this yangset.
        """
        ys = YSYangSet.load("multiversion", "a")
        ctx = YSContext(ys, None, ['a', 'z'])
        result = ctx.validate()

        self.assertEqual([
            {'name': 'a',
             'revision': '2010-09-08',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': None},
            {'name': 'z',
             'revision': '2001-01-01',
             'found': True,
             'usable': True,
             'errors': None,
             'warnings': None},
        ], result)

    def test_repository_variants(self):
        """Test the different ways a YSContext can have a repository.

        1. Instantiation with a YSYangSet instance
        2. Instantiation with a pyang.FileRepository instance
        3. Instantiation with a path to a YSYangSet JSON file
        4. Instantiation with a path to a directory of files
        """
        ctx1 = YSContext(self.ys)
        ctx2 = YSContext(pyang.FileRepository(
            get_path('repository', user='test', reponame='testrepo'),
            use_env=False)
        )
        ctx3 = YSContext(
            get_path('yangset', user='test', setname='testyangset'))
        ctx4 = YSContext(
            get_path('repository', user='test', reponame='testrepo'))

        self.assertEqual(sorted(ctx1.modules.keys()),
                         sorted(ctx3.modules.keys()))
        self.assertEqual(sorted(ctx2.modules.keys()),
                         sorted(ctx4.modules.keys()))

        self.assertIsInstance(ctx3.repository, YSYangSet)
        self.assertIsInstance(ctx4.repository, pyang.FileRepository)

        # The YSYangSet is a subset of the files in the directory,
        # with the exception that pyang.FileRepository thinks
        # 'utf8module@unknown.yang' is a module named 'utf8module@unknown'.
        # We're fixing filemanager so that future additions to the repository
        # will use the preferred 'utf8module.yang' to keep pyang happy,
        # but in the meantime, we'll hack around it:
        self.assertLess(set(ctx1.modules.keys()) - {('utf8module', 'unknown')},
                        set(ctx2.modules.keys()))

    def test_delayed_loading(self):
        """Instantiate a context, then later load modules into it."""
        ctx = YSContext(self.ys, None, [])
        self.assertEqual(0, len(ctx.modules))

        # Load a module and its dependencies
        ctx.load_module_files(['openconfig-if-ethernet'])
        self.assertEqual(5, len(ctx.modules))

        # Try to load an additional module which fails parsing
        ctx.load_module_files(['Cisco-IOS-XR-lib-keychain-act'])
        self.assertEqual(5, len(ctx.modules))

        # Load a mix of new and already-loaded modules
        ctx.load_module_files([
            'openconfig-interfaces',  # loaded via openconfig-if-ethernet
            'Cisco-IOS-XR-ipv4-bgp-oc-oper',  # new + 4 new dependencies
            'ietf-yang-types',        # loaded via openconfig-if-ethernet
        ])
        self.assertEqual(10, len(ctx.modules))

    def test_identity_bases_implied(self):
        """Make sure the identity_bases are constructed properly.

        In this case we only explicitly load openconfig-interfaces,
        and the only identityrefs eventually loaded have bases in:

        - ietf-interfaces (interface-type)
        - openconfig-if-ethernet (ethernet-speed)
        """
        ctx = YSContext(self.ys, None, ['openconfig-interfaces'])
        self.assertEqual(
            ['ietf-interfaces', 'openconfig-if-ethernet'],
            sorted(ctx.identities.keys()))
        self.assertIn('ethernet-speed',
                      ctx.identities['openconfig-if-ethernet'])
        self.assertEqual(
            9, len(ctx.identities['openconfig-if-ethernet']['ethernet-speed'])
        )
        self.assertIn('interface-type',
                      ctx.identities['ietf-interfaces'])
        self.assertEqual(
            276, len(ctx.identities['ietf-interfaces']['interface-type'])
        )

    def test_identity_bases_order(self):
        """Make sure the identity_bases are constructed properly.

        In this case, we test different orders of loading to make sure
        things are correct regardless.
        """
        ctx = YSContext(self.ys, None,
                        ['openconfig-interfaces', 'ietf-interfaces'])
        self.assertEqual(
            ['ietf-interfaces', 'openconfig-if-ethernet'],
            sorted(ctx.identities.keys()))
        self.assertIn('ethernet-speed',
                      ctx.identities['openconfig-if-ethernet'])
        self.assertEqual(
            9, len(ctx.identities['openconfig-if-ethernet']['ethernet-speed'])
        )
        self.assertIn('interface-type',
                      ctx.identities['ietf-interfaces'])
        self.assertEqual(
            276, len(ctx.identities['ietf-interfaces']['interface-type'])
        )

        ctx = YSContext(self.ys, None,
                        ['ietf-interfaces', 'openconfig-interfaces'])
        self.assertEqual(
            ['ietf-interfaces', 'openconfig-if-ethernet'],
            sorted(ctx.identities.keys()))
        self.assertIn('ethernet-speed',
                      ctx.identities['openconfig-if-ethernet'])
        self.assertEqual(
            9, len(ctx.identities['openconfig-if-ethernet']['ethernet-speed'])
        )
        self.assertIn('interface-type',
                      ctx.identities['ietf-interfaces'])
        self.assertEqual(
            276, len(ctx.identities['ietf-interfaces']['interface-type'])
        )

        ctx = YSContext(self.ys, None,
                        ['openconfig-interfaces'])
        ctx.load_module_files(['ietf-interfaces'])
        self.assertEqual(
            ['ietf-interfaces', 'openconfig-if-ethernet'],
            sorted(ctx.identities.keys()))
        self.assertIn('ethernet-speed',
                      ctx.identities['openconfig-if-ethernet'])
        self.assertEqual(
            9, len(ctx.identities['openconfig-if-ethernet']['ethernet-speed'])
        )
        self.assertIn('interface-type',
                      ctx.identities['ietf-interfaces'])
        self.assertEqual(
            276, len(ctx.identities['ietf-interfaces']['interface-type'])
        )

    def test_identity_bases_submodules(self):
        """Make sure identity bases handles identities defined in a submodule.

        Models openconfig-aaa-radius and openconfig-aaa-tacacs are submodules
        of openconfig-aaa. They both have identities based in
        openconfit-aaa-types and since they are submodules, their identity
        prefix should be the parent's prefix (oc-aaa). The rest of them should
        be prefixed with oc-aaa-types.
        """
        ctx = YSContext(YSYangSet.load("test", "OC AAA"), None,
                        ['openconfig-aaa'])

        # should only be one module with identities
        self.assertEqual(
            ['openconfig-aaa-types'],
            sorted(ctx.identities.keys()))
        self.assertEqual([
            'AAA_ACCOUNTING_EVENT_TYPE',
            'AAA_AUTHORIZATION_EVENT_TYPE',
            'AAA_METHOD_TYPE',
            'AAA_SERVER_TYPE',
            'SYSTEM_DEFINED_ROLES',
        ], sorted(ctx.identities['openconfig-aaa-types'].keys()))

        # oc-aaa:RADIUS and oc-aaa:TACACS are defined in openconfig-aaa-radius
        # and openconfig-aaa-tacacs submodules of openconfig-aaa module.
        self.assertEqual(
            2,
            len(ctx.identities['openconfig-aaa-types']['AAA_SERVER_TYPE'])
        )
        self.assertEqual(
            ['oc-aaa:RADIUS', 'oc-aaa:TACACS'],
            sorted(ctx.identities['openconfig-aaa-types']['AAA_SERVER_TYPE']))

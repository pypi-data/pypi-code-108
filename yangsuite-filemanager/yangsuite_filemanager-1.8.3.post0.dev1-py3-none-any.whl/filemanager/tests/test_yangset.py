import os
import shutil

from yangsuite.paths import set_base_path
from .test_base import TestYSYangSetBase
from ..yangset import YSYangSet
from ..utility import repository_path
from ..base import ReadError


class TestYSYangSet(TestYSYangSetBase):
    """Tests for the YSYangSet class."""

    cls = YSYangSet
    yangset_file_path = os.path.join(TestYSYangSetBase.base_dir,
                                     'users', 'test',
                                     'yangsets', 'xrbgpv4')
    bad_yangset_path = os.path.join(TestYSYangSetBase.base_dir,
                                    'users', 'badfiles',
                                    'yangsets', 'badfiles')

    maxDiff = None

    def test_user_yangsets(self):
        """Test the YSYangSet.user_yangsets() API."""
        self.assertEqual(
            [{'name': 'xrbgpv4', 'slug': 'test+xrbgpv4'}],
            self.cls.user_yangsets('test'))
        self.assertEqual([],
                         self.cls.user_yangsets('nobody'))

    def test_all_yangsets(self):
        """Test the YSYangSet.all_yangsets() API."""
        self.assertEqual({
            'test': [{'name': 'xrbgpv4', 'slug': 'test+xrbgpv4'}],
            'nobody': [],
            'badfiles': [{'name': 'badfiles', 'slug': 'badfiles+badfiles'}],
        }, self.cls.all_yangsets())
        # Test for issue #145
        shutil.rmtree(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)
        # Junk file, not an actual user directory
        shutil.copy(__file__, os.path.join(self.temp_path, 'users'))
        self.assertEqual({
            'test': [{'name': 'xrbgpv4', 'slug': 'test+xrbgpv4'}],
            'nobody': [],
            'badfiles': [{'name': 'badfiles', 'slug': 'badfiles+badfiles'}],
        }, self.cls.all_yangsets())

    def test_from_file_negative(self):
        """Test various failure modes of YSYangSet.from_file()."""
        # No such file/directory
        self.assertRaises(OSError, self.cls.from_file,
                          os.path.join(self.temp_path, 'foo'))
        # Not a JSON file
        self.assertRaises(ValueError, self.cls.from_file, __file__)

    def test_load_negative(self):
        """Failure modes of YSYangSet.load()"""
        # Loading a nonexistent yangset for an existent user is an OSError
        self.assertRaises(OSError, self.cls.load,
                          'test', 'nosuchyangset')
        # Loading any yangset for a nonexistent user is a RuntimeError
        self.assertRaises(RuntimeError, self.cls.load,
                          'nosuchuser', 'nosuchyangset')
        # Invalid arguments raise ValueError
        self.assertRaises(ValueError, self.cls.load,
                          'nosuchuser', '')
        self.assertRaises(ValueError, self.cls.load,
                          '', 'testrepo')

    def test_from_file(self):
        """Test from_file() loading from JSON."""
        ys = self.cls.from_file(self.yangset_file_path)
        self.assertEqual('test', ys.owner)
        self.assertEqual('xrbgpv4', ys.setname)

        self.assertEqual([
            ("Cisco-IOS-XR-ipv4-bgp-datatypes", "2015-08-27"),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper", "2015-11-09"),
        ], [(m[0], m[1]) for m in sorted(ys.modules)])

        ys2 = self.cls.load('test', 'xrbgpv4')
        self.assertEqual(ys, ys2)

    def test_delete(self):
        shutil.rmtree(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)
        fake_yangset_path = os.path.join(self.temp_path, 'users', 'test',
                                         'yangsets', 'xrbgpv4')
        self.assertTrue(os.path.exists(fake_yangset_path))

        self.cls.delete('test', 'xrbgpv4')
        self.assertFalse(os.path.exists(fake_yangset_path))

        self.assertRaises(OSError, self.cls.load, 'test', 'xrbgpv4')

    def test_get_modules_and_revisions_negative(self):
        set_base_path(self.temp_path)
        files_path = os.path.join(self.temp_path,
                                  'users', 'test', 'repositories', 'scratch')
        os.makedirs(files_path)
        # Directory in set directory; we don't presently recurse
        os.makedirs(os.path.join(files_path, 'directory'))
        # Not a YANG file, not named with .yang
        shutil.copy(__file__, files_path)
        # Not a YANG file, named with .yang
        shutil.copyfile(__file__, os.path.join(files_path, 'fake.yang'))

        ys = self.cls('test', 'badyangset', [os.path.join(files_path, p)
                                             for p in os.listdir(files_path)],
                      reponame='scratch')
        self.assertEqual(
            [('fake', 'unknown')],
            [(m[0], m[1]) for m in ys.get_modules_and_revisions()])

    def test_get_module_from_handle_invalid(self):
        """Negative tests for get_module_from_handle() API"""
        ys = self.cls.load('badfiles', 'badfiles')
        # IOError caught by yangset and rethrown as ReadError
        self.assertRaises(ReadError,
                          ys.get_module_from_handle, 'foobar')
        # UnicodeDecodeError caught by yangset and rethrown as ReadError
        self.assertRaises(ReadError,
                          ys.get_module_from_handle,
                          os.path.join(ys.repository.path,
                                       'cp1252@unknown.yang'))

    def test_equality(self):
        """Test equality checks; overrides TestYSYangSetBase test."""
        ys1 = self.cls.load('test', 'xrbgpv4')
        ys2 = YSYangSet.from_file(self.yangset_file_path)
        ys3 = self.cls.load('badfiles', 'badfiles')

        self.assertTrue(ys1 == ys2)
        self.assertFalse(ys1 == ys3)

        # Check inverse as well for python 2's sake.
        self.assertFalse(ys1 != ys2)
        self.assertTrue(ys1 != ys3)

    def test_repr(self):
        """Test string representation."""
        ys = self.cls.load('test', 'xrbgpv4')
        self.assertEqual("YANG set 'xrbgpv4' owned by 'test' (2 modules)",
                         repr(ys))

    def test_modules_setter(self):
        """Test input formats accepted/rejected by the modules() property."""
        ys = self.cls(owner='test', setname='fakesetname',
                      reponame='testrepo', modules=[
                          # absolute path to existing module, as ascii
                          os.path.join(repository_path('test', 'testrepo'),
                                       "iana-if-type@2015-06-12.yang"),
                          # absolute path to existing module, as unicode
                          os.path.join(repository_path('test', 'testrepo'),
                                       u"ietf-inet-types@2010-09-24.yang"),
                          # absolute path to non-yang file
                          os.path.join(repository_path('test', 'testrepo'),
                                       'testrepo.json'),
                          # nonexistent file
                          os.path.join(repository_path('test', 'testrepo'),
                                       'nosuchfile.yang'),
                          # name, rev, path - exists
                          ['openconfig-if-ethernet', '2015-11-20',
                           os.path.join(
                               repository_path('test', 'testrepo'),
                               'openconfig-if-ethernet@2015-11-20.yang')],
                          # name, rev, path - does not exist
                          ['notinrepo', '2001-01-01',
                           os.path.join(repository_path('test', 'testrepo'),
                                        'notinrepo@2001-01-01.yang')],
                          # name, rev - exists
                          ['Cisco-IOS-XR-types', '2015-06-29'],
                          # name, rev - does not exist
                          ['notfound', '2010-09-08'],
                          # name, unknown rev - exists
                          ['ietf-yang-types', 'unknown'],
                      ])
        self.assertEqual([(name, rev) for name, rev, path in ys.modules], [
            # derived from file, given path to it
            ('Cisco-IOS-XR-types', '2015-06-29'),
            ('iana-if-type', '2015-06-12'),
            # we pointed to an older revision, make sure we got it
            ('ietf-inet-types', '2010-09-24'),
            # we didn't specify revision - get the latest!
            ('ietf-yang-types', '2013-07-15'),
            ('openconfig-if-ethernet', '2015-11-20'),
        ])
        with self.assertRaises(ValueError):
            ys = self.cls(owner='test', setname='fakesetname',
                          reponame='testrepo', modules=[
                              ['2015-06-29'],
                              22,
                              None,
                          ])

    def test_mutability(self):
        """YSYangSet should be immutable."""
        ys = self.cls.load('test', 'xrbgpv4')
        self.assertEqual([
            ("Cisco-IOS-XR-ipv4-bgp-datatypes", "2015-08-27"),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper", "2015-11-09"),
        ], [(m[0], m[1]) for m in ys.modules])

        with self.assertRaises(RuntimeError):
            ys.modules = ys.modules + [
                ("Cisco-IOS-XR-lib-keychain-cfg", "2015-07-30")]

    def test_module_path(self):
        """Test the module_path() API."""
        ys = self.cls.load('test', 'xrbgpv4')
        # successful get with name and revision
        self.assertEqual(os.path.join(
            self.test_dir, 'Cisco-IOS-XR-ipv4-bgp-datatypes@2015-08-27.yang'),
            ys.module_path('Cisco-IOS-XR-ipv4-bgp-datatypes', '2015-08-27'))
        # successful get with name but not revision
        self.assertEqual(os.path.join(
            self.test_dir, 'Cisco-IOS-XR-ipv4-bgp-datatypes@2015-08-27.yang'),
            ys.module_path('Cisco-IOS-XR-ipv4-bgp-datatypes'))
        # fail get - no matching revision
        self.assertIs(None,
                      ys.module_path('Cisco-IOS-XR-ipv4-bgp-datatypes',
                                     '2018-02-12'))
        # fail get - no such module
        self.assertIs(None, ys.module_path('nosuchmodule'))
        self.assertIs(None, ys.module_path('nosuchmodule', '2015-08-27'))

    def test_extra_dependencies(self):
        """YSYangSet can't discover dependencies from the repo."""
        ys = self.cls.load('test', 'xrbgpv4')
        self.assertEqual([
            ('Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1', 'unknown'),
            ('Cisco-IOS-XR-types', 'unknown'),
            ('ietf-inet-types', 'unknown'),
        ], [(m[0], m[1]) for m in ys.extra_dependencies()])

        ys = self.cls('test', 'n/a', [('ietf-interfaces', '2014-05-08')],
                      repository='test+testrepo')
        self.assertEqual([
            ('ietf-yang-types', 'unknown'),
        ], [(m[0], m[1]) for m in ys.extra_dependencies()])

        # Submodule depends on parent module as well
        ys = self.cls('test', 'n/a',
                      [('Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1', "2015-11-09")],
                      repository='test+testrepo')
        self.assertEqual([
            ('Cisco-IOS-XR-ipv4-bgp-oc-oper', 'unknown'),
            ('Cisco-IOS-XR-types', 'unknown'),
            ('ietf-inet-types', 'unknown'),
            ('ietf-yang-types', 'unknown'),
        ], [(m[0], m[1]) for m in ys.extra_dependencies()])

    def test_modules_using(self):
        """Upstream module detection."""
        ys = self.cls.load('test', 'xrbgpv4')

        # In this set, one known upstream
        self.assertEqual([
            'Cisco-IOS-XR-ipv4-bgp-oc-oper',
        ], sorted(ys.modules_using('Cisco-IOS-XR-ipv4-bgp-datatypes')))

        # In this set, no known upstreams
        self.assertEqual([], sorted(ys.modules_using(
            'Cisco-IOS-XR-ipv4-bgp-oc-oper')))

        # Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1 is actually missing from this set,
        # but we can still check what modules in this set need it.
        self.assertEqual([
            'Cisco-IOS-XR-ipv4-bgp-oc-oper',
        ], sorted(ys.modules_using('Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1')))

        # In the repo, but not in this set or known as a missing dependency.
        self.assertEqual(set(), ys.modules_using('ietf-yang-types'))

    def test_modules_augmenting(self):
        """Detection of modules that augment a module."""
        ys = self.cls('test', 'n/a', [
            ('ietf-interfaces', '2014-05-08'),
        ], repository='test+testrepo')
        self.assertEqual([], ys.modules_augmenting('openconfig-interfaces'))

        ys = self.cls('test', 'n/a', [
            ('ietf-interfaces', '2014-05-08'),
            ('openconfig-if-ethernet', "2015-11-20"),
            ('openconfig-interfaces', "2015-11-20"),
        ], repository='test+testrepo')

        self.assertEqual(['openconfig-if-ethernet'],
                         ys.modules_augmenting('openconfig-interfaces'))

    def test_modules_deriving_identities_from(self):
        """Detection of modules that derive identities from a module."""
        ys = self.cls('test', 'n/a', [
            ('ietf-interfaces', '2014-05-08'),
        ], repository='test+testrepo')

        self.assertEqual([], ys.modules_deriving_identities_from(
            'ietf-interfaces'))

        ys = self.cls('test', 'n/a', [
            ('ietf-interfaces', '2014-05-08'),
            ('iana-if-type', '2015-06-12'),
        ], repository='test+testrepo')

        self.assertEqual(['iana-if-type'],
                         ys.modules_deriving_identities_from(
                             'ietf-interfaces'))

    def test_validate(self):
        """Quick self-validation test."""
        ys = self.cls.load('test', 'xrbgpv4')
        self.assertEqual([
            {
                'name': 'Cisco-IOS-XR-ipv4-bgp-datatypes',
                'revision': '2015-08-27',
                'found': True,
                'in_yangset': True,
                'usable': True,
                'warnings': [],
                'errors': [],
            },
            {
                'name': 'Cisco-IOS-XR-ipv4-bgp-oc-oper',
                'revision': '2015-11-09',
                'found': True,
                'in_yangset': True,
                'usable': False,
                'warnings': [],
                'errors': [
                    'Dependency Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1@unknown '
                    'not found!',
                    'Dependency Cisco-IOS-XR-types@unknown not found!',
                    'Dependency ietf-inet-types@unknown not found!',
                ],
            },
            {
                'name': 'Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1',
                'revision': 'unknown',
                'found': False,
                'in_yangset': False,
                'usable': False,
                'warnings': [],
                'errors': ['Not found in YANG set or user repository'],
            },
            {
                'name': 'Cisco-IOS-XR-types',
                'revision': 'unknown',
                'found': False,
                'in_yangset': False,
                'usable': False,
                'warnings': [],
                'errors': ['Not found in YANG set or user repository'],
            },
            {
                'name': 'ietf-inet-types',
                'revision': 'unknown',
                'found': False,
                'in_yangset': False,
                'usable': False,
                'warnings': [],
                'errors': ['Not found in YANG set or user repository'],
            },
        ], ys.validate())

    def test_validate_negative(self):
        """Validate check with some malformed files."""
        ys = self.cls.load('badfiles', 'badfiles')
        self.assertEqual([
            {
                'name': 'cp1252',
                'revision': 'unknown',
                'found': True,
                'usable': True,
                'in_yangset': True,
                'warnings': [],
                'errors': [],
            },
            {
                'name': 'empty',
                'revision': 'unknown',
                'found': True,
                'usable': False,
                'in_yangset': True,
                'warnings': [],
                'errors': ['Error in parsing module'],
            },
            {
                'name': 'nomodule',
                'revision': 'unknown',
                'found': True,
                'usable': False,
                'in_yangset': True,
                'warnings': [],
                'errors': ['Error in parsing module'],
            },
            {
                'name': 'truncated',
                'revision': '2015-11-20',
                'found': False,
                'usable': False,
                'in_yangset': True,
                'warnings': [],
                'errors': ['No information available'],
            },
        ], ys.validate())

    def test_get_module_graph_negative(self):
        """Some negative tests for the internal _get_module_graph API."""
        ys = self.cls.load('badfiles', 'badfiles')
        # Normally _get_module_graph gets called with ys.modules, but
        # it's easier to exercise negative cases with a constructed list

        # File not found - still added to graph
        graph = ys._get_module_graph([
            ('bar', 'unknown', '/foo/bar'),
        ])
        self.assertEqual(['bar'], graph.nodes())

        graph = ys.digraph
        # None of the modules actually *in* this set are loaded successfully,
        # but we at least detect a few dependencies that we might need.
        self.assertEqual([
            'cp1252',
            'empty',
            'iana-if-type',
            'ietf-yang-types',
            'nomodule',
            'openconfig-extensions',
            'openconfig-if-ethernet',
            'openconfig-interfaces',
        ], sorted(graph.nodes()))

    def test_no_multi_revisions(self):
        """Multiple revisions of a single module are not allowed."""
        self.assertRaises(ValueError, self.cls, owner='test',
                          setname='multirev', reponame='testrepo',
                          modules=[('ietf-inet-types', '2010-09-24'),
                                   ('ietf-inet-types', '2013-07-15')])

# -*- coding: utf-8 -*-
import os
import shutil

from yangsuite.paths import get_path, set_base_path
from .test_yangset import TestYSYangSet
# TODO: due to the way test case discovery works, this means TestYSYangSet will
#       actually be run twice. It's quick enough that's not a big problem right
#       now, but it's inelegant.
from ..mutableyangset import YSMutableYangSet
from ..repository import YSYangRepository
from ..utility import yangset_path, repository_path, merge_user_set


class TestYSMutableYangSet(TestYSYangSet):
    """Test YSMutableYangSet class."""

    cls = YSMutableYangSet

    def test_write(self):
        """Test writing to JSON."""
        shutil.rmtree(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)
        ys = self.cls.load('test', 'xrbgpv4')
        ys.setname = 'newset'
        ys.write()

        self.assertTrue(os.path.exists(
            get_path('yangset', user='test', setname='newset')))

        ys2 = self.cls.load('test', 'newset')
        self.assertEqual(ys, ys2)
        self.assertEqual(ys2.mtime.strftime("%Y-%m-%d %H:%M:%S"),
                         ys2.datastore_mtime.strftime("%Y-%m-%d %H:%M:%S"))

        self.cls.delete('test', 'newset')
        self.assertFalse(os.path.exists(
            get_path('yangset', user='test', setname='newset')))
        self.assertRaises(OSError, self.cls.load, 'test', 'newset')

    def test_setname_vs_filename(self):
        """Test translation between unicode setnames and ascii filenames."""
        shutil.rmtree(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)

        # Create and save a new yangset with a unicode name.
        # Note that due to differences between Python 2.7 and 3.x unicode
        # handling, slugify will not necessarily produce the same results
        # on one versus the other - specifically, 2.7 will omit any characters
        # outside the Unicode BMP, while 3.x will attempt to find replacements
        # for them.
        # 2.7: slugify( "𝐌𝐲 𝑌𝐴𝑁𝐺 𝓈ℯ𝓉 ❤️") --> 'e'
        # 3.6: slugify( "𝐌𝐲 𝑌𝐴𝑁𝐺 𝓈ℯ𝓉 ❤️") --> 'my-yang-set'
        # To get consistent test results here, we are careful about
        # which characters we use in our example.
        ys = self.cls('test', u"My ♥︎ YANG ♡ set ❤️", [
            ('ietf-inet-types', '2013-07-15'),
            ('ietf-yang-types', '2013-07-15')
        ], reponame='testrepo')
        ys.write()
        self.assertTrue(os.path.exists(
            get_path('yangset', user='test', setname='my-yang-set')))
        # os.path.exists may be ASCII-only depending on environment,
        # so the below may error out e.g. on our Jenkins server.
        # self.assertFalse(os.path.exists(get_path(
        #     'yangset', user='test', setname="My ♥︎ YANG ♡ set ❤️")))
        # Instead, we can check the dir listing:
        self.assertNotIn(u"My ♥︎ YANG ♡ set ❤️",
                         os.listdir(get_path('yangsets_dir', user='test')))
        self.assertEqual(
            yangset_path('test', u"My ♥︎ YANG ♡ set ❤️"),
            get_path('yangset', user='test', setname='my-yang-set'))

        ys2 = self.cls.load('test', u"My ♥︎ YANG ♡ set ❤️")
        self.assertEqual(ys, ys2)
        self.assertEqual(ys2.setname, u"My ♥︎ YANG ♡ set ❤️")

        ys3 = self.cls.load('test', 'my-yang-set')
        self.assertEqual(ys, ys3)
        self.assertEqual(ys3.setname, u"My ♥︎ YANG ♡ set ❤️")

        self.assertEqual(ys2, ys3)

    def test_setname_and_reponame_unicode(self):
        """Test that things work together with unicode in both set and repo."""
        shutil.rmtree(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)

        # Create and populate new repo with files from testrepo
        newrepo = YSYangRepository.create('test', u'♛ ⇒ h4, checkmate!')
        newrepo.add_yang_files(repository_path('test', 'testrepo'),
                               remove=False)

        # Create new yangset linked to new repo
        ys = self.cls('test', u"My ♥︎ YANG ♡ set ❤️",
                      [('ietf-inet-types', '2013-07-15'),
                       ('ietf-yang-types', '2013-07-15')],
                      repository=newrepo.slug)
        ys.write()

        ys2 = self.cls.load('test', u"My ♥︎ YANG ♡ set ❤️")
        self.assertEqual(ys2.setname, u"My ♥︎ YANG ♡ set ❤️")
        self.assertEqual(ys2.reponame, u'♛ ⇒ h4, checkmate!')
        self.assertEqual([m[:2] for m in ys2.modules],
                         [('ietf-inet-types', '2013-07-15'),
                          ('ietf-yang-types', '2013-07-15')])

    def test_repository_setter(self):
        """Test changes to the associated repository."""
        shutil.rmtree(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)

        anotherrepo = YSYangRepository.create('test', u'Another repo')
        anotherrepo.add_yang_files(YSYangRepository('test', 'testrepo').path,
                                   remove=False)

        ys = self.cls.load(owner='test', setname='xrbgpv4')
        self.assertEqual(ys.reponame, 'testrepo')
        initial_mtime = ys.mtime

        ys.repository = anotherrepo
        self.assertEqual(ys.reponame, u'Another repo')

        ys.repository = merge_user_set('test', 'testrepo')
        self.assertEqual(ys.reponame, 'testrepo')

        ys.repository = u'' + merge_user_set('test', u'Another repo')
        self.assertEqual(ys.reponame, u'Another repo')

        self.assertGreater(ys.mtime, initial_mtime)

        with self.assertRaises(TypeError):
            ys.repository = None

        with self.assertRaises(TypeError):
            ys.repository = ['too', 'many', 'args']

    def test_extra_dependencies(self):
        """Unlike YSYangSet, YSMutableYangSet can find stuff in repo."""
        ys = self.cls.load('test', 'xrbgpv4')
        self.assertEqual([
            ('Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1', '2015-11-09'),
            ('Cisco-IOS-XR-types', '2015-06-29'),
            ('ietf-inet-types', '2013-07-15'),
            ('ietf-yang-types', '2013-07-15'),
        ], [(m[0], m[1]) for m in ys.extra_dependencies()])
        # All dependencies found in repo

        ys = self.cls('test', 'n/a', [('ietf-interfaces', '2014-05-08')],
                      reponame='testrepo')
        self.assertEqual([
            ('ietf-yang-types', '2013-07-15'),
        ], [(m[0], m[1]) for m in ys.extra_dependencies()])
        # All dependencies found in repo

        # Submodule depends on parent module as well
        ys = self.cls('test', 'n/a',
                      [('Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1', "2015-11-09")],
                      repository='test+testrepo')
        self.assertEqual([
            ('Cisco-IOS-XR-ipv4-bgp-oc-oper', '2015-11-09'),
            ('Cisco-IOS-XR-types', '2015-06-29'),
            ('ietf-inet-types', '2013-07-15'),
            ('ietf-yang-types', '2013-07-15'),
        ], [(m[0], m[1]) for m in ys.extra_dependencies()])
        # All dependencies found in repo

        # Create a copy of the repository with missing files
        os.rmdir(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)
        os.remove(os.path.join(
            get_path('repository', user='test', reponame='testrepo'),
            'ietf-inet-types@2013-07-15.yang'))
        os.remove(os.path.join(
            get_path('repository', user='test', reponame='testrepo'),
            'ietf-inet-types@2010-09-24.yang'))
        ys = self.cls.load('test', 'xrbgpv4')
        self.assertEqual([
            ('Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1', '2015-11-09'),
            ('Cisco-IOS-XR-types', '2015-06-29'),
            ('ietf-inet-types', 'unknown'),
            ('ietf-yang-types', '2013-07-15'),
        ], [(m[0], m[1]) for m in ys.extra_dependencies()])

    def test_modules_using(self):
        """Unlike YSYangSet, YSMutableYangSet can find stuff in repo."""
        ys = self.cls.load('test', 'xrbgpv4')

        # In this set, one known upstream
        self.assertEqual([
            'Cisco-IOS-XR-ipv4-bgp-oc-oper',
        ], sorted(ys.modules_using('Cisco-IOS-XR-ipv4-bgp-datatypes')))

        # In this set, no known upstreams
        self.assertEqual([], sorted(ys.modules_using(
            'Cisco-IOS-XR-ipv4-bgp-oc-oper')))

        # Not in set, but a direct dependency of modules in the set
        self.assertEqual([
            'Cisco-IOS-XR-ipv4-bgp-oc-oper',
        ], sorted(ys.modules_using('Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1')))

        # not in set but in repo
        self.assertEqual([
            'Cisco-IOS-XR-ipv4-bgp-oc-oper',
            'Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1',
            'iana-if-type',
            'ietf-interfaces',
            'openconfig-if-ethernet',
            'openconfig-interfaces',
        ], sorted(ys.modules_using('ietf-yang-types')))

        # not in set or repo
        self.assertEqual(set(), ys.modules_using('foobar'))

    def test_modules_augmenting(self):
        """Unlike YSYangSet, YSMutableYangSet can find stuff in repo."""
        ys = self.cls('test', 'n/a', [
            ('ietf-interfaces', '2014-05-08'),
        ], repository='test+testrepo')
        self.assertEqual(['openconfig-if-ethernet'],
                         ys.modules_augmenting('openconfig-interfaces'))

        ys = self.cls('test', 'n/a', [
            ('ietf-interfaces', '2014-05-08'),
            ('openconfig-if-ethernet', "2015-11-20"),
            ('openconfig-interfaces', "2015-11-20"),
        ], repository='test+testrepo')

        self.assertEqual(['openconfig-if-ethernet'],
                         ys.modules_augmenting('openconfig-interfaces'))

    def test_modules_deriving_identities_from(self):
        """Unlike YSYangSet, YSMutableYangSet can find stuff in repo."""
        ys = self.cls('test', 'n/a', [
            ('ietf-interfaces', '2014-05-08'),
        ], repository='test+testrepo')

        self.assertEqual(['iana-if-type'],
                         ys.modules_deriving_identities_from(
                             'ietf-interfaces'))

        ys = self.cls('test', 'n/a', [
            ('ietf-interfaces', '2014-05-08'),
            ('iana-if-type', '2015-06-12'),
        ], repository='test+testrepo')

        self.assertEqual(['iana-if-type'],
                         ys.modules_deriving_identities_from(
                             'ietf-interfaces'))

    def test_upstream_modules(self):
        """Test the upstream_modules() API."""
        ys = self.cls.load('test', 'xrbgpv4')
        self.assertEqual([], ys.upstream_modules())

        ys = self.cls('test', 'n/a', [('ietf-interfaces', '2014-05-08')],
                      repository='test+testrepo')
        self.assertEqual([], ys.upstream_modules())

        # TODO add some cases where there actually are upstream modules

    def test_augmenter_modules(self):
        """Test the augmenter_modules() API."""
        ys = self.cls.load('test', 'xrbgpv4')
        self.assertEqual([], ys.augmenter_modules())

        ys = self.cls('test', 'n/a', [('openconfig-interfaces', '2015-11-20')],
                      repository='test+testrepo')
        self.assertEqual([
            ('openconfig-if-ethernet', '2015-11-20'),
        ], [(m[0], m[1]) for m in ys.augmenter_modules()])

    def test_identity_deriving_modules(self):
        """Test the identity_deriving_modules() API."""
        ys = self.cls.load('test', 'xrbgpv4')
        self.assertEqual([], ys.identity_deriving_modules())

        ys = self.cls('test', 'n/a', [('ietf-interfaces', '2014-05-08')],
                      reponame='testrepo')
        self.assertEqual(
            [('iana-if-type', '2015-06-12')],
            [(m[0], m[1]) for m in ys.identity_deriving_modules()])

    def test_related_modules(self):
        """Test the related_modules() API."""
        ys = self.cls.load('test', 'xrbgpv4')
        self.assertEqual([
            ('Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1', '2015-11-09'),
        ], [(m[0], m[1]) for m in ys.related_modules()])

        ys = self.cls('test', 'n/a', [('ietf-interfaces', '2014-05-08')],
                      reponame='testrepo')
        self.assertEqual([], ys.related_modules())

        ys = self.cls.load('badfiles', 'badfiles')
        self.assertEqual([], ys.related_modules())

    def test_mutability(self):
        """YSMutableYangSet is mutable."""
        ys = self.cls.load('test', 'xrbgpv4')
        initial_mtime = ys.mtime
        self.assertEqual([
            ("Cisco-IOS-XR-ipv4-bgp-datatypes", "2015-08-27"),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper", "2015-11-09"),
        ], [(m[0], m[1]) for m in ys.modules])

        ys.modules = ys.modules + [
            ("Cisco-IOS-XR-lib-keychain-cfg", "2015-07-30")]
        self.assertEqual([
            ("Cisco-IOS-XR-ipv4-bgp-datatypes", "2015-08-27"),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper", "2015-11-09"),
            ("Cisco-IOS-XR-lib-keychain-cfg", "2015-07-30"),
        ], [(m[0], m[1]) for m in ys.modules])
        self.assertGreater(ys.mtime, initial_mtime)

    def test_validate(self):
        """Unlike YSYangSet, YSMutableYangSet suggests dependencies in repo."""
        ys = self.cls.load('test', 'xrbgpv4')
        self.maxDiff = None
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
                'warnings': [
                    'Missing dependency Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1 - '
                    'possibly add Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1'
                    '@2015-11-09 from the repository?',
                    'Missing dependency Cisco-IOS-XR-types - possibly add '
                    'Cisco-IOS-XR-types@2015-06-29 from the repository?',
                    'Missing dependency ietf-inet-types - possibly add '
                    'ietf-inet-types@2013-07-15 from the repository?',
                    'Missing dependency ietf-yang-types - possibly add '
                    'ietf-yang-types@2013-07-15 from the repository?',
                ],
                'errors': [],
            },
            {
                'name': 'Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1',
                'revision': '2015-11-09',
                'found': True,
                'in_yangset': False,
                'usable': False,
                'warnings': [
                    'Found in user repository but must be added '
                    'to the YANG set.',
                    'Missing dependency Cisco-IOS-XR-types - possibly add '
                    'Cisco-IOS-XR-types@2015-06-29 from the repository?',
                    'Missing dependency ietf-inet-types - possibly add '
                    'ietf-inet-types@2013-07-15 from the repository?',
                    'Missing dependency ietf-yang-types - possibly add '
                    'ietf-yang-types@2013-07-15 from the repository?',
                ],
                'errors': [],
            },
            {
                'name': 'Cisco-IOS-XR-types',
                'revision': '2015-06-29',
                'found': True,
                'in_yangset': False,
                'usable': False,
                'warnings': [
                    'Found in user repository but must be added '
                    'to the YANG set.',
                ],
                'errors': [],
            },
            {
                'name': 'ietf-inet-types',
                'revision': '2013-07-15',
                'found': True,
                'in_yangset': False,
                'usable': False,
                'warnings': [
                    'Found in user repository but must be added '
                    'to the YANG set.',
                ],
                'errors': [],
            },
            {
                'name': 'ietf-yang-types',
                'revision': '2013-07-15',
                'found': True,
                'in_yangset': False,
                'usable': False,
                'warnings': [
                    'Found in user repository but must be added '
                    'to the YANG set.',
                ],
                'errors': [],
            },
        ], ys.validate())

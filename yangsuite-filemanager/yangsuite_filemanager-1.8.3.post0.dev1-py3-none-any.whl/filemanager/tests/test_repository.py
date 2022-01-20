# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import shutil
import time

from yangsuite.paths import set_base_path, get_path
from .test_base import TestYSYangSetBase
from ..repository import YSYangRepository
from ..yangset import YSYangSet


class TestYSYangRepository(TestYSYangSetBase):
    """Tests for the YSYangRepository class."""

    cls = YSYangRepository

    def test_repository(self):
        """Verify that YSYangRepository includes all user files in the dir."""
        ys = self.cls('test', 'testrepo')
        self.assertEqual('test', ys.owner)
        self.assertEqual('testrepo', ys.reponame)
        # repo.json mtime is probably just when this repo was pulled,
        # so we can't check for any specific time
        # self.assertEqual(ys.mtime, ....)
        # But we can make sure it's self-consistent!
        self.assertEqual(ys.mtime, ys.datastore_mtime)
        self.assertFalse(ys.is_stale)

        # NOTE: because this just lists .yang files in the directory,
        #       it includes the Cisco-IOS-XR-lib-keychain-act file
        #       that pyang is actually unable to parse.
        mods = ys.get_modules_and_revisions()
        self.assertIsInstance(mods, list)
        self.assertEqual([
            ("Cisco-IOS-XR-ipv4-bgp-datatypes", "2015-08-27",
             os.path.join(self.test_dir,
                          "Cisco-IOS-XR-ipv4-bgp-datatypes@2015-08-27.yang")),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper", "2015-11-09",
             os.path.join(self.test_dir,
                          "Cisco-IOS-XR-ipv4-bgp-oc-oper@2015-11-09.yang")),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1", "2015-11-09",
             os.path.join(
                 self.test_dir,
                 "Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1@2015-11-09.yang")),
            ("Cisco-IOS-XR-lib-keychain-act", "2017-04-17",
             os.path.join(self.test_dir,
                          "Cisco-IOS-XR-lib-keychain-act@2017-04-17.yang")),
            ('Cisco-IOS-XR-lib-keychain-cfg', '2015-07-30',
             os.path.join(self.test_dir,
                          'Cisco-IOS-XR-lib-keychain-cfg@2015-07-30.yang')),
            ("Cisco-IOS-XR-types", "2015-06-29",
             os.path.join(self.test_dir,
                          "Cisco-IOS-XR-types@2015-06-29.yang")),
            ("iana-if-type", "2015-06-12",
             os.path.join(self.test_dir, "iana-if-type@2015-06-12.yang")),
            ("ietf-inet-types", "2010-09-24",
             os.path.join(self.test_dir, "ietf-inet-types@2010-09-24.yang")),
            ("ietf-inet-types", "2013-07-15",
             os.path.join(self.test_dir, "ietf-inet-types@2013-07-15.yang")),
            ("ietf-interfaces", "2014-05-08",
             os.path.join(self.test_dir, "ietf-interfaces@2014-05-08.yang")),
            ("ietf-yang-types", "2010-09-24",
             os.path.join(self.test_dir, "ietf-yang-types@2010-09-24.yang")),
            ("ietf-yang-types", "2013-07-15",
             os.path.join(self.test_dir, "ietf-yang-types@2013-07-15.yang")),
            ("openconfig-if-ethernet", "2015-11-20",
             os.path.join(self.test_dir,
                          "openconfig-if-ethernet@2015-11-20.yang")),
            ("openconfig-interfaces", "2015-11-20",
                os.path.join(self.test_dir,
                             "openconfig-interfaces@2015-11-20.yang")),
        ], sorted(mods))

        handle = os.path.join(
            self.test_dir, "Cisco-IOS-XR-lib-keychain-act@2017-04-17.yang")
        filename, fmt, text = ys.get_module_from_handle(handle)

        self.assertEqual(handle, filename)
        self.assertEqual('yang', fmt)
        self.assertEqual(open(handle, 'r').read(), text)

    def test_repo_nonexistent(self):
        """Can't load a nonexistent repo - must create() first."""
        # TypeError - invalid arguments
        self.assertRaises(TypeError, self.cls, 27)
        self.assertRaises(TypeError, self.cls, 'test', 'testrepo', 'extraarg')
        # OSError - user exists, but not the requested repo
        self.assertRaises(OSError, self.cls, 'test', 'nonexistent')
        # RuntimeError - user doesn't even exist
        self.assertRaises(RuntimeError, self.cls,
                          'nonexistent', 'testrepo')

    def test_add_yang_files(self):
        """Exercise the add_yang_files() API."""
        set_base_path(self.temp_path)
        user_dir = os.path.join(self.temp_path, 'users', 'foobar')
        repo_dir = os.path.join(user_dir, 'repositories', 'baz')

        os.makedirs(user_dir)

        repo = self.cls.create('foobar', 'baz')
        initial_mtime = repo.mtime

        same_repo = self.cls('foobar', 'baz')
        self.assertEqual(repo.mtime, same_repo.mtime)

        time.sleep(2)

        result = repo.add_yang_files(self.test_dir, remove=False)

        self.assertEqual(len(self.test_yang_files), len(result['added']))
        # repo_dir will contain all the yang files plus baz.json
        self.assertEqual(len(self.test_yang_files) + 1,
                         len(os.listdir(repo_dir)))
        self.assertEqual([], result['unchanged'])
        self.assertEqual([], result['errors'])
        # Make sure the mtime was updated
        self.assertGreater(repo.mtime, initial_mtime)
        latest_mtime = repo.mtime
        self.assertEqual(repo.mtime.strftime("%Y-%m-%dT%H:%M:%S"),
                         repo.datastore_mtime.strftime("%Y-%m-%dT%H:%M:%S"))
        self.assertFalse(repo.is_stale)
        # We updated "repo" - "same_repo" is now stale
        self.assertLess(same_repo.mtime, latest_mtime)
        self.assertLess(same_repo.mtime, same_repo.datastore_mtime)
        self.assertTrue(same_repo.is_stale)

        result = repo.add_yang_files(self.test_dir, remove=False)
        self.assertEqual([], result['added'])
        self.assertEqual(len(self.test_yang_files) + 1,
                         len(os.listdir(repo_dir)))
        self.assertEqual(len(self.test_yang_files), len(result['unchanged']))
        self.assertEqual([], result['errors'])
        # Nothing actually changed, so mtime is unchanged
        self.assertEqual(latest_mtime, repo.mtime)

        # Additional tests are in test_utility.test_migrate_yang_files

    def test_user_repos(self):
        """Exercise the user_repos() API."""
        self.assertEqual([], self.cls.user_repos('nobody'))
        self.assertEqual([
            {'name': 'testrepo', 'slug': 'test+testrepo'},
        ], self.cls.user_repos('test'))
        # Yes, repo names can contain unicode. Yay for slugify!
        self.assertEqual([
            {'name': 'PrefixCollision',
             'slug': 'badfiles+prefixcollision'},
            {'name': '😀 badrepo 🙂', 'slug': 'badfiles+badrepo'},
        ], self.cls.user_repos('badfiles'))

    def test_all_repos(self):
        """Exercise the all_repos() API."""
        # 'nobody' has no repos, so they're not in the list below
        self.assertEqual({
            'test': [{'name': 'testrepo', 'slug': 'test+testrepo'}],
            'badfiles': [
                {'name': 'PrefixCollision',
                 'slug': 'badfiles+prefixcollision'},
                {'name': '😀 badrepo 🙂', 'slug': 'badfiles+badrepo'},
            ],
        }, self.cls.all_repos())

    def test_create_update_delete(self):
        """Repository creation, update, and deletion."""
        set_base_path(self.temp_path)
        os.makedirs(os.path.join(self.temp_path, 'users', 'x'))

        repo1 = self.cls.create('x', 'Hello World!')
        self.assertEqual(repo1.owner, 'x')
        self.assertEqual(repo1.reponame, 'Hello World!')
        self.assertEqual(repo1.modules, [])
        initial_mtime = repo1.mtime
        self.assertFalse(repo1.is_stale)

        # The repo directory uses the slugified reponame
        self.assertTrue(os.path.isdir(os.path.join(
            self.temp_path, 'users', 'x', 'repositories', 'hello-world')))
        self.assertFalse(os.path.isdir(os.path.join(
            self.temp_path, 'users', 'x', 'repositories', 'Hello World!')))

        # The repo json file also uses slugify.
        self.assertTrue(os.path.isfile(os.path.join(
            self.temp_path, 'users', 'x', 'repositories', 'hello-world',
            'hello-world.json')))

        # Because of slugification, one can actually look up a yangset by
        # other strings:
        repo2 = self.cls('x', 'hello-world')
        self.assertEqual(repo1, repo2)
        repo3 = self.cls('x', 'Hello, world?')
        self.assertEqual(repo1, repo3)

        repo1.add_yang_files(self.test_dir, remove=False)

        # Check actual files in repository
        self.assertEqual(os.listdir(self.test_dir).remove('testrepo.json'),
                         os.listdir(repo1.path).remove('hello-world.json'))
        self.assertTrue(os.path.exists(os.path.join(
            repo1.path, 'ietf-inet-types@2010-09-24.yang')))
        self.assertTrue(os.path.exists(os.path.join(
            repo1.path, 'ietf-inet-types@2013-07-15.yang')))

        # Check reported repo contents too
        self.assertEqual([
            ("Cisco-IOS-XR-ipv4-bgp-datatypes", "2015-08-27"),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper", "2015-11-09"),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1", "2015-11-09"),
            ("Cisco-IOS-XR-lib-keychain-act", "2017-04-17"),
            ('Cisco-IOS-XR-lib-keychain-cfg', '2015-07-30'),
            ("Cisco-IOS-XR-types", "2015-06-29"),
            ("iana-if-type", "2015-06-12"),
            ("ietf-inet-types", "2010-09-24"),
            ("ietf-inet-types", "2013-07-15"),
            ("ietf-interfaces", "2014-05-08"),
            ("ietf-yang-types", "2010-09-24"),
            ("ietf-yang-types", "2013-07-15"),
            ("openconfig-if-ethernet", "2015-11-20"),
            ("openconfig-interfaces", "2015-11-20"),
        ], [m[:2] for m in sorted(repo1.modules)])

        self.assertGreater(repo1.mtime, initial_mtime)
        self.assertEqual(repo1.mtime, repo1.datastore_mtime)
        self.assertFalse(repo1.is_stale)
        self.assertTrue(repo2.is_stale)

        initial_mtime = repo1.mtime

        # Create a directory where repository expects to find a file
        os.makedirs(os.path.join(repo1.path, 'hammond@1918-06-22.yang'))

        result = repo1.remove_modules([
            ('ietf-inet-types', '2010-09-24'),   # file in repo
            ('ietf-inet-types', '1999-12-31'),   # file not in repo
            ('hammond', '1918-06-22'),           # directory, not file!
        ])
        self.assertEqual({
            'deleted': [('ietf-inet-types', '2010-09-24')],
            'module_errors': [
                ('ietf-inet-types', '1999-12-31', 'File not found'),
                ('hammond', '1918-06-22', 'File not found')],
            'yangset_errors': [],
        }, result)

        # Removed module is gone, other module(s) still present
        self.assertFalse(os.path.exists(os.path.join(
            repo1.path, 'ietf-inet-types@2010-09-24.yang')))
        self.assertTrue(os.path.exists(os.path.join(
            repo1.path, 'ietf-inet-types@2013-07-15.yang')))

        # Check repo contents are updated
        self.assertEqual([
            ("Cisco-IOS-XR-ipv4-bgp-datatypes", "2015-08-27"),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper", "2015-11-09"),
            ("Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1", "2015-11-09"),
            ("Cisco-IOS-XR-lib-keychain-act", "2017-04-17"),
            ('Cisco-IOS-XR-lib-keychain-cfg', '2015-07-30'),
            ("Cisco-IOS-XR-types", "2015-06-29"),
            ("iana-if-type", "2015-06-12"),
            ("ietf-inet-types", "2013-07-15"),
            ("ietf-interfaces", "2014-05-08"),
            ("ietf-yang-types", "2010-09-24"),
            ("ietf-yang-types", "2013-07-15"),
            ("openconfig-if-ethernet", "2015-11-20"),
            ("openconfig-interfaces", "2015-11-20"),
        ], [m[:2] for m in sorted(repo1.modules)])

        self.assertGreater(repo1.mtime, initial_mtime)
        self.assertEqual(repo1.mtime, repo1.datastore_mtime)
        self.assertFalse(repo1.is_stale)
        self.assertTrue(repo2.is_stale)

        # Delete repository
        # Here too, as long as the reponame slugifies, it's fine:
        self.cls.delete('x', 'Hello world?')
        self.assertFalse(os.path.exists(os.path.join(
            self.temp_path, 'users', 'x', 'repositories', 'hello-world')))

        # Already deleted - delete again raises error
        self.assertRaises(OSError, self.cls.delete, 'x', 'hello-world')

    def test_reponame_vs_dirname_filename(self):
        """Test translation from unicode reponames to ascii file/dir names."""
        # Create a working copy of our test repo
        shutil.rmtree(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)

        repo1 = self.cls.create('test', "♛ ⇒ h4, checkmate!")
        self.assertEqual(repo1.reponame, "♛ ⇒ h4, checkmate!")
        self.assertEqual(repo1.path, get_path('repository', user='test',
                                              reponame='h4-checkmate'))
        repo2 = self.cls('test', 'h4-checkmate')
        self.assertEqual(repo1, repo2)

    def test_equality(self):
        """Test equality checks; overrides TestYSYangSetBase test logic."""
        ys1 = self.cls("test", "testrepo")
        ys2 = self.cls("test", "testrepo")
        ys3 = self.cls("badfiles", "badrepo")

        self.assertTrue(ys1 == ys2)
        self.assertFalse(ys1 == ys3)

        # Check inverse as well for python 2's sake.
        self.assertFalse(ys1 != ys2)
        self.assertTrue(ys1 != ys3)

    def test_delete_negative(self):
        """Test failure modes of delete()."""
        # Create a working copy of our test repo
        shutil.rmtree(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)

        # Invalid arguments
        self.assertRaises(ValueError,
                          self.cls.delete, '', 'testrepo')
        self.assertRaises(ValueError, self.cls.delete, 'test', '')

        # Can't delete a repository that has associated yangsets
        self.assertRaises(RuntimeError,
                          self.cls.delete, 'test', 'testrepo')

    def test_remove_modules_negative(self):
        """Test failure modes of remove_modules()."""
        # Create a working copy of our test repo
        shutil.rmtree(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)

        repo = self.cls('test', 'testrepo')
        results = repo.remove_modules([
            ('iana-if-type', '2010-01-01'),   # revision not in repository
            ('Cisco-IOS-XR-ipv4-bgp-oc-oper', '2015-11-09'),  # used by xrbgpv4
        ])
        self.assertEqual({
            'deleted': [],
            'module_errors': [
                ('iana-if-type', '2010-01-01', 'File not found'),
            ],
            'yangset_errors': [
                ('xrbgpv4', [('Cisco-IOS-XR-ipv4-bgp-oc-oper', '2015-11-09')]),
            ],
        }, results)

    def test_validate_prefix_collision(self):
        """Verify that colliding module prefixes are detected."""
        repo = self.cls('badfiles', 'prefixcollision')
        self.maxDiff = None
        self.assertEqual([
            {
                'name': 'anotherchild',
                'revision': '1999-12-31',
                'found': True,
                'in_yangset': True,
                'usable': True,
                'warnings': [],
                'errors': [],
            },
            {
                'name': 'child',
                'revision': '2018-06-13',
                'found': True,
                'in_yangset': True,
                'usable': True,
                'warnings': [],
                'errors': [],
            },
            {
                'name': 'oldgrandchild',
                'revision': '1999-12-31',
                'found': True,
                'in_yangset': True,
                'usable': True,
                'warnings': [],
                'errors': [],
            },
            {
                'name': 'parent',
                'revision': '2018-06-13',
                'found': True,
                'in_yangset': True,
                'usable': True,
                'warnings': [],
                'errors': ['Prefix collision: This module or its dependencies '
                           'import both "child" and "oldgrandchild" under the '
                           'same prefix "child", but each prefix MUST '
                           'uniquely identify a single module. '
                           'One possible cause is using the wrong revision(s) '
                           "of this module's dependencies."],
            },
        ], repo.validate())

    def test_repository_update_marks_yangsets_as_stale(self):
        """When a repository gets updated YANG modules, yangsets may be stale.

        YANG sets not using the updated modules are not stale.
        """
        # Create a working copy of our test repo
        shutil.rmtree(self.temp_path)
        shutil.copytree(self.base_dir, self.temp_path)
        set_base_path(self.temp_path)

        repo = self.cls('test', 'testrepo')
        initial_repo_mtime = repo.mtime
        ys = YSYangSet.load('test', 'xrbgpv4')
        initial_ys_mtime = ys.mtime
        # Import an "updated" Cisco-IOS-XR-ipv4-bgp-oc-oper module,
        # with new contents but the same revision date.
        # This is what might occur as a developer is actively developing
        # a YANG module.
        newfile = os.path.join(os.path.dirname(__file__),
                               '..',
                               '..',
                               'tests',
                               "Cisco-IOS-XR-ipv4-bgp-oc-oper@2015-11-09.yang")
        repo.add_yang_files(newfile, remove=False)
        self.assertGreater(repo.mtime, initial_repo_mtime)
        self.assertGreater(repo.datastore_mtime, initial_repo_mtime)
        self.assertFalse(repo.is_stale)

        # Yangset instance is now stale
        self.assertEqual(ys.mtime, initial_ys_mtime)
        self.assertGreater(ys.datastore_mtime, initial_ys_mtime)
        self.assertTrue(ys.is_stale)

import unittest2 as unittest
import filecmp
import os
import tempfile
import shutil

from yangsuite.paths import set_base_path, get_path

from ..utility import (
    list_yang_files,
    report_yang_files,
    migrate_yang_files,
    atomic_create,
    user_status,
    do_validation,
    validation_status,
)
from ..yangset import YSYangSet


class TestFilemanagerUtility(unittest.TestCase):
    """Test generic APIs not specific to a class."""

    # ysfilemanager/filemanager/tests/x --> ysfilemanager/tests/data
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'tests', 'data')
    test_dir = os.path.join(base_dir,
                            'users', 'test', 'repositories', 'testrepo')

    def setUp(self):
        """Pre-test setup function, called automatically."""
        self.test_yang_files = [os.path.join(self.test_dir, f)
                                for f in os.listdir(self.test_dir)
                                if f.endswith('.yang')]
        set_base_path(self.base_dir)
        self.temp_path = tempfile.mkdtemp()

    def tearDown(self):
        """Post-test cleanup function, called automatically."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_list_yang_files(self):
        """Exercise the list_yang_files() API."""
        # Find in a directory
        result = list_yang_files(self.test_dir)
        self.assertNotEqual(0, len(result))
        self.assertEqual(len(self.test_yang_files), len(result))

        # Find a single file
        result = list_yang_files(self.test_yang_files[0])
        self.assertEqual([self.test_yang_files[0]], result)

        # Find from multiple sources
        extra_dir = get_path('repository', user='badfiles', reponame='badrepo')
        result = list_yang_files([self.test_dir, extra_dir])
        self.assertGreater(len(result), len(self.test_yang_files))
        self.assertEqual(len(result), (len(self.test_yang_files) +
                                       len(list_yang_files(extra_dir))))

        # Garbage input
        self.assertRaises(TypeError, list_yang_files, None)

        # Find a nonexistent path
        self.assertRaises(OSError, list_yang_files, '/foo/bar/')
        self.assertRaises(OSError, list_yang_files, u'/foo/bar/')

        # Find a file that's not a YANG file or directory
        self.assertRaises(ValueError, list_yang_files, __file__)

    def test_report_yang_files(self):
        """Exercise the report_yang_files() API."""
        result = report_yang_files(self.test_dir)

        self.maxDiff = None
        self.assertEqual(
            [
                ('Cisco-IOS-XR-ipv4-bgp-datatypes', '2015-08-27',
                 'Cisco-IOS-XR-ipv4-bgp-datatypes@2015-08-27.yang'),
                ('Cisco-IOS-XR-ipv4-bgp-oc-oper', '2015-11-09',
                 'Cisco-IOS-XR-ipv4-bgp-oc-oper@2015-11-09.yang'),
                ('Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1', '2015-11-09',
                 'Cisco-IOS-XR-ipv4-bgp-oc-oper-sub1@2015-11-09.yang'),
                ('Cisco-IOS-XR-lib-keychain-act', '2017-04-17',
                 'Cisco-IOS-XR-lib-keychain-act@2017-04-17.yang'),
                ('Cisco-IOS-XR-lib-keychain-cfg',
                 '2015-07-30',
                 'Cisco-IOS-XR-lib-keychain-cfg@2015-07-30.yang'),
                ('Cisco-IOS-XR-types', '2015-06-29',
                 'Cisco-IOS-XR-types@2015-06-29.yang'),
                ('iana-if-type', '2015-06-12',
                 'iana-if-type@2015-06-12.yang'),
                ('ietf-inet-types', '2010-09-24',
                 'ietf-inet-types@2010-09-24.yang'),
                ('ietf-inet-types', '2013-07-15',
                 'ietf-inet-types@2013-07-15.yang'),
                ('ietf-interfaces', '2014-05-08',
                 'ietf-interfaces@2014-05-08.yang'),
                ('ietf-yang-types', '2010-09-24',
                 'ietf-yang-types@2010-09-24.yang'),
                ('ietf-yang-types', '2013-07-15',
                 'ietf-yang-types@2013-07-15.yang'),
                ('openconfig-if-ethernet', '2015-11-20',
                 'openconfig-if-ethernet@2015-11-20.yang'),
                ('openconfig-interfaces', '2015-11-20',
                 'openconfig-interfaces@2015-11-20.yang'),
            ],
            result)

        result = report_yang_files(__file__)
        self.assertEqual([], result)

    def test_migrate_yang_files(self):
        """Exercise the migrate_yang_files function."""
        dir1 = os.path.join(self.temp_path, "dir1")
        os.makedirs(dir1)
        dir2 = os.path.join(self.temp_path, "dir2")
        os.makedirs(dir2)
        dir3 = os.path.join(self.temp_path, "dir3")
        os.makedirs(dir3)

        with open(os.path.join(dir1, "alpha.yang"), "w") as fd:
            fd.write("""
module alpha {
    revision 1001-01-01 {
        description "The first";
    }
}""")

        with open(os.path.join(dir1, "beta.yang"), "w") as fd:
            fd.write("""
module beta {
}""")

        with open(os.path.join(dir2, "alpha.yang"), "w") as fd:
            fd.write("""
module alpha {
    revision 2001-01-01 {
        description "The second";
    }
    revision 1001-01-01 {
        description "The first";
    }
}""")

        with open(os.path.join(dir2, "beta.yang"), "w") as fd:
            fd.write("""
module beta {
}""")

        # Migrate without remove
        result = migrate_yang_files(dir1, dir3, remove=False)
        self.assertEqual({
            'added': [('alpha', '1001-01-01'), ('beta', 'unknown')],
            'updated': [],
            'unchanged': [],
            'errors': [],
        }, result)
        self.assertEqual(['alpha.yang', 'beta.yang'], sorted(os.listdir(dir1)))
        self.assertEqual(['alpha@1001-01-01.yang', 'beta.yang'],
                         sorted(os.listdir(dir3)))

        # Migrate again - no changes
        result = migrate_yang_files(dir1, dir3, remove=False)
        self.assertEqual({
            'added': [],
            'updated': [],
            'unchanged': [('alpha', '1001-01-01'), ('beta', 'unknown')],
            'errors': [],
        }, result)
        self.assertEqual(['alpha.yang', 'beta.yang'], sorted(os.listdir(dir1)))
        self.assertEqual(['alpha@1001-01-01.yang', 'beta.yang'],
                         sorted(os.listdir(dir3)))

        # Migrate from another directory, some new, some unchanged
        # Remove source files regardless (default remove value)
        result = migrate_yang_files(dir2, dir3)
        self.assertEqual({
            'added': [('alpha', '2001-01-01')],
            'updated': [],
            'unchanged': [('beta', 'unknown')],
            'errors': [],
        }, result)
        self.assertEqual([], os.listdir(dir2))
        self.assertEqual(['alpha@1001-01-01.yang', 'alpha@2001-01-01.yang',
                          'beta.yang'], sorted(os.listdir(dir3)))

        # File differs from already present in dest
        with open(os.path.join(dir1, 'alpha.yang'), 'a') as fd:
            fd.write("//Added comment here")
        result = migrate_yang_files(dir1, dir3, remove=False)
        self.assertEqual({
            'added': [],
            'updated': [('alpha', '1001-01-01')],
            'unchanged': [('beta', 'unknown')],
            'errors': [],
        }, result)
        # Make sure dir3 actually got updated with the new alpha file
        self.assertTrue(filecmp.cmp(
            os.path.join(dir1, 'alpha.yang'),
            os.path.join(dir3, 'alpha@1001-01-01.yang')))

        # Invalid dest
        result = migrate_yang_files(dir3, __file__, remove=False)
        self.assertEqual({
            'added': [],
            'updated': [],
            'unchanged': [],
            'errors': [(__file__, "No such directory")],
        }, result)

    def test_atomic_create(self):
        """Exercise the atomic_create context manager."""
        atomicfile = os.path.join(self.temp_path, 'nukular')

        with self.assertRaises(RuntimeError):
            with atomic_create(atomicfile, reraise=True) as fd:
                fd.write("Hello")
                raise RuntimeError
                fd.write("Goodbye")
        self.assertFalse(os.path.exists(atomicfile))

        with atomic_create(atomicfile, reraise=False) as fd:
            fd.write("Hello")
            raise RuntimeError
            fd.write("Goodbye")
        self.assertFalse(os.path.exists(atomicfile))

        with atomic_create(atomicfile, reraise=True) as fd:
            fd.write("Hello")
            fd.write("Goodbye")
        self.assertTrue(os.path.exists(atomicfile))

        # File can't be created (no such directory) - make sure it is safe too
        nuclearfile = os.path.join(atomicfile, 'nuclear')
        with self.assertRaises(RuntimeError):
            with atomic_create(nuclearfile, reraise=False) as fd:
                fd.write("Hello")
        self.assertFalse(os.path.exists(nuclearfile))

        with atomic_create(atomicfile, reraise=False) as fd:
            os.remove(atomicfile)
            raise RuntimeError
        self.assertFalse(os.path.exists(atomicfile))

    def test_do_validation(self):
        """Exercise the do_validation view helper function."""
        ys = YSYangSet.load('test', 'xrbgpv4')

        reply = do_validation('someuser', ys, quick=True)
        self.assertEqual(reply['reply'], ys.validate())
        self.assertNotIn('someuser', user_status)

    def test_validation_status(self):
        """Exercise the validation_status view helper function."""
        # No request in progress
        self.assertNotIn('someuser', user_status)
        result = validation_status('someuser')
        self.assertEqual(result['value'], 0)
        self.assertEqual(result['max'], 0)
        self.assertEqual(result['info'], "No request in progress")

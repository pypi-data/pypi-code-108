#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_OSTOOLS.PY -- test script for OSTOOLS module
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the OSTOOLS module in the
PLIB3.STDLIB sub-package.
"""

import os
import unittest
from tempfile import mkdtemp
from shutil import rmtree

from plib.stdlib.ostools import (
    tmp_chdir, locate, subdirs, dirfinder, filefinder, data_changed
)


def touch(filename):
    with open(filename, 'w'):
        pass


def create_tree(tree, rootpath):
    for item in tree:
        if isinstance(item, tuple):
            dirname, subtree = item
            dirpath = os.path.join(rootpath, dirname)
            os.mkdir(dirpath)
            create_tree(subtree, dirpath)
        else:
            touch(os.path.join(rootpath, item))


test_tree = (
    ("one", ()),
    ("two", (
        ("there", ()),
        ("another", (
            ("there", ()),
        ))
    )),
    ("three", (
        "there",
    )),
    "there",
    (".hidden", ())
)


class TestFileFunctions(unittest.TestCase):
    
    def setUp(self):
        # Create temporary file structure for testing
        self.tmpdir = mkdtemp()
        create_tree(test_tree, self.tmpdir)
    
    def tearDown(self):
        # Remove temporary file structure
        rmtree(self.tmpdir, ignore_errors=True)
    
    def _tmp_chdir_create(self, create):
        # Helper function, part of class so it can easily access self.tempdir
        created_dir = os.path.join(self.tmpdir, "one", "created")
        with tmp_chdir(created_dir, create):
            return os.getcwd() == created_dir
    
    def test_functions(self):
        with tmp_chdir(self.tmpdir):
            self.assertEqual(os.getcwd(), self.tmpdir)
            
            self.assertEqual(sorted(subdirs()),
                             ["one", "three", "two"])
            self.assertEqual(sorted(subdirs(include_hidden=True)),
                             [".hidden", "one", "three", "two"])
            self.assertEqual(sorted(subdirs(fullpath=True)),
                             [os.path.join(self.tmpdir, d)
                             for d in ("one", "three", "two")])
            
            self.assertEqual(sorted(locate("t*")),
                             [os.path.join(self.tmpdir, d)
                             for d in ("there",
                                       os.path.join("three", "there"))])
            self.assertEqual(sorted(locate("t*", include_dirs=True)),
                             [os.path.join(self.tmpdir, d)
                             for d in ("there",
                                       "three",
                                       os.path.join("three", "there"),
                                       "two",
                                       os.path.join("two", "another", "there"),
                                       os.path.join("two", "there"))])
            
            self.assertEqual(sorted(dirfinder(("there",))),
                             [os.path.join(self.tmpdir, "two")])
            self.assertEqual(sorted(dirfinder(("there",), recurse=True)),
                             [os.path.join(self.tmpdir, d)
                             for d in ("two",
                                       os.path.join("two", "another"))])
            
            self.assertEqual(sorted(filefinder(("there",))),
                             [self.tmpdir])
            self.assertEqual(sorted(filefinder(("there",), recurse=True)),
                             [self.tmpdir,
                             os.path.join(self.tmpdir, "three")])
        
        # Make sure tmp_chdir doesn't create unless we tell it to
        self.assertRaises(OSError, self._tmp_chdir_create, False)
        
        # Do these after the above since they change the file tree structure
        self.assertTrue(self._tmp_chdir_create(True))
        
        tmpfile = os.path.join(self.tmpdir, "tmpfile")
        tmpdata = "Test data"
        altdata = tmpdata.replace(' ', '.')
        
        # Data must be changed if the file doesn't exist yet!
        self.assertTrue(data_changed(tmpdata.encode(), tmpfile))
        
        with open(tmpfile, 'wb') as f:
            f.write(tmpdata.encode())
        
        # No change
        self.assertFalse(data_changed(tmpdata.encode(), tmpfile))
        # Note that the test data must be bytes, not string, otherwise
        # we get false positives (data_changed always uses byte
        # comparison since that's how the file data is stored)
        self.assertTrue(data_changed(tmpdata, tmpfile))
        
        # Size change in data
        self.assertTrue(data_changed("{}{}".format(tmpdata, tmpdata).encode(), tmpfile))
        
        # Same size but different data
        self.assertEqual(len(altdata.encode()), os.stat(tmpfile).st_size)
        self.assertTrue(data_changed(altdata.encode(), tmpfile))
        
        with open(tmpfile, 'ab') as f:
            f.write(tmpdata.encode())
        
        # Size change in file
        self.assertEqual(os.stat(tmpfile).st_size, len(tmpdata.encode()) * 2)
        self.assertTrue(data_changed(tmpdata.encode(), tmpfile))
        
        with open(tmpfile, 'wb') as f:
            f.write(altdata.encode())
        
        # Same size but different data in file
        self.assertEqual(os.stat(tmpfile).st_size, len(tmpdata.encode()))
        self.assertTrue(data_changed(tmpdata.encode(), tmpfile))


if __name__ == '__main__':
    unittest.main()

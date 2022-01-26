#!/usr/bin/python
"""\
@file   test_replacefile.py
@author Nat Goodspeed
@date   2011-04-13
@brief  Test replacefile.py

Copyright (c) 2011, Nat Goodspeed
"""

from __future__ import with_statement   # for Python 2.5
from __future__ import print_function

import os
import sys
import errno
import tempfile
import unittest
from ..replacefile import ReplaceFile

class BogusError(Exception):
    pass

class TestReplaceFile(unittest.TestCase):
    def setUp(self):
        self.name = "foo.txt"
        self.content = "a\nb\nc\n"
        self.updated = "d\ne\nf\n"
        self.tempdir = tempfile.gettempdir()
        self.origtempfiles = set(os.listdir(self.tempdir))
        self.path = os.path.join(self.tempdir, self.name)
        f = open(self.path, "w")
        f.write(self.content)
        f.close()
        self.tempfiles = set(os.listdir(self.tempdir))

    def tearDown(self):
        for fn in set(os.listdir(self.tempdir)) - self.origtempfiles:
            fp = os.path.join(self.tempdir, fn)
            try:
                os.remove(fp)
            except OSError as err:
                if err.errno != errno.ENOENT:
                    print("*** Couldn't remove:", fp, file=sys.stderr)
                    # but continue because we've got more to clean up

    def test_no_existing_file(self):
        notthere = os.path.join(self.tempdir, "notthere.txt")
        # no exception...
        ReplaceFile(notthere)
        try:
            with ReplaceFile(notthere):
                pass
            self.fail("expecting exception on ReplaceFile(%s)" % notthere)
        except:
            pass

    def test_no_newext_no_oldext_commit(self):
        with ReplaceFile(self.path) as (inf, outf):
            # with no newext, have to figure out new file's name indirectly
            # (only check this in one no-newext test)
            newfiles = self.newfiles()
            self.assertEquals(len(newfiles), 1)
            newfile = newfiles.pop()
            ## print "created", newfile
            assert not newfile.startswith(self.name)
            # verify that 'inf' is in fact our original file (only check this
            # in one test)
            self.assertEquals(inf.read(), self.content)
            # every test should change outf
            outf.write(self.updated)
        self.verify(self.updated)       # new data saved

    def test_no_newext_no_oldext_exc(self):
        try:
            with ReplaceFile(self.path) as (inf, outf):
                outf.write(self.updated)
                # The flush() call is in case doubters scoff, "Oh, well, the
                # original file was preserved only because you raised an
                # exception before that tiny write got flushed." We only need
                # this for no-newext-exc tests: with newext, we directly
                # checkfile() the newext content, even without the flush().
                outf.flush()
                raise BogusError("oh oh")
        except BogusError:
            pass
        self.verify(self.content)       # original file preserved

    def test_no_newext_yes_oldext_commit(self):
        with ReplaceFile(self.path, oldext=".bak") as (inf, outf):
            outf.write(self.updated)
        self.verify(self.updated, set([self.name + ".bak"]))
        self.checkfile(self.path + ".bak", self.content)
        # before we clean all this up, replace the file AGAIN, forcing us to
        # remove previous .bak
        third = "g\nh\ni\n"
        with ReplaceFile(self.path, oldext=".bak") as (inf, outf):
            outf.write(third)
        self.verify(third, set([self.name + ".bak"]))
        self.checkfile(self.path + ".bak", self.updated)

    def test_no_newext_yes_oldext_exc(self):
        try:
            with ReplaceFile(self.path, oldext=".bak") as (inf, outf):
                outf.write(self.updated)
                outf.flush()
                raise BogusError("oh oh")
        except BogusError:
            pass
        # oldext is simply moot on exception
        self.verify(self.content)       # original file preserved

    def test_yes_newext_no_oldext_commit(self):
        with ReplaceFile(self.path, newext=".new") as (inf, outf):
            newfiles = self.newfiles()
            self.assertEquals(len(newfiles), 1)
            newfile = newfiles.pop()
            self.assertEquals(newfile, self.name + ".new")
            outf.write(self.updated)
        # newext should be promoted on normal commit
        self.verify(self.updated)

    def test_yes_newext_no_oldext_exc(self):
        try:
            with ReplaceFile(self.path, newext=".new") as (inf, outf):
                outf.write(self.updated)
                raise BogusError("oh oh")
        except BogusError:
            pass
        # original file preserved, also newext
        self.verify(self.content, set([self.name + ".new"]))
        self.checkfile(self.path + ".new", self.updated)

    def test_yes_newext_yes_oldext_commit(self):
        with ReplaceFile(self.path, oldext=".bak", newext=".new") as (inf, outf):
            newfiles = self.newfiles()
            self.assertEquals(len(newfiles), 1)
            newfile = newfiles.pop()
            self.assertEquals(newfile, self.name + ".new")
            outf.write(self.updated)
        # newext should be promoted on normal commit
        self.verify(self.updated, set([self.name + ".bak"]))
        self.checkfile(self.path + ".bak", self.content)

    def test_yes_newext_yes_oldext_exc(self):
        try:
            with ReplaceFile(self.path, oldext=".bak", newext=".new") as (inf, outf):
                outf.write(self.updated)
                raise BogusError("oh oh")
        except BogusError:
            pass
        # oldext is simply moot on exception
        self.verify(self.content, set([self.name + ".new"])) # original file preserved
        self.checkfile(self.path + ".new", self.updated)

    def newfiles(self):
        return set(os.listdir(self.tempdir)) - self.tempfiles

    def verify(self, content, extra=set()):
        self.checkfile(self.path, content)
        self.assertEquals(self.newfiles(), extra)

    def checkfile(self, name, content):
        f = open(name)
        data = f.read()
        f.close()
        self.assertEquals(data, content)

if __name__ == "__main__":
    unittest.main()

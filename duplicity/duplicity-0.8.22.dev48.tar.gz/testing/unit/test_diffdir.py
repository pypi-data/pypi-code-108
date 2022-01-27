from __future__ import print_function
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object

import os
import unittest

from duplicity import diffdir
from duplicity import selection
from duplicity import tarfile
from duplicity import util
from duplicity.path import *  # pylint: disable=unused-wildcard-import,redefined-builtin
from testing import _runtest_dir
from . import UnitTestCase


class DDTest(UnitTestCase):
    u"""Test functions in diffdir.py"""
    def setUp(self):
        super(DDTest, self).setUp()
        self.unpack_testfiles()

    def copyfileobj(self, infp, outfp):
        u"""Copy in fileobj to out, closing afterwards"""
        blocksize = 32 * 1024
        while 1:
            buf = infp.read(blocksize)
            if not buf:
                break
            outfp.write(buf)
        assert not infp.close()
        assert not outfp.close()

    def testsig(self):
        u"""Test producing tar signature of various file types"""
        select = selection.Select(Path(u"{0}/testfiles/various_file_types".format(_runtest_dir)))
        select.set_iter()
        sigtar = diffdir.SigTarBlockIter(select)
        diffdir.write_block_iter(sigtar, u"{0}/testfiles/output/sigtar".format(_runtest_dir))

        i = 0
        for tarinfo in tarfile.TarFile(u"{0}/testfiles/output/sigtar".format(_runtest_dir), u"r"):
            i += 1
        assert i >= 5, u"There should be at least 5 files in sigtar"

    def empty_diff_schema(self, dirname):
        u"""Given directory name, make sure can tell when nothing changes"""
        select = selection.Select(Path(dirname))
        select.set_iter()
        sigtar = diffdir.SigTarBlockIter(select)
        diffdir.write_block_iter(sigtar, u"{0}/testfiles/output/sigtar".format(_runtest_dir))

        sigtar_fp = open(u"{0}/testfiles/output/sigtar".format(_runtest_dir), u"rb")
        select2 = selection.Select(Path(dirname))
        select2.set_iter()
        diffdir.write_block_iter(diffdir.DirDelta(select2, sigtar_fp),
                                 u"{0}/testfiles/output/difftar".format(_runtest_dir))

        size = os.stat(u"{0}/testfiles/output/difftar".format(_runtest_dir)).st_size
        assert size == 0 or size == 10240, size  # 10240 is size of one record
        if size != 0:
            fin = open(u"{0}/testfiles/output/difftar".format(_runtest_dir), u"rb")
            diff_buf = fin.read()
            assert not fin.close()
            assert diff_buf == b'\0' * 10240

    def test_empty_diff(self):
        u"""Test producing a diff against same sig; should be len 0"""
        self.empty_diff_schema(u"{0}/testfiles/various_file_types".format(_runtest_dir))

        select = selection.Select(Path(u"{0}/testfiles/various_file_types".format(_runtest_dir)))
        select.set_iter()
        sigtar = diffdir.SigTarBlockIter(select)
        diffdir.write_block_iter(sigtar, u"{0}/testfiles/output/sigtar".format(_runtest_dir))

        sigtar_fp = open(u"{0}/testfiles/output/sigtar".format(_runtest_dir), u"rb")
        select2 = selection.Select(Path(u"{0}/testfiles/various_file_types".format(_runtest_dir)))
        select2.set_iter()
        diffdir.write_block_iter(diffdir.DirDelta(select2, sigtar_fp),
                                 u"{0}/testfiles/output/difftar".format(_runtest_dir))

        size = os.stat(u"{0}/testfiles/output/difftar".format(_runtest_dir)).st_size
    
    def test_empty_diff2(self):
        u"""Test producing diff against directories of special files"""
        self.empty_diff_schema(u"{0}/testfiles/special_cases/neg_mtime".format(_runtest_dir))
        self.empty_diff_schema(u"{0}/testfiles/special_cases/no_uname".format(_runtest_dir))

    def test_diff(self):
        u"""Test making a diff"""
        sel1 = selection.Select(Path(u"{0}/testfiles/dir1".format(_runtest_dir)))
        diffdir.write_block_iter(diffdir.SigTarBlockIter(sel1.set_iter()),
                                 u"{0}/testfiles/output/dir1.sigtar".format(_runtest_dir))

        sigtar_fp = open(u"{0}/testfiles/output/dir1.sigtar".format(_runtest_dir), u"rb")
        sel2 = selection.Select(Path(u"{0}/testfiles/dir2".format(_runtest_dir)))
        delta_tar = diffdir.DirDelta(sel2.set_iter(), sigtar_fp)
        diffdir.write_block_iter(delta_tar,
                                 u"{0}/testfiles/output/dir1dir2.difftar".format(_runtest_dir))

        changed_files = [u"diff/changeable_permission",
                         u"diff/regular_file",
                         u"snapshot/symbolic_link/",
                         u"deleted/deleted_file",
                         u"snapshot/directory_to_file",
                         u"snapshot/file_to_directory/"]
        for tarinfo in tarfile.TarFile(u"{0}/testfiles/output/dir1dir2.difftar".format(_runtest_dir),
                                       u"r"):
            tiname = util.get_tarinfo_name(tarinfo)
            if tiname in changed_files:
                changed_files.remove(tiname)
        assert not changed_files, (u"Following files not found:\n"
                                   + u"\n".join(changed_files))

    def test_diff2(self):
        u"""Another diff test - this one involves multivol support
        (requires rdiff to be installed to pass)"""
        sel1 = selection.Select(Path(u"{0}/testfiles/dir2".format(_runtest_dir)))
        diffdir.write_block_iter(diffdir.SigTarBlockIter(sel1.set_iter()),
                                 u"{0}/testfiles/output/dir2.sigtar".format(_runtest_dir))

        sigtar_fp = open(u"{0}/testfiles/output/dir2.sigtar".format(_runtest_dir), u"rb")
        sel2 = selection.Select(Path(u"{0}/testfiles/dir3".format(_runtest_dir)))
        delta_tar = diffdir.DirDelta(sel2.set_iter(), sigtar_fp)
        diffdir.write_block_iter(delta_tar,
                                 u"{0}/testfiles/output/dir2dir3.difftar".format(_runtest_dir))

        buffer = b""
        tf = tarfile.TarFile(u"{0}/testfiles/output/dir2dir3.difftar".format(_runtest_dir), u"r")
        for tarinfo in tf:
            if tarinfo.name.startswith(r"multivol_diff/"):
                buffer += tf.extractfile(tarinfo).read()
        assert 3000000 < len(buffer) < 4000000
        fout = open(u"{0}/testfiles/output/largefile.delta".format(_runtest_dir), u"wb")
        fout.write(buffer)
        fout.close()
        assert not os.system(u"rdiff patch {0}/testfiles/dir2/largefile ".format(_runtest_dir) +
                             u"{0}/testfiles/output/largefile.delta ".format(_runtest_dir) +
                             u"{0}/testfiles/output/largefile.patched".format(_runtest_dir))
        dir3large = open(u"{0}/testfiles/dir3/largefile".format(_runtest_dir), u"rb").read()
        patchedlarge = open(u"{0}/testfiles/output/largefile.patched".format(_runtest_dir), u"rb").read()
        assert dir3large == patchedlarge

    def test_dirdelta_write_sig(self):
        u"""Test simultaneous delta and sig generation

        Generate signatures and deltas of dirs1, 2, 3, 4 and compare
        those produced by DirDelta_WriteSig and other methods.

        """
        deltadir1 = Path(u"{0}/testfiles/output/dir.deltatar1".format(_runtest_dir))
        deltadir2 = Path(u"{0}/testfiles/output/dir.deltatar2".format(_runtest_dir))
        cur_full_sigs = Path(u"{0}/testfiles/output/fullsig.dir1".format(_runtest_dir))

        cur_dir = Path(u"{0}/testfiles/dir1".format(_runtest_dir))
        get_sel = lambda cur_dir: selection.Select(cur_dir).set_iter()
        diffdir.write_block_iter(diffdir.SigTarBlockIter(get_sel(cur_dir)),
                                 cur_full_sigs)

        sigstack = [cur_full_sigs]
        for dirname in [u'dir2', u'dir3', u'dir4']:
            # print "Processing ", dirname
            old_dir = cur_dir
            cur_dir = Path(u"{0}/testfiles/".format(_runtest_dir) + dirname)

            old_full_sigs = cur_full_sigs
            cur_full_sigs = Path(u"{0}/testfiles/output/fullsig.".format(_runtest_dir) + dirname)

            delta1 = Path(u"{0}/testfiles/output/delta1.".format(_runtest_dir) + dirname)
            delta2 = Path(u"{0}/testfiles/output/delta2.".format(_runtest_dir) + dirname)
            incsig = Path(u"{0}/testfiles/output/incsig.".format(_runtest_dir) + dirname)

            # Write old-style delta to deltadir1
            diffdir.write_block_iter(diffdir.DirDelta(get_sel(cur_dir),
                                                      old_full_sigs.open(u"rb")),
                                     delta1)

            # Write new signature and delta to deltadir2 and sigdir2, compare
            block_iter = diffdir.DirDelta_WriteSig(
                get_sel(cur_dir),
                [p.open(u"rb") for p in sigstack],
                incsig.open(u"wb"))
            sigstack.append(incsig)
            diffdir.write_block_iter(block_iter, delta2)

            # print delta1.name, delta2.name
            compare_tar(delta1.open(u"rb"), delta2.open(u"rb"))
            assert not os.system(u"cmp %s %s" % (delta1.uc_name, delta2.uc_name))

            # Write old-style signature to cur_full_sigs
            diffdir.write_block_iter(diffdir.SigTarBlockIter(get_sel(cur_dir)),
                                     cur_full_sigs)

    def test_combine_path_iters(self):
        u"""Test diffdir.combine_path_iters"""
        class Dummy(object):
            def __init__(self, index, other=None):
                self.index = index
                self.other = other

            def __repr__(self):
                return u"(%s %s)" % (self.index, self.other)

        def get_iter1():
            yield Dummy(())
            yield Dummy((1,))
            yield Dummy((1, 5), 2)

        def get_iter2():
            yield Dummy((), 2)
            yield Dummy((1, 5))
            yield Dummy((2,))

        def get_iter3():
            yield Dummy((), 3)
            yield Dummy((2,), 1)

        result = diffdir.combine_path_iters([get_iter1(),
                                             get_iter2(),
                                             get_iter3()])
        elem1 = next(result)
        assert elem1.index == () and elem1.other == 3, elem1
        elem2 = next(result)
        assert elem2.index == (1,) and elem2.other is None, elem2
        elem3 = next(result)
        assert elem3.index == (1, 5) and elem3.other is None
        elem4 = next(result)
        assert elem4.index == (2,) and elem4.other == 1
        try:
            elem5 = next(result)
        except StopIteration:
            pass
        else:
            assert 0, elem5


def compare_tar(tarfile1, tarfile2):
    u"""Compare two tarfiles"""
    tf1 = tarfile.TarFile(u"none", u"r", tarfile1)
    tf2 = tarfile.TarFile(u"none", u"r", tarfile2)
    tf2_iter = iter(tf2)

    for ti1 in tf1:
        try:
            ti2 = next(tf2_iter)
        except StopIteration:
            assert 0, (u"Premature end to second tarfile, "
                       u"ti1.name = %s" % ti1.name)
        # print "Comparing ", ti1.name, ti2.name
        assert tarinfo_eq(ti1, ti2), u"%s %s" % (ti1.name, ti2.name)
        if ti1.size != 0:
            fp1 = tf1.extractfile(ti1)
            buf1 = fp1.read()
            fp1.close()
            fp2 = tf2.extractfile(ti2)
            buf2 = fp2.read()
            fp2.close()
            assert buf1 == buf2
    try:
        ti2 = next(tf2_iter)
    except StopIteration:
        pass
    else:
        assert 0, (u"Premature end to first tarfile, "
                   u"ti2.name = %s" % ti2.name)

    tarfile1.close()
    tarfile2.close()


def tarinfo_eq(ti1, ti2):
    if ti1.name != ti2.name:
        print(u"Name:", ti1.name, ti2.name)
        return 0
    if ti1.size != ti2.size:
        print(u"Size:", ti1.size, ti2.size)
        return 0
    if ti1.mtime != ti2.mtime:
        print(u"Mtime:", ti1.mtime, ti2.mtime)
        return 0
    if ti1.mode != ti2.mode:
        print(u"Mode:", ti1.mode, ti2.mode)
        return 0
    if ti1.type != ti2.type:
        print(u"Type:", ti1.type, ti2.type)
        return 0
    if ti1.issym() or ti1.islnk():
        if ti1.linkname != ti2.linkname:
            print(u"Linkname:", ti1.linkname, ti2.linkname)
            return 0
    if ti1.uid != ti2.uid or ti1.gid != ti2.gid:
        print(u"IDs:", ti1.uid, ti2.uid, ti1.gid, ti2.gid)
        return 0
    if ti1.uname != ti2.uname or ti1.gname != ti2.gname:
        print(u"Owner names:", ti1.uname, ti2.uname, ti1.gname, ti2.gname)
        return 0
    return 1

if __name__ == u"__main__":
    unittest.main()

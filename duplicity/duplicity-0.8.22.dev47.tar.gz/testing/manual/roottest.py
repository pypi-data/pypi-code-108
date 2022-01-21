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

import config
import sys, unittest
sys.path.insert(0, u"../")

from duplicity import diffdir
from duplicity import patchdir
from duplicity import selection
from duplicity.path import *  # pylint: disable=unused-wildcard-import,redefined-builtin

config.setup()

class RootTest(unittest.TestCase):
    u"""Test doing operations that only root can"""

    def setUp(self):
        # must run with euid/egid of root
        assert(os.geteuid() == 0)
        # make sure uid/gid match euid/egid
        os.setuid(os.geteuid())
        os.setgid(os.getegid())
        assert not os.system(u"tar xzf manual/rootfiles.tar.gz > /dev/null 2>&1")

    def tearDown(self):
        assert not os.system(u"rm -rf /tmp/testfiles tempdir temp2.tar")

    def copyfileobj(self, infp, outfp):
        u"""Copy in fileobj to out, closing afterwards"""
        blocksize = 32 * 1024
        while 1:
            buf = infp.read(blocksize)
            if not buf: break
            outfp.write(buf)
        assert not infp.close()
        assert not outfp.close()

    def deltmp(self):
        u"""Delete temporary directories"""
        assert not os.system(u"rm -rf /tmp/testfiles/output")
        os.mkdir(u"/tmp/testfiles/output")

    def get_sel(self, path):
        u"""Get selection iter over the given directory"""
        return selection.Select(path).set_iter()

    def total_sequence(self, filelist):
        u"""Test signatures, diffing, and patching on directory list"""
        assert len(filelist) >= 2
        self.deltmp()
        assert not os.system(u"cp -pR %s /tmp/testfiles/output/sequence" %
                             (filelist[0],))
        seq_path = Path(u"/tmp/testfiles/output/sequence")
        sig = Path(u"/tmp/testfiles/output/sig.tar")
        diff = Path(u"/tmp/testfiles/output/diff.tar")
        for dirname in filelist[1:]:
            new_path = Path(dirname)
            diffdir.write_block_iter(
                diffdir.DirSig(selection.Select(seq_path).set_iter()), sig)

            diffdir.write_block_iter(
                diffdir.DirDelta(selection.Select(new_path).set_iter(),
                                 sig.open(u"rb")),
                diff)

            patchdir.Patch(seq_path, diff.open(u"rb"))

            assert seq_path.compare_recursive(new_path, 1)

    def test_basic_cycle(self):
        u"""Test cycle on dir with devices, changing uid/gid, etc."""
        self.total_sequence([u'/tmp/testfiles/root1', u'/tmp/testfiles/root2'])

    def test_patchdir(self):
        u"""Test changing uid/gid, devices"""
        self.deltmp()
        os.system(u"cp -pR /tmp/testfiles/root1 /tmp/testfiles/output/sequence")
        seq_path = Path(u"/tmp/testfiles/output/sequence")
        new_path = Path(u"/tmp/testfiles/root2")
        sig = Path(u"/tmp/testfiles/output/sig.tar")
        diff = Path(u"/tmp/testfiles/output/diff.tar")

        diffdir.write_block_iter(diffdir.DirSig(self.get_sel(seq_path)), sig)
        deltablock = diffdir.DirDelta(self.get_sel(new_path), sig.open(u"rb"))
        diffdir.write_block_iter(deltablock, diff)

        patchdir.Patch(seq_path, diff.open(u"rb"))

        # since we are not running as root, don't even both comparing,
        # just make sure file5 exists and file4 doesn't.
        file5 = seq_path.append(u"file5")
        assert file5.isreg()
        file4 = seq_path.append(u"file4")
        assert file4.type is None

    def test_patchdir2(self):
        u"""Again test files we don't have access to, this time Tar_WriteSig"""
        self.deltmp()
        sig_path = Path(u"/tmp/testfiles/output/sig.sigtar")
        tar_path = Path(u"/tmp/testfiles/output/tar.tar")
        basis_path = Path(u"/tmp/testfiles/root1")

        deltablock = diffdir.DirFull_WriteSig(self.get_sel(basis_path),
                                              sig_path.open(u"wb"))
        diffdir.write_block_iter(deltablock, tar_path)

def runtests(): unittest.main()

if __name__ == u"__main__":
    unittest.main()

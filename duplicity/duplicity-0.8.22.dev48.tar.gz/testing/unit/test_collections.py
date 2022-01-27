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

import pytest
import random
import unittest

from . import UnitTestCase
from duplicity import backend
from duplicity import config
from duplicity import dup_collections
from duplicity import dup_time
from duplicity import gpg
from duplicity import path
from testing import _runtest_dir

filename_list1 = [b"duplicity-full.2002-08-17T16:17:01-07:00.manifest.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol1.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol2.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol3.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol4.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol5.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol6.difftar.gpg",
                  b"duplicity-inc.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.manifest.gpg",
                  b"duplicity-inc.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.vol1.difftar.gpg",
                  b"Extra stuff to be ignored"]

remote_sigchain_filename_list = [b"duplicity-full-signatures.2002-08-17T16:17:01-07:00.sigtar.gpg",
                                 b"duplicity-new-signatures.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.sigtar.gpg",
                                 b"duplicity-new-signatures.2002-08-18T00:04:30-07:00.to.2002-08-20T00:00:00-07:00.sigtar.gpg"]

local_sigchain_filename_list = [b"duplicity-full-signatures.2002-08-17T16:17:01-07:00.sigtar.gz",
                                b"duplicity-new-signatures.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.sigtar.gz",
                                b"duplicity-new-signatures.2002-08-18T00:04:30-07:00.to.2002-08-20T00:00:00-07:00.sigtar.gz"]

# A filename list with some incomplete volumes, an older full volume,
# and a complete chain.
filename_list2 = [b"duplicity-full.2001-01-01T16:17:01-07:00.manifest.gpg",
                  b"duplicity-full.2001-01-01T16:17:01-07:00.vol1.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.manifest.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol1.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol2.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol3.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol4.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol5.difftar.gpg",
                  b"duplicity-full.2002-08-17T16:17:01-07:00.vol6.difftar.gpg",
                  b"duplicity-inc.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.manifest.gpg",
                  b"duplicity-inc.2002-08-17T16:17:01-07:00.to.2002-08-18T00:04:30-07:00.vol1.difftar.gpg",
                  b"The following are extraneous duplicity files",
                  b"duplicity-new-signatures.2001-08-17T02:05:13-05:00.to.2002-08-17T05:05:14-05:00.sigtar.gpg",
                  b"duplicity-full.2002-08-15T01:01:01-07:00.vol1.difftar.gpg",
                  b"duplicity-inc.2000-08-17T16:17:01-07:00.to.2000-08-18T00:04:30-07:00.manifest.gpg",
                  b"duplicity-inc.2000-08-17T16:17:01-07:00.to.2000-08-18T00:04:30-07:00.vol1.difftar.gpg",
                  b"Extra stuff to be ignored"]


class CollectionTest(UnitTestCase):
    u"""Test collections"""
    def setUp(self):
        super(CollectionTest, self).setUp()

        self.unpack_testfiles()

        col_test_dir = path.Path(u"{0}/testfiles/collectionstest".format(_runtest_dir))
        archive_dir_path = col_test_dir.append(u"archive_dir")
        self.set_config(u'archive_dir_path', archive_dir_path)
        self.archive_dir_backend = backend.get_backend(u"file://{0}/testfiles/collectionstest".format(_runtest_dir) +
                                                       u"/archive_dir")

        self.real_backend = backend.get_backend(u"file://%s/%s" %
                                                (col_test_dir.uc_name, u"remote_dir"))
        self.output_dir = path.Path(u"{0}/testfiles/output".format(_runtest_dir))  # used as a temp directory
        self.output_dir_backend = backend.get_backend(u"file://{0}/testfiles/output".format(_runtest_dir))

    def set_gpg_profile(self):
        u"""Set gpg profile to standard "foobar" sym"""
        self.set_config(u'gpg_profile', gpg.GPGProfile(passphrase=u"foobar"))

    def test_backup_chains(self):
        u"""Test basic backup chain construction"""
        random.shuffle(filename_list1)
        cs = dup_collections.CollectionsStatus(None, config.archive_dir_path, u"full")
        chains, orphaned, incomplete = cs.get_backup_chains(filename_list1)
        if len(chains) != 1 or len(orphaned) != 0:
            print(chains)
            print(orphaned)
            assert 0

        chain = chains[0]
        assert chain.end_time == 1029654270
        assert chain.fullset.time == 1029626221

    def test_collections_status(self):
        u"""Test CollectionStatus object's set_values()"""
        def check_cs(cs):
            u"""Check values of collections status"""
            assert cs.values_set

            assert cs.matched_chain_pair
            assert cs.matched_chain_pair[0].end_time == 1029826800
            assert len(cs.all_backup_chains) == 1, cs.all_backup_chains

        cs = dup_collections.CollectionsStatus(self.real_backend, config.archive_dir_path, u"full").set_values()
        check_cs(cs)
        assert cs.matched_chain_pair[0].islocal()

    def test_sig_chain(self):
        u"""Test a single signature chain"""
        chain = dup_collections.SignatureChain(1, config.archive_dir_path)
        for filename in local_sigchain_filename_list:
            assert chain.add_filename(filename)
        assert not chain.add_filename(b"duplicity-new-signatures.2002-08-18T00:04:30-07:00.to.2002-08-20T00:00:00-07:00.sigtar.gpg")

    def test_sig_chains(self):
        u"""Test making signature chains from filename list"""
        cs = dup_collections.CollectionsStatus(None, config.archive_dir_path, u"full")
        chains, orphaned_paths = cs.get_signature_chains(local=1)
        self.sig_chains_helper(chains, orphaned_paths)

    def test_sig_chains2(self):
        u"""Test making signature chains from filename list on backend"""
        cs = dup_collections.CollectionsStatus(self.archive_dir_backend, config.archive_dir_path, u"full")
        chains, orphaned_paths = cs.get_signature_chains(local=None)
        self.sig_chains_helper(chains, orphaned_paths)

    def sig_chains_helper(self, chains, orphaned_paths):
        u"""Test chains and orphaned_paths values for two above tests"""
        if orphaned_paths:
            for op in orphaned_paths:
                print(op)
            assert 0
        assert len(chains) == 1, chains
        assert chains[0].end_time == 1029826800

    def sigchain_fileobj_get(self, local):
        u"""Return chain, local if local is true with filenames added"""
        if local:
            chain = dup_collections.SignatureChain(1, config.archive_dir_path)
            for filename in local_sigchain_filename_list:
                assert chain.add_filename(filename)
        else:
            chain = dup_collections.SignatureChain(None, self.real_backend)
            for filename in remote_sigchain_filename_list:
                assert chain.add_filename(filename)
        return chain

    def sigchain_fileobj_check_list(self, chain):
        u"""Make sure the list of file objects in chain has right contents

        The contents of the /tmp/testfiles/collectiontest/remote_dir have
        to be coordinated with this test.

        """
        fileobjlist = chain.get_fileobjs()
        assert len(fileobjlist) == 3

        def test_fileobj(i, s):
            buf = fileobjlist[i].read()
            fileobjlist[i].close()
            assert buf == s, (buf, s)

        test_fileobj(0, b"Hello, world!")
        test_fileobj(1, b"hello 1")
        test_fileobj(2, b"Hello 2")

    @pytest.mark.usefixtures(u"redirect_stdin")
    def test_sigchain_fileobj(self):
        u"""Test getting signature chain fileobjs from archive_dir_path"""
        self.set_gpg_profile()
        self.sigchain_fileobj_check_list(self.sigchain_fileobj_get(1))
        self.sigchain_fileobj_check_list(self.sigchain_fileobj_get(None))

    def get_filelist2_cs(self):
        u"""Return set CollectionsStatus object from filelist 2"""
        # Set up /tmp/testfiles/output with files from filename_list2
        for filename in filename_list2:
            p = self.output_dir.append(filename)
            p.touch()

        cs = dup_collections.CollectionsStatus(self.output_dir_backend, config.archive_dir_path, u"full")
        cs.set_values()
        return cs

    def test_get_extraneous(self):
        u"""Test the listing of extraneous files"""
        cs = self.get_filelist2_cs()
        assert len(cs.orphaned_backup_sets) == 1, cs.orphaned_backup_sets
        assert len(cs.local_orphaned_sig_names) == 0, cs.local_orphaned_sig_names
        assert len(cs.remote_orphaned_sig_names) == 1, cs.remote_orphaned_sig_names
        assert len(cs.incomplete_backup_sets) == 1, cs.incomplete_backup_sets

        right_list = [b"duplicity-new-signatures.2001-08-17T02:05:13-05:00.to.2002-08-17T05:05:14-05:00.sigtar.gpg",
                      b"duplicity-full.2002-08-15T01:01:01-07:00.vol1.difftar.gpg",
                      b"duplicity-inc.2000-08-17T16:17:01-07:00.to.2000-08-18T00:04:30-07:00.manifest.gpg",
                      b"duplicity-inc.2000-08-17T16:17:01-07:00.to.2000-08-18T00:04:30-07:00.vol1.difftar.gpg"]
        local_received_list, remote_received_list = cs.get_extraneous()
        errors = []
        for filename in remote_received_list:
            if filename not in right_list:
                errors.append(u"### Got bad extraneous filename " + filename.decode())
            else:
                right_list.remove(filename)
        for filename in right_list:
            errors.append(u"### Didn't receive extraneous filename " + filename)
        assert not errors, u"\n" + u"\n".join(errors)

    def test_get_olderthan(self):
        u"""Test getting list of files older than a certain time"""
        cs = self.get_filelist2_cs()
        oldsets = cs.get_older_than(
            dup_time.genstrtotime(u"2002-05-01T16:17:01-07:00"))
        oldset_times = [s.get_time() for s in oldsets]
        right_times = [dup_time.genstrtotime(u'2001-01-01T16:17:01-07:00')]
        assert oldset_times == right_times, \
            [oldset_times, right_times]

        oldsets_required = cs.get_older_than_required(
            dup_time.genstrtotime(u"2002-08-17T20:00:00-07:00"))
        oldset_times = [s.get_time() for s in oldsets_required]
        right_times_required = [dup_time.genstrtotime(u'2002-08-17T16:17:01-07:00')]
        assert oldset_times == right_times_required, \
            [oldset_times, right_times_required]


if __name__ == u"__main__":
    unittest.main()

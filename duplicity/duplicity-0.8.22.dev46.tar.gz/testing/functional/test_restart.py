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

import glob
import os
import platform
import subprocess
import sys
import unittest

from testing import _runtest_dir
from . import FunctionalTestCase


class RestartTest(FunctionalTestCase):
    u"""
    Test checkpoint/restart using duplicity binary
    """
    @unittest.skipIf(sys.version_info.major == 2, u"Skip on possible timing error")
    def test_basic_checkpoint_restart(self):
        u"""
        Test basic Checkpoint/Restart
        """
        self.make_largefiles()
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), fail=1)
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir))
        self.verify(u"{0}/testfiles/largefiles".format(_runtest_dir))

    @unittest.skipIf(sys.version_info.major == 2, u"Skip on possible timing error")
    def test_multiple_checkpoint_restart(self):
        u"""
        Test multiple Checkpoint/Restart
        """
        self.make_largefiles()
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), fail=1)
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), fail=2)
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), fail=3)
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir))
        self.verify(u"{0}/testfiles/largefiles".format(_runtest_dir))

    @unittest.skipIf(sys.version_info.major == 2, u"Skip on possible timing error")
    def test_first_volume_failure(self):
        u"""
        Test restart when no volumes are available on the remote.
        Caused when duplicity fails before the first transfer.
        """
        self.make_largefiles()
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), fail=1)
        assert not os.system(u"rm {0}/testfiles/output/duplicity-full*difftar*".format(_runtest_dir))
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir))
        self.verify(u"{0}/testfiles/largefiles".format(_runtest_dir))

    @unittest.skipIf(sys.version_info.major == 2, u"Skip on possible timing error")
    def test_multi_volume_failure(self):
        u"""
        Test restart when fewer volumes are available on the remote
        than the local manifest has on record.  Caused when duplicity
        fails the last queued transfer(s).
        """
        self.make_largefiles()
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), fail=3)
        assert not os.system(u"rm {0}/testfiles/output/duplicity-full*vol[23].difftar*".format(_runtest_dir))
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir))
        self.verify(u"{0}/testfiles/largefiles".format(_runtest_dir))

    @unittest.skipIf(sys.version_info.major == 2, u"Skip on possible timing error")
    def test_restart_encrypt_without_password(self):
        u"""
        Test that we can successfully restart a encrypt-key-only backup without
        providing a password for it. (Normally, we'd need to decrypt the first
        volume, but there is special code to skip that with an encrypt key.)
        """
        self.set_environ(u'PASSPHRASE', None)
        self.set_environ(u'SIGN_PASSPHRASE', None)
        self.make_largefiles()
        enc_opts = [u"--encrypt-key", self.encrypt_key1]
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), options=enc_opts, fail=2)
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), options=enc_opts)

        self.set_environ(u'PASSPHRASE', self.sign_passphrase)
        self.verify(u"{0}/testfiles/largefiles".format(_runtest_dir))

    @unittest.skipIf(sys.version_info.major == 2, u"Skip on possible timing error")
    def test_restart_sign_and_encrypt(self):
        u"""
        Test restarting a backup using same key for sign and encrypt
        https://bugs.launchpad.net/duplicity/+bug/946988
        """
        self.make_largefiles()
        enc_opts = [u"--sign-key", self.sign_key, u"--encrypt-key", self.sign_key]
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), options=enc_opts, fail=2)
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), options=enc_opts)
        self.verify(u"{0}/testfiles/largefiles".format(_runtest_dir))

    @unittest.skipIf(sys.version_info.major == 2, u"Skip on possible timing error")
    def test_restart_sign_and_hidden_encrypt(self):
        u"""
        Test restarting a backup using same key for sign and encrypt (hidden key id)
        https://bugs.launchpad.net/duplicity/+bug/946988
        """
        self.make_largefiles()
        enc_opts = [u"--sign-key", self.sign_key, u"--hidden-encrypt-key", self.sign_key]
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), options=enc_opts, fail=2)
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), options=enc_opts)
        self.verify(u"{0}/testfiles/largefiles".format(_runtest_dir))

    def test_last_file_missing_in_middle(self):
        u"""
        Test restart when the last file being backed up is missing on restart.
        Caused when the user deletes a file after a failure.  This test puts
        the file in the middle of the backup, with files following.
        """
        self.make_largefiles()
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), fail=3)
        assert not os.system(u"rm {0}/testfiles/largefiles/file2".format(_runtest_dir))
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir))
        self.verify(u"{0}/testfiles/largefiles".format(_runtest_dir))

    @unittest.skipIf(platform.machine() in [u"ppc64el", u"ppc64le"], u"Skip on ppc64el and ppc64le machines")
    def test_last_file_missing_at_end(self):
        u"""
        Test restart when the last file being backed up is missing on restart.
        Caused when the user deletes a file after a failure.  This test puts
        the file at the end of the backup, with no files following.
        """
        self.make_largefiles()
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), fail=6)
        assert not os.system(u"rm {0}/testfiles/largefiles/file3".format(_runtest_dir))
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir))
        self.verify(u"{0}/testfiles/largefiles".format(_runtest_dir))

    def test_restart_incremental(self):
        u"""
        Test restarting an incremental backup
        """
        self.make_largefiles()
        self.backup(u"full", u"{0}/testfiles/dir1".format(_runtest_dir))
        self.backup(u"inc", u"{0}/testfiles/largefiles".format(_runtest_dir), fail=2)
        self.backup(u"inc", u"{0}/testfiles/largefiles".format(_runtest_dir))
        self.verify(u"{0}/testfiles/largefiles".format(_runtest_dir))

    def make_fake_second_volume(self, name):
        u"""
        Takes a successful backup and pretend that we interrupted a backup
        after two-volumes.  (This is because we want to be able to model
        restarting the second volume and duplicity deletes the last volume
        found because it may have not finished uploading.)
        """
        # First, confirm that we have signs of a successful backup
        self.assertEqual(len(glob.glob(u"{0}/testfiles/output/*.manifest*".format(_runtest_dir))), 1)
        self.assertEqual(len(glob.glob(u"{0}/testfiles/output/*.sigtar*".format(_runtest_dir))), 1)
        self.assertEqual(len(glob.glob(u"{0}/testfiles/cache/{1}/*".format(_runtest_dir, name))), 2)
        self.assertEqual(len(glob.glob(
            u"{0}/testfiles/cache/{1}/*.manifest*".format(_runtest_dir, name))), 1)
        self.assertEqual(len(glob.glob(
            u"{0}/testfiles/cache/{1}/*.sigtar*".format(_runtest_dir, name))), 1)
        # Alright, everything is in order; fake a second interrupted volume
        assert not os.system(u"rm {0}/testfiles/output/*.manifest*".format(_runtest_dir))
        assert not os.system(u"rm {0}/testfiles/output/*.sigtar*".format(_runtest_dir))
        assert not os.system(u"rm -f {0}/testfiles/output/*.vol[23456789].*".format(_runtest_dir))
        assert not os.system(u"rm -f {0}/testfiles/output/*.vol1[^.]+.*".format(_runtest_dir))
        self.assertEqual(len(glob.glob(u"{0}/testfiles/output/*.difftar*".format(_runtest_dir))), 1)
        assert not os.system(u"rm {0}/testfiles/cache/{1}/*.sigtar*".format(_runtest_dir, name))
        assert not os.system(u"cp {0}/testfiles/output/*.difftar* ".format(_runtest_dir) +
                             u"`ls {0}/testfiles/output/*.difftar* | ".format(_runtest_dir) +
                             u" sed 's|vol1|vol2|'`")
        assert not os.system(u"head -n6 {0}/testfiles/cache/{1}/*.manifest > ".format(_runtest_dir, name) +
                             u"{0}/testfiles/cache/{1}/".format(_runtest_dir, name) +
                             u"`basename {0}/testfiles/cache/{1}/*.manifest`".format(_runtest_dir, name) +
                             u".part")
        assert not os.system(u"rm {0}/testfiles/cache/{1}/*.manifest".format(_runtest_dir, name))
        assert not os.system(u"""echo 'Volume 2:
    StartingPath   foo
    EndingPath     bar
    Hash SHA1 sha1' >> {0}/testfiles/cache/{1}/*.manifest.part""".format(_runtest_dir, name))

    def test_split_after_small(self):
        u"""
        If we restart right after a volume that ended with a small
        (one-block) file, make sure we restart in the right place.
        """
        source = u'{0}/testfiles/largefiles'.format(_runtest_dir)
        assert not os.system(u"mkdir -p %s" % source)
        assert not os.system(u"echo hello > %s/file1" % source)
        self.backup(u"full", source, options=[u"--name=backup1"])
        # Fake an interruption
        self.make_fake_second_volume(u"backup1")
        # Add new file
        assert not os.system(u"cp %s/file1 %s/newfile" % (source, source))
        # 'restart' the backup
        self.backup(u"full", source, options=[u"--name=backup1"])
        # Confirm we actually resumed the previous backup
        self.assertEqual(len(os.listdir(u"{0}/testfiles/output".format(_runtest_dir))), 4)
        # Now make sure everything is byte-for-byte the same once restored
        self.restore()
        assert not os.system(u"diff -r {1} {0}/testfiles/restore_out".format(_runtest_dir, source))

    def test_split_after_large(self):
        u"""
        If we restart right after a volume that ended with a large
        (multi-block) file, make sure we restart in the right place.
        """
        source = u'{0}/testfiles/largefiles'.format(_runtest_dir)
        self.make_largefiles(count=1, size=1)
        self.backup(u"full", source, options=[u"--volsize=5", u"--name=backup1"])
        # Fake an interruption
        self.make_fake_second_volume(u"backup1")
        # Add new file
        assert not os.system(u"cp %s/file1 %s/newfile" % (source, source))
        # 'restart' the backup
        self.backup(u"full", source, options=[u"--volsize=5", u"--name=backup1"])
        # Confirm we actually resumed the previous backup
        self.assertEqual(len(os.listdir(u"{0}/testfiles/output".format(_runtest_dir))), 4)
        # Now make sure everything is byte-for-byte the same once restored
        self.restore()
        assert not os.system(u"diff -r %s {0}/testfiles/restore_out".format(_runtest_dir) % source)

    def test_split_inside_large(self):
        u"""
        If we restart right after a volume that ended inside of a large
        (multi-block) file, make sure we restart in the right place.
        """
        source = u'{0}/testfiles/largefiles'.format(_runtest_dir)
        self.make_largefiles(count=1, size=3)
        self.backup(u"full", source, options=[u"--name=backup1"])
        # Fake an interruption
        self.make_fake_second_volume(u"backup1")
        # 'restart' the backup
        self.backup(u"full", source, options=[u"--name=backup1"])
        # Now make sure everything is byte-for-byte the same once restored
        self.restore()
        assert not os.system(u"diff -r {0} {1}/testfiles/restore_out".format(source, _runtest_dir))

    def test_new_file(self):
        u"""
        If we restart right after a volume, but there are new files that would
        have been backed up earlier in the volume, make sure we don't wig out.
        (Expected result is to ignore new, ealier files, but pick up later
        ones.)
        """
        source = u'{0}/testfiles/largefiles'.format(_runtest_dir)
        self.make_largefiles(count=1, size=1)
        self.backup(u"full", source, options=[u"--name=backup1"])
        # Fake an interruption
        self.make_fake_second_volume(u"backup1")
        # Add new files, earlier and later in filename sort order
        assert not os.system(u"echo hello > %s/a" % source)
        assert not os.system(u"echo hello > %s/z" % source)
        # 'restart' the backup
        self.backup(u"full", source, options=[u"--name=backup1"])
        # Now make sure everything is the same once restored, except 'a'
        self.restore()
        assert not os.system(u"test ! -e {0}/testfiles/restore_out/a".format(_runtest_dir))
        assert not os.system(u"diff {0}/file1 {1}/testfiles/restore_out/file1".format(source, _runtest_dir))
        assert not os.system(u"diff {0}/z {1}/testfiles/restore_out/z".format(source, _runtest_dir))

    @unittest.skipIf(sys.version_info.major == 2, u"Skip on possible timing error")
    def test_changed_source_dangling_manifest_volume(self):
        u"""
        If we restart but find remote volumes missing, we can easily end up
        with a manifest that lists "vol1, vol2, vol3, vol2", leaving a dangling
        vol3.  Make sure we can gracefully handle that.  This will only happen
        if the source data changes to be small enough to not create a vol3 on
        restart.
        """
        source = u'{0}/testfiles/largefiles'.format(_runtest_dir)
        self.make_largefiles(count=5, size=1)
        self.backup(u"full", source, fail=3)
        # now delete the last volume on remote end and some source files
        assert not os.system(u"rm {0}/testfiles/output/duplicity-full*vol3.difftar*".format(_runtest_dir))
        assert not os.system(u"rm %s/file[2345]" % source)
        assert not os.system(u"echo hello > %s/z" % source)
        # finish backup
        self.backup(u"full", source)
        # and verify we can restore
        self.restore()

    def test_changed_source_file_disappears(self):
        u"""
        Make sure we correctly handle restarting a backup when a file
        disappears when we had been in the middle of backing it up.  It's
        possible that the first chunk of the next file will be skipped unless
        we're careful.
        """
        source = u'{0}/testfiles/largefiles'.format(_runtest_dir)
        self.make_largefiles(count=1)
        self.backup(u"full", source, fail=2)
        # now remove starting source data and make sure we add something after
        assert not os.system(u"rm %s/*" % source)
        assert not os.system(u"echo hello > %s/z" % source)
        # finish backup
        self.backup(u"full", source)
        # and verify we can restore
        self.restore()
        assert not os.system(u"diff {0}/z {1}/testfiles/restore_out/z".format(source, _runtest_dir))


# Note that this class duplicates all the tests in RestartTest
class RestartTestWithoutEncryption(RestartTest):

    def setUp(self):
        super(RestartTestWithoutEncryption, self).setUp()
        self.class_args.extend([u"--no-encryption"])

    def test_no_write_double_snapshot(self):
        u"""
        Test that restarting a full backup does not write duplicate entries
        into the sigtar, causing problems reading it back in older
        versions.
        https://launchpad.net/bugs/929067
        """
        self.make_largefiles()
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir), fail=2)
        self.backup(u"full", u"{0}/testfiles/largefiles".format(_runtest_dir))
        # Now check sigtar
        sigtars = glob.glob(u"{0}/testfiles/output/duplicity-full*.sigtar.gz".format(_runtest_dir))
        self.assertEqual(1, len(sigtars))
        sigtar = sigtars[0]
        output = subprocess.Popen([u"tar", u"t", u"--file=%s" % sigtar], stdout=subprocess.PIPE).communicate()[0]
        self.assertEqual(1, output.split(b"\n").count(b"snapshot/"))

    def test_ignore_double_snapshot(self):
        u"""
        Test that we gracefully ignore double snapshot entries in a signature
        file.  This winds its way through duplicity as a deleted base dir,
        which doesn't make sense and should be ignored.  An older version of
        duplicity accidentally created such files as a result of a restart.
        https://launchpad.net/bugs/929067
        """

        if platform.system().startswith(u'Linux'):
            tarcmd = u"tar"
        elif platform.system().startswith(u'Darwin'):
            tarcmd = u"gtar"
        elif platform.system().endswith(u'BSD'):
            tarcmd = u"gtar"
        else:
            raise Exception(u"Platform %s not supported by tar/gtar." % platform.platform())

        # Intial normal backup
        self.backup(u"full", u"{0}/testfiles/blocktartest".format(_runtest_dir))
        # Create an exact clone of the snapshot folder in the sigtar already.
        # Permissions and mtime must match.
        os.mkdir(u"{0}/testfiles/snapshot".format(_runtest_dir), 0o755)
        os.utime(u"{0}/testfiles/snapshot".format(_runtest_dir), (1030384548, 1030384548))
        # Adjust the sigtar.gz file to have a bogus second snapshot/ entry
        # at the beginning.
        sigtars = glob.glob(u"{0}/testfiles/output/duplicity-full*.sigtar.gz".format(_runtest_dir))
        self.assertEqual(1, len(sigtars))
        sigtar = sigtars[0]
        self.assertEqual(0, os.system(u"{0} c --file={1}/testfiles/snapshot.sigtar -C {1}/testfiles snapshot".format(tarcmd, _runtest_dir)))
        self.assertEqual(0, os.system(u"gunzip -c {1} > {0}/testfiles/full.sigtar".format(_runtest_dir, sigtar)))
        self.assertEqual(0, os.system(u"{0} A --file={1}/testfiles/snapshot.sigtar {1}/testfiles/full.sigtar".format(tarcmd, _runtest_dir)))
        self.assertEqual(0, os.system(u"gzip {0}/testfiles/snapshot.sigtar".format(_runtest_dir)))
        os.remove(sigtar)
        os.rename(u"{0}/testfiles/snapshot.sigtar.gz".format(_runtest_dir), sigtar)
        # Clear cache so our adjusted sigtar will be sync'd back into the cache
        self.assertEqual(0, os.system(u"rm -r {0}/testfiles/cache".format(_runtest_dir)))
        # Try a follow on incremental (which in buggy versions, would create
        # a deleted entry for the base dir)
        self.backup(u"inc", u"{0}/testfiles/blocktartest".format(_runtest_dir))
        self.assertEqual(1, len(glob.glob(u"{0}/testfiles/output/duplicity-new*.sigtar.gz".format(_runtest_dir))))
        # Confirm we can restore it (which in buggy versions, would fail)
        self.restore()

if __name__ == u"__main__":
    unittest.main()

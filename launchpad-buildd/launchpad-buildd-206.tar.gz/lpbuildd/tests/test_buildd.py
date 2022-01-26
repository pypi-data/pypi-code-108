# Copyright 2009 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Builder tests.

This file contains the following tests:

 * Basic authentication handling (used to download private sources);
 * Build log sanitization (removal of passwords from private buildlog);
 * Build log(tail) mechanisms (limited output from the end of the buildlog).

"""

__metaclass__ = type

__all__ = ['LaunchpadBuilddTests']

import difflib
import os
import shutil
import sys
import tempfile
import unittest

from six.moves.urllib.request import HTTPBasicAuthHandler
from six.moves.xmlrpc_client import ServerProxy
import twisted

from lpbuildd.tests.harness import (
    BuilddTestCase,
    BuilddTestSetup,
    MockBuildManager,
    )


def read_file(path):
    """Helper for reading the contents of a file."""
    with open(path) as file_object:
        return file_object.read()


class LaunchpadBuilddTests(BuilddTestCase):
    """Unit tests for scrubbing (removal of passwords) of buildlog files."""

    def testBasicAuth(self):
        """Test that the auth handler is installed with the right details."""
        url = "http://fakeurl/"
        user = "myuser"
        password = "fakepassword"

        opener = self.builder.setupAuthHandler(url, user, password)

        # Inspect the openers and ensure the wanted handler is installed.
        basic_auth_handler = None
        for handler in opener.handlers:
            if isinstance(handler, HTTPBasicAuthHandler):
                basic_auth_handler = handler
                break
        self.assertTrue(
            basic_auth_handler is not None,
            "No basic auth handler installed.")

        password_mgr = basic_auth_handler.passwd
        stored_user, stored_pass = password_mgr.find_user_password(None, url)
        self.assertEqual(user, stored_user)
        self.assertEqual(password, stored_pass)

    def testBuildlogScrubbing(self):
        """Tests the buildlog scrubbing (removal of passwords from URLs)."""
        # This is where the buildlog file lives.
        log_path = self.builder.cachePath('buildlog')

        # This is where the builder leaves the original/unsanitized
        # buildlog file after scrubbing.
        unsanitized_path = self.builder.cachePath('buildlog.unsanitized')

        # Copy the fake buildlog file to the cache path.
        shutil.copy(os.path.join(self.here, 'buildlog'), log_path)

        # Invoke the builder's buildlog scrubbing method.
        self.builder.sanitizeBuildlog(log_path)

        # Read the unsanitized original content.
        unsanitized = read_file(unsanitized_path).splitlines()
        # Read the new, sanitized content.
        clean = read_file(log_path).splitlines()

        # Compare the scrubbed content with the unsanitized one.
        differences = '\n'.join(difflib.unified_diff(unsanitized, clean))

        # Read the expected differences from the prepared disk file.
        expected = read_file(os.path.join(self.here, 'test_1.diff'))

        # Python difflib slightly changed the formatting of the headers; we
        # don't care; let's make it look the same as it used to.
        differences = differences.replace(
            '--- \n\n+++ \n\n',
            '---  \n\n+++  \n\n')

        # Make sure they match.
        self.assertEqual(differences, expected)

    def testLogtailScrubbing(self):
        """Test the scrubbing of the builder's getLogTail() output."""

        # This is where the buildlog file lives.
        log_path = self.builder.cachePath('buildlog')

        # Copy the prepared, longer buildlog file so we can test lines
        # that are chopped off in the middle.
        shutil.copy(os.path.join(self.here, 'buildlog.long'), log_path)

        # First get the unfiltered log tail output (which is the default
        # behaviour because the BuildManager's 'is_archive_private'
        # property is initialized to False).
        self.builder.manager.is_archive_private = False
        unsanitized = self.builder.getLogTail().decode('UTF-8').splitlines()

        # Make the builder believe we are building in a private archive to
        # obtain the scrubbed log tail output.
        self.builder.manager.is_archive_private = True
        clean = self.builder.getLogTail().decode('UTF-8').splitlines()

        # Get the differences ..
        differences = '\n'.join(difflib.unified_diff(unsanitized, clean))

        # .. and the expected differences.
        expected = read_file(os.path.join(self.here, 'test_2.diff'))

        # Python difflib slightly changed the formatting of the headers; we
        # don't care; let's make it look the same as it used to.
        differences = differences.replace(
            '--- \n\n+++ \n\n',
            '---  \n\n+++  \n\n')

        # Finally make sure what we got is what we expected.
        self.assertEqual(differences, expected)

    def testLogtail(self):
        """Tests the logtail mechanisms.

        'getLogTail' return up to 2 KiB text from the current 'buildlog' file.
        """
        self.makeLog(0)
        log_tail = self.builder.getLogTail()
        self.assertEqual(len(log_tail), 0)

        self.makeLog(1)
        log_tail = self.builder.getLogTail()
        self.assertEqual(len(log_tail), 1)

        self.makeLog(2048)
        log_tail = self.builder.getLogTail()
        self.assertEqual(len(log_tail), 2048)

        self.makeLog(2049)
        log_tail = self.builder.getLogTail()
        self.assertEqual(len(log_tail), 2048)

        self.makeLog(4096)
        log_tail = self.builder.getLogTail()
        self.assertEqual(len(log_tail), 2048)

    def testLogtailWhenLogFileVanishes(self):
        """Builder.getLogTail doesn't get hurt if the logfile has vanished.

        This is a common race-condition in our builders, since they get
        polled all the time when they are building.

        Sometimes the getLogTail calls coincides with the job
        cleanup/sanitization, so there is no buildlog to inspect and thus
        we expect an empty string to be returned instead of a explosion.
        """
        # Create some log content and read it.
        self.makeLog(2048)
        log_tail = self.builder.getLogTail()
        self.assertEqual(len(log_tail), 2048)

        # Read it again for luck.
        log_tail = self.builder.getLogTail()
        self.assertEqual(len(log_tail), 2048)

        # Remove the buildlog file
        os.remove(self.builder.cachePath('buildlog'))

        # Instead of shocking the getLogTail call, return an empty string.
        log_tail = self.builder.getLogTail()
        self.assertEqual(len(log_tail), 0)

    def testCleanDuplicateFiles(self):
        """The clean method copes with duplicate waiting files."""
        workdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, workdir)
        self.builder._log = None
        self.builder.startBuild(MockBuildManager())
        self.builder.buildComplete()
        paths = [os.path.join(workdir, name) for name in ('a', 'b')]
        for path in paths:
            with open(path, 'w') as f:
                f.write('data')
            self.builder.addWaitingFile(path)
        self.builder.clean()
        self.assertEqual([], os.listdir(self.builder._cachepath))


class XMLRPCBuilderTests(unittest.TestCase):

    def setUp(self):
        super(XMLRPCBuilderTests, self).setUp()
        self.builder = BuilddTestSetup()
        self.builder.setUp()
        self.server = ServerProxy('http://localhost:8321/rpc/')

    def tearDown(self):
        self.builder.tearDown()
        super(XMLRPCBuilderTests, self).tearDown()

    @unittest.skipIf(
        sys.version >= '3' and
        (twisted.version.major, twisted.version.minor) < (16, 4),
        'twistd fails to daemonise on Python 3 before Twisted 16.4.0')
    def test_build_unknown_builder(self):
        # If a bogus builder name is passed into build, it returns an
        # appropriate error message and not just 'None'.
        buildername = 'nonexistentbuilder'
        status, info = self.server.build('foo', buildername, 'sha1', {}, {})

        self.assertEqual('BuilderStatus.UNKNOWNBUILDER', status)
        self.assertIsNotNone(info, "UNKNOWNBUILDER returns 'None' info.")
        self.assertTrue(
            info.startswith("%s not in [" % buildername),
            'UNKNOWNBUILDER info is "%s"' % info)

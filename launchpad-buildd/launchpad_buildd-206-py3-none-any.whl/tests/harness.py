# Copyright 2009-2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type
__all__ = [
    'BuilddTestCase',
    ]

try:
    from configparser import ConfigParser as SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser
import os
import shutil
import tempfile
import unittest

from fixtures import EnvironmentVariable
from txfixtures.tachandler import TacTestFixture

from lpbuildd.builder import Builder


test_conffile = os.path.join(
    os.path.dirname(__file__), 'buildd-slave-test.conf')


class MockBuildManager(object):
    """Mock BuildManager class.

    Only implements 'is_archive_private' and 'needs_sanitized_logs' as False.
    """
    is_archive_private = False

    @property
    def needs_sanitized_logs(self):
        return self.is_archive_private


class BuilddTestCase(unittest.TestCase):
    """Unit tests for logtail mechanisms."""

    def setUp(self):
        """Setup a Builder using the test config."""
        conf = SafeConfigParser()
        conf.read(test_conffile)
        conf.set("builder", "filecache", tempfile.mkdtemp())

        self.builder = Builder(conf)
        self.builder._log = True
        self.builder.manager = MockBuildManager()

        self.here = os.path.abspath(os.path.dirname(__file__))

    def tearDown(self):
        """Remove the 'filecache' directory used for the tests."""
        shutil.rmtree(self.builder._cachepath)

    def makeLog(self, size):
        """Inject data into the default buildlog file."""
        f = open(self.builder.cachePath('buildlog'), 'w')
        f.write("x" * size)
        f.close()


class BuilddTestSetup(TacTestFixture):
    r"""Setup Builder for use by functional tests

    >>> fixture = BuilddTestSetup()
    >>> fixture.setUp()

    Make sure the server is running

    >>> try:
    ...     from xmlrpc.client import ServerProxy
    ... except ImportError:
    ...     from xmlrpclib import ServerProxy
    >>> s = ServerProxy('http://localhost:8321/rpc/')
    >>> s.echo('Hello World')
    ['Hello World']
    >>> fixture.tearDown()

    Again for luck !

    >>> fixture.setUp()
    >>> s = ServerProxy('http://localhost:8321/rpc/')

    >>> s.echo('Hello World')
    ['Hello World']

    >>> info = s.info()
    >>> len(info)
    3
    >>> print(info[:2])
    ['1.0', 'i386']

    >>> for buildtype in sorted(info[2]):
    ...     print(buildtype)
    binarypackage
    debian
    sourcepackagerecipe
    translation-templates

    >>> s.status()["builder_status"]
    'BuilderStatus.IDLE'

    >>> fixture.tearDown()
    """
    def setUpRoot(self):
        """Recreate empty root directory to avoid problems."""
        if os.path.exists(self.root):
            shutil.rmtree(self.root)
        os.mkdir(self.root)
        filecache = os.path.join(self.root, 'filecache')
        os.mkdir(filecache)
        self.useFixture(EnvironmentVariable('HOME', self.root))
        self.useFixture(
            EnvironmentVariable('BUILDD_SLAVE_CONFIG', test_conffile))
        # XXX cprov 2005-05-30:
        # When we are about running it seriously we need :
        # * install sbuild package
        # * to copy the scripts for sbuild
        self.addCleanup(shutil.rmtree, self.root)

    @property
    def root(self):
        return '/var/tmp/buildd'

    @property
    def tacfile(self):
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            'buildd-slave.tac'
            ))

    @property
    def pidfile(self):
        return os.path.join(self.root, 'build-slave.pid')

    @property
    def logfile(self):
        return '/var/tmp/build-slave.log'

    @property
    def daemon_port(self):
        # This must match buildd-slave-test.conf.
        return 8321

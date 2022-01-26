# Copyright 2021 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import os
try:
    from unittest import mock
except ImportError:
    import mock

from fixtures import (
    EnvironmentVariable,
    TempDir,
    )
from testtools import TestCase
from testtools.deferredruntest import AsynchronousDeferredRunTest
from twisted.internet import defer

from lpbuildd.charm import CharmBuildManager, CharmBuildState
from lpbuildd.tests.fakebuilder import FakeBuilder
from lpbuildd.tests.matchers import HasWaitingFiles


class MockBuildManager(CharmBuildManager):
    def __init__(self, *args, **kwargs):
        super(MockBuildManager, self).__init__(*args, **kwargs)
        self.commands = []
        self.iterators = []

    def runSubProcess(self, path, command, iterate=None, env=None):
        self.commands.append([path] + command)
        if iterate is None:
            iterate = self.iterate
        self.iterators.append(iterate)
        return 0


class TestCharmBuildManagerIteration(TestCase):
    """Run CharmBuildManager through its iteration steps."""

    run_tests_with = AsynchronousDeferredRunTest.make_factory(timeout=5)

    def setUp(self):
        super(TestCharmBuildManagerIteration, self).setUp()
        self.working_dir = self.useFixture(TempDir()).path
        builder_dir = os.path.join(self.working_dir, "builder")
        home_dir = os.path.join(self.working_dir, "home")
        for dir in (builder_dir, home_dir):
            os.mkdir(dir)
        self.useFixture(EnvironmentVariable("HOME", home_dir))
        self.builder = FakeBuilder(builder_dir)
        self.buildid = "123"
        self.buildmanager = MockBuildManager(self.builder, self.buildid)
        self.buildmanager._cachepath = self.builder._cachepath

    def getState(self):
        """Retrieve build manager's state."""
        return self.buildmanager._state

    @defer.inlineCallbacks
    def startBuild(self, args=None, options=None):
        # The build manager's iterate() kicks off the consecutive states
        # after INIT.
        extra_args = {
            "series": "xenial",
            "arch_tag": "i386",
            "name": "test-charm",
            }
        if args is not None:
            extra_args.update(args)
        original_backend_name = self.buildmanager.backend_name
        self.buildmanager.backend_name = "fake"
        self.buildmanager.initiate({}, "chroot.tar.gz", extra_args)
        self.buildmanager.backend_name = original_backend_name

        # Skip states that are done in DebianBuildManager to the state
        # directly before BUILD_CHARM.
        self.buildmanager._state = CharmBuildState.UPDATE

        # BUILD_CHARM: Run the builder's payload to build the charm.
        yield self.buildmanager.iterate(0)
        self.assertEqual(CharmBuildState.BUILD_CHARM, self.getState())
        expected_command = [
            "sharepath/bin/in-target", "in-target", "build-charm",
            "--backend=lxd", "--series=xenial", "--arch=i386", self.buildid,
            ]
        if options is not None:
            expected_command.extend(options)
        expected_command.append("test-charm")
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("chrootFail"))

    def test_status(self):
        # The build manager returns saved status information on request.
        self.assertEqual({}, self.buildmanager.status())
        status_path = os.path.join(
            self.working_dir, "home", "build-%s" % self.buildid, "status")
        os.makedirs(os.path.dirname(status_path))
        with open(status_path, "w") as status_file:
            status_file.write('{"revision_id": "foo"}')
        self.assertEqual({"revision_id": "foo"}, self.buildmanager.status())

    @defer.inlineCallbacks
    def test_iterate(self):
        # The build manager iterates a normal build from start to finish.
        args = {
            "git_repository": "https://git.launchpad.dev/~example/+git/charm",
            "git_path": "master",
            }
        expected_options = [
            "--git-repository",
            "https://git.launchpad.dev/~example/+git/charm",
            "--git-path", "master",
            ]
        yield self.startBuild(args, expected_options)

        log_path = os.path.join(self.buildmanager._cachepath, "buildlog")
        with open(log_path, "w") as log:
            log.write("I am a build log.")

        self.buildmanager.backend.add_file(
            "/home/buildd/test-charm/test-charm_0_all.charm",
            b"I am charming.")

        # After building the package, reap processes.
        yield self.buildmanager.iterate(0)
        expected_command = [
            "sharepath/bin/in-target", "in-target", "scan-for-processes",
            "--backend=lxd", "--series=xenial", "--arch=i386", self.buildid,
            ]

        self.assertEqual(CharmBuildState.BUILD_CHARM, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("buildFail"))
        self.assertThat(self.builder, HasWaitingFiles.byEquality({
            "test-charm_0_all.charm": b"I am charming.",
            }))

        # Control returns to the DebianBuildManager in the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        expected_command = [
            "sharepath/bin/in-target", "in-target", "umount-chroot",
            "--backend=lxd", "--series=xenial", "--arch=i386", self.buildid,
            ]
        self.assertEqual(CharmBuildState.UMOUNT, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("buildFail"))

    @mock.patch('lpbuildd.proxy.urlopen')
    def test_revokeProxyToken(self, urlopen_mock):
        self.buildmanager.revocation_endpoint = "http://revoke_endpoint"
        self.buildmanager.proxy_url = "http://username:password@proxy_url"
        self.buildmanager.revokeProxyToken()
        self.assertEqual(1, urlopen_mock.call_count)
        request = urlopen_mock.call_args[0][0]
        self.assertEqual(
            {'Authorization': "Basic dXNlcm5hbWU6cGFzc3dvcmQ="},
            request.headers)
        self.assertEqual('http://revoke_endpoint', request.get_full_url())

# Copyright 2013-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import os

from fixtures import (
    EnvironmentVariable,
    TempDir,
    )
from testtools import TestCase
from testtools.deferredruntest import AsynchronousDeferredRunTest
from twisted.internet import defer

from lpbuildd.livefs import (
    LiveFilesystemBuildManager,
    LiveFilesystemBuildState,
    )
from lpbuildd.tests.fakebuilder import FakeBuilder
from lpbuildd.tests.matchers import HasWaitingFiles


class MockBuildManager(LiveFilesystemBuildManager):
    def __init__(self, *args, **kwargs):
        super(MockBuildManager, self).__init__(*args, **kwargs)
        self.commands = []
        self.iterators = []

    def runSubProcess(self, path, command, iterate=None):
        self.commands.append([path] + command)
        if iterate is None:
            iterate = self.iterate
        self.iterators.append(iterate)
        return 0


class TestLiveFilesystemBuildManagerIteration(TestCase):
    """Run LiveFilesystemBuildManager through its iteration steps."""

    run_tests_with = AsynchronousDeferredRunTest.make_factory(timeout=5)

    def setUp(self):
        super(TestLiveFilesystemBuildManagerIteration, self).setUp()
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
            "project": "ubuntu",
            "series": "saucy",
            "pocket": "release",
            "arch_tag": "i386",
            }
        if args is not None:
            extra_args.update(args)
        original_backend_name = self.buildmanager.backend_name
        self.buildmanager.backend_name = "fake"
        self.buildmanager.initiate({}, "chroot.tar.gz", extra_args)
        self.buildmanager.backend_name = original_backend_name

        # Skip states that are done in DebianBuildManager to the state
        # directly before BUILD_LIVEFS.
        self.buildmanager._state = LiveFilesystemBuildState.UPDATE

        # BUILD_LIVEFS: Run the builder's payload to build the live filesystem.
        yield self.buildmanager.iterate(0)
        self.assertEqual(
            LiveFilesystemBuildState.BUILD_LIVEFS, self.getState())
        expected_command = [
            "sharepath/bin/in-target", "in-target", "buildlivefs",
            "--backend=lxd", "--series=saucy", "--arch=i386", self.buildid,
            "--project", "ubuntu",
            ]
        if options is not None:
            expected_command.extend(options)
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("chrootFail"))

    @defer.inlineCallbacks
    def test_iterate(self):
        # The build manager iterates a normal build from start to finish.
        yield self.startBuild()

        log_path = os.path.join(self.buildmanager._cachepath, "buildlog")
        with open(log_path, "w") as log:
            log.write("I am a build log.")

        self.buildmanager.backend.add_file(
            "/build/livecd.ubuntu.manifest", b"I am a manifest file.")

        # After building the package, reap processes.
        yield self.buildmanager.iterate(0)
        expected_command = [
            "sharepath/bin/in-target", "in-target", "scan-for-processes",
            "--backend=lxd", "--series=saucy", "--arch=i386", self.buildid,
            ]
        self.assertEqual(
            LiveFilesystemBuildState.BUILD_LIVEFS, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("buildFail"))
        self.assertThat(self.builder, HasWaitingFiles.byEquality({
            "livecd.ubuntu.manifest": b"I am a manifest file.",
            }))

        # Control returns to the DebianBuildManager in the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        expected_command = [
            "sharepath/bin/in-target", "in-target", "umount-chroot",
            "--backend=lxd", "--series=saucy", "--arch=i386", self.buildid,
            ]
        self.assertEqual(LiveFilesystemBuildState.UMOUNT, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("buildFail"))

    @defer.inlineCallbacks
    def test_iterate_extra_ppas_and_snaps(self):
        # The build manager can be told to pass requests for extra PPAs and
        # snaps through to the backend.
        yield self.startBuild(
            args={
                "extra_ppas": ["owner1/name1", "owner2/name2"],
                "extra_snaps": ["snap1", "snap2"],
                },
            options=[
                "--extra-ppa", "owner1/name1",
                "--extra-ppa", "owner2/name2",
                "--extra-snap", "snap1",
                "--extra-snap", "snap2",
                ])

    @defer.inlineCallbacks
    def test_iterate_snap_store_proxy(self):
        # The build manager can be told to use a snap store proxy.
        self.builder._config.set(
            "proxy", "snapstore", "http://snap-store-proxy.example/")
        expected_options = [
            "--snap-store-proxy-url", "http://snap-store-proxy.example/"]
        yield self.startBuild(options=expected_options)

    @defer.inlineCallbacks
    def test_omits_symlinks(self):
        # Symlinks in the build output are not included in gathered results.
        yield self.startBuild()

        log_path = os.path.join(self.buildmanager._cachepath, "buildlog")
        with open(log_path, "w") as log:
            log.write("I am a build log.")

        self.buildmanager.backend.add_file(
            "/build/livecd.ubuntu.kernel-generic", b"I am a kernel.")
        self.buildmanager.backend.add_link(
            "/build/livecd.ubuntu.kernel", "livefs.ubuntu.kernel-generic")

        yield self.buildmanager.iterate(0)
        self.assertThat(self.builder, HasWaitingFiles.byEquality({
            "livecd.ubuntu.kernel-generic": b"I am a kernel.",
            }))

# Copyright 2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

from collections import OrderedDict
import io
import json
import os

from fixtures import (
    EnvironmentVariable,
    MockPatch,
    TempDir,
    )
from testtools import TestCase
from testtools.matchers import Contains
from testtools.deferredruntest import AsynchronousDeferredRunTest
from twisted.internet import defer

from lpbuildd.oci import (
    OCIBuildManager,
    OCIBuildState,
    )
from lpbuildd.tests.fakebuilder import FakeBuilder
from lpbuildd.tests.oci_tarball import OCITarball


class MockBuildManager(OCIBuildManager):
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


class MockOCITarSave():
    @property
    def stdout(self):
        tar_path = OCITarball().build_tar_file()
        return io.open(tar_path, 'rb')


class TestOCIBuildManagerIteration(TestCase):
    """Run OCIBuildManager through its iteration steps."""

    run_tests_with = AsynchronousDeferredRunTest.make_factory(timeout=5)

    def setUp(self):
        super(TestOCIBuildManagerIteration, self).setUp()
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
            "name": "test-image",
            }
        if args is not None:
            extra_args.update(args)
        original_backend_name = self.buildmanager.backend_name
        self.buildmanager.backend_name = "fake"
        self.buildmanager.initiate({}, "chroot.tar.gz", extra_args)
        self.buildmanager.backend_name = original_backend_name

        # Skip states that are done in DebianBuildManager to the state
        # directly before BUILD_OCI.
        self.buildmanager._state = OCIBuildState.UPDATE

        # BUILD_OCI: Run the builder's payload to build the OCI image.
        yield self.buildmanager.iterate(0)
        self.assertEqual(OCIBuildState.BUILD_OCI, self.getState())
        expected_command = [
            "sharepath/bin/in-target", "in-target", "build-oci",
            "--backend=lxd", "--series=xenial", "--arch=i386", self.buildid,
            ]
        if options is not None:
            expected_command.extend(options)
        expected_command.append("test-image")
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("chrootFail"))

    @defer.inlineCallbacks
    def test_iterate(self):
        # This sha would change as it includes file attributes in the
        # tar file. Fix it so we can test against a known value.
        sha_mock = self.useFixture(
            MockPatch('lpbuildd.oci.OCIBuildManager._calculateLayerSha'))
        sha_mock.mock.return_value = "testsha"
        # The build manager iterates a normal build from start to finish.
        args = {
            "git_repository": "https://git.launchpad.dev/~example/+git/snap",
            "git_path": "master",
            }
        expected_options = [
            "--git-repository", "https://git.launchpad.dev/~example/+git/snap",
            "--git-path", "master",
            ]
        yield self.startBuild(args, expected_options)

        log_path = os.path.join(self.buildmanager._cachepath, "buildlog")
        with open(log_path, "w") as log:
            log.write("I am a build log.")

        self.buildmanager.backend.run.result = MockOCITarSave()

        self.buildmanager.backend.add_file(
            '/var/lib/docker/image/'
            'vfs/distribution/v2metadata-by-diffid/sha256/diff1',
            b"""[{"Digest": "test_digest", "SourceRepository": "test"}]""")

        # After building the package, reap processes.
        yield self.buildmanager.iterate(0)
        expected_command = [
            "sharepath/bin/in-target", "in-target", "scan-for-processes",
            "--backend=lxd", "--series=xenial", "--arch=i386", self.buildid,
            ]
        self.assertEqual(OCIBuildState.BUILD_OCI, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("buildFail"))
        expected_files = [
            'manifest.json',
            'layer-1.tar.gz',
            'layer-2.tar.gz',
            'layer-3.tar.gz',
            'digests.json',
            'config.json',
            ]
        for expected in expected_files:
            self.assertThat(self.builder.waitingfiles, Contains(expected))

        cache_path = self.builder.cachePath(
            self.builder.waitingfiles['digests.json'])
        with open(cache_path) as f:
            digests_contents = f.read()
        digests_expected = [{
            "sha256:diff1": {
                "source": "test",
                "digest": "test_digest",
                "layer_id": "layer-1"
            },
            "sha256:diff2": {
                "source": "",
                "digest": "testsha",
                "layer_id": "layer-2"
            },
            "sha256:diff3": {
                "source": "",
                "digest": "testsha",
                "layer_id": "layer-3"
            }
        }]
        self.assertEqual(digests_expected, json.loads(digests_contents))
        # Control returns to the DebianBuildManager in the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        expected_command = [
            "sharepath/bin/in-target", "in-target", "umount-chroot",
            "--backend=lxd", "--series=xenial", "--arch=i386", self.buildid,
            ]
        self.assertEqual(OCIBuildState.UMOUNT, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("buildFail"))

    @defer.inlineCallbacks
    def test_iterate_with_file_and_args(self):
        # This sha would change as it includes file attributes in the
        # tar file. Fix it so we can test against a known value.
        sha_mock = self.useFixture(
            MockPatch('lpbuildd.oci.OCIBuildManager._calculateLayerSha'))
        sha_mock.mock.return_value = "testsha"
        # The build manager iterates a build that specifies a non-default
        # Dockerfile location from start to finish.
        args = {
            "git_repository": "https://git.launchpad.dev/~example/+git/snap",
            "git_path": "master",
            "build_file": "build-aux/Dockerfile",
            "build_args": OrderedDict([("VAR1", "xxx"), ("VAR2", "yyy zzz")]),
            }
        expected_options = [
            "--git-repository", "https://git.launchpad.dev/~example/+git/snap",
            "--git-path", "master",
            "--build-file", "build-aux/Dockerfile",
            "--build-arg", "VAR1=xxx",
            "--build-arg", "VAR2=yyy zzz",
        ]
        yield self.startBuild(args, expected_options)

        log_path = os.path.join(self.buildmanager._cachepath, "buildlog")
        with open(log_path, "w") as log:
            log.write("I am a build log.")

        self.buildmanager.backend.run.result = MockOCITarSave()

        self.buildmanager.backend.add_file(
            '/var/lib/docker/image/'
            'vfs/distribution/v2metadata-by-diffid/sha256/diff1',
            b"""[{"Digest": "test_digest", "SourceRepository": "test"}]"""
        )

        # After building the package, reap processes.
        yield self.buildmanager.iterate(0)
        expected_command = [
            "sharepath/bin/in-target", "in-target", "scan-for-processes",
            "--backend=lxd", "--series=xenial", "--arch=i386", self.buildid,
            ]
        self.assertEqual(OCIBuildState.BUILD_OCI, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("buildFail"))
        expected_files = [
            'manifest.json',
            'layer-1.tar.gz',
            'layer-2.tar.gz',
            'layer-3.tar.gz',
            'digests.json',
            'config.json',
            ]
        for expected in expected_files:
            self.assertThat(self.builder.waitingfiles, Contains(expected))

        cache_path = self.builder.cachePath(
            self.builder.waitingfiles['digests.json'])
        with open(cache_path) as f:
            digests_contents = f.read()
        digests_expected = [{
            "sha256:diff1": {
                "source": "test",
                "digest": "test_digest",
                "layer_id": "layer-1"
            },
            "sha256:diff2": {
                "source": "",
                "digest": "testsha",
                "layer_id": "layer-2"
            },
            "sha256:diff3": {
                "source": "",
                "digest": "testsha",
                "layer_id": "layer-3"
            }
        }]
        self.assertEqual(digests_expected, json.loads(digests_contents))

        # Control returns to the DebianBuildManager in the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        expected_command = [
            "sharepath/bin/in-target", "in-target", "umount-chroot",
            "--backend=lxd", "--series=xenial", "--arch=i386", self.buildid,
            ]
        self.assertEqual(OCIBuildState.UMOUNT, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("buildFail"))

    @defer.inlineCallbacks
    def test_iterate_no_pull(self):
        # check with no pulled images.
        # This sha would change as it includes file attributes in the
        # tar file. Fix it so we can test against a known value.
        sha_mock = self.useFixture(
            MockPatch('lpbuildd.oci.OCIBuildManager._calculateLayerSha'))
        sha_mock.mock.return_value = "testsha"
        # The build manager iterates a normal build from start to finish.
        args = {
            "git_repository": "https://git.launchpad.dev/~example/+git/snap",
            "git_path": "master",
            }
        expected_options = [
            "--git-repository", "https://git.launchpad.dev/~example/+git/snap",
            "--git-path", "master",
            ]
        yield self.startBuild(args, expected_options)

        log_path = os.path.join(self.buildmanager._cachepath, "buildlog")
        with open(log_path, "w") as log:
            log.write("I am a build log.")

        self.buildmanager.backend.run.result = MockOCITarSave()
        yield self.buildmanager.iterate(0)
        self.assertFalse(self.builder.wasCalled("buildFail"))

    @defer.inlineCallbacks
    def test_iterate_snap_store_proxy(self):
        # The build manager can be told to use a snap store proxy.
        self.builder._config.set(
            "proxy", "snapstore", "http://snap-store-proxy.example/")
        expected_options = [
            "--snap-store-proxy-url", "http://snap-store-proxy.example/"]
        yield self.startBuild(options=expected_options)

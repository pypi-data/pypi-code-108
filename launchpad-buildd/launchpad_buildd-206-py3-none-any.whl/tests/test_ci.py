# Copyright 2022 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import os
import shutil

from fixtures import (
    EnvironmentVariable,
    TempDir,
    )
from testtools import TestCase
from testtools.deferredruntest import AsynchronousDeferredRunTest
from twisted.internet import defer

from lpbuildd.builder import get_build_path
from lpbuildd.ci import (
    CIBuildManager,
    CIBuildState,
    )
from lpbuildd.tests.fakebuilder import FakeBuilder
from lpbuildd.tests.matchers import HasWaitingFiles


class MockBuildManager(CIBuildManager):
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


class TestCIBuildManagerIteration(TestCase):
    """Run CIBuildManager through its iteration steps."""

    run_tests_with = AsynchronousDeferredRunTest.make_factory(timeout=5)

    def setUp(self):
        super(TestCIBuildManagerIteration, self).setUp()
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
            "series": "focal",
            "arch_tag": "amd64",
            "name": "test",
            }
        if args is not None:
            extra_args.update(args)
        original_backend_name = self.buildmanager.backend_name
        self.buildmanager.backend_name = "fake"
        self.buildmanager.initiate({}, "chroot.tar.gz", extra_args)
        self.buildmanager.backend_name = original_backend_name

        # Skip states that are done in DebianBuildManager to the state
        # directly before PREPARE.
        self.buildmanager._state = CIBuildState.UPDATE

        # PREPARE: Run the builder's payload to prepare for running CI jobs.
        yield self.buildmanager.iterate(0)
        self.assertEqual(CIBuildState.PREPARE, self.getState())
        expected_command = [
            "sharepath/bin/in-target", "in-target", "run-ci-prepare",
            "--backend=lxd", "--series=focal", "--arch=amd64", self.buildid,
            ]
        if options is not None:
            expected_command.extend(options)
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("chrootFail"))

    @defer.inlineCallbacks
    def expectRunJob(self, job_name, job_index, options=None):
        yield self.buildmanager.iterate(0)
        self.assertEqual(CIBuildState.RUN_JOB, self.getState())
        expected_command = [
            "sharepath/bin/in-target", "in-target", "run-ci",
            "--backend=lxd", "--series=focal", "--arch=amd64", self.buildid,
            ]
        if options is not None:
            expected_command.extend(options)
        expected_command.extend([job_name, job_index])
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("chrootFail"))

    @defer.inlineCallbacks
    def test_iterate(self):
        # The build manager iterates multiple CI jobs from start to finish.
        args = {
            "git_repository": "https://git.launchpad.test/~example/+git/ci",
            "git_path": "main",
            "jobs": [("build", "0"), ("test", "0")],
            }
        expected_options = [
            "--git-repository", "https://git.launchpad.test/~example/+git/ci",
            "--git-path", "main",
            ]
        yield self.startBuild(args, expected_options)

        # After preparation, start running the first job.
        yield self.expectRunJob("build", "0")
        self.buildmanager.backend.add_file(
            "/build/output/build:0.log", b"I am a CI build job log.")
        self.buildmanager.backend.add_file(
            "/build/output/build:0/ci.whl",
            b"I am output from a CI build job.")

        # Collect the output of the first job and start running the second.
        yield self.expectRunJob("test", "0")
        self.buildmanager.backend.add_file(
            "/build/output/test:0.log", b"I am a CI test job log.")
        self.buildmanager.backend.add_file(
            "/build/output/test:0/ci.tar.gz",
            b"I am output from a CI test job.")

        # Output from the first job is visible in the status response.
        extra_status = self.buildmanager.status()
        self.assertEqual(
            {
                "build:0": {
                    "log": self.builder.waitingfiles["build:0.log"],
                    "output": {
                        "ci.whl": self.builder.waitingfiles["build:0/ci.whl"],
                        },
                    },
                },
            extra_status["jobs"])

        # After running the final job, reap processes.
        yield self.buildmanager.iterate(0)
        expected_command = [
            "sharepath/bin/in-target", "in-target", "scan-for-processes",
            "--backend=lxd", "--series=focal", "--arch=amd64", self.buildid,
            ]
        self.assertEqual(CIBuildState.RUN_JOB, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("buildFail"))
        self.assertThat(self.builder, HasWaitingFiles.byEquality({
            "build:0.log": b"I am a CI build job log.",
            "build:0/ci.whl": b"I am output from a CI build job.",
            "test:0.log": b"I am a CI test job log.",
            "test:0/ci.tar.gz": b"I am output from a CI test job.",
            }))

        # Output from both jobs is visible in the status response.
        extra_status = self.buildmanager.status()
        self.assertEqual(
            {
                "build:0": {
                    "log": self.builder.waitingfiles["build:0.log"],
                    "output": {
                        "ci.whl": self.builder.waitingfiles["build:0/ci.whl"],
                        },
                    },
                "test:0": {
                    "log": self.builder.waitingfiles["test:0.log"],
                    "output": {
                        "ci.tar.gz":
                            self.builder.waitingfiles["test:0/ci.tar.gz"],
                        },
                    },
                },
            extra_status["jobs"])

        # Control returns to the DebianBuildManager in the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        expected_command = [
            "sharepath/bin/in-target", "in-target", "umount-chroot",
            "--backend=lxd", "--series=focal", "--arch=amd64", self.buildid,
            ]
        self.assertEqual(CIBuildState.UMOUNT, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled("buildFail"))

        # If we iterate to the end of the build, then the extra status
        # information is still present.
        self.buildmanager.iterate(0)
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'remove-build',
            '--backend=lxd', '--series=focal', '--arch=amd64', self.buildid,
            ]
        self.assertEqual(CIBuildState.CLEANUP, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertTrue(self.builder.wasCalled('buildOK'))
        self.assertTrue(self.builder.wasCalled('buildComplete'))
        # remove-build would remove this in a non-test environment.
        shutil.rmtree(get_build_path(
            self.buildmanager.home, self.buildmanager._buildid))
        self.assertIn("jobs", self.buildmanager.status())

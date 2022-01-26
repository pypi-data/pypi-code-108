# Copyright 2013-2018 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import os
import shutil
import tempfile
from textwrap import dedent

from testtools import TestCase
from testtools.deferredruntest import AsynchronousDeferredRunTest
from twisted.internet import defer

from lpbuildd.sourcepackagerecipe import (
    RETCODE_FAILURE_INSTALL_BUILD_DEPS,
    SourcePackageRecipeBuildManager,
    SourcePackageRecipeBuildState,
    )
from lpbuildd.tests.fakebuilder import FakeBuilder
from lpbuildd.tests.matchers import HasWaitingFiles


class MockBuildManager(SourcePackageRecipeBuildManager):
    def __init__(self, *args, **kwargs):
        super(MockBuildManager, self).__init__(*args, **kwargs)
        self.commands = []
        self.iterators = []

    def runSubProcess(self, path, command, iterate=None):
        self.commands.append([path]+command)
        if iterate is None:
            iterate = self.iterate
        self.iterators.append(iterate)
        return 0


class TestSourcePackageRecipeBuildManagerIteration(TestCase):
    """Run SourcePackageRecipeBuildManager through its iteration steps."""

    run_tests_with = AsynchronousDeferredRunTest.make_factory(timeout=5)

    def setUp(self):
        super(TestSourcePackageRecipeBuildManagerIteration, self).setUp()
        self.working_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.working_dir))
        builder_dir = os.path.join(self.working_dir, 'builder')
        home_dir = os.path.join(self.working_dir, 'home')
        for dir in (builder_dir, home_dir):
            os.mkdir(dir)
        self.builder = FakeBuilder(builder_dir)
        self.buildid = '123'
        self.buildmanager = MockBuildManager(self.builder, self.buildid)
        self.buildmanager.home = home_dir
        self.buildmanager._cachepath = self.builder._cachepath
        self.chrootdir = os.path.join(
            home_dir, 'build-%s' % self.buildid, 'chroot-autobuild')

    def getState(self):
        """Retrieve build manager's state."""
        return self.buildmanager._state

    @defer.inlineCallbacks
    def startBuild(self, git=False):
        # The build manager's iterate() kicks off the consecutive states
        # after INIT.
        extra_args = {
            'recipe_text': dedent("""\
                # bzr-builder format 0.2 deb-version {debupstream}-0~{revno}
                http://bazaar.launchpad.dev/~ppa-user/+junk/wakeonlan"""),
            'series': 'maverick',
            'suite': 'maverick',
            'ogrecomponent': 'universe',
            'author_name': 'Steve\u1234',
            'author_email': 'stevea@example.org',
            'archive_purpose': 'puppies',
            'distroseries_name': 'maverick',
            'archives': [
                'deb http://archive.ubuntu.com/ubuntu maverick main universe',
                'deb http://ppa.launchpad.net/launchpad/bzr-builder-dev/'
                'ubuntu main',
                ],
            }
        if git:
            extra_args['git'] = True
        self.buildmanager.initiate({}, 'chroot.tar.gz', extra_args)

        # Skip states that are done in DebianBuildManager to the state
        # directly before BUILD_RECIPE.
        self.buildmanager._state = SourcePackageRecipeBuildState.UPDATE

        # BUILD_RECIPE: Run the builder's payload to build the source package.
        yield self.buildmanager.iterate(0)
        self.assertEqual(
            SourcePackageRecipeBuildState.BUILD_RECIPE, self.getState())
        expected_command = ['sharepath/bin/buildrecipe', 'buildrecipe']
        if git:
            expected_command.append('--git')
        expected_command.extend([
            self.buildid,
            'Steve\u1234'.encode('utf-8'), 'stevea@example.org',
            'maverick', 'maverick', 'universe', 'puppies',
            ])
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled('chrootFail'))

    @defer.inlineCallbacks
    def test_iterate(self):
        # The build manager iterates a normal build from start to finish.
        yield self.startBuild()

        log_path = os.path.join(self.buildmanager._cachepath, 'buildlog')
        with open(log_path, 'w') as log:
            log.write("I am a build log.")

        changes_path = os.path.join(
            self.buildmanager.home, 'build-%s' % self.buildid,
            'foo_1_source.changes')
        with open(changes_path, 'w') as changes:
            changes.write("I am a changes file.")

        manifest_path = os.path.join(
            self.buildmanager.home, 'build-%s' % self.buildid, 'manifest')
        with open(manifest_path, 'w') as manifest:
            manifest.write("I am a manifest file.")

        # After building the package, reap processes.
        yield self.buildmanager.iterate(0)
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'scan-for-processes',
            '--backend=chroot', '--series=maverick', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(
            SourcePackageRecipeBuildState.BUILD_RECIPE, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled('buildFail'))
        self.assertThat(self.builder, HasWaitingFiles.byEquality({
            'foo_1_source.changes': b'I am a changes file.',
            'manifest': b'I am a manifest file.',
            }))

        # Control returns to the DebianBuildManager in the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'umount-chroot',
            '--backend=chroot', '--series=maverick', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(SourcePackageRecipeBuildState.UMOUNT, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled('buildFail'))

    @defer.inlineCallbacks
    def test_iterate_BUILD_RECIPE_install_build_deps_depfail(self):
        # The build manager can detect dependency wait states.
        yield self.startBuild()

        log_path = os.path.join(self.buildmanager._cachepath, 'buildlog')
        with open(log_path, 'w') as log:
            log.write(
                "The following packages have unmet dependencies:\n"
                " pbuilder-satisfydepends-dummy :"
                " Depends: base-files (>= 1000)"
                " but it is not going to be installed.\n")

        # The buildmanager calls depFail correctly and reaps processes.
        yield self.buildmanager.iterate(RETCODE_FAILURE_INSTALL_BUILD_DEPS)
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'scan-for-processes',
            '--backend=chroot', '--series=maverick', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(
            SourcePackageRecipeBuildState.BUILD_RECIPE, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled('buildFail'))
        self.assertEqual(
            [(("base-files (>= 1000)",), {})], self.builder.depFail.calls)

        # Control returns to the DebianBuildManager in the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'umount-chroot',
            '--backend=chroot', '--series=maverick', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(SourcePackageRecipeBuildState.UMOUNT, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled('buildFail'))

    @defer.inlineCallbacks
    def test_iterate_BUILD_RECIPE_install_build_deps_buildfail(self):
        # If the build manager cannot detect a dependency wait from a
        # build-dependency installation failure, it fails the build.
        yield self.startBuild()

        log_path = os.path.join(self.buildmanager._cachepath, 'buildlog')
        with open(log_path, 'w') as log:
            log.write("I am a failing build log.")

        # The buildmanager calls buildFail correctly and reaps processes.
        yield self.buildmanager.iterate(RETCODE_FAILURE_INSTALL_BUILD_DEPS)
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'scan-for-processes',
            '--backend=chroot', '--series=maverick', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(
            SourcePackageRecipeBuildState.BUILD_RECIPE, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertTrue(self.builder.wasCalled('buildFail'))
        self.assertFalse(self.builder.wasCalled('depFail'))

        # Control returns to the DebianBuildManager in the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'umount-chroot',
            '--backend=chroot', '--series=maverick', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(SourcePackageRecipeBuildState.UMOUNT, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

    @defer.inlineCallbacks
    def test_iterate_git(self):
        # Starting a git-based recipe build passes the correct option.  (The
        # rest of the build is identical to bzr-based recipe builds from the
        # build manager's point of view.)
        yield self.startBuild(git=True)

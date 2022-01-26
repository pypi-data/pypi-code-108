# Copyright 2010-2018 Canonical Ltd.  This software is licensed under the
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

from lpbuildd.target.generate_translation_templates import (
    RETCODE_FAILURE_BUILD,
    RETCODE_FAILURE_INSTALL,
    )
from lpbuildd.tests.fakebuilder import FakeBuilder
from lpbuildd.tests.matchers import HasWaitingFiles
from lpbuildd.translationtemplates import (
    TranslationTemplatesBuildManager,
    TranslationTemplatesBuildState,
    )


class MockBuildManager(TranslationTemplatesBuildManager):
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


class TestTranslationTemplatesBuildManagerIteration(TestCase):
    """Run TranslationTemplatesBuildManager through its iteration steps."""

    run_tests_with = AsynchronousDeferredRunTest.make_factory(timeout=5)

    def setUp(self):
        super(TestTranslationTemplatesBuildManagerIteration, self).setUp()
        self.working_dir = self.useFixture(TempDir()).path
        builder_dir = os.path.join(self.working_dir, 'builder')
        home_dir = os.path.join(self.working_dir, 'home')
        for dir in (builder_dir, home_dir):
            os.mkdir(dir)
        self.useFixture(EnvironmentVariable("HOME", home_dir))
        self.builder = FakeBuilder(builder_dir)
        self.buildid = '123'
        self.buildmanager = MockBuildManager(self.builder, self.buildid)
        self.chrootdir = os.path.join(
            home_dir, 'build-%s' % self.buildid, 'chroot-autobuild')

    def getState(self):
        """Retrieve build manager's state."""
        return self.buildmanager._state

    @defer.inlineCallbacks
    def test_iterate(self):
        # Two iteration steps are specific to this build manager.
        url = 'lp:~my/branch'
        # The build manager's iterate() kicks off the consecutive states
        # after INIT.
        original_backend_name = self.buildmanager.backend_name
        self.buildmanager.backend_name = "fake"
        self.buildmanager.initiate(
            {}, 'chroot.tar.gz', {'series': 'xenial', 'branch_url': url})
        self.buildmanager.backend_name = original_backend_name

        # Skip states that are done in DebianBuildManager to the state
        # directly before GENERATE.
        self.buildmanager._state = TranslationTemplatesBuildState.UPDATE

        # GENERATE: Run the builder's payload, the script that generates
        # templates.
        yield self.buildmanager.iterate(0)
        self.assertEqual(
            TranslationTemplatesBuildState.GENERATE, self.getState())
        expected_command = [
            'sharepath/bin/in-target', 'in-target',
            'generate-translation-templates',
            '--backend=chroot', '--series=xenial', '--arch=i386',
            self.buildid,
            '--branch', url, 'resultarchive',
            ]
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled('chrootFail'))

        outfile_path = os.path.join(
            self.buildmanager.home, self.buildmanager._resultname)
        self.buildmanager.backend.add_file(
            outfile_path, b"I am a template tarball. Seriously.")

        # After generating templates, reap processes.
        yield self.buildmanager.iterate(0)
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'scan-for-processes',
            '--backend=chroot', '--series=xenial', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(
            TranslationTemplatesBuildState.GENERATE, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled('buildFail'))
        self.assertThat(self.builder, HasWaitingFiles.byEquality({
            self.buildmanager._resultname: (
                b'I am a template tarball. Seriously.'),
            }))

        # The control returns to the DebianBuildManager in the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'umount-chroot',
            '--backend=chroot', '--series=xenial', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(
            TranslationTemplatesBuildState.UMOUNT, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertFalse(self.builder.wasCalled('buildFail'))

    @defer.inlineCallbacks
    def test_iterate_fail_GENERATE_install(self):
        # See that a GENERATE that fails at the install step is handled
        # properly.
        url = 'lp:~my/branch'
        # The build manager's iterate() kicks off the consecutive states
        # after INIT.
        self.buildmanager.initiate(
            {}, 'chroot.tar.gz', {'series': 'xenial', 'branch_url': url})

        # Skip states to the GENERATE state.
        self.buildmanager._state = TranslationTemplatesBuildState.GENERATE

        # The buildmanager fails and reaps processes.
        yield self.buildmanager.iterate(RETCODE_FAILURE_INSTALL)
        self.assertEqual(
            TranslationTemplatesBuildState.GENERATE, self.getState())
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'scan-for-processes',
            '--backend=chroot', '--series=xenial', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertTrue(self.builder.wasCalled('chrootFail'))

        # The buildmanager iterates to the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        self.assertEqual(
            TranslationTemplatesBuildState.UMOUNT, self.getState())
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'umount-chroot',
            '--backend=chroot', '--series=xenial', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

    @defer.inlineCallbacks
    def test_iterate_fail_GENERATE_build(self):
        # See that a GENERATE that fails at the build step is handled
        # properly.
        url = 'lp:~my/branch'
        # The build manager's iterate() kicks off the consecutive states
        # after INIT.
        self.buildmanager.initiate(
            {}, 'chroot.tar.gz', {'series': 'xenial', 'branch_url': url})

        # Skip states to the GENERATE state.
        self.buildmanager._state = TranslationTemplatesBuildState.GENERATE

        # The buildmanager fails and reaps processes.
        yield self.buildmanager.iterate(RETCODE_FAILURE_BUILD)
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'scan-for-processes',
            '--backend=chroot', '--series=xenial', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(
            TranslationTemplatesBuildState.GENERATE, self.getState())
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])
        self.assertTrue(self.builder.wasCalled('buildFail'))

        # The buildmanager iterates to the UMOUNT state.
        self.buildmanager.iterateReap(self.getState(), 0)
        self.assertEqual(
            TranslationTemplatesBuildState.UMOUNT, self.getState())
        expected_command = [
            'sharepath/bin/in-target', 'in-target', 'umount-chroot',
            '--backend=chroot', '--series=xenial', '--arch=i386',
            self.buildid,
            ]
        self.assertEqual(expected_command, self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

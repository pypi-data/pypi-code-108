# Copyright 2017-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import base64
import os.path
import shutil
import tempfile

from testtools import TestCase
from twisted.internet.task import Clock

from lpbuildd.debian import (
    DebianBuildManager,
    DebianBuildState,
    )
from lpbuildd.tests.fakebuilder import FakeBuilder


class MockBuildState(DebianBuildState):

    MAIN = "MAIN"


class MockBuildManager(DebianBuildManager):

    initial_build_state = MockBuildState.MAIN

    def __init__(self, *args, **kwargs):
        super(MockBuildManager, self).__init__(*args, **kwargs)
        self.commands = []
        self.iterators = []
        self.arch_indep = False

    def runSubProcess(self, path, command, iterate=None, stdin=None):
        self.commands.append(([path] + command, stdin))
        if iterate is None:
            iterate = self.iterate
        self.iterators.append(iterate)
        return 0

    def doRunBuild(self):
        self.runSubProcess('/bin/true', ['true'])

    def iterate_MAIN(self, success):
        if success != 0:
            if not self.alreadyfailed:
                self._builder.buildFail()
            self.alreadyfailed = True
        self.doReapProcesses(self._state)

    def iterateReap_MAIN(self, success):
        self._state = DebianBuildState.UMOUNT
        self.doUnmounting()


class TestDebianBuildManagerIteration(TestCase):
    """Run a generic DebianBuildManager through its iteration steps."""

    def setUp(self):
        super(TestDebianBuildManagerIteration, self).setUp()
        self.working_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.working_dir))
        builder_dir = os.path.join(self.working_dir, 'builder')
        home_dir = os.path.join(self.working_dir, 'home')
        for dir in (builder_dir, home_dir):
            os.mkdir(dir)
        self.builder = FakeBuilder(builder_dir)
        self.buildid = '123'
        self.clock = Clock()
        self.buildmanager = MockBuildManager(
            self.builder, self.buildid, reactor=self.clock)
        self.buildmanager.home = home_dir
        self.buildmanager._cachepath = self.builder._cachepath
        self.chrootdir = os.path.join(
            home_dir, 'build-%s' % self.buildid, 'chroot-autobuild')

    def getState(self):
        """Retrieve build manager's state."""
        return self.buildmanager._state

    def startBuild(self, extra_args):
        # The build manager's iterate() kicks off the consecutive states
        # after INIT.
        self.buildmanager.initiate({}, 'chroot.tar.gz', extra_args)
        self.assertEqual(DebianBuildState.INIT, self.getState())
        self.assertEqual(
            (['sharepath/bin/builder-prep', 'builder-prep'], None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

    def test_iterate(self):
        # The build manager iterates a normal build from start to finish.
        extra_args = {
            'arch_tag': 'amd64',
            'archives': [
                'deb http://ppa.launchpad.dev/owner/name/ubuntu xenial main',
                ],
            'series': 'xenial',
            }
        self.startBuild(extra_args)

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.UNPACK, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'unpack-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid,
              '--image-type', 'chroot',
              os.path.join(self.buildmanager._cachepath, 'chroot.tar.gz')],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.MOUNT, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'mount-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.SOURCES, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'override-sources-list',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid,
              'deb http://ppa.launchpad.dev/owner/name/ubuntu xenial main'],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.UPDATE, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'update-debian-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(MockBuildState.MAIN, self.getState())
        self.assertEqual(
            (['/bin/true', 'true'], None), self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(MockBuildState.MAIN, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'scan-for-processes',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterateReap(self.getState(), 0)
        self.assertEqual(DebianBuildState.UMOUNT, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'umount-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.CLEANUP, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'remove-build',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertFalse(self.builder.wasCalled('builderFail'))
        self.assertFalse(self.builder.wasCalled('chrootFail'))
        self.assertFalse(self.builder.wasCalled('buildFail'))
        self.assertFalse(self.builder.wasCalled('depFail'))
        self.assertTrue(self.builder.wasCalled('buildOK'))
        self.assertTrue(self.builder.wasCalled('buildComplete'))

    def test_iterate_trusted_keys(self):
        # The build manager iterates a build with trusted keys from start to
        # finish.
        extra_args = {
            'arch_tag': 'amd64',
            'archives': [
                'deb http://ppa.launchpad.dev/owner/name/ubuntu xenial main',
                ],
            'series': 'xenial',
            'trusted_keys': [base64.b64encode(b'key material')],
            }
        self.startBuild(extra_args)

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.UNPACK, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'unpack-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid,
              '--image-type', 'chroot',
              os.path.join(self.buildmanager._cachepath, 'chroot.tar.gz')],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.MOUNT, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'mount-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.SOURCES, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'override-sources-list',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid,
              'deb http://ppa.launchpad.dev/owner/name/ubuntu xenial main'],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.KEYS, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'add-trusted-keys',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             b'key material'),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.UPDATE, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'update-debian-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(MockBuildState.MAIN, self.getState())
        self.assertEqual(
            (['/bin/true', 'true'], None), self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(MockBuildState.MAIN, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'scan-for-processes',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterateReap(self.getState(), 0)
        self.assertEqual(DebianBuildState.UMOUNT, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'umount-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.CLEANUP, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'remove-build',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertFalse(self.builder.wasCalled('builderFail'))
        self.assertFalse(self.builder.wasCalled('chrootFail'))
        self.assertFalse(self.builder.wasCalled('buildFail'))
        self.assertFalse(self.builder.wasCalled('depFail'))
        self.assertTrue(self.builder.wasCalled('buildOK'))
        self.assertTrue(self.builder.wasCalled('buildComplete'))

    def test_iterate_fast_cleanup(self):
        # The build manager can be told that it doesn't need to do the final
        # cleanup steps, because the VM is about to be torn down anyway.  It
        # iterates such a build from start to finish, but without calling
        # umount-chroot or remove-build.
        extra_args = {
            'arch_tag': 'amd64',
            'archives': [
                'deb http://ppa.launchpad.dev/owner/name/ubuntu xenial main',
                ],
            'fast_cleanup': True,
            'series': 'xenial',
            }
        self.startBuild(extra_args)

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.UNPACK, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'unpack-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid,
              '--image-type', 'chroot',
              os.path.join(self.buildmanager._cachepath, 'chroot.tar.gz')],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.MOUNT, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'mount-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.SOURCES, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'override-sources-list',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid,
              'deb http://ppa.launchpad.dev/owner/name/ubuntu xenial main'],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.UPDATE, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'update-debian-chroot',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(MockBuildState.MAIN, self.getState())
        self.assertEqual(
            (['/bin/true', 'true'], None), self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterate(0)
        self.assertEqual(MockBuildState.MAIN, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'scan-for-processes',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid],
             None),
            self.buildmanager.commands[-1])
        self.assertNotEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

        self.buildmanager.iterateReap(self.getState(), 0)
        self.assertFalse(self.builder.wasCalled('builderFail'))
        self.assertFalse(self.builder.wasCalled('chrootFail'))
        self.assertFalse(self.builder.wasCalled('buildFail'))
        self.assertFalse(self.builder.wasCalled('depFail'))
        self.assertTrue(self.builder.wasCalled('buildOK'))
        self.assertTrue(self.builder.wasCalled('buildComplete'))

    def test_iterate_apt_proxy(self):
        # The build manager can be configured to use an APT proxy.
        self.builder._config.set(
            'proxy', 'apt', 'http://apt-proxy.example:3128/')
        extra_args = {
            'arch_tag': 'amd64',
            'archives': [
                'deb http://ppa.launchpad.dev/owner/name/ubuntu xenial main',
                ],
            'series': 'xenial',
            }
        self.startBuild(extra_args)

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.UNPACK, self.getState())
        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.MOUNT, self.getState())
        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.SOURCES, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'override-sources-list',
              '--backend=chroot', '--series=xenial', '--arch=amd64',
              self.buildid,
              '--apt-proxy-url', 'http://apt-proxy.example:3128/',
              'deb http://ppa.launchpad.dev/owner/name/ubuntu xenial main'],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

    def test_iterate_lxd(self):
        # The build manager passes the image_type argument through to
        # unpack-chroot.
        self.buildmanager.backend_name = 'lxd'
        extra_args = {
            'image_type': 'lxd',
            'arch_tag': 'amd64',
            'series': 'xenial',
            }
        self.startBuild(extra_args)

        self.buildmanager.iterate(0)
        self.assertEqual(DebianBuildState.UNPACK, self.getState())
        self.assertEqual(
            (['sharepath/bin/in-target', 'in-target', 'unpack-chroot',
              '--backend=lxd', '--series=xenial', '--arch=amd64',
              self.buildid,
              '--image-type', 'lxd',
              os.path.join(self.buildmanager._cachepath, 'chroot.tar.gz')],
             None),
            self.buildmanager.commands[-1])
        self.assertEqual(
            self.buildmanager.iterate, self.buildmanager.iterators[-1])

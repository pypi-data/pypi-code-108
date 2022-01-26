# Copyright 2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

from textwrap import dedent

from fixtures import FakeLogger
from testtools import TestCase
from testtools.matchers import StartsWith

from lpbuildd.target.backend import BackendException
from lpbuildd.target.cli import parse_args


class TestCreate(TestCase):

    def test_succeeds(self):
        args = [
            "unpack-chroot",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "/path/to/tarball",
            ]
        create = parse_args(args=args).operation
        self.assertEqual(0, create.run())
        self.assertEqual(
            [(("/path/to/tarball", "chroot"), {})],
            create.backend.create.calls)

    def test_image_type(self):
        args = [
            "unpack-chroot",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--image-type", "lxd", "/path/to/tarball",
            ]
        create = parse_args(args=args).operation
        self.assertEqual(0, create.run())
        self.assertEqual(
            [(("/path/to/tarball", "lxd"), {})],
            create.backend.create.calls)


class TestStart(TestCase):

    def test_succeeds(self):
        args = [
            "mount-chroot",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            ]
        start = parse_args(args=args).operation
        self.assertEqual(0, start.run())
        self.assertEqual([((), {})], start.backend.start.calls)


class TestKillProcesses(TestCase):

    def test_succeeds(self):
        args = [
            "scan-for-processes",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            ]
        kill_processes = parse_args(args=args).operation
        self.assertEqual(0, kill_processes._run())
        self.assertEqual(
            [((), {})], kill_processes.backend.kill_processes.calls)


class TestStop(TestCase):

    def test_succeeds(self):
        args = [
            "umount-chroot",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            ]
        stop = parse_args(args=args).operation
        self.assertEqual(0, stop.run())
        self.assertEqual([((), {})], stop.backend.stop.calls)

    def test_fails(self):
        logger = self.useFixture(FakeLogger())
        args = [
            "umount-chroot",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            ]
        stop = parse_args(args=args).operation
        stop.backend.stop.failure = BackendException
        self.assertEqual(1, stop.run())
        self.assertEqual([((), {})], stop.backend.stop.calls)
        self.assertThat(logger.output, StartsWith(dedent("""\
            Stopping target for build 1
            Failed to stop target
            Traceback (most recent call last):
            """)))


class TestRemove(TestCase):

    def test_succeeds(self):
        args = [
            "remove-build",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            ]
        remove = parse_args(args=args).operation
        self.assertEqual(0, remove.run())
        self.assertEqual([((), {})], remove.backend.remove.calls)

# Copyright 2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import io
import os.path
import signal
from textwrap import dedent
import time

from fixtures import (
    EnvironmentVariable,
    TempDir,
    )
import six
from systemfixtures import (
    FakeProcesses,
    FakeTime,
    )
from testtools import TestCase
from testtools.matchers import DirContains

from lpbuildd.target.backend import BackendException
from lpbuildd.target.chroot import Chroot
from lpbuildd.target.tests.testfixtures import (
    CarefulFakeProcessFixture,
    FakeFilesystem,
    KillFixture,
    SudoUmount,
    )


class TestChroot(TestCase):

    def setUp(self):
        super(TestChroot, self).setUp()
        self.useFixture(CarefulFakeProcessFixture())

    def test_create(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(lambda _: {}, name="sudo")
        Chroot("1", "xenial", "amd64").create("/path/to/tarball", "chroot")

        expected_args = [
            ["sudo", "tar", "-C", "/expected/home/build-1",
             "-xf", "/path/to/tarball"],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_start(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(lambda _: {}, name="sudo")
        fs_fixture = self.useFixture(FakeFilesystem())
        fs_fixture.add("/etc")
        os.mkdir("/etc")
        for etc_name in ("hosts", "hostname", "resolv.conf.real"):
            with open(os.path.join("/etc", etc_name), "w") as etc_file:
                etc_file.write("%s\n" % etc_name)
            os.chmod(os.path.join("/etc", etc_name), 0o644)
        os.symlink("resolv.conf.real", "/etc/resolv.conf")
        Chroot("1", "xenial", "amd64").start()

        expected_args = [
            ["sudo", "mount", "-t", "proc", "none",
             "/expected/home/build-1/chroot-autobuild/proc"],
            ["sudo", "mount", "-t", "devpts", "-o", "gid=5,mode=620", "none",
             "/expected/home/build-1/chroot-autobuild/dev/pts"],
            ["sudo", "mount", "-t", "sysfs", "none",
             "/expected/home/build-1/chroot-autobuild/sys"],
            ["sudo", "mount", "-t", "tmpfs", "none",
             "/expected/home/build-1/chroot-autobuild/dev/shm"],
            ["sudo", "install", "-o", "root", "-g", "root", "-m", "644",
             "/etc/hosts",
             "/expected/home/build-1/chroot-autobuild/etc/hosts"],
            ["sudo", "install", "-o", "root", "-g", "root", "-m", "644",
             "/etc/hostname",
             "/expected/home/build-1/chroot-autobuild/etc/hostname"],
            ["sudo", "install", "-o", "root", "-g", "root", "-m", "644",
             "/etc/resolv.conf",
             "/expected/home/build-1/chroot-autobuild/etc/resolv.conf"],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_run(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(lambda _: {}, name="sudo")
        Chroot("1", "xenial", "amd64").run(
            ["apt-get", "update"], env={"LANG": "C"})

        expected_args = [
            ["sudo", "/usr/sbin/chroot",
             "/expected/home/build-1/chroot-autobuild",
             "linux64", "env", "LANG=C", "apt-get", "update"],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_run_get_output(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(
            lambda _: {"stdout": io.BytesIO(b"hello\n")}, name="sudo")
        self.assertEqual(
            b"hello\n",
            Chroot("1", "xenial", "amd64").run(
                ["echo", "hello"], get_output=True))

        expected_args = [
            ["sudo", "/usr/sbin/chroot",
             "/expected/home/build-1/chroot-autobuild",
             "linux64", "echo", "hello"],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_run_non_ascii_arguments(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(lambda _: {}, name="sudo")
        arg = u"\N{SNOWMAN}"
        Chroot("1", "xenial", "amd64").run(["echo", arg])

        expected_args = [
            ["sudo", "/usr/sbin/chroot",
             "/expected/home/build-1/chroot-autobuild",
             "linux64", "echo", arg.encode("UTF-8") if six.PY2 else arg],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_run_env_shell_metacharacters(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(lambda _: {}, name="sudo")
        Chroot("1", "xenial", "amd64").run(
            ["echo", "hello"], env={"OBJECT": "{'foo': 'bar'}"})

        expected_args = [
            ["sudo", "/usr/sbin/chroot",
             "/expected/home/build-1/chroot-autobuild",
             "linux64", "env", "OBJECT={'foo': 'bar'}", "echo", "hello"],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_copy_in(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        source_dir = self.useFixture(TempDir()).path
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(lambda _: {}, name="sudo")
        source_path = os.path.join(source_dir, "source")
        with open(source_path, "w"):
            pass
        os.chmod(source_path, 0o644)
        target_path = "/path/to/target"
        Chroot("1", "xenial", "amd64").copy_in(source_path, target_path)

        expected_target_path = (
            "/expected/home/build-1/chroot-autobuild/path/to/target")
        expected_args = [
            ["sudo", "install", "-o", "root", "-g", "root", "-m", "644",
             source_path, expected_target_path],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_copy_out(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(lambda _: {}, name="sudo")
        Chroot("1", "xenial", "amd64").copy_out(
            "/path/to/source", "/path/to/target")

        expected_args = [
            ["sudo", "cp", "--preserve=timestamps",
             "/expected/home/build-1/chroot-autobuild/path/to/source",
             "/path/to/target"],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_path_exists(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        test_proc_infos = iter([{}, {"returncode": 1}])
        processes_fixture.add(lambda _: next(test_proc_infos), name="sudo")
        self.assertTrue(Chroot("1", "xenial", "amd64").path_exists("/present"))
        self.assertFalse(Chroot("1", "xenial", "amd64").path_exists("/absent"))

        expected_args = [
            ["sudo", "/usr/sbin/chroot",
             "/expected/home/build-1/chroot-autobuild",
             "linux64", "test", "-e", path]
            for path in ("/present", "/absent")
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_isdir(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        test_proc_infos = iter([{}, {"returncode": 1}])
        processes_fixture.add(lambda _: next(test_proc_infos), name="sudo")
        self.assertTrue(Chroot("1", "xenial", "amd64").isdir("/dir"))
        self.assertFalse(Chroot("1", "xenial", "amd64").isdir("/file"))

        expected_args = [
            ["sudo", "/usr/sbin/chroot",
             "/expected/home/build-1/chroot-autobuild",
             "linux64", "test", "-d", path]
            for path in ("/dir", "/file")
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_islink(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        test_proc_infos = iter([{}, {"returncode": 1}])
        processes_fixture.add(lambda _: next(test_proc_infos), name="sudo")
        self.assertTrue(Chroot("1", "xenial", "amd64").islink("/link"))
        self.assertFalse(Chroot("1", "xenial", "amd64").islink("/file"))

        expected_args = [
            ["sudo", "/usr/sbin/chroot",
             "/expected/home/build-1/chroot-autobuild",
             "linux64", "test", "-h", path]
            for path in ("/link", "/file")
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_find(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        test_proc_infos = iter([
            {"stdout": io.BytesIO(b"foo\0bar\0bar/bar\0bar/baz\0")},
            {"stdout": io.BytesIO(b"foo\0bar\0")},
            {"stdout": io.BytesIO(b"foo\0bar/bar\0bar/baz\0")},
            {"stdout": io.BytesIO(b"bar\0bar/bar\0")},
            {"stdout": io.BytesIO(b"")},
            ])
        processes_fixture.add(lambda _: next(test_proc_infos), name="sudo")
        self.assertEqual(
            ["foo", "bar", "bar/bar", "bar/baz"],
            Chroot("1", "xenial", "amd64").find("/path"))
        self.assertEqual(
            ["foo", "bar"],
            Chroot("1", "xenial", "amd64").find("/path", max_depth=1))
        self.assertEqual(
            ["foo", "bar/bar", "bar/baz"],
            Chroot("1", "xenial", "amd64").find(
                "/path", include_directories=False))
        self.assertEqual(
            ["bar", "bar/bar"],
            Chroot("1", "xenial", "amd64").find("/path", name="bar"))
        self.assertEqual(
            [],
            Chroot("1", "xenial", "amd64").find("/path", name="nonexistent"))

        find_prefix = [
            "sudo", "/usr/sbin/chroot",
            "/expected/home/build-1/chroot-autobuild",
            "linux64", "find", "/path", "-mindepth", "1",
            ]
        find_suffix = ["-printf", "%P\\0"]
        expected_args = [
            find_prefix + find_suffix,
            find_prefix + ["-maxdepth", "1"] + find_suffix,
            find_prefix + ["!", "-type", "d"] + find_suffix,
            find_prefix + ["-name", "bar"] + find_suffix,
            find_prefix + ["-name", "nonexistent"] + find_suffix,
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_listdir(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(
            lambda _: {"stdout": io.BytesIO(b"foo\0bar\0baz\0")}, name="sudo")
        self.assertEqual(
            ["foo", "bar", "baz"],
            Chroot("1", "xenial", "amd64").listdir("/path"))

        expected_args = [
            ["sudo", "/usr/sbin/chroot",
             "/expected/home/build-1/chroot-autobuild",
             "linux64", "find", "/path", "-mindepth", "1", "-maxdepth", "1",
             "-printf", "%P\\0"],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_is_package_available(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        test_proc_infos = iter([
            {"stdout": io.StringIO(u"Package: snapd\n")},
            {"returncode": 100},
            {"stderr": io.StringIO(u"N: No packages found\n")},
            ])
        processes_fixture.add(lambda _: next(test_proc_infos), name="sudo")
        self.assertTrue(
            Chroot("1", "xenial", "amd64").is_package_available("snapd"))
        self.assertFalse(
            Chroot("1", "xenial", "amd64").is_package_available("nonexistent"))
        self.assertFalse(
            Chroot("1", "xenial", "amd64").is_package_available("virtual"))

        expected_args = [
            ["sudo", "/usr/sbin/chroot",
             "/expected/home/build-1/chroot-autobuild",
             "linux64", "apt-cache", "show", package]
            for package in ("snapd", "nonexistent", "virtual")
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

    def test_kill_processes(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        fs_fixture = self.useFixture(FakeFilesystem())
        fs_fixture.add("/expected")
        os.makedirs("/expected/home/build-1/chroot-autobuild")
        fs_fixture.add("/proc")
        fs_fixture.remove("/proc/self/fd")
        os.mkdir("/proc")
        os.mkdir("/proc/1")
        os.symlink("/", "/proc/1/root")
        os.mkdir("/proc/10")
        os.symlink("/expected/home/build-1/chroot-autobuild", "/proc/10/root")
        os.mkdir("/proc/11")
        os.symlink("/expected/home/build-1/chroot-autobuild", "/proc/11/root")
        os.mkdir("/proc/12")
        os.symlink(
            "/expected/home/build-1/chroot-autobuild/submount",
            "/proc/12/root")
        os.mkdir("/proc/13")
        os.symlink(
            "/expected/home/build-1/chroot-autobuildsomething",
            "/proc/13/root")
        with open("/proc/version", "w"):
            pass
        kill_fixture = self.useFixture(KillFixture(delays={10: 1}))
        Chroot("1", "xenial", "amd64").kill_processes()

        self.assertEqual(
            [(pid, signal.SIGKILL) for pid in (11, 12, 10)],
            kill_fixture.kills)
        self.assertThat("/proc", DirContains(["1", "13", "version"]))

    def _make_initial_proc_mounts(self):
        fs_fixture = self.useFixture(FakeFilesystem())
        fs_fixture.add("/proc")
        fs_fixture.remove("/proc/self/fd")
        os.mkdir("/proc")
        with open("/proc/mounts", "w") as mounts_file:
            mounts_file.write(dedent("""\
                sysfs /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
                proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
                none {chroot}/proc proc rw,relatime 0 0
                none {chroot}/dev/pts devpts rw,relative,gid=5,mode=620 0 0
                none {chroot}/sys sysfs rw,relatime 0 0
                none {chroot}/dev/shm tmpfs rw,relatime 0 0
                """.format(chroot="/expected/home/build-1/chroot-autobuild")))

    def test_stop(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(SudoUmount(), name="sudo")
        self._make_initial_proc_mounts()
        self.useFixture(FakeTime())
        start_time = time.time()
        Chroot("1", "xenial", "amd64").stop()

        expected_chroot_path = "/expected/home/build-1/chroot-autobuild"
        expected_args = [
            ["sudo", "umount", expected_chroot_path + "/dev/shm"],
            ["sudo", "umount", expected_chroot_path + "/sys"],
            ["sudo", "umount", expected_chroot_path + "/dev/pts"],
            ["sudo", "umount", expected_chroot_path + "/proc"],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])
        self.assertEqual(start_time, time.time())

    def test_stop_retries(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        delays = {"/expected/home/build-1/chroot-autobuild/sys": 1}
        processes_fixture.add(SudoUmount(delays=delays), name="sudo")
        self._make_initial_proc_mounts()
        self.useFixture(FakeTime())
        start_time = time.time()
        Chroot("1", "xenial", "amd64").stop()

        expected_chroot_path = "/expected/home/build-1/chroot-autobuild"
        expected_args = [
            ["sudo", "umount", expected_chroot_path + "/dev/shm"],
            ["sudo", "umount", expected_chroot_path + "/sys"],
            ["sudo", "umount", expected_chroot_path + "/dev/pts"],
            ["sudo", "umount", expected_chroot_path + "/proc"],
            ["sudo", "umount", expected_chroot_path + "/sys"],
            ]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])
        self.assertEqual(start_time + 1, time.time())

    def test_stop_too_many_retries(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        delays = {"/expected/home/build-1/chroot-autobuild/sys": 20}
        processes_fixture.add(SudoUmount(delays=delays), name="sudo")
        processes_fixture.add(lambda _: {}, name="lsof")
        self._make_initial_proc_mounts()
        self.useFixture(FakeTime())
        start_time = time.time()
        self.assertRaises(
            BackendException, Chroot("1", "xenial", "amd64").stop)

        expected_chroot_path = "/expected/home/build-1/chroot-autobuild"
        expected_args = [
            ["sudo", "umount", expected_chroot_path + "/dev/shm"],
            ["sudo", "umount", expected_chroot_path + "/sys"],
            ["sudo", "umount", expected_chroot_path + "/dev/pts"],
            ["sudo", "umount", expected_chroot_path + "/proc"],
            ]
        expected_args.extend(
            [["sudo", "umount", expected_chroot_path + "/sys"]] * 19)
        expected_args.append(["lsof", expected_chroot_path])
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])
        self.assertEqual(start_time + 20, time.time())

    def test_remove(self):
        self.useFixture(EnvironmentVariable("HOME", "/expected/home"))
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(lambda _: {}, name="sudo")
        Chroot("1", "xenial", "amd64").remove()

        expected_args = [["sudo", "rm", "-rf", "/expected/home/build-1"]]
        self.assertEqual(
            expected_args,
            [proc._args["args"] for proc in processes_fixture.procs])

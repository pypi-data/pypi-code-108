# Copyright 2017-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import io
import stat
import subprocess
from textwrap import dedent
import time

from fixtures import FakeLogger
from systemfixtures import FakeTime
from testtools import TestCase
from testtools.matchers import (
    ContainsDict,
    Equals,
    MatchesDict,
    MatchesListwise,
    )

from lpbuildd.target.cli import parse_args
from lpbuildd.tests.fakebuilder import FakeMethod


class MockCopyIn(FakeMethod):

    def __init__(self, *args, **kwargs):
        super(MockCopyIn, self).__init__(*args, **kwargs)
        self.source_bytes = None

    def __call__(self, source_path, *args, **kwargs):
        with open(source_path, "rb") as source:
            self.source_bytes = source.read()
        return super(MockCopyIn, self).__call__(source_path, *args, **kwargs)


class TestOverrideSourcesList(TestCase):

    def test_succeeds(self):
        args = [
            "override-sources-list",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "deb http://archive.ubuntu.com/ubuntu xenial main",
            "deb http://ppa.launchpad.net/launchpad/ppa/ubuntu xenial main",
            ]
        override_sources_list = parse_args(args=args).operation
        self.assertEqual(0, override_sources_list.run())
        self.assertEqual(
            (dedent("""\
                deb http://archive.ubuntu.com/ubuntu xenial main
                deb http://ppa.launchpad.net/launchpad/ppa/ubuntu xenial main
                """).encode("UTF-8"), stat.S_IFREG | 0o644),
            override_sources_list.backend.backend_fs["/etc/apt/sources.list"])
        self.assertEqual(
            (b'Acquire::Retries "3";\n', stat.S_IFREG | 0o644),
            override_sources_list.backend.backend_fs[
                "/etc/apt/apt.conf.d/99retries"])
        self.assertEqual(
            (b'APT::Get::Always-Include-Phased-Updates "true";\n',
             stat.S_IFREG | 0o644),
            override_sources_list.backend.backend_fs[
                "/etc/apt/apt.conf.d/99phasing"])
        self.assertEqual(
            (b"Package: *\nPin: release a=*-proposed\nPin-Priority: 500\n",
             stat.S_IFREG | 0o644),
            override_sources_list.backend.backend_fs[
                "/etc/apt/preferences.d/proposed.pref"])
        self.assertEqual(
            (b"Package: *\nPin: release a=*-backports\nPin-Priority: 500\n",
             stat.S_IFREG | 0o644),
            override_sources_list.backend.backend_fs[
                "/etc/apt/preferences.d/backports.pref"])

    def test_apt_proxy(self):
        args = [
            "override-sources-list",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--apt-proxy-url", "http://apt-proxy.example:3128/",
            "deb http://archive.ubuntu.com/ubuntu xenial main",
            ]
        override_sources_list = parse_args(args=args).operation
        self.assertEqual(0, override_sources_list.run())
        self.assertEqual(
            (dedent("""\
                deb http://archive.ubuntu.com/ubuntu xenial main
                """).encode("UTF-8"), stat.S_IFREG | 0o644),
            override_sources_list.backend.backend_fs["/etc/apt/sources.list"])
        self.assertEqual(
            (b'Acquire::Retries "3";\n', stat.S_IFREG | 0o644),
            override_sources_list.backend.backend_fs[
                "/etc/apt/apt.conf.d/99retries"])
        self.assertEqual(
            (b'APT::Get::Always-Include-Phased-Updates "true";\n',
             stat.S_IFREG | 0o644),
            override_sources_list.backend.backend_fs[
                "/etc/apt/apt.conf.d/99phasing"])
        self.assertEqual(
            (dedent("""\
                Acquire::http::Proxy "http://apt-proxy.example:3128/";
                """).encode("UTF-8"), stat.S_IFREG | 0o644),
            override_sources_list.backend.backend_fs[
                "/etc/apt/apt.conf.d/99proxy"])


class TestAddTrustedKeys(TestCase):

    def test_add_trusted_keys(self):
        args = [
            "add-trusted-keys",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            ]
        input_file = io.BytesIO()
        add_trusted_keys = parse_args(args=args).operation
        add_trusted_keys.input_file = input_file
        self.assertEqual(0, add_trusted_keys.run())
        expected_run = [
            ((["apt-key", "add", "-"],), {"stdin": input_file}),
            ((["apt-key", "list"],), {}),
            ]
        self.assertEqual(expected_run, add_trusted_keys.backend.run.calls)


class RanAptGet(MatchesListwise):

    def __init__(self, args_list):
        super(RanAptGet, self).__init__([
            MatchesListwise([
                Equals((["/usr/bin/apt-get"] + args,)),
                ContainsDict({
                    "env": MatchesDict({
                        "LANG": Equals("C"),
                        "DEBIAN_FRONTEND": Equals("noninteractive"),
                        "TTY": Equals("unknown"),
                        }),
                    }),
                ]) for args in args_list
            ])


class TestUpdate(TestCase):

    def test_succeeds(self):
        self.useFixture(FakeTime())
        start_time = time.time()
        args = [
            "update-debian-chroot",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            ]
        update = parse_args(args=args).operation
        self.assertEqual(0, update.run())

        expected_args = [
            ["-uy", "update"],
            ["-o", "DPkg::Options::=--force-confold", "-uy", "--purge",
             "dist-upgrade"],
            ]
        self.assertThat(update.backend.run.calls, RanAptGet(expected_args))
        self.assertEqual(start_time, time.time())

    def test_first_run_fails(self):
        class FailFirstTime(FakeMethod):
            def __call__(self, run_args, *args, **kwargs):
                super(FailFirstTime, self).__call__(run_args, *args, **kwargs)
                if len(self.calls) == 1:
                    raise subprocess.CalledProcessError(1, run_args)

        logger = self.useFixture(FakeLogger())
        self.useFixture(FakeTime())
        start_time = time.time()
        args = [
            "update-debian-chroot",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            ]
        update = parse_args(args=args).operation
        update.backend.run = FailFirstTime()
        self.assertEqual(0, update.run())

        expected_args = [
            ["-uy", "update"],
            ["-uy", "update"],
            ["-o", "DPkg::Options::=--force-confold", "-uy", "--purge",
             "dist-upgrade"],
            ]
        self.assertThat(update.backend.run.calls, RanAptGet(expected_args))
        self.assertEqual(
            "Updating target for build 1\n"
            "Waiting 15 seconds and trying again ...\n",
            logger.output)
        self.assertEqual(start_time + 15, time.time())

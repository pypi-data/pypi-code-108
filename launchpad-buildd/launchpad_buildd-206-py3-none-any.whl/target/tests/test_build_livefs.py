# Copyright 2017-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import subprocess
from textwrap import dedent

from fixtures import FakeLogger
import responses
from testtools import TestCase
from testtools.matchers import (
    AnyMatch,
    MatchesAll,
    MatchesListwise,
    )

from lpbuildd.target.build_livefs import (
    RETCODE_FAILURE_BUILD,
    RETCODE_FAILURE_INSTALL,
    )
from lpbuildd.target.cli import parse_args
from lpbuildd.target.tests.matchers import (
    RanAptGet,
    RanBuildCommand,
    RanCommand,
    )
from lpbuildd.tests.fakebuilder import FakeMethod


class TestBuildLiveFS(TestCase):

    def test_install(self):
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            ]
        build_livefs = parse_args(args=args).operation
        build_livefs.install()
        self.assertThat(build_livefs.backend.run.calls, MatchesListwise([
            RanAptGet("install", "livecd-rootfs"),
            ]))

    def test_install_locale(self):
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--locale=zh_CN",
            ]
        build_livefs = parse_args(args=args).operation
        build_livefs.install()
        self.assertThat(build_livefs.backend.run.calls, MatchesListwise([
            RanAptGet("install", "livecd-rootfs"),
            RanAptGet(
                "--install-recommends", "install", "ubuntu-defaults-builder"),
            ]))

    @responses.activate
    def test_install_snap_store_proxy(self):
        store_assertion = dedent("""\
            type: store
            store: store-id
            url: http://snap-store-proxy.example

            body
            """)

        def respond(request):
            return 200, {"X-Assertion-Store-Id": "store-id"}, store_assertion

        responses.add_callback(
            "GET", "http://snap-store-proxy.example/v2/auth/store/assertions",
            callback=respond)
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--snap-store-proxy-url", "http://snap-store-proxy.example/",
            ]
        build_livefs = parse_args(args=args).operation
        build_livefs.install()
        self.assertThat(build_livefs.backend.run.calls, MatchesListwise([
            RanAptGet("install", "livecd-rootfs"),
            RanCommand(
                ["snap", "ack", "/dev/stdin"], input_text=store_assertion),
            RanCommand(["snap", "set", "core", "proxy.store=store-id"]),
            ]))

    def test_build(self):
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--project=ubuntu",
            ]
        build_livefs = parse_args(args=args).operation
        build_livefs.build()
        self.assertThat(build_livefs.backend.run.calls, MatchesListwise([
            RanBuildCommand(["rm", "-rf", "auto", "local"]),
            RanBuildCommand(["mkdir", "-p", "auto"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/config", "auto/"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/build", "auto/"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/clean", "auto/"]),
            RanBuildCommand(["lb", "clean", "--purge"]),
            RanBuildCommand(
                ["lb", "config"],
                PROJECT="ubuntu", ARCH="amd64", SUITE="xenial"),
            RanBuildCommand(["lb", "build"], PROJECT="ubuntu", ARCH="amd64"),
            ]))

    def test_build_locale(self):
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--locale=zh_CN",
            ]
        build_livefs = parse_args(args=args).operation
        build_livefs.build()
        self.assertThat(build_livefs.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["ubuntu-defaults-image", "--locale", "zh_CN",
                 "--arch", "amd64", "--release", "xenial"]),
            ]))

    def test_build_extra_ppas_and_snaps(self):
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--project=ubuntu-core",
            "--extra-ppa=owner1/name1", "--extra-ppa=owner2/name2",
            "--extra-snap=snap1", "--extra-snap=snap2",
            ]
        build_livefs = parse_args(args=args).operation
        build_livefs.build()
        self.assertThat(build_livefs.backend.run.calls, MatchesListwise([
            RanBuildCommand(["rm", "-rf", "auto", "local"]),
            RanBuildCommand(["mkdir", "-p", "auto"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/config", "auto/"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/build", "auto/"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/clean", "auto/"]),
            RanBuildCommand(["lb", "clean", "--purge"]),
            RanBuildCommand(
                ["lb", "config"],
                PROJECT="ubuntu-core", ARCH="amd64", SUITE="xenial",
                EXTRA_PPAS="owner1/name1 owner2/name2",
                EXTRA_SNAPS="snap1 snap2"),
            RanBuildCommand(
                ["lb", "build"], PROJECT="ubuntu-core", ARCH="amd64"),
            ]))

    def test_build_debug(self):
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--project=ubuntu", "--debug",
            ]
        build_livefs = parse_args(args=args).operation
        build_livefs.build()
        self.assertThat(build_livefs.backend.run.calls, MatchesListwise([
            RanBuildCommand(["rm", "-rf", "auto", "local"]),
            RanBuildCommand(["mkdir", "-p", "auto"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/config", "auto/"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/build", "auto/"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/clean", "auto/"]),
            RanBuildCommand(["mkdir", "-p", "local/functions"]),
            RanBuildCommand(
                ["sh", "-c", "echo 'set -x' >local/functions/debug.sh"]),
            RanBuildCommand(["lb", "clean", "--purge"]),
            RanBuildCommand(
                ["lb", "config"],
                PROJECT="ubuntu", ARCH="amd64", SUITE="xenial"),
            RanBuildCommand(["lb", "build"], PROJECT="ubuntu", ARCH="amd64"),
            ]))

    def test_build_with_http_proxy(self):
        proxy = "http://example.com:8000"
        expected_env = {
            "PROJECT": "ubuntu-cpc",
            "ARCH": "amd64",
            "http_proxy": proxy,
            "LB_APT_HTTP_PROXY": proxy,
            }
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--project=ubuntu-cpc",
            "--http-proxy={}".format(proxy),
            ]
        build_livefs = parse_args(args=args).operation
        build_livefs.build()
        self.assertThat(build_livefs.backend.run.calls, MatchesListwise([
            RanBuildCommand(["rm", "-rf", "auto", "local"]),
            RanBuildCommand(["mkdir", "-p", "auto"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/config", "auto/"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/build", "auto/"]),
            RanBuildCommand(
                ["ln", "-s",
                 "/usr/share/livecd-rootfs/live-build/auto/clean", "auto/"]),
            RanBuildCommand(["lb", "clean", "--purge"]),
            RanBuildCommand(["lb", "config"], SUITE="xenial", **expected_env),
            RanBuildCommand(["lb", "build"], **expected_env),
            ]))

    def test_run_succeeds(self):
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--project=ubuntu",
            ]
        build_livefs = parse_args(args=args).operation
        self.assertEqual(0, build_livefs.run())
        self.assertThat(build_livefs.backend.run.calls, MatchesAll(
            AnyMatch(RanAptGet("install", "livecd-rootfs")),
            AnyMatch(RanBuildCommand(
                ["lb", "build"], PROJECT="ubuntu", ARCH="amd64"))))

    def test_run_install_fails(self):
        class FailInstall(FakeMethod):
            def __call__(self, run_args, *args, **kwargs):
                super(FailInstall, self).__call__(run_args, *args, **kwargs)
                if run_args[0] == "apt-get":
                    raise subprocess.CalledProcessError(1, run_args)

        self.useFixture(FakeLogger())
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--project=ubuntu",
            ]
        build_livefs = parse_args(args=args).operation
        build_livefs.backend.run = FailInstall()
        self.assertEqual(RETCODE_FAILURE_INSTALL, build_livefs.run())

    def test_run_build_fails(self):
        class FailBuild(FakeMethod):
            def __call__(self, run_args, *args, **kwargs):
                super(FailBuild, self).__call__(run_args, *args, **kwargs)
                if run_args[0] == "rm":
                    raise subprocess.CalledProcessError(1, run_args)

        self.useFixture(FakeLogger())
        args = [
            "buildlivefs",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--project=ubuntu",
            ]
        build_livefs = parse_args(args=args).operation
        build_livefs.backend.run = FailBuild()
        self.assertEqual(RETCODE_FAILURE_BUILD, build_livefs.run())

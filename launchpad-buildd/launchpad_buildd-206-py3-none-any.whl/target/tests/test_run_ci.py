# Copyright 2022 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import json
import os
import stat
import subprocess
from textwrap import dedent

from fixtures import (
    FakeLogger,
    TempDir,
    )
import responses
from systemfixtures import FakeFilesystem
from testtools import TestCase
from testtools.matchers import (
    AnyMatch,
    MatchesAll,
    MatchesListwise,
    )

from lpbuildd.target.cli import parse_args
from lpbuildd.target.run_ci import (
    RETCODE_FAILURE_BUILD,
    RETCODE_FAILURE_INSTALL,
    )
from lpbuildd.target.tests.matchers import (
    RanAptGet,
    RanBuildCommand,
    RanCommand,
    RanSnap,
    )
from lpbuildd.tests.fakebuilder import FakeMethod


class FakeRevisionID(FakeMethod):

    def __init__(self, revision_id):
        super(FakeRevisionID, self).__init__()
        self.revision_id = revision_id

    def __call__(self, run_args, *args, **kwargs):
        super(FakeRevisionID, self).__call__(run_args, *args, **kwargs)
        if run_args[0] == "git" and "rev-parse" in run_args:
            return "%s\n" % self.revision_id


class TestRunCIPrepare(TestCase):

    def test_install_git(self):
        args = [
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.install()
        self.assertThat(run_ci_prepare.backend.run.calls, MatchesListwise([
            RanAptGet("install", "git"),
            RanSnap("install", "lxd"),
            RanSnap("install", "--classic", "lpcraft"),
            RanCommand(["lxd", "init", "--auto"]),
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
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            "--snap-store-proxy-url", "http://snap-store-proxy.example/",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.install()
        self.assertThat(run_ci_prepare.backend.run.calls, MatchesListwise([
            RanAptGet("install", "git"),
            RanSnap("ack", "/dev/stdin", input_text=store_assertion),
            RanSnap("set", "core", "proxy.store=store-id"),
            RanSnap("install", "lxd"),
            RanSnap("install", "--classic", "lpcraft"),
            RanCommand(["lxd", "init", "--auto"]),
            ]))

    def test_install_proxy(self):
        args = [
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            "--proxy-url", "http://proxy.example:3128/",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.bin = "/builderbin"
        self.useFixture(FakeFilesystem()).add("/builderbin")
        os.mkdir("/builderbin")
        with open("/builderbin/lpbuildd-git-proxy", "w") as proxy_script:
            proxy_script.write("proxy script\n")
            os.fchmod(proxy_script.fileno(), 0o755)
        run_ci_prepare.install()
        self.assertThat(run_ci_prepare.backend.run.calls, MatchesListwise([
            RanAptGet("install", "python3", "socat", "git"),
            RanSnap("install", "lxd"),
            RanSnap("install", "--classic", "lpcraft"),
            RanCommand(["lxd", "init", "--auto"]),
            ]))
        self.assertEqual(
            (b"proxy script\n", stat.S_IFREG | 0o755),
            run_ci_prepare.backend.backend_fs[
                "/usr/local/bin/lpbuildd-git-proxy"])

    def test_install_channels(self):
        args = [
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--channel=core=candidate", "--channel=core20=beta",
            "--channel=lxd=beta", "--channel=lpcraft=edge",
            "--git-repository", "lp:foo",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.install()
        self.assertThat(run_ci_prepare.backend.run.calls, MatchesListwise([
            RanAptGet("install", "git"),
            RanSnap("install", "--channel=candidate", "core"),
            RanSnap("install", "--channel=beta", "core20"),
            RanSnap("install", "--channel=beta", "lxd"),
            RanSnap("install", "--classic", "--channel=edge", "lpcraft"),
            RanCommand(["lxd", "init", "--auto"]),
            ]))

    def test_repo_git(self):
        args = [
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.backend.build_path = self.useFixture(TempDir()).path
        run_ci_prepare.backend.run = FakeRevisionID("0" * 40)
        run_ci_prepare.repo()
        self.assertThat(run_ci_prepare.backend.run.calls, MatchesListwise([
            RanBuildCommand(["git", "clone", "lp:foo", "tree"], cwd="/build"),
            RanBuildCommand(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd="/build/tree"),
            RanBuildCommand(
                ["git", "rev-parse", "HEAD^{}"],
                cwd="/build/tree", get_output=True, universal_newlines=True),
            ]))
        status_path = os.path.join(run_ci_prepare.backend.build_path, "status")
        with open(status_path) as status:
            self.assertEqual({"revision_id": "0" * 40}, json.load(status))

    def test_repo_git_with_path(self):
        args = [
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--git-repository", "lp:foo", "--git-path", "next",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.backend.build_path = self.useFixture(TempDir()).path
        run_ci_prepare.backend.run = FakeRevisionID("0" * 40)
        run_ci_prepare.repo()
        self.assertThat(run_ci_prepare.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["git", "clone", "-b", "next", "lp:foo", "tree"],
                cwd="/build"),
            RanBuildCommand(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd="/build/tree"),
            RanBuildCommand(
                ["git", "rev-parse", "next^{}"],
                cwd="/build/tree", get_output=True, universal_newlines=True),
            ]))
        status_path = os.path.join(run_ci_prepare.backend.build_path, "status")
        with open(status_path) as status:
            self.assertEqual({"revision_id": "0" * 40}, json.load(status))

    def test_repo_git_with_tag_path(self):
        args = [
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--git-repository", "lp:foo", "--git-path", "refs/tags/1.0",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.backend.build_path = self.useFixture(TempDir()).path
        run_ci_prepare.backend.run = FakeRevisionID("0" * 40)
        run_ci_prepare.repo()
        self.assertThat(run_ci_prepare.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["git", "clone", "-b", "1.0", "lp:foo", "tree"], cwd="/build"),
            RanBuildCommand(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd="/build/tree"),
            RanBuildCommand(
                ["git", "rev-parse", "refs/tags/1.0^{}"],
                cwd="/build/tree", get_output=True, universal_newlines=True),
            ]))
        status_path = os.path.join(run_ci_prepare.backend.build_path, "status")
        with open(status_path) as status:
            self.assertEqual({"revision_id": "0" * 40}, json.load(status))

    def test_repo_proxy(self):
        args = [
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            "--proxy-url", "http://proxy.example:3128/",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.backend.build_path = self.useFixture(TempDir()).path
        run_ci_prepare.backend.run = FakeRevisionID("0" * 40)
        run_ci_prepare.repo()
        env = {
            "http_proxy": "http://proxy.example:3128/",
            "https_proxy": "http://proxy.example:3128/",
            "GIT_PROXY_COMMAND": "/usr/local/bin/lpbuildd-git-proxy",
            "SNAPPY_STORE_NO_CDN": "1",
            }
        self.assertThat(run_ci_prepare.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["git", "clone", "lp:foo", "tree"], cwd="/build", **env),
            RanBuildCommand(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd="/build/tree", **env),
            RanBuildCommand(
                ["git", "rev-parse", "HEAD^{}"],
                cwd="/build/tree", get_output=True, universal_newlines=True),
            ]))
        status_path = os.path.join(run_ci_prepare.backend.build_path, "status")
        with open(status_path) as status:
            self.assertEqual({"revision_id": "0" * 40}, json.load(status))

    def test_run_succeeds(self):
        args = [
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.backend.build_path = self.useFixture(TempDir()).path
        run_ci_prepare.backend.run = FakeRevisionID("0" * 40)
        self.assertEqual(0, run_ci_prepare.run())
        # Just check that it did something in each step, not every detail.
        self.assertThat(run_ci_prepare.backend.run.calls, MatchesAll(
            AnyMatch(RanSnap("install", "--classic", "lpcraft")),
            AnyMatch(
                RanBuildCommand(
                    ["git", "clone", "lp:foo", "tree"], cwd="/build")),
            ))

    def test_run_install_fails(self):
        class FailInstall(FakeMethod):
            def __call__(self, run_args, *args, **kwargs):
                super(FailInstall, self).__call__(run_args, *args, **kwargs)
                if run_args[0] == "apt-get":
                    raise subprocess.CalledProcessError(1, run_args)

        self.useFixture(FakeLogger())
        args = [
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.backend.run = FailInstall()
        self.assertEqual(RETCODE_FAILURE_INSTALL, run_ci_prepare.run())

    def test_run_repo_fails(self):
        class FailRepo(FakeMethod):
            def __call__(self, run_args, *args, **kwargs):
                super(FailRepo, self).__call__(run_args, *args, **kwargs)
                if run_args[0] == "git":
                    raise subprocess.CalledProcessError(1, run_args)

        self.useFixture(FakeLogger())
        args = [
            "run-ci-prepare",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            ]
        run_ci_prepare = parse_args(args=args).operation
        run_ci_prepare.backend.run = FailRepo()
        self.assertEqual(RETCODE_FAILURE_BUILD, run_ci_prepare.run())


class TestRunCI(TestCase):

    def test_run_job(self):
        args = [
            "run-ci",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "test", "0",
            ]
        run_ci = parse_args(args=args).operation
        run_ci.run_job()
        self.assertThat(run_ci.backend.run.calls, MatchesListwise([
            RanCommand(["mkdir", "-p", "/build/output/test:0"]),
            RanBuildCommand([
                "/bin/bash", "-o", "pipefail", "-c",
                "lpcraft -v run-one --output /build/output/test:0 test 0 2>&1 "
                "| tee /build/output/test:0.log",
                ], cwd="/build/tree"),
            ]))

    def test_run_job_proxy(self):
        args = [
            "run-ci",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "--proxy-url", "http://proxy.example:3128/",
            "test", "0",
            ]
        run_ci = parse_args(args=args).operation
        run_ci.run_job()
        env = {
            "http_proxy": "http://proxy.example:3128/",
            "https_proxy": "http://proxy.example:3128/",
            "GIT_PROXY_COMMAND": "/usr/local/bin/lpbuildd-git-proxy",
            "SNAPPY_STORE_NO_CDN": "1",
            }
        self.assertThat(run_ci.backend.run.calls, MatchesListwise([
            RanCommand(["mkdir", "-p", "/build/output/test:0"]),
            RanBuildCommand([
                "/bin/bash", "-o", "pipefail", "-c",
                "lpcraft -v run-one --output /build/output/test:0 test 0 2>&1 "
                "| tee /build/output/test:0.log",
                ], cwd="/build/tree", **env),
            ]))

    def test_run_succeeds(self):
        args = [
            "run-ci",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "test", "0",
            ]
        run_ci = parse_args(args=args).operation
        self.assertEqual(0, run_ci.run())
        # Just check that it did something in each step, not every detail.
        self.assertThat(
            run_ci.backend.run.calls,
            AnyMatch(RanCommand(["mkdir", "-p", "/build/output/test:0"])))

    def test_run_install_fails(self):
        class FailInstall(FakeMethod):
            def __call__(self, run_args, *args, **kwargs):
                super(FailInstall, self).__call__(run_args, *args, **kwargs)
                if run_args[0] == "/bin/bash":
                    raise subprocess.CalledProcessError(1, run_args)

        self.useFixture(FakeLogger())
        args = [
            "run-ci",
            "--backend=fake", "--series=focal", "--arch=amd64", "1",
            "test", "0",
            ]
        run_ci = parse_args(args=args).operation
        run_ci.backend.run = FailInstall()
        self.assertEqual(RETCODE_FAILURE_BUILD, run_ci.run())

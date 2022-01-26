# Copyright 2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import os.path
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

from lpbuildd.target.backend import InvalidBuildFilePath
from lpbuildd.target.build_oci import (
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


class TestBuildOCI(TestCase):

    def test_run_build_command_no_env(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.run_build_command(["echo", "hello world"])
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["echo", "hello world"],
                cwd="/home/buildd/test-image"),
            ]))

    def test_run_build_command_env(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.run_build_command(
            ["echo", "hello world"], env={"FOO": "bar baz"})
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["echo", "hello world"],
                FOO="bar baz",
                cwd="/home/buildd/test-image")
            ]))

    def test_install_bzr(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "test-image"
            ]
        build_oci = parse_args(args=args).operation
        build_oci.install()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanAptGet("install", "bzr", "docker.io"),
            RanCommand(["systemctl", "restart", "docker"]),
            RanCommand(["mkdir", "-p", "/home/buildd"]),
            ]))

    def test_install_git(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", "lp:foo", "test-image"
            ]
        build_oci = parse_args(args=args).operation
        build_oci.install()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanAptGet("install", "git", "docker.io"),
            RanCommand(["systemctl", "restart", "docker"]),
            RanCommand(["mkdir", "-p", "/home/buildd"]),
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
            "buildsnap",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            "--snap-store-proxy-url", "http://snap-store-proxy.example/",
            "test-snap",
            ]
        build_snap = parse_args(args=args).operation
        build_snap.install()
        self.assertThat(build_snap.backend.run.calls, MatchesListwise([
            RanAptGet("install", "git", "snapcraft"),
            RanCommand(
                ["snap", "ack", "/dev/stdin"], input_text=store_assertion),
            RanCommand(["snap", "set", "core", "proxy.store=store-id"]),
            ]))

    def test_install_proxy(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            "--proxy-url", "http://proxy.example:3128/",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.bin = "/builderbin"
        self.useFixture(FakeFilesystem()).add("/builderbin")
        os.mkdir("/builderbin")
        with open("/builderbin/lpbuildd-git-proxy", "w") as proxy_script:
            proxy_script.write("proxy script\n")
            os.fchmod(proxy_script.fileno(), 0o755)
        build_oci.install()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanCommand(
                ["mkdir", "-p", "/etc/systemd/system/docker.service.d"]),
            RanAptGet("install", "python3", "socat", "git", "docker.io"),
            RanCommand(["systemctl", "restart", "docker"]),
            RanCommand(["mkdir", "-p", "/home/buildd"]),
            ]))
        self.assertEqual(
            (b"proxy script\n", stat.S_IFREG | 0o755),
            build_oci.backend.backend_fs["/usr/local/bin/lpbuildd-git-proxy"])

    def test_repo_bzr(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.build_path = self.useFixture(TempDir()).path
        build_oci.backend.run = FakeMethod()
        build_oci.repo()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["bzr", "branch", "lp:foo", "test-image"], cwd="/home/buildd"),
            ]))

    def test_repo_git(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", "lp:foo", "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.build_path = self.useFixture(TempDir()).path
        build_oci.backend.run = FakeMethod()
        build_oci.repo()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["git", "clone", "--depth", "1", "lp:foo", "test-image"],
                cwd="/home/buildd"),
            RanBuildCommand(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd="/home/buildd/test-image"),
            ]))

    def test_repo_git_with_path(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", "lp:foo", "--git-path", "next", "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.build_path = self.useFixture(TempDir()).path
        build_oci.backend.run = FakeMethod()
        build_oci.repo()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["git", "clone", "--depth", "1", "-b", "next",
                 "lp:foo", "test-image"], cwd="/home/buildd"),
            RanBuildCommand(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd="/home/buildd/test-image"),
            ]))

    def test_repo_git_with_tag_path(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", "lp:foo", "--git-path", "refs/tags/1.0",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.build_path = self.useFixture(TempDir()).path
        build_oci.backend.run = FakeMethod()
        build_oci.repo()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["git", "clone", "--depth", "1", "-b", "1.0", "lp:foo",
                 "test-image"], cwd="/home/buildd"),
            RanBuildCommand(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd="/home/buildd/test-image"),
            ]))

    def test_repo_proxy(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", "lp:foo",
            "--proxy-url", "http://proxy.example:3128/",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.build_path = self.useFixture(TempDir()).path
        build_oci.backend.run = FakeMethod()
        build_oci.repo()
        env = {
            "http_proxy": "http://proxy.example:3128/",
            "https_proxy": "http://proxy.example:3128/",
            "GIT_PROXY_COMMAND": "/usr/local/bin/lpbuildd-git-proxy",
            "SNAPPY_STORE_NO_CDN": "1",
            }
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["git", "clone", "--depth", "1", "lp:foo", "test-image"],
                cwd="/home/buildd", **env),
            RanBuildCommand(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd="/home/buildd/test-image", **env),
            ]))

    def test_build(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.add_dir('/build/test-directory')
        build_oci.build()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["docker", "build", "--no-cache", "--tag", "test-image",
                 "/home/buildd/test-image/."],
                cwd="/home/buildd/test-image"),
            ]))

    def test_build_with_file(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--build-file", "build-aux/Dockerfile",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.add_dir('/build/test-directory')
        build_oci.build()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["docker", "build", "--no-cache", "--tag", "test-image",
                 "--file", "./build-aux/Dockerfile",
                 "/home/buildd/test-image/."],
                cwd="/home/buildd/test-image"),
            ]))

    def test_build_with_path(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--build-path", "a-sub-directory/",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.add_dir('/build/test-directory')
        build_oci.build()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["docker", "build", "--no-cache", "--tag", "test-image",
                 "/home/buildd/test-image/a-sub-directory/"],
                cwd="/home/buildd/test-image"),
            ]))

    def test_build_with_file_and_path(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--build-file", "build-aux/Dockerfile",
            "--build-path", "test-build-path",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.add_dir('/build/test-directory')
        build_oci.build()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["docker", "build", "--no-cache", "--tag", "test-image",
                 "--file", "test-build-path/build-aux/Dockerfile",
                 "/home/buildd/test-image/test-build-path"],
                cwd="/home/buildd/test-image"),
            ]))

    def test_build_with_args(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--build-file", "build-aux/Dockerfile",
            "--build-path", "test-build-path",
            "--build-arg=VAR1=xxx", "--build-arg=VAR2=yyy",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.add_dir('/build/test-directory')
        build_oci.build()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["docker", "build", "--no-cache", "--tag", "test-image",
                 "--file", "test-build-path/build-aux/Dockerfile",
                 "--build-arg=VAR1=xxx", "--build-arg=VAR2=yyy",
                 "/home/buildd/test-image/test-build-path"],
                cwd="/home/buildd/test-image"),
            ]))

    def test_build_proxy(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--proxy-url", "http://proxy.example:3128/",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.add_dir('/build/test-directory')
        build_oci.build()
        self.assertThat(build_oci.backend.run.calls, MatchesListwise([
            RanBuildCommand(
                ["docker", "build", "--no-cache",
                 "--build-arg", "http_proxy=http://proxy.example:3128/",
                 "--build-arg", "https_proxy=http://proxy.example:3128/",
                 "--tag", "test-image", "/home/buildd/test-image/."],
                cwd="/home/buildd/test-image"),
            ]))

    def test_run_succeeds(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.build_path = self.useFixture(TempDir()).path
        build_oci.backend.run = FakeMethod()
        self.assertEqual(0, build_oci.run())
        self.assertThat(build_oci.backend.run.calls, MatchesAll(
            AnyMatch(RanAptGet("install", "bzr", "docker.io")),
            AnyMatch(RanBuildCommand(
                ["bzr", "branch", "lp:foo", "test-image"],
                cwd="/home/buildd")),
            AnyMatch(RanBuildCommand(
                ["docker", "build", "--no-cache", "--tag", "test-image",
                 "/home/buildd/test-image/."],
                cwd="/home/buildd/test-image")),
            ))

    def test_run_install_fails(self):
        class FailInstall(FakeMethod):
            def __call__(self, run_args, *args, **kwargs):
                super(FailInstall, self).__call__(run_args, *args, **kwargs)
                if run_args[0] == "apt-get":
                    raise subprocess.CalledProcessError(1, run_args)

        self.useFixture(FakeLogger())
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.run = FailInstall()
        self.assertEqual(RETCODE_FAILURE_INSTALL, build_oci.run())

    def test_run_repo_fails(self):
        class FailRepo(FakeMethod):
            def __call__(self, run_args, *args, **kwargs):
                super(FailRepo, self).__call__(run_args, *args, **kwargs)
                if run_args[:2] == ["bzr", "branch"]:
                    raise subprocess.CalledProcessError(1, run_args)

        self.useFixture(FakeLogger())
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.run = FailRepo()
        self.assertEqual(RETCODE_FAILURE_BUILD, build_oci.run())

    def test_run_build_fails(self):
        class FailBuild(FakeMethod):
            def __call__(self, run_args, *args, **kwargs):
                super(FailBuild, self).__call__(run_args, *args, **kwargs)
                if run_args[0] == "docker":
                    raise subprocess.CalledProcessError(1, run_args)

        self.useFixture(FakeLogger())
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.build_path = self.useFixture(TempDir()).path
        build_oci.backend.run = FailBuild()
        self.assertEqual(RETCODE_FAILURE_BUILD, build_oci.run())

    def test_build_with_invalid_file_path_parent(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--build-file", "../build-aux/Dockerfile",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.add_dir('/build/test-directory')
        self.assertRaises(InvalidBuildFilePath, build_oci.build)

    def test_build_with_invalid_file_path_absolute(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--build-file", "/etc/Dockerfile",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.add_dir('/build/test-directory')
        self.assertRaises(InvalidBuildFilePath, build_oci.build)

    def test_build_with_invalid_file_path_symlink(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--build-file", "Dockerfile",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.buildd_path = self.useFixture(TempDir()).path
        os.symlink(
            '/etc/hosts',
            os.path.join(build_oci.buildd_path, 'Dockerfile'))
        self.assertRaises(InvalidBuildFilePath, build_oci.build)

    def test_build_with_invalid_build_path_parent(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--build-path", "../",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.add_dir('/build/test-directory')
        self.assertRaises(InvalidBuildFilePath, build_oci.build)

    def test_build_with_invalid_build_path_absolute(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--build-path", "/etc",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.backend.add_dir('/build/test-directory')
        self.assertRaises(InvalidBuildFilePath, build_oci.build)

    def test_build_with_invalid_build_path_symlink(self):
        args = [
            "build-oci",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", "--build-path", "build/",
            "test-image",
            ]
        build_oci = parse_args(args=args).operation
        build_oci.buildd_path = self.useFixture(TempDir()).path
        os.symlink(
            '/etc/hosts',
            os.path.join(build_oci.buildd_path, 'build'))
        self.assertRaises(InvalidBuildFilePath, build_oci.build)

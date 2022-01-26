# Copyright 2010-2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import os
import subprocess
import tarfile
try:
    from unittest import mock
except ImportError:
    import mock

from fixtures import (
    EnvironmentVariable,
    FakeLogger,
    TempDir,
    )
from testtools import TestCase
from testtools.matchers import (
    Equals,
    MatchesListwise,
    MatchesSetwise,
    )

from lpbuildd.target.cli import parse_args
from lpbuildd.target.tests.matchers import (
    RanAptGet,
    RanCommand,
    )


class TestGenerateTranslationTemplates(TestCase):
    """Test generate-translation-templates script."""

    result_name = "translation-templates.tar.gz"

    def setUp(self):
        super(TestGenerateTranslationTemplates, self).setUp()
        self.home_dir = self.useFixture(TempDir()).path
        self.useFixture(EnvironmentVariable("HOME", self.home_dir))
        self.logger = self.useFixture(FakeLogger())

    def make_branch_contents(self, content_map):
        """Create a directory with the contents of a working branch.

        :param content_map: A dict mapping file names to file contents.
            Each of these files with their contents will be written to the
            branch.  Currently only supports writing files at the root
            directory of the branch.
        """
        branch_path = self.useFixture(TempDir()).path
        for name, contents in content_map.items():
            with open(os.path.join(branch_path, name), 'wb') as f:
                f.write(contents)
        return branch_path

    def make_bzr_branch(self, branch_path):
        """Make a bzr branch from an existing directory."""
        bzr_home = self.useFixture(TempDir()).path
        self.useFixture(EnvironmentVariable("BZR_HOME", bzr_home))
        self.useFixture(EnvironmentVariable("BZR_EMAIL"))
        self.useFixture(EnvironmentVariable("EMAIL"))

        subprocess.check_call(["bzr", "init", "-q"], cwd=branch_path)
        subprocess.check_call(["bzr", "add", "-q"], cwd=branch_path)
        committer_id = "Committer <committer@example.com>"
        with EnvironmentVariable("BZR_EMAIL", committer_id):
            subprocess.check_call(
                ["bzr", "commit", "-q", "-m", "Populating branch."],
                cwd=branch_path)

    def make_git_branch(self, branch_path):
        subprocess.check_call(["git", "init", "-q"], cwd=branch_path)
        subprocess.check_call(
            ["git", "config", "user.name", "Committer"], cwd=branch_path)
        subprocess.check_call(
            ["git", "config", "user.email", "committer@example.com"],
            cwd=branch_path)
        subprocess.check_call(["git", "add", "."], cwd=branch_path)
        subprocess.check_call(
            ["git", "commit", "-q", "--allow-empty",
             "-m", "Populating branch"],
            cwd=branch_path)

    def test_install_bzr(self):
        args = [
            "generate-translation-templates",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", "lp:foo", self.result_name,
            ]
        generator = parse_args(args=args).operation
        generator.install()
        self.assertThat(generator.backend.run.calls, MatchesListwise([
            RanAptGet("install", "intltool", "bzr"),
            ]))

    def test_install_git(self):
        args = [
            "generate-translation-templates",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", "lp:foo", self.result_name,
            ]
        generator = parse_args(args=args).operation
        generator.install()
        self.assertThat(generator.backend.run.calls, MatchesListwise([
            RanAptGet("install", "intltool", "git"),
            ]))

    def test_fetch_bzr(self):
        # fetch can retrieve branch contents from a Bazaar branch.
        marker_text = b"Ceci n'est pas cet branch."
        branch_path = self.make_branch_contents({'marker.txt': marker_text})
        self.make_bzr_branch(branch_path)

        args = [
            "generate-translation-templates",
            "--backend=uncontained", "--series=xenial", "--arch=amd64", "1",
            "--branch", branch_path, self.result_name,
            ]
        generator = parse_args(args=args).operation
        generator.fetch(quiet=True)

        marker_path = os.path.join(generator.branch_dir, 'marker.txt')
        with open(marker_path, "rb") as marker_file:
            self.assertEqual(marker_text, marker_file.read())

    def test_fetch_git(self):
        # fetch can retrieve branch contents from a Git repository.
        marker_text = b"Ceci n'est pas cet branch."
        branch_path = self.make_branch_contents({'marker.txt': marker_text})
        self.make_git_branch(branch_path)

        args = [
            "generate-translation-templates",
            "--backend=uncontained", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", branch_path, self.result_name,
            ]
        generator = parse_args(args=args).operation
        generator.fetch(quiet=True)

        marker_path = os.path.join(generator.branch_dir, 'marker.txt')
        with open(marker_path, "rb") as marker_file:
            self.assertEqual(marker_text, marker_file.read())

    def test_fetch_git_with_path(self):
        # fetch can retrieve branch contents from a Git repository and
        # branch name.
        marker_text = b"Ceci n'est pas cet branch."
        branch_path = self.make_branch_contents({'marker.txt': marker_text})
        self.make_git_branch(branch_path)
        subprocess.call(
            ["git", "branch", "-m", "master", "next"], cwd=branch_path)

        args = [
            "generate-translation-templates",
            "--backend=uncontained", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", branch_path, "--git-path", "next",
            self.result_name,
            ]
        generator = parse_args(args=args).operation
        generator.fetch(quiet=True)

        marker_path = os.path.join(generator.branch_dir, 'marker.txt')
        with open(marker_path, "rb") as marker_file:
            self.assertEqual(marker_text, marker_file.read())

    def test_templates_tarball(self):
        # Create a tarball from pot files.
        branchdir = os.path.join(self.home_dir, 'branchdir')
        dummy_tar = os.path.join(
            os.path.dirname(__file__), 'dummy_templates.tar.gz')
        with tarfile.open(dummy_tar, 'r|*') as tar:
            tar.extractall(branchdir)
            potnames = [
                member.name
                for member in tar.getmembers() if not member.isdir()]
        self.make_bzr_branch(branchdir)

        args = [
            "generate-translation-templates",
            "--backend=uncontained", "--series=xenial", "--arch=amd64", "1",
            "--branch", branchdir, self.result_name,
            ]
        generator = parse_args(args=args).operation
        generator.fetch(quiet=True)
        generator._makeTarball(potnames)
        result_path = os.path.join(self.home_dir, self.result_name)
        with tarfile.open(result_path, 'r|*') as tar:
            tarnames = tar.getnames()
        self.assertThat(tarnames, MatchesSetwise(*(map(Equals, potnames))))

    def test_run_bzr(self):
        # Install dependencies and generate a templates tarball from Bazaar.
        branch_url = "lp:~my/branch"
        branch_dir = os.path.join(self.home_dir, "source-tree")
        po_dir = os.path.join(branch_dir, "po")
        result_path = os.path.join(self.home_dir, self.result_name)

        args = [
            "generate-translation-templates",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--branch", branch_url, self.result_name,
            ]
        generator = parse_args(args=args).operation
        generator.backend.add_file(os.path.join(po_dir, "POTFILES.in"), b"")
        generator.backend.add_file(
            os.path.join(po_dir, "Makevars"), b"DOMAIN = test\n")
        generator.run()
        self.assertThat(generator.backend.run.calls, MatchesListwise([
            RanAptGet("install", "intltool", "bzr"),
            RanCommand(
                ["bzr", "branch", "lp:~my/branch", "source-tree"],
                cwd=self.home_dir, LANG="C.UTF-8", SHELL="/bin/sh"),
            RanCommand(
                ["rm", "-f",
                 os.path.join(po_dir, "missing"),
                 os.path.join(po_dir, "notexist")]),
            RanCommand(
                ["/usr/bin/intltool-update", "-m"],
                stdout=mock.ANY, stderr=mock.ANY, cwd=po_dir),
            RanCommand(
                ["/usr/bin/intltool-update", "-p", "-g", "test"],
                stdout=mock.ANY, stderr=mock.ANY, cwd=po_dir),
            RanCommand(
                ["tar", "-C", branch_dir, "-czf", result_path, "po/test.pot"]),
            ]))

    def test_run_git(self):
        # Install dependencies and generate a templates tarball from Git.
        repository_url = "lp:~my/repository"
        branch_dir = os.path.join(self.home_dir, "source-tree")
        po_dir = os.path.join(branch_dir, "po")
        result_path = os.path.join(self.home_dir, self.result_name)

        args = [
            "generate-translation-templates",
            "--backend=fake", "--series=xenial", "--arch=amd64", "1",
            "--git-repository", repository_url, self.result_name,
            ]
        generator = parse_args(args=args).operation
        generator.backend.add_file(os.path.join(po_dir, "POTFILES.in"), b"")
        generator.backend.add_file(
            os.path.join(po_dir, "Makevars"), b"DOMAIN = test\n")
        generator.run()
        self.assertThat(generator.backend.run.calls, MatchesListwise([
            RanAptGet("install", "intltool", "git"),
            RanCommand(
                ["git", "clone", "lp:~my/repository", "source-tree"],
                cwd=self.home_dir, LANG="C.UTF-8", SHELL="/bin/sh"),
            RanCommand(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd=branch_dir, LANG="C.UTF-8", SHELL="/bin/sh"),
            RanCommand(
                ["rm", "-f",
                 os.path.join(po_dir, "missing"),
                 os.path.join(po_dir, "notexist")]),
            RanCommand(
                ["/usr/bin/intltool-update", "-m"],
                stdout=mock.ANY, stderr=mock.ANY, cwd=po_dir),
            RanCommand(
                ["/usr/bin/intltool-update", "-p", "-g", "test"],
                stdout=mock.ANY, stderr=mock.ANY, cwd=po_dir),
            RanCommand(
                ["tar", "-C", branch_dir, "-czf", result_path, "po/test.pot"]),
            ]))

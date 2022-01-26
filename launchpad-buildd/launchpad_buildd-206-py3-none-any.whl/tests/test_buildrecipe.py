# Copyright 2014-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

from contextlib import contextmanager
import imp
import io
import os
import shutil
import stat
import sys
import tempfile
from textwrap import dedent

from fixtures import (
    EnvironmentVariable,
    MockPatch,
    MockPatchObject,
    TempDir,
    )
import six
from systemfixtures import FakeProcesses
from testtools import TestCase
from testtools.matchers import (
    Equals,
    MatchesListwise,
    StartsWith,
    )


@contextmanager
def disable_bytecode():
    original = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    yield
    sys.dont_write_bytecode = original


# By-hand import to avoid having to put .py suffixes on builder binaries.
with disable_bytecode():
    RecipeBuilder = imp.load_source(
        "buildrecipe", "bin/buildrecipe").RecipeBuilder


class RanCommand(MatchesListwise):

    def __init__(self, *args):
        args_matchers = [
            Equals(arg) if isinstance(arg, six.string_types) else arg
            for arg in args]
        super(RanCommand, self).__init__(args_matchers)


class RanInChroot(RanCommand):

    def __init__(self, home_dir, *args):
        super(RanInChroot, self).__init__(
            "sudo", "/usr/sbin/chroot",
            os.path.join(home_dir, "build-1", "chroot-autobuild"), *args)


class TestRecipeBuilder(TestCase):
    def setUp(self):
        super(TestRecipeBuilder, self).setUp()
        self.save_env = dict(os.environ)
        self.home_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.home_dir))
        os.environ["HOME"] = self.home_dir
        self.build_id = "1"
        self.builder = RecipeBuilder(
            self.build_id, "Recipe Builder", "builder@example.org>", "grumpy",
            "grumpy", "main", "PPA")
        os.makedirs(self.builder.work_dir)

    def resetEnvironment(self):
        for key in set(os.environ.keys()) - set(self.save_env.keys()):
            del os.environ[key]
        for key, value in os.environ.items():
            if value != self.save_env[key]:
                os.environ[key] = self.save_env[key]
        for key in set(self.save_env.keys()) - set(os.environ.keys()):
            os.environ[key] = self.save_env[key]

    def tearDown(self):
        self.resetEnvironment()
        super(TestRecipeBuilder, self).tearDown()

    def test_is_command_on_path_missing_environment(self):
        self.useFixture(EnvironmentVariable("PATH"))
        self.assertFalse(self.builder._is_command_on_path("ls"))

    def test_is_command_on_path_present_executable(self):
        temp_dir = self.useFixture(TempDir()).path
        bin_dir = os.path.join(temp_dir, "bin")
        os.mkdir(bin_dir)
        program = os.path.join(bin_dir, "program")
        with open(program, "w"):
            pass
        os.chmod(program, 0o755)
        self.useFixture(EnvironmentVariable("PATH", bin_dir))
        self.assertTrue(self.builder._is_command_on_path("program"))

    def test_is_command_on_path_present_not_executable(self):
        temp_dir = self.useFixture(TempDir()).path
        bin_dir = os.path.join(temp_dir, "bin")
        os.mkdir(bin_dir)
        with open(os.path.join(bin_dir, "program"), "w"):
            pass
        self.useFixture(EnvironmentVariable("PATH", bin_dir))
        self.assertFalse(self.builder._is_command_on_path("program"))

    def test_buildTree_git(self):
        def fake_git(args):
            if args["args"][1] == "--version":
                print("git version x.y.z")
                return {}
            else:
                return {"returncode": 1}

        def fake_git_build_recipe(args):
            print("dummy recipe build")
            os.makedirs(os.path.join(self.builder.tree_path, "foo"))
            return {}

        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(
            lambda _: {"stdout": io.StringIO(u"5.10\n")}, name="sudo")
        processes_fixture.add(fake_git, name="git")
        processes_fixture.add(
            lambda _: {"stdout": io.StringIO(u"git-build-recipe\tx.y.z\n")},
            name="dpkg-query")
        processes_fixture.add(fake_git_build_recipe, name="git-build-recipe")
        self.builder = RecipeBuilder(
            self.build_id, "Recipe Builder", "builder@example.org>", "grumpy",
            "grumpy", "main", "PPA", git=True)
        with open(os.path.join(self.builder.work_dir, "recipe"), "w") as f:
            f.write("dummy recipe contents\n")
        mock_stdout = six.StringIO()
        self.useFixture(MockPatch("sys.stdout", mock_stdout))
        self.assertEqual(0, self.builder.buildTree())
        self.assertEqual(
            os.path.join(self.builder.work_dir_relative, "tree", "foo"),
            self.builder.source_dir_relative)
        expected_recipe_command = [
            "git-build-recipe", "--safe", "--no-build",
            "--manifest", os.path.join(self.builder.tree_path, "manifest"),
            "--distribution", "grumpy", "--allow-fallback-to-native",
            "--append-version", u"~ubuntu5.10.1",
            os.path.join(self.builder.work_dir, "recipe"),
            self.builder.tree_path,
            ]
        self.assertEqual(
            dedent("""\
                Git version:
                git version x.y.z
                git-build-recipe x.y.z
                Building recipe:
                dummy recipe contents

                RUN %s
                dummy recipe build
                """) % repr(expected_recipe_command),
            mock_stdout.getvalue())

    def test_buildTree_brz(self):
        def fake_bzr(args):
            if args["args"][1] == "version":
                print("brz version x.y.z")
                return {}
            elif args["args"][1] == "plugins":
                print("brz-plugin x.y.z")
                return {}
            else:
                return {"returncode": 1}

        def fake_brz_build_daily_recipe(args):
            print("dummy recipe build")
            os.makedirs(os.path.join(self.builder.tree_path, "foo"))
            return {}

        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(
            lambda _: {"stdout": io.StringIO(u"5.10\n")}, name="sudo")
        processes_fixture.add(fake_bzr, name="bzr")
        processes_fixture.add(
            fake_brz_build_daily_recipe, name="brz-build-daily-recipe")
        with open(os.path.join(self.builder.work_dir, "recipe"), "w") as f:
            f.write("dummy recipe contents\n")
        mock_stdout = six.StringIO()
        self.useFixture(MockPatch("sys.stdout", mock_stdout))
        self.useFixture(MockPatchObject(
            self.builder, "_is_command_on_path",
            side_effect=lambda command: command == "brz-build-daily-recipe"))
        self.assertEqual(0, self.builder.buildTree())
        self.assertEqual(
            os.path.join(self.builder.work_dir_relative, "tree", "foo"),
            self.builder.source_dir_relative)
        expected_recipe_command = [
            "brz-build-daily-recipe", "--safe", "--no-build",
            "--manifest", os.path.join(self.builder.tree_path, "manifest"),
            "--distribution", "grumpy", "--allow-fallback-to-native",
            "--append-version", u"~ubuntu5.10.1",
            os.path.join(self.builder.work_dir, "recipe"),
            self.builder.tree_path,
            ]
        self.assertEqual(
            dedent("""\
                Bazaar versions:
                brz version x.y.z
                brz-plugin x.y.z
                Building recipe:
                dummy recipe contents

                RUN %s
                dummy recipe build
                """) % repr(expected_recipe_command),
            mock_stdout.getvalue())

    def test_buildTree_bzr(self):
        def fake_bzr(args):
            if args["args"][1] == "version":
                print("bzr version x.y.z")
                return {}
            elif args["args"][1] == "plugins":
                print("bzr-plugin x.y.z")
                return {}
            elif "dailydeb" in args["args"][1:]:
                print("dummy recipe build")
                os.makedirs(os.path.join(self.builder.tree_path, "foo"))
                return {}
            else:
                return {"returncode": 1}

        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(
            lambda _: {"stdout": io.StringIO(u"5.10\n")}, name="sudo")
        processes_fixture.add(fake_bzr, name="bzr")
        with open(os.path.join(self.builder.work_dir, "recipe"), "w") as f:
            f.write("dummy recipe contents\n")
        mock_stdout = six.StringIO()
        self.useFixture(MockPatch("sys.stdout", mock_stdout))
        self.useFixture(MockPatchObject(
            self.builder, "_is_command_on_path", return_value=False))
        self.assertEqual(0, self.builder.buildTree())
        self.assertEqual(
            os.path.join(self.builder.work_dir_relative, "tree", "foo"),
            self.builder.source_dir_relative)
        expected_recipe_command = [
            "bzr", "-Derror", "dailydeb", "--safe", "--no-build",
            "--manifest", os.path.join(self.builder.tree_path, "manifest"),
            "--distribution", "grumpy", "--allow-fallback-to-native",
            "--append-version", u"~ubuntu5.10.1",
            os.path.join(self.builder.work_dir, "recipe"),
            self.builder.tree_path,
            ]
        self.assertEqual(
            dedent("""\
                Bazaar versions:
                bzr version x.y.z
                bzr-plugin x.y.z
                Building recipe:
                dummy recipe contents

                RUN %s
                dummy recipe build
                """) % repr(expected_recipe_command),
            mock_stdout.getvalue())

    def test_makeDummyDsc(self):
        self.builder.source_dir_relative = os.path.join(
            self.builder.work_dir_relative, "tree", "foo")
        control_path = os.path.join(
            self.builder.work_dir, "tree", "foo", "debian", "control")
        os.makedirs(os.path.dirname(control_path))
        os.makedirs(self.builder.apt_dir)
        with open(control_path, "w") as control:
            print(
                dedent("""\
                    Source: foo
                    Build-Depends: debhelper (>= 9~), libfoo-dev

                    Package: foo
                    Depends: ${shlibs:Depends}"""),
                file=control)
        self.builder.makeDummyDsc("foo")
        with open(os.path.join(self.builder.apt_dir, "foo.dsc")) as dsc:
            self.assertEqual(
                dedent("""\
                    Format: 1.0
                    Source: foo
                    Architecture: any
                    Version: 99:0
                    Maintainer: invalid@example.org
                    Build-Depends: debhelper (>= 9~), libfoo-dev

                    """),
                dsc.read())

    def test_makeDummyDsc_comments(self):
        # apt_pkg.TagFile doesn't support comments, but python-debian's own
        # parser does.  Make sure we're using the right one.
        self.builder.source_dir_relative = os.path.join(
            self.builder.work_dir_relative, "tree", "foo")
        control_path = os.path.join(
            self.builder.work_dir, "tree", "foo", "debian", "control")
        os.makedirs(os.path.dirname(control_path))
        os.makedirs(self.builder.apt_dir)
        with open(control_path, "w") as control:
            print(
                dedent("""\
                    Source: foo
                    Build-Depends: debhelper (>= 9~),
                                   libfoo-dev,
                    # comment line
                                   pkg-config

                    Package: foo
                    Depends: ${shlibs:Depends}"""),
                file=control)
        self.builder.makeDummyDsc("foo")
        with open(os.path.join(self.builder.apt_dir, "foo.dsc")) as dsc:
            self.assertEqual(
                dedent("""\
                    Format: 1.0
                    Source: foo
                    Architecture: any
                    Version: 99:0
                    Maintainer: invalid@example.org
                    Build-Depends: debhelper (>= 9~),
                                   libfoo-dev,
                                   pkg-config

                    """),
                dsc.read())

    def test_runAptFtparchive(self):
        os.makedirs(self.builder.apt_dir)
        with open(os.path.join(self.builder.apt_dir, "foo.dsc"), "w") as dsc:
            print(
                dedent("""\
                    Format: 1.0
                    Source: foo
                    Architecture: any
                    Version: 99:0
                    Maintainer: invalid@example.org
                    Build-Depends: debhelper (>= 9~), libfoo-dev"""),
                file=dsc)
        self.assertEqual(0, self.builder.runAptFtparchive())
        self.assertEqual(
            ["Release", "Sources", "Sources.bz2", "foo.dsc",
             "ftparchive.conf"],
            sorted(os.listdir(self.builder.apt_dir)))
        with open(os.path.join(self.builder.apt_dir, "Sources")) as sources:
            sources_text = sources.read()
            self.assertIn("Package: foo\n", sources_text)
            self.assertIn(
                "Build-Depends: debhelper (>= 9~), libfoo-dev\n", sources_text)

    def test_installBuildDeps(self):
        processes_fixture = self.useFixture(FakeProcesses())
        processes_fixture.add(lambda _: {}, name="sudo")
        copies = {}

        def mock_copy_in(source_path, target_path):
            with open(source_path, "rb") as source:
                copies[target_path] = (
                    source.read(), os.fstat(source.fileno()).st_mode)

        self.useFixture(
            MockPatchObject(self.builder, "copy_in", mock_copy_in))
        self.builder.source_dir_relative = os.path.join(
            self.builder.work_dir_relative, "tree", "foo")
        changelog_path = os.path.join(
            self.builder.work_dir, "tree", "foo", "debian", "changelog")
        control_path = os.path.join(
            self.builder.work_dir, "tree", "foo", "debian", "control")
        os.makedirs(os.path.dirname(changelog_path))
        with open(changelog_path, "w") as changelog:
            # Not a valid changelog, but only the first line matters here.
            print("foo (1.0-1) bionic; urgency=medium", file=changelog)
        with open(control_path, "w") as control:
            print(
                dedent("""\
                    Source: foo
                    Build-Depends: debhelper (>= 9~), libfoo-dev

                    Package: foo
                    Depends: ${shlibs:Depends}"""),
                file=control)
        self.assertEqual(0, self.builder.installBuildDeps())
        self.assertThat(
            [proc._args["args"] for proc in processes_fixture.procs],
            MatchesListwise([
                RanInChroot(
                    self.home_dir, "apt-get",
                    "-o", StartsWith("Dir::Etc::sourcelist="),
                    "-o", "APT::Get::List-Cleanup=false",
                    "update"),
                RanCommand(
                    "sudo", "mv",
                    os.path.join(
                        self.builder.apt_dir, "buildrecipe-archive.list"),
                    os.path.join(
                        self.builder.apt_sources_list_dir,
                        "buildrecipe-archive.list")),
                RanInChroot(
                    self.home_dir, "apt-get",
                    "build-dep", "-y", "--only-source", "foo"),
                ]))
        self.assertEqual(
            (dedent("""\
                Package: foo
                Suite: grumpy
                Component: main
                Purpose: PPA
                Build-Debug-Symbols: no
                """).encode("UTF-8"), stat.S_IFREG | 0o644),
            copies["/CurrentlyBuilding"])
        # This is still in the temporary location, since we mocked the "sudo
        # mv" command.
        with open(os.path.join(
                self.builder.apt_dir,
                "buildrecipe-archive.list")) as tmp_list:
            self.assertEqual(
                "deb-src [trusted=yes] file://%s ./\n" %
                self.builder.apt_dir_relative,
                tmp_list.read())

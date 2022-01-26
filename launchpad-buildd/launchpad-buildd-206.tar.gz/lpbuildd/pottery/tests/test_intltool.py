# Copyright 2009-2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import errno
import os
import tarfile
from textwrap import dedent

from fixtures import TempDir
from six import StringIO
from testtools import TestCase
from testtools.matchers import (
    Equals,
    MatchesSetwise,
    )

from lpbuildd.pottery.intltool import (
    check_potfiles_in,
    ConfigFile,
    find_intltool_dirs,
    find_potfiles_in,
    generate_pot,
    generate_pots,
    get_translation_domain,
    )
from lpbuildd.tests.fakebuilder import (
    FakeMethod,
    UncontainedBackend,
    )


class SetupTestPackageMixin:

    test_data_dir = "pottery_test_data"

    def prepare_package(self, packagename, buildfiles=None):
        """Unpack the specified package in a temporary directory.

        Return the package's directory.

        :param packagename: The name of the package to prepare.
        :param buildfiles: A dictionary of path:content describing files to
            add to the package.
        """
        # First build the path for the package.
        tarpath = os.path.join(
            os.path.dirname(__file__), self.test_data_dir,
            packagename + ".tar.bz2")
        # Then change into the temporary directory and unpack it.
        parent = self.useFixture(TempDir()).path
        with tarfile.open(tarpath, "r|bz2") as tar:
            tar.extractall(parent)
        package_dir = os.path.join(parent, packagename)

        if buildfiles is None:
            return package_dir

        # Add files as requested.
        for path, content in buildfiles.items():
            directory = os.path.dirname(path)
            if directory != '':
                try:
                    os.makedirs(os.path.join(package_dir, directory))
                except OSError as e:
                    # Doesn't matter if it already exists.
                    if e.errno != errno.EEXIST:
                        raise
            with open(os.path.join(package_dir, path), 'w') as the_file:
                the_file.write(content)

        return package_dir


class TestDetectIntltool(TestCase, SetupTestPackageMixin):

    def test_detect_potfiles_in(self):
        # Find POTFILES.in in a package with multiple dirs when only one has
        # POTFILES.in.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_POTFILES_in_1")
        dirs = find_potfiles_in(backend, package_dir)
        self.assertThat(dirs, MatchesSetwise(Equals("po-intltool")))

    def test_detect_potfiles_in_module(self):
        # Find POTFILES.in in a package with POTFILES.in at different levels.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_POTFILES_in_2")
        dirs = find_potfiles_in(backend, package_dir)
        self.assertThat(
            dirs, MatchesSetwise(Equals("po"), Equals("module1/po")))

    def test_check_potfiles_in_content_ok(self):
        # Ideally all files listed in POTFILES.in exist in the source package.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_single_ok")
        self.assertTrue(
            check_potfiles_in(backend, os.path.join(package_dir, "po")))

    def test_check_potfiles_in_content_ok_file_added(self):
        # If a file is not listed in POTFILES.in, the file is still good for
        # our purposes.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_single_ok")
        added_path = os.path.join(package_dir, "src/sourcefile_new.c")
        with open(added_path, "w") as added_file:
            added_file.write("/* Test file. */")
        self.assertTrue(
            check_potfiles_in(backend, os.path.join(package_dir, "po")))

    def test_check_potfiles_in_content_not_ok_file_removed(self):
        # If a file is missing that is listed in POTFILES.in, the file
        # intltool structure is probably broken and cannot be used for
        # our purposes.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_single_ok")
        os.remove(os.path.join(package_dir, "src/sourcefile1.c"))
        self.assertFalse(
            check_potfiles_in(backend, os.path.join(package_dir, "po")))

    def test_check_potfiles_in_wrong_directory(self):
        # Passing in the wrong directory will cause the check to fail
        # gracefully and return False.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_single_ok")
        self.assertFalse(
            check_potfiles_in(backend, os.path.join(package_dir, "foo")))

    def test_find_intltool_dirs(self):
        # Complete run: find all directories with intltool structure.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_full_ok")
        self.assertEqual(
            ["po-module1", "po-module2"],
            find_intltool_dirs(backend, package_dir))

    def test_find_intltool_dirs_broken(self):
        # Complete run: part of the intltool structure is broken.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_full_ok")
        os.remove(os.path.join(package_dir, "src/module1/sourcefile1.c"))
        self.assertEqual(
            ["po-module2"], find_intltool_dirs(backend, package_dir))


class TestIntltoolDomain(TestCase, SetupTestPackageMixin):

    def test_get_translation_domain_makevars(self):
        # Find a translation domain in Makevars.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_domain_makevars")
        self.assertEqual(
            "translationdomain",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_makevars_subst_1(self):
        # Find a translation domain in Makevars, substituted from
        # Makefile.in.in.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package(
            "intltool_domain_base",
            {
                "po/Makefile.in.in": "PACKAGE=packagename-in-in\n",
                "po/Makevars": "DOMAIN = $(PACKAGE)\n",
            })
        self.assertEqual(
            "packagename-in-in",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_makevars_subst_2(self):
        # Find a translation domain in Makevars, substituted from
        # configure.ac.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package(
            "intltool_domain_base",
            {
                "configure.ac": "PACKAGE=packagename-ac\n",
                "po/Makefile.in.in": "# No domain here.\n",
                "po/Makevars": "DOMAIN = $(PACKAGE)\n",
            })
        self.assertEqual(
            "packagename-ac",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_makefile_in_in(self):
        # Find a translation domain in Makefile.in.in.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_domain_makefile_in_in")
        self.assertEqual(
            "packagename-in-in",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_configure_ac(self):
        # Find a translation domain in configure.ac.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_domain_configure_ac")
        self.assertEqual(
            "packagename-ac",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def prepare_ac_init(self, parameters, extra_files=None):
        # Prepare test for various permutations of AC_INIT parameters
        configure_ac_content = dedent("""
            AC_INIT(%s)
            GETTEXT_PACKAGE=AC_PACKAGE_NAME
            """) % parameters
        files = {"configure.ac": configure_ac_content}
        if extra_files is not None:
            files.update(extra_files)
        return self.prepare_package("intltool_domain_base", files)

    def test_get_translation_domain_configure_ac_init(self):
        # Find a translation domain in configure.ac in AC_INIT.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_ac_init(
            "packagename-ac-init, 1.0, http://bug.org")
        self.assertEqual(
            "packagename-ac-init",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_configure_ac_init_single_param(self):
        # Find a translation domain in configure.ac in AC_INIT.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_ac_init("[Just 1 param]")
        self.assertIsNone(
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_configure_ac_init_brackets(self):
        # Find a translation domain in configure.ac in AC_INIT with brackets.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_ac_init(
            "[packagename-ac-init], 1.0, http://bug.org")
        self.assertEqual(
            "packagename-ac-init",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_configure_ac_init_tarname(self):
        # Find a translation domain in configure.ac in AC_INIT tar name
        # parameter.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_ac_init(
            "[Package name], 1.0, http://bug.org, [package-tarname]")
        self.assertEqual(
            "package-tarname",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_configure_ac_init_multiline(self):
        # Find a translation domain in configure.ac in AC_INIT when it
        # spans multiple lines.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_ac_init(
            "[packagename-ac-init],\n    1.0,\n    http://bug.org")
        self.assertEqual(
            "packagename-ac-init",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_configure_ac_init_multiline_tarname(self):
        # Find a translation domain in configure.ac in AC_INIT tar name
        # parameter that is on a different line.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_ac_init(
            "[Package name], 1.0,\n    http://bug.org, [package-tarname]")
        self.assertEqual(
            "package-tarname",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_substitute_package_from_ac_init(self):
        # PACKAGE is substituted from AC_INIT parameters as a fallback.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_ac_init(
            "[packagename-ac-init], 1.0, http://bug.org",
            {"po/Makevars": "DOMAIN = $(PACKAGE)\n"})
        self.assertEqual(
            "packagename-ac-init",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_configure_in(self):
        # Find a translation domain in configure.in.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_domain_configure_in")
        self.assertEqual(
            "packagename-in",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_makefile_in_in_substitute(self):
        # Find a translation domain in Makefile.in.in with substitution from
        # configure.ac.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package(
            "intltool_domain_makefile_in_in_substitute")
        self.assertEqual(
            "domainname-ac-in-in",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_makefile_in_in_substitute_same_name(self):
        # Find a translation domain in Makefile.in.in with substitution from
        # configure.ac from a variable with the same name as in
        # Makefile.in.in.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package(
            "intltool_domain_makefile_in_in_substitute_same_name")
        self.assertEqual(
            "packagename-ac-in-in",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_makefile_in_in_substitute_same_file(self):
        # Find a translation domain in Makefile.in.in with substitution from
        # the same file.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package(
            "intltool_domain_makefile_in_in_substitute_same_file")
        self.assertEqual(
            "domain-in-in-in-in",
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_makefile_in_in_substitute_broken(self):
        # Find no translation domain in Makefile.in.in when the substitution
        # cannot be fulfilled.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package(
            "intltool_domain_makefile_in_in_substitute_broken")
        self.assertIsNone(
            get_translation_domain(backend, os.path.join(package_dir, "po")))

    def test_get_translation_domain_configure_in_substitute_version(self):
        # Find a translation domain in configure.in with Makefile-style
        # substitution from the same file.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package(
            "intltool_domain_configure_in_substitute_version")
        self.assertEqual(
            "domainname-in42",
            get_translation_domain(backend, os.path.join(package_dir, "po")))


class TestGenerateTemplates(TestCase, SetupTestPackageMixin):

    def test_generate_pot(self):
        # Generate a given PO template.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_full_ok")
        self.assertEqual(
            "module1",
            generate_pot(
                backend, os.path.join(package_dir, "po-module1"), "module1"),
            "PO template generation failed.")
        expected_path = "po-module1/module1.pot"
        self.assertTrue(
            os.access(os.path.join(package_dir, expected_path), os.F_OK),
            "Generated PO template '%s' not found." % expected_path)

    def test_generate_pot_no_domain(self):
        # Generate a generic PO template.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_full_ok")
        self.assertEqual(
            "messages",
            generate_pot(
                backend, os.path.join(package_dir, "po-module1"), None),
            "PO template generation failed.")
        expected_path = "po-module1/messages.pot"
        self.assertTrue(
            os.access(os.path.join(package_dir, expected_path), os.F_OK),
            "Generated PO template '%s' not found." % expected_path)

    def test_generate_pot_empty_domain(self):
        # Generate a generic PO template.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_full_ok")
        self.assertEqual(
            "messages",
            generate_pot(backend, os.path.join(package_dir, "po-module1"), ""),
            "PO template generation failed.")
        expected_path = "po-module1/messages.pot"
        self.assertTrue(
            os.access(os.path.join(package_dir, expected_path), os.F_OK),
            "Generated PO template '%s' not found." % expected_path)

    def test_generate_pot_not_intltool(self):
        # Fail when not an intltool setup.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_full_ok")
        # Cripple the setup.
        os.remove(os.path.join(package_dir, "po-module1/POTFILES.in"))
        self.assertIsNone(
            generate_pot(
                backend, os.path.join(package_dir, "po-module1"), "nothing"),
            "PO template generation should have failed.")
        not_expected_path = "po-module1/nothing.pot"
        self.assertFalse(
            os.access(os.path.join(package_dir, not_expected_path), os.F_OK),
            "Not expected PO template '%s' generated." % not_expected_path)

    def test_generate_pots(self):
        # Generate all PO templates in the package.
        backend = UncontainedBackend("1")
        package_dir = self.prepare_package("intltool_full_ok")
        expected_paths = [
            'po-module1/packagename-module1.pot',
            'po-module2/packagename-module2.pot',
            ]
        pots_list = generate_pots(backend, package_dir)
        self.assertEqual(expected_paths, pots_list)
        for expected_path in expected_paths:
            self.assertTrue(
                os.access(os.path.join(package_dir, expected_path), os.F_OK),
                "Generated PO template '%s' not found." % expected_path)


class TestConfigFile(TestCase):

    def _makeConfigFile(self, text):
        """Create a `ConfigFile` containing `text`."""
        return ConfigFile(StringIO(dedent(text)))

    def test_getVariable_smoke(self):
        configfile = self._makeConfigFile("""
            A = 1
            B = 2
            C = 3
            """)
        self.assertEqual('1', configfile.getVariable('A'))
        self.assertEqual('2', configfile.getVariable('B'))
        self.assertEqual('3', configfile.getVariable('C'))

    def test_getVariable_exists(self):
        configfile = self._makeConfigFile("DDD=dd.d")
        self.assertEqual('dd.d', configfile.getVariable('DDD'))

    def test_getVariable_ignores_mere_mention(self):
        configfile = self._makeConfigFile("""
            CCC
            CCC = ccc # (this is the real definition)
            CCC
            """)
        self.assertEqual('ccc', configfile.getVariable('CCC'))

    def test_getVariable_ignores_irrelevancies(self):
        configfile = self._makeConfigFile("""
            A = a
            ===
            blah
            FOO(n, m)
            a = case-insensitive

            Z = z
            """)
        self.assertEqual('a', configfile.getVariable('A'))
        self.assertEqual('z', configfile.getVariable('Z'))

    def test_getVariable_exists_spaces_comment(self):
        configfile = self._makeConfigFile("CCC = ccc # comment")
        self.assertEqual('ccc', configfile.getVariable('CCC'))

    def test_getVariable_empty(self):
        configfile = self._makeConfigFile("AAA=")
        self.assertEqual('', configfile.getVariable('AAA'))

    def test_getVariable_empty_spaces(self):
        configfile = self._makeConfigFile("BBB = ")
        self.assertEqual('', configfile.getVariable('BBB'))

    def test_getVariable_nonexistent(self):
        configfile = self._makeConfigFile("X = y")
        self.assertIsNone(configfile.getVariable('FFF'))

    def test_getVariable_broken(self):
        configfile = self._makeConfigFile("EEE \n= eee")
        self.assertIsNone(configfile.getVariable('EEE'))

    def test_getVariable_strips_quotes(self):
        # Quotes get stripped off variables.
        configfile = self._makeConfigFile("QQQ = 'qqq'")
        self.assertEqual('qqq', configfile.getVariable('QQQ'))

        # This is done by invoking _stripQuotes (tested separately).
        configfile._stripQuotes = FakeMethod(result='foo')
        self.assertEqual('foo', configfile.getVariable('QQQ'))
        self.assertNotEqual(0, configfile._stripQuotes.call_count)

    def test_getFunctionParams_single(self):
        configfile = self._makeConfigFile("FUNC_1(param1)")
        self.assertEqual(['param1'], configfile.getFunctionParams('FUNC_1'))

    def test_getFunctionParams_multiple(self):
        configfile = self._makeConfigFile("FUNC_2(param1, param2, param3 )")
        self.assertEqual(
            ['param1', 'param2', 'param3'],
            configfile.getFunctionParams('FUNC_2'))

    def test_getFunctionParams_multiline_indented(self):
        configfile = self._makeConfigFile("""
            ML_FUNC_1(param1,
                param2, param3)
            """)
        self.assertEqual(
            ['param1', 'param2', 'param3'],
            configfile.getFunctionParams('ML_FUNC_1'))

    def test_getFunctionParams_multiline_not_indented(self):
        configfile = self._makeConfigFile("""
            ML_FUNC_2(
            param1,
            param2)
            """)
        self.assertEqual(
            ['param1', 'param2'], configfile.getFunctionParams('ML_FUNC_2'))

    def test_getFunctionParams_strips_quotes(self):
        # Quotes get stripped off function parameters.
        configfile = self._makeConfigFile('FUNC("param")')
        self.assertEqual(['param'], configfile.getFunctionParams('FUNC'))

        # This is done by invoking _stripQuotes (tested separately).
        configfile._stripQuotes = FakeMethod(result='arg')
        self.assertEqual(['arg'], configfile.getFunctionParams('FUNC'))
        self.assertNotEqual(0, configfile._stripQuotes.call_count)

    def test_stripQuotes_unquoted(self):
        # _stripQuotes leaves unquoted identifiers intact.
        configfile = self._makeConfigFile('')
        self.assertEqual('hello', configfile._stripQuotes('hello'))

    def test_stripQuotes_empty(self):
        configfile = self._makeConfigFile('')
        self.assertEqual('', configfile._stripQuotes(''))

    def test_stripQuotes_single_quotes(self):
        # Single quotes are stripped.
        configfile = self._makeConfigFile('')
        self.assertEqual('x', configfile._stripQuotes("'x'"))

    def test_stripQuotes_double_quotes(self):
        # Double quotes are stripped.
        configfile = self._makeConfigFile('')
        self.assertEqual('y', configfile._stripQuotes('"y"'))

    def test_stripQuotes_bracket_quotes(self):
        # Brackets are stripped.
        configfile = self._makeConfigFile('')
        self.assertEqual('z', configfile._stripQuotes('[z]'))

    def test_stripQuotes_opening_brackets(self):
        # An opening bracket must be matched by a closing one.
        configfile = self._makeConfigFile('')
        self.assertEqual('[x[', configfile._stripQuotes('[x['))

    def test_stripQuotes_closing_brackets(self):
        # A closing bracket is not accepted as an opening quote.
        configfile = self._makeConfigFile('')
        self.assertEqual(']x]', configfile._stripQuotes(']x]'))

    def test_stripQuotes_multiple(self):
        # Only a single layer of quotes is stripped.
        configfile = self._makeConfigFile('')
        self.assertEqual('"n"', configfile._stripQuotes("'\"n\"'"))

    def test_stripQuotes_single_quote(self):
        # A string consisting of just one quote is not stripped.
        configfile = self._makeConfigFile('')
        self.assertEqual("'", configfile._stripQuotes("'"))

    def test_stripQuotes_mismatched(self):
        # Mismatched quotes are not stripped.
        configfile = self._makeConfigFile('')
        self.assertEqual("'foo\"", configfile._stripQuotes("'foo\""))

    def test_stripQuotes_unilateral(self):
        # A quote that's only on one end doesn't get stripped.
        configfile = self._makeConfigFile('')
        self.assertEqual('"foo', configfile._stripQuotes('"foo'))

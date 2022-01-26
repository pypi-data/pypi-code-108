# Copyright 2009-2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Functions to build PO templates on the builder."""

__metaclass__ = type
__all__ = [
    'check_potfiles_in',
    'generate_pot',
    'generate_pots',
    'get_translation_domain',
    'find_intltool_dirs',
    'find_potfiles_in',
    ]

import os.path
import re
import subprocess
import tempfile


def find_potfiles_in(backend, package_dir):
    """Search `package_dir` and its subdirectories for POTFILES.in.

    :param backend: The `Backend` where work is done.
    :param package_dir: The directory to search.
    :returns: A list of names of directories that contain a file
        POTFILES.in, relative to `package_dir`.
    """
    paths = backend.find(
        package_dir, include_directories=False, name="POTFILES.in")
    return [os.path.dirname(path) for path in paths]


def check_potfiles_in(backend, path):
    """Check if the files listed in the POTFILES.in file exist.

    Running 'intltool-update -m' will perform this check and also take a
    possible POTFILES.skip into account. It stores details about 'missing'
    (files that should be in POTFILES.in) and 'notexist'ing files (files
    that are listed in POTFILES.in but don't exist) in files which are
    named accordingly. These files are removed before the run.

    We don't care about files missing from POTFILES.in but want to know if
    all listed files exist. The presence of the 'notexist' file tells us
    that.

    :param backend: The `Backend` where work is done.
    :param path: The directory where POTFILES.in resides.
    :returns: False if the directory does not exist, if an error occurred
        when executing intltool-update or if files are missing from
        POTFILES.in. True if all went fine and all files in POTFILES.in
        actually exist.
    """
    # Abort nicely if the directory does not exist.
    if not backend.isdir(path):
        return False
    # Remove stale files from a previous run of intltool-update -m.
    backend.run(
        ["rm", "-f"] +
        [os.path.join(path, name) for name in ("missing", "notexist")])
    with open("/dev/null", "w") as devnull:
        try:
            backend.run(
                ["/usr/bin/intltool-update", "-m"],
                stdout=devnull, stderr=devnull, cwd=path)
        except subprocess.CalledProcessError:
            return False

    return not backend.path_exists(os.path.join(path, "notexist"))


def find_intltool_dirs(backend, package_dir):
    """Search for directories with intltool structure.

    `package_dir` and its subdirectories are searched. An 'intltool
    structure' is a directory that contains a POFILES.in file and where all
    files listed in that POTFILES.in do actually exist. The latter
    condition makes sure that the file is not stale.

    :param backend: The `Backend` where work is done.
    :param package_dir: The directory to search.
    :returns: A list of directory names, relative to `package_dir`.
    """
    return sorted(
        podir for podir in find_potfiles_in(backend, package_dir)
        if check_potfiles_in(backend, os.path.join(package_dir, podir)))


def _get_AC_PACKAGE_NAME(config_file):
    """Get the value of AC_PACKAGE_NAME from function parameters.

    The value of AC_PACKAGE_NAME is either the first or the fourth
    parameter of the AC_INIT call if it is called with at least two
    parameters.
    """
    params = config_file.getFunctionParams("AC_INIT")
    if params is None or len(params) < 2:
        return None
    if len(params) < 4:
        return params[0]
    else:
        return params[3]


def _try_substitution(config_files, varname, substitution):
    """Try to find a substitution in the config files.

    :returns: The completed substitution or None if none was found.
    """
    subst_value = None
    if varname == substitution.name:
        # Do not look for the same name in the current file.
        config_files = config_files[:-1]
    for config_file in reversed(config_files):
        subst_value = config_file.getVariable(substitution.name)
        if subst_value is None and substitution.name == "PACKAGE":
            subst_value = _get_AC_PACKAGE_NAME(config_file)
        if subst_value is not None:
            # Substitution found.
            break
    else:
        # No substitution found.
        return None
    return substitution.replace(subst_value)


def get_translation_domain(backend, dirname):
    """Get the translation domain for this PO directory.

    Imitates some of the behavior of intltool-update to find out which
    translation domain the build environment provides. The domain is usually
    defined in the GETTEXT_PACKAGE variable in one of the build files. Another
    variant is DOMAIN in the Makevars file. This function goes through the
    ordered list of these possible locations, top to bottom, and tries to
    find a valid value. Since the same variable name may be defined in
    multiple files (usually configure.ac and Makefile.in.in), it needs to
    keep trying with the next file, until it finds the most specific
    definition.

    If the found value contains a substitution, either autoconf style (@...@)
    or make style ($(...)), the search is continued in the same file and back
    up the list of files, now searching for the substitution. Multiple
    substitutions or multi-level substitutions are not supported.
    """
    locations = [
        ('../configure.ac', 'GETTEXT_PACKAGE', True),
        ('../configure.in', 'GETTEXT_PACKAGE', True),
        ('Makefile.in.in', 'GETTEXT_PACKAGE', False),
        ('Makevars', 'DOMAIN', False),
    ]
    value = None
    substitution = None
    config_files = []
    for filename, varname, keep_trying in locations:
        path = os.path.join(dirname, filename)
        if not backend.path_exists(path):
            # Skip non-existent files.
            continue
        with tempfile.NamedTemporaryFile() as local_file:
            backend.copy_out(path, local_file.name)
            config_files.append(ConfigFile(local_file.file))
        new_value = config_files[-1].getVariable(varname)
        if new_value is not None:
            value = new_value
            if value == "AC_PACKAGE_NAME":
                value = _get_AC_PACKAGE_NAME(config_files[-1])
            else:
                # Check if the value needs a substitution.
                substitution = Substitution.get(value)
                if substitution is not None:
                    # Try to substitute with value.
                    value = _try_substitution(
                        config_files, varname, substitution)
                    if value is None:
                        # No substitution found; the setup is broken.
                        break
        if value is not None and not keep_trying:
            # A value has been found.
            break
    return value


def generate_pot(backend, podir, domain):
    """Generate one PO template using intltool.

    Although 'intltool-update -p' can try to find out the translation domain
    we trust our own code more on this one and simply specify the domain.
    Also, the man page for 'intltool-update' states that the '-g' option
    "has an additional effect: the name of current working directory is no
    more  limited  to 'po' or 'po-*'." We don't want that limit either.

    :param backend: The `Backend` where work is done.
    :param podir: The PO directory in which to build template.
    :param domain: The translation domain to use as the name of the template.
      If it is None or empty, 'messages.pot' will be used.
    :return: The effective domain if generation succeeded, otherwise None.
    """
    if domain is None or domain.strip() == "":
        domain = "messages"
    with open("/dev/null", "w") as devnull:
        try:
            backend.run(
                ["/usr/bin/intltool-update", "-p", "-g", domain],
                stdout=devnull, stderr=devnull, cwd=podir)
            return domain
        except subprocess.CalledProcessError:
            return None


def generate_pots(backend, package_dir):
    """Top-level function to generate all PO templates in a package."""
    potpaths = []
    for podir in find_intltool_dirs(backend, package_dir):
        full_podir = os.path.join(package_dir, podir)
        domain = get_translation_domain(backend, full_podir)
        effective_domain = generate_pot(backend, full_podir, domain)
        if effective_domain is not None:
            potpaths.append(os.path.join(podir, effective_domain + ".pot"))
    return potpaths


class ConfigFile:
    """Represent a config file and return variables defined in it."""

    def __init__(self, file_or_name):
        if isinstance(file_or_name, str):
            with open(file_or_name, "rb") as conf_file:
                content = conf_file.read()
        else:
            content = file_or_name.read()
        if isinstance(content, bytes):
            content = content.decode("UTF-8", "replace")
        self.content = content

    def _stripQuotes(self, identifier):
        """Strip surrounding quotes from `identifier`, if present.

        :param identifier: a string, possibly surrounded by matching
            'single,' "double," or [bracket] quotes.
        :return: `identifier` but with the outer pair of matching quotes
            removed, if they were there.
        """
        if len(identifier) < 2:
            return identifier

        quote_pairs = [
            ('"', '"'),
            ("'", "'"),
            ("[", "]"),
            ]
        for (left, right) in quote_pairs:
            if identifier.startswith(left) and identifier.endswith(right):
                return identifier[1:-1]

        return identifier

    def getVariable(self, name):
        """Search the file for a variable definition with this name."""
        pattern = re.compile(
            r"^%s[ \t]*=[ \t]*([^\s]*)" % re.escape(name), re.M)
        result = pattern.search(self.content)
        if result is None:
            return None
        return self._stripQuotes(result.group(1))

    def getFunctionParams(self, name):
        """Search file for a function call with this name, return parameters.
        """
        pattern = re.compile(r"^%s\(([^)]*)\)" % re.escape(name), re.M)
        result = pattern.search(self.content)
        if result is None:
            return None
        else:
            return [
                self._stripQuotes(param.strip())
                for param in result.group(1).split(',')
                ]


class Substitution(object):
    """Find and replace substitutions.

    Variable texts may contain other variables which should be substituted
    for their value. These are either marked by surrounding @ signs (autoconf
    style) or preceded by a $ sign with optional () (make style).

    This class identifies a single such substitution in a variable text and
    extracts the name of the variable whose value is to be inserted. It also
    facilitates the actual replacement so that caller does not have to worry
    about the substitution style that is being used.
    """

    autoconf_pattern = re.compile(r"@([^@]+)@")
    makefile_pattern = re.compile(r"\$\(?([^\s\)]+)\)?")

    @staticmethod
    def get(variabletext):
        """Factory method.

        Creates a Substitution instance and checks if it found a substitution.

        :param variabletext: A variable value with possible substitution.
        :returns: A Substitution object or None if no substitution was found.
        """
        subst = Substitution(variabletext)
        if subst.name is not None:
            return subst
        return None

    def _searchForPatterns(self):
        """Search for all the available patterns in variable text."""
        result = self.autoconf_pattern.search(self.text)
        if result is None:
            result = self.makefile_pattern.search(self.text)
        return result

    def __init__(self, variabletext):
        """Extract substitution name from variable text."""
        self.text = variabletext
        self.replaced = False
        result = self._searchForPatterns()
        if result is None:
            self._replacement = None
            self.name = None
        else:
            self._replacement = result.group(0)
            self.name = result.group(1)

    def replace(self, value):
        """Return a copy of the variable text with the substitution resolved.
        """
        self.replaced = True
        return self.text.replace(self._replacement, value)

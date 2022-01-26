# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

# pylint: disable=no-member

import logging
import os
import shutil
from glob import iglob
from logging import info, warning
from typing import Callable, Iterable, List, Optional, Pattern, Set, Tuple, Union, cast

from portmodlib.atom import Atom
from portmodlib.colour import blue, magenta
from portmodlib.execute import execute
from portmodlib.fs import ci_exists, is_parent, make_unique_filename, patch_dir
from portmodlib.globals import messages_dir, warnings_dir
from portmodlib.l10n import l10n
from portmodlib.pybuild import FullPybuild, InstallDir, get_installed_env
from portmodlib.source import Source
from portmodlib.usestr import check_required_use, use_reduce
from portmodlib.util import fnmatch_list_to_re


def apply_patch(patch: str):
    """
    Applies git patch using Git apply

    Patch files must be in a format that can be applied via git apply. Such patches can
    be produced with ``git diff --no-index ORIG NEW``. The ``--binary`` option can be
    used to produce binary diffs for non-text files.

    Patches must be self-applying.  I.e. they should not rely on paths being passed to
    git apply, and must apply from the default working directory in src_prepare.

    It is recommended that a comment header is included to describe what the patch
    does, where it's from etc.

    args:
        patch: Path to the patch to be applied
    """
    print(l10n("applying-patch", patch=patch))
    execute(["git", "apply", patch, "--stat", "--apply"])


class Pybuild1(FullPybuild):
    """
    The class all Pybuilds should derive.

    The name and path of a pybuild declares the package name, category, version and
    (optionally) revision::

        {CATEGORY}/{PKG_NAME}-{VER}(-r{REV}).pybuild

    Categories and package names may contain lower case letters, numbers and hyphens.
    Versions may contain numbers and dots. Revisions may only contain numbers
    (following the -r prefix). (See the PMS for the complete naming scheme).

    Note that revisions refer to revisions of the pybuild itself, not the package,
    and are used to indicate that the way the mod is configured has changed in a way
    that will impact the installed version. For changes, such as the source files
    moving, that would not impact a mod that is already installed, you do not need to
    update the revision.

    .. [1] Fields which are set automatically and should not be defined in the
           package file
    """

    __file__ = __file__

    P: Atom
    """
    The package name and version. [1]_

    E.g.: ``example-suite-1.0``
    """
    PF: Atom
    """
    The package name with version and revision. [1]_

    E.g.: ``example-suite-1.0-r1``
    """
    PN: Atom
    """
    The package name without version. [1]_

    E.g.: ``example-suite``
    """
    CATEGORY: str
    """
    The package's category. [1]_

    E.g. ``base``
    """
    PV: str
    """
    The package's version without revision [1]_

    E.g. ``1.0``
    """
    PR: str
    """
    The package's revision [1]_

    E.g. ``r1``

    Is equal to ``r0`` is no revision is specified
    """
    PVR: str
    """
    The package's version and revision [1]_

    E.g. ``1.0-r1``
    """
    USE: Set[str]
    """
    Enabled use flags [1]_

    Scope: All except __init__
    """
    WORKDIR: str
    """
    The directory where packaging takes place [1]_

    Scope: src_*
    """
    T: str
    """
    Path to a temporary directory which may be used during packaging [1]_

    Scope: All except __init__
    """
    D: str
    """
    The full path of the directory where the package is to be installed. [1]_

    Note that this is a temporary directory and not the final install location.

    Scope: src_install
    """
    ROOT: str
    """
    The full path of the prefix root where packages will be installed

    Note: This functions as both ROOT and SYSROOT (as defined by PMS section 11.1).

    Scope: src_*, pkg_*
    """
    A: List[Source]
    """
    The list of enabled sources [1]_

    Scope: All except __init__
    """
    UNFETCHED: List[Source]
    """
    The list of sources which need to be fetched [1]_

    Scope: pkg_nofetch
    """
    DEPEND = ""
    """
    Build dependencies.

    Is used to specify packages which need to be installed in order for this package to
    install correctly.

    Most mods do not have build dependencies, however mods that require patching using
    tools external to portmod, or packages that generate content from other sources,
    will need to include their masters, or the other sources, as build dependencies,
    to ensure that they are installed prior to the package being installed.

    Format:
    A list of dependencies in the form of package atoms. All dependencies should
    include both category and package name. Versions should also be included if
    the package depends on a specific version of another mod.
    It is recommended not to include a version number in the dependency unless it is
    known that the package will not work with other versions.

    Ranges of versions can be indicated by prefixing >,<,<=,>= to the atoms.
    E.g. ``>=cat/foo-1.0``

    Use flag dependencies can be specified in the following manner:

    - ``cat/foo[flag]`` - Indicates that flag must be enabled
    - ``cat/foo[flag,flag2]`` - Indicates that both flag and flag2 must be enabled
    - ``cat/foo[!flag]`` - Indicates that flag must be disabled
    - ``cat/foo[flag?]`` - Indicates that flag must be enabled if it is enabled for
        this package
    - ``cat/foo[!flag?]`` - Indicates that flag must be disabled if it is enabled for
        this package

    Atoms can be surrounded by use-conditionals if they are only dependencies when
    that use flag is enabled/disabled.

    E.g. ``flag? ( cat/foo )``

    Atoms can be grouped and prefixed by a ``||`` operator to indicate that any of the
    given packages will satisfy the dependency.

    E.g. ``|| ( cat/foo cat/bar cat/baz )``

    Note that it is required that the parentheses ``(`` ``)`` are separated from the atoms
    by whitespace.

    Packages which cannot be installed at the same time can be marked as blocks using the
    ``!!`` operator. I.e. ``!!cat/foo`` indicates that ``cat/foo`` cannot be installed at
    the same time as the current package.
    """

    RDEPEND = ""
    """
    Runtime dependencies.

    Is used to specify packages which are required at runtime for this package
    to function. The format is the same as for DEPEND
    """
    DATA_OVERRIDES = ""
    """
    A use-reduce-able list of atoms indicating packages whose data directories should
    come before the data directories of this package when sorting data directories.

    They do not need to be dependencies. Blockers (atoms beginning with !!) can be used
    to specify underrides, and use dependencies (e.g. the [bar] in foo[bar]) can be
    used to conditionally override based on the target atom's flag configuration.

    Not included in PMS
    """
    IUSE = ""
    """
    A field containing a space-separated list of the use flags used by the package.

    IUSE should contain all regular use flags used by this package, both local and
    global. Prefixing the use flags with a + means that the option is enabled by
    default. Otherwise use flags are disabled by default.

    Note that you do not need to include TEXTURE_SIZES type flags in IUSE, but
    USE_EXPAND variables should be included in IUSE.
    """
    TIER = "a"
    """
    The Tier of a package represents the position of its data directories and plugins
    in the virtual file system.

    This is used to group packages in such a way to avoid having to individually
    specify overrides whenever possible.

    The value is either in the range [0-9] or [a-z].

    Default value: 'a'

    Tier 0 represents top-level mods such as morrowind
    Tier 1 is for mods that replace or modify top-level mods. E.g. texture and mesh replacers.
    Tier 2 is for large mods that are designed to be built on top of by other mods, such as Tamriel Data
    Tier a is for all other mods.
    Tier z is for mods that should be installed or loaded last. E.g. omwllf
    The remaining tiers are reserved in case the tier system needs to be expanded

    Not included in PMS
    """
    KEYWORDS = ""
    """
    Keywords indicating compatibility.
    Existence of the keyword indicates that the mod is stable on that platform.

    a ~ in front of the keyword indicates that the mod is unstable on that platform
    no keyword indicates that the mod is untested on that platform
    a - in front of the keyword indicates that the mod is known to not work on that platform

    E.g. A package that works on OpenMW but does not on tes3mp::

        KEYWORDS='openmw -tes3mp'
    """
    LICENSE = ""
    """
    One or more licenses used by the package.

    A list of licenses can be found in the licenses directory of the repository.
    """
    NAME = ""
    """
    Descriptive package name.

    The package name used for identification is the name used in the filename, however
    this name is included when searching for packages.
    """
    DESC = ""
    """
    A short description of the package.

    Is may (depending on options provided) be used in searches.
    Note that a longer description can be provided in metadata.yaml.
    """
    HOMEPAGE = ""
    """
    The URL of the package's homepage(s).

    Used for descriptive purposes and included in search results.
    """
    REBUILD_FILES: List[str] = []
    """
    Files in the VFS which, if changed, should cause this package to be rebuilt

    Can include glob-style patterns using the *, ? and [] operators.
    See https://docs.python.org/3/library/fnmatch.html.
    Unlike normal fnmatch parsing, wildcards (*) will not match accross
    path separators.

    This field can be modified during installation, and will only be used after the
    package has been installed.
    """
    RESTRICT = ""
    """
    Lists features which should be disabled for this package

    The following two options are supported:

    * mirror: The package's SRC_URI entries should not be mirrored, and mirrors
      should not be checked when fetching.
    * fetch: The packages's SRC_URI entries should not be fetched automatically,
      and the pkg_nofetch function should be invoked if a source cannot be found.
      This option implies mirror.

    Note that portmod also supports determining these automatically based on source
    URIs and licenses, so it is no longer necessary to set them explicitly. mirror
    is restricted for licenses which are not in the REDISTRIBUTABLE license group
    (see license_groups.yaml), and fetch is restricted for files which are not
    redistributable (according to license) and do not have a scheme in their
    SRC_URI (i.e. just a filename, no https://domain.tld etc.).
    """
    PROPERTIES = ""
    """
    A white-space-delimited list of additional properties of the given pybuild to
    enable special behaviour.

    Possible values are given below:

    * ``live``: Indicates that the pybuild doesn't have a specific version (e.g. if
        installing from a git repository branch but not using a specific commit).
        Live pybuilds should have an empty KEYWORDS list, as stability testing is
        not meaningful if the upstream source is changing.
    * ``local``: Only used internally to refer to Local mods with generated metadata
    """
    TEXTURE_SIZES = ""
    """
    A field declaring the texture size options that the package supports.

    If only one texture size option is available, this field need not be included.
    Texture sizes should be numbers representing the size of the texture in pixels.
    Given that textures are usually two-dimensional, the convention is to use:
    :math:`\\sqrt{ l \\cdot w}`

    E.g.::

        TEXTURE_SIZES = "1024 2048"

    This is a special type of USE_EXPAND variable, as use flags are created for its
    values in the form texture_size_SIZE (in the above example texture_size_1024 and
    texture_size_2048).

    These use flags can (and should) be used in the pybuild to enable sources and
    InstallDirs conditionally depending on whether or not the texture size was selected.
    Exactly one of these use flags will be enabled when the mod is installed depending
    on the value of the TEXTURE_SIZE variable in the user's portmod.cfg.

    Not included in the PMS
    """
    REQUIRED_USE = ""
    """
    An expression indicating valid combinations of use flags.

    Consists of a string containing sub-expressions of the form given below.
    Note that the brackets can contain arbitrary nested expressions of this form, and
    are not limited to what is shown in the examples below.

    ===================================================   ============================
    Behaviour                                             Expression
    ===================================================   ============================
    flag must be enabled                                  ``flag``
    flag must not be enabled                              ``!flag``
    If flag1 enabled then flag2 enabled                   ``flag1? ( flag2 )``
    If flag1 disabled then flag2 enabled                  ``!flag1? ( flag2 )``
    If flag1 disabled then flag2 disabled	          ``!flag1? ( !flag2 )``
    Must enable any one or more (inclusive or)            ``|| ( flag1 flag2 flag3 )``
    Must enable exactly one but not more (exclusive or)   ``^^ ( flag1 flag2 flag3 )``
    May enable at most one                                ``?? ( flag1 flag2 flag3 )``
    ===================================================   ============================
    """
    SRC_URI = ""
    """
    A List of sources to be fetched.

    If source files should be renamed, this can be done with the arrow operator as
    shown in the example below.

    Sources can be wrapped in use-conditional expressions to prevent certain sources
    from being downloaded unless certain use flags are set or unset.

    E.g.::

        SRC_URI=\"\"\"
            http://mw.modhistory.com/file.php?id=9321 -> FileName-1.0.zip
            flag? ( https://cdn.bethsoft.com/elderscrolls/morrowind/other/masterindex.zip )
        \"\"\"

    Note that if you are renaming files, they should correspond to the original
    filename as best possible, but should also contain version information of some sort
    to prevent conflicts with other sources from the same package. That is, if the
    package is updated, we do not want the updated source name to be the same as a
    previous source name, even if the source name did not change upstream.
    """
    __ENV = None
    PATCHES = ""
    """
    A list of patch files stored within the package's files directory in the repository

    Note that unlike as specified in the PMS, their paths must be relative to the
    files directory.

    See :func:`~apply_patch` for details on the supported patch format.
    """
    S = None
    """
    Specifies the default working directory for src_* functions.

    The default value (if S is None) is the name (minus extension) of the first source
    in SRC_URI (after use-conditionals have been evaluated).
    If this path does not exist, the working directory falls back to WORKDIR.

    This is also used to determine the base source path used for installing a InstallDir
    in the default src_install if S is not defined on the InstallDir.
    """
    INSTALL_DIRS: List[InstallDir] = []
    """
    The INSTALL_DIRS variable consists of a python list of InstallDir objects.

    E.g.::

        INSTALL_DIRS=[
            InstallDir(
                'Morrowind/Data Files',
                REQUIRED_USE='use use ...',
                DESTPATH='.',
                PLUGINS=[File('Plugin Name',
                    REQUIRED_USE='use use ...', satisfied
                )],
                ARCHIVES=[File('Archive Name')],
                S='Source Name Without Extension',
            )
        ]

    Not included in PMS
    """

    def src_prepare(self):
        if self.PATCHES:
            enabled = self.get_use()
            for patch in use_reduce(self.PATCHES, enabled, flat=True):
                path = os.path.join(self.FILESDIR, patch)
                apply_patch(path)

    def _get_install_dir_dest_specific(self, install_dir: InstallDir) -> str:
        install_dir_dest = self._get_install_dir_dest()

        if install_dir.RENAME is None:
            return os.path.normpath(
                os.path.join(self.D, install_dir_dest, install_dir.PATCHDIR)
            )
        else:
            return os.path.normpath(
                os.path.join(
                    self.D,
                    install_dir_dest,
                    install_dir.PATCHDIR,
                    install_dir.RENAME,
                )
            )

    def _install_directory(
        self, source: str, install_dir: InstallDir, to_install: Set[str]
    ):
        case_insensitive = os.environ.get("CASE_INSENSITIVE_FILES", False)

        dest = self._get_install_dir_dest_specific(install_dir)

        os.makedirs(dest, exist_ok=True)
        blacklist_entries = install_dir.BLACKLIST or []

        for file in install_dir.get_files():
            # ignore files which will not be used
            if not check_required_use(
                file.REQUIRED_USE, self.get_use(), self.valid_use
            ):
                blacklist_entries.append(file.NAME)

        blacklist = fnmatch_list_to_re(blacklist_entries)
        if install_dir.WHITELIST is None:
            whitelist = None
        else:
            whitelist = fnmatch_list_to_re(install_dir.WHITELIST)

        def get_listfn(filter_re: Pattern, polarity: bool):
            def fn(directory: str, contents: Iterable[str]):
                paths = []
                basedir = os.path.relpath(directory, source)
                for file in contents:
                    path = os.path.normpath(os.path.join(basedir, file))
                    paths.append(path)

                if polarity:
                    return {
                        file
                        for path, file in zip(paths, contents)
                        if filter_re.match(path)
                        and not os.path.isdir(os.path.join(directory, file))
                    }
                else:
                    return {
                        file
                        for path, file in zip(paths, contents)
                        if not filter_re.match(path)
                        and not os.path.isdir(os.path.join(directory, file))
                    }

            return fn

        # Function to ingore additional paths, given an existing ignore function
        def ignore_more(
            ignorefn, to_ignore: List[str]
        ) -> Callable[[str, List[str]], Set[str]]:
            def fn(directory: str, contents: Iterable[str]):
                results = ignorefn(directory, contents)
                for name in contents:
                    if any(
                        os.path.normpath(os.path.join(directory, name))
                        == os.path.normpath(path)
                        for path in to_ignore
                    ):
                        results.add(name)
                return results

            return fn

        # Determine if any other InstallDirs are inside this one and add them to the blacklist
        to_ignore = []
        for other_path in to_install:
            if other_path != source and is_parent(
                os.path.abspath(other_path), os.path.abspath(source)
            ):
                to_ignore.append(other_path)

        if os.path.islink(source):
            linkto = os.readlink(source)
            if os.path.exists(dest):
                if os.path.islink(dest):
                    os.remove(dest)
                else:
                    os.rmdir(dest)
            os.symlink(linkto, dest, True)
        elif whitelist is not None:
            ignore = get_listfn(whitelist, False)
            if to_ignore:
                ignore = ignore_more(ignore, to_ignore)
            patch_dir(source, dest, ignore=ignore, case_sensitive=not case_insensitive)
        elif blacklist_entries:
            ignore = get_listfn(blacklist, True)
            if to_ignore:
                ignore = ignore_more(ignore, to_ignore)
            patch_dir(source, dest, ignore=ignore, case_sensitive=not case_insensitive)
        else:
            ignore = None
            if to_ignore:
                ignore = ignore_more(lambda _d, _c: set(), to_ignore)
            patch_dir(source, dest, case_sensitive=not case_insensitive, ignore=ignore)

    def src_install(self):
        to_install: List[Tuple[str, InstallDir, bool]] = []
        sources = set()
        for install_dir in self.INSTALL_DIRS:
            source_dir = install_dir.S or cast(str, self.S)
            source = os.path.normpath(
                os.path.join(self.WORKDIR, source_dir, install_dir.PATH)
            )
            sources.add(source)
            if check_required_use(
                install_dir.REQUIRED_USE, self.get_use(), self.valid_use
            ):
                # self.S will be set in package.py via the PhaseState
                to_install.append((source, install_dir, True))
            else:
                to_install.append((source, install_dir, False))

        for (source, install_dir, enabled) in to_install:
            source_dir_path = os.path.join(
                install_dir.S or cast(str, self.S), install_dir.PATH
            )

            if enabled:
                info(
                    l10n(
                        "installing-directory-into",
                        dir=magenta(source_dir_path),
                        dest=magenta(self._get_install_dir_dest_specific(install_dir)),
                    )
                )
                for doc_path in set(install_dir.DOC) | {
                    "README*",
                    "readme*",
                    "ReadMe*",
                    "ChangeLog",
                    "CHANGELOG*",
                    "AUTHORS*",
                    "NEWS*",
                    "TODO*",
                    "CHANGES*",
                    "THANKS*",
                    "BUGS*",
                    "FAQ*",
                    "CREDITS*",
                    "Doc/*",
                    "doc/*",
                    "docs/*",
                    "Docs/*",
                }:
                    self.dodoc(os.path.join(self.WORKDIR, source_dir_path, doc_path))
                self._install_directory(source, install_dir, sources)
            else:
                print(
                    l10n(
                        "skipping-directory",
                        dir=magenta(source_dir_path),
                        req=blue(install_dir.REQUIRED_USE),
                    )
                )

    def pkg_postinst(self):
        pass

    def pkg_prerm(self):
        pass

    def unpack(self, archives: Union[str, Iterable[Union[Source, str]]]):
        """
        Unpacks the given archive into the workdir

        args:
            archives: The list of archives to be unpacked
        """
        # Slow import
        import patoolib

        if isinstance(archives, str):
            archives = [archives]

        for archive in archives:
            if isinstance(archive, str):
                name = archive
                path = archive
            else:
                path = archive.path
                name = archive.name

            info(">>> " + l10n("pkg-unpacking-source", archive=name))
            archive_name, ext = os.path.splitext(os.path.basename(name))
            # Hacky way to handle tar.etc having multiple extensions
            if archive_name.endswith("tar"):
                archive_name, _ = os.path.splitext(archive_name)
            outdir = os.path.join(self.WORKDIR, archive_name)
            os.makedirs(outdir)
            if logging.root.level >= logging.WARN:
                verbosity = -1
            else:
                verbosity = 0
            patoolib.extract_archive(
                path, outdir=outdir, interactive=False, verbosity=verbosity
            )

    def src_unpack(self):
        """
        Unpacks archives into the WORKDIR

        By default calls: ``self.unpack(self.A)``
        """
        self.unpack(self.A)

    def can_update_live(self) -> bool:
        """
        Indicates whether or not a live package can be updated.

        returns:
            If the package has ``PROPERTIES="live"`` and can be updated, returns True
            Otherwise, returns False
        """
        return False

    @staticmethod
    def execute(
        command: str, pipe_output: bool = False, pipe_error: bool = False
    ) -> Optional[str]:
        """
        Allows execution of arbitrary commands at runtime.
        Command is sandboxed with filesystem and network access depending on
        the context in which it is called

        args:
            command: Command to be executed
            pipe_output: If true, returns the output of the command
        """
        raise Exception("execute was called from an invalid context")

    def warn(self, string: str):
        """
        Displays warning message both immediately, and in the summary after all
        transactions have been completed

        args:
            string: String to display
        """
        directory = os.path.realpath(os.path.join(warnings_dir(), self.CATEGORY))
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, self.ATOM.PF), "a+") as file:
            print(string, file=file)
        warning(string)

    def info(self, string: str):
        """
        Displays info message both immediately, and in the summary after all
        transactions have been completed

        args:
            string: String to display
        """
        directory = os.path.realpath(os.path.join(messages_dir(), self.CATEGORY))
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, self.ATOM.PF), "a+") as file:
            print(string, file=file)
        info(string)

    def get_installed_env(self):
        """Returns a dictionary containing installed object values"""
        return get_installed_env(self)

    def dodoc(self, pattern: str):
        if not self.D:
            raise Exception("dodoc must be executed within src_install")
        dest = os.environ.get("DOC_DEST") or "doc"

        os.makedirs(os.path.join(self.D, dest, self.PN), exist_ok=True)

        for file in iglob(pattern):
            info(
                l10n(
                    "installing-doc-into",
                    src=os.path.relpath(file, self.WORKDIR),
                    dest=dest,
                )
            )
            # Handle multiple files of the same name.
            #
            # Such files will cause errors on Windows, however it is also a logic error since
            # different pieces of documentation with the same name are probably from
            # different parts of the package (e.g. main mod and a patch) and should
            # probably all be installed side by side.
            #
            # Instead, rename them so they have unique names.
            if os.environ.get("CASE_INSENSITIVE_FILES", False):
                path = os.path.join(dest, self.PN, os.path.basename(file))
                ci_path = ci_exists(path, prefix=self.D)
                if ci_path:
                    dest_path = make_unique_filename(
                        os.path.join(self.D, path), case_insensitive=True
                    )
                    shutil.move(file, dest_path)
                else:
                    shutil.move(file, os.path.join(self.D, dest, self.PN))
            else:
                dest_path = os.path.join(self.D, dest, self.PN, os.path.basename(file))
                if os.path.exists(dest_path):
                    dest_path = make_unique_filename(os.path.join(self.D, path))

                shutil.move(file, dest_path)

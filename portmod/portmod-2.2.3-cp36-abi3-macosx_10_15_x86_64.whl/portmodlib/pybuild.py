# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import json
import lzma
import os
from pathlib import Path
from typing import Any, Generator, Iterable, List, Optional, Set, Tuple, Union

from .atom import Atom, FQAtom, QualifiedAtom
from .globals import local_mods, root
from .source import Source
from .usestr import check_required_use, use_reduce


class File:
    """Represents important installed files and their metadata"""

    def __init__(
        self,
        NAME: str,
        REQUIRED_USE: str = "",
        OVERRIDES: Union[str, List[str]] = [],
        **kwargs,
    ):
        """
        File objects also support a REQUIRED_USE variable, for , and an OVERRIDES variable for overriding other plugins in the load order.
        """
        self.__keys__: Set[str] = set()
        self.NAME: str = NAME
        """Name of the file relative to the root of the InstallDir"""
        self.REQUIRED_USE: str = REQUIRED_USE
        """
        Requirements for installing this file

        The default empty string is always satisfied.
        See Pybuild1.REQUIRED_USE for details on the syntax.
        """
        self.OVERRIDES: Union[str, List[str]] = OVERRIDES
        """
        A list of files which this overrides when sorting (if applicable).

        Can either be in the form of a string containing use-conditionals (note that
        this does not support files that contain spaces) or a list of files to override.
        Note that these overridden files are not considered masters and do not need to
        be present.

        For archives it determines the order in which the fallback archives will be
        searched during VFS lookups.
        """
        if REQUIRED_USE:
            self._add_kwarg("REQUIRED_USE", REQUIRED_USE)
        if OVERRIDES:
            self._add_kwarg("OVERRIDES", OVERRIDES)

        for key in kwargs:
            self._add_kwarg(key, kwargs[key])

    def _add_kwarg(self, key, value):
        self.__dict__[key] = value
        self.__keys__.add(key)

    def __repr__(self):
        return self.__str__()

    def __str__(self) -> str:
        kvps = []
        for key in self.__keys__:
            value = getattr(self, key)
            if isinstance(value, str):
                kvps.append(f'{key}="{getattr(self, key)}"')
            else:
                kvps.append(f"{key}={getattr(self, key)}")

        separator = ""
        if kvps:
            separator = ", "
        return f'File("{self.NAME}"' + separator + ", ".join(kvps) + ")"

    def _to_cache(self):
        cache = {"NAME": self.NAME}
        for key in self.__keys__:
            cache[key] = getattr(self, key)

        cache["__type__"] = "File"
        return cache


class InstallDir:
    """
    Represents a directory in the Virtual File System

    Note that arbitrary arguments can be passed to the constructor, as
    repositories may make use of custom information.
    See the repository-level documentation for such information.
    """

    def __init__(
        self,
        PATH: str,
        REQUIRED_USE: str = "",
        PATCHDIR: str = ".",
        S: Optional[str] = None,
        WHITELIST: Optional[List[str]] = None,
        BLACKLIST: Optional[List[str]] = None,
        RENAME: Optional[str] = None,
        DATA_OVERRIDES: str = "",
        ARCHIVES: Iterable[File] = (),
        VFS: Optional[bool] = None,
        DOC: Iterable[str] = (),
        **kwargs,
    ):
        self.PATH: str = PATH
        """
        The path to the data directory that this InstallDir represents
        relative to the root of the archive it is contained within.
        """
        self.REQUIRED_USE: str = REQUIRED_USE
        """
        A list of use flags with the same format as the package's
        REQUIRED_USE variable which enable the InstallDir if satisfied.
        Defaults to an empty string that is always satisfied.
        """
        self.PATCHDIR: str = PATCHDIR
        """
        The destination path of the InstallDir within the package's directory.

        Defaults to ".", i.e. the root of the mod directory. If multiple InstallDirs
        share the same PATCHDIR they will be installed into the same directory in the
        order that they are defined in the INSTALL_DIRS list.
        Each unique PATCHDIR has its own entry in the VFS, and its own sorting rules
        """
        self.S: Optional[str] = S
        """
        The source directory corresponding to this InstallDir.

        Similar function to S for the entire pybuild, this determines which directory
        contains this InstallDir, and generally corresponds to the name of the source
        archive, minus extensions. This is required for packages that contain more
        than one source, but is automatically detected for those with only one source
        if it is not specified, and will first take the value of Pybuild1.S, then the
        source's file name without extension if the former was not defined.
        """
        self.WHITELIST: Optional[List[str]] = WHITELIST
        """
        If present, only installs files matching the patterns in this list.
        fnmatch-style globbing patterns (e.g. * and [a-z]) can be used
        """
        self.BLACKLIST: Optional[List[str]] = BLACKLIST
        """
        If present, does not install files matching the patterns in this list.
        fnmatch-style globbing patterns (e.g. * and [a-z]) can be used
        """
        self.RENAME: Optional[str] = RENAME
        """
        Destination path of this directory within the final directory.

        E.g.::

            InstallDir("foo/bar", PATCHDIR=".", RENAME="bar")

        Will install the contents of ``foo/bar`` (in the source) into the directory
        ``bar`` inside the package's installation directory (and also the VFS).
        """
        self.DATA_OVERRIDES: str = DATA_OVERRIDES
        """
        A list of packages that this InstallDir should override in the VFS

        This only has a different effect from Pybuild1.DATA_OVERRIDES if multiple PATCHDIRs
        are set, as it can define overrides for individual PATCHDIRS, while
        Pybuild1.DATA_OVERRIDES affects all PATCHDIRs.
        See Pybuild1.DATA_OVERRIDES for details of the syntax.
        """
        self.ARCHIVES: List[File] = list(ARCHIVES)
        """
        A list of File objects representing VFS archives.

        These will be searched, in order, during VFS file lookups if the file is not
        present in the package directories.
        """
        self.VFS: Optional[bool] = VFS
        """
        Whether or not this InstallDir gets added to the VFS

        Defaults to the value of the VFS variable in the profile configuration
        """
        self.DOC: List[str] = list(DOC)
        """
        A list of patterns matching documentation files within the package

        This documentation will be installed separately
        fnmatch-style globbing patterns (e.g. * and [a-z]) can be used.
        """
        self.__keys__: Set[str] = set()
        if ARCHIVES:
            self._add_kwarg("ARCHIVES", ARCHIVES)
        if PATCHDIR != ".":
            self._add_kwarg("PATCHDIR", PATCHDIR)
        for arg in [
            "DATA_OVERRIDES",
            "RENAME",
            "BLACKLIST",
            "WHITELIST",
            "S",
            "REQUIRED_USE",
        ]:
            if getattr(self, arg):
                self._add_kwarg(arg, getattr(self, arg))
        for key in kwargs:
            self._add_kwarg(key, kwargs[key])

    def _add_kwarg(self, key, value):
        if isinstance(value, list):
            new_value = []
            for item in value:
                if isinstance(item, dict) and item.get("__type__") == "File":
                    file = dict(item)
                    file.pop("__type__", None)
                    new_value.append(File(**file))
                else:
                    new_value.append(item)
            value = new_value

        self.__dict__[key] = value
        self.__keys__.add(key)

    def get_files(self):
        """Generator function yielding file subattributes of the installdir"""
        for key in self.__dict__:
            if isinstance(getattr(self, key), list):
                for item in getattr(self, key):
                    if isinstance(item, File):
                        yield item

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        kvps = []
        for key in self.__keys__:
            value = getattr(self, key)
            if isinstance(value, str):
                kvps.append(f'{key}="{getattr(self, key)}"')
            else:
                kvps.append(f"{key}={getattr(self, key)}")

        separator = ""
        if kvps:
            separator = ", "
        return f'InstallDir("{self.PATH}"' + separator + ", ".join(kvps) + ")"

    def _to_cache(self):
        cache = {"PATH": self.PATH}
        for key in self.__keys__:
            value = getattr(self, key)
            if isinstance(value, list):
                new = []
                for item in value:
                    if isinstance(item, File):
                        new.append(item._to_cache())
                    else:
                        new.append(item)
                value = new
            cache[key] = value

        return cache


class BasePybuild:
    """
    Interface describing the Pybuild Type
    Only describes elements that are cached.
    This class cannot be used to install/uninstall mods
    """

    __file__ = __file__

    ATOM: FQAtom
    RDEPEND: str = ""
    DEPEND: str = ""
    SRC_URI: str = ""
    P: Atom
    PF: Atom
    PN: Atom
    CATEGORY: str
    PV: str
    PR: str
    PVR: str
    CPN: QualifiedAtom
    CP: QualifiedAtom
    REQUIRED_USE: str = ""
    RESTRICT: str = ""
    PROPERTIES: str = ""
    IUSE_EFFECTIVE: Set[str] = set()
    IUSE: Set[str] = set()
    TEXTURE_SIZES: str = ""
    DESC: str = ""
    NAME: str = ""
    HOMEPAGE: str = ""
    LICENSE: str = ""
    KEYWORDS: str = ""
    REBUILD_FILES: List[str] = []
    TIER: str = "a"
    FILE: str
    REPO: str
    INSTALLED: bool = False
    INSTALL_DIRS: List[InstallDir] = []
    DATA_OVERRIDES = ""
    S: Optional[str] = None  # Primary directory during prepare and install operations:w
    PATCHES: str = ""
    # Phase functions defined by the pybuild (or superclasses other than Pybuild1)
    # Used to determine if a function should be run, as certain functions don't have any default
    # behaviour
    FUNCTIONS: List[str] = []
    # Only set in phase functions
    USE: Set[str]

    # Note: This function will only work inside the sandbox, as otherwise INSTALL_DEST
    # won't be an environment variable
    def _get_install_dir_dest(self):
        install_dir_dest = os.environ.get("INSTALL_DEST", ".")
        for attr in dir(self):
            if not attr.startswith("_") and isinstance(getattr(self, attr), str):
                install_dir_dest = install_dir_dest.replace(
                    "{" + attr + "}", getattr(self, attr)
                )
        return os.path.normpath(install_dir_dest)

    def get_use(self) -> Set[str]:
        """Returns the enabled use flags for the package"""
        return self.USE

    def get_dir_path(self, install_dir: InstallDir) -> str:
        """Returns the installed path of the given InstallDir"""
        # Local dirs should be relative to LOCAL_MODS
        if "local" in self.PROPERTIES:
            path = os.path.normpath(os.path.join(local_mods(), self.PN))
        else:
            path = os.path.normpath(
                os.path.join(root(), self._get_install_dir_dest(), install_dir.PATCHDIR)
            )
        if os.path.islink(path):
            return os.readlink(path)
        else:
            return path

    def get_file_path(self, install_dir: InstallDir, esp: File) -> str:
        return os.path.join(self.get_dir_path(install_dir), esp.NAME)

    def get_directories(self) -> Generator[InstallDir, None, None]:
        """
        Returns all enabled InstallDir objects in INSTALL_DIRS
        """
        for install_dir in self.INSTALL_DIRS:
            if check_required_use(
                install_dir.REQUIRED_USE, self.get_use(), self.valid_use
            ):
                yield install_dir

    def get_files(self, typ: str) -> Generator[Tuple[InstallDir, File], None, None]:
        """
        Returns all enabled files and their directories
        """
        for install_dir in self.get_directories():
            if hasattr(install_dir, typ):
                for file in getattr(install_dir, typ):
                    if check_required_use(
                        file.REQUIRED_USE, self.get_use(), self.valid_use
                    ):
                        yield install_dir, file

    def valid_use(self, use: str) -> bool:
        """Returns true if the given flag is a valid use flag for this mod"""
        return use in self.IUSE_EFFECTIVE


class FullPybuild(BasePybuild):
    """Interface describing the Pybuild Type"""

    __file__ = __file__
    TIER: str
    REPO_PATH: Optional[str]
    __pybuild__: str

    # Variables defined during the install/removal process
    A: List[Source]  # List of enabled sources
    D: str  # Destination directory where the mod is to be installed
    FILESDIR: str  # Path of the directory containing additional repository files
    ROOT: str  # Path of the installed directory of the mod
    T: str  # Path of temp directory
    UNFETCHED: List[Source]  # List of sources that need to be fetched
    USE: Set[str]  # Enabled use flags
    WORKDIR: str  # Path of the working directory

    # Note: declared as a string, but converted into a set during __init__
    IUSE = ""  # type: ignore
    KEYWORDS = ""

    def __init__(self):
        self.FILE = self.__class__.__pybuild__

        category = Path(self.FILE).resolve().parent.parent.name
        # Note: type will be fixed later by the loader and will become an FQAtom
        self.ATOM = Atom(  # type: ignore
            "{}/{}".format(category, os.path.basename(self.FILE)[: -len(".pybuild")])
        )

        self.REPO_PATH = str(Path(self.FILE).resolve().parent.parent.parent)
        repo_name_path = os.path.join(self.REPO_PATH, "profiles", "repo_name")
        if os.path.exists(repo_name_path):
            with open(repo_name_path, "r") as repo_file:
                self.REPO = repo_file.readlines()[0].rstrip()
            self.ATOM = FQAtom("{}::{}".format(self.ATOM, self.REPO))

        self.P = Atom(self.ATOM.P)
        self.PN = Atom(self.ATOM.PN)
        self.PV = self.ATOM.PV
        self.PF = Atom(self.ATOM.PF)
        self.PR = self.ATOM.PR or "r0"
        self.CATEGORY = self.ATOM.C
        self.R = self.ATOM.R
        self.CP = QualifiedAtom(self.ATOM.CP)
        self.CPN = QualifiedAtom(self.ATOM.CPN)
        self.PVR = self.ATOM.PVR

        self.IUSE_EFFECTIVE = set()

        if type(self.IUSE) is str:
            self.IUSE = set(self.IUSE.split())  # type: ignore # pylint: disable=no-member
            self.IUSE_EFFECTIVE |= set([use.lstrip("+") for use in self.IUSE])
        else:
            raise TypeError("IUSE must be a space-separated list of use flags")

        if type(self.KEYWORDS) is str:
            self.KEYWORDS = set(self.KEYWORDS.split())  # type: ignore # pylint: disable=no-member
        else:
            raise TypeError("KEYWORDS must be a space-separated list of keywords")

        if type(self.TIER) is int:
            self.TIER = str(self.TIER)
        elif type(self.TIER) is not str:
            raise TypeError("TIER must be a integer or string containing 0-9 or z")

        if type(self.TEXTURE_SIZES) is str:
            texture_sizes = use_reduce(self.TEXTURE_SIZES, matchall=True)
            self.IUSE_EFFECTIVE |= set(
                ["texture_size_{}".format(size) for size in texture_sizes]
            )
        else:
            raise TypeError(
                "TEXTURE_SIZES must be a string containing a space separated list of "
                "texture sizes"
            )

    def pkg_nofetch(self):
        """
        Function to give user instructions on how to fetch a mod
        which cannot be fetched automatically
        """

    def pkg_pretend(self):
        """
        May be used to carry out sanity checks early on in the install process

        Note that the default does nothing, and it will not even be executed unless defined.
        """

    def src_unpack(self):
        """Function used to unpack mod sources"""

    def src_prepare(self):
        """Function used to apply patches and configuration"""

    def src_install(self):
        """Function used to create the final install directory"""

    def pkg_prerm(self):
        """
        Function called immediately before mod removal

        Note that the default does nothing, and it will not even be executed unless defined.
        """

    def pkg_postinst(self):
        """
        Function called immediately after mod installation

        Note that the default does nothing, and it will not even be executed unless defined.
        """

    @staticmethod
    def execute(
        command: str, pipe_output: bool = False, pipe_error: bool = False
    ) -> Optional[str]:
        """Function pybuild files can use to execute native commands"""


class FullInstalledPybuild(FullPybuild):
    """Interface describing the type of installed Pybuilds"""

    INSTALLED_USE: Set[str] = set()
    INSTALLED: bool = True
    INSTALLED_REBUILD_FILES: Optional[Any] = None


def get_installed_env(pkg: BasePybuild):
    environment = {}
    path = os.path.join(os.path.dirname(pkg.FILE), "environment.xz")

    if os.path.exists(path):
        environment_json = lzma.LZMAFile(path)
        try:
            environment = json.load(environment_json)
        except EOFError as e:
            raise RuntimeError(f"Failed to read {path}") from e
    return environment

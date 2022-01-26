# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Pybuild classes

Pybuilds are divided into two types:

1. The Pybuild class, which is used internally by portmod and includes several helper functions
2. The FullPybuild class, which is what packages inherit from and is accessible when loading

A third class, the BasePybuild, includes common code shared between Pybuild and FullPybuild
There is also an InstalledPybuild variant of the Pybuild, and a FullInstalledPybuild
variant of the FullPybuild which include information about the installed package.

Due to the Unsandboxed loader having full access to the FullPybuild, this class must
not implement any (non-private) functions which access the filesystem. Such functions
either belong in Pybuild, or Pybuild1 (the subclass of FullPybuild which is used by the
Sandboxed loader).

Note that the Pybuild/Pybuild1 split also provides a mechanism for modifying the Pybuild
format, as we can make changes to this interface, and update the implementations to
conform to it while keeping their structure the same, performing conversions
of the data inside the init function.
"""

import os
import urllib
import urllib.parse
from typing import AbstractSet, Dict, Iterable, List, Optional, Set, cast

from portmod.config import get_config
from portmod.globals import env
from portmod.parsers.manifest import Manifest
from portmod.repo import get_repo_name, get_repo_root
from portmod.source import SourceManifest
from portmodlib.atom import Atom, FQAtom, QualifiedAtom
from portmodlib.colour import green
from portmodlib.pybuild import (
    BasePybuild,
    File,
    FullInstalledPybuild,
    FullPybuild,
    InstallDir,
    get_installed_env,
)
from portmodlib.source import Source, get_archive_basename
from portmodlib.usestr import UseParserError, check_required_use, use_reduce


class Pybuild(BasePybuild):
    """Interface used internally to define helper functions on pybuilds"""

    def __init__(
        self, atom: FQAtom, cache: Optional[Dict] = None, *, FILE: str, **kwargs
    ):
        # Note: mypy doesn't like how we coerce INSTALL_DIRS
        if cache:
            self.__dict__ = cache
            self.INSTALL_DIRS = [
                InstallDir(**cast(Dict, idir)) for idir in self.INSTALL_DIRS
            ]
        for keyword, value in kwargs.items():
            setattr(self, keyword, value)
        self.ATOM = atom
        self.P = Atom(atom.P)
        self.PF = Atom(atom.PF)
        self.PN = Atom(atom.PN)
        self.CATEGORY = atom.C
        self.PV = atom.PV
        self.PR = atom.PR or "r0"
        self.PVR = atom.PVR
        self.CPN = QualifiedAtom(atom.CPN)
        self.CP = QualifiedAtom(atom.CP)
        self.__ENV = None
        self.INSTALLED = False
        self.FILE = FILE
        self.REPO_PATH = get_repo_root(self.FILE)
        if not self.REPO and self.REPO_PATH:
            self.REPO = get_repo_name(self.REPO_PATH)

    def __str__(self):
        return self.ATOM

    def __repr__(self):
        return self.__class__.__name__ + "(" + self.FILE + ")"

    def get_manifest(self):
        """Returns the manifest object for the mod's sources"""
        if os.path.exists(manifest_path(self.FILE)):
            self._manifest = get_manifest(self.FILE)

        if hasattr(self, "_manifest"):
            return self._manifest

        return get_manifest(self.FILE)

    def _get_sources(
        self,
        uselist: AbstractSet[str] = frozenset(),
        masklist: AbstractSet[str] = frozenset(),
        matchnone=False,
        matchall=False,
    ) -> List[Source]:
        """
        Returns a list of sources that are enabled using the given configuration
        """
        sourcestr = self.SRC_URI
        sources = use_reduce(
            sourcestr,
            uselist,
            masklist,
            is_valid_flag=self.valid_use,
            is_src_uri=True,
            flat=True,
            matchnone=matchnone,
            matchall=matchall,
        )
        return parse_arrow(sources)

    def get_sources(
        self,
        uselist: AbstractSet[str] = frozenset(),
        masklist: AbstractSet[str] = frozenset(),
        matchnone=False,
        matchall=False,
    ) -> List[SourceManifest]:
        """
        Returns a list of sources that are enabled using the given configuration
        """
        sources = self._get_sources(uselist, masklist, matchnone, matchall)
        manifest = self.get_manifest()

        manifested_sources: List[SourceManifest] = []

        for source in sources:
            if manifest.get(source.name) is not None:
                m = manifest.get(source.name)
                manifested_sources.append(SourceManifest(source, m.hashes, m.size))
            else:
                raise Exception(f"Source {source.name}  is missing from the manifest!")

        return manifested_sources

    def get_use(self) -> Set[str]:
        """Returns the enabled use flags for the package"""
        from .config.use import get_use

        return get_use(self)[0]

    def parse_string(self, string, matchall=False):
        from .config.use import get_use

        if not matchall:
            (enabled, disabled) = get_use(self)
        else:
            (enabled, disabled) = (set(), set())

        return use_reduce(
            self.RESTRICT,
            enabled,
            disabled,
            is_valid_flag=self.valid_use,
            flat=True,
            matchall=matchall,
        )

    def get_restrict(self, *, matchall=False):
        """Returns parsed tokens in RESTRICT using current use flags"""
        # If we don't have a prefix there is no user configuration
        if not env.PREFIX_NAME:
            matchall = True
        return self.parse_string(self.RESTRICT, matchall=matchall)

    def get_properties(self, *, matchall=False):
        """Returns parsed tokens in PROPERTIES using current use flags"""
        return self.parse_string(self.PROPERTIES, matchall=matchall)

    def get_default_source_basename(self) -> Optional[str]:
        tmp_source = next(iter(self.get_sources(self.get_use())), None)
        if tmp_source:
            return get_archive_basename(tmp_source.name)
        return None

    def _get_install_dir_dest(self):
        install_dir_dest = get_config().get("INSTALL_DEST", ".")
        for attr in dir(self):
            if not attr.startswith("_") and isinstance(getattr(self, attr), str):
                install_dir_dest = install_dir_dest.replace(
                    "{" + attr + "}", getattr(self, attr)
                )
        return os.path.normpath(install_dir_dest)

    def validate(self):
        """QA Checks pybuild structure"""
        from portmod.repo.loader import pkg_exists
        from portmod.repo.metadata import (
            check_use_expand_flag,
            get_global_use,
            get_package_metadata,
            get_use_expand,
            license_exists,
        )

        if not isinstance(self.RDEPEND, str):
            raise TypeError("RDEPEND must be a string")

        if not isinstance(self.DEPEND, str):
            raise TypeError("DEPEND must be a string")

        if not isinstance(self.SRC_URI, str):
            raise TypeError("SRC_URI must be a string")

        if not isinstance(self.DATA_OVERRIDES, str):
            raise TypeError("DATA_OVERRIDES must be a string")

        if not isinstance(self.LICENSE, str):
            raise TypeError(
                "LICENSE must be a string containing a space separated list of licenses"
            )

        if not isinstance(self.RESTRICT, str):
            raise TypeError(
                "RESTRICT must be a string containing a space separated list"
            )

        if not isinstance(self.PROPERTIES, str):
            raise TypeError(
                "PROPERTIES must be a string containing a space separated list"
            )

        iuse_strip = {use.lstrip("+") for use in self.IUSE}
        errors = []

        if not self.REPO_PATH:
            raise RuntimeError(
                "Pybuild.validate called on a pybuild which doesn't have a repository!"
            )

        def check_use_reduce(attr: str, *, is_src_uri: bool = False, token_class=str):
            try:
                return use_reduce(
                    getattr(self, attr),
                    token_class=token_class,
                    matchall=True,
                    flat=True,
                    is_valid_flag=self.valid_use,
                    is_src_uri=is_src_uri,
                )
            except UseParserError as error:
                errors.append(f"Failed to parse {attr}: {error}")
            return []

        rdeps = check_use_reduce("RDEPEND", token_class=Atom)
        deps = check_use_reduce("DEPEND", token_class=Atom)
        overrides = check_use_reduce("DATA_OVERRIDES", token_class=Atom)
        check_use_reduce("HOMEPAGE")
        check_use_reduce("SRC_URI", is_src_uri=True)
        check_use_reduce("PATCHES")
        licenses = check_use_reduce("LICENSE")

        for license in licenses:
            if license != "||" and not license_exists(self.REPO_PATH, license):
                errors.append(
                    f"LICENSE {license} does not exist! Please make sure that it named "
                    "correctly, or if it is a new License that it is added to "
                    "the licenses directory of the repository"
                )

        for atom in rdeps + deps:
            if isinstance(atom, Atom) and not pkg_exists(atom, repo_name=self.REPO):
                errors.append(f"Dependency {atom} could not be found!")

        for atom in overrides:
            if isinstance(atom, Atom) and not pkg_exists(atom, repo_name=self.REPO):
                errors.append(f"Data Override {atom} could not be found!")

        for install in self.INSTALL_DIRS:
            if not isinstance(install, InstallDir):
                errors.append(f'InstallDir "{install}" must have type InstallDir')
                continue
            for file in install.get_files():
                if not isinstance(file, File):
                    errors.append(f'File "{file}" must have type File')
                    continue

                try:
                    check_required_use(file.REQUIRED_USE, set(), self.valid_use)
                except UseParserError as error:
                    errors.append(f"Error processing file {file.NAME}: {error}")

            try:
                check_required_use(install.REQUIRED_USE, set(), self.valid_use)
            except UseParserError as error:
                errors.append(f"Error processing dir {install.PATH}: {error}")

            if install.WHITELIST is not None and not isinstance(
                install.WHITELIST, list
            ):
                errors.append(f"WHITELIST {install.WHITELIST} must be a list")
            elif install.WHITELIST is not None:
                for string in install.WHITELIST:
                    if not isinstance(string, str):
                        errors.append(
                            f'"{string}" in InstallDir WHITELIST is not a string'
                        )

            if install.BLACKLIST is not None and not isinstance(
                install.BLACKLIST, list
            ):
                errors.append(f"BLACKLIST {install.BLACKLIST} must be a list")
            elif install.BLACKLIST is not None:
                for string in install.BLACKLIST:
                    if not isinstance(string, str):
                        errors.append(
                            f'"{string}" in InstallDir BLACKLIST is not a string'
                        )

            if install.WHITELIST is not None and install.BLACKLIST is not None:
                errors.append("WHITELIST and BLACKLIST are mutually exclusive")

        global_use = get_global_use(self.REPO_PATH)
        metadata = get_package_metadata(self)

        for use in iuse_strip:
            if global_use.get(use) is None and (
                metadata is None
                or metadata.use is None
                or metadata.use.get(use) is None
            ):
                valid = False
                # If the flag contains an underscore, it may be a USE_EXPAND flag
                if "_" in use:
                    for use_expand in get_use_expand(self.REPO_PATH):
                        length = len(use_expand) + 1  # Add one for underscore
                        if use.startswith(use_expand.lower()) and check_use_expand_flag(
                            self.REPO_PATH, use_expand, use[length:]
                        ):
                            valid = True
                            break

                if not valid:
                    errors.append(
                        f'Use flag "{use}" must be either a global use flag '
                        "or declared in metadata.yaml"
                    )

        for value in self.get_restrict(matchall=True):
            if value not in {"fetch", "mirror"}:
                errors.append(f"Unsupported restrict flag {value}")

        if not self.NAME or "FILLME" in self.NAME or len(self.NAME) == 0:
            errors.append("Please fill in the NAME field")
        if not self.DESC or "FILLME" in self.DESC or len(self.DESC) == 0:
            errors.append("Please fill in the DESC field")
        if not isinstance(self.HOMEPAGE, str) or "FILLME" in self.HOMEPAGE:
            errors.append("Please fill in the HOMEPAGE field")

        all_sources = self._get_sources(matchall=True)

        for install in self.INSTALL_DIRS:
            if isinstance(install, InstallDir):
                if len(all_sources) > 0 and install.S is None:
                    if len(all_sources) != 1:
                        errors.append(
                            "InstallDir does not declare a source name but source "
                            "cannot be set automatically"
                        )
            else:
                errors.append(f"InstallDir {install} should be of type InstallDir")

        manifest = self.get_manifest()
        for source in self._get_sources(matchall=True):
            if manifest.get(source.name) is None:
                errors.append(f'Source "{source.name}" is not listed in the Manifest')

        if len(errors) > 0:
            raise Exception(
                "Pybuild {} contains the following errors:\n{}".format(
                    green(self.FILE), "\n".join(errors)
                )
            )


class InstalledPybuild(Pybuild):
    """Interface describing the type of installed Pybuilds"""

    INSTALLED_USE: Set[str] = set()
    INSTALLED_REBUILD_FILES: Optional[Manifest] = None

    def __init__(
        self, atom: FQAtom, cache: Optional[Dict] = None, *, FILE: str, **kwargs
    ):
        super().__init__(atom, cache=cache, FILE=FILE, **kwargs)
        self.INSTALLED_USE = set(self.INSTALLED_USE)
        self.INSTALLED = True
        if self.INSTALLED_REBUILD_FILES:
            self.INSTALLED_REBUILD_FILES = Manifest.from_json(
                self.INSTALLED_REBUILD_FILES
            )
        self._installed_env: Optional[Dict] = None
        self._contents: Optional[Manifest] = None

    def get_use(self):
        return self.INSTALLED_USE

    def get_installed_env(self):
        """Returns a dictionary containing installed object values"""
        if self._installed_env is None:
            self._installed_env = get_installed_env(self)

        return self._installed_env

    def get_contents(self) -> Manifest:
        """Returns a manifest listing the files installed by the package"""
        if self._contents is None:
            path = os.path.join(os.path.dirname(self.FILE), "CONTENTS")
            self._contents = Manifest(path)

        return self._contents


def parse_arrow(sourcelist: Iterable[str]) -> List[Source]:
    """
    Turns a list of urls using arrow notation into a list of
    Source objects
    """
    result: List[Source] = []
    arrow = False
    for value in sourcelist:
        if arrow:
            result[-1] = Source(result[-1].url, value)
            arrow = False
        elif value == "->":
            arrow = True
        else:
            url = urllib.parse.urlparse(value)
            result.append(Source(value, os.path.basename(url.path)))
    return result


def manifest_path(file):
    return os.path.join(os.path.dirname(file), "Manifest")


# Loads the manifest for the given file, i.e. the Manifest file in the same directory
#    and turns it into a map of filenames to (shasum, size) pairs
def get_manifest(file):
    m_path = manifest_path(file)

    return Manifest(m_path)


def to_cache(pkg: FullPybuild) -> Dict:
    cache = {}
    for key in [
        "RDEPEND",
        "DEPEND",
        "SRC_URI",
        "REQUIRED_USE",
        "RESTRICT",
        "PROPERTIES",
        "IUSE_EFFECTIVE",
        "IUSE",
        "TEXTURE_SIZES",
        "DESC",
        "NAME",
        "HOMEPAGE",
        "LICENSE",
        "KEYWORDS",
        "REBUILD_FILES",
        "TIER",
        "FILE",
        "REPO",
        "DATA_OVERRIDES",
        "S",
        "PATCHES",
    ]:
        cache[key] = getattr(pkg, key)

    cache["INSTALL_DIRS"] = [idir._to_cache() for idir in pkg.INSTALL_DIRS]
    phase_functions = [
        "src_unpack",
        "src_install",
        "src_prepare",
        "pkg_nofetch",
        "pkg_pretend",
        "pkg_postinst",
        "pkg_prerm",
    ]
    cache["FUNCTIONS"] = [
        func
        for func in phase_functions
        if hasattr(pkg.__class__, func)
        and getattr(pkg.__class__, func) != getattr(FullPybuild, func)
    ]

    if pkg.INSTALLED:
        pkg = cast(FullInstalledPybuild, pkg)
        cache["INSTALLED_USE"] = pkg.INSTALLED_USE
        cache["INSTALLED_REBUILD_FILES"] = None
        if pkg.INSTALLED_REBUILD_FILES:
            cache["INSTALLED_REBUILD_FILES"] = pkg.INSTALLED_REBUILD_FILES.to_json()
    return cache

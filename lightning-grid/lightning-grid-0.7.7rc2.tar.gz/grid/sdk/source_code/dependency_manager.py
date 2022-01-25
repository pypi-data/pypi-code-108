from __future__ import annotations

import abc
from enum import Enum
import functools
import itertools
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Collection, Dict, List, Optional, Union
from urllib.parse import urlparse
import warnings

from packaging.specifiers import SpecifierSet
from pipreqs import pipreqs
import pkg_resources
from pkg_resources import Requirement
import yaml

from grid.sdk import env
from grid.sdk.source_code.git import execute_git_command

PIP_MANAGER = 'PIP'
CONDA_MANAGER = 'CONDA'


def find_package_manager(file):
    """
    Find the package manager for the provided dependency file depends on basic heuristics.
    We currently assume a minimal conda environment file would have `dependencies` as the
    key that lists all the dependencies, as described here
    https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#create-env-file-manually
    """
    if not file:
        raise RuntimeError("Invalid call to find the package manager")
    f = Path(file).open()
    try:
        content = yaml.safe_load(f)
    except Exception:
        # Assuming PIP if yaml load fails
        return PIP_MANAGER
    else:
        if isinstance(content, dict):
            # valid conda env file should have `dependencies` keys
            if 'dependencies' in content:
                return CONDA_MANAGER
    return PIP_MANAGER


PIP_REQUIREMENTS_FILE = "requirements.txt"
CONDA_REQUIREMENTS_FILE = "environment.yml"


def get_manager(repo_root) -> DependencyManagerBase:
    files = os.listdir(repo_root)
    conda_env = os.getenv("CONDA_DEFAULT_ENV")
    if CONDA_REQUIREMENTS_FILE in files:
        if PIP_REQUIREMENTS_FILE in files:  # skipcq: PYL-R1705
            warnings.warn(
                f"Found both {CONDA_REQUIREMENTS_FILE} and {PIP_REQUIREMENTS_FILE}. "
                f"Defaulting to use {PIP_REQUIREMENTS_FILE}."
            )
            manager_class = PipManager
        else:
            manager_class = CondaManager
    elif PIP_REQUIREMENTS_FILE in files:
        manager_class = PipManager
    elif conda_env:
        manager_class = CondaManager
    else:
        manager_class = PipManager
    return manager_class()


def guess_manager_from_dependency_file(dependency_file) -> DependencyManagerBase:
    """
    If user provides the dependency file instead of letting us find it from the root,
    use this function to create the Manager. If dependency_file is not provided,
    use `_get_manager`
    """
    package_manager = find_package_manager(dependency_file)
    if package_manager == PIP_MANAGER:
        return PipManager(dependency_file=dependency_file)
    if package_manager == CONDA_MANAGER:
        return CondaManager(dependency_file=dependency_file)

    raise RuntimeError("Unknown package manager")


# def serialize_dependencies(config_path: Optional[str] = None, dependency_file: Optional[str] = None) -> Optional[Path]:
#     """
#     Serialize dependency information to the corresponding source.
#
#     Write python dependencies to the corresponding dependency listing
#     (requirements.txt or environment.yml) and system dependencies to
#     grid config (config.yml). Both write operations are actually offloaded
#     downstream to the dependency manager object. Also fetches warnings
#     from the dependency manager and echo to the user's terminal
#
#     config:
#         Grid config either read from the file provided by the user or the
#         default generated one
#
#     Returns
#     -------
#     Path to the requirement file
#     """
#     check_status = check_dependency_listing(do_diff_check=False, ignore_warnings=False)
#     if not check_status:
#         print("Dependency check failed. Cannot sync environment")
#         return None
#
#     repo_root = execute_git_command(['rev-parse', '--show-toplevel'])
#     try:
#         if dependency_file:
#             deps_manager = guess_manager_from_dependency_file(dependency_file)
#         else:
#             deps_manager = get_manager(repo_root)
#     except Exception as e:  # noqa
#         # it's already being checked by `check_dependency_listing`
#         raise RuntimeError("Exception while initializing dependency manager")
#
#     deps_manager.write_spec()
#     deps_manager.write_config(config_path)
#     return deps_manager.req_file


def check_dependency_listing(
    repo_root: Path,
    do_diff_check=True,
    ignore_warnings=env.IGNORE_WARNINGS,
    dependency_file=None,
):
    """
    Evaluate if dependency listing is correct or not

    Determines the package manager employed by the user to specify
    application dependencies, setting up the appropriate interaction
    classes used to query one of the various package managers available
    as the system resolves dependency versions. Should no requirement file
    exist which specifies needed libraries+versions, this method provides
    the logic through which users are asked to select how they would like
    to proceed - automatic heuristic based generation or manual.

    Parameters
    ----------
    do_diff_check: bool
        Check for the diff between requirements file and the environment. This
        is True by default but `serialize_dependencies` checks this explicitly
        as part of serializing the dependencies and hence will set as False
    ignore_warnings: bool
        Should warnings be ignored. Should be removed when we move
        click component out of SDK -> TODO
    repo_root
        Root of the repository. Defaults to git root

    Returns
    -------
    Return False if check fails. True otherwise
    """
    repo_root = Path(execute_git_command(['rev-parse', '--show-toplevel'])).absolute()
    if ignore_warnings:
        return True

    # Assuming the requirements file is always at the repo root if not passed
    # through dependency_file argument
    files = os.listdir(repo_root)

    try:
        if dependency_file:
            deps_manager = guess_manager_from_dependency_file(dependency_file)
        else:
            deps_manager = get_manager(repo_root)
    except Exception as e:  # noqa
        # ==============================================
        # Case 1: Initializing dependency manager failed
        # ==============================================
        # Ignoring to avoid internal errors to go to users
        if PIP_REQUIREMENTS_FILE not in files and CONDA_REQUIREMENTS_FILE not in files:
            message = "No requirements.txt or environment.yml found. Your build could crash or not start."
            warnings.warn(message)
        return False

    # =====================================
    # Case 2: Requirements file not present
    # =====================================
    if PIP_REQUIREMENTS_FILE not in files and CONDA_REQUIREMENTS_FILE not in files:
        deps_found = "\n        ".join(deps_manager.source_deps)
        message = (
            "No requirements.txt or environment.yml found but we identified below "
            "dependencies from your source. Your build could crash or not start. "
            f"\n {deps_found} \n"
        )
        warnings.warn(message)
        return False

    # ===========================================================
    # Case 3: Packages found imported for which spec is not found
    # ===========================================================
    missing = "\n        ".join(deps_manager.get_missing())
    if missing:
        message = (
            "Your requirements.txt or environment.yml are missing the following packages:"
            f"\n {missing} \n"
            f"Your experiment could crash if these are missing! Add them yourself or try `grid sync-env`"
        )
        warnings.warn(message)
        return False

    # ==============================================
    # Case 4: Incomplete/different-spec requirements
    # ==============================================
    if do_diff_check and deps_manager.has_change:
        message = (
            "Incomplete requirements.txt or environment.yml found. "
            "Your build could crash or not start. Run `grid sync-env` "
            "to auto-populate the changed packages"
        )
        warnings.warn(message)
        return False

    # Returning True if all looks good
    return True


# https://www.python.org/dev/peps/pep-0610/
PACKAGE_URL_METAFILE = "direct_url.json"
ALLOWED_SCHEMES = {'http', 'https', 'file', 'ftp', 'ssh', 'git', 'sftp', 'git+http', 'git+https'}


class NonComparableError(Exception):
    """
    Two Packages are non-comparable
    """


def execute_conda_command(args: List[str]):
    process = subprocess.run(["conda"] + args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True,
                             check=False)
    output = process.stdout.strip() + process.stderr.strip()
    return output


def get_url_scheme(url: str) -> str:
    """Parse the URL and get the scheme"""
    return urlparse(url).scheme


def is_valid_url(url: str) -> bool:
    """Check the validity of the URL. Currently it's only based
    on the scheme. Whether the scheme is in allowed schemes or not
    """
    return get_url_scheme(url) in ALLOWED_SCHEMES


class RuleLabels(Enum):
    PIP_NAME_MAPPING = "pip_name_mapping"
    CONDA_NAME_MAPPING = "conda_name_mapping"
    SYSTEM = "system"


@functools.lru_cache(maxsize=None)
def _get_rule_maps() -> Dict[str, Dict[str, str]]:
    """
    Parsing the rule files for mapping python package names, conda names
    and finding out the system dependencies. The whole rule set is built by
    keeping the parsed pypi name as reference. The parsed pypi name is the
    name of a package as listed in pypi but replaced all the hyphens with
    underscores. Below given are few examples of parsed pypi name

            Import name : sklearn
            Parsed pypi : scikit_learn
            pypi name   : scikit-learn

    For more details, refer the documentation in the YAML rule file
    """
    rule_file = Path(__file__).parent / "dependency_rules/dependency_rules.yml"
    mappings = yaml.safe_load(rule_file.open())
    mandatory_keys = {val.value for val in RuleLabels}
    # Both must have exactly the same elements
    if mandatory_keys.symmetric_difference(mappings.keys()):
        raise RuntimeError("Rule file is corrupted")
    out = {}
    for k in mandatory_keys:
        out[k] = dict(mapping.strip().split(":") for mapping in mappings[k])

    # nested parsing of system dependencies
    for name, value in out[RuleLabels.SYSTEM.value].items():
        out[RuleLabels.SYSTEM.value][name] = value.split(",")

    return out


def _get_system_deps(name: str) -> List[str]:
    """
    Get the list of system dependencies required for a python package. For
    example graphviz is required to have graphviz and xdg-utils installed
    in the system apart from the python package itself.

    Parameters
    ----------
    name:
        Parsed pypi name

    Returns
    -------
    List of system dependencies required for a python package to be working
    """
    system_rules = _get_rule_maps()[RuleLabels.SYSTEM.value]
    return system_rules.get(name, [])


def _conda2parsed_pypi(name: str) -> str:
    """
    Parsed pypi names are being used as the standard for making comparisons
    in this module. For instance, conda list the package pytorch as
    "pytorch" while pip list it as "torch". This function converts conda name
    ("pytorch" to parsed pypi name ("torch") using the predefined mapping rule
    """
    conda_rules = _get_rule_maps()[RuleLabels.CONDA_NAME_MAPPING.value]
    return conda_rules.get(name, name).replace("-", "_")


def _source2parsed_pypi(name: str) -> str:
    """
    Parsed pypi names are being used as the standard for making comparisons
    in this module. This function converts the `import` name to the parsed
    pypi name. While both names are same for almost all the cases, there are
    few that isn't. For example sklearn is the import name while scikit-learn
    is the pypi name (and scikit_learn is the parsed pypi name - note the
    underscore). Note that for python's dependency manager, both "-" and "_"
    has same meaning. scikit-learn = scikit_learn
    """
    pypi_rules = _get_rule_maps()[RuleLabels.PIP_NAME_MAPPING.value]
    return pypi_rules.get(name, name).replace("-", "_")


def _get_distribution_url(dist: pkg_resources.Distribution) -> Optional[str]:
    """
    Fetch the distribution URL from package distribution based on pep440
    and pep610. Different details about how this feature eventually landed
    in `pip` and different considerations can be found at the issue page -
    https://github.com/pypa/pip/issues/609.
    """
    try:
        url_meta = json.loads(dist.get_metadata(PACKAGE_URL_METAFILE))
    except (FileNotFoundError, ValueError, UnicodeDecodeError, KeyError):
        return None
    url = url_meta.get("url")
    if not url:
        return None
    if "vcs_info" in url_meta:
        commit_id = url_meta["vcs_info"].get("commit_id")
        vcs = url_meta["vcs_info"].get("vcs")
        return f"{vcs}+{url}@{commit_id}"
    return url


def _is_dist_editable(dist: pkg_resources.Distribution) -> bool:
    """
    Check if a Distribution is installed as editable
    """
    for path_item in sys.path:
        egg_link = Path(path_item) / dist.project_name / '.egg-link'
        if egg_link.is_file():
            return True
    return False


def _get_url_n_rev(string):
    """ If the url is in the format `url@head

    Example: https://github.com/org/repo@branch
    """
    if "@" in string:
        return string.rsplit("@", maxsplit=1)
    return string, None


def _get_valid_stem(string: str) -> Optional[str]:
    """
    Validate and get the stem from the given path / URL

    It verifies whether the given path is valid or not and if valid
    fetches the stem from the path and consider that as the name. This
    doesn't work in all the cases (eg. hangar-py) but it is probably the
    most reasonable assumption that would work in almost all the cases
    """
    string = string.strip()
    scheme = get_url_scheme(string).lower()
    if scheme == "file":
        raise RuntimeError(f"Local paths are not portable '{string}'")

    # Windows paths either get parsed as scheme = drive letter (e.g. "C") for absolute paths or as scheme = string for
    # relative paths. We explicitly filter these cases before checking for a match to ALLOWED_SCHEMES.
    if scheme and len(scheme) > 1 and scheme != string and scheme not in ALLOWED_SCHEMES:
        raise RuntimeError(f"Valid URL schemes are {ALLOWED_SCHEMES}")

    if is_valid_url(string):
        url, _ = _get_url_n_rev(string)
        parsed = urlparse(url)
        if parsed.path:
            path = Path(parsed.path)
        else:
            raise RuntimeError(f"Invalid URL '{string}'")

    else:
        path = Path(string)
        if path.is_absolute():
            raise RuntimeError(f"Absolute paths might not resolve '{path}'")
        if path.exists():
            cwd = Path.cwd()
            # Use os.path.abspath as an alternative to path.resolve() which doesn't work on Windows.
            absolute = Path(os.path.abspath(path))
            if cwd not in absolute.parents and cwd != absolute:
                raise RuntimeError(f"Paths outside of the current working directory are not portable: {path}")
        else:
            raise RuntimeError(f"Error while parsing {string}")
    return path.resolve().stem.split(".")[0]


def _guess_valid_name(string):
    """
    Heuristics to fallback when `Requirement.parse` fails. This function tries
    to find a valid name from the given string and return. This name is
    then used to make comparison from the names from other sources.

    Evidently, pip's parsing logic is exhaustive and we wouldn't want to copy
    the whole pip parser to our source code. The heuristics this function
    supports are a given below. Every other string would lead to a
    warning or an exception. More details on parsing logic, checkout pip's
    source code or the grammar + parser specified in pip508

        location: /src/pip/_internal/req/constructors.py#L291
        commit: a089883a8

        - Current directory
        - Wheel files or sub directories in current directory
        - Valid URLs (git, remote wheel file, remote zip file etc)
        - Valid Requirement spec with options (pkg==0.1 -i <url>)
    """
    string = string.strip()
    if string.startswith("-e "):
        raise RuntimeError("Found editable requirements which might not be" f"portable {string}")
    if "@ " in string:
        # name@ path is not a valid specification in 3.7
        name, _ = string.split("@ ", maxsplit=1)
        if not name:
            raise RuntimeError(f"Error while parsing '{string}'")
        return name.strip()
    marker_sep = '; ' if is_valid_url(string) else ";"
    substr = string.split(marker_sep, 1)[0]
    # If options are present in the string (pkg=0.1 -i <url>)
    splits = re.split(r" -[\w\-]+ ", substr)
    if len(splits) > 1:
        try:
            req = Requirement.parse(splits[0])
        except Exception:  # noqa
            raise RuntimeError(f"Error while parsing {string}")
        name = req.project_name
    else:
        name = _get_valid_stem(substr)
    return name


class BasePackage(abc.ABC):
    """Base Package class for holding the PIP and Conda Spec.

    Custom Package classes must be inherited from this class to include
    custom logic for equality check and parsing

    Note: Parameter `name` comes from the name of the package defined
    by the developer of the package. But in cases where we cannot infer
    that name, we fallback to other methods. For example, in the case
    of a URL, the name is the `stem` of the `path` in the URL. If the
    name is identified by none of the methods, we generate a uuid instead
    """
    def __init__(self, name: str):
        self.name = name
        self.parsed_name = self.name.replace("-", "_")

    @abc.abstractmethod
    def from_string(self, string):
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other: BasePackage) -> bool:
        return NotImplemented

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError


class CondaPackage(BasePackage):
    """
    Do not call the constructor / init directly. Use classmethod(s) instead
    """
    def __init__(self, name: Optional[str], version: Optional[str], build: Optional[str]):
        super().__init__(name)
        self.parsed_name = _conda2parsed_pypi(self.name)
        self.version = version
        self.build = build

    @classmethod
    def from_string(cls, string: str) -> CondaPackage:
        splits = re.split(r"\W*=\W*", string)
        if len(splits) > 3:
            raise RuntimeError(f"ParsingError: Conda spec {string} is " f"not readable")
        expected_elem_count = 3  # name, version and build
        splits = splits + [None] * (expected_elem_count - len(splits))  # noqa
        name, version, build = splits
        return cls(name=name, version=version, build=build)

    def __str__(self):
        not_none = [val for val in (self.name, self.version, self.build) if val]
        return "=".join(not_none)

    def __eq__(self, other: CondaPackage):
        if other.__class__ is self.__class__:
            return all((self.version == other.version, self.parsed_name == other.parsed_name))
        return NotImplemented


class PipPackage(BasePackage):
    """
    Offload all parsing, de-parsing, checks etc to `Requirement` object.
    Do not call the constructor / init directly. Use classmethod(s) instead
    """
    def __init__(self, name: str, req_obj: Optional[Requirement] = None, original_string: Optional[str] = None):
        super().__init__(name)
        self._requirement_obj = req_obj
        self._original_string = original_string

    @classmethod
    def from_string(cls, string) -> PipPackage:
        string = string.strip()
        try:
            req = Requirement.parse(string)
        except Exception:  # noqa
            # generic exception since different python versions have
            # inconsistencies in raising exceptions
            obj = None
        else:
            obj = cls.from_requirement(req)

        if obj is None:
            name = _guess_valid_name(string)
            if name is None:
                raise RuntimeError(f"Guessing name for '{string}' failed")
            obj = cls(name=name, original_string=string)
        return obj

    @classmethod
    def from_requirement(cls, req: pkg_resources.Requirement):
        self = cls(req.project_name, req_obj=req)
        return self

    @classmethod
    def from_distribution(cls, dist: pkg_resources.Distribution):
        if _is_dist_editable(dist):
            raise RuntimeError(f"Found editable installation which might have" f"local changes {dist.project_name}")
        req = dist.as_requirement()
        url = _get_distribution_url(dist)
        # if the URL is available, we'll remove the specifier (version info)
        # from the Requirement object since req has a bug when str(req) is
        # invoked for a req object with both version and URL. Nevertheless,
        # we wouldn't need the version info if url is present
        if url:
            req.url = url
            req.specifier = SpecifierSet("")
        # TODO: identify hashCmp, marker when possible
        return cls.from_requirement(req)

    def _version_check(self, other: PipPackage):
        """
        Checking the versions of two instances with special constraints.

        This fine grained check is triggered only in the case basic
        equality check (==) fails. It is for making sure version inclusion
        checks will pass. Specifically, version for package info fetched from
        environment would always has `==` as the version specifier since
        exact version is known. But version specifier for packages from
        requirements.txt could be any (`>` or `>=` or ...)

        Constraints:
            1. Number of specifier to the `self` must be 1. This is to
                make sure next constraint is valid
            2. The only specifier exist on `self` is `==`. This is to
                make sure the `self` knows exact version
            3. The version of `self` is included in the version of `other`
                Eg: `"pkg==1.2.0" == pkg>1.0.0,<=2.0.0

        Note: This check is based on the strong assumption that `other` is
        also a `PipPackage` but not a `CondaPackage`
        """
        self_has_version = bool(len(self._requirement_obj.specifier))
        other_has_version = bool(len(other._requirement_obj.specifier))
        if not self_has_version or not other_has_version:
            return NotImplemented
        if not bool(len(self._requirement_obj.specifier)):
            return NotImplemented
        if len(self._requirement_obj.specifier) > 1:
            # expecting other.__eq__ to solve the equality check
            return NotImplemented
        specifier = tuple(self._requirement_obj.specifier)[0]
        if specifier.operator != "==":
            # expecting other.__eq__ to solve the equality check
            return NotImplemented
        # checking at-least one specifier on the other side has
        # non-empty version
        for sp in other._requirement_obj.specifier:
            if sp.version:
                break
        else:
            return False
        # TODO: check for prereleases
        return specifier.version in other._requirement_obj.specifier

    def __str__(self):
        if self._requirement_obj:
            return str(self._requirement_obj)
        if self._original_string:
            return self._original_string
        raise RuntimeError("Found corrupted package")

    def __eq__(self, other: PipPackage):
        if self.__class__ != other.__class__:
            return NotImplemented

        if self.parsed_name != other.parsed_name:
            raise NonComparableError
        if self._requirement_obj is None or other._requirement_obj is None:
            # Comparison without the Requirement object needs to be
            # well thought out
            raise NonComparableError

        # Checking the equality on requirement object
        if self._requirement_obj == other._requirement_obj:
            return True
        # Checking the string representation since there are cases
        # Requirement's __eq__ check is not working as expected
        # pytorch-lightning-bolts installed from github is an example
        if str(self._requirement_obj) == str(other._requirement_obj):
            return True
        # Version inclusion check
        return self._version_check(other)


class DependencyManagerBase(abc.ABC):
    """Dependency manager base class.

    The dependency managers such as pip or conda or any future managers
    such as poetry should subclassed from this base class. The Abstract
    methods are specific to each package manager and should be implemented
    by the child class. These methods are being called in the setup time
    to build the information base by parsing the dependency listing and
    analyzing the environment file. It's also being utilized to write
    the dependency listing back to the package manager specific file
    """
    def __init__(self, dependency_file: Optional[str] = None):
        self._setup(dependency_file=dependency_file)

    @abc.abstractmethod
    def write_spec(self):
        """Write the dependency spec after formatting based on the dependency manager.
        """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def _get_default_req_file() -> Path:
        """Get the Path object for the requirement file for each dependency manager.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _read_file_deps(self) -> Dict[str, BasePackage]:
        """Implement reading the requirement listing for each package manager.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _fetch_env_deps(self) -> Dict[str, BasePackage]:
        """Implement reading dependencies from current environment.
        """
        raise NotImplementedError

    @property
    def source_deps(self):
        if not hasattr(self, "_source_deps_list"):
            raise RuntimeError("Manager is not ready. Run `_setup()`")
        if not isinstance(self._source_deps_list, list):
            raise RuntimeError("Source list is not a valid python list")
        return self._source_deps_list

    def _setup(self, dependency_file: Optional[str] = None):
        self._source_deps_list: List[str] = self._scan_source_deps()

        # Reading package manager specific methods to build information base
        if dependency_file:
            self.req_file = Path(dependency_file)
        else:
            self.req_file: Path = self._get_default_req_file()
        self.file_deps: Dict[str, BasePackage] = self._read_file_deps()
        self.env_deps: Dict[str, BasePackage] = {}
        for k, v in self._fetch_env_deps().items():
            if k in self._source_deps_list:
                self.env_deps[k] = v

    @property
    def has_change(self):
        """
        Return True if any change is needed. False other wise.
        """
        if not self.req_file.exists():
            return True
        if set(self._source_deps_list) - set(self.file_deps):
            return True
        for key in set(self._source_deps_list).intersection(self.env_deps):
            # TODO this equality check might have issues
            #  But the only way to make it work is to deploy in the wild
            #  and take feedback
            try:
                if self.env_deps[key] != self.file_deps[key]:
                    return True
            except NonComparableError:
                continue

    @staticmethod
    def _scan_source_deps() -> List[str]:
        # TODO: This could take a lot of time if files are a lot (1000s)
        """Scan source code in the CWD (recursively) and finds the
        package dependencies

        This information will then be used as the reference while fetching
        information from different sources such as current environment,
        requirement listing, pypi etc
        """
        ignore_dirs = ["venv", "test", "tests", "_test", "_tests", "egg", "EGG", "info", "docs", "__pycache__"]
        input_path = Path.cwd()
        for pth in input_path.iterdir():
            # ignore directories beginning with ('.' and '__')
            if pth.is_dir() and (pth.name.startswith('.') or pth.name.startswith('__')):
                ignore_dirs.append(pth.name)

        # TODO: remove pipreqs dependency
        # other considerations: pydeps & pigar
        candidates = pipreqs.get_all_imports(
            input_path, encoding=None, extra_ignore_dirs=ignore_dirs, follow_links=True
        )
        return [_source2parsed_pypi(c) for c in candidates]

    def get_missing(self) -> Collection[str]:
        """
        Get packages with proper information is missing. Any package which
        is found installed in environment and found specified in the
        requirement listing file (even if no version is specified), will
        be considered as "not missing". Other packages present in the source
        code will be returned as "missing"
        """
        available = set(self.env_deps) | set(self.file_deps)
        return set(self._source_deps_list) - available

    def collate_final(self):
        """
        Collate the final list of requirements for writing back to the
        disk.

        It loops through all the existing requirements in the requirement
        listing file and make sure the the spec (eg: version) hasn't been
        changed by comparing with the spec of installed package. It then
        loops through the packages those are missing in the requirement
        listing and add the spec by fetching it from the environment
        """
        if self.get_missing():
            raise ValueError("Found requirements without spec identified")
        collated = []
        # don't union on env_deps since it could have non-necessary packages.
        # That might be true for file_deps as well but that's something user
        # gave us explicitly and hence ignoring. Also, valid_names must keep
        # the order of values in requirements file

        missing = set(self._source_deps_list) - set(self.file_deps)
        for name in itertools.chain(self.file_deps.keys(), sorted(missing)):
            if name in self.env_deps and name in self.file_deps:
                try:
                    is_same = self.env_deps[name] == self.file_deps[name]
                    # Preferring file deps in case both are equal to avoid
                    # losing other information such as markers
                    if is_same:
                        qualified = self.file_deps[name]
                    else:
                        qualified = self.env_deps[name]
                except NonComparableError:
                    # Assuming both are same if not comparable
                    qualified = self.file_deps[name]
            elif name in self.file_deps:
                qualified = self.file_deps[name]
            elif name in self.env_deps:
                qualified = self.env_deps[name]
            else:
                raise RuntimeError(f"Package name '{name}' not found in file " f"or env")
            collated.append(qualified)
        return collated

    def write_config(self, config_path: Optional[str] = None):
        names = set()
        for n in self._source_deps_list:
            names |= set(_get_system_deps(n))
        if names:
            config_path = Path(config_path or "config.yml")
            if config_path.exists():
                from grid.cli.cli.utilities import read_config
                config = read_config(value=config_path.open('r'))
            else:
                config = {"compute": {}}
                config_path.touch()
            # Sorting to make the order deterministic
            sys_deps_action = f"apt install -y {' '.join(sorted(names))}"
            if "actions" not in config["compute"]:
                config["compute"]["actions"] = {"on_image_build": []}
            elif "on_image_build" not in config["compute"]["actions"]:
                config["compute"]["actions"]["on_image_build"] = []

            if not isinstance(config["compute"]["actions"]["on_image_build"], list):
                raise RuntimeError("Parsing error while reading config.yml")

            config["compute"]["actions"]["on_image_build"].append(sys_deps_action)
            yaml.safe_dump(config, config_path.open(mode="w+"))


class CondaManager(DependencyManagerBase):
    _env_name: Optional[str] = None
    _prefix: Optional[str] = None
    _channels: List[str] = []

    @staticmethod
    def _build_dependency_dict(specs: List) -> Dict[str, Union[CondaPackage, PipPackage]]:
        """
        Build dependency objects from the spec

        Parameters
        ----------
        specs:
            Dependency specs read from the environment.yml file. It would
            contain the all the dependencies formatted as "name=version=build".
            It would also contain PIP dependencies as a dictionary with
            key as "pip". An example `specs` is given below

            specs = ["numpy-base=1.19.2=py38hcfb5961_0",
                     "ninja=1.10.2=py38hf7b0b51_0",
                     ...
                     {"pip": ["absl-py==0.11.0"
                              "attrs==20.2.0",
                              ...
                             ]
                     }
                     ]

            We are not expecting it to contain a dictionary with key other than
            "pip" and hence we throw if that's the case

        Returns
        -------
        A dictionary that maps the parsed pypi name of each dependency to the
        Package object. Since conda dependency listing has both conda and
        pip spec, the return value would contain both CondaPackage and
        PipPackage containers
        """
        dependencies = {}
        pip_dependencies = []
        for d in specs:
            # Only pip listing inside a yaml file must be a mapping
            if isinstance(d, dict):
                if "pip" not in d or len(d) > 1:
                    raise RuntimeError("Could not parse the conda yaml file. " "Raise the issue with Grid support")
                pip_dependencies = d["pip"]
            # conda deps listing in a yaml file will be a string
            else:
                try:
                    dep = CondaPackage.from_string(d)
                except RuntimeError:
                    raise RuntimeError("Could not parse the conda yaml file. " "Raise the issue with Grid support")
                dependencies[dep.parsed_name] = dep
        for elem in pip_dependencies:
            dep = PipPackage.from_string(elem)
            dependencies[dep.parsed_name] = dep
        return dependencies

    def _read_file_deps(self) -> Dict[str, CondaPackage]:
        """
        Read environment.yml to fetch user defined dependencies
        """
        if self.req_file.exists():
            specs = yaml.safe_load(self.req_file.read_text())
            if not isinstance(specs, dict):
                raise RuntimeError(f"Parsing error with {self.req_file}")
            self._env_name = specs.get("name")
            self._prefix = specs.get("prefix")
            self._channels = self._channels + specs["channels"]
            return self._build_dependency_dict(specs["dependencies"])
        return {}

    @staticmethod
    def _get_default_req_file() -> Path:
        return Path("environment.yml")

    def _fetch_env_deps(self) -> Dict[str, CondaPackage]:
        """
        Fetch dependencies from currently active conda environment
        """
        if not os.getenv("CONDA_DEFAULT_ENV"):
            return {}
        export = execute_conda_command(["env", "export"])
        specs = yaml.safe_load(export)

        self._env_name = self._env_name or specs.get("name")
        self._channels = self._channels + specs["channels"]
        return self._build_dependency_dict(specs["dependencies"])

    def write_spec(self):
        """
        Write requirements to `environment.yml`
        """
        final = {}
        if self._env_name:
            final["name"] = self._env_name
        if self._prefix:
            final["prefix"] = self._prefix
        final["channels"] = sorted(list(set(self._channels)))
        conda_deps = []
        pip_deps = []
        collated = self.collate_final()
        for dep in collated:
            if isinstance(dep, PipPackage):
                pip_deps.append(str(dep))
            else:
                conda_deps.append(str(dep))
        final["dependencies"] = conda_deps
        final["dependencies"].append({"pip": pip_deps})  # noqa
        yaml.safe_dump(final, self.req_file.open(mode="w+"))


def _yield_valid_lines(content):
    """Yield valid lines from requirements.txt
    """
    lines = (line for line in content.splitlines())
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Drop comments but not # in a URL
        if ' #' in line:
            line = line[:line.find(' #')]
        # line continuations
        if line.endswith('\\'):
            line = line[:-2].strip()
            try:
                line += next(lines)
            except StopIteration:
                return
        yield line


class PipManager(DependencyManagerBase):
    def _read_file_deps(self) -> Dict[str, PipPackage]:
        """
        Read requirements.txt to fetch user defined dependencies
        """
        file_deps = {}
        if self.req_file.exists():
            for ln in _yield_valid_lines(self.req_file.read_text()):
                dep = PipPackage.from_string(ln)
                file_deps[dep.parsed_name] = dep
        return file_deps

    @staticmethod
    def _get_default_req_file() -> Path:
        return Path("requirements.txt")

    def _fetch_env_deps(self) -> Dict[str, PipPackage]:
        """
        Look at the currently active environment to fetch the list of installed
        dependencies.
        """
        out = {}
        working_set = pkg_resources.working_set
        if working_set:
            for ws in working_set:  # skipcq: PYL-E1133
                dep = PipPackage.from_distribution(ws)
                out[dep.parsed_name] = dep
        return out

    def write_spec(self):
        """
        Write requirements to `requirements.txt`
        """
        collated = self.collate_final()
        out = "\n".join((str(val) for val in collated)) + "\n"
        Path("requirements.txt").write_text(out)

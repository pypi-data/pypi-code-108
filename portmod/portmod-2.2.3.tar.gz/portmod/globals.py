# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import pickle
import tempfile
from functools import lru_cache
from typing import Any, List, Optional

from appdirs import AppDirs

import portmod
from portmodlib.l10n import l10n


@lru_cache()
def get_version() -> str:
    """Returns portmod version"""
    try:
        from ._version import version

        return str(version)
    except ImportError:
        osp = os.path
        possible_root = osp.dirname(osp.dirname(osp.realpath(__file__)))
        if osp.isfile(osp.join(possible_root, ".portmod_not_installed")):
            # Only a dev dependency and is otherwise unneeded at runtime
            import setuptools_scm

            return str(setuptools_scm.get_version(possible_root))
        else:
            try:
                from importlib.metadata import version as version_func
            except ModuleNotFoundError:
                from importlib_metadata import version as version_func  # type: ignore

            return str(version_func("portmod"))


class Env:
    ALLOW_LOAD_ERROR = True
    DEBUG = False
    _DIRS = AppDirs("portmod")
    DATA_DIR: str = _DIRS.user_data_dir
    CONFIG_DIR: str = _DIRS.user_config_dir
    CACHE_DIR: str = _DIRS.user_cache_dir
    INTERACTIVE = True
    TESTING = False
    PREFIX_NAME: Optional[str] = None
    PREFIX_ARCH: Optional[str] = None
    REPOS: List["portmod.repo.Repo"]

    # The following variables are none if a prefix has not been selected
    class Prefix:
        REPOS: List["portmod.repo.Repo"]

        def __init__(self, prefix_name: str):
            from portmod.prefix import get_prefixes

            if prefix_name not in get_prefixes():
                raise Exception(l10n("invalid-prefix", prefix=prefix_name))

            prefix = get_prefixes()[prefix_name]

            self.ARCH: str = prefix.arch
            self.CONFIG_DIR: str = os.path.join(env.CONFIG_DIR, prefix_name)
            self.SET_DIR: str = os.path.join(self.CONFIG_DIR, "sets")
            self.CONFIG: str = os.path.join(self.CONFIG_DIR, "portmod.conf")

            self.ROOT: str = prefix.path or os.path.join(env.DATA_DIR, prefix_name)
            self.MODULES_DIR = os.path.join(self.ROOT, "modules")
            self.VARIABLE_DATA = os.path.join(self.ROOT, "var")
            self.VAR_SET_DIR = os.path.join(self.VARIABLE_DATA, "sets")
            self.INSTALLED_DB = os.path.join(self.VARIABLE_DATA, "db")
            self.NEWS_DIR = os.path.join(self.VARIABLE_DATA, "news")

            self.CACHE_DIR = os.path.join(env.CACHE_DIR, "prefix", prefix_name)
            self.PYBUILD_INSTALLED_CACHE = os.path.join(self.CACHE_DIR, "pybuild")
            self.CONFIG_PROTECT_DIR = os.path.join(self.CACHE_DIR, "cfg_protect")
            self.LOCAL_MODS = os.path.join(self.ROOT, "local")
            self.REPOS = []

        def __setattr__(self, name: str, value: Any):
            if isinstance(value, str):
                os.environ["PORTMOD_" + name] = value
            super().__setattr__(name, value)

    def prefix(self) -> Prefix:
        if self.PREFIX_NAME is not None:
            return self._prefix
        raise Exception("Internal error: Prefix has not been initialized!")

    def set_prefix(self, prefix: Optional[str]):
        from portmod.lock import has_prefix_exclusive_lock, has_prefix_lock
        from portmod.repos import get_repos

        if self.PREFIX_NAME:
            if has_prefix_exclusive_lock() or has_prefix_lock():
                raise Exception("Cannot change prefix while a lock is acquired!")

        if prefix:
            self._prefix = Env.Prefix(prefix)
            self.PREFIX_NAME = prefix
            self._prefix.REPOS = get_repos()
        else:
            self.PREFIX_NAME = None

    def __init__(self):
        self.PREFIX_FILE = os.path.join(self.DATA_DIR, "prefix")
        self.REPOS_DIR = os.path.join(self.DATA_DIR, "repos")
        self.PYBUILD_CACHE_DIR = os.path.join(self.CACHE_DIR, "pybuild")
        self.DOWNLOAD_DIR = os.path.join(self.CACHE_DIR, "downloads")
        self.GLOBAL_PORTMOD_CONFIG = os.path.join(self.CONFIG_DIR, "portmod.conf")
        self.REPOS_FILE = os.path.join(self.CONFIG_DIR, "repos.cfg")
        self.REPOS = []

        tempfile.tempdir = None
        self.TMP_DIR = os.path.join(tempfile.gettempdir(), "portmod")
        self.PYBUILD_TMP_DIR = os.path.join(self.TMP_DIR, "pybuild")
        self.WARNINGS_DIR = os.path.join(self.PYBUILD_TMP_DIR, "messages")
        self.MESSAGES_DIR = os.path.join(self.PYBUILD_TMP_DIR, "warnings")
        self.TMP_VDB = os.path.join(self.TMP_DIR, "tmpdb")
        self.INDEX = os.path.join(self.CACHE_DIR, "index")

    def __setattr__(self, name: str, value: Any):
        if isinstance(value, str):
            os.environ["PORTMOD_" + name] = value
        super().__setattr__(name, value)

    def serialize(self):
        result = {}
        for key in dir(self):
            if not key.startswith("__") and not callable(getattr(self, key)):
                result[key] = getattr(self, key)
        return pickle.dumps(result)

    def deserialize(self, dump: bytes):
        result = pickle.loads(dump)
        for key in result:
            setattr(self, key, result[key])


env = Env()

# Must be imported after env has been defined
from portmod.repos import get_local_repos  # noqa: E402


def refresh_env():
    global env

    env.__init__()  # type: ignore
    env.REPOS = list(get_local_repos().values())


env.REPOS = list(get_local_repos().values())

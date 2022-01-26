# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Module for directly loading pybuild files.
These functions should not be called directly.
See portmod.loader for functions to load pybuilds safely using a sandbox.
"""

import ast
import glob
import importlib
import importlib.util
import os
import sys
from functools import lru_cache
from logging import warning
from types import SimpleNamespace
from typing import Any, Dict, Optional, cast

from RestrictedPython import (
    RestrictingNodeTransformer,
    compile_restricted_exec,
    limited_builtins,
    safe_globals,
)
from RestrictedPython.Eval import default_guarded_getitem, default_guarded_getiter
from RestrictedPython.Guards import (
    guarded_iter_unpack_sequence,
    guarded_unpack_sequence,
    safer_getattr,
)

from .atom import Atom
from .globals import tmp_vdb, vdb_path
from .pybuild import FullInstalledPybuild, FullPybuild

WHITELISTED_IMPORTS = {
    "filecmp",
    "glob",
    "os",
    "sys",
    "shutil",
    "stat",
    "os.path",
    "chardet",
    "pybuild",
    "pybuild.info",
    "pybuild.winreg",
    "re",
    "csv",
    "json",
    "typing",
    "fnmatch",
    "collections",
}


def find_installed_path(atom: Atom, vdb: Optional[str] = None) -> Optional[str]:
    if not vdb:
        vdb = vdb_path()

    if atom.C:
        path = os.path.join(vdb, atom.C, atom.PN)
        if os.path.exists(path):
            results = glob.glob(os.path.join(path, "*.pybuild"))
            assert len(results) == 1
            return results[0]
    else:
        for dirname in glob.glob(os.path.join(vdb, "*")):
            path = os.path.join(vdb, dirname, atom.PN)
            if os.path.exists(path):
                results = glob.glob(os.path.join(path, "*.pybuild"))
                assert len(results) == 1
                return results[0]
    return None


@lru_cache()
def _import_common(name: str) -> SimpleNamespace:
    """
    args:
        name: The import name as an absolute import path
        installed: Whether or not the package calling this is an installed package
        load_function: The function taking a file path and a keyword argument installed,
            indicating the installed status of the file to be loaded, to be used to load
            the common module

    returns:
        The Module as a SimpleNamespace
    """
    if len(name.split(".")) > 2:
        raise Exception(f"Invalid package {name}")
    _, module_name = name.split(".")
    base_atom = Atom(f"common/{module_name}")
    path = find_installed_path(base_atom)

    if not path:
        path = find_installed_path(base_atom, tmp_vdb())

    if not path:
        raise Exception(f"Could not find package {name}")

    result = __load_module(path, installed=True)

    return SimpleNamespace(
        **{key: value for key, value in result.items() if not key.startswith("_")}
    )


def _import(installed: bool, repo: Optional[str] = None):
    def import_fn(name, globs, loc, fromlist, level):
        if name.startswith("common."):
            return _import_common(name)
        if name not in WHITELISTED_IMPORTS:
            raise RuntimeError(f"Importing from {name} is not allowed")
        return __import__(name, globs, loc, fromlist, level)

    return import_fn


# Default implementation to handle invalid pybuilds
class Package:
    def __init__(self):
        raise Exception("Package is not defined")


def default_write_guard(ob):
    """Noop write guard"""
    return ob


def safer_hasattr(obj, name):
    """
    Version of hasattr implemented using safet_getattr

    This doesn't really provide any extra security, but does mean that
    str.format, and attributes beginning with underscores, which are
    blocked by safer_getattr, return False rather than True
    """
    try:
        safer_getattr(obj, name)
    except (NotImplementedError, AttributeError):
        return False
    return True


def default_apply(func, *args, **kwargs):
    return func(*args, **kwargs)


MINIMAL_GLOBALS: Dict[str, Any] = safe_globals
SAFE_GLOBALS: Dict[str, Any] = MINIMAL_GLOBALS.copy()
SAFE_GLOBALS["__builtins__"] = MINIMAL_GLOBALS["__builtins__"].copy()
SAFE_GLOBALS.update({"Package": Package})
SAFE_GLOBALS["__builtins__"].update(
    {
        "FileNotFoundError": FileNotFoundError,
        "__metaclass__": type,
        "_apply_": default_apply,
        "_getattr_": safer_getattr,
        "_getitem_": default_guarded_getitem,
        "_getiter_": default_guarded_getiter,
        "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
        "_unpack_sequence_": guarded_unpack_sequence,
        "_write_": default_write_guard,
        "all": all,
        "any": any,
        "dict": dict,
        "enumerate": enumerate,
        "filter": filter,
        "frozenset": frozenset,
        "getattr": safer_getattr,
        "hasattr": safer_hasattr,
        "iter": iter,
        "map": map,
        "max": max,
        "min": min,
        "next": next,
        "reversed": reversed,
        "set": set,
        "sorted": sorted,
        "sum": sum,
        "super": super,
    }
)
SAFE_GLOBALS["__builtins__"].update(limited_builtins)

SANDBOX_GLOBALS: Dict[str, Any] = SAFE_GLOBALS.copy()
SANDBOX_GLOBALS["__builtins__"] = SAFE_GLOBALS["__builtins__"].copy()


class PrintWrapper:
    def __init__(self, _getattr_=None):
        self.txt = []
        self._getattr_ = _getattr_

    def write(self, text):
        self.txt.append(text)

    def __call__(self):
        return "".join(self.txt)

    def _call_print(self, *objects, **kwargs):
        if kwargs.get("file", None) is None:
            kwargs["file"] = sys.stdout
        else:
            self._getattr_(kwargs["file"], "write")
        print(*objects, **kwargs)


# print and open are only allowed within the sandbox
SANDBOX_GLOBALS["__builtins__"].update({"_print_": PrintWrapper, "open": open})


class Policy(RestrictingNodeTransformer):
    def visit_JoinedStr(self, node):
        return self.node_contents_visit(node)

    def visit_FormattedValue(self, node):
        return self.node_contents_visit(node)

    def visit_AnnAssign(self, node):
        return self.node_contents_visit(node)

    def visit_AugAssign(self, node):
        return self.node_contents_visit(node)

    def visit_ImportFrom(self, node):
        if (
            node.module in WHITELISTED_IMPORTS
            or node.module.startswith("pybuild")
            and node.level == 0
        ):
            try:
                module = importlib.import_module(node.module)
                for name in node.names:
                    if isinstance(module.__dict__.get(name.name), type(importlib)):
                        self.error(
                            node, "Importing modules from other modules is forbidden"
                        )
            except ModuleNotFoundError:
                pass

        return RestrictingNodeTransformer.visit_ImportFrom(self, node)

    def visit_FunctionDef(self, node):
        node = RestrictingNodeTransformer.visit_FunctionDef(self, node)
        if node.name == "__init__":
            newnode = ast.parse("super().__init__()").body[0]
            newnode.lineno = node.lineno
            newnode.col_offset = node.col_offset
            node.body.insert(0, newnode)
        return node


def restricted_load(code, filepath: str, _globals: Dict[str, Any]):
    if sys.platform == "win32":
        code = code.replace("\\", "\\\\")
    byte_code, errors, warnings, names = compile_restricted_exec(
        code, filename=filepath, policy=Policy
    )
    if errors:
        raise SyntaxError(errors)
    seen: Dict[str, str] = {}
    for message in [seen.setdefault(x, x) for x in warnings if x not in seen]:
        if not message.endswith("Prints, but never reads 'printed' variable."):
            warning(f"In file {filepath}: {message}")
    exec(byte_code, _globals, _globals)


def __load_module(path: str, *, installed=False) -> Dict[str, Any]:
    filename, _ = os.path.splitext(os.path.basename(path))

    with open(path, "r", encoding="utf-8") as file:
        code = file.read()
        tmp_globals = SANDBOX_GLOBALS.copy()
        tmp_globals["__builtins__"]["__import__"] = _import(
            installed=installed,
        )
        tmp_globals["__name__"] = filename
        restricted_load(code, path, tmp_globals)

    return tmp_globals


def __load_file_common(path: str, module: Dict[str, Any], installed: bool):
    module["Package"].__pybuild__ = path
    pkg = module["Package"]()
    pkg.FILE = os.path.abspath(path)
    pkg.INSTALLED = False

    if not installed:
        # determine common dependencies
        def find_common_imports(file: str):
            depends = []
            with open(file, "r", encoding="utf-8") as fp:
                tree = ast.parse(fp.read())

            def find_imports(tree: ast.AST):
                if isinstance(tree, ast.Module):
                    for statement in tree.body:
                        if isinstance(statement, ast.Import):
                            for alias in statement.names:
                                if alias.name.startswith("common."):
                                    depends.append(alias.name.replace(".", "/"))
                        elif isinstance(statement, ast.ImportFrom):
                            if statement.module and statement.module.startswith(
                                "common."
                            ):
                                depends.append(statement.module.replace(".", "/"))

            # Globals
            find_imports(tree)
            # TODO: Inline imports in functions?
            return depends

        pkg.DEPEND = " ".join([pkg.DEPEND] + find_common_imports(pkg.FILE))
    return pkg


def load_file(path: str, *, installed=False) -> FullPybuild:
    """
    Loads a pybuild file

    :param path: Path of the pybuild file
    """
    module = __load_module(path, installed=installed)
    pkg = __load_file_common(path, module, installed)
    return cast(FullPybuild, pkg)


def load_installed(file: str) -> FullInstalledPybuild:
    """
    Loads an installed pybuild

    :param file: Path of the pybuild file
    """
    mod = cast(FullInstalledPybuild, load_file(file, installed=True))
    __load_installed_common(mod, file)
    return mod


def __load_installed_common(mod, file: str):
    """Shared code for loading installed pybuilds"""
    mod.INSTALLED = True
    parent = os.path.dirname(file)

    def read_file(name: str) -> Optional[str]:
        if os.path.exists(os.path.join(parent, name)):
            with open(os.path.join(parent, name), "r") as repo_file:
                return repo_file.read().strip()
        return None

    repo = read_file("REPO")
    if not repo:
        raise Exception(
            f"Internal Error: Installed package in file {file}"
            "has no repository identifier"
        )
    mod.REPO = repo
    mod.INSTALLED_USE = set((read_file("USE") or "").split())
    mod.RDEPEND = read_file("RDEPEND") or mod.RDEPEND
    mod.DEPEND = read_file("DEPEND") or mod.DEPEND

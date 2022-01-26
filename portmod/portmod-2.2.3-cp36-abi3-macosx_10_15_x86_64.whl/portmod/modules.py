# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Interface for interacting with installed modules
"""

import csv
import glob
import os
import shutil
from difflib import unified_diff
from logging import info
from types import SimpleNamespace
from typing import Generator, List

from portmodlib.l10n import l10n
from portmodlib.parsers.list import add_list, read_list

from .config import get_config
from .globals import env
from .loader import load_module
from .prompt import prompt_options


class ModuleState(SimpleNamespace):
    TEMP: str
    ROOT: str
    CACHE: str


def do_func(state, func, args=None):
    if args is None:
        func(state)
    else:
        func(state, args)


class ModuleFunction:
    """Function defined by a module"""

    name: str

    def __init__(
        self, name: str, desc: str, do, options, parameters, state: ModuleState
    ):
        self.name = name
        self.desc = desc
        self.__do__ = do
        self.state = state
        if options is not None:
            self.options = options
        else:
            self.options = []
        if parameters is not None:
            self.parameters = parameters
        else:
            self.parameters = []

    def do(self, args):
        """Execute action"""
        do_func(
            self.state,
            self.__do__,
            {key: getattr(args, key) for key in self.options},
        )

    def do_noargs(self):
        """Execute action without arguments"""
        do_func(self.state, self.__do__)

    def describe(self) -> str:
        """Returns string describing function"""
        return str(self.__do__.__doc__)


class Module:
    """Base module object"""

    def __init__(self, name: str, desc: str, funcs: List[ModuleFunction], state):
        self.funcs = {func.name: func for func in funcs}
        self.name = name
        self.desc = desc
        self.state = state
        os.makedirs(state.TEMP, exist_ok=True)
        os.makedirs(state.CACHE, exist_ok=True)

    def update(self):
        if "update" in self.funcs:
            self.funcs["update"].do_noargs()

    def add_parser(self, parsers, parents):
        parser = parsers.add_parser(self.name, help=self.desc, parents=parents)
        this_subparsers = parser.add_subparsers()
        for func in self.funcs.values():
            if func.name == "update":
                continue
            func_parser = this_subparsers.add_parser(func.name, help=func.desc)
            for option, parameter in zip(func.options, func.parameters):
                func_parser.add_argument(option, help=parameter)
            func_parser.set_defaults(func=func.do)

        def help_func(args):
            parser.print_help()

        parser.set_defaults(func=help_func)
        self.arg_parser = parser

        return self.arg_parser

    def prerm(self):
        if "prerm" in self.funcs:
            self.funcs["prerm"].do_noargs()

    def cleanup(self):
        shutil.rmtree(self.state.TEMP)


def get_state(module_name: str) -> ModuleState:
    return ModuleState(
        TEMP=os.path.join(env.TMP_DIR, "modules", module_name),
        ROOT=os.path.join(env.prefix().ROOT),
        CACHE=os.path.join(env.prefix().CACHE_DIR, "modules", module_name),
    )


def iterate_modules() -> Generator[Module, None, None]:
    """Returns a generator which produces all modules"""
    modules_dir = get_config().get("MODULEPATH")
    if modules_dir:
        modules_path = os.path.join(env.prefix().ROOT, modules_dir)
        for module_file in glob.glob(os.path.join(modules_path, "*.pmodule")):
            module_name, _ = os.path.splitext(os.path.basename(module_file))
            module = load_module(module_file, get_state(module_name))
            yield module
            module.cleanup()


def module_prerm(path: str):
    module_name, _ = os.path.splitext(os.path.basename(path))
    module = load_module(path, get_state(module_name))
    module.prerm()
    module.cleanup()


def update_modules():
    """Runs update function (if present) on all installed modules"""
    for module in iterate_modules():
        info(l10n("updating-module", name=module.name))
        module.update()

    handle_cfg_protect()


def handle_cfg_protect():
    """Prompts user to allow changes to files made by modules"""
    whitelist_file = os.path.join(
        env.prefix().VARIABLE_DATA, "module-data", "file-whitelist"
    )
    blacklist_file = os.path.join(
        env.prefix().VARIABLE_DATA, "module-data", "file-blacklist"
    )
    blacklist = set()
    whitelist = set()
    if os.path.exists(whitelist_file):
        whitelist = set(read_list(whitelist_file))
    if os.path.exists(blacklist_file):
        blacklist = set(read_list(blacklist_file))

    # Display file changes to user and prompt
    for src, dst in get_redirections():
        src_data = None
        dst_data = None
        if os.path.islink(src):
            src_lines = [l10n("symlink-to", path=os.readlink(src)) + "\n"]
        else:
            try:
                with open(src, "r") as src_file:
                    src_lines = src_file.readlines()
            except UnicodeDecodeError:
                src_lines = ["<Binary data>\n"]
                with open(src, "rb") as src_file_b:
                    src_data = src_file_b.read()
        dst_lines = []
        if os.path.lexists(dst):
            if os.path.islink(dst):
                dst_lines = [l10n("symlink-to", path=os.readlink(dst)) + "\n"]
            else:
                try:
                    with open(dst, "r") as dst_file:
                        dst_lines = dst_file.readlines()
                except UnicodeDecodeError:
                    dst_lines = ["<" + l10n("binary-data") + ">\n"]
                    with open(dst, "rb") as dst_file_b:
                        dst_data = dst_file_b.read()

        if src_lines == dst_lines and src_data == dst_data:
            os.remove(src)
            continue

        if dst in blacklist:
            info(l10n("skipped-blacklisted-file", file=dst))
            os.remove(src)
            continue

        output = unified_diff(dst_lines, src_lines, dst, src)
        if dst in whitelist:
            # User won't be prompted, so we should still display output, but supress it
            # unless running verbosely
            info("".join(output))
        else:
            print("".join(output))

        print()

        if dst not in whitelist and not env.INTERACTIVE:
            info(l10n("skipped-update-noninteractive", file=dst))
            continue

        response = None
        if dst not in whitelist:
            response = prompt_options(
                l10n("apply-above-change-qn"),
                [
                    (l10n("yes-short"), l10n("apply-change")),
                    (l10n("always-short"), l10n("module-apply-always")),
                    (l10n("no-short"), l10n("module-do-not-apply-change")),
                    (l10n("never-short"), l10n("module-apply-never")),
                ],
            )

        if dst in whitelist or response in (l10n("yes-short"), l10n("always-short")):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(dst) or os.path.islink(dst):
                os.remove(dst)
            shutil.move(src, dst)

        if response == l10n("all-short"):
            add_list(whitelist_file, dst)

        if response == l10n("never-short"):
            add_list(blacklist_file, dst)

        if response in {l10n("no-short"), l10n("never-short")}:
            os.remove(src)

    if env.INTERACTIVE:
        clear_redirections()


def add_parsers(parsers, parents) -> List[Module]:
    """Adds parsers for the modules to the given argument parser"""
    modules = []
    for module in iterate_modules():
        module.add_parser(parsers, parents)
        modules.append(module)
    return modules


def require_module_updates():
    """
    Creates a file that indicates that modules need to be updated
    """
    open(
        os.path.join(env.prefix().VARIABLE_DATA, ".modules_need_updating"), "a"
    ).close()


def clear_module_updates():
    """Clears the file indicating that modules need updating"""
    path = os.path.join(env.prefix().VARIABLE_DATA, ".modules_need_updating")
    if os.path.exists(path):
        os.remove(path)


def modules_need_updating():
    """Returns true if changes have been made since the config was sorted"""
    return os.path.exists(
        os.path.join(env.prefix().VARIABLE_DATA, ".modules_need_updating")
    )


def get_redirections():
    """
    Iterates over all previously made file redirections and returns the (non-empty)
    results
    """
    if os.path.exists(os.path.join(env.prefix().CONFIG_PROTECT_DIR, "cfg_protect.csv")):
        with open(
            os.path.join(env.prefix().CONFIG_PROTECT_DIR, "cfg_protect.csv"), "r"
        ) as file:
            reader = csv.reader(file)
            for row in reader:
                dst = row[0]
                src = row[1]

                if os.path.exists(src) and os.stat(src).st_size != 0:
                    yield src, dst


def clear_redirections():
    path = os.path.join(env.prefix().CONFIG_PROTECT_DIR, "cfg_protect.csv")
    if os.path.exists(path):
        os.remove(path)

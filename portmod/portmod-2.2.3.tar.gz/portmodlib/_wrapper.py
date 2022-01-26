# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
CLI for interacting with individual pybuild files
"""

import argparse
import json
import logging
import lzma
import os
import pickle
import re
import sys
from traceback import extract_tb, format_exception_only, format_list
from types import SimpleNamespace

from ._loader import load_file, load_installed
from ._phase import PhaseState
from .execute import execute
from .fs import is_parent
from .globals import prefix_name, vdb_path
from .log import init_logger
from .pybuild import FullPybuild
from .util import pybuild_dumper


def excepthook(typ, value, tb):
    """An exception hook which suppresses frames from this module in the traceback"""
    if value.__cause__:
        cause = value.__cause__
        excepthook(type(cause), cause, cause.__traceback__)
        print()
        print(
            "The above exception was the direct cause of the following exception:"
            + os.linesep
        )
    if value.__context__:
        context = value.__context__
        excepthook(type(context), context, context.__traceback__)
        print()
        print(
            "During handling of the above exception, another exception occurred:"
            + os.linesep
        )
    show = [
        fs
        for fs in extract_tb(tb)
        if fs.filename and fs.filename not in (__file__, "<string>")
    ]
    fmt = format_list(show) + format_exception_only(typ, value)
    print("Traceback (most recent call last):")
    print("".join(fmt), end="", file=sys.stderr)


def wrapper_pybuild(args):
    # Set info variables
    from pybuild.info import _set_info

    _set_info(args.pybuild_file)

    pkg: FullPybuild
    if prefix_name() and is_parent(
        os.path.abspath(os.path.normpath(args.pybuild_file)), vdb_path()
    ):
        pkg = load_installed(args.pybuild_file)
    else:
        pkg = load_file(args.pybuild_file)

    if args.state_dir and os.path.exists(args.state_dir):
        state_file = os.path.join(args.state_dir, "state.pickle")
        if os.path.exists(state_file):
            with open(state_file, "rb") as b_file:
                pkg.__dict__ = pickle.load(b_file)

    if args.initial_state:
        state = PhaseState.from_json(json.loads(args.initial_state))
        pkg.__dict__.update(state.__dict__)

    def pkg_func(pkg, name):
        pkg.execute = execute
        func = getattr(pkg, name)
        return func()

    for command in args.command:
        if command == "unpack":
            pkg_func(pkg, "src_unpack")
        elif command == "prepare":
            pkg_func(pkg, "src_prepare")
        elif command == "install":
            pkg_func(pkg, "src_install")
        elif command == "postinst":
            pkg_func(pkg, "pkg_postinst")
        elif command == "pretend":
            pkg_func(pkg, "pkg_pretend")
        elif command == "nofetch":
            pkg_func(pkg, "pkg_nofetch")
        elif command == "can-update-live":
            result = pkg_func(pkg, "can_update_live")
            if not isinstance(result, bool):
                raise RuntimeError(
                    f"can_update_live returned unexpected result {result}"
                )
            sys.exit(int(result) * 142)

    if args.state_dir:
        with open(os.path.join(args.state_dir, "state.pickle"), "wb") as b_file:
            pickle.dump(pkg.__dict__, b_file)

        with open(os.path.join(args.state_dir, "environment.xz"), "wb") as b_file:
            # Keys are sorted to produce consistent results and
            # easy to read commits in the DB
            dictionary = pkg.__class__.__dict__.copy()
            dictionary.update(pkg.__dict__)
            dictionary = dict(
                filter(
                    lambda elem: not elem[0].startswith("_") and elem[0] != "execute",
                    dictionary.items(),
                )
            )
            jsonstr = json.dumps(dictionary, default=pybuild_dumper, sort_keys=True)
            b_file.write(lzma.compress(str.encode(jsonstr)))


def wrapper_module(args):
    if args.initial_state:
        state = PhaseState.from_json(json.loads(args.initial_state))

    name, _ = os.path.splitext(os.path.basename(args.module_file))
    module = os.path.basename(os.path.dirname(args.module_file))
    sys.path.append(os.path.dirname(os.path.dirname(args.module_file)))
    with open(args.module_file, "r", encoding="utf-8") as file:
        tmp_globals = {
            "__builtins__": __builtins__,
            "__name__": name,
            "__package__": module,
        }
        code = compile(file.read(), args.module_file, "exec")
        exec(code, tmp_globals)

    do_functions = {}
    descriptions = {}
    describe_options = {}
    describe_parameters = {}
    for globname in tmp_globals:
        if globname.startswith("do_"):
            name = re.sub("^do_", "", globname)
            do_functions[name] = tmp_globals[globname]
            descriptions[name] = tmp_globals[globname].__doc__
        match = re.match("^describe_(.*)_options$", globname)
        if match:
            describe_options[match.group(1)] = tmp_globals[globname]()
        match = re.match("^describe_(.*)_parameters$", globname)
        if match:
            describe_parameters[match.group(1)] = tmp_globals[globname]()

    if args.command == "load":
        name = os.path.basename(args.module_file)
        name, _ = os.path.splitext(name)
        dictionary = {
            "name": name,
            "desc": tmp_globals.get("__doc__"),
            "functions": {
                name: {
                    "desc": descriptions[name],
                    "options": describe_options.get(name),
                    "parameters": describe_parameters.get(name),
                }
                for name in descriptions
            },
        }
        print(json.dumps(dictionary))
    elif args.command == "execute" and args.module_func:
        if args.module_func == "update":
            do_functions[args.module_func](state)
        else:
            function_args = None
            if args.args:
                function_args = SimpleNamespace(**json.loads(args.args))
            do_functions[args.module_func](state, function_args)


def main():
    """
    Wrapper script for directly loading pybuild and module files.
    This should always be invoked using the executable sandbox,
    and is not intended to be invoked manually.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--verbosity", help="verbosity level")
    subparsers = parser.add_subparsers()
    pybuild = subparsers.add_parser("pybuild", help="interact with pybuild files")
    module = subparsers.add_parser("module", help="interact with module files")
    pybuild.add_argument("pybuild_file", metavar="<pybuild file>")
    pybuild.add_argument("command", metavar="<command>", nargs="+")
    pybuild.add_argument(
        "--state-dir",
        help="The path of a directory to be used to store state information",
    )
    pybuild.add_argument(
        "--initial-state",
        help="A json-encoded dictionary of values to be set as package attributes",
    )

    module.add_argument("module_file", metavar="<module file>")
    module.add_argument("command", metavar="<command>")
    module.add_argument(
        "--module-func", help="name of function to execute if command is execute"
    )
    module.add_argument("--args", help="arguments to pass to the function")
    module.add_argument(
        "--initial-state",
        help="A json-encoded dictionary of values to be set as package attributes",
    )

    pybuild.set_defaults(func=wrapper_pybuild)
    module.set_defaults(func=wrapper_module)

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    args.verbose = None
    args.quiet = None
    init_logger(args)
    # Set logging level manually. Args doesn't contain any of --verbose or --quiet
    if args.verbosity is not None:
        logging.root.setLevel(args.verbosity)

    # In debug-level verbosity or lower, use default full traces
    # Otherwise suppress the parts referencing this module
    if logging.root.level > logging.DEBUG:
        sys.excepthook = excepthook
    args.func(args)

#!/usr/bin/env python
# pylint: disable = invalid-name, missing-docstring

"""Check classes are documented properly as per numpydoc requirements.

This currently checks:
  - constructor parameters are documented in the class docstring, not __init__
  - listed sections in docstrings are valid

Note: because this script imports finesse modules directly, it should be executed within the same
environment used to develop Finesse. In pre-commit, for example, this means setting the script
language as "system" and not "python".

Author: Sean Leavey
"""

import sys
import argparse
import inspect
from textwrap import indent as _indent, wrap
from pathlib import Path
from importlib import import_module
import warnings
from numpydoc.docscrape import FunctionDoc, ClassDoc
import finesse


indent = lambda text: _indent("\n".join(wrap(str(text))) + "\n", prefix=" " * 4)


FINESSE_ROOT = Path(finesse.__file__.replace("__init__.py", ""))
DOCURL = "https://finesse.docs.ligo.org/finesse3/developer/documenting.html#writing-sphinx-compatible-docstrings"


def check_module(path):
    path = Path(path).resolve()

    try:
        module_path = path.relative_to(FINESSE_ROOT)
    except ValueError:
        # Specified file is not part of the finesse package.
        return 0

    module_name = "." + str(module_path.stem)
    package = str(finesse.__name__ + "." + str(module_path.parent).replace("/", "."))
    package = package.rstrip(".")

    try:
        module = import_module(module_name, package)
    except ModuleNotFoundError:
        return 0

    has_issue = False

    # Categorise members.
    classes = []
    functions = []
    for _, obj in inspect.getmembers(module):
        try:
            if obj.__module__ != module.__name__:
                # Reject imported modules.
                continue
        except AttributeError:
            # This is not a class or function; maybe a dict or something else defined on
            # the top level that we don't care about.
            continue

        if inspect.isclass(obj):
            classes.append(obj)
        elif inspect.isfunction(obj):
            functions.append(obj)
        else:
            warnings.warn(f"don't know how to handle member {repr(obj)}")
            continue

    for class_ in classes:
        classname = f"{module_path}::{class_.__name__}"

        with warnings.catch_warnings(record=True) as warnlist:
            # Create a ClassDoc object so that we can grab any warnings issued by
            # numpydoc.
            try:
                ClassDoc(class_)
            except Exception as e:
                print(
                    f"error while processing docstring for {class_.__name__}: \n{indent(e)}"
                )
                has_issue = True

            # Print any caught warnings.
            if warnlist:
                for wrng in warnlist:
                    print(f"{classname}: numpydoc warning: {wrng.message}")

                has_issue = True

        # Create FunctionDoc objects for each of the class methods to grab any
        # warnings issued by numpydoc.
        for _, method in inspect.getmembers(class_):
            try:
                methodname = method.__name__
                methodmodule = method.__module__
            except AttributeError:
                # Maybe a property?
                try:
                    methodname = method.fget.__name__
                    methodmodule = method.fget.__module__
                except AttributeError:
                    continue

            if methodmodule is not class_.__module__:
                # This is an inherited member, which we'll skip.
                continue

            if methodname.startswith("__"):
                # Skip dunder methods.
                continue

            methodpath = f"{classname}.{methodname}"

            with warnings.catch_warnings(record=True) as warnlist:
                try:
                    methoddoc = FunctionDoc(method)
                except Exception as e:
                    print(
                        f"error while processing docstring for "
                        f"{class_.__name__}.{method.__name__}:\n{indent(e)}"
                    )
                    has_issue = True
                else:
                    # Detect if the method is the current class's init method.
                    try:
                        isinit = method is class_.__init__
                    except AttributeError:
                        # Probably a C parent.
                        isinit = False

                    if isinit:
                        # Check whether the __init__ documentation incorrectly lists the
                        # init parameters.
                        if methoddoc and methoddoc.get("Parameters"):
                            print(
                                f"{methodpath}: constructor parameters should be "
                                f"documented in the class docstring, not __init__ "
                                f"(see {DOCURL})."
                            )

                            has_issue = True

                # Print any caught warnings.
                if warnlist:
                    for wrng in warnlist:
                        print(f"{methodpath}: numpydoc warning: {wrng.message}")

                    has_issue = True

    for function in functions:
        functionname = f"{module_path}::{function.__name__}"

        with warnings.catch_warnings(record=True) as warnlist:
            try:
                FunctionDoc(function)
            except Exception as e:
                print(f"error while processing docstring for {function}: \n{indent(e)}")
                has_issue = True

            # Print any caught warnings.
            if warnlist:
                for wrng in warnlist:
                    print(f"{functionname}: numpydoc warning: {wrng.message}")

                has_issue = True

    return 1 if has_issue else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args(sys.argv)

    retv = 0

    for filename in args.filenames:
        retv |= check_module(filename)

    sys.exit(retv)

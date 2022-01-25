"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2022 Fair Isaac Corporation. All rights reserved.
"""

import os
import sys
import importlib
from typing import Type

from . import __version__
from .app_base import AppBase
from .exec_mode import ExecMode

MSG_PREFIX = "xpressinsight: "


def exit_msg(code: int, msg: str):
    print(MSG_PREFIX + msg, file=sys.stderr)
    exit(code)


def import_app(app_source_dir: str, app_package_name: str = 'application') -> Type[AppBase]:
    """
    Import an Insight application class from an Insight application package. The function
    returns the first class in the imported package that extends the AppBase class.

    Side effects:
    Adds application source directory to sys.path. The imported application package can be
    imported again even after reverting sys.path to it's original value.

    @param app_source_dir: Source directory of the application package.
    @param app_package_name: Name of the application package or main file.
    @return: Imported Insight app class, i.e., a subclass of xpressinsight.AppBase.
    """
    if not os.path.isdir(app_source_dir):
        exit_msg(-1, 'import_app: Parameter app_source_dir="{}" is not a directory.'.format(app_source_dir))

    if not app_package_name == 'application':
        exit_msg(-1, 'import_app: Parameter app_package_name must be set to "application", but it is "{}".'
                 .format(app_package_name))

    app_source_dir = os.path.abspath(app_source_dir)
    sys.path.append(app_source_dir)

    try:
        app_pkg = importlib.import_module(app_package_name)
    except (ImportError, ModuleNotFoundError):
        print(MSG_PREFIX + 'import_app: Could not import "{}" package from directory: {}'
              .format(app_package_name, app_source_dir), file=sys.stderr)
        raise

    app_pkg_dir = os.path.dirname(app_pkg.__file__)

    if app_pkg_dir != app_source_dir:
        print(MSG_PREFIX + "Imported application from non-standard location: {}"
              .format(app_pkg_dir), file=sys.stderr)

    for pkg_attr_name, pkg_attr in app_pkg.__dict__.items():
        if isinstance(pkg_attr, type) and issubclass(pkg_attr, AppBase):
            return pkg_attr

    exit_msg(-1, 'import_app: The "{}" package does not define a subclass of xpressinsight.AppBase.'
             .format(app_package_name))


def run(app_source_dir: str, work_dir: str, exec_mode: str, apprunner_version: str = None,
        test_mode: bool = None, app_package_name: str = 'application'):
    print("xpressinsight package v" + __version__)

    if not os.path.isdir(work_dir):
        exit_msg(-1, 'app_runner.run: Parameter work_dir="{}" is not a directory.'.format(work_dir))

    if not isinstance(exec_mode, str):
        exit_msg(-1, 'app_runner.run: Parameter exec_mode="{}" must be a string.'.format(exec_mode))

    if test_mode is None:
        test_mode = (exec_mode == ExecMode.NONE)
    elif not isinstance(test_mode, bool):
        exit_msg(-1, 'app_runner.run: Parameter test_mode="{}" must be a bool.'.format(test_mode))

    #
    app_type = import_app(app_source_dir, app_package_name)
    app_type.app_cfg._work_dir = work_dir
    app_type.app_cfg._test_mode = test_mode

    if apprunner_version is None or apprunner_version < '1.2.0':
        print("ERROR: Old version of Xpress Insight server detected. Please upgrade to a more recent version, "
              "or downgrade 'xpressinsight' Python package.", file=sys.stderr)
        sys.exit(1)

    if exec_mode == ExecMode.NONE:
        exit_code = app_type().load_and_run(delete_work_dir=False)
    else:
        exit_code = app_type().call_exec_mode(exec_mode)

    sys.exit(exit_code)

# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
Main GUI and CLI application entry point.
"""
import os
import functools
import sys
import signal
import contextlib
import psutil

from PySide2 import QtCore

from sympathy.platform import node_result
from sympathy.platform import feature
from .. import execore
from .. import appcore
from .. import version
from .. import util
from .. tasks import task_worker
from .. import settings
from .. import flow
from .. import cli_application
from .. import common

# Python's default recursion limit (1000) is a bit low. We currently hit that
# ceiling when recursively traversing big (hundreds of nodes) workflows. This
# is an easier fix than optimizing those graph algorithms.
sys.setrecursionlimit(10000)


def connect_app_and_exe(app_core, exe_core):
    # Signals from app_core
    app_core.execute_nodes_requested[util.OrderedSet].connect(
        exe_core.execute_nodes)
    app_core.debug_nodes_requested[util.OrderedSet].connect(
        exe_core.debug_nodes)
    app_core.profile_nodes_requested[util.OrderedSet, util.OrderedSet].connect(
        exe_core.profile_nodes)

    app_core.abort_node_requested[flow.NodeInterface].connect(
        exe_core.abort_node)

    app_core.validate_node_requested[flow.Node].connect(
        exe_core.validate_node)
    app_core.execute_node_parameter_view_requested[flow.Node].connect(
        exe_core.execute_node_parameter_view)
    app_core.execute_subflow_parameter_view_requested[
        flow.Flow, str].connect(
            exe_core.execute_subflow_parameter_view)
    app_core.execute_port_viewer[flow.Port].connect(
        exe_core.execute_port_viewer)
    app_core.node_library_aliases.connect(exe_core.set_type_aliases)
    app_core.restart_all_task_workers.connect(
        exe_core.restart_all_task_workers)
    app_core.message_output.connect(
        exe_core.message_input)

    # Signals from exe_core
    exe_core.execute_node_done[flow.NodeInterface, node_result.NodeResult].connect(
        app_core.execute_node_done)
    exe_core.execute_child_node_done[
        flow.NodeInterface, flow.NodeInterface, node_result.NodeResult, bool].connect(
            app_core.execute_child_node_done)
    exe_core.display_message.connect(
        app_core.display_message)
    exe_core.node_has_aborted[flow.NodeInterface, list].connect(
        app_core.node_has_aborted)
    exe_core.node_is_aborting[flow.NodeInterface, list].connect(
        app_core.set_node_is_aborting)
    exe_core.validate_node_done[flow.NodeInterface, node_result.NodeResult].connect(
        app_core.validate_node_done)
    exe_core.node_progress_changed[flow.NodeInterface, float].connect(
        app_core.update_node_progress)
    exe_core.child_node_progress_changed[
        flow.Flow, flow.NodeInterface, float].connect(
        app_core.update_child_node_progress)
    exe_core.execute_node_parameter_view_done[
        flow.NodeInterface, node_result.NodeResult].connect(
            app_core.execute_node_parameter_view_done)
    exe_core.execute_subflow_parameter_view_done[
        flow.NodeInterface, node_result.NodeResult].connect(
            app_core.execute_subflow_parameter_view_done)
    exe_core.node_is_queued[flow.NodeInterface].connect(
        app_core.set_node_status_queued)
    exe_core.node_execution_started[flow.NodeInterface].connect(
        app_core.set_node_status_execution_started)
    exe_core.all_nodes_finished.connect(
        app_core.all_execution_has_finished)
    exe_core.profiling_finished[set].connect(
        app_core.profiling_finished)
    exe_core.message_output.connect(
        app_core.message_input)
    exe_core.help_requested.connect(
        app_core.help_requested)


def create_server():
    pass


def basic_setup(app, args=None):
    app_core = appcore.AppCore(args, parent=app)
    # app_core.reload_node_library()
    exe_core = execore.ExeCore(parent=app)
    execore.working_dir = os.getcwd()
    connect_app_and_exe(app_core, exe_core)
    return app_core, exe_core


def kill(ppid):
    if not psutil.pid_exists(ppid):
        os.kill(os.getpid(), signal.SIGTERM)


def common_setup(app, args=None):
    # app.processEvents()
    create_server()
    task_worker.create_client()
    util.create_default_folder()
    util.create_install_folder()
    util.setup_resource_folder()
    # WARNING: create_storage_folder depends on the application name (via
    # QDesktopServices.storageLocation). Make sure to use setApplicationName
    # before common_setup.
    util.create_storage_folder()
    # Moved before creating AppCore, and ExeCore to enable use of server tasks
    # while initiating these components.
    res = basic_setup(app, args)
    return res

def common_teardown(app_core):
    # Gracefully exit appcore and deallocate resources used by the platform.
    task_worker.close_client()
    util.post_execution()


def create_start_flow(main_window, args):
    if args.filename is not None and len(args.filename) > 0:
        flow_filename = args.filename
        main_window.open_named_flow.emit(flow_filename)


def create_gui(args, sys_args, splash):
    # Made imports internal to the function to avoid pulling dependencies into
    # the CLI and the Extract code path. Alternatively this function could be
    # moved to a separate module with these two dependencies on the toplevel
    # (as well as application.py).
    app = QtCore.QCoreApplication.instance()

    from .. import main_window

    app_core, exe_core = common_setup(app, args)
    main_window_ = main_window.MainWindow(app_core, args, splash)
    main_window_.show()
    main_window_.raise_()
    main_window_.activateWindow()

    def interrupt_handler(signum, frame):
        main_window_.quit_application()

    signal.signal(signal.SIGINT, interrupt_handler)

    ppid = settings.instance()['task_manager_pid']
    if ppid:
        kill_timer = QtCore.QTimer(parent=app)
        kill_timer.timeout.connect(lambda: kill(ppid))
        kill_timer.start(200)

    return main_window_, functools.partial(common_teardown, app_core)


def start_cli_application(app, args, sys_args):
    if args.version:
        print('{} {}'.format(
            version.application_name(),
            version.version))
        return common.return_value('success')

    documentation = args.generate_docs

    if documentation:
        pass

    elif args.filename:
        if os.path.basename(args.filename) == '-':
            pass
        elif not os.path.isfile(args.filename):
            common.print_error('no_such_file')
            return common.return_value('no_such_file')

    app_core, exe_core = common_setup(app, args)

    cli = cli_application.Application(app, app_core, args)
    QtCore.QTimer.singleShot(0, cli.started)
    ppid = settings.instance()['task_manager_pid']
    if ppid:
        kill_timer = QtCore.QTimer(parent=app)
        kill_timer.timeout.connect(lambda: kill(ppid))
        kill_timer.start(200)

    try:
        return app.exec_()
    finally:
        common_teardown(app_core)


def _named_application():
    try:
        app = QtCore.QCoreApplication([])
    except RuntimeError:
        app = QtCore.QCoreApplication.instance()

    app.setApplicationName(version.application_name())
    app.setApplicationVersion(version.version)
    return app


def extract_lambdas(filenames, datatype, env, lib, folders, identifier):
    app = _named_application()

    for key, value in folders.items():
        settings.instance()['{}_folder'.format(key)] = value

    features = feature.available_features()

    with contextlib.ExitStack() as stack:

        for f in features:
            manager = f.worker()
            stack.enter_context(manager)

        app_core, exe_core = basic_setup(app)
        app_core.set_library_dict(lib)

        result = []
        application = cli_application.LambdaExtractorApplication(
            app, app_core, exe_core, filenames, identifier, env, result)
        QtCore.QTimer.singleShot(0, application.run)
        app.exec_()
    return result


def clear(session=False, storage=False):
    app = _named_application()  # NOQA
    if session:
        print('Clearing sessions in:', util.sessions_folder())
        try:
            util.remove_sessions_folder()
        except OSError:
            # Nothing to do, assuming not existing.
            pass
    if storage:
        print('Clearing caches in:', util.storage_folder())
        try:
            util.remove_storage_folders()
        except OSError:
            # Nothing to do, assuming not existing.
            pass

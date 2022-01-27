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
import os
import sys
import datetime
import logging

import time

from sympathy.platform import version_support as vs
from sympathy.platform import exceptions
from sympathy.app import common
from sympathy.app import messages
from sympathy.app import filename_manager as fm
from sympathy.app.environment_variables import instance as env_instance
from sympathy.app import settings
from sympathy.app import credentials
from sympathy.app import user_statistics
from sympathy.app.util import check_requires
import sympathy.app.flow
from sympathy.utils import log

from Qt import QtCore

core_logger = log.get_logger('core')
node_logger = log.get_logger('node')

LOCALHOST = '127.0.0.1'


def log_sep(raw, level):
    if node_logger.isEnabledFor(level):
        print(raw, end='', file=sys.stderr)


class Application(QtCore.QObject):
    """CLI Application"""
    quit = QtCore.Signal()
    results = QtCore.Signal(dict)

    def __init__(self, app, app_core, args, parent=None):
        parent = parent or app
        super(Application, self).__init__(parent)
        self._node_uuid_label_map = {}
        self._app = app
        self._app_core = app_core
        self._args = args
        self._flow = None
        self._error = False
        self._cwd = os.getcwd()
        self._t0 = time.time()
        self._connect()
        self._message_id = None
        self._next_action = None
        self._app_core.reload_node_library()

        for msg in check_requires():
            self.print_display_message(msg)

    def _connect(self):
        self._app_core.all_execution_has_finished.connect(self.finalize)
        self._app_core.display_message_received[messages.DisplayMessage].connect(
            self.print_display_message)
        self._app_core.node_library_output[messages.DisplayMessage].connect(
            self.print_display_message)
        self._app_core.node_progress[
            sympathy.app.flow.NodeInterface, float].connect(
            self.print_progress_message)

    def set_flow(self, flow_filename):
        self._flow_filename = flow_filename

    @QtCore.Slot()
    def started(self):
        self._app_core.interface_started()
        return self.run()

    def run(self):
        if self._args.generate_docs:
            docs_output_dir = None
            docs_library_dir = None
            if self._args.docs_output_dir:
                docs_output_dir = os.path.normpath(self._args.docs_output_dir)

                if os.path.isfile(docs_output_dir):
                    print('Could not generate documentation in '
                          'specified output dir, it is an existing file')
                    return self._app.exit(common.return_value('error'))
                elif os.path.isdir(docs_output_dir):
                    for _, dirnames, filenames in os.walk(docs_output_dir):
                        if dirnames or filenames:
                            print('Could not generate documentation in '
                                  'specified output dir, it exists and is '
                                  'non-empty.')
                            return self._app.exit(common.return_value('error'))
            if self._args.docs_library_dir:
                docs_library_dir = os.path.normpath(self._args.docs_library_dir)

            excluded_exts = []
            if self._args.docs_exclude_code_links:
                excluded_exts = ['sphinx.ext.viewcode']

            try:
                self._app_core.reload_documentation(
                    library=docs_library_dir,
                    output_folder=docs_output_dir,
                    excluded_exts=excluded_exts)
            except Exception as e:
                print("Error:", e)
                return self._app.exit(common.return_value('error'))

            return self._app.exit(common.return_value('success'))

        else:
            if self._args.filename is None:
                return self._app.exit(common.return_value('success'))

            common.hash_support(self._app, self._app_core)
            common.log_environ(self._app, self._app_core)

            QtCore.QTimer.singleShot(0, self.build_flows)

    @QtCore.Slot()
    def finalize(self):
        if self._flow:
            user_statistics.user_closed_workflow(self._flow)

        self._flow.abort()
        if self._error:
            nodes = self._flow.node_set_list(remove_invalid=False)
            if any([
                    node for node in nodes
                    if sympathy.app.flow.Type.is_node(node)
                    and node.is_queued()]):
                core_logger.info('Flow executed with error')
                self._process_exit(common.return_value('queued_nodes'))
            else:
                core_logger.info('Flow executed with error')
                self._process_exit(common.return_value('workflow_error'))
        else:
            # Note: This exact line is matched for in
            # sympathy.test.run_workflow, so if changed it also needs to be
            # updated there.
            core_logger.info(
                'Flow successfully executed in %ss', time.time() - self._t0)

            if self._next_action:
                self._next_action()
            else:
                self._process_exit(common.return_value('success'))

    def build_flows(self):
        self._error = False
        self._t0 = time.time()

        if vs.decode(os.path.basename(
                self._args.filename), vs.fs_encoding) == '-':
            self._next_action = self._wait_for_stdin_filename
            self._next_action()
        elif self._args.filename is not None:
            filename = os.path.abspath(self._args.filename)
            self.set_flow(filename)
            core_logger.info('Using flow: {}'.format(filename))

            try:
                self.build_flow()
            except exceptions.ReadSyxFileError:
                common.print_error('corrupt_workflow')
                self._process_exit(common.return_value('corrupt_workflow'))

    def _wait_for_stdin_filename(self):
        self._t0 = time.time()
        try:
            filename = sys.stdin.readline()
            filename = filename.strip()

            if not filename:
                self._process_exit(common.return_value('success'))
            else:
                os.chdir(self._cwd)
                self.set_flow(os.path.abspath(filename))
                try:
                    self.build_flow()
                except exceptions.ReadSyxFileError:
                    common.print_error('corrupt_workflow')
                    self._process_exit(
                        common.return_value('corrupt_workflow'))
        except Exception:
            common.print_error('corrupt_workflow')
            self._process_exit(common.return_value('corrupt_workflow'))

    @QtCore.Slot()
    def build_flow(self):
        core_logger.info(
            'Start processing flow: %s', self._flow_filename)

        os.chdir(self._cwd)
        self._update_environment()
        self._flow = common.load_flow_from_file(
            self._app_core, self._flow_filename)
        user_statistics.user_opened_workflow(self._flow)

        # Wait until all nodes have been validated.
        self.wait_for_pending()

    def wait_for_pending(self):
        if self._flow.has_pending_request():
            QtCore.QTimer.singleShot(100, self.wait_for_pending)
        else:
            self.execute_all()

    @QtCore.Slot()
    def execute_all(self):
        nodes = self._flow.node_set_list(remove_invalid=False)
        executable = all(node.is_executable() for node in nodes
                         if sympathy.app.flow.Type.is_node(node))

        if not executable:
            common.print_error('invalid_nodes')
            self._process_exit(common.return_value('invalid_nodes'))

        elif not nodes:
            common.print_error('empty_workflow')
            self._process_exit(common.return_value('empty_workflow'))
        else:
            self._flow.execute_all_nodes()

    def _update_environment(self):
        env = env_instance()
        settings_ = settings.instance()
        env_vars = settings_['environment']
        env.set_global_variables(
            dict([env_var.split('=', 1) for env_var in env_vars]))

    def _process_exit(self, exitcode):
        self._app.exit(exitcode)

    @QtCore.Slot(sympathy.app.flow.NodeInterface, float)
    def print_progress_message(self, node, message):
        self._message_id = None
        formatted_message = '{} MESSAGE {} {}'.format(
            datetime.datetime.isoformat(datetime.datetime.today()),
            node.full_uuid, message)

        log_sep('\n', logging.DEBUG)
        node_logger.debug(formatted_message)

    def _log_output_header(self, source, category):
        timestring = datetime.datetime.isoformat(datetime.datetime.today())

        log_sep('\n', logging.INFO)
        formatted_message = '{} {} {}'.format(
            common.BLUE(timestring),
            category,
            common.WHITE(source))

        node_logger.info(formatted_message)

    @QtCore.Slot(messages.DisplayMessage)
    def print_display_message(self, message, category='OUTPUT'):

        level = message.level()
        message_id = message.id()
        current_id = self._message_id == message_id

        if level in [messages.Levels.error, messages.Levels.exception]:

            # TODO(erik): questionable design: flag set by print determines
            # process exit code. Tracking node execution status would be
            # better.
            self._error = True

            text = message.brief()
            details = message.details()
            if details:
                text = details

            if text:
                category = level.value.upper()

                timestring = datetime.datetime.isoformat(
                    datetime.datetime.today())

                formatted_message = common.RED(text)
                formatted_message = '{} {} {}\n{}'.format(
                    common.BLUE(timestring),
                    category,
                    common.WHITE(message.source()),
                    formatted_message)

                node_logger.info(formatted_message)
        else:
            if (not current_id) and level in [
                    messages.Levels.notice, messages.Levels.warning]:
                self._log_output_header(message.source(), category)

            self.print_node_output_no_banner(message.brief())

        self._message_id = message_id

    @QtCore.Slot(str, dict)
    def print_node_output_no_banner(self, output):
        log_sep(output, logging.INFO)


class LambdaExtractorApplication(Application):
    def __init__(self, app, app_core, exe_core, filenames, identifier, env,
                 result, parent=None):
        parent = parent or app
        super(Application, self).__init__(parent)
        self._node_uuid_label_map = {}
        self._app = app
        self._app_core = app_core
        self._exe_core = exe_core
        self._filenames = filenames
        self._identifier = identifier
        self._current_filename = None
        self._env = env
        # Input output parameter result.
        self._result = result
        self._result_dict = {}

        self._connect()

    def build_flows(self):
        filenames = self._filenames

        try:
            fm.instance().set_prefix(self._identifier)
            env = env_instance()
            env.set_from_dict(self._env)
        except:
            for filename in filenames:
                self._result_dict[filename] = (False, 'Global extract failure')
            filenames = []

        try:
            self._app_core.set_reload_node_library_enabled(False)
            for filename in filenames:
                self._current_filename = filename
                try:
                    self._flow = common.load_flow_from_file(
                        self._app_core, filename, validate=False)
                    self._result_dict[filename] = (True, self._flow)
                except:
                    self._result_dict[filename] = (False, 'Could not read file')
        finally:
            self._app_core.set_reload_node_library_enabled(True)

        self._result[:] = [(filename, self._result_dict[filename])
                           for filename in filenames]
        self._app.quit()

    def run(self):
        QtCore.QTimer.singleShot(0, self.build_flows)

    @QtCore.Slot(messages.DisplayMessage)
    def print_display_message(self, message):
        def print_with_path(path, data, file=sys.stdout):
            data = (data or '').strip()
            if data:
                print(path, ':', '\n', data, file=file, sep='')

        if message.level() == messages.Levels.error:
            self._result_dict[self._current_filename] = (False, 'Error')
        if message.level() == messages.Levels.exception:
            self._result_dict[self._current_filename] = (False, 'Exception')

        flode = message.node()
        if flode is None:
            return
        paths = [flode.name]
        parent = flode.flow
        while parent is not None:
            paths.append(parent.name)
            parent = parent.flow
        path = ' > '.join(reversed(paths))
        if message.level() == messages.Levels.notice:
            print_with_path(path, message.brief(), file=sys.stdout)
        if message.level() == messages.Levels.warning:
            print_with_path(path, message.brief(), file=sys.stderr)

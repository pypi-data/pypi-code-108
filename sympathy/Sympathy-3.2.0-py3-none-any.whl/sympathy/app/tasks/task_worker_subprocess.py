# This file is part of Sympathy for Data.
# Copyright (c) 2013-2016 Combine Control Systems AB
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
Sympathy worker used to start Sympathy Python worker processes.
"""
import locale
import os
import sys
import json
import base64
import tempfile
import sqlite3
import cProfile as profile
import copy
import io
import dask
import warnings
import contextlib

from Qt import QtCore, QtWidgets
from sympathy.utils.prim import uri_to_path
from sympathy.utils import network
from sympathy.platform import state
from sympathy.platform import node_result
from sympathy.platform import os_support
from sympathy.platform import parameter_helper
from sympathy.platform import editor as editor_api
from sympathy.platform import types
from sympathy.platform import message_util
from sympathy.app import builtin
from sympathy.app.config_aggregation import (
    ConfigurationAggregation, clean_flow_info)


pid = os.getpid()
_debug_worker_global = {}


def set_high_dpi_unaware():
    os_support.set_high_dpi_unaware()


def setup_qt_opengl():
    os_support.setup_qt_opengl()


def write_run_config(filename, *args):
    def quote(filename):
        return filename.replace('\\', '\\\\')

    arguments = base64.b64encode(
        json.dumps(args).encode('ascii')).decode('ascii')
    source_file = args[0]
    data_filename = '{}.data.py'.format(filename)
    run_filename = '{}.run.py'.format(filename)
    run_config_string = """# -*- coding: utf-8 -*-
import sys
import os
import base64
import json
argumentsb64 = b'{arguments}'
arguments = json.loads(
    base64.b64decode(argumentsb64).decode('ascii'))
sys.path[:] = arguments[9]
sys.path.append('{file_dir}')
from sympathy.app.tasks.task_worker_subprocess import debug_worker, _debug_worker_global
""".format(arguments=str(arguments), file_dir=quote(__file__))
    with io.open(data_filename, 'w', encoding='utf8') as run_config:
        run_config.write(run_config_string)

    with io.open(run_filename, 'w', encoding='utf8') as run_config:
        run_config.write("""# -*- coding: utf-8 -*-
exec(open(u'{data_filename}').read())
dnc = debug_node_context = debug_worker(
    _debug_worker_global, *arguments).open()
""".format(data_filename=quote(data_filename)))

    try:
        dbpath = os.path.join(tempfile.gettempdir(),
                              'sympathy_1.1.dbg.sqlite3')
        conn = sqlite3.connect(dbpath)
        conn.execute(
            'CREATE TABLE if not exists dbg (src text PRIMARY KEY, dst text)')
        conn.execute('insert or replace into dbg values (?, ?)',
                     (uri_to_path(source_file), run_filename))
        conn.commit()
    finally:
        conn.close()


def load_typealiases(typealiases):
    if typealiases:
        for key, value in typealiases.items():
            types.manager.add_load_typealias(key, value)
            utilmod = value['util'].split(':')[0]
            __import__(utilmod)
        types.manager.load_typealiases()


def _write_result_close(socket, data):
    network.send_all(socket, data)


class PrintErrorApplication(QtWidgets.QApplication):

    def __init__(self, argv):
        super().__init__(argv)

    # TODO(erik): Overriding notify resulted in hard crash when creating node
    # configuration using QtWebEngineWidgets.QWebEngineView(). Tested on
    # PySide2==5.11.2, MacOS 10.13.6, 2018-09-26.
    # The override may not be needed anymore.
    #
    # def notify(self, obj, evt):
    #     try:
    #         return super().notify(obj, evt)
    #     except:
    #         traceback.print_exc(file=sys.stderr)
    #         return False


class DebugNodeContextManager(object):

    def __init__(self, node, typealiases, parameters,
                 library_dirs, application_dir, session_dir, python_paths,
                 debug_state, node_settings):
        self._node = node
        self._typealiases = typealiases
        self._parameters = parameters
        self._library_dirs = library_dirs
        self._application_dir = application_dir
        self._session_dir = session_dir
        self._python_paths = python_paths
        self._gens = []
        self._debug_state = debug_state
        self._node_settings = node_settings

    def open(self):
        with state.state():
            try:
                state.node_state().create(
                    library_dirs=self._library_dirs,
                    application_dir=self._application_dir,
                    session_dir=self._session_dir,
                    support_dirs=self._python_paths,
                    node_settings=self._node_settings)

                node_context = self._node._build_node_context(
                    self._parameters,
                    self._typealiases,
                    read_only=True)
                input_fileobjs = [input for input in node_context.input]
                output_fileobjs = [output for output in node_context.output]

                self._fileobjs = input_fileobjs + output_fileobjs
                return self._node.update_node_context(
                    node_context,
                    input_fileobjs,
                    output_fileobjs,
                    parameters=parameter_helper.ParameterRoot(
                        node_context.parameters))
            finally:
                self._debug_state['opened'] = self
                self._debug_state['state'] = state.node_state()

    def close(self):
        try:
            for fileobj in reversed(self._fileobjs):
                fileobj.close()
        except TypeError:
            pass

        self._debug_state['state'].clear()
        self._debug_state['opened'] = None
        self._debug_state['state'] = None


def debug_worker(debug_state, source_file, library_dirs, class_name,
                 identifier,
                 json_parameters, type_aliases, action,
                 log_fq_filename, environ, path, python_paths, application_dir,
                 session_dir, working_dir, node_settings, worker_settings):
    os.chdir(working_dir)
    os.environ.update(environ)
    opened = debug_state.get('opened', None)
    if opened:
        opened.close()

    with state.state():

        try:
            mod = builtin.source_module(source_file)
            node = getattr(mod, class_name)()
            state.node_state().create(library_dirs=library_dirs,
                                      application_dir=application_dir,
                                      session_dir=session_dir,
                                      support_dirs=python_paths,
                                      worker_settings=worker_settings,
                                      node_settings=node_settings)

            type_aliases = type_aliases
            parameters = json.loads(json_parameters)
            load_typealiases(type_aliases)

            if action == 'execute':
                node._sys_execute(parameters, type_aliases)
            return DebugNodeContextManager(
                node, type_aliases, parameters, library_dirs, application_dir,
                session_dir, python_paths, debug_state, node_settings)
        finally:
            state.node_state().clear()


def _reset_warnings():
    for mod in list(sys.modules.values()):
        try:
            mod.__warningregistry__.clear()
        except AttributeError:
            pass


@contextlib.contextmanager
def nullcontext(obj=None):
    # Startings with Python 3.7 contextlib.nullcontext can be used instead.
    yield obj


def worker(io_bundle, nocapture, action, *args, **kwargs):
    """
    Interface function to switch between different specialized workers.
    """
    try:
        from sklearn.utils import parallel_backend as skl_backend
    except ImportError:
        skl_backend = nullcontext

    state.node_state().set_attributes(capture_output=not nocapture)

    try:
        # Dask >= 0.18.
        dask_config = dask.config.set(scheduler='single-threaded')
    except AttributeError:
        dask_config = dask.set_options(get=dask.local.get_sync)

    _reset_warnings()

    with warnings.catch_warnings(), dask_config, skl_backend('threading'):
        # TODO(erik): unify interfaces so that node worker (or at least one
        # single interface) can be called for both types.
        # This would reduce some setup code duplication.
        if action == 'aggregated_parameter_view':
            return aggregated_parameter_view_worker(
                io_bundle, action, *args, **kwargs)
        else:
            node_worker(
                io_bundle, action, *args, **kwargs)


SocketBundle = builtin.SocketBundle


def setup_socket(iobundle, blocking):
    iobundle.socket.setblocking(blocking)
    return iobundle.socket


def _check_for_unsupported_qt():
    res = None
    for mod in ['PyQt4', 'PyQt4.QtCore',
                'PyQt5', 'PyQt5.QtCore',
                'PySide', 'PySide.QtCore']:
        if mod in list(sys.modules):
            res = mod
            break
    return res


def _warn_for_unsupported_qt(unsupported_qt):
    if unsupported_qt is None:
        # We support having both PySide2 and PyQt5 in the same python
        # environment. However, we must ensure that PyQt5 is not loaded in the
        # worker process itself, since this may cause all sorts of
        # problems. Subprocesses can be used work around this limitation to
        # encapsulate PyQt5.
        unsupported_qt = _check_for_unsupported_qt()
        if unsupported_qt:
            print('WARNING: node imported an unsupported Qt framework. This '
                  f'node made use of {unsupported_qt}, but '
                  'only PySide2 is supported, please contact the developer of '
                  'the node or plugin causing this.',
                  file=sys.stderr)


def _execute_node(node, parameters, typealiases, context, result,
                  capture_output):
    node._sys_before_execute()
    node._sys_execute(parameters, typealiases)
    node._sys_after_execute()
    builtin.store_stdouterr(result, context, capture_output)


def node_worker(io_bundle, action, source_file, class_name,
                identifier, json_parameters, type_aliases, working_dir,
                node_settings, environ,
                library_dirs, path, python_paths,
                application_dir, session_dir,
                worker_settings,
                log_fq_filename):
    """
    Internal function called by the Sympathy platform to start
    Python processes where the node will execute.

    The returned value is a dictionary with the two following keys:
        exception_string = '' if valid is True and a string representation
            of the Exception otherwise.
        exception_trace = [] if valid is True and a list of strings
            containing the exception trace otherwise.
        output = None, on complete failure and otherwise depending on
            action. Every action has a default value and which will
            be used for the result in the exception case.
        stdout = String containing captured stdout.
        stderr = String containing captured stderr.
        valid = True if no unhandled Exception occured False otherwise.
    """
    os.environ.update(environ)
    sys.path[:] = path
    os.chdir(working_dir)
    had_unsupported_qt = _check_for_unsupported_qt()
    context = {}
    capture_output = state.node_state().attributes['capture_output']
    result = node_result.NodeResult()

    application = None
    reader = None
    if action in ['execute_parameter_view', 'execute_port_viewer']:
        # Must create QApplication before socket to ensure that events
        # can be handled by the Eventloop.
        os_support.set_application_id()
        application = PrintErrorApplication([])  # NOQA
        QtCore.QLocale.setDefault(QtCore.QLocale('C'))
        socket = setup_socket(io_bundle, False)
        reader = message_util.SocketMessageCommunicator(socket)
    else:
        socket = setup_socket(io_bundle, True)

    socket_bundle = SocketBundle(
        socket, io_bundle.input_func, io_bundle.output_func, reader)

    builtin.capture_stdouterr(
        context, capture_output, socket_bundle, state.Node(identifier))
    try:
        state.node_state().create(library_dirs=library_dirs,
                                  application_dir=application_dir,
                                  session_dir=session_dir,
                                  support_dirs=python_paths,
                                  worker_settings=worker_settings,
                                  node_settings=node_settings)

        result = state.node_state().result
        parameters = json.loads(json_parameters)
        load_typealiases(type_aliases)
        mod = builtin.source_module(source_file)
        node = getattr(mod, class_name)()._future__init__(
            identifier=identifier,
            definition=parameters, socket_bundle=socket_bundle)
        # name = node.name

        if action == 'execute':
            _execute_node(node, parameters, type_aliases, context, result,
                          capture_output)

            with io.open(log_fq_filename, 'w', encoding='utf8') as out_file:
                out_file.write(result.format_std_output())
        elif action == 'profile':  # => 'execute'
            clean_identifier = ''.join(
                [c for c in identifier if c not in '{}'])
            stat_fq_filename = os.path.join(session_dir, '{}_{}.stat'.format(
                class_name, clean_identifier))
            result.output = ''
            # The code should be the same as performed in the 'execute' case,
            # the reason for not using a function here is to avoid adding an
            # extra level to tracebacks etc (there are already so many before
            # the user's node execute starts).
            prof = profile.Profile()
            prof.runcall(
                _execute_node, node, parameters, type_aliases, context, result,
                capture_output)
            prof.dump_stats(stat_fq_filename)
        elif action == 'debug':  # => 'execute'
            clean_identifier = ''.join(
                [c for c in identifier if c not in '{}'])
            log_fq_filename = os.path.join(session_dir, '{}_{}.log'.format(
                class_name, clean_identifier))
            run_fq_filename = os.path.join(session_dir, '{}_{}'.format(
                class_name, clean_identifier))

            write_run_config(
                run_fq_filename,
                source_file, library_dirs, class_name, identifier,
                json_parameters,
                type_aliases, 'execute',
                log_fq_filename, environ, path, python_paths, application_dir,
                session_dir, working_dir, node_settings, worker_settings)

            if editor_api.debug_file(filename=uri_to_path(source_file)) is False:
                # TODO(erik): stdoe and exceptions are not propagated.
                print('Editor plugin which can debug is not installed.')

        elif action == 'validate_parameters':
            result.output = False
            result.output = node._sys_verify_parameters(
                parameters, type_aliases)
        elif action == 'execute_parameter_view':
            result.output = json_parameters
            result.output = json.dumps(node._sys_exec_parameter_view(
                parameters, type_aliases))
        elif action == 'test_parameter_view':
            result.output = json_parameters
            node._sys_exec_parameter_view(
                parameters, type_aliases, return_widget=True)
        elif action == 'execute_port_viewer':
            result.output = True
            node.exec_port_viewer(parameters)
            builtin.store_stdouterr(result, context, capture_output)
        elif action == 'adjust_parameters':
            assert False, 'Can this be removed?'
            result.output = json_parameters
            result.output = json.dumps(node._sys_adjust_parameters(
                parameters, type_aliases))
        elif action == 'execute_library_creator':
            libraries, temp_dir = parameters
            create_result = node.create(
                libraries, temp_dir, session_dir)
            builtin.store_stdouterr(result, context, capture_output)
            result.output = create_result
        else:
            print('Unsupported node action requested.')

        created_qapplication = QtCore.QCoreApplication.instance()
        if application:
            if application.clipboard().ownsClipboard():
                os_support.flush_clipboard()
        elif created_qapplication:
            print('WARNING: node created a QApplication, this will cause hard '
                  'crashes in worker processes. Please refrain from creating '
                  'QApplications except in separate subprocesses, '
                  'using matplotlib.pyplot in F(x) is a frequent cause.',
                  file=sys.stderr)

        _warn_for_unsupported_qt(had_unsupported_qt)
    except:  # NOQA
        result.valid = False
        result.store_current_exception(source_file)
    finally:
        state.node_state().clear()

    builtin.store_stdouterr(result, context, capture_output)
    builtin.restore_stdouterr(context, capture_output)
    result.stdout_limit = worker_settings.get('max_task_chars')
    result.stderr_limit = worker_settings.get('max_task_chars')
    if log_fq_filename:
        result.limit_footer = 'Wrote full output to: {}.'.format(
            log_fq_filename)

    _write_result_close(socket, io_bundle.result_func(result))


def aggregated_parameter_view_worker(
        io_bundle, action, conf, identifier, json_flow_info, type_aliases,
        working_dir, environ,
        library_dirs, path, python_paths,
        application_dir, session_dir,
        worker_settings):

    os.environ.update(environ)
    os_support.set_application_id()
    sys.path[:] = path
    had_unsupported_qt = _check_for_unsupported_qt()
    os.chdir(working_dir)
    context = {}
    capture_output = state.node_state().attributes['capture_output']
    result = node_result.NodeResult()
    result.output = json_flow_info

    def add_instances(x, socket_bundle):
        for key, value in x.items():
            if key == 'nodes':
                for node_info in value:
                    source_file = node_info['source_file']
                    class_name = node_info['class_name']
                    node_dict = json.loads(node_info['json_node_dict'])
                    identifier = node_info['uuid']
                    if source_file:
                        mod = builtin.source_module(source_file)
                        node_instance = getattr(mod, class_name)()._future__init__(
                            identifier=identifier,
                            definition=node_dict, socket_bundle=socket_bundle)
                        # Extra payload.
                        node_info['library_node_instance'] = node_instance
            elif key == 'flows':
                for flw in value:
                    add_instances(flw, socket_bundle)

    application = PrintErrorApplication([])  # NOQA
    socket = setup_socket(io_bundle, False)
    reader = message_util.SocketMessageCommunicator(socket)
    socket_bundle = SocketBundle(
        socket, io_bundle.input_func, io_bundle.output_func, reader)

    builtin.capture_stdouterr(
        context, capture_output, socket_bundle, state.Node(identifier))

    # TODO: Move to top level when shiboken is no longer being imported.

    try:
        state.node_state().create(library_dirs=library_dirs,
                                  application_dir=application_dir,
                                  session_dir=session_dir,
                                  support_dirs=python_paths,
                                  worker_settings=worker_settings)
        load_typealiases(type_aliases)

        flow_info = json.loads(json_flow_info)

        # Store flow info without instances.
        old_flow_info = copy.deepcopy(flow_info)

        # Manage modifications to flow_info automatically.
        # with node_instances(flow_info) as modified_flow_info:
        add_instances(flow_info, socket_bundle)
        aggregator = ConfigurationAggregation(conf,
                                              socket_bundle,
                                              flow_info,
                                              type_aliases)
        accept = aggregator.run()
        aggregator = None
        del aggregator
        flow_info = clean_flow_info(flow_info)

        if accept:
            result.output = json.dumps(flow_info)
        else:
            result.valid = False
            result.output = json.dumps(old_flow_info)

        if application.clipboard().ownsClipboard():
            os_support.flush_clipboard()

        _warn_for_unsupported_qt(had_unsupported_qt)
    except:  # NOQA
        result.valid = False
        result.store_current_exception()
    finally:
        state.node_state().clear()

    builtin.store_stdouterr(result, context, capture_output)
    builtin.restore_stdouterr(context, capture_output)

    result.stdout_limit = worker_settings.get('max_task_chars')
    result.stderr_limit = worker_settings.get('max_task_chars')
    _write_result_close(socket, io_bundle.result_func(result))


def main():
    json_parent_context = sys.argv[-1]
    parent_context = json.loads(json_parent_context)
    os.environ.update(parent_context['environ'])
    sys.path[:] = parent_context['sys.path']
    result = worker(*sys.argv[1:-1])
    sys.stdout.write(json.dumps(result,
                                encoding=locale.getpreferredencoding()))


if __name__ == '__main__':
    main()

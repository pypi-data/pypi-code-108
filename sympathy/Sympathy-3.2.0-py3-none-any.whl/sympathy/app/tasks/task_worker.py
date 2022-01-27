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
Sympathy worker used to start Sympathy Python worker processes.
"""
import os
import contextlib
import sys

import Qt.QtNetwork as QtNetwork

from .. import util
from .. import settings
from . import task_worker2
from sympathy.platform import message_util
import sympathy.platform.library


_client = None


def _client_instance():
    global _client
    if _client is None:
        _client = TaskClient()
        _client.setup()
    return _client


class TaskClient(message_util.MessageReader):

    def __init__(self, parent=None):
        self._next_taskid = 0
        qiodev = QtNetwork.QTcpSocket()
        qiodev.setSocketOption(
            QtNetwork.QAbstractSocket.SocketOption.KeepAliveOption, True)
        super().__init__(qiodev, parent=parent)

    def setup(self):
        try:
            port = settings.instance()['task_manager_port']
        except KeyError:
            # Not set when in extract mode.
            pass
        else:
            self._qiodev.connectToHost('127.0.0.1', port)
            if self._qiodev.waitForConnected():
                pass

    def _read(self):
        # TODO(erik): this code overrides parent class implementation and
        # suppresses building of message objects, returning raw data.
        # It would be better to cover all kinds of messages here and return
        # objects (Message, NodeResult) instead of raw data. NodeResult could
        # be made a Message subclass if it would help.
        data = self._qiodev.readAll().data()
        lines = task_worker2.datalines(data, self._buf)
        msgs = [task_worker2.decode_json(line) for line in lines]
        return msgs

    def read(self):
        return self._read()

    def add_task(self, data, quit_after):
        taskid = self._next_taskid
        yield taskid
        self._next_taskid += 1
        cmd = (task_worker2.NEW_QUIT_TASK
               if quit_after
               else task_worker2.NEW_TASK)
        msg = [taskid, cmd, data]
        self._qiodev.write(task_worker2.encode_json(msg) + b'\n')

    def abort_task(self, taskid):
        msg = [taskid, task_worker2.ABORT_TASK, None]
        self._qiodev.write(task_worker2.encode_json(msg) + b'\n')

    def update_task(self, taskid, data):
        msg = [taskid, task_worker2.UPDATE_TASK, data]
        self._qiodev.write(task_worker2.encode_json(msg) + b'\n')

    def set_workers(self, nworkers=None):
        msg = [None, task_worker2.SET_WORKERS_TASK, nworkers]
        self._qiodev.write(task_worker2.encode_json(msg) + b'\n')

    @contextlib.contextmanager
    def await_done(self, task):
        taskid = next(task)
        for _ in task:
            pass

        self.set_block(True)
        wait_msgs = []
        update_msgs = []
        done = False
        while not done:
            self.wait(-1)
            msgs = iter(self.read())
            for msg in msgs:
                taskid_, cmd, data = msg
                if taskid_ == taskid and cmd == task_worker2.DONE_TASK:
                    done = True
                    wait_msgs.extend(msgs)
                    yield (msg, update_msgs)
                    break
                if taskid_ == taskid and cmd == task_worker2.UPDATE_TASK:
                    update_msgs.append(msg)
                else:
                    wait_msgs.append(msg)
            wait_msgs.extend(msgs)
        if wait_msgs:
            self.received.emit(wait_msgs)
        self.set_block(False)

    def close(self):
        self._qiodev.close()


def create_client():
    return _client_instance()


def close_client():
    _client_instance().close()


class ProcessError(Exception):
    def __init__(self, status):
        self.status = status
        super().__init__('')

    def __str__(self):
        return 'Failed with code {}'.format(self.status)


def set_workers(workers):
    """
    Create the requested number of workers after terminating any existing
    workers. It is important to make sure that no tasks are in the air
    before this function is called. This can be assured by waiting for
    tasks to complete or by aborting them. Setting workers to the same
    number essentially performs a worker restart.
    """
    _client_instance().set_workers(workers)


class Paths(object):
    """Convenience class for accessing paths in the desired format."""
    def __init__(self, install_path=None):
        self._install_path = install_path

    def install_path(self):
        return (self._install_path or
                settings.instance()['install_folder'])

    def python_paths(self):
        return util.python_paths()

    def support_paths(self):
        return []

    def library_paths(self):
        return util.library_paths()

    def common_paths(self):
        result = []
        for library in self.library_paths():
            result.append(sympathy.platform.library.package_python_path(library))
        return result

    def environ(self):
        return os.environ

    def sys_path(self):
        return list(sys.path)


paths = Paths()


def common_env():
    python_paths = paths.python_paths()
    common_paths = paths.common_paths()
    support_paths = paths.support_paths()
    settings_ = settings.get_worker_settings()
    return (
        dict(paths.environ().items()),
        paths.library_paths(),
        (paths.sys_path() + python_paths + support_paths +
         common_paths),
        python_paths + support_paths + common_paths,
        settings.instance()['install_folder'],
        settings.instance()['session_folder'],
        settings_)


def worker(action, log_fq_filename, quit_after=False):
    """Internal function called by the Sympathy platform to start
    Python processes where the node will execute.
    """
    return _base_worker(
        (action + common_env() + (log_fq_filename,)),
        quit_after)


def worker_light(action):
    """Internal function called by the Sympathy platform to wrap Python
    function calls in order to intercept exceptions, stdout and stderr.
    """
    return worker(action + common_env(), None, quit_after=False)


def library_creator_worker(action, library_path=None, python_paths=None,
                           quit_after=True):
    """Internal function called by Sympathy for Data platform to start a Python
    process which runs the library creator for a specific library."""
    env = common_env()

    if library_path is not None:
        # Use relevant paths for selected library instead of those in
        # common_env:
        python_paths = python_paths or []
        common_path = os.path.join(library_path, 'Common')
        env = list(env)
        env[1] = [library_path]
        env[2] = (paths.sys_path()
                  + python_paths
                  + paths.support_paths()
                  + [common_path])
        env = tuple(env)

    return _base_worker(
        (action + env + (None,)), quit_after)


def aggregated_parameter_view_worker(action, quit_after=True):
    """Internal function called by Sympathy for Data platform to show
    aggregated parameter views for a flow."""
    return _base_worker(
        action + common_env(), quit_after)


def _base_worker(arguments, quit_after=True):
    return iter(_client_instance().add_task(arguments, quit_after))


def abort_task(taskid):
    _client_instance().abort_task(taskid)


def await_done(taskid):
    return _client_instance().await_done(taskid)


def update_task(taskid, data):
    return _client_instance().update_task(taskid, data)

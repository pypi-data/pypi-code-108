# This file is part of Sympathy for Data.
# Copyright (c) 2016 Combine Control Systems AB
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
import signal
import threading
import psutil
import time
import socket


(NEW_TASK, NEW_QUIT_TASK, UPDATE_TASK, QUIT_TASK, ABORT_TASK,
 DONE_TASK, SET_WORKERS_TASK, WORKER_CONNECTED) = range(8)


def readlines_fd(fd, bufl):
    return datalines(os.read(fd, 2048), bufl)


def setup_socket(sock):
    if sock:
        try:
            sock.setsockopt(
                socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        except AttributeError:
            pass
        try:
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        except AttributeError:
            pass


class CommunicationHelper(object):

    def __init__(self, port, worker_id, socket, taskid, msg_reader, file_obj):
        # Port and worker_id might be useful to format temporary debug
        # messages.
        self._port = port
        self._worker_id = worker_id
        self._socket = socket
        self._taskid = taskid
        self._msg_reader = msg_reader
        self._file_obj = file_obj

    @property
    def socket(self):
        return self._socket

    def output_func(self, msg):
        """
        Format an update message for sending to output socket.
        """
        return encode_json([self._taskid, UPDATE_TASK, msg.to_dict()]) + b'\n'

    def result_func(self, msg):
        """
        Format a done message for sending to output socket.
        """
        return encode_json([self._taskid, DONE_TASK, msg.to_dict()]) + b'\n'

    def input_func(self):
        return self._msg_reader(self._file_obj)


def killer(ppid):
    while True:
        if not psutil.pid_exists(ppid):
            os.kill(os.getpid(), signal.SIGTERM)
        time.sleep(0.2)


def _conn_func(pid, prev_taskid):
    return encode_json([prev_taskid, WORKER_CONNECTED, pid]) + b'\n'


def worker(function, worker_id, port, ppid, nocapture, stack, features):
    ipipebuf = []
    taskid = -1
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    quit_after = [False]

    def get_msgs():
        lines = readlines_fd(0, ipipebuf)
        return [decode_json(line) for line in lines]

    def read_task(file_obj):
        line = file_obj.readline().rstrip()
        msg = decode_json(line)
        return msg

    def read_update_data(file_obj):
        taskid_new, cmd, data = read_task(file_obj)
        assert cmd == UPDATE_TASK, 'Received unexpected command'
        return data

    killer_thread = threading.Thread(target=killer, args=(ppid,))
    killer_thread.daemon = True
    killer_thread.start()

    quit_after = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", port))
    setup_socket(sock)

    features_initialized = False

    while not quit_after:

        msg_in = None
        try:
            sock.setblocking(True)
            sock.send(_conn_func(worker_id, taskid))
            msg_in = sock.makefile(mode='rb')

            # Get new task, discarding any other messages.
            taskid_new, cmd, data = read_task(msg_in)
            if not features_initialized:
                # TODO(erik):
                # Temporary measure to ensure that platform features are
                # initialized before worker features. For the future, this
                # could instead be handled by launching workers after the
                # platform has started.
                features_initialized = True
                for f in features:
                    stack.enter_context(f.worker())

            while cmd not in [NEW_TASK, NEW_QUIT_TASK]:
                taskid_new, cmd, data = read_task(msg_in)

            quit_after = cmd == NEW_QUIT_TASK
            taskid = taskid_new
            io_bundle = CommunicationHelper(
                port, worker_id, sock, taskid, read_update_data, msg_in)
            function(io_bundle, nocapture, *data)
        finally:
            if msg_in is not None:
                msg_in.close()
                msg_in = None


def datalines(data, bufl):
    i = data.rfind(b'\n')
    if i >= 0:
        bufl.append(data[:i])
        sdata = b''.join(bufl)
        bufl[:] = [data[i + 1:]]
        lines = sdata.split(b'\n')
        return [line.strip() for line in lines]
    else:
        bufl.append(data)
    return []


def decode_json(str_):
    from sympathy.platform.crypto import decode_json
    return decode_json(str_)


def encode_json(dict_):
    from sympathy.platform.crypto import encode_json
    return encode_json(dict_)


def get_msgs(lines):
    return [decode_json(line) for line in lines]


def main():
    import argparse
    import contextlib
    import sys
    from sympathy.app.tasks import task_worker_subprocess
    from sympathy.utils import log
    from sympathy.platform import feature
    from sympathy.platform.os_support import encode_stream
    from sympathy.platform.crypto import init_from_env
    from sympathy.app import version
    from Qt import QtCore
    QtCore.QCoreApplication.setApplicationName(version.application_name())
    QtCore.QCoreApplication.setApplicationVersion(version.version)

    task_worker_subprocess.set_high_dpi_unaware()
    task_worker_subprocess.setup_qt_opengl()

    encode_stream(sys.stdout)
    encode_stream(sys.stderr)

    parser = argparse.ArgumentParser()
    parser.add_argument('worker_id', type=int)
    parser.add_argument('port', type=int)
    parser.add_argument('parent_pid', type=int)
    parser.add_argument('nocapture', type=int)
    parser.add_argument(
        '-L', '--loglevel', nargs='+',
        action=log.LogLevelAction,
        default={},
    )
    (parsed, _) = parser.parse_known_args()
    log.setup_log_levels(parsed.loglevel)

    init_from_env()

    features = feature.available_features()
    with contextlib.ExitStack() as stack:
        worker(
            task_worker_subprocess.worker, parsed.worker_id, parsed.port,
            parsed.parent_pid, parsed.nocapture, stack, features)


if __name__ == '__main__':
    main()

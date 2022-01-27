# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
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
import base64
import json
import os
from Qt import QtCore
from . import message
from . crypto import decode_json


class MessageReader(QtCore.QObject):
    """
    Reads from qtcp socket.
    """
    received = QtCore.Signal(list)

    def __init__(self, qiodev, parent=None):
        super().__init__(parent=parent)
        self._buf = [b'']
        self._qiodev = qiodev
        qiodev.readyRead.connect(self._handle_notifier_activated)

    def _handle_notifier_activated(self):
        msgs = self._read()
        if msgs:
            self.received.emit(msgs)

    def _read(self):
        data = self._qiodev.readAll().data()
        lines = datalines(data, self._buf)
        elems = [decode_json(line) for line in lines]
        msgs = [message.from_dict(elem[2]) for elem in elems]
        return msgs

    def wait(self, time):
        self._qiodev.waitForReadyRead(time)

    def set_block(self, state):
        self._block = self._qiodev.blockSignals(state)


class SocketMessageReader(QtCore.QObject):
    """
    Reads from normal python socket.
    """
    received = QtCore.Signal(list)

    def __init__(self, socket, parent=None):
        super().__init__(parent=parent)
        self._notifier = QtCore.QSocketNotifier(
            socket.fileno(), QtCore.QSocketNotifier.Read, parent=self)
        self._buf = [b'']
        self._socket = socket
        self._notifier.activated.connect(self._handle_notifier_activated)

    def _handle_notifier_activated(self, fd):
        msgs = self._read()
        if msgs:
            self.received.emit(msgs)

    def _read(self):
        lines = []

        try:
            data = self._socket.recv(4096)
            while data:
                lines.extend(datalines(data, self._buf))
                data = self._socket.recv(4096)
        except Exception:
            pass
        elems = [decode_json(line) for line in lines]
        msgs = [message.from_dict(elem[2]) for elem in elems]
        return msgs


class SocketMessageCommunicator(SocketMessageReader):

    def __init__(self, *args, **kwargs):
        self._requests = {}
        super().__init__(*args, **kwargs)

    def _read(self):
        msgs = super()._read()
        if msgs:
            msgs = [msg for msg in msgs if not self._handle_reply(msg)]
        return msgs

    def _handle_notifier_activated(self, fd):
        msgs = self._read()
        if msgs:
            self.received.emit(msgs)

    def _handle_reply(self, msg):
        handled = isinstance(msg, message.ReplyMessage)
        if handled:
            handler = self._requests.pop(msg.request_id, None)
            if handler:
                # Replies with no handler are simply discarded.
                handler(msg.data)
        return handled

    def request(self, msg, handler):
        self._requests[msg.request_id] = handler


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

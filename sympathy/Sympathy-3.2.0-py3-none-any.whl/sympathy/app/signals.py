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
import Qt.QtCore as QtCore
import functools
import collections

from sympathy.utils import log

core_logger = log.get_logger('core')


class SignalHandler(object):
    """
    The SignalHandler is a simple book-keeping class that can be used to
    register, connect and disconnect signals associated with an object.
    """

    def __init__(self):
        self._signals = collections.defaultdict(list)

    def add(self, reference, signal, receiver):
        if (signal, receiver) in self._signals[reference]:
            core_logger.error(
                'Reconnecting signal, ref: {}, sig: {}, rec: {}'.format(
                    reference, signal, receiver))
        self._signals[reference].append((signal, receiver))

    def remove(self, reference, signal, receiver):
        pair = (signal, receiver)
        if reference in self._signals:
            if pair in self._signals[reference]:
                del self._signals[reference][
                    self._signals[reference].index(pair)]

    def _remove_all(self, reference):
        if reference in self._signals:
            del self._signals[reference]

    def connect(self, reference, signal, receiver):
        self.add(reference, signal, receiver)
        success = signal.connect(receiver)
        return success

    def connect_reference(self, reference, connections):
        """
        Convenience method for connecting severall signals
        with the same reference.

        Parameters
        ----------
        reference
            Object used as key for tracking a set of signal connections.
        connections
            Sequence of pairs: signal, receiver.
        """
        for signal, receiver in connections:
            self.connect(reference, signal, receiver)

    def disconnect(self, reference, signal, receiver):
        self.remove(reference, signal, receiver())
        signal.disconnect(receiver)

    def _disconnect_reference(self, reference):
        if reference in self._signals:
            for signal, receiver in self._signals[reference]:
                try:
                    signal.disconnect(receiver)
                except Exception:
                    core_logger.error(
                        'Disconnect failed, ref: {}, sig: {}, rec: {}'.format(
                            reference, signal, receiver))
            self._remove_all(reference)

    def disconnect_all(self, reference=None):
        if reference is not None:
            self._disconnect_reference(reference)
        else:
            all_signals = list(self._signals.keys())
            for ref in all_signals:
                self._disconnect_reference(ref)

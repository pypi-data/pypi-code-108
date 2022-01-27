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


class FlowManager(QtCore.QObject):
    # I'll be waiting with these until they are really necessary
    # document_inserted = QtCore.Signal(unicode)
    # document_removed = QtCore.Signal(unicode)
    # node_state_changed = QtCore.Signal(unicode, unicode)
    # connection_state_changed = QtCore.Signal(unicode, unicode)
    # node_parameter_validation_requested = QtCore.Signal(unicode, unicode)
    # execution_started = QtCore.Signal(unicode, unicode)
    # execution_finished = QtCore.Signal(unicode, unicode)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._flows = {}

    def flow(self, namespace_uuid):
        """
        Return the flow with namespace_uuid.
        Raises KeyError if the flow with this namespace_uuid has been closed.
        """
        return self._flows[namespace_uuid]

    def insert_flow(self, flow):
        self._flows[flow.namespace_uuid()] = flow

    def remove_flow(self, flow):
        if flow.namespace_uuid() in self._flows:
            del self._flows[flow.namespace_uuid()]

    def remove_root_flow(self, flow):
        root_namespace_uuid = flow.namespace_uuid()
        self.remove_flow(flow)
        for flow_ in list(self.flows()):
            root_flow = flow_.root_flow()
            if (root_flow is not None
                    and root_flow.namespace_uuid() == root_namespace_uuid):
                self.remove_flow(flow_)

    def is_empty(self):
        return len(self._flows) == 0

    def flows(self):
        return self._flows.values()

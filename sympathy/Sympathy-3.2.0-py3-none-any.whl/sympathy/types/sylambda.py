# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
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

from . import sybase
from .. platform import types
from . import exception as exc


class FlowDesc(object):
    """
    Extra level of typing to ensure that the user takes care and does not pass
    arbitrary strings or objects.
    """
    def __init__(self, flow_identifier, name, nodes, input_nodes,
                 output_nodes, node_deps, input_ports, output_ports,
                 bypass_ports,
                 node_settings):
        assert(isinstance(flow_identifier, str))
        self.flow_identifier = flow_identifier
        self.name = name
        self.nodes = nodes
        self.input_nodes = input_nodes
        self.output_nodes = output_nodes
        self.node_deps = node_deps
        self.input_ports = input_ports
        self.output_ports = output_ports
        self.bypass_ports = bypass_ports
        self.node_settings = node_settings


class PortDesc(object):
    """
    Extra level of typing to ensure that the user takes care and does not pass
    arbitrary strings or objects.
    """
    def __init__(self, port):
        assert(isinstance(port, dict))
        self.data = port


class sylambda(sybase.sygroup):

    def __init__(self, container_type, datasource=sybase.NULL_SOURCE):
        super(sylambda, self).__init__(container_type,
                                       datasource or sybase.NULL_SOURCE)
        self._args = []
        self._cache = (None, False)

        body_type = container_type

        try:
            while True:
                self._args.append(body_type.arg)
                body_type = body_type.result

        except AttributeError:
            # Last body reached, all args collected.
            pass

    def _get(self):
        value = self._cache[0]

        if value is None:
            value = self._datasource.read()
            self._cache = (value, False)
        return value

    def _set(self, value):
        flow, port = value
        self._cache = (value, True)

    def identifier(self):
        return self._get()[0][0]

    def name(self):
        return self._get()[0][1]

    def get(self):
        """Returns a pair of flow, list of port assignments."""
        flow, ports = self._get()
        return (FlowDesc(*flow), [PortDesc(port) for port in ports])

    def set(self, value):
        """Value is a pair of flow, list of port assignments."""
        flow, ports = value
        self._set(((flow.flow_identifier,
                    flow.name,
                    flow.nodes,
                    flow.input_nodes,
                    flow.output_nodes,
                    flow.node_deps,
                    flow.input_ports,
                    flow.output_ports,
                    flow.bypass_ports,
                    flow.node_settings),
                   [port.data
                    for port in ports]))

    def apply(self, port):
        assert(len(self._args) > 1)
        value = self._get()
        flow, ports = value
        assert(flow is not None)
        ports.append(port.data)
        self._set(value)
        self._args = self._args[1:]
        self.container_type = self.container_type.result

    def arguments(self):
        return self._args

    def source(self, other, shallow=False):
        assert(types.match(self.container_type, other.container_type))
        self._set(other._get())

    def __copy__(self):
        obj = super(sylambda, self).__copy__()
        obj._args = list(self._args)
        obj._cache = tuple(self._cache)
        return obj

    def __deepcopy__(self, memo=None):
        return self.__copy__()

    def _writeback(self, datasource, link=None):
        # Transfer relies on direct compatiblity, for example, in the hdf5
        # datasource case both sources need to be hdf5 and the source needs to
        # be read only.
        origin = self._datasource
        target = datasource
        exc.assert_exc(target.can_write, exc=exc.WritebackReadOnlyError)

        if link:
            return False

        shares_origin = target.shares_origin(origin)
        value, dirty = self._cache

        if shares_origin and not dirty:
            # At this point there is no support for writing flows more than
            # once.
            return

        if target.transferable(origin) and not dirty:
            target.transfer(
                None, origin, None)
        else:
            # No transfer possible, writing using numpy texts.
            if value is None:
                value = self._get()

            if value is not None:
                target.write(value)

    def __repr__(self):
        return "lambda()"

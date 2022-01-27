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
import numpy as np
import json

from . import dsgroup
from . import dstable


def decode_bytes_attr(bytes_or_str):
    # Prior to h5py 3.0 attributes were bytes.
    try:
        bytes_or_str = bytes_or_str.decode('utf8')
    except AttributeError:
        pass
    return bytes_or_str


class Hdf5Lambda(dsgroup.Hdf5Group):
    """Abstraction of an HDF5-lambda."""
    def __init__(self, factory, external=True, **kwargs):
        self._compress = (
            dstable.int_compress if not external else dstable.ext_compress)
        super().__init__(factory, external=external, **kwargs)

    def _create_dataset(self, name, data):
        if data.nbytes > dstable._h5py_compress_threshold:
            self.group.create_dataset(
                name, data=data, **self._compress)
        else:
            self.group.create_dataset(name, data=data)

    def read(self):
        """
        Return stored pair of flow and list of port assignments or None if
        nothing is stored.
        """
        flow = decode_bytes_attr(self.group.attrs['flow'])
        name = decode_bytes_attr(self.group.attrs['name'])
        nodes = json.loads(
            self.group['nodes'][...][0].tolist().decode('ascii'))
        input_nodes = self.group[
            'input_nodes'][...].astype(str).tolist()
        output_nodes = self.group[
            'output_nodes'][...].astype(str).tolist()
        node_deps = self.group['node_deps'][...].astype(str).tolist()
        input_ports = json.loads(
            self.group['input_ports'][...].tolist().decode('ascii'))
        output_ports = self.group[
            'output_ports'][...].astype(str).tolist()
        bypass_ports = self.group[
            'bypass_ports'][...].astype(str).tolist()
        node_settings = json.loads(
            self.group['node_settings'][...].tolist().decode('ascii'))
        ports = json.loads(self.group[
            'ports'][...][0].tolist().decode('ascii'))

        return (
            (flow, name, nodes, input_nodes, output_nodes, node_deps,
             input_ports, output_ports, bypass_ports, node_settings),
            ports)

    def write(self, value):
        """
        Stores lambda in the hdf5 file, at path,
        with data from the given text
        """
        (flow, name, nodes, input_nodes, output_nodes, node_deps,
         input_ports,
         output_ports, bypass_ports, node_settings) = value[0]
        ports = value[1]
        self.group.attrs.create('flow', flow.encode('utf8'))
        self.group.attrs.create('name', name.encode('utf8'))
        self._create_dataset(
            'nodes', data=np.array([json.dumps(nodes).encode('ascii')],
                                   dtype=bytes))
        self.group.create_dataset('input_nodes',
                                  data=np.array(input_nodes,
                                                dtype=bytes),)
        self.group.create_dataset('output_nodes',
                                  data=np.array(
                                      output_nodes, dtype=bytes))
        self.group.create_dataset('node_deps',
                                  data=np.array(
                                      node_deps, dtype=bytes))
        self.group.create_dataset('input_ports',
                                  data=np.array(
                                      json.dumps(input_ports).encode('ascii'),
                                      dtype=bytes))
        self.group.create_dataset('output_ports',
                                  data=np.array(output_ports,
                                                dtype=bytes))
        self.group.create_dataset('bypass_ports',
                                  data=np.array(bypass_ports,
                                                dtype=bytes))
        self.group.create_dataset(
            'ports',
            data=np.array([json.dumps(ports).encode('ascii')],
                          dtype=bytes))
        self.group.create_dataset('node_settings',
                                  data=np.array(
                                      json.dumps(input_ports).encode('ascii'),
                                      dtype=bytes))

    def transferable(self, other):
        return False

    def transfer(self, other):
        self.group.attrs['flow'] = other.group.attrs['flow']
        self.group.attrs['name'] = other.group.attrs['name']
        for key in ['nodes', 'input_nodes', 'output_nodes', 'node_deps',
                    'input_ports',
                    'output_ports', 'bypass_ports']:
            self.group[key] = other.group[key]

    def write_link(self, name, other, other_name):
        return False

# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
The vertical join, or the VJoin, of :ref:`ADAF` objects has the purpose
to merge data from tests performed at different occasions, where the data
from the occasions have been imported into different ADAFs. This opens up
for the possibility to perform analysis of tests/events over the course of
time.

The output of the operation is a new ADAF, where each data container is the
result of a vertical join performed between the corresponding data containers
of the incoming ADAFs. At the moment the output will only include the result
the vertical join of the metadata and the result containers. The timeseries
container will be empty in the outgoing ADAF.

The content of the metadata and the result containers are tables and the
vertical join of these containers follows the procedure described in
:ref:`VJoin Table`.
"""
import warnings
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, deprecated_node
from sympathy.api import exceptions as exc
from sylib import vjoin

INDEX = 'VJoin-index'


def reference_time_controller():
    controller = synode.controller(
        when=synode.field('include_rasters', 'checked'),
        action=synode.field('use_reference_time', 'enabled'))
    return controller


class VJoinBase(synode.Node):
    icon = 'vjoin_adaf.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['org.sysess.sympathy.data.table.vjointablenode']

    parameters = vjoin.base_params()
    parameters.set_boolean(
        'include_rasters', value=True, label='Include rasters in the result',
        description='Include rasters in the result.')
    parameters.set_boolean(
        'use_reference_time', value=False, label='Use raster reference time',
        description='Use raster reference time.')

    controllers = vjoin.base_controller() + (reference_time_controller(),)

    def extra_parameters(self, parameters):

        try:
            include_rasters = parameters['include_rasters'].value
        except Exception:
            include_rasters = False

        use_reference_time = False
        if include_rasters:
            try:
                use_reference_time = parameters['use_reference_time'].value
            except Exception:
                pass

        return vjoin.base_values(parameters) + (include_rasters,
                                                use_reference_time)

    def vjoin(self, output_adaf, input_adafs, input_index, output_index, fill,
              minimum_increment, include_rasters, use_reference_time):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                output_adaf.vjoin(
                    input_adafs, input_index, output_index, fill,
                    minimum_increment, include_rasters, use_reference_time)
        except exc.SyColumnTypeError:
            raise exc.SyDataError(
                'Input columns to stack have incompatible types',
                details=(
                    'Input columns to stack have incompatible types. '
                    'Keep in mind that datetime and timedelta cannot be '
                    'used in a column with other types'))


@deprecated_node('4.0.0')
class VJoinADAF(VJoinBase):
    """
    Sympathy node for vertical join of two ADAF files. The output of node
    is a new ADAF.
    """

    name = "VJoin ADAF"
    description = "VJoin two ADAF files."
    nodeid = "org.sysess.sympathy.data.adaf.vjoinadaf"
    author = "Alexander Busck"
    version = '1.0'

    inputs = Ports([
        Port.ADAF('ADAF 1', name='port1'),
        Port.ADAF('ADAF 2', name='port2')])
    outputs = Ports([Port.ADAF('Joined ADAF', name='port1')])

    def execute(self, node_context):
        """Execute"""
        input_adaf1 = node_context.input['port1']
        input_adaf2 = node_context.input['port2']
        output_adaf = node_context.output['port1']
        (input_index, output_index, minimum_increment, fill, include_rasters,
         use_reference_time) = self.extra_parameters(node_context.parameters)

        self.vjoin(
            output_adaf,
            [input_adaf1, input_adaf2],
            input_index,
            output_index,
            fill,
            minimum_increment,
            include_rasters,
            use_reference_time)


@deprecated_node('4.0.0')
class VJoinADAFs(VJoinBase):
    """
    Sympathy node for vertical join of the ADAFs in the incoming list.
    The output of node is a new ADAF.

    VJoin multiple ADAF files.
    """

    name = "VJoin ADAFs"
    description = "VJoin multiple ADAF files."
    nodeid = "org.sysess.sympathy.data.adaf.vjoinadafs"
    author = "Alexander Busck"
    version = '1.0'
    inputs = Ports([Port.ADAFs('Input ADAFs', name='port0')])
    outputs = Ports([Port.ADAF('Joined ADAFs', name='port0')])

    def execute(self, node_context):
        """Execute"""
        input_adafs = node_context.input['port0']
        output_adaf = node_context.output['port0']
        (input_index, output_index, minimum_increment, fill, include_rasters,
         use_reference_time) = self.extra_parameters(node_context.parameters)

        self.vjoin(
            output_adaf,
            input_adafs,
            input_index,
            output_index,
            fill,
            minimum_increment,
            include_rasters,
            use_reference_time)


@node_helper.list_node_decorator(['port1', 'port2'], ['port1'])
class VJoinADAFLists(VJoinADAF):
    name = "VJoin ADAFs pairwise"
    nodeid = "org.sysess.sympathy.data.adaf.vjoinadaflists"

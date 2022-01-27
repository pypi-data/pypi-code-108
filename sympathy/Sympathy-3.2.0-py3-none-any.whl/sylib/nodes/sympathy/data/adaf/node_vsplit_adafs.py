# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017, Combine Control Systems AB
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
The node performs a vertical, rowwise, split of :ref:`ADAF`. The vertical
split, or VSplit, is the inverse operation compared to the vertical join,
see :ref:`VJoin ADAF`.

The vertical split operation is only applied on the content of the metadata
and result containers. The timeseries container is not included, since the
inverse operation, VJoin, is not defined for this container. The content of
the metadata and the result containers are tables and the vertical split of
these containers follows the procedure described in :ref:`VSplit Table`.
For the split to be well defined, the Input Index column is required in
metadata and result containers.
"""
import warnings
from sympathy.api import node as synode
from sympathy.api.nodeconfig import (
    Port, Ports, Tag, Tags, adjust, deprecated_node)


INDEX = 'VJoin-index'


class VSplitBase(synode.Node):
    parameters = synode.parameters()
    parameters.set_boolean(
        'remove_fill', value=False, label='Remove fill',
        description='Remove split columns which contain only NaN.')
    parameters.set_string(
        'input_index',
        label='Input Index',
        value=INDEX,
        description='Choose name for grouped index column. '
                    'Required in both metadata and results.',
        editor=synode.Util.combo_editor(edit=True))
    parameters.set_boolean(
        'include_rasters', value=True, label='Include rasters in the result',
        description='Include rasters in the result.')
    tags = Tags(Tag.DataProcessing.TransformStructure)

    def extra_parameters(self, parameters):
        try:
            input_index = parameters['input_index'].value
        except:
            input_index = INDEX
        try:
            include_rasters = parameters['include_rasters'].value
        except:
            include_rasters = False

        return (input_index, include_rasters)

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['input_index'], node_context.input[0])


@deprecated_node('4.0.0')
class VSplitADAFNode(VSplitBase):
    """
    Vertical split of ADAF into ADAFs.
    """

    author = "Alexander Busck"
    version = '1.0'
    name = 'VSplit ADAF'
    description = 'Split an ADAF into multiple ADAFs.'
    nodeid = 'org.sysess.sympathy.data.adaf.vsplitadafnode'
    icon = 'vsplit_adaf.svg'
    related = ['org.sysess.sympathy.data.adaf.vjoinadaf',
               'org.sysess.sympathy.data.table.vsplittablenode']

    inputs = Ports([Port.ADAF('Input ADAF', name='port1')])
    outputs = Ports([Port.ADAFs('Split ADAFs', name='port1')])

    def execute(self, node_context):
        """Execute"""
        input_adaf = node_context.input['port1']
        output_adafs = node_context.output['port1']
        input_index, include_rasters = self.extra_parameters(
            node_context.parameters)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', FutureWarning)

            input_adaf.vsplit(
                output_adafs,
                input_index,
                node_context.parameters['remove_fill'].value,
                True,
                include_rasters)

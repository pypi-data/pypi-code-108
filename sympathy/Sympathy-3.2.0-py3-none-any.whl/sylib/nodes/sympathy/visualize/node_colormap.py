# This file is part of Sympathy for Data.
# Copyright (c) 2018, Combine Control Systems AB
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
import matplotlib as mpl
import matplotlib.cm as cm

from sympathy.api import node as synode
from sympathy.platform.exceptions import SyError
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sylib.figure import colors


class ColormapLookup(synode.Node):

    version = '0.1'
    name = 'Colormap lookup'
    icon = 'colourmap.svg'
    description = 'Maps input values into colours based on a colourmap.'
    nodeid = 'org.sysess.sympathy.visualize.colormap_lookup'
    tags = Tags(Tag.Visual.Figure)

    inputs = Ports([Port.Table('Input data', name='input')])
    outputs = Ports([Port.Table('Output data', name='output')])

    parameters = synode.parameters()
    parameters.set_string(
        'colormap', value='viridis', label='Colormap',
        description=(
            'Colormap used for converting the input values'),
        editor=synode.Util.combo_editor(options=list(colors.COLORMAPS.keys())))
    parameters.set_float(
        'vmin', value=0.0, label='vmin',
        description=(
            'First (lowest) value that should be mapped to colors'))
    parameters.set_float(
        'vmax', value=1.0, label='vmax',
        description=(
            'Last (highest) value that should be mapped to colors'))
    parameters.set_string(
        'suffix', value='', label='Suffix',
        description=('Suffix added to each column name when '
                     'generating the output names'))

    def execute(self, node_context):
        in_tbl = node_context.input['input']
        out_tbl = node_context.output['output']
        suffix = node_context.parameters['suffix'].value
        vmin = node_context.parameters['vmin'].value
        vmax = node_context.parameters['vmax'].value
        colormap_name = node_context.parameters['colormap'].value
        colormap = cm.get_cmap(colors.COLORMAPS[colormap_name])

        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

        for col in in_tbl.cols():
            try:
                data = (colormap(norm(col.data)) * 255)[:, :3].astype(int)
            except TypeError:
                raise SyError("Colormap node requires all input "
                              "columns to be numerical.")
            as_strings = ['#{:0>2X}{:0>2X}{:0>2X}'
                          .format(*list(c))
                          for c in data]
            out_tbl.set_column_from_array(col.name+suffix,
                                          np.array(as_strings))

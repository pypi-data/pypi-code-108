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
import numpy as np

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyConfigurationError, SyDataError


class HistogramCalculation(synode.Node):
    """
    This node takes a table and calculates a histogram from one of its columns.

    The output consists of bin edges and bin values and can for instance be
    used in a histogram plot in the node :ref:`Figure`.

    Masked values in the data column are ignored. Masked values in the weights
    column are treated as 1.
    """
    author = 'Magnus Sandén'
    version = '0.1'
    icon = 'histogram_calculation.svg'
    name = 'Histogram calculation'
    description = 'Calculate the histogram of a given signal.'
    nodeid = 'org.sysess.sympathy.dataanalysis.histogramcalc'
    tags = Tags(Tag.Analysis.Statistic)

    parameters = synode.parameters()
    combo_editor = synode.editors.combo_editor(edit=True)
    combo_editor_w_empty = synode.editors.combo_editor(
        include_empty=True, edit=True)
    parameters.set_list('data_column', label="Data column:",
                        description='Column to create histogram for.',
                        editor=combo_editor)
    parameters.set_list('weights_column', label="Weights column:",
                        description=('If you choose a weights column, '
                                     'each value in the data column only '
                                     'contributes its associated weight '
                                     'towards the bin count, instead of 1.'),
                        editor=combo_editor_w_empty)
    parameters.set_integer('bins', label="Bins:", value=10,
                           description='Number of bins.')
    parameters.set_boolean('auto_range', label="Auto range", value=True,
                           description=('When checked, use data range as '
                                        'histogram range.'))
    parameters.set_float('x_min', label="X min:", value=0.0,
                         description='Minimum x value.')
    parameters.set_float('x_max', label="X max:", value=1.0,
                         description='Maximum x value.')
    parameters.set_boolean('normed', label="Density",
                           description=('When checked, the result is the '
                                        'value of the probability density '
                                        'function at each bin, normalized '
                                        'such that the integral of the '
                                        'histogram is 1.'))

    controllers = synode.controller(
        when=synode.field('auto_range', 'checked'),
        action=(synode.field('x_min', 'disabled'),
                synode.field('x_max', 'disabled')))

    inputs = Ports([Port.Table('Input data', name='in')])
    outputs = Ports([Port.Table('Histogram data', name='out')])

    def update_parameters(self, parameters):
        parameters['weights_column'].editor['include_empty'] = True

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['data_column'],
               node_context.input['in'])
        adjust(node_context.parameters['weights_column'],
               node_context.input['in'])

    def execute(self, node_context):
        parameters = node_context.parameters
        bins = parameters['bins'].value
        density = parameters['normed'].value
        data_param = parameters['data_column']
        auto_range = parameters['auto_range'].value
        if auto_range:
            range_ = None
        else:
            x_min = parameters['x_min'].value
            x_max = parameters['x_max'].value
            range_ = x_min, x_max

        data = node_context.input['in']._require_column(data_param)
        weights_param = parameters['weights_column']
        if not weights_param.selected:
            weights = None
        else:
            weights = node_context.input['in']._require_column(weights_param)

        # Handle masked arrays
        if isinstance(weights, np.ma.MaskedArray):
            weights.fill(1)
        if isinstance(data, np.ma.MaskedArray):
            mask = data.mask
            data = data.compressed()
            if weights is not None:
                weights = weights[np.logical_not(mask)]

        # Handle NaNs
        if data.dtype.kind == 'f':
            nan_mask = np.isnan(data)
            if weights is not None and weights.dtype.kind == 'f':
                nan_mask |= np.isnan(weights)
            data = data[~nan_mask]
            if weights is not None:
                weights = weights[~nan_mask]

        # Handle datetimes
        datetime_dtype = None
        if data.dtype.kind in 'mM':
            if density:
                raise SyConfigurationError(
                    "Density can't be used with data of types datetime or "
                    "timedelta.")
            datetime_dtype = data.dtype
            data = data.astype('int64')

        bin_values, bin_edges = np.histogram(
            data, bins=bins, density=density, weights=weights, range=range_)

        # Handle datetimes
        if datetime_dtype is not None:
            bin_edges = bin_edges.astype(datetime_dtype)

        node_context.output['out'].set_column_from_array(
            "Bin values", bin_values)
        node_context.output['out'].set_column_from_array(
            "Bin min edges", bin_edges[:-1])
        node_context.output['out'].set_column_from_array(
            "Bin max edges", bin_edges[1:])

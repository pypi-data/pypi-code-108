# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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
import itertools
import collections

import numpy as np

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyConfigurationError


class IHeatMapAccumulator(object):
    def __init__(self):
        self._value = None

    def add_data(self, data):
        raise NotImplementedError

    def value(self):
        return self._value


class CountAccumulator(IHeatMapAccumulator):
    def add_data(self, data):
        if not self._value:
            self._value = 0
        self._value += data.size


class SumAccumulator(IHeatMapAccumulator):
    def add_data(self, data):
        if not self._value:
            self._value = 0
        self._value += data.sum()


class MinAccumulator(IHeatMapAccumulator):
    def add_data(self, data):
        if not data.size:
            return
        if self._value is None:
            self._value = data.min()
        else:
            self._value = min(self._value, data.min())


class MaxAccumulator(IHeatMapAccumulator):
    def add_data(self, data):
        if not data.size:
            return
        if self._value is None:
            self._value = data.max()
        else:
            self._value = max(self._value, data.max())


class MeanAccumulator(IHeatMapAccumulator):
    def __init__(self):
        self._sum = 0
        self._count = 0

    def add_data(self, data):
        self._sum += data.sum()
        self._count += data.size

    def value(self):
        if self._count:
            return self._sum / self._count
        else:
            return None


class MedianAccumulator(IHeatMapAccumulator):
    def __init__(self):
        self._values = []

    def add_data(self, data):
        self._values.append(data)

    def value(self):
        if self._values:
            return np.ma.median(np.vstack(self._values))
        else:
            return None


REDUCTION_FUNCTIONS = collections.OrderedDict([
    ('Count (histogram)', CountAccumulator),
    ('Sum', SumAccumulator),
    ('Min', MinAccumulator),
    ('Max', MaxAccumulator),
    ('Mean', MeanAccumulator),
    ('Median', MedianAccumulator)])


class HeatmapCalculation(synode.Node):
    """
    This node calculates a 2D histogram or other heatmap of a given signal.

    The output consists of bin edges and bin values and can for instance be
    used in a heatmap plot in the node :ref:`Figure`.

    This node ignores any rows in the input where one or more of the selected
    columns are masked.
    """

    author = 'Magnus Sandén'
    version = '0.1'
    icon = 'heatmap_calculation.svg'
    name = 'Heatmap calculation'
    description = ('Calculate a 2d histogram or other heatmap of a given'
                   'signal.')
    nodeid = 'org.sysess.sympathy.dataanalysis.heatmapcalc'
    tags = Tags(Tag.Analysis.Statistic)

    parameters = synode.parameters()
    combo_editor = synode.Util.combo_editor(edit=True)
    reduction_editor = synode.Util.combo_editor(
        options=list(REDUCTION_FUNCTIONS.keys()))
    parameters.set_string('x_data_column', label="X data column:",
                          editor=combo_editor,
                          description='Select X axis data')
    parameters.set_string('y_data_column', label="Y data column:",
                          editor=combo_editor,
                          description='Select Y axis data')
    parameters.set_string('z_data_column', label="Z data column:",
                          description='The data points of the z data are '
                                      'placed in bins according to the '
                                      'cooresponding values of x and y. They '
                                      'are then reduced to a single bin value '
                                      'using the selected reduction function. '
                                      'For "{}" no z data column is needed.'
                                      ''.format(
                                          list(REDUCTION_FUNCTIONS.keys())[0]),
                          editor=combo_editor)
    parameters.set_string('reduction', label="Reduction function:",
                          value=list(REDUCTION_FUNCTIONS.keys())[0],
                          description='A function used on all the z data '
                                      'points in a bin. For "{}" no z data '
                                      'column is needed.'.format(
                                          list(REDUCTION_FUNCTIONS.keys())[0]),
                          editor=reduction_editor)
    parameters.set_integer('x_bins', label="X Bins:", value=10,
                           description='Number of bins on the x axis')
    parameters.set_integer('y_bins', label="Y Bins:", value=10,
                           description='Number of bins on the y axis')
    parameters.set_boolean('auto_range', label="Auto range", value=True,
                           description=('When checked, use data range as '
                                        'histogram range'))
    parameters.set_float(
        'x_min', label="X min:", value=0.0, description='Set minimum X value')
    parameters.set_float(
        'x_max', label="X max:", value=1.0, description='Set maximum X value')
    parameters.set_float(
        'y_min', label="Y min:", value=0.0, description='Set minimum Y value')
    parameters.set_float(
        'y_max', label="Y max:", value=1.0, description='Set maximum Y value')

    controllers = (synode.controller(
        when=synode.field('auto_range', 'checked'),
        action=(synode.field('x_min', 'disabled'),
                synode.field('x_max', 'disabled'),
                synode.field('y_min', 'disabled'),
                synode.field('y_max', 'disabled'))),
        synode.controller(
            when=synode.field(
                'reduction', 'value', list(REDUCTION_FUNCTIONS.keys())[0]),
            action=synode.field('z_data_column', 'disabled')))

    inputs = Ports([Port.Table('Input data', name='in')])
    outputs = Ports([Port.Table('Heatmap data', name='out')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['x_data_column'],
               node_context.input['in'])
        adjust(node_context.parameters['y_data_column'],
               node_context.input['in'])
        adjust(node_context.parameters['z_data_column'],
               node_context.input['in'])

    def execute(self, node_context):
        parameters = node_context.parameters
        x_bins = parameters['x_bins'].value
        y_bins = parameters['y_bins'].value
        x_data_param = parameters['x_data_column']
        y_data_param = parameters['y_data_column']
        z_data_param = parameters['z_data_column']
        auto_range = parameters['auto_range'].value

        x_data = node_context.input['in']._require_column(x_data_param)
        y_data = node_context.input['in']._require_column(y_data_param)

        if (list(REDUCTION_FUNCTIONS.keys())[0] ==
                parameters['reduction'].value):
            z_data = np.zeros_like(x_data, dtype=int)
        else:
            z_data = node_context.input['in']._require_column(z_data_param)

        # Handle masked arrays
        mask = np.zeros(x_data.shape, dtype=bool)
        if isinstance(x_data, np.ma.MaskedArray):
            mask |= x_data.mask
        if isinstance(y_data, np.ma.MaskedArray):
            mask |= y_data.mask
        if isinstance(z_data, np.ma.MaskedArray):
            mask |= z_data.mask
        if np.any(mask):
            mask = np.logical_not(mask)
            x_data = x_data[mask]
            y_data = y_data[mask]
            z_data = z_data[mask]

        # Handle datetimes in x and y:
        x_dtype = x_data.dtype
        y_dtype = y_data.dtype
        z_dtype = z_data.dtype
        if x_dtype.kind == 'M':
            x_data = x_data.astype('int64')
        if y_dtype.kind == 'M':
            y_data = y_data.astype('int64')
        if z_dtype.kind == 'M':
            z_data = z_data.astype('int64')

        if auto_range:
            x_min = min(x_data)
            x_max = max(x_data)
            y_min = min(y_data)
            y_max = max(y_data)
        else:
            x_min = parameters['x_min'].value
            x_max = parameters['x_max'].value
            y_min = parameters['y_min'].value
            y_max = parameters['y_max'].value

        x_bin_edges = np.linspace(x_min, x_max, x_bins + 1)
        y_bin_edges = np.linspace(y_min, y_max, y_bins + 1)
        Accumulator = REDUCTION_FUNCTIONS[parameters['reduction'].value]  # noqa
        values_buffer = np.empty((x_bins, y_bins), dtype=object)

        x_bin_indices = np.digitize(x_data, x_bin_edges)
        y_bin_indices = np.digitize(y_data, y_bin_edges)

        # Digitize puts values on bin edges in the right bin, but for the
        # rightmost bin this is not what we want. We want the rightmost bin to
        # be a closed interval.
        on_x_edge = x_data == x_bin_edges[-1]
        on_y_edge = y_data == y_bin_edges[-1]
        x_bin_indices[on_x_edge] -= 1
        y_bin_indices[on_y_edge] -= 1

        # Build the values buffer. The values buffer holds a list of z
        # values for each bin.
        for x_bin_index, y_bin_index, z in zip(
                x_bin_indices, y_bin_indices, z_data):
            if 0 < x_bin_index <= x_bins and 0 < y_bin_index <= y_bins:
                xi = x_bin_index - 1
                yi = y_bin_index - 1
            else:
                # print("bin doesn't exist: ({}, {})".format(
                #     x_bin_index, y_bin_index))
                continue
            if values_buffer[xi, yi] is None:
                values_buffer[xi, yi] = Accumulator()
            values_buffer[xi, yi].add_data(z)

        # Now go through the values buffer and reduce each list into the real z
        # data for that bin.
        bin_values = np.ma.masked_all((x_bins, y_bins), dtype=z_data.dtype)
        for xi, yi in itertools.product(range(x_bins), range(y_bins)):
            z_values = values_buffer[xi, yi]
            if z_values is not None:
                bin_values[xi, yi] = z_values.value()

        x_output = np.array([x_bin_edges[:-1]] * y_bins).reshape(-1, order='F')
        y_output = np.array([y_bin_edges[:-1]] * x_bins).reshape(-1, order='C')
        if x_dtype.kind == 'M':
            x_output = x_output.astype(x_dtype)
        if y_dtype.kind == 'M':
            y_output = y_output.astype(y_dtype)
        if z_dtype.kind == 'M':
            bin_values = bin_values.astype(z_dtype)
        node_context.output['out'].set_column_from_array(
            "X bin edges", x_output)
        node_context.output['out'].set_column_from_array(
            "Y bin edges", y_output)
        node_context.output['out'].set_column_from_array(
            "Bin values", bin_values.flatten())

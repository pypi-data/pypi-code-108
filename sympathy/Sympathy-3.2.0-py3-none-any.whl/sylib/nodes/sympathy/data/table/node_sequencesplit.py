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
from sympathy.api import node
from sympathy.api import table
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import sywarn, SyConfigurationError, SyDataError
import numpy as np
import scipy
import scipy.signal as signal
import math
import warnings
import distutils.version

LOCAL_MAXIMA = 'Local Maxima'
WAVELET = 'Continuous Wavelet Transform'


def _scipy_version():
    return distutils.version.LooseVersion(scipy.__version__).version[:3]


def median_period(data, peak_detector, samples):
    # Lowpass filter to reduce the risk of erroneous detections.
    # Remove last element to keep the original data length.
    data = np.convolve(data, np.ones(10) / 10)[:-1]

    # Calculate the autocorrelation
    # (see https://en.wikipedia.org/wiki/Autocorrelation)
    # and extract a sequence with the same size as the original data.
    correlation = signal.correlate(data, data, mode='same') / len(data)

    # Detect local maxima using the selected algorithm.
    if peak_detector == LOCAL_MAXIMA:
        peaks = signal.argrelmax(correlation)[0]
    else:
        if _scipy_version() < [1, 5, 0]:
            peaks = signal.find_peaks_cwt(correlation, np.linspace(1, samples))
        else:
            # Avoid special case rounding by passing default window_size.
            # https://github.com/scipy/scipy/issues/12739.
            peaks = signal.find_peaks_cwt(
                correlation, np.linspace(1, samples),
                window_size=int(np.ceil(len(correlation) / 20)))

    # Differentiate to calculate the distance between peaks.
    # Then remove the first and last peaks to avoid problems where these
    # samples are to close the start or end of the data.
    diff_peaks = np.diff(peaks)

    # Calculate the average of 80 % of the found peaks.
    start = int(np.ceil(len(diff_peaks) * 0.1))
    stop = int(-np.ceil(len(diff_peaks) * 0.1))
    med_diff = np.mean(diff_peaks[start:stop])
    return med_diff


class SequenceSplit(node.Node):
    """
    Find peaks in a signal and slice the input Table into a list of Tables, where
    each element contains one peak.

    If peaks are found very close to the edges of the data, the first and/or
    last element may contain unexpected results. If this is the case,
    use :ref:`Slice List` to remove these elements.
    """

    name = 'Periodic Sequence Split Table'
    author = 'Måns Fällman'
    version = '1.0'
    icon = 'sequencesplit.svg'
    description = (
        'Splits tables of data in equidistant points based on the periodicity '
        'of an identifier column')
    nodeid = 'org.sysess.sympathy.data.table.sequencesplit'
    tags = Tags(Tag.Analysis.SignalProcessing)

    inputs = Ports([Port.Table('The sequence to split', 'sequence')])
    outputs = Ports([Port.Tables('The split sequences', 'sequences')])

    parameters = node.parameters()
    parameters.set_string(
        'peak_detector',
        label='Peak Detecting Algorithm',
        description='Choose which algorithm to detect periodic events',
        value=LOCAL_MAXIMA,
        editor=node.Util.combo_editor(options=[LOCAL_MAXIMA, WAVELET]))
    parameters.set_integer(
        'samples',
        label='Samples per peak',
        description=(
            'Choose an approximate value for the number of expected samples '
            'between peaks'),
        editor=node.Util.bounded_spinbox_editor(2, 9999999, 1))
    parameters.set_list(
        'select_column',
        label='Select column',
        description='Choose column to use as identifier',
        editor=node.Util.combo_editor(edit=True, placeholder='Required'))
    parameters.set_float(
        'lag_offset',
        label='Offset of peridodic event (0-100)',
        description='Add lag as a percentage of the discarded data',
        value=0.0,
        editor=node.Util.bounded_lineedit_editor(
            0, 100, placeholder='0-100'))

    controllers = (
        node.controller(
            when=node.field('peak_detector', 'value', value=WAVELET),
            action=(node.field('samples', 'enabled'))),
        node.controller(
            when=node.field('peak_detector', 'value', value=LOCAL_MAXIMA),
            action=(node.field('samples', 'disabled'))))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['select_column'],
               node_context.input['sequence'])

    def execute(self, node_context):
        parameters = node_context.parameters
        in_table = node_context.input['sequence']
        data = in_table._require_column(parameters['select_column'])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            med_diff = median_period(
                data,
                parameters['peak_detector'].value,
                parameters['samples'].value)
        if math.isnan(med_diff):
            sywarn('No peaks found. Check input data.')
            return

        offset = np.mod(len(data), np.round(med_diff))
        offset = int(offset * parameters['lag_offset'].value * 0.01)

        number_of_tables = np.int(len(data) / med_diff)
        for x in range(number_of_tables):
            out_table = table.File()
            names = in_table.column_names()
            start = int(np.round(x * med_diff) + offset + np.mod(x, 2))
            stop = int(np.round((x + 1) * med_diff) + offset + np.mod(x, 2))
            for name in names:
                out_table.set_column_from_array(
                    name, in_table.get_column_to_array(name)[start:stop])
            node_context.output['sequences'].append(out_table)

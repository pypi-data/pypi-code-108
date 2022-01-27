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
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyNodeError

import numpy as np
from scipy.spatial.distance import cdist


class DistanceMatrix(node.Node):
    """
    Computes a distance matrix between each pair of rows in two tables.

    Each row corresponds to a vector of length N where N is the number of
    columns each table. Metrics for calculation include Euclidean (default),
    City-block (aka. Manhattan) distance, and more. Hamming distance is not
    recommended for float data.
    """

    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'distance_matrix.svg'
    description = ('Computes a distance matrix between each pair of rows\n'
                   'in two tables. Each row corresponds to a vector of\n'
                   'length N where N is the number of columns each table.')
    name = 'Distance Matrix'
    tags = Tags(Tag.Analysis.Features)
    future_nodeid = 'se.combine.sympathy.dataanalysis.distance_matrix'

    parameters = node.parameters()
    parameters.set_string(
        'metric', value='euclidean', label='Metric',
        description=(
            'Metric used for comparing keypoints. '
            'See http://scipy.spatial.distance.cdist for details.'),
        editor=node.Util.combo_editor(
            options=['euclidean', 'cityblock', 'correlation', 'minkowski',
                     'hamming', 'braycurtis', 'canberra',
                     'chebyshev', 'cosine', 'dice', 'hamming', 'jaccard',
                     'kulsinski', 'mahalanobis', 'matching', 'rogerstanimoto',
                     'russellrao', 'seuclidean', 'sokalmichener',
                     'sokalsneath', 'sqeuclidean', 'wminkowski', 'yule'])
    )
    parameters.set_integer(
        'p', value=2, label='P',
        description='P norm to apply for minkowski metrics')

    inputs = Ports([
        Port.Table('Input 1', name='input 1'),
        Port.Table('Input 2', name='input 2'),
    ])
    outputs = Ports([
        Port.Table('Table with results', name='result'),
    ])

    def execute(self, node_context):
        input1      = node_context.input['input 1']
        input2      = node_context.input['input 2']
        output      = node_context.output['result']
        pnorm       = node_context.parameters['p'].value
        metric      = node_context.parameters['metric'].value

        desc1 = np.column_stack([col.data for col in input1.cols()])
        desc2 = np.column_stack([col.data for col in input2.cols()])

        if desc1.shape[1] != desc2.shape[1]:
            raise SyNodeError(
                "Number of columns does not match in the two tables")

        distances = cdist(desc1, desc2, metric=metric, p=pnorm)
        for i in range(desc2.shape[0]):
            output.set_column_from_array('{}'.format(i+1), distances[:, i])

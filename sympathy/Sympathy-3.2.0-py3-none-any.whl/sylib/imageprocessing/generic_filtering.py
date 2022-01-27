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
from sympathy.api.nodeconfig import Tag, Tags
import numpy as np


class GenericImageFiltering(object):
    """
    Generic class for implementing all image processing nodes that takes
    a simple image and paramter list as inputs and outputs an image
    """

    version   = '0.1'
    author    = 'Mathias Broxvall'
    copyright = "(C) 2017 Combine Control Systems AB"
    tags      = Tags(Tag.ImageProcessing.ImageManipulation)

    def execute(self, node_context):
        params = node_context.parameters
        source = node_context.input['source'].get_image()

        if len(source.shape) == 3 and source.shape[2] > 1:
            is_multichannel = True
        else:
            is_multichannel = False

        alg_dict = self.algorithms[params['algorithm'].value]
        alg = alg_dict['algorithm']
        multi_chromatic = alg_dict['multi_chromatic']
        if (is_multichannel and not multi_chromatic):
            # Process each channel one by one
            # Process first channel separately to get the Width/Height of it
            res0       = alg(source[:, :, 0], params)
            res        = np.zeros(res0.shape[:2]+source.shape[2:])
            res[:, :, 0] = res0
            for channel in range(1, source.shape[2]):
                res[:, :, channel] = alg(source[:, :, channel], params)
            node_context.output['result'].set_image(res)
        else:
            # Process all channels at once
            if len(source.shape) == 3 and source.shape[2] == 1:
                source = source.reshape(source.shape[:2])
            node_context.output['result'].set_image(alg(source, params))




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
from sympathy.api.nodeconfig import Ports, Tag, Tags

from skimage import morphology
from sylib.imageprocessing.image import Image


class ImageLabelling(node.Node):
    name = 'Label image'
    icon = 'image_labelling.svg'  #
    description = (
        'Creates integer image with separate labels for each connected '
        'region with same values in input image')
    nodeid = 'syip.labelling'
    tags = Tags(Tag.ImageProcessing.Segmentation)

    parameters = node.parameters()
    parameters.set_boolean(
        'diagonal', value=False,
        description='Allow connections along diagonal',
        label='Diagonal neighbourhood')

    inputs = Ports([
        Image('source image to label', name='source'),
    ])
    outputs = Ports([
        Image('result after labelling', name='result'),
    ])

    def execute(self, node_context):
        params = node_context.parameters
        image = node_context.input['source'].get_image()
        im = morphology.label(
            image,
            connectivity=2 if params['diagonal'].value else 1)
        node_context.output['result'].set_image(im)

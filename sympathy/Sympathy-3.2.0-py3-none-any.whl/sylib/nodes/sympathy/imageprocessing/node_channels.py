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

import numpy as np
from sylib.imageprocessing.image import Image


class SplitChannels(node.Node):
    """
    Copies the given channels from the input image to the first output image,
    remaining channels are copied to second output image.
    """
    name = 'Split Image Channels'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'image_split_channels.svg'
    description = ('Copies the given channels from the input image to the '
                   'first output image, remaining channels are copied to '
                   'second output image')
    nodeid = 'syip.splitchannels'
    tags = Tags(Tag.ImageProcessing.Layers)

    parameters = node.parameters()
    parameters.set_string(
        'selected_channels', label='selected channels',
        description=('Comma separated list of channels to send to first image '
                     'output.\n\nCommon channel numbers and names:\n   0 '
                     '(red/gray), 1 (green), 2 (blue).\n   '
                     'Alpha is always last channel.'),
        value='0')

    inputs = Ports([
        Image('Input image', name='input'),
    ])
    outputs = Ports([
        Image('Image with selected channels', name='output1'),
        Image('All non-selected channels', name='output2'),
    ])

    def execute(self, node_context):
        im = node_context.input['input'].get_image()
        channels_str = node_context.parameters['selected_channels'].value

        def lookup_channel(s, depth):
            kv = {'r': 0, 'g': 1, 'b': 2,
                  'red': 0, 'green': 1, 'blue': 2, 'gray': 0, 'grey': 0,
                  'hue': 0, 'sat': 1, 'saturation': 1,
                  'val': 2 if depth in [3, 4] else 0,
                  'value': 2 if depth in [3, 4] else 0,
                  'real': 0, 'imaginary': 1, 'alpha': depth-1}
            try:
                return kv[s.lower()]
            except KeyError:
                pass
            try:
                return int(s)
            except ValueError:
                return None

        if len(im.shape) < 3:
            im = im.reshape(im.shape[:2]+(1,))
        depth = im.shape[2]
        channels = []
        for s in channels_str.split(','):
            v = lookup_channel(s.lstrip(), depth)
            if v is not None:
                channels.append(v)
        complement = list(filter(lambda c: c not in channels, range(depth)))
        out1 = np.zeros(im.shape[:2]+(len(channels),))
        out2 = np.zeros(im.shape[:2]+(len(complement),))
        for pos, c in enumerate(channels):
            out1[:, :, pos] = im[:, :, c]
        for pos, c in enumerate(complement):
            out2[:, :, pos] = im[:, :, c]

        if len(channels) > 0:
            node_context.output['output1'].set_image(out1)
        if len(complement) > 0:
            node_context.output['output2'].set_image(out2)


class ConcatChannels(node.Node):
    """
    Creates a new image with all the channels in the two input images.
    """
    name = 'Merge Image Channels'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'image_merge_channels.svg'
    description = ('Creates a new image with all the channels in the two '
                   'input images')
    nodeid = 'syip.concatchannels'
    tags = Tags(Tag.ImageProcessing.Layers)

    parameters = node.parameters()
    inputs = Ports([
        Image('Input image', name='input1'),
        Image('Input image', name='input2')])
    outputs = Ports([
        Image('Resulting image with all channels', name='output')])

    def execute(self, node_context):
        im1 = node_context.input['input1'].get_image()
        im2 = node_context.input['input2'].get_image()

        if len(im1.shape) < 3:
            im1 = im1.reshape(im1.shape[:2] + (1,))
        if len(im2.shape) < 3:
            im2 = im2.reshape(im2.shape[:2] + (1,))
        shape = (max(im1.shape[0], im2.shape[0]),
                 max(im1.shape[1], im2.shape[1]), im1.shape[2]+im2.shape[2])

        out = np.zeros(shape)
        out[:im1.shape[0], :im1.shape[1], :im1.shape[2]] = im1
        out[:im2.shape[0], :im2.shape[1], im1.shape[2]:] = im2
        node_context.output['output'].set_image(out)

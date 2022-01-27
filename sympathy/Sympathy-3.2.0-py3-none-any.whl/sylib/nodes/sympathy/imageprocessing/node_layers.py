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

import numpy as np
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract


class OverlayImagesAbstract(ImageFiltering_abstract, node.Node):
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'image_overlay.svg'
    description = (
        'Combines two images by layering the first (top port) image on top of '
        'the other (bottom port) image\n, with choice for combining operator. '
        'Images must have the same number of channels')
    tags = Tags(Tag.ImageProcessing.Layers)

    default_parameters = {
        'use alpha channel': (
            'Use last channel of source images as alpha channel'),
        'alpha': 'Alpha value used when no alpha channel is given'
    }
    algorithms = {
        'additive': dict({
            'description': 'Adds the two images together where they overlap.',
            'unity': 0.0,
            'expr': lambda result, im: result + im,
            'single_pass': False
        }, **default_parameters),
        'multiplicative': dict({
            'description': 'Multiplies images where they overlap.',
            'unity': 1.0,
            'expr': lambda result, im: result * im,
            'single_pass': False,
        }, **default_parameters),
        'divide': dict({
            'description': (
                'Divides bottom image by all other images, one at a time.'),
            'unity': 1.0,
            'expr': lambda result, im: result / im,
            'single_pass': False,
        }, **default_parameters),
        'subtract': dict({
            'description': 'Subtracts top image from bottom.',
            'unity': 0.0,
            'expr': lambda result, im: result - im,
            'single_pass': False,
        }, **default_parameters),
        'max': dict({
            'description': 'Takes the maximum value of the images.',
            'unity': 0.0,
            'expr': lambda result, im: np.maximum(result, im),
            'single_pass': False,
        }, **default_parameters),
        'min': dict({
            'description': 'Takes the minimum value of the images.',
            'unity': 0.0,
            'expr': lambda result, im: np.minimum(result, im),
            'single_pass': False,
        }, **default_parameters),
        'median': dict({
            'description': 'Takes the median value of the images.',
            'unity': 0.0,
            'expr': lambda images: np.median(np.array(images), axis=0),
            'single_pass': True,
        }, **default_parameters),
        'layer': dict({
            'description': (
                'Layers on image on top of the other, alpha channel (if any) '
                'determines transparency. Otherwise alpha value below'),
            'unity': 0.0,
            'expr': lambda result, im: im,
            'single_pass': False,
        }, **default_parameters),
    }

    options_list  = [
        'use alpha channel', 'alpha'
    ]
    options_types = {
        'use alpha channel': bool, 'alpha': float
    }
    options_default = {
        'use alpha channel': False, 'alpha': 1.0
    }

    parameters = node.parameters()
    parameters.set_string(
        'algorithm', value=next(iter(algorithms)), description='',
        label='Algorithm')
    ImageFiltering_abstract.generate_parameters(
        parameters, options_types, options_default)

    def execute(self, node_context):
        images = self.get_input_images(node_context)
        # images = [
        #     obj.get_image() for obj in node_context.input.group('images')]

        params   = node_context.parameters
        alg_name = params['algorithm'].value
        use_alpha = params['use alpha channel'].value

        # Reshape so all images guaranteed to have 3 dimensions
        images = [
            (im.reshape(im.shape + (1,)) if len(im.shape) < 3 else im)
            for im in images]

        # Compute max size
        max_y = max([im.shape[0] for im in images])
        max_x = max([im.shape[1] for im in images])
        max_c = max([im.shape[2] for im in images])

        if alg_name == 'multiplicative':
            unity = 1.0
        elif alg_name == 'divide':
            unity = 1.0
        else:
            unity = 0.0

        result = np.full((max_y, max_x, max_c), unity)
        if any([im.dtype.kind == 'c' for im in images]):
            result = result.astype(np.complex)

        if len(images) == 0:
            # Return early for all empty inputs
            node_context.output['result'].set_image(result)
            return

        bot = images[-1]
        result[:bot.shape[0], :bot.shape[1], :bot.shape[2]] = bot
        rest = images[:-1]

        alpha = params['alpha'].value

        if OverlayImages.algorithms[alg_name]['single_pass']:
            self.set_progress(50)
            expr = OverlayImages.algorithms[alg_name]['expr']
            result = expr(images)
        else:
            for i,im in enumerate(rest[::-1]):
                self.set_progress(50 + (i*50) / len(rest))
                for c in range(im.shape[2]):
                    expr    = OverlayImages.algorithms[alg_name]['expr']
                    y, x, _ = im.shape
                    if use_alpha:
                        result[:y, :x, c] = (
                            result[:y, :x, c] * (1-im[:, :, -1]) +
                            im[:, :, -1] * expr(result[:y, :x, c], im[:, :, c]))
                    else:
                        result[:y, :x, c] = (
                            result[:y, :x, c] * (1-alpha) +
                            alpha * expr(result[:y, :x, c], im[:, :, c]))
        node_context.output['result'].set_image(result)

class OverlayImages(OverlayImagesAbstract):
    name = 'Overlay Images'
    nodeid = 'syip.overlay'

    inputs = Ports([
        Port.Custom('image', 'Input images', name='images', n=(2,))
    ])
    outputs = Ports([
        Image('result after filtering', name='result'),
    ])

    __doc__ = ImageFiltering_abstract.generate_docstring(
        OverlayImagesAbstract.description,
        OverlayImagesAbstract.algorithms,
        OverlayImagesAbstract.options_list,
        inputs, outputs)

    def get_input_images(self, node_context):
        return [obj.get_image() for obj in node_context.input.group('images')]

class OverlayImagesList(OverlayImagesAbstract):
    name = 'Overlay Images List'
    nodeid = 'syip.overlay_list'

    inputs = Ports([
        Port.Custom('[image]', 'Input images', name='images')
    ])
    outputs = Ports([
        Image('result after filtering', name='result'),
    ])

    __doc__ = ImageFiltering_abstract.generate_docstring(
        OverlayImagesAbstract.description,
        OverlayImagesAbstract.algorithms,
        OverlayImagesAbstract.options_list,
        inputs, outputs)

    def get_input_images(self, node_context):
        images = []
        for i, obj in enumerate(node_context.input['images']):
            images.append(obj.get_image())
            self.set_progress((50*i)/len(node_context.input['images']))
        return images


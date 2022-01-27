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
import numpy as np

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from skimage import filters
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract
from sylib.imageprocessing.generic_filtering import GenericImageFiltering


API_URL = 'http://scikit-image.org/docs/0.13.x/api/'


def alg_auto_threshold(im, params):
    method = params['auto threshold method'].value
    fns = {
        'otsu': filters.threshold_otsu,
        'yen': filters.threshold_yen,
        'isodata': filters.threshold_isodata,
        'li': filters.threshold_li,
        'minimum': filters.threshold_minimum,
        'mean': filters.threshold_mean,
        'triangle': filters.threshold_triangle,
        'median': lambda x: np.median(x)
    }
    fn = fns[method]
    return im > fn(im)


THRESHOLD_ALGS = {
    'basic': {
        'description': 'Compares each channel with a threshold',
        'threshold': 'Threshold value to compare with',
        'multi_chromatic': False,
        'algorithm': lambda im, par: im >= par['threshold'].value
    },
    'automatic': {
        'description': (
            'Performs global thresholding based a selection of automatic '
            'algorithms with none or few parameters'),
        'auto threshold method': (
            'Method used for calculating threshold'),
        'url': (
            API_URL+'skimage.filters.html'),
        'algorithm': alg_auto_threshold,
        'multi_chromatic': False,
    },
    'adaptive': {
        'description': (
            'Applies an adaptive threshold to an array.\n\n'
            'Also known as local or dynamic thresholding where the '
            'threshold value is the weighted mean for the local '
            'neighborhood of a pixel subtracted by a constant.'),
        'kernel size': (
            'Size of blocks used during threshold check.\n'
            'Must be an odd number. (default 3)'),
        'threshold method': (
            'Method used for calculating adaptive threshold'),
        'offset': (
            'Constant subtracted from weighted mean of neighborhood '
            'to calculate the local threshold value. (default 0.0)'),
        'sigma': (
            'Standard deviation of gaussian kernel when method '
            'gaussian is used.'),
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.filters.html#skimage.filters.threshold_local'),
        'algorithm': lambda im, par: im > filters.threshold_local(
            im, par['kernel size'].value,
            method=par['threshold method'].value,
            offset=par['offset'].value,
            param=par['sigma'].value)
    },
}

THRESHOLD_PARAMETERS = [
    'threshold method', 'auto threshold method', 'threshold',
    'kernel size', 'offset', 'sigma',
]
THRESHOLD_TYPES = {
    'threshold method': ['gaussian', 'mean', 'median'],
    'auto threshold method': [
        'otsu', 'yen', 'isodata', 'li', 'minimum', 'mean', 'triangle', 'median'
    ],
    'offset': float, 'threshold': float, 'kernel size': int, 'sigma': float
}
THRESHOLD_DEFAULTS = {
    'threshold': 0.15, 'kernel size': 21, 'sigma': 21.0,
    'auto threshold method': 'otsu', 'offset': 0.0
}


class ThresholdImage(ImageFiltering_abstract, GenericImageFiltering,
                     node.Node):
    name = 'Threshold image'
    icon = 'image_threshold.svg'
    description = (
        'Applies a threshold to an image giving a boolean output')
    nodeid = 'syip.threshold'
    tags      = Tags(Tag.ImageProcessing.Segmentation)

    algorithms = THRESHOLD_ALGS
    options_list = THRESHOLD_PARAMETERS
    options_types = THRESHOLD_TYPES
    options_default = THRESHOLD_DEFAULTS

    parameters = node.parameters()
    parameters.set_string('algorithm', value=next(iter(algorithms)),
                          description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(parameters, options_types,
                                                options_default)
    inputs = Ports([
        Image('source image to filter', name='source'),
    ])
    outputs = Ports([
        Image('result after filtering', name='result'),
    ])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)

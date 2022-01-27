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
from sympathy.api.nodeconfig import Ports

from skimage import morphology
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract
from sylib.imageprocessing.generic_filtering import GenericImageFiltering


API_URL = 'http://scikit-image.org/docs/0.13.x/api/'
CONVEX_HULL_DESC = (
    'The convex hull is the set of pixels included in the smallest convex'
    'polygon that surround all white pixels in the input image.'
)


def _remove_small_holes(im, area_threshold, connectivity):
    """
    Handling for renamed parameter in remove_small_holes.
    """
    try:
        return morphology.remove_small_holes(
            im, area_threshold=area_threshold, connectivity=connectivity)
    except TypeError:
        # scikit-image <= 0.13.
        return morphology.remove_small_holes(
            im, min_size=area_threshold, connectivity=connectivity)


MORPHOLOGY_ALGS = {
    'labeling': {
        'description': (
            'Creates a unique integer label for each connected component '
            'in an integer valued or binary image.'),
        'diagonal neighborhood': (
            'If true then also consider diagonals for connectivity'),
        'multi_chromatic': False,
        'url': API_URL+'skimage.morphology.html#skimage.morphology.label',
        'algorithm': lambda im, par: morphology.label(
            im,
            connectivity=2 if par['diagonal neighborhood'].value else 1)
    },
    'remove small holes': {
        'description': (
            'Removes small holes from an integer or boolean image.'),
        'diagonal neighborhood': (
            'If true then also consider diagonals for connectivity'),
        'n': 'Maximum size in pixels of areas to remove (default 64)',
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.morphology.html'
            '#skimage.morphology.remove_small_holes'),
        'algorithm': lambda im, par: _remove_small_holes(
            im, area_threshold=par['n'].value,
            connectivity=2 if par['diagonal neighborhood'].value else 1)
    },
    'remove small objects': {
        'description': (
            'Removes connected components smaller than the given size.'),
        'diagonal neighborhood': (
            'If true then also consider diagonals for connectivity'),
        'n': 'Maximum size in pixels of areas to remove (default 64)',
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.morphology.html'
            '#skimage.morphology.remove_small_objects'),
        'algorithm': lambda im, par: morphology.remove_small_objects(
            im, min_size=par['n'].value,
            connectivity=2 if par['diagonal neighborhood'].value else 1)
    },
    'skeletonize': {
        'description': (
            'Returns the skeleton of a binary image. '
            'Thinning is used to reduce each connected component in a '
            'binary image to a single-pixel wide skeleton.'),
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.morphology.html#skimage.morphology.skeletonize'),
        'algorithm': lambda im, par: morphology.skeletonize(im)
    },
    'convex hull, image': {
        'description': (
            'Computes the convex hull of a binary image.\n' +
            CONVEX_HULL_DESC),
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.morphology.html'
            '#skimage.morphology.convex_hull_image'),
        'algorithm': lambda im, par: morphology.convex_hull_image(im)
    },
    'convex hull, objects': {
        'description': (
            'Computes the convex hull of each object in a binary image.\n' +
            CONVEX_HULL_DESC +
            '\nThis function uses labeling to define unique objects, finds'
            'the convex hull of each using convex_hull_image,\nand '
            'combines these regions with logical OR. Be aware the convex'
            'hulls of unconnected objects may overlap in the result'),
        'multi_chromatic': False,
        'url': (
            API_URL + 'skimage.morphology.html'
            '#skimage.morphology.convex_hull_object'),
        'algorithm': lambda im, par: morphology.convex_hull_object(im)
    },
}
MORPHOLOGY_PARAMETERS = ['diagonal neighborhood', 'n']
MORPHOLOGY_TYPES = {
    'n': int,
    'diagonal neighborhood': bool,
}
MORPHOLOGY_DEFAULTS = {
    'n': 12,
    'diagonal neighborhood': False,
}

class MorphologySingleInput(ImageFiltering_abstract, GenericImageFiltering,
                            node.Node):
    name = 'Morphology (single input)'
    icon = 'image_filtering.svg'
    description = (
        'Uses morphology based algorithms with a built-in structuring element')
    nodeid = 'syip.morphology_single_input'

    algorithms = MORPHOLOGY_ALGS
    options_list = MORPHOLOGY_PARAMETERS
    options_types = MORPHOLOGY_TYPES
    options_default = MORPHOLOGY_DEFAULTS

    parameters = node.parameters()
    parameters.set_string('algorithm', value=next(iter(algorithms)),
                          description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(parameters, options_types,
                                                options_default)
    inputs = Ports([Image('source image to filter', name='source')])
    outputs = Ports([Image('result after filtering', name='result')])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)

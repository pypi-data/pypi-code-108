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
import matplotlib.cm
from skimage import filters, feature, exposure, color, morphology, transform
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract
from sylib.imageprocessing.color import grayscale_transform
from sympathy.api.exceptions import SyNodeError, sywarn
import scipy.ndimage.filters


def table_to_image(table):
    data = [column.data for column in table.cols()]
    return np.column_stack(data)


def alg_prewitt(im, params):
    method = params['horizontal/vertical'].value
    if method == 'horizontal':
        return filters.prewitt_h(im)
    elif method == 'vertical':
        return filters.prewitt_v(im)
    else:
        return filters.prewitt(im)


def alg_scharr(im, params):
    method = params['horizontal/vertical'].value
    if method == 'horizontal':
        return filters.scharr_h(im)
    elif method == 'vertical':
        return filters.scharr_v(im)
    else:
        return filters.scharr(im)


def alg_sobel(im, params):
    method = params['horizontal/vertical'].value
    if method == 'horizontal':
        return filters.sobel_h(im)
    elif method == 'vertical':
        return filters.sobel_v(im)
    else:
        return filters.sobel(im)


def alg_roberts(im, params):
    method = params['positive/negative diagonal'].value
    if method == 'positive':
        return filters.roberts_pos_diag(im)
    elif method == 'negative':
        return filters.roberts_neg_diag(im)
    else:
        return filters.roberts(im)


def alg_greyscale(im, params):
    if len(im.shape) == 2:
        result = im
    elif im.shape[2] == 3 and params['luminance preserving'].value:
        result = im.dot(grayscale_transform)
    elif (im.shape[2] == 4 and
          params['luminance preserving'].value and
          params['preserve alpha'].value):
        result = np.zeros(im.shape[:2]+(2,))
        result[:, :, 0] = im[:, :, :3].dot(grayscale_transform)
        result[:, :, 1] = im[:, :, 3]
    elif im.shape[2] == 4 and not params['preserve alpha'].value:
        result = im[:, :, :3].dot(grayscale_transform)
    else:
        result = im.mean(axis=2).reshape(im.shape[:2]+(1,))
    return result


def alg_center_image(im, params):
    x_weights = np.ones(im.shape[:2]) * np.arange(im.shape[1])
    y_weights = (
        np.ones((im.shape[1], im.shape[0])) * np.arange(im.shape[0])
    ).transpose()
    if len(im.shape) < 3:
        im = im.reshape(im.shape+(1,))
    channels = im.shape[2]
    x_w_sum, y_w_sum = 0, 0
    x_sum, y_sum = 0, 0
    for channel in range(channels):
        x_w_sum += np.sum(im[:, :, channel] * x_weights)
        y_w_sum += np.sum(im[:, :, channel] * y_weights)
        x_sum += np.sum(im[:, :, channel])
        y_sum += np.sum(im[:, :, channel])
    xpos = x_w_sum / x_sum
    ypos = y_w_sum / y_sum
    dx = int(xpos - im.shape[1]/2)
    dy = int(ypos - im.shape[0]/2)
    out = np.zeros(im.shape)
    if dx < 0 and dy < 0:
        out[-dy:, -dx:, :] = im[:dy, :dx, :]
    elif dx < 0 and dy >= 0:
        out[:-dy, -dx:, :] = im[dy:, :dx, :]
    elif dx >= 0 and dy < 0:
        out[-dy:, :-dx, :] = im[:dy, dx:, :]
    elif dx >= 0 and dy >= 0:
        out[:-dy, :-dx, :] = im[dy:, dx:, :]
    return out


def alg_padding(im, params):
    if len(im.shape) < 3:
        im = im.reshape(im.shape+(1,))
    add_alpha = params['add alpha'].value
    px, py = params['x'].value, params['y'].value
    px, py = int(px), int(py)
    k = params['k'].value
    max_x = im.shape[1]+abs(px)
    max_y = im.shape[0]+abs(py)
    result = np.full((max_y, max_x, im.shape[2]+add_alpha), k)
    if add_alpha:
        result[max(0, py):max(0, py)+im.shape[0],
               max(0, px):max(0, px)+im.shape[1], :-1] = im
        result[max(0, py):max(0, py)+im.shape[0],
               max(0, px):max(0, px)+im.shape[1], -1] = np.ones(im.shape[:2])
    else:
        result[max(0, py):max(0, py)+im.shape[0],
               max(0, px):max(0, px)+im.shape[1]] = im
    return result


def alg_crop_image(im, params):
    x, y = params['x'].value, params['y'].value
    w, h = params['width'].value, params['height'].value
    shape = im.shape
    x, y = min(x, shape[1]), min(y, shape[0])
    w, h = min(w, shape[1]-x), min(h, shape[0]-y)
    return im[y:y+h, x:x+w]


def alg_resize(im, params):
    req_h = params['height'].value
    req_w = params['width'].value
    h, w = req_h, req_w
    if params['aspect'].value:
        aspect = im.shape[1] / float(im.shape[0])
        size = min(req_w / aspect, req_h)
        w = int(size * aspect)
        h = int(size)

    shape = (h, w) + im.shape[2:]
    result_im = transform.resize(
        im, shape, order=params['interpolation degree'].value)
    if params['padding'].value:
        pad_h = req_h - h
        pad_w = req_w - w
        padded_im = np.zeros((req_h, req_w) + im.shape[2:])
        x0 = int(pad_w/2)
        x1 = x0 + result_im.shape[1]
        y0 = int(pad_h/2)
        y1 = y0 + result_im.shape[0]
        padded_im[y0:y1, x0:x1] = result_im
        return padded_im
    return result_im


def alg_convolution(im, params, tables):
    if len(tables) == 0:
        raise SyNodeError(
            'Convolution filters require second input for kernel '
            '(right-click node to create new input)')
    kernel = table_to_image(tables[0])
    return scipy.ndimage.filters.convolve(
        im, kernel, mode=params['border mode'].value,
        cval=params['k'].value)


def alg_generic_colourspace(im, params, tables):
    if len(tables) == 0:
        raise SyNodeError(
            'Generic colourspace conversion require second table input '
            '(right-click node to create new input)')
    conv = table_to_image(tables[0])
    print("Conv: ", conv)
    rows = conv.shape[0]
    out = np.zeros(im.shape[:2]+(rows,))
    for out_ch in range(rows):
        out[:, :, out_ch] = np.dot(im, conv[out_ch, :])
    return out


def alg_colourmap(im, params):
    if len(im.shape) >= 3 and im.shape[2] != 1:
        sywarn('Colourmap expects a single-channel input')
    if len(im.shape) >= 3:
        im = im[:, :, 0]
    cmap = matplotlib.cm.get_cmap(params['cmap'].value)
    try:
        cols = np.array(cmap.colors)
    except AttributeError:
        cols = cmap(np.linspace(0.0, 1.0, 256))
        if cols.shape[-1] == 4:
            cols = cols[:, :3]
    minv = np.nanmin(im)
    maxv = np.nanmax(im)
    im[np.isnan(im)] = minv
    im = np.round((len(cols)-1) * (im-minv) / (maxv-minv)).astype(np.int)
    return cols[im.ravel()].reshape(im.shape[:2]+(cols.shape[-1],))


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


class ImageFiltering2(ImageFiltering_abstract, node.Node):
    name = 'Filter Image, Dual Output'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'image_filtering_dual.svg'
    description = 'Filters one image using algorithms with two images as output'
    nodeid = 'syip.imagefiltering2'
    tags = Tags(Tag.ImageProcessing.ImageManipulation)

    def alg_hessian_eigenval(im, par):
        hrr, hrc, hcc = feature.hessian_matrix(im, sigma=par['sigma'].value)
        return feature.hessian_matrix_eigvals(hrr, hrc, hcc)

    algorithms = {
        'corner_foerstner': {
            'description': (
                'Computes Foerstner corner measure response images. Outputs '
                'error eclipse sizes (top) and roundness or error eclipse '
                '(bottom).'),
            'sigma': 'Standard deviation of gaussian kernel (default 1.0)',
            'multi_chromatic': False,
            'algorithm': lambda im, par: feature.corner_foerstner(
                im, sigma=par['sigma'].value)
        },
        'hessian eigenvalues': {
            'description': (
                'Computes the eigenvalues of the hessian matrix for each '
                'pixel. Returns larger eigenvalue in first output image and '
                'smaller in second'),
            'multi_chromatic': False,
            'sigma': (
                'Standard deviation of gaussian kernel (default 3.0) used for '
                'calculating Hessian.\nApproximation is not reliable for '
                'sigma < 3.0'),
            'algorithm': alg_hessian_eigenval
        },
    }

    options_list    = ['n', 'sigma', 'threshold']
    options_types   = {'n': int, 'sigma': float, 'threshold': float}
    options_default = {'n': 12, 'sigma': 1.0, 'threshold': 0.15}

    parameters = node.parameters()
    parameters.set_string(
        'algorithm', value=next(iter(algorithms)), description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(
        parameters, options_types, options_default)

    inputs = Ports(
        [Image('source image to filter', name='source'), ]
    )
    outputs = Ports([
        Image('result after filtering', name='resultA'),
        Image('result after filtering', name='resultB'),
    ])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)

    def execute(self, node_context):
        source_obj = node_context.input['source']
        source = source_obj.get_image()
        params = node_context.parameters
        alg_name = params['algorithm'].value

        if len(source.shape) == 3 and source.shape[2] > 1:
            multichannel_image = True
        else:
            multichannel_image = False

        alg = self.algorithms[alg_name]['algorithm']
        if (multichannel_image and
            not self.algorithms[alg_name]['multi_chromatic']):
            # Process each channel separately
            imA1, imB1 = alg(source[:, :, 0], params)
            imA = np.zeros(imA1.shape[:2]+(source.shape[2],))
            imB = np.zeros(imB1.shape[:2]+(source.shape[2],))
            imA[:, :, 0] = imA1
            imB[:, :, 0] = imA1
            for channel in range(1, source.shape[2]):
                result = alg(source[:, :, channel], params)
                imA[:, :, channel], imB[:, :, channel] = result
        else:
            # Process all channels at once
            if len(source.shape) == 3 and source.shape[2] == 1:
                source = source.reshape(source.shape[:2])
            imA, imB = alg(source, params)

        node_context.output['resultA'].set_image(imA)
        node_context.output['resultB'].set_image(imB)

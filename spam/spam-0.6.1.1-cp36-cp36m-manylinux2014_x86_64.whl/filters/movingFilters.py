"""
Library of SPAM filters.
Copyright (C) 2020 SPAM Contributors

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy
import spam.mesh

# Default structural element
#       0 0 0
#       0 1 0
#       0 0 0
#    0 1 0
#    1 2 1
#    0 1 0
# 0 0 0
# 0 1 0
# 0 0 0
structEl = spam.mesh.structuringElement(radius=1, order=1).astype('<f4')
structEl[1, 1, 1] = 2.0


def average(im, structEl=structEl):
    """
    This function calculates the average map of a grey scale image over a structuring element
    It works for 3D and 2D images

    Parameters
    ----------
        im : 3D or 2D numpy array
            The grey scale image for which the average map will be calculated

        structEl : 3D or 2D numpy array, optional
            The structural element defining the local window-size of the operation
            Note that the value of each component is considered as a weight (ponderation) for the operation
            (see `spam.mesh.structured.structuringElement` for details about the structural element)
            Default = radius = 1 (3x3x3 array), order = 1 (`diamond` shape)

    Returns
    -------
        imFiltered : 3D or 2D numpy array
            The averaged image
    """
    import spam.filters.filtersToolkit as mft

    # Detect 2D image:
    if len(im.shape) == 2:
        # pad it
        im = im[numpy.newaxis, ...]
        structEl = structEl[numpy.newaxis, ...]

    imFiltered = numpy.zeros_like(im).astype('<f4')
    mft.average(im, imFiltered, structEl)

    # Return back 2D image:
    if im.shape[0] == 1:
        imFiltered = imFiltered[0, :, :]

    return imFiltered


def variance(im, structEl=structEl):
    """"
    This function calculates the variance map of a grey scale image over a structuring element
    It works for 3D and 2D images

    Parameters
    ----------
        im : 3D or 2D numpy array
            The grey scale image for which the variance map will be calculated

        structEl : 3D or 2D numpy array, optional
            The structural element defining the local window-size of the operation
            Note that the value of each component is considered as a weight (ponderation) for the operation
            (see `spam.mesh.structured.structuringElement` for details about the structural element)
            Default = radius = 1 (3x3x3 array), order = 1 (`diamond` shape)

    Returns
    -------
        imFiltered : 3D or 2D numpy array
            The variance image
    """
    import spam.filters.filtersToolkit as mft

    # Detect 2D image:
    if len(im.shape) == 2:
        # pad it
        im = im[numpy.newaxis, ...]
        structEl = structEl[numpy.newaxis, ...]

    imFiltered = numpy.zeros_like(im).astype('<f4')
    mft.variance(im, imFiltered, structEl)

    # Return back 2D image:
    if im.shape[0] == 1:
        imFiltered = imFiltered[0, :, :]

    return imFiltered


def hessian(im):
    """
    This function computes the hessian matrix of grey values (matrix of second derivatives)
    and returns eigenvalues and eigenvectors of the hessian matrix for each voxel...
    I hope you have a lot of memory!

    Parameters
    -----------
        im: 3D numpy array
            The grey scale image for which the hessian will be calculated

    Returns
    --------
        list containing two lists:
            List 1: contains 3 different 3D arrays (same size as im):
                Maximum, Intermediate, Minimum eigenvalues
            List 2: contains 9 different 3D arrays (same size as im):
                Components Z, Y, X of Maximum
                Components Z, Y, X of Intermediate
                Components Z, Y, X of Minimum eigenvalues
    """
    # 2018-10-24 EA OS MCB "double" hessian fracture filter
    # There is already an imageJ implementation, but it does not output eigenvectors
    import spam.filters.filtersToolkit as ftk

    im = im.astype('<f4')

    # The hessian matrix in 3D is a 3x3 matrix of gradients embedded in each point...
    # hessian = numpy.zeros((3,3,im.shape[0],im.shape[1],im.shape[2]), dtype='<f4' )
    hzz = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    hzy = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    hzx = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    hyz = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    hyy = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    hyx = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    hxz = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    hxy = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    hxx = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigValA = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigValB = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigValC = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigVecAz = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigVecAy = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigVecAx = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigVecBz = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigVecBy = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigVecBx = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigVecCz = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigVecCy = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')
    eigVecCx = numpy.zeros((im.shape[0], im.shape[1], im.shape[2]), dtype='<f4')

    # gaussian
    # gauss = ndi.gaussian_filter(image,sigma=0.5, mode='constant', cval=0)

    # first greylevel derivative, return Z, Y, X gradients
    gradient = numpy.gradient(im)

    # second derivate
    tmp = numpy.gradient(gradient[0])
    hzz = tmp[0]
    hzy = tmp[1]
    hzx = tmp[2]
    tmp = numpy.gradient(gradient[1])
    hyz = tmp[0]
    hyy = tmp[1]
    hyx = tmp[2]
    tmp = numpy.gradient(gradient[2])
    hxz = tmp[0]
    hxy = tmp[1]
    hxx = tmp[2]

    del tmp, gradient

    # run eigen solver for each pixel!!!
    ftk.hessian(hzz, hzy, hzx, hyz, hyy, hyx, hxz, hxy, hxx,
                eigValA, eigValB, eigValC,
                eigVecAz, eigVecAy, eigVecAx,
                eigVecBz, eigVecBy, eigVecBx,
                eigVecCz, eigVecCy, eigVecCx)

    return [[eigValA, eigValB, eigValC], [eigVecAz, eigVecAy, eigVecAx, eigVecBz, eigVecBy, eigVecBx, eigVecCz, eigVecCy, eigVecCx]]


# old equivalent 100% python stuff... way slower
# def _moving_average( im, struct=default_struct ):
#     """
#     Calculate the average of a grayscale image over a 3x3x3 structuring element
#     The output is float32 since results is sometimes outof the uint bounds during computation
#     PARAMETERS:
#     - im (numpy.array): The grayscale image to be treated
#     - struct (array of int): the structural element.
#        Note that the value of each component is considerred as a weight (ponderation) for the operation
#     RETURNS:
#     - o_im (numpy.array float32): The averaged image
#     HISTORY:
#     2016-03-24 (JBC): First version of the function
#     2016-04-05 (ER): generalisation using structural elements
#     2016-05-03 (ER): add progress bar
#     """
#     # Step 1: init output_image as float 32 bits
#     o_im = numpy.zeros( im.shape, dtype='<f4' )
#     # Step 2: structutral element
#     structural_element_size = int( len( struct )/2 )
#     structural_element_weight = float( struct.sum() )
#     if prlv>5:
#         import progressbar
#         max_values = len( numpy.argwhere( struct ) )
#         bar = progressbar.ProgressBar( maxval=max_values, widgets=['Average filter: ', progressbar.Percentage(), progressbar.Bar('=', '[', ']')] )
#         bar.start()
#     for i, c in enumerate( numpy.argwhere( struct ) ):
#         # convert structural element coordinates into shift to apply
#         shift_to_apply = c-structural_element_size
#         # get the local weight from the structural element value
#         current_voxel_weight = float( struct[c[0], c[1], c[2]] )
#         # if prlv>5: print '   Shift {} of weight {}'.format( shift_to_apply, current_voxel_weight )
#         # output_image = output_image + ( voxel_weight * image / element_weight )
#         o_im += current_voxel_weight*sman.multiple_shifts( im, shifts=shift_to_apply )/structural_element_weight
#         if prlv>5: bar.update( i+1 )
#     if prlv>5: bar.finish()
#     return o_im
#
# def _moving_variance( im, struct=default_struct ):
#     """
#     Calculate the variance of a grayscale image over a 3x3x3 structuring element
#     The output is float32 since results is sometimes outof the uint bounds during computation
#     PARAMETERS:
#     - image (numpy.array): The grayscale image to be treat
#     RETURNS:
#     - o_im (numpy.array): The varianced image
#     HISTORY:
#     2016-04-05 (ER): First version of the function
#     """
#     # Step 1: return E(im**2) - E(im)**2
#     return moving_average( numpy.square( im.astype('<f4') ), struct=struct ) - numpy.square( moving_average( im, struct=struct ) )

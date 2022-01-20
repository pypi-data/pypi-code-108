"""
Library of SPAM morphological functions.
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
import spam.helpers
import multiprocessing
import progressbar
import spam.label.label
import scipy.ndimage
import skimage.morphology
# operations on greyscale images

# Global number of processes
nProcessesDefault = multiprocessing.cpu_count()


def greyDilation(im, nBytes=1):
    """
    This function applies a dilation on a grey scale image

    Parameters
    -----------
        im: numpy array
            The input image (greyscale)
        nBytes: int, default=1
            Number of bytes used to substitute the values on the border.

    Returns
    --------
        numpy array
            The dilated image
    """
    # Step 1: check type and dimension
    dim = len(im.shape)
    # Step 2: Determine substitution value
    sub = 2**(8 * nBytes) - 1
    # Step 3: apply dilation                                                          #  x  y  z
    outputIm = im                                                                     # +0  0  0
    outputIm = numpy.maximum(outputIm, spam.helpers.singleShift(im, 1, 0, sub=sub))   # +1  0  0
    outputIm = numpy.maximum(outputIm, spam.helpers.singleShift(im, -1, 0, sub=sub))  # -1  0  0
    outputIm = numpy.maximum(outputIm, spam.helpers.singleShift(im, 1, 1, sub=sub))   # +0  1  0
    outputIm = numpy.maximum(outputIm, spam.helpers.singleShift(im, -1, 1, sub=sub))  # +0 -1  0
    if dim == 3:
        outputIm = numpy.maximum(outputIm, spam.helpers.singleShift(im, 1, 2, sub=sub))   # 0  0  1
        outputIm = numpy.maximum(outputIm, spam.helpers.singleShift(im, -1, 2, sub=sub))  # 0  0 -1
    return outputIm


def greyErosion(im, nBytes=1):
    """
    This function applies a erosion on a grey scale image

    Parameters
    -----------
        im: numpy array
            The input image (greyscale)
        nBytes: int, default=1
            Number of bytes used to substitute the values on the border.

    Returns
    --------
        numpy array
            The eroded image
    """
    # Step 1: check type and dimension
    dim = len(im.shape)
    # Step 2: Determine substitution value
    sub = 2**(8 * nBytes) - 1
    # Step 1: apply erosion                                                       #  x  y  z
    outputIm = im  # 0  0  0
    outputIm = numpy.minimum(outputIm, spam.helpers.singleShift(im, 1, 0, sub=sub))  # 1  0  0
    outputIm = numpy.minimum(outputIm, spam.helpers.singleShift(im, -1, 0, sub=sub))  # -1  0  0
    outputIm = numpy.minimum(outputIm, spam.helpers.singleShift(im, 1, 1, sub=sub))  # 0  1  0
    outputIm = numpy.minimum(outputIm, spam.helpers.singleShift(im, -1, 1, sub=sub))  # 0 -1  0
    if dim == 3:
        outputIm = numpy.minimum(outputIm, spam.helpers.singleShift(im, 1, 2, sub=sub))  # 0  0  1
        outputIm = numpy.minimum(outputIm, spam.helpers.singleShift(im, -1, 2, sub=sub))  # 0  0 -1
    return outputIm


def greyMorphologicalGradient(im, nBytes=1):
    """
    This function applies a morphological gradient on a grey scale image

    Parameters
    -----------
        im: numpy array
            The input image (greyscale)
        nBytes: int, default=1
            Number of bytes used to substitute the values on the border.

    Returns
    --------
        numpy array
            The morphologycal gradient of the image
    """
    return (greyDilation(im, nBytes=nBytes) - im)


# operation on binary images

def binaryDilation(im, sub=False):
    """
    This function applies a dilation on a binary scale image

    Parameters
    -----------
        im: numpy array
            The input image (greyscale)
        sub: bool, default=False
            Subtitute value.

    Returns
    --------
        numpy array
            The dilated image
    """
    # Step 0: import as bool
    im = im.astype(bool)
    # Step 1: check type and dimension
    dim = len(im.shape)
    # Step 1: apply dilation                             #  x  y  z
    outputIm = im  # 0  0  0
    outputIm = outputIm | spam.helpers.singleShift(im, 1, 0, sub=sub)  # 1  0  0
    outputIm = outputIm | spam.helpers.singleShift(im, -1, 0, sub=sub)   # -1  0  0
    outputIm = outputIm | spam.helpers.singleShift(im, 1, 1, sub=sub)  # 0  1  0
    outputIm = outputIm | spam.helpers.singleShift(im, -1, 1, sub=sub)  # 0 -1  0
    if dim == 3:
        outputIm = outputIm | spam.helpers.singleShift(im, 1, 2, sub=sub)  # 0  0  1
        outputIm = outputIm | spam.helpers.singleShift(im, -1, 2, sub=sub)  # 0  0 -1
    return numpy.array(outputIm).astype('<u1')


def binaryErosion(im, sub=False):
    """
    This function applies a erosion on a binary scale image

    Parameters
    -----------
        im: numpy array
            The input image (greyscale)
        sub: bool, default=False
            Substitute value.

    Returns
    --------
        numpy array
            The eroded image
    """
    # Step 1: apply erosion with dilation --> erosion = ! dilation( ! image )
    return numpy.logical_not(binaryDilation(numpy.logical_not(im), sub=sub)).astype('<u1')


def binaryMorphologicalGradient(im, sub=False):
    """
    This function applies a morphological gradient on a binary scale image

    Parameters
    -----------
        im: numpy array
            The input image (greyscale)
        nBytes: int, default=False
            Number of bytes used to substitute the values on the border.

    Returns
    --------
        numpy array
            The morphologycal gradient of the image
    """
    return (numpy.logical_xor(binaryDilation(im, sub=sub), im)).astype('<u1')


def binaryGeodesicReconstruction(im, marker, dmax=None, verbose=False):
    """
    Calculate the geodesic reconstruction of a binary image with a given marker

    Parameters
    -----------
        im: numpy.array
            The input binary image

        marker: numpy.array or list
            If numpy array: direct input of the marker (must be the size of im)
            If list: description of the plans of the image considered as the marker
            | ``[1, 0]`` plan defined by all voxels at ``x1=0``
            | ``[0, -1]`` plan defined by all voxels at ``x0=x0_max``
            | ``[0, 0, 2, 5]`` plans defined by all voxels at ``x0=0`` and ``x2=5``

        dmax: int, default=None
            The maximum geodesic distance. If None, the reconstruction is complete.

        verbose: bool, default=False
            Verbose mode

    Returns
    --------
        numpy.array
            The reconstructed image
    """
    from spam.errors import InputError

    # Step 1: Define marker
    if isinstance(marker, list):
        # marker based on list of plans
        if len(marker) % 2:
            raise InputError("marker", explanation="len(marker) must be a multiple of 2")

        plans = marker[:]
        marker = numpy.zeros(im.shape, dtype=bool)
        for i in range(len(plans) // 2):
            direction = plans[2 * i]
            distance = plans[2 * i + 1]
            if len(im.shape) == 2:
                if direction == 0:
                    marker[distance, :] = im[distance, :]
                elif direction == 1:
                    marker[:, distance] = im[:, distance]
                else:
                    raise InputError("marker", explanation=f"Wrong marker plan direction {direction}")

            elif len(im.shape) == 3:
                if direction == 0:
                    marker[distance, :, :] = im[distance, :, :]
                elif direction == 1:
                    marker[:, distance, :] = im[:, distance, :]
                elif direction == 2:
                    marker[:, :, distance] = im[:, :, distance]
                else:
                    raise InputError("marker", explanation=f"Wrong marker plan direction {direction}")

            else:
                raise InputError("marker", explanation=f"Image dimension should be 2 or 3, not {len(im.shape)}")

            if verbose:
                print(f"binaryGeodesicReconstruction: marker -> set plan in direction {direction} at distance {distance}")

    elif isinstance(marker, numpy.ndarray):
        # direct input of the marker
        if im.shape != marker.shape:
            raise InputError("marker", explanation="im and marker must have same shape")
    else:
        raise InputError("marker", explanation="must be a numpy array or a list")

    # Step 2: first dilation and intersection
    r1 = binaryDilation(marker) & im
    r2 = r1
    r1 = binaryDilation(r2) & im
    d = 1
    dmax = numpy.inf if dmax is None else dmax
    if verbose:
        print(f'binaryGeodesicReconstruction: geodesic distance = {d} (sum = {r1.sum()} & {r2.sum()})')

    # binary dilation until:
    #   geodesic distance reach dmax
    #   reconstuction complete
    while not numpy.array_equal(r1, r2) and d < dmax:
        r2 = r1
        r1 = binaryDilation(r2) & im
        d += 1
        if verbose:
            print(f'binaryGeodesicReconstruction: geodesic distance = {d} (sum = {r1.sum()} & {r2.sum()})')

    return r1  # send the reconstructed image


def directionalErosion(bwIm, vect, a, c, nProcesses=nProcessesDefault, verbose = False):
    """
    This functions performs direction erosion over the binarized image using
    an ellipsoidal structuring element over a range of directions. It is highly
    recommended that the structuring element is slightly smaller than the 
    expected particle (50% smaller in each axis is a fair guess)

    Parameters
    -----------
        bwIm : 3D numpy array
            Binarized image to perform the erosion

        vect : list of n elements, each element correspond to a 1X3 array of floats
            List of directional vectors for the structuring element

        a : int or float
            Length of the secondary semi-axis of the structuring element in px

        c : int or float
            Lenght of the principal semi-axis of the structuring element in px

        nProcesses : integer (optional, default = nProcessesDefault)
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : boolean, optional (Default = False)
            True for printing the evolution of the process
            False for not printing the evolution of process

    Returns
    --------
        imEroded : 3D boolean array
            Booean array with the result of the erosion

    Note
    -----
        Taken from https://sbrisard.github.io/posts/20150930-orientation_correlations_among_rice_grains-06.html

    """


    #Check if the directional vector input is a list
    if isinstance(vect,list) == False:
        print("spam.contacts.directionalErosion: The directional vector must be a list")
        return

    numberOfJobs = len( vect )
    imEroded = numpy.zeros(bwIm.shape)

    # Function for directionalErosion
    global funDirectionalErosion
    def funDirectionalErosion(job):
        maxDim = numpy.max([a,c])
        spheroid = spam.kalisphera.makeBlurryNoisySpheroid([maxDim,maxDim,maxDim],
                                                    [numpy.floor(maxDim/2), numpy.floor(maxDim/2), numpy.floor(maxDim/2)],
                                                    [a,c],
                                                    vect[job],
                                                    background=0,
                                                    foreground=1)
        imEroded_i = scipy.ndimage.binary_erosion(bwIm, structure = spheroid)
        return imEroded_i

    if verbose:
        widgets = [progressbar.FormatLabel(''), ' ', progressbar.Bar(), ' ', progressbar.AdaptiveETA()]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=numberOfJobs)
        pbar.start()
        finishedNodes = 0

    # Run multiprocessing
    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(funDirectionalErosion, range(0, numberOfJobs)):
            if verbose:
                finishedNodes += 1
                widgets[0] = progressbar.FormatLabel("{}/{} ".format(finishedNodes, numberOfJobs))
                pbar.update(finishedNodes)
            imEroded = imEroded + returns
        pool.close()
        pool.join()

    if verbose:
        pbar.finish()

    return imEroded


def morphologicalReconstruction(im, selem = None):
    """
    This functions performs a complete morphological reconstruction (reconstruction
    by dilation followed by a reconstruction by erosion. The ouput image presents less
    variability in the greyvalues inside each phase, without modifying the original
    shape of the objects of the image.
    -

    Parameters
    -----------
        im : 3D numpy array
            Greyscale image to perform the reconstuction

        selem : structuring element, optional
            Structuring element
            Default = None

    Returns
    --------
        imReconstructed : 3D boolean array
            Greyscale image after the reconstuction

    """
    #Create the seed for the dilation
    imErosion = skimage.morphology.erosion(im,selem = selem)
    #Dilate the seed until it reaches the mask
    imOpening = skimage.morphology.reconstruction(seed = imErosion, mask = im, method = 'dilation')
    #Create the seed for the dilation
    imDilation = skimage.morphology.dilation(imOpening, selem = selem)
    #Erode the seed until it reaches the mask
    imReconstructed = skimage.morphology.reconstruction(seed = imDilation, mask = imOpening, method='erosion')

    return imReconstructed

"""
Library of SPAM functions for manipulating images
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
import tifffile
import spam.label
import progressbar

def stackToArray(prefix, sufix='.tif', stack=range(10), digits='05d', erosion=False, verbose=False):
    """
    Convert of stack of 2D sequential tif images into a 3D array.

    Parameters
    ----------
        prefix : string
            The common name of the 2D images files before the sequential number

        sufix : string, default='.tif'
            The common name and extension of the 2D images after the sequential number

        stack : sequence, default=range(10)
            The numbers of the slices with no formating (with no leading zeros)

        digits : string, default='05d'
            The format (number of digits) of the numbers (add leading zeros).

        erosion : bool, default=None
            Apply an erosion of 1px to the mask in order to avoid border noise.

        verbose: bool, default=False
            Verbose mode if True.

    Returns
    -------
        im : array
            The 3D image

        mask : array
            The 3D mask (full of 1 if ``createMask=None``)
    """

    if verbose:
        print("spam.helpers.imageManipulation.stackToArray:")
        print('\tfrom: {p}{first:{d}}{s}'.format(p=prefix, s=sufix, first=stack[0], d=digits))
        print('\tto:   {p}{last:{d}}{s}'.format(p=prefix, s=sufix, last=stack[-1], d=digits))

    # Step 1 If nBytes is not defined: we open the first slice just for the dimensions
    slice_name = '{h}{s:{d}}{t}'.format(h=prefix, t=sufix, s=stack[0], d=digits)
    slice_im = tifffile.imread(slice_name)

    # Step 2 compute the dimension and create the 3D array
    ny = slice_im.shape[0]
    nx = slice_im.shape[1]
    nz = len(stack)
    im = numpy.zeros([nz, ny, nx], dtype=slice_im.dtype)

    # Step 2.1 create empty mask (8 bits)
    mask = numpy.ones([nz, ny, nx], dtype='<u1')

    # Step 3 stack all the slices
    for i, s in enumerate(stack):
        slice_name = '{h}{s:{d}}{t}'.format(h=prefix, t=sufix, s=s, d=digits)
        if verbose:
            print('\tStack slice number {}/{} ({s:{d}})'.format(i + 1, len(stack), s=s, d=digits))
        im[i, :, :] = tifffile.imread(slice_name)
        # we fill the mask
        #if createMask:
            #mask[i, :, :] = _mask2D(im[i, :, :], erosion=erosion)

    return im, mask


def crop(im, boxSize, boxOrigin=None):
    """
    This function crops an image using slicing.

    Parameters
    ----------
        im: array
            The image to crop.

       boxSize: int
            The size in voxels of the crop box (from boxOrigin). If a int, the size is the same for each axis. If a sequence, ``boxSize`` should contain one value for each axis.

        boxOrigin : int, default=None
            The coordinates in voxels of the origin of the crop box. If a int, the coordinates are the same for each axis. If a tuple, ``boxOrigin`` should contain one value for each axis. If ``None`` the image is cropped from its centre.

    Returns
    -------
        array
            The cropped image.
    """

    # get center of the image
    imCentre = [int(s) / 2 for s in im.shape]
    # get sizes
    (sz, sy, sx) = (boxSize, boxSize, boxSize) if isinstance(boxSize, int) else boxSize

    # get box origin
    if boxOrigin is not None:
        (cz, cy, cx) = (boxOrigin, boxOrigin, boxOrigin) if isinstance(boxOrigin, int) else boxOrigin
    else:
        (cz, cy, cx) = (imCentre[0] - sz // 2, imCentre[1] - sy // 2, imCentre[2] - sx // 2)

    # test sizes
    if (cz + sz > im.shape[0] or cy + sy > im.shape[1] or cx + sx > im.shape[2]):
        print("spam.helpers.imageManipulation.crop: box bigger than image.")
        print("exit function.")
        return -1

    return im[int(cz):int(cz + sz),
              int(cy):int(cy + sy),
              int(cx):int(cx + sx)]


def rescale(im, scale=(0, 1)):
    """
    This function **rescales** the values of an image according to a scale
    and save it to as n bytes floats.

    Parameters
    ----------
        im: array
            The image to rescale

        scale : (float, float), default=(0 1)
            The min and max of the rescaled image

    Returns
    -------
        array, float
            The rescaled image.

    Examples
    --------
        >>> im = numpy.random.randn( 100, 100, 100 ).astype( '<f4' )
        produce float32 array of positive and negative numbers
        >>> imRescaled = rescale( im, scale=[-1, 1] )
        produce float32 array of numbers between -1 and 1

    """

    im_max = float(im.max())
    im_min = float(im.min())

    return (min(scale) + (max(scale) - min(scale)) * ((im.astype('<f4') - im_min) / (im_max - im_min))).astype('<f4')


def rescaleToInteger(im, nBytes=1, scale=None):
    """
    This function **rescales** image values to an unsigned integer.

    Parameters
    ----------
        im: array, float32
            The image to rescale

        nBytes : int, default=1
            The number of bytes of the unsigned interger output.
            Possible values are power of 2

            .. code-block:: text

                reminder
                1 byte  =  8 bits -> ouput from 0 to           255
                2 bytes = 16 bits -> ouput from 0 to        65 535
                4 bytes = 32 bits -> ouput from 0 to 4 294 967 295

        scale : (float, float), default=None
            If None, the maximum and minimum use for the rescaling is the maximum and the minimum of the image

    Returns
    -------
        array, uint
            The rescaled image

    Examples
    --------
        >>> im = numpy.random.randn( 100, 100, 100 ).astype( '<f4' )
        produce float32 array of positive and negative numbers
        >>> imRescaled = rescaleToInteger( im, nBytes=4 )
        produce uint32 array of numbers between 0 and 4 294 967 295

    """

    nBytes = int(nBytes)
    if ((nBytes & (nBytes - 1)) != 0):
        print("spam.helpers.imageManipulation.rescaleToInteger: nBytes = {}. Should be a power of 2.".format(nBytes))
        print("exit function.")
        return -1

    if scale is None:
        # if no scale is given: it takes the max and min of the image
        im_max = im.max()
        im_min = im.min()
    else:
        # if a scale is given take it if larger (smaller) than max (min) of image
        # im_max = max(scale) if max(scale) > im.max() else im.max()
        # im_min = min(scale) if min(scale) < im.min() else im.min()
        im_max = max(scale)
        im_min = min(scale)
        im[im > im_max] = im_max
        im[im < im_min] = im_min

    im_min = float(im_min)
    im_max = float(im_max)

    return ((2**(8 * nBytes) - 1) * ((im.astype('<f4') - im_min) / (im_max - im_min))).astype('<u{}'.format(nBytes))


def convertUnsignedIntegers(im, nBytes=1):
    """
    This function **converts** an images of unsigned integers.

    Note: this function does not rescale.

    Parameters
    ----------
        im: array, uint
            The image to convert.

        nBytes : int, default=1
            The number of bytes of the unsigned interger output.
            Possible values are power of 2.

            .. code-block:: text

                reminder
                1 byte  =  8 bits -> ouput from 0 to           255
                2 bytes = 16 bits -> ouput from 0 to        65 535
                4 bytes = 32 bits -> ouput from 0 to 4 294 967 295

    Returns
    -------
        array, uint
            The converted image.

    Examples
    --------
        >>> im = numpy.random.randint( 12, high=210, size=(100, 100, 100) ).astype( '<u1' )
        produce an uint8 array of numbers between 12 and 210
        >>> imRescaled = rescaleToInteger( im, nBytes=2 )
        produce an uint16 array 3084 and 53970

    """

    nBytes = int(nBytes)
    if ((nBytes & (nBytes - 1)) != 0):
        print('spam.helpers.imageManipulation.convertUnsignedIntegers: nBytes = {}. Should be a power of 2.'.format(nBytes))
        print("exit function.")
        return -1

    # number of bits of the output
    nbo = 8 * nBytes

    # number of bits of the input
    inputType = im.dtype
    if inputType == numpy.uint8:
        nbi = 8
    elif inputType == numpy.uint16:
        nbi = 16
    elif inputType == numpy.uint32:
        nbi = 32
    elif inputType == numpy.uint64:
        nbi = 64
    else:
        print('spam.helpers.imageManipulation.convertUnsignedIntegers: im.dytpe = {}. Input should be uint.'.format(inputType))
        print("exit function.")
        return -1

    return (float(2**nbo - 1) * (im) / float(2**nbi - 1)).astype('<u{}'.format(nBytes))


def singleShift(im, shift, axis, sub=0):
    """
    This function shift the image and replace the border by an substitution value.

    It uses ``numpy.roll``.

    Parameters
    -----------
        im : array
            The input to shift.
        shift : int
            The number of places by which elements are shifted (from numpy.roll).
            Default: 1
        axis : int
            The axis along which elements are shifted (from numpy.rool).
        sub : foat, default=0
            The substitution value of the border

    Returns
    -------
        array :
            The shifted image.

    """

    # Step 1: Cyclic permutation on im
    im = numpy.roll(im, shift, axis=axis)

    # Step 2: get image dimension
    dim = len(im.shape)

    # Step 3: modify the boundary with replacement value
    if dim == 2:  # if 2D image
        if shift == 1 and axis == 0:
            im[0, :] = sub
        elif shift == -1 and axis == 0:
            im[-1, :] = sub
        elif shift == 1 and axis == 1:
            im[:, 0] = sub
        elif shift == -1 and axis == 1:
            im[:, -1] = sub
    elif dim == 3:  # if 3D image
        if shift >= 1 and axis == 0:
            im[0:shift, :, :] = sub
        elif shift <= -1 and axis == 0:
            im[shift:, :, :] = sub
        elif shift >= 1 and axis == 1:
            im[:, 0:shift, :] = sub
        elif shift <= -1 and axis == 1:
            im[:, shift:, :] = sub
        elif shift >= 1 and axis == 2:
            im[:, :, 0:shift] = sub
        elif shift <= -1 and axis == 2:
            im[:, :, shift:] = sub
    else:
        print("spam.helpers.imageManipulation.singleShift: dim={}. Should be 2 or 3.".format(dim))
        print("exit function.")
        return -1

    return im


def multipleShifts(im, shifts, sub=0):
    """
    This function call ``singleShift`` multiple times.

    Parameters
    ----------
        im : array
            The input to shift.
        shifts : [int, int, int]
            Defines the number of shifts to apply in every axis.

            .. code-block:: text

                shift = [s_x, s_y, s_z] applies a shift of:
                .   s_x on axis 0
                .   s_y on axis 1
                .   s_z on axis 2

        sub : float, default=0
            The substitution value of the border

    Returns
    -------
        array :
            The shifted image.

    """

    # loop over the n axis
    for i in range(len(shifts)):
        # if the value of the shift is not 0 on axis i
        if shifts[i]:
            # we call singleShift (only once)
            im = singleShift(im, shift=shifts[i], axis=i)

    return im


def _binarisation(im, threshold=0.0, boolean=False, op='>', mask=None):
    """
    This function binarise an input image according to a given threshold

    It has an option to apply a mask to the binarized image to ignore the
    outside of the sample/specimen

    Parameters
    -----------
        im: array
            The image to binarise.

        threshold : float
            the input limit value for binarization

        boolean : bool
            Changes the output format and phase distribution (see output)

        op : string, default='>'
            defines the thresholding operation

        mask : array, default=None
            The mask of the input image: is 0 outside the boundary(specimen) and 1 inside

    Returns
    --------
        phases : array
            The repartition of phases resulting the binarisation.

            For operator '>' it gives, if ``boolean=True``:

            .. code-block:: text

                0 - masked parts (where mask equals 0)
                0 - below threshold
                1 - above threshold

            and if ``boolean=False``

            .. code-block:: text

                0 - masked parts (where mask equals 0)
                1 - below threshold
                2 - above threshold
    """

    import operator

    # Step 1: Get operator
    operation = {'>': operator.gt,
                 '<': operator.lt,
                 '>=': operator.ge,
                 '<=': operator.le,
                 '=': operator.eq}.get(op)

    # Step 2: binarisation
    phases = operation(im, threshold).astype('<u1')

    # Step 3: rescaling if bool
    if not boolean:
        phases += 1

    # Step 4: apply mask
    if mask is not None:
        phases = phases * mask

    return phases


def slicePadded(im, startStop, createMask=False, padValue=0, verbose=False):
    """
    Extract slice from im, padded with zeros, which is always of the dimensions asked (given from startStop)

    Parameters
    ----------
        im : 3D numpy array
            The image to be sliced

        startStop : 6 component list of ints
            This array contains:
            [Zmin, Zmax, Ymin, Ymax, Xmin, Xmax]

        createMask : bool, optional
            If True, return a padded slice, which is False when the slice falls outside im
            Default = False

    Returns
    -------
        imSliced : 3D numpy array
            The sliced image

        mask : 3D numpy array of bools
            The 3D mask, only returned if createMask is True
    """
    startStop = numpy.array(startStop).astype(int)

    assert (startStop[1]>startStop[0]), "spam.helpers.slicePadded(): Zmax should be bigger than Zmin"
    assert (startStop[3]>startStop[2]), "spam.helpers.slicePadded(): Ymax should be bigger than Ymin"
    assert (startStop[5]>startStop[4]), "spam.helpers.slicePadded(): Xmax should be bigger than Xmin"

    imSliced = numpy.zeros((startStop[1]-startStop[0],
                            startStop[3]-startStop[2],
                            startStop[5]-startStop[4]), dtype=im.dtype) + padValue

    start       = numpy.array([startStop[0],     startStop[2],     startStop[4]])
    stop        = numpy.array([startStop[1],     startStop[3],     startStop[5]])
    startOffset = numpy.array([max(0, start[0]), max(0, start[1]), max(0, start[2])])
    stopOffset  = numpy.array([min(im.shape[0], stop[0]), min(im.shape[1], stop[1]), min(im.shape[2], stop[2])])
    startLocal  = startOffset - start
    stopLocal   = startLocal + stopOffset - startOffset

    # Check condition that we're asking for a slice of data wholly outside im
    #   This means either that the stop values are all smaller than 0
    #   OR the start are all bigger than im.shape
    if numpy.any(stop < numpy.array([0, 0, 0])) or numpy.any(start >= numpy.array(im.shape)):
        if verbose: print("spam.helpers.slicePadded(): The extracted padded slice doesn't not touch the image!")
        imSliced = imSliced.astype('<f4')
        imSliced *= numpy.nan
        if createMask:
            return imSliced, numpy.zeros_like(imSliced, dtype=bool)

    else:
        imSliced[startLocal[0]:stopLocal[0],
                 startLocal[1]:stopLocal[1],
                 startLocal[2]:stopLocal[2]] = im[startOffset[0]:stopOffset[0],
                                                  startOffset[1]:stopOffset[1],
                                                  startOffset[2]:stopOffset[2]]
        if createMask:
            mask = numpy.zeros_like(imSliced, dtype=bool)
            mask[startLocal[0]:stopLocal[0], startLocal[1]:stopLocal[1], startLocal[2]:stopLocal[2]] = 1
            return imSliced, mask

    return imSliced


def splitImage(im, divisions, margin, verbose=True):
    """
    Divides the image in zDiv x yDiv x xDiv blocks, each block is padded 
    with a margin.

    Parameters
    ----------
        im : 3D numpy array
            The image to be splitted

        divisions : 3-component list of ints
            Desired number of blocks along Z, Y, X axes

        margin : int
            Overlapping margin between each block.
            For applying a filter on subvolumes, it is recommended to use a margin of 1.5 times the filter diameter.
            For labelled data it is recommended that the margin is at least 1.5 times bigger than the particles largest axis

        verbose : bool
            Print the parameters of the operations (number of blocks and margin)
            Default = True

    Returns
    -------
        output: Dictionary
            Dictionary with keys labelled acoording to the position of the block along each axis (e.g., 000, 001, 002,...)
            Each element (e.g., 001) within the dictionary carries the block origin and the resulting block, in that order

    Note
    ----
        This function should be used along `spam.helpers.imageManipulation.rebuildImage()`

    """
    zDiv, yDiv, xDiv = divisions

    # Check if the slices can be made
    if zDiv >= im.shape[0]:
        print('spam.helpers.imageManipulation.splitImage: Incorrect number of slices for axis z')
        print("exit function.")
        return -1
    if yDiv >= im.shape[1]:
        print('spam.helpers.imageManipulation.splitImage: Incorrect number of slices for axis y')
        print("exit function.")
        return -1
    if xDiv >= im.shape[2]:
        print('spam.helpers.imageManipulation.splitImage: Incorrect number of slices for axis x')
        print("exit function.")
        return -1

    # Check that margin is not greater than the slice
    if margin >= im.shape[0]/zDiv:
        print('spam.helpers.imageManipulation.splitImage: Margin is too big for z axis')
        print("exit function.")
        return -1
    if margin >= im.shape[1]/yDiv:
        print('spam.helpers.imageManipulation.splitImage: Margin is too big for y axis')
        print("exit function.")
        return -1
    if margin >= im.shape[2]/xDiv:
        print('spam.helpers.imageManipulation.splitImage: Margin is too big for x axis')
        print("exit function.")
        return -1
    # Print parameters if needed
    if verbose==True:
        print('spam.helpers.imageManipulation.splitImage: Working with margin of ', margin, '. The total number of blocks is ', zDiv*yDiv*xDiv)

    # Pad initial image with zeros on the edge
    imPad = numpy.pad(im, margin, mode='edge')

    # Compute size of blocks
    zSize = int(im.shape[0]/zDiv)
    ySize = int(im.shape[1]/yDiv)
    xSize = int(im.shape[2]/xDiv)

    # Create return dictionary
    output = {}
   
    # Iterate through each block
    for zBlock in range(zDiv):
        for yBlock in range(yDiv):
            for xBlock in range(xDiv):
                # Get the origin of each block   
                blockOrigin = numpy.array([zBlock*zSize,
                                           yBlock*ySize,
                                           xBlock*xSize])
                blockSize = [zSize, ySize, xSize]
                # Check if the size needs to be changed to fit the image
                if zBlock == zDiv - 1 and im.shape[0] % zDiv !=0:
                    blockSize[0] = zSize + (im.shape[0] % zDiv)
                if yBlock == yDiv - 1 and im.shape[1] % yDiv !=0:
                    blockSize[1] = ySize + (im.shape[1] % yDiv)
                if xBlock == xDiv - 1 and im.shape[2] % xDiv !=0:
                    blockSize[2] = xSize + (im.shape[2] % xDiv)

                # Generate block with the margin on all sides
                imBlock = crop(imPad,
                               (blockSize[0] + 2*margin, blockSize[1] + 2*margin, blockSize[2] + 2*margin),
                               boxOrigin=(blockOrigin[0], blockOrigin[1], blockOrigin[2]))
                # Save the results
                output.update({str(zBlock) + str(yBlock) + str(xBlock): [blockOrigin, imBlock]})
    # Save the margin
    output.update({'margin':margin})

    # Return
    return output


def rebuildImage(listBlocks, listCoordinates, margin, mode, keepLabels=False, verbose=True):
    """
    Rebuilds splitted image from `spam.helpers.imageManipulation.splitImage()`.

    Parameters
    ----------
        listBlocks : list
            List of the 3D blocks that will form the re-built the image.
            Note: The order of listBlocks should be equivalent to the order of listCoordinates

        listCoordinates : list
            List of the origin coordinates of each block. (Usually taken from `spam.helpers.imageManipulation.splitImage()`)
            Note: The order of listCoordinates should be equivalent to the order of listBlocks

        margin : integer
            Value of the margin used for the images. (Usually taken from `spam.helpers.imageManipulation.splitImage()`)

        mode : string
            'grey' : re-builds 3D greyscale arrays
            'label' : re-builds 3D labelled arrays

        keepLabels : bool
            Do we need to want to keep the current labels from the blocks, or create a new one?
            Default = False
            
        verbose : bool
            Print the evolution of the operation
            Default = True

    Returns
    -------
        imBuild : 3D numpy array
            Re-built image without the margins

    Note
    ----
        This function should be used along with `spam.helpers.imageManipulation.splitImage()`

    """

    # Checking if listBlocks and listCoordinates have the same length
    if len(listBlocks) != len(listCoordinates):
        print('spam.helpers.imageManipulation.splitImage: listBlocks and listCoordinates must have the same length')
        return -1

    # Transform listCoordinates into array
    arrayCoord = numpy.asarray(listCoordinates)

    # Checking if all the origin coordinates are different
    _, counts = numpy.unique(arrayCoord, axis=0, return_counts=True)
    if len(counts) != len(arrayCoord):
        print('spam.helpers.imageManipulation.splitImage: coordinates in listCoordinates must be all different')
        return -1

    if verbose:
        # Create progressbar
        widgets = [progressbar.FormatLabel(''), ' ', progressbar.Bar(), ' ', progressbar.AdaptiveETA()]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(listCoordinates))
        pbar.start()
        finishedBlocks = 0

    if mode == 'grey':

        # Shape of the block opposite to the origine
        shapeLast = listBlocks[numpy.argmax(numpy.sum(arrayCoord, axis=1))].shape

        # Tentative size of the final image
        zSize = numpy.amax(arrayCoord[:, 0]) + shapeLast[0] - 2*margin
        ySize = numpy.amax(arrayCoord[:, 1]) + shapeLast[1] - 2*margin
        xSize = numpy.amax(arrayCoord[:, 2]) + shapeLast[2] - 2*margin

        # Initialising rebuild image
        imBuild = numpy.zeros((zSize, ySize, xSize))

        # Loop on the length to lists, so to replace zeros in imBuild with the actual values at the right position
        for i in range(len(listCoordinates)):
            origin = listCoordinates[i]
            blockPad = listBlocks[i]

            if margin == 0:
                imBuild[origin[0]:origin[0]+blockPad.shape[0] - 2*margin,
                        origin[1]:origin[1]+blockPad.shape[1] - 2*margin,
                        origin[2]:origin[2]+blockPad.shape[2] - 2*margin] = blockPad
            else:
                imBuild[origin[0]:origin[0]+blockPad.shape[0] - 2*margin,
                        origin[1]:origin[1]+blockPad.shape[1] - 2*margin,
                        origin[2]:origin[2]+blockPad.shape[2] - 2*margin] = blockPad[margin:-margin, margin:-margin, margin:-margin]
            if verbose:
                # Update the progressbar
                finishedBlocks += 1
                widgets[0] = progressbar.FormatLabel("{}/{} ".format(finishedBlocks, len(listCoordinates)))
                pbar.update(finishedBlocks)
        print('\n\t')
        return imBuild

    if mode == 'label':

        # Shape of the block opposite to the origine
        shapeLast = listBlocks[numpy.argmax(numpy.sum(arrayCoord, axis = 1))].shape

        # Size of the final image
        zSize = numpy.amax(arrayCoord[:, 0]) + shapeLast[0] - 2*margin
        ySize = numpy.amax(arrayCoord[:, 1]) + shapeLast[1] - 2*margin
        xSize = numpy.amax(arrayCoord[:, 2]) + shapeLast[2] - 2*margin

        # Initialising rebuild image
        imBuild = numpy.zeros((zSize, ySize, xSize))
        # Loop over the lists
        for i in range(len(listCoordinates)):
            # Get the origin of the block
            origin = listCoordinates[i]
            # Get the block
            block = listBlocks[i]
            # Compute the bounding boxes
            boundingBoxes = spam.label.boundingBoxes(block)
            # Compute centre of mass
            centresOfMass = spam.label.centresOfMass(block, boundingBoxes = boundingBoxes)

            # List for classifying the labels
            inside = []
            outside = []
            partial = []

            # Check if each label is inside the true block - i.e., it is inside the block without the margin
            for j in range(1,len(boundingBoxes),1):
                # Get the box
                box = boundingBoxes[j]
                # Check if the origin is inside the true block
                checkOrigin = margin < box[0] < block.shape[0] - margin and margin < box[2] < block.shape[1] - margin and margin < box[4] < block.shape[2] - margin
                # Check if the coordinate opposite to the origin is inside the true block
                checkOpp = margin < box[1] < block.shape[0] - margin and margin < box[3] < block.shape[1] - margin and margin < box[5] < block.shape[2] - margin
                if checkOrigin and checkOpp:
                    # Both points are inside
                    inside.append(j)
                elif checkOrigin or checkOpp:
                    # Only one is inside
                    partial.append(j)
                else:
                    # Both are outside
                    outside.append(j)

            # Create true block array, keep only particles fully inside
            trueBlock = spam.label.removeLabels(block, partial+outside)  

            if not keepLabels:
                # Check that we have labels inside the block
                    if len(numpy.unique(trueBlock))>1 :
                        # Make labels consecutive
                        trueBlock = spam.label.makeLabelsSequential(trueBlock)
                        trueBlock = numpy.where(trueBlock != 0, trueBlock + numpy.max(imBuild), trueBlock)

            # IV (04-03-21): Info needed to avoid chopping grains that would be considered as outside particles 
            imBuildSubSet = imBuild[origin[0]:origin[0]+trueBlock.shape[0]-2*margin,
                                    origin[1]:origin[1]+trueBlock.shape[1]-2*margin,
                                    origin[2]:origin[2]+trueBlock.shape[2]-2*margin]

            # Add the true block preserving previous info
            imBuild[origin[0]:origin[0]+trueBlock.shape[0]-2*margin,
                    origin[1]:origin[1]+trueBlock.shape[1]-2*margin,
                    origin[2]:origin[2]+trueBlock.shape[2]-2*margin] = trueBlock[margin:-margin, margin:-margin, margin:-margin] + imBuildSubSet

            #Get current maximum label
            tempMax = numpy.max(imBuild)
            #Label counter
            labCounter = 1
            #Solve the labels inside partial list
            if len(partial) > 0:
                #Iterate trough each label
                for label in partial:
                    #Get the bounding box
                    box = boundingBoxes[label]   
                    #Get subset 
                    labelSubset = spam.label.getLabel(block, label, boundingBoxes = boundingBoxes, centresOfMass = centresOfMass)
                    labelSubvol = labelSubset['subvol'].astype(int)
                    labelSubvol = numpy.where(labelSubvol != 0, labCounter+tempMax, labelSubvol)
                    #IV+GP implementation - Just put the box there, overwrite whatever you find there
                    # Get the subset from imBuild
                    imBuildSubset = imBuild[origin[0]+box[0]-margin:origin[0]+box[1]+1-margin,
                                            origin[1]+box[2]-margin:origin[1]+box[3]+1-margin,
                                            origin[2]+box[4]-margin:origin[2]+box[5]+1-margin]
                    # Change
                    imBuildSubset = numpy.where(labelSubvol != 0, labelSubvol, imBuildSubset)
                    # Put back
                    imBuild[origin[0]+box[0]-margin:origin[0]+box[1]+1-margin,
                            origin[1]+box[2]-margin:origin[1]+box[3]+1-margin,
                            origin[2]+box[4]-margin:origin[2]+box[5]+1-margin] = imBuildSubset
                    #Update label counter
                    labCounter += 1
                    
            if verbose:
                # Update the progressbar
                finishedBlocks += 1
                widgets[0] = progressbar.FormatLabel("{}/{} ".format(finishedBlocks, len(listCoordinates)))
                pbar.update(finishedBlocks)

        if not keepLabels:
            imBuild = spam.label.makeLabelsSequential(imBuild)
            
            
        print('\n\t')
        return imBuild   

    else:
        # The mode is not correct
        print('spam.helpers.imageManipulation.splitImage(): Incorrect mode, check your input')

        return -1

# private functions
#def _mask2D(im, erosion=False, structure=None, ):
    #"""
    #get contour of 2D image.
    #"""

    #import cv2
    #from scipy import ndimage

    ## step 2: convert into uint8 if not the case
    #if im.dtype != 'uint8':
        ## actually it rescales the image but it doesn't really amtter
        #im = rescaleToInteger(im, nBytes=1)

    ## Step 3: ...
    #blur = cv2.GaussianBlur(im, (5, 5), 0)
    #_, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #_, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    #largest = 0
    #biggest = []
    #for contour in contours:
        #area = cv2.contourArea(contour)
        #if largest < area:
            #largest = area
            #biggest = contour

    #mask = numpy.zeros(im.shape, dtype='<u1')
    #cv2.drawContours(mask, [biggest], 0, 1, -1)

    ## Step 4: apply erosion of the mask (which corresponds to an erosion of the specimen)
    #if erosion:
        #mask = ndimage.morphology.binary_erosion(
            #mask, structure=structure).astype(mask.dtype)

    #return mask

"""
Library of SPAM functions for deforming images.
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
import scipy.ndimage
import multiprocessing
nProcessesDefault = multiprocessing.cpu_count()
#numpy.set_printoptions(precision=3, suppress=True)

###########################################################
# Take an Phi and apply it (C++) to an image
###########################################################
def applyPhi(im, Phi=None, PhiCentre=None, interpolationOrder=1):
    """
    Deform a 3D image using a deformation function "Phi", applied using spam's C++ interpolator.
    Only interpolation order = 1 is implemented.

    Parameters
    ----------
        im : 3D numpy array
            3D numpy array of grey levels to be deformed

        Phi : 4x4 array, optional
            "Phi" deformation function.
            Highly recommended additional argument (why are you calling this function otherwise?)

        PhiCentre : 3x1 array of floats, optional
            Centre of application of Phi.
            Default = (numpy.array(im1.shape)-1)/2.0
            i.e., the centre of the image

        interpolationOrder : int, optional
            Order of image interpolation to use, options are either 0 (strict nearest neighbour) or 1 (trilinear interpolation)
            Default = 1

    Returns
    -------
        imDef : 3D array
            Deformed greyscales by Phi
    """
    # import sys
    # import os
    from . import DICToolkit

    # Detect 2D images, and bail, doesn't work with our interpolator
    if len(im.shape) == 2 or (numpy.array(im.shape) == 1).any():
        print("DIC.deformationFunction.applyPhi(): looks like a 2D image which cannot be handled. Please use DIC.deformationFunction.applyPhiPython")
        return

    # Sort out Phi and calculate inverse
    if Phi is None:
        PhiInv = numpy.eye(4, dtype='<f4')
    else:
        try:
            PhiInv = numpy.linalg.inv(Phi).astype('<f4')
        except numpy.linalg.linalg.LinAlgError:
            # print( "\tapplyPhi(): Can't inverse Phi, setting it to identity matrix. Phi is:\n{}".format( Phi ) )
            PhiInv = numpy.eye(4, dtype='<f4')

    if PhiCentre is None:
        PhiCentre = (numpy.array(im.shape) - 1) / 2.0

    if interpolationOrder > 1:
        print("DIC.deformationFunction.applyPhi(): interpolation Order > 1 not implemented")
        return

    im = im.astype('<f4')
    PhiCentre = numpy.array(PhiCentre).astype('<f4')
    # We need to inverse Phi for question of direction
    imDef = numpy.zeros_like(im, dtype='<f4')
    DICToolkit.applyPhi(im.astype('<f4'),
                        imDef,
                        PhiInv.astype('<f4'),
                        PhiCentre.astype('<f4'),
                        int(interpolationOrder))

    return imDef

###########################################################
# Take an Phi and apply it to an image
###########################################################
def applyPhiPython(im, Phi=None, PhiCentre=None, interpolationOrder=3):
    """
    Deform a 3D image using a deformation function "Phi", applied using scipy.ndimage.map_coordinates
    Can have orders > 1 but is hungry in memory.

    Parameters
    ----------
        im : 3D numpy array
            3D numpy array of grey levels to be deformed

        Phi : 4x4 array, optional
            "Phi" linear deformation function.
            Highly recommended additional argument (why are you calling this function otherwise?)

        PhiCentre : 3x1 array of floats, optional
            Centre of application of Phi.
            Default = (numpy.array(im1.shape)-1)/2.0
            i.e., the centre of the image

        interpolationOrder : int, optional
            Order of image interpolation to use. This value is passed directly to ``scipy.ndimage.map_coordinates`` as "order".
            Default = 3

    Returns
    -------
        imSub : 3D array
            Deformed greyscales by Phi
    """

    if Phi is None:
        PhiInv = numpy.eye(4, dtype='<f4')
    else:
        try:
            PhiInv = numpy.linalg.inv(Phi).astype('<f4')
        except numpy.linalg.linalg.LinAlgError:
            # print( "\tapplyPhiPython(): Can't inverse Phi, setting it to identity matrix. Phi is:\n{}".format( Phi ) )
            PhiInv = numpy.eye(4)

    if PhiCentre is None:
        PhiCentre = (numpy.array(im.shape) - 1) / 2.0

    imDef = numpy.zeros_like(im, dtype='<f4')

    coordinatesInitial = numpy.ones((4, im.shape[0] * im.shape[1] * im.shape[2]), dtype='<f4')

    coordinates_mgrid = numpy.mgrid[0:im.shape[0],
                                    0:im.shape[1],
                                    0:im.shape[2]]

    # Copy into coordinatesInitial
    coordinatesInitial[0, :] = coordinates_mgrid[0].ravel() - PhiCentre[0]
    coordinatesInitial[1, :] = coordinates_mgrid[1].ravel() - PhiCentre[1]
    coordinatesInitial[2, :] = coordinates_mgrid[2].ravel() - PhiCentre[2]

    # Apply Phi to coordinates
    coordinatesDef = numpy.dot(PhiInv, coordinatesInitial)

    coordinatesDef[0, :] += PhiCentre[0]
    coordinatesDef[1, :] += PhiCentre[1]
    coordinatesDef[2, :] += PhiCentre[2]

    imDef += scipy.ndimage.map_coordinates(im,
                                           coordinatesDef[0:3],
                                           order=interpolationOrder).reshape(imDef.shape).astype('<f4')
    return imDef

###############################################################
# Take a field of Phi and apply it (quite slowly) to an image
###############################################################
def applyPhiField(im, fieldCoordsRef, PhiField, imMaskDef=None, displacementMode="applyPhi", nNeighbours=8, interpolationOrder=1, nProcesses=nProcessesDefault, verbose=False):
    """
    Deform a 3D image using a field of deformation functions "Phi" coming from a regularGrid,
    applied using scipy.ndimage.map_coordinates.

    Parameters
    ----------
        im : 3D array
            3D array of grey levels to be deformed

        fieldCoordsRef: 2D array, optional
            nx3 array of n points coordinates (ZYX)
            centre where each deformation function "Phi" has been calculated

        PhiField: 3D array, optional
            nx4x4 array of n points deformation functions

        imMaskDef: 3D array of bools, optional
            3D array same size as im but DEFINED IN THE DEFORMED CONFIGURATION
            which should be True in the pixels to fill in in the deformed configuration.
            Default = None

        displacementMode : string, optional
            How do you want to calculate displacements?
            With "interpolate" they are just interpolated from the PhiField
            With "applyPhi" each neighbour's Phi function is applied to the pixel position
            and the resulting translations weighted and summed.
            Default = "applyPhi"

        nNeighbours : int, optional
            Number of the nearest neighbours to consider
            #This OR neighbourRadius must be set.
            Default = 8

        interpolationOrder : int, optional
            Order of image interpolation to use. This value is passed directly to ``scipy.ndimage.map_coordinates`` as "order".
            Default = 1

        nProcesses : integer, optional
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : boolean, optional
            Print progress?
            Default = True

    Returns
    -------
        imDef : 3D array
            deformed greylevels by a field of deformation functions "Phi"
    """
    import spam.DIC
    import spam.deformation
    import multiprocessing
    import progressbar

    tol = 1e-6 # OS is responsible for the validity of this magic number

    #print("making pixel grid")
    if imMaskDef is not None:
        #print("...from a passed mask, cool, this should shave time")
        pixCoordsDef = numpy.array(numpy.where(imMaskDef)).T
    else:
        # Create the grid of the input image
        imSize = im.shape
        coordinates_mgrid = numpy.mgrid[0:imSize[0],
                                        0:imSize[1],
                                        0:imSize[2]]

        pixCoordsDef = numpy.ones((imSize[0] * imSize[1] * imSize[2], 3))

        pixCoordsDef[:, 0] = coordinates_mgrid[0].ravel()
        pixCoordsDef[:, 1] = coordinates_mgrid[1].ravel()
        pixCoordsDef[:, 2] = coordinates_mgrid[2].ravel()
        #print(pixCoordsDef.shape)

    # Initialise deformed coordinates
    fieldCoordsDef = fieldCoordsRef + PhiField[:, 0:3, -1]
    #print("done")

    maskPhiField = numpy.isfinite(PhiField[:, 0, 0])

    if displacementMode == "interpolate":
        """
        In this mode we're only taking into account displacements.
        We use interpolatePhiField in the deformed configuration, in displacements only,
        and we don't feed PhiInv, but only the negative of the displacements
        """
        backwardsDisplacementsPhi = numpy.zeros_like(PhiField)
        backwardsDisplacementsPhi[:, 0:3, -1] = -1*PhiField[:, 0:3, -1]

        pixDispsDef = spam.DIC.interpolatePhiField(fieldCoordsDef[maskPhiField],
                                                   backwardsDisplacementsPhi[maskPhiField],
                                                   pixCoordsDef,
                                                   nNeighbours=nNeighbours,
                                                   interpolateF="no",
                                                   nProcesses=nProcesses,
                                                   verbose=verbose)
        pixCoordsRef = pixCoordsDef + pixDispsDef[:, 0:3, -1]

    elif displacementMode == "applyPhi":
        """
        In this mode we're NOT interpolating the displacement field.
        For each pixel, we're applying the neighbouring Phis and looking
        at the resulting displacement of the pixel.
        Those different displacements are weighted as a function of distance
        and averaged into the point's final displacement.

        Obviously if your PhiField is only a displacement field, this changes
        nothing from above (except for computation time), but with some stretches
        this can become interesting.
        """
        #print("inversing PhiField")
        PhiFieldInv = numpy.zeros_like(PhiField)
        for n in range(PhiField.shape[0]):
            try:
                PhiFieldInv[n] = numpy.linalg.inv(PhiField[n])
            except:
                maskPhiField[n] = False
        #print("done")

        # mask everything
        PhiFieldInvMasked = PhiFieldInv[maskPhiField]
        fieldCoordsRefMasked = fieldCoordsRef[maskPhiField]
        fieldCoordsDefMasked = fieldCoordsDef[maskPhiField]

        # build KD-tree
        treeCoordDef = scipy.spatial.KDTree(fieldCoordsDefMasked)

        pixCoordsRef = numpy.zeros_like(pixCoordsDef, dtype='f4')

        """
        Define multiproc function only for displacementMode == "applyPhi"
        """
        global computeDisplacementForSeriesOfPixels
        def computeDisplacementForSeriesOfPixels(seriesNumber):
            pixelNumbers = splitPixNumbers[seriesNumber]

            pixCoordsRefSeries = numpy.zeros((len(pixelNumbers), 3), dtype='f4')

            # all jobs should take the same time, so just show progress bar in 0th process
            if seriesNumber == 0 and verbose: pbar = progressbar.ProgressBar(maxval=len(pixelNumbers)).start()

            for localPixelNumber, globalPixelNumber in enumerate(pixelNumbers):
                if seriesNumber == 0 and verbose: pbar.update(localPixelNumber)

                pixCoordDef = pixCoordsDef[globalPixelNumber]
                # get nNeighbours and compute distance weights
                distances, indices = treeCoordDef.query(pixCoordDef, k=nNeighbours)
                weights = (1/(distances+tol))

                displacement = numpy.zeros(3, dtype='float')

                # for each neighbour
                for neighbour, index in enumerate(indices):
                    # apply PhiInv to current point with PhiCentre = fieldCoordsREF <- this is important
                    # -> this gives a displacement for each neighbour
                    PhiInv = PhiFieldInvMasked[index]
                    #print("PhiInv", PhiInv)
                    translationTmp = PhiInv[0:3, -1].copy()
                    dist = pixCoordDef - fieldCoordsRefMasked[index]
                    #print(f"dist = {dist}")
                    translationTmp -= dist - numpy.dot(PhiInv[0:3, 0:3], dist)
                    #print(f"translationTmp ({neighbour}): {translationTmp} (weight = {weights[neighbour]})")
                    displacement += translationTmp*weights[neighbour]

                # compute resulting displacement as weights * displacements
                # compute pixel coordinates in reference config
                #print("pixCoordDef", pixCoordDef)
                #print("displacement", displacement)
                pixCoordsRefSeries[localPixelNumber] = pixCoordDef + displacement / weights.sum()

            if seriesNumber == 0 and verbose: pbar.finish()
            return pixelNumbers, pixCoordsRefSeries
                #pixCoordsRef[pixNumber] = pixCoordDef + numpy.sum(displacements*weights[:, numpy.newaxis], axis=0)

        splitPixNumbers = numpy.array_split(numpy.arange(pixCoordsDef.shape[0]), nProcesses)

        # Run multiprocessing filling in FfieldFlatGood, which will then update FfieldFlat
        with multiprocessing.Pool(processes=nProcesses) as pool:
            for returns in pool.imap_unordered(computeDisplacementForSeriesOfPixels, range(nProcesses)):
                pixCoordsRef[returns[0]] = returns[1]
            pool.close()
            pool.join()

    if imMaskDef is not None:
        imDef = numpy.zeros_like(im)
        imDef[imMaskDef] = scipy.ndimage.map_coordinates(im,
                                                         pixCoordsRef.T,
                                                         mode="constant",
                                                         order=interpolationOrder)

    else: # no pixel mask, image comes out directly
        imDef = scipy.ndimage.map_coordinates(im,
                                              pixCoordsRef.T,
                                              mode="constant",
                                              order=interpolationOrder).reshape(im.shape)

    return imDef


def binning(im, binning, returnCropAndCentre=False):
    """
    This function downscales images by averaging NxNxN voxels together in 3D and NxN pixels in 2D.
    This is useful for reducing data volumes, and denoising data (due to averaging procedure).

    Parameters
    ----------
        im : 2D/3D numpy array
            Input measurement field

        binning : int
            The number of pixels/voxels to average together

        returnCropAndCentre: bool (optional)
            Return the position of the centre of the binned image
            in the coordinates of the original image, and the crop
            Default = False

    Returns
    -------
        imBin : 2/3D numpy array
            `binning`-binned array

        (otherwise if returnCropAndCentre): list containing:
            imBin,
            topCrop, bottomCrop
            centre of imBin in im coordinates (useful for re-stitching)
    Notes
    -----
        Here we will only bin pixels/voxels if they is a sufficient number of
        neighbours to perform the binning. This means that the number of pixels that
        will be rejected is the dimensions of the image, modulo the binning amount.

        The returned volume is computed with only fully binned voxels, meaning that some voxels on the edges
        may be excluded.
        This means that the output volume size is the input volume size / binning or less (in fact the crop
        in the input volume is the input volume size % binning
    """
    twoD = False
    from . import DICToolkit

    if im.dtype == 'f8':
        im = im.astype('<f4')

    binning = int(binning)
    #print("binning = ", binning)

    dimsOrig = numpy.array(im.shape)
    #print("dimsOrig = ", dimsOrig)

    # Note: // is a floor-divide
    imBin = numpy.zeros(dimsOrig // binning, dtype=im.dtype)
    #print("imBin.shape = ", imBin.shape)

    # Calculate number of pixels to throw away
    offset = dimsOrig % binning
    #print("offset = ", offset)

    # Take less off the top corner than the bottom corner
    topCrop = offset // 2
    #print("topCrop = ", topCrop)
    topCrop = topCrop.astype('<i2')

    if len(im.shape) == 2:
        # pad them
        im = im[numpy.newaxis, ...]
        imBin = imBin[numpy.newaxis, ...]
        topCrop = numpy.array([0, topCrop[0], topCrop[1]]).astype('<i2')
        offset = numpy.array([0, offset[0], offset[1]]).astype('<i2')
        twoD = True

    # Call C++
    if im.dtype == 'f4':
        #print("Float binning")
        DICToolkit.binningFloat(im.astype('<f4'),
                                imBin,
                                topCrop.astype('<i4'),
                                int(binning))
    elif im.dtype == 'u2':
        #print("Uint 2 binning")
        DICToolkit.binningUInt(im.astype('<u2'),
                               imBin,
                               topCrop.astype('<i4'),
                               int(binning))
    elif im.dtype == 'u1':
        #print("Char binning")
        DICToolkit.binningChar(im.astype('<u1'),
                               imBin,
                               topCrop.astype('<i4'),
                               int(binning))

    if twoD:
        imBin = imBin[0]

    if returnCropAndCentre:
        centreBinned = (numpy.array(imBin.shape) - 1) / 2.0
        relCentOrig = offset + binning * centreBinned
        return [imBin, [topCrop, offset - topCrop], relCentOrig]
    else:
        return imBin

###############################################################
# Take a tetrahedral mesh (defined by coords and conn) and use
#   it to deform an image
###############################################################
def applyMeshTransformation(im, coordinates, connectivity, displacements, tetLabel=None):
    """
    This function deforms an image based on a tetrahedral mesh and
    nodal displacements (normally from Global DVC),
    using the mesh's shape functions to interpolate.

    Parameters
    ----------
        im : 3D numpy array of greyvalues
            Input image to be deformed

        coordinates : m x 3 numpy array
            M nodal coordinates in reference configuration

        connectivity : n x 4 numpy array
            Tetrahedral connectivity generated by spam.mesh.triangulate() for example

        displacements : m x 3 numpy array
            M displacements defined at the nodes


        tetLabel : 3D numpy array of ints (optional)
            Pixels labelled with the tetrahedron (i.e., line number in connectivity matrix) they belong to.
            This is in the deformed configuration.
            If this is not passed, it's calculated in this function (can be slow).

    Returns
    -------
        imDef : 3D numpy array of greyvalues
            Deformed image

    """
    import spam.label

    if tetLabel is None:
        #print("spam.DIC.applyMeshTransformation(): tetLabel not passed, recomputing it.")
        tetLabel = spam.label.labelTetrahedra(im.shape, coordinates+displacements, connectivity)

    # Allocate output array that will be painted in by C++
    imDef = numpy.zeros_like(im, dtype='<f4')


    spam.DIC.DICToolkit.applyMeshTransformation(im.astype('<f4'),
                                                tetLabel.astype("<u4"),
                                                imDef,
                                                connectivity.astype("<u4"),
                                                (coordinates+displacements).astype("<f8"),
                                                displacements.astype("<f8"))
    return imDef


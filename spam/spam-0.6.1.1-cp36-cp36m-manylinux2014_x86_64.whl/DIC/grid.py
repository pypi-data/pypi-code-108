"""
Library of SPAM functions for defining a regular grid in a reproducible way.
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
import spam.DIC.correlate
import sys
import progressbar

def makeGrid(imageSize, nodeSpacing):
    """
        Define a grid of correlation points.

        Parameters
        ----------
        imageSize : 3-item list
            Size of volume to spread the grid inside

        nodeSpacing : 3-item list or int
            Spacing between nodes

        Returns
        -------
        nodePositions : nPointsx3 numpy.array
            Array containing Z, Y, X positions of each point in the grid
    """

    if len(imageSize) != 3:
        print("\tgrid.makeGrid(): imageSize doesn't have three dimensions, exiting")
        return

    if type(nodeSpacing) == int or type(nodeSpacing) == float:
        nodeSpacing = [nodeSpacing] * 3
    elif len(nodeSpacing) != 3:
        print("\tgrid.makeGrid(): nodeSpacing is not an int or float and doesn't have three dimensions, exiting")
        return

    if imageSize[0] == 1:
        twoD = True
    else:
        twoD = False

    # Note: in this cheap node spacing, the first node is always at a distance of --nodeSpacing-- from the origin
    # The following could just be done once in principle...
    nodesMgrid = numpy.mgrid[nodeSpacing[0]:imageSize[0]:nodeSpacing[0],
                             nodeSpacing[1]:imageSize[1]:nodeSpacing[1],
                             nodeSpacing[2]:imageSize[2]:nodeSpacing[2]]

    # If twoD then overwrite nodesMgrid
    if twoD:
        nodesMgrid = numpy.mgrid[0: 1: 1,
                                 nodeSpacing[1]:imageSize[1]:nodeSpacing[1],
                                 nodeSpacing[2]:imageSize[2]:nodeSpacing[2]]

    nodesDim = (nodesMgrid.shape[1], nodesMgrid.shape[2], nodesMgrid.shape[3])

    numberOfNodes = int(nodesMgrid.shape[1] * nodesMgrid.shape[2] * nodesMgrid.shape[3])

    nodePositions = numpy.zeros((numberOfNodes, 3))

    nodePositions[:, 0] = nodesMgrid[0].ravel()
    nodePositions[:, 1] = nodesMgrid[1].ravel()
    nodePositions[:, 2] = nodesMgrid[2].ravel()

    return nodePositions, nodesDim


def getImagettes(im1, nodePosition, halfWindowSize, Phi, im2, searchRange, im1mask=None, im2mask=None, minMaskCoverage=0.0, greyThreshold=[-numpy.inf, numpy.inf], applyF='all', twoD=False):
    """
    This function is responsible for extracting correlation windows ("imagettes") from two larger images (im1 and im2).
    Both spam.correlate.pixelSearch and spam.correlate.register[Multiscale] want a fixed, smaller imagette1
    and a larger imagette 2 in which to search/interpolate.

    Parameters
    ----------
        im1 : 3D numpy array
            This is the large input reference image

        nodePosition : 3-component numpy array of ints
            This defines the centre of the window to extract from im1.
            Note: for 2D Z = 0

        halfWindowSize : 3-component numpy array of ints
            This defines the half-size of the correlation window,
            i.e., how many pixels to extract in Z, Y, X either side of the centre.
            Note: for 2D Z = 0

        Phi : 4x4 numpy array of floats
            Phi matrix representing the movement of imagette1,
            if not equal to `I`, imagette1 is deformed by the non-translation parts of Phi (F)
            and the displacement is added to the search range (see below)

        im2 :  3D numpy array
            This is the large input deformed image

        searchRange : 6-component numpy array of ints
            This defines where imagette2 should be extracted with respect to imagette1's position in im1.
            The 6 components correspond to [ Zbot Ztop Ybot Ytop Xbot Xtop ].
            If Z, Y and X values are the same, then imagette2 will be displaced and the same size as imagette1.
            If 'bot' is lower than 'top', imagette2 will be larger in that dimension

        im1mask : 3D numpy array, optional
            This needs to be same size as im1, but can be `None` if no mask is wanted.
            This defines a mask for zones to correlate in im1, 0 means zone not to correlate
            Default = None

        im2mask : 3D numpy array, optional
            This needs to be same size as im2, but can be `None` if no mask is wanted.
            This defines a mask for zones to correlate in im2, 0 means zone not to correlate
            Default = None

        minMaskCoverage : float, optional
            Threshold for imagette1 non-mask coverage, i.e. how much of imagette1 can be full of mask
            before it is rejected with returnStatus = -5?
            Default = 0

        greyThreshold : two-component list of floats, optional
            Bottom and top threshold values for mean value of imagette1 to reject it with returnStatus = -5
            Default = no threshold

        applyF : string, optional
            If a non-identity Phi is passed, should the F be applied to the returned imagette1?
            Options are: 'all', 'rigid', 'no'
            Default = 'all'
            Note: as of January 2021, it seems to make more sense to have this as 'all' for pixelSearch, and 'no' for local DIC

        twoD : bool, optional
            Are the images two-dimensional?

    Returns
    -------
        Dictionary :

            'imagette1' :    3D numpy array,

            'imagette1mask': 3D numpy array of same size as imagette1 or None,

            'imagette2':     3D numpy array, bigger or equal size to imagette1

            'imagette2mask': 3D numpy array of same size as imagette2 or None,

            'returnStatus':  int,
                Describes success in extracting imagette1 and imagette2.
                If == 1 success, otherwise negative means failure.

            'pixelSearchOffset': 3-component list of ints
                Coordinates of the top of the pixelSearch range in im1, i.e., the displacement that needs to be
                added to the raw pixelSearch output to make it a im1 -> im2 displacement
    """
    returnStatus = 1
    #imagette1mask = None
    imagette2mask = None
    intDisplacement = numpy.round(Phi[0:3, 3]).astype(int)

    assert len(im1.shape) == len(im2.shape) == 3, "3D images needed for im1 and im2, if you have 2D images please pad them with im[numpy.newaxis, ...]"
    if im1mask is not None: assert len(im1mask.shape) == 3, "3D image needed for im1mask, if you have 2D images please pad them with im[numpy.newaxis, ...]"
    if im2mask is not None: assert len(im2mask.shape) == 3, "3D image needed for im2mask, if you have 2D images please pad them with im[numpy.newaxis, ...]"

    ## Detect 2D images
    #if im1.shape[0] == 1:
        #twoD = True
        ## Impose no funny business in z if in twoD
        #halfWindowSize[0] = 0
        #searchRange[0:2] = 0
    #else:
        #twoD = False

    PhiNoDisp = Phi.copy()
    #PhiNoDisp[0:3,-1] -= intDisplacement
    PhiNoDisp[0:3,-1] = numpy.zeros(3)
    if applyF == 'rigid':
        PhiNoDisp = spam.deformation.computeRigidPhi(PhiNoDisp)

    # If F is not the identity, create a pad to be able to apply F to imagette 1
    if numpy.allclose(PhiNoDisp, numpy.eye(4)) or applyF == 'no':
        # 2020-09-25 OS and EA: Prepare startStop array for imagette 1 to be extracted with new slicePadded
        startStopIm1 = [int(nodePosition[0] - halfWindowSize[0]    ),
                        int(nodePosition[0] + halfWindowSize[0] + 1),
                        int(nodePosition[1] - halfWindowSize[1]    ),
                        int(nodePosition[1] + halfWindowSize[1] + 1),
                        int(nodePosition[2] - halfWindowSize[2]    ),
                        int(nodePosition[2] + halfWindowSize[2] + 1)]

        # In either case, extract imagette1, now guaranteed to be the right size
        imagette1def = spam.helpers.slicePadded(im1, startStopIm1)

        ### Check mask
        if im1mask is None:
            # no mask1 --> always pas this test (e.g., labelled image)
            maskVolumeCondition = True
            imagette1mask = None
        else:
            imagette1mask = spam.helpers.slicePadded(im1mask, startStopIm1) != 0
            maskVolumeCondition = (imagette1mask != 0).mean() >= minMaskCoverage

    else: ## This is the case that we should apply F to imagette1, which requires a pad
        # 2020-10-06 OS and EA: Add a pad to each dimension of 25% of max(halfWindowSize) to allow space to apply F (no displacement) to imagette1
        applyPhiPad = int(0.5*numpy.ceil(max(halfWindowSize)))

        if twoD:
            applyPhiPad = (     0     , applyPhiPad, applyPhiPad)
        else:
            applyPhiPad = (applyPhiPad, applyPhiPad, applyPhiPad)

        # 2020-09-25 OS and EA: Prepare startStop array for imagette 1 to be extracted with new slicePadded
        startStopIm1 = [int(nodePosition[0] - halfWindowSize[0] - applyPhiPad[0]    ),
                        int(nodePosition[0] + halfWindowSize[0] + applyPhiPad[0] + 1),
                        int(nodePosition[1] - halfWindowSize[1] - applyPhiPad[1]    ),
                        int(nodePosition[1] + halfWindowSize[1] + applyPhiPad[1] + 1),
                        int(nodePosition[2] - halfWindowSize[2] - applyPhiPad[2]    ),
                        int(nodePosition[2] + halfWindowSize[2] + applyPhiPad[2] + 1)]

        # In either case, extract imagette1, now guaranteed to be the right size
        imagette1padded = spam.helpers.slicePadded(im1, startStopIm1)

        # apply F to imagette 1 padded
        if twoD:    imagette1paddedDef = spam.DIC.applyPhiPython(imagette1padded, PhiNoDisp)
        else:       imagette1paddedDef = spam.DIC.applyPhi(      imagette1padded, PhiNoDisp)

        # undo padding
        if twoD:
            imagette1def = imagette1paddedDef[              :               ,
                                              applyPhiPad[1]:-applyPhiPad[1],
                                              applyPhiPad[2]:-applyPhiPad[2]]

        else:
            imagette1def = imagette1paddedDef[applyPhiPad[0]:-applyPhiPad[0],
                                              applyPhiPad[1]:-applyPhiPad[1],
                                              applyPhiPad[2]:-applyPhiPad[2]]

        ### Check mask
        if im1mask is None:
            # no mask1 --> always pas this test (e.g., labelled image)
            maskVolumeCondition = True
            imagette1mask = None
        else:
            imagette1maskPadded = spam.helpers.slicePadded(im1mask, startStopIm1) != 0

            # apply F to imagette 1 padded
            #if twoD:    imagette1maskPaddedDef = spam.DIC.applyPhiPython(imagette1maskPadded, PhiNoDisp, interpolationOrder=0)
            #else:       imagette1maskPaddedDef = spam.DIC.applyPhiPython(imagette1maskPadded, PhiNoDisp, interpolationOrder=0)
            imagette1maskPaddedDef = spam.DIC.applyPhiPython(imagette1maskPadded, PhiNoDisp, interpolationOrder=0)

            # undo padding
            if twoD:
                imagette1mask = imagette1maskPaddedDef[              :               ,
                                                       applyPhiPad[1]:-applyPhiPad[1],
                                                       applyPhiPad[2]:-applyPhiPad[2]]
            else:
                imagette1mask = imagette1maskPaddedDef[applyPhiPad[0]:-applyPhiPad[0],
                                                       applyPhiPad[1]:-applyPhiPad[1],
                                                       applyPhiPad[2]:-applyPhiPad[2]]

            maskVolumeCondition = (imagette1mask != 0).mean() >= minMaskCoverage


    # Make sure imagette is not 0-dimensional in any dimension
    # Check minMaskVolume
    if numpy.all(numpy.array(imagette1def.shape) > 0) or (twoD and numpy.all(numpy.array(imagette1def.shape[1:3]) > 0)):
        # ------------ Grey threshold low --------------- and -------------- Grey threshold high -----------
        if numpy.nanmean(imagette1def) > greyThreshold[0] and numpy.nanmean(imagette1def) < greyThreshold[1]:
            if maskVolumeCondition:
                # Slice for image 2
                ## 2020-09-25 OS and EA: Prepare startStop array for imagette 2 to be extracted with new slicePadded
                ## Extract it...
                startStopIm2 = [int(nodePosition[0] - halfWindowSize[0] + intDisplacement[0] + searchRange[0]    ),
                                int(nodePosition[0] + halfWindowSize[0] + intDisplacement[0] + searchRange[1] + 1),
                                int(nodePosition[1] - halfWindowSize[1] + intDisplacement[1] + searchRange[2]    ),
                                int(nodePosition[1] + halfWindowSize[1] + intDisplacement[1] + searchRange[3] + 1),
                                int(nodePosition[2] - halfWindowSize[2] + intDisplacement[2] + searchRange[4]    ),
                                int(nodePosition[2] + halfWindowSize[2] + intDisplacement[2] + searchRange[5] + 1)]
                imagette2 = spam.helpers.slicePadded(im2, startStopIm2)

                if im2mask is not None:
                    imagette2mask = spam.helpers.slicePadded(im2mask, startStopIm2)

            # Failed minMaskVolume condition
            else:
                returnStatus = -5
                imagette1def = None
                imagette2 = None

        # Failed greylevel condition
        else:
            returnStatus = -5
            imagette1def = None
            imagette2 = None

    # Failed 0-dimensional imagette test
    else:
        returnStatus = -5
        imagette1def = None
        imagette2 = None

    return {'imagette1':            imagette1def,
            'imagette1mask':        imagette1mask,
            'imagette2':            imagette2,
            'imagette2mask':        imagette2mask,
            'returnStatus':         returnStatus,
            'pixelSearchOffset':    searchRange[0::2] + intDisplacement
            }

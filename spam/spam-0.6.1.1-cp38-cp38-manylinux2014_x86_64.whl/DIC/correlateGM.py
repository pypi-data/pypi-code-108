# -*- coding: utf-8 -*-

"""
Library of SPAM multimodal image correlation functions using a Gaussian Mixture model from Tudisco et al. 2017.
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

# 2017-05-29 ER and EA

import scipy.ndimage
import numpy

from . import DICToolkit
import spam.deformation
import spam.DIC

import matplotlib as mpl
import matplotlib.pyplot as plt


numpy.set_printoptions(precision=3, suppress=True)
mpl.rc('font', size=6)
cmapPhases = 'Set1_r'


def multimodalRegistration(im1, im2, phaseDiagram, gaussianParameters, im1mask=None, PhiInit=None, margin=None, maxIterations=50, deltaPhiMin=0.005, interpolationOrder=1, verbose=False, GRAPHS=False, INTERACTIVE=False, sliceAxis=0, suffix="", rootPath=".", BINS=64):
    """
    Perform subpixel image correlation between im1 and im2 -- images of the same object acquired with different modalities.

    This function will deform im2 until it best matches im1.
    The matching includes sub-pixel displacements, rotation, and linear straining of the whole image.
    The correlation of im1, im2 will give a deformationFunction F which maps im1 into im2.
    Phi(im1(x),im2(F.x)) = 0
    As per Equation (3) of Tudisco `et al.`

    "Discrete correlation" can be performed by masking im1.

    Parameters
    ----------
        im1 : 3D numpy array
            The greyscale image that will not move

        im2 : 3D numpy array
            The greyscale image that will be deformed

        phaseDiagram : Nbins x Nbins numpy array of ints
            Pre-labelled phase diagram, which is a joint histogram with the phases labelled

        gaussianParameters : 2D numpy array Nx6
            Key parameter which is the result of a 2D gaussian fit of the first N peaks in the joint histograms of
            im1 and im2.
            The 6 parameters of the fit are:
            φ, μ(im1), μ(im2), and a, b, c, where {a,b,c} are the parameter that can be found for `two-dimensional elliptical Gaussian function` here:
            https://en.wikipedia.org/wiki/Gaussian_function, `i.e.`, coupled with im1², im1*im2 and im2² respectively

        im1mask : 3D numpy array, float, optional
            A mask for the zone to correlate in im1 with NaNs in the zone to not correlate. Default = None, `i.e.`, correlate all of im1 minus the margin

        PhiInit : 4x4 numpy array, optional
            Initial transformation to apply. Default = numpy.eye(4), `i.e.`, no transformation

        margin : int, optional
            Margin, in pixels, to take in im1 and im2 to allow space for interpolation and movement.
            Default = None (`i.e.`, enough margin for a worse-case 45degree rotation with no displacement)

        maxIterations : int, optional
            Maximum number of quasi-Newton interations to perform before stopping. Default = 25

        deltaPhiMin : float, optional
            Smallest change in the norm of F (the transformation operator) before stopping. Default = 0.001

        interpolationOrder : int, optional
            Order of the greylevel interpolation for applying F to im1 when correlating. Reccommended value is 3, but you can get away with 1 for faster calculations. Default = 3

        verbose : bool, optional
            Get to know what the function is really thinking, recommended for debugging only. Default = False

        GRAPHS : bool, optional
            Pop up a window showing the image differences (im1-im2) as im1 is progressively deformed.

    Returns
    --------
        Dictionary:

            'transformation'
                Dictionary containing:

                    't' : 3-component vector

                        Z, Y, X displacements in pixels

                    'r' : 3-component vector

                        Z, Y, X components of rotation vector

            'Phi': 4 x 4 numpy array of floats
                Deformation function, Phi

            'returnStatus': int
                Return status from the correlation:

                2 : Achieved desired precision in the norm of delta Phi

                1 : Hit maximum number of iterations while iterating

                -1 : Error is more than 80% of previous error, we're probably diverging

                -2 : Singular matrix M cannot be inverted

                -3 : Displacement > 5*margin

            'iterations': int
                Number of iterations

            'logLikelyhood' : float
                Number indicating quality of match

            'deltaPhiNorm' : float
                Size of last Phi step

            'residualField': 3D numpy array of floats
                Same size as input image, residual field

            'phaseField': phaseField
                Same size as input image, labelled phases

    Note
    ----
        This correlation is what is proposed in Tudisco et al. "An extension of Digital Image Correlation for intermodality image registration", section 4.3.
    """

    # if verbose:
    #     print("Enter registration")

    # for interactive graphs
    if INTERACTIVE:
        GRAPHS = True
        plt.ion()

    # Detect default case and calculate maring necessary for a 45deg rotation with no displacement
    if margin is None:
        # sqrt
        margin = int((3**0.5 - 1.0) * max(im1.shape)*0.5)
    else:
        # Make sure margin is an int
        margin = int(margin)

    # Exit clause for singular matrices
    singular = False

    crop = (slice(margin, im1.shape[0]-margin),
            slice(margin, im1.shape[1]-margin),
            slice(margin, im1.shape[2]-margin))

    # Figure out coordinates on which the correlation should happen, i.e., the non NaN ones
    # NOTE: these coordinates are within the cropped margin for interpolation
    # cropImCoordsFG = numpy.where( numpy.isfinite( im1[crop] ) )
    if im1mask is not None:
        # TODO: This could just be directly = mask and equals inv of mask
        #  i.e., arry a boolean mask and not a series of coord array
        cropImCoordsFG = numpy.where(im1mask[crop] is True)
        cropImCoordsBG = numpy.where(im1mask[crop] is False)
    else:
        # Everything regular, except that we might have NaNs in the CW...
        # cropImCoordsFG = numpy.ones_like(  im1[crop], dtype='bool' )
        # cropImCoordsBG = numpy.zeros_like( im1[crop], dtype='bool' )
        cropImCoordsFG = numpy.isfinite(im1[crop], dtype='bool')
        cropImCoordsBG = numpy.isnan(im1[crop], dtype='bool')

        # HACK
        # print cropImCoordsFG
        # print cropImCoordsBG

        # HACK: set nans in im2 to zero
        im2[numpy.isnan(im2)] = 0.0

        # if numpy.isnan( im1[crop] ).sum() > 0 numpy.isnan( im2[crop] ).sum() > 0:

    # compute image centre
    # im1centre = (numpy.array(im1.shape)-1)/2.0

    # If there is no initial Phi, initalise it to zero.
    if PhiInit is None:
        Phi = numpy.eye(4)
        im2def = im2.copy()

    # If there is an initial guess...
    else:
        Phi = PhiInit.copy()

        # invert PhiInit to apply it to im2
        try:
            PhiInv = numpy.linalg.inv(Phi.copy())
        except numpy.linalg.linalg.LinAlgError:
            PhiInv = numpy.eye(4)

        im2def = spam.DIC.applyPhi(im2, Phi=PhiInv, interpolationOrder=interpolationOrder).astype(im2.dtype)

    # At this stage we've computed gradients which we are not going to update, im2 and it's gradients will be set equal to
    #   their cropped versions:
    # im2def      = im2def[crop]
    # im2defGradZ = im2defGradZ[crop]
    # im2defGradY = im2defGradY[crop]
    # im2defGradX = im2defGradX[crop]

    # Mask nans in gradient (but not before or there are jumps when the grey goes to zero
    #   beacuse of this a label dilate of at least 1 is recommended)
    # im2defGradZ[ numpy.where( numpy.isnan( im1gradZ ) ) ] = 0
    # im2defGradY[ numpy.where( numpy.isnan( im1gradY ) ) ] = 0
    # im2defGradX[ numpy.where( numpy.isnan( im1gradX ) ) ] = 0

    iterations = 0
    returnStatus = 0
    deltaPhiNorm = 0.0

    # compute initial Log likelyhood
    # p, _, _ = numpy.histogram2d(im1[crop].ravel(), im2def[crop].ravel(), bins=BINS, range=[[0.0, BINS], [0.0, BINS]], normed=False, weights=None)
    # LL = 0.0
    # for v in p.ravel():
    #     if v:
    #         LL += numpy.log(v)
    # LL = numpy.prod(p[numpy.where(p > 0)])

    p, _, _ = numpy.histogram2d(im1[crop].ravel(),
                                im2def[crop].ravel(),
                                bins=BINS,
                                range=[[0.0, BINS], [0.0, BINS]],
                                normed=False,
                                weights=None)
    LL = numpy.sum(numpy.log(p[numpy.where(p > 0)]))

    if verbose:
        print("\tInitial state        LL = {:0.2f}".format(LL))
        print("\tIteration Number {:03d} ".format(iterations), end="")
        print("LL = {:0.2f} ".format(LL), end="")
        print("dPhi = {:0.4f} ".format(deltaPhiNorm), end="")
        # print("\nPhi", Phi )
        # currentTransformation = spam.deformation.decomposePhi(Phi, PhiPoint=im1centre)
        currentTransformation = spam.deformation.decomposePhi(Phi)
        print("Tr = {: .3f}, {: .3f}, {: .3f} ".format(*currentTransformation['t']), end="")
        print("Ro = {: .3f}, {: .3f}, {: .3f} ".format(*currentTransformation['r']), end="")
        print("Zo = {: .3f}, {: .3f}, {: .3f} ".format(*currentTransformation['z']))

    # Use gradient of image 1 which does not move
    #im1GradZ, im1GradY, im1GradX = [g.astype('<f4') for g in numpy.gradient(im1)]
    #im2GradZ, im2GradY, im2GradX = [g.astype('<f4') for g in numpy.gradient(im2def)]

    while (iterations <= maxIterations and deltaPhiNorm > deltaPhiMin) or iterations == 0:
        previousLL = LL

        if verbose:
            print("\tIteration Number {:03d} ".format(iterations+1), end="")

        im2defGradZ, im2defGradY, im2defGradX = [g.astype('<f4') for g in numpy.gradient(im2def)]

        M = numpy.zeros((12, 12), dtype='<f8')
        A = numpy.zeros((12),     dtype='<f8')
        # im2 updated
        DICToolkit.computeDICoperatorsGM(im1[crop].astype("<f4"),
                                         im2def[crop].astype("<f4"),
                                         im2defGradZ[crop].astype("<f4"),
                                         im2defGradY[crop].astype("<f4"),
                                         im2defGradX[crop].astype("<f4"),
                                         phaseDiagram.astype("<u1"),
                                         gaussianParameters.astype("<f8"),
                                         M, A)
        ## im2 with guess
        #DICToolkit.computeDICoperatorsGM(im1[crop].astype("<f4"),
                                         #im2def[crop].astype("<f4"),
                                         #im2GradZ[crop].astype("<f4"),
                                         #im2GradY[crop].astype("<f4"),
                                         #im2GradX[crop].astype("<f4"),
                                         #phaseDiagram.astype("<u1"),
                                         #gaussianParameters.astype("<f8"),
                                         #M, A)
        ## im1
        #DICToolkit.computeDICoperatorsGM(im1[crop].astype("<f4"),
                                         #im2def[crop].astype("<f4"),
                                         #im1GradZ[crop].astype("<f4"),
                                         #im1GradY[crop].astype("<f4"),
                                         #im1GradX[crop].astype("<f4"),
                                         #phaseDiagram.astype("<u1"),
                                         #gaussianParameters.astype("<f8"),
                                         #M, A)

        try:
            deltaPhi = numpy.dot(numpy.linalg.inv(M), A)

        except numpy.linalg.linalg.LinAlgError:  # no cover
            singular = True
            # TODO: Calculate error for clean break.
            print('\tsingular M matrix')
            print('exiting')
            exit()
            # break

        deltaPhiNorm = numpy.linalg.norm(deltaPhi)

        # Add padding zeros
        deltaPhi = numpy.hstack([deltaPhi, numpy.zeros(4)]).reshape((4, 4))

        # In Roux X-N paper equation number 11
        #Phi = numpy.dot((numpy.eye(4) - deltaPhi), Phi)
        Phi = numpy.dot(Phi, (numpy.eye(4) + deltaPhi))

        # currentTransformation = spam.deformation.decomposePhi(Phi, PhiPoint=im1centre)
        currentTransformation = spam.deformation.decomposePhi(Phi)

        # Solve for delta Phi
        try:
            PhiInv = numpy.linalg.inv(Phi.copy())
        except numpy.linalg.linalg.LinAlgError:
            singular = True
            break

        im2def = spam.DIC.applyPhi(im2, Phi=PhiInv, interpolationOrder=interpolationOrder)

        residualField = numpy.zeros_like(im2[crop], dtype="<f4")
        phaseField = numpy.zeros_like(im2[crop], dtype="<u1")

        DICToolkit.computeGMresidualAndPhase(im1[crop].astype("<f4"),
                                             im2def[crop].astype("<f4"),
                                             phaseDiagram.astype("<u1"),
                                             gaussianParameters.astype("<f8"),
                                             residualField,
                                             phaseField)

        #DICToolkit.computeGMresidualAndPhase(im1[crop].astype("<f4"),
                                             #im2def[crop].astype("<f4"),
                                             #phaseDiagram.copy().astype("<u1"),
                                             #gaussianParameters.copy().astype("<f8"),
                                             #residualField,
                                             #phaseField)

        # compute current log likelyhood
        # p, _, _ = numpy.histogram2d(im1[crop].ravel(), im2def[crop].ravel(), bins=BINS, range=[[0.0, BINS], [0.0, BINS]], normed=False, weights=None)
        # LL = 0.0
        # for v in p.ravel():
        #     if v:
        #         LL += numpy.log(v)
        p, _, _ = numpy.histogram2d(im1[crop].ravel(), im2def[crop].ravel(), bins=BINS, range=[[0.0, BINS], [0.0, BINS]], normed=False, weights=None)
        LL = numpy.sum(numpy.log(p[numpy.where(p > 0)]))

        if verbose:
            print("LL = {:0.2f} ".format(LL), end="")
            print("dPhi = {:0.4f} ".format(deltaPhiNorm), end="")
            # print("\nPhi", Phi )
            print("Tr = {: .3f}, {: .3f}, {: .3f} ".format(*currentTransformation['t']), end="")
            print("Ro = {: .3f}, {: .3f}, {: .3f} ".format(*currentTransformation['r']), end="")
            print("Zo = {: .3f}, {: .3f}, {: .3f} ".format(*currentTransformation['z']))

        if previousLL < LL*0.6:
            # undo this bad Phi which has increased the LL:
            Phi = numpy.dot((numpy.eye(4) + deltaPhi), Phi)
            returnStatus = -1
            print("Log-likelyhood increasing, divergence condition detected, exiting.")
            # break
            print("...no actually continuing...")

        if GRAPHS:
            NPHASES = gaussianParameters.shape[0]
            grid = plt.GridSpec(2, 4)
            plt.clf()
            plt.suptitle("Gaussian Mixture {} iteration number {} "
                         "|deltaPhi|={:.5f} \nT = [{: 2.4f} {: 2.4f} {:.4f}]\n"
                         "R = [{: 2.4f} {: 2.4f} {: 2.4f}]\n"
                         "Z = [{: 2.4f} {: 2.4f} {: 2.4f}]".format(suffix, iterations, deltaPhiNorm,
                                                                   currentTransformation['t'][0],
                                                                   currentTransformation['t'][1],
                                                                   currentTransformation['t'][2],
                                                                   currentTransformation['r'][0],
                                                                   currentTransformation['r'][1],
                                                                   currentTransformation['r'][2],
                                                                   currentTransformation['z'][0],
                                                                   currentTransformation['z'][1],
                                                                   currentTransformation['z'][2]))

            plt.subplot(grid[0, 0])
            plt.axis('off')
            plt.title('Residual field')
            if sliceAxis == 0:
                plt.imshow(residualField[residualField.shape[0]//2, :, :])
            elif sliceAxis == 1:
                plt.imshow(residualField[:, residualField.shape[1]//2, :])
            elif sliceAxis == 2:
                plt.imshow(residualField[:, :, residualField.shape[2]//2])
            # plt.colorbar()

            plt.subplot(grid[0, 1])
            plt.axis('off')
            plt.title('Phase field')
            if sliceAxis == 0:
                plt.imshow(phaseField[phaseField.shape[0]//2, :, :], vmin=-0.5, vmax=NPHASES+0.5, cmap=mpl.cm.get_cmap(cmapPhases, NPHASES+1))
            elif sliceAxis == 1:
                plt.imshow(phaseField[:, phaseField.shape[1]//2, :], vmin=-0.5, vmax=NPHASES+0.5, cmap=mpl.cm.get_cmap(cmapPhases, NPHASES+1))
            elif sliceAxis == 2:
                plt.imshow(phaseField[:, :, phaseField.shape[2]//2], vmin=-0.5, vmax=NPHASES+0.5, cmap=mpl.cm.get_cmap(cmapPhases, NPHASES+1))
            # plt.colorbar(ticks=numpy.arange(0, NPHASES+1))

            plt.subplot(grid[1, 0])
            plt.axis('off')
            plt.title('im1')
            if sliceAxis == 0:
                plt.imshow(im1[crop][im1[crop].shape[0]//2, :, :])
            elif sliceAxis == 1:
                plt.imshow(im1[crop][:, im1[crop].shape[1]//2, :])
            elif sliceAxis == 2:
                plt.imshow(im1[crop][:, :, im1[crop].shape[2]//2])
            # plt.colorbar()

            plt.subplot(grid[1, 1])
            plt.axis('off')
            plt.title('im2def')
            if sliceAxis == 0:
                plt.imshow(im2def[crop][im2def[crop].shape[0]//2, :, :])
            elif sliceAxis == 1:
                plt.imshow(im2def[crop][:, im2def[crop].shape[1]//2, :])
            elif sliceAxis == 2:
                plt.imshow(im2def[crop][:, :, im2def[crop].shape[2]//2])
            # plt.colorbar()

            plt.subplot(grid[:, 2:])
            plt.axis('off')
            plt.title('Checker Board')
            if sliceAxis == 0:
                plt.imshow(checkerBoard(im1[crop][im2def[crop].shape[0]//2, :, :], im2def[crop][im2def[crop].shape[0]//2, :, :]))
            elif sliceAxis == 1:
                plt.imshow(checkerBoard(im1[crop][:, im2def[crop].shape[1]//2, :], im2def[crop][:, im2def[crop].shape[1]//2, :]))
            elif sliceAxis == 2:
                plt.imshow(checkerBoard(im1[crop][:, :, im2def[crop].shape[2]//2], im2def[crop][:, :, im2def[crop].shape[2]//2]))

            if INTERACTIVE:
                plt.show()
                plt.pause(1.0)
            else:
                plt.savefig('{}/GaussianMixture_Iteration-{}-{}.png'.format(rootPath, iterations, suffix), dpi=600)

        iterations += 1

    if INTERACTIVE:
        plt.ioff()
        plt.close()

    # Positive return status is a healthy end of while loop:
    if iterations >= maxIterations:
        returnStatus = 1
    if deltaPhiNorm <= deltaPhiMin:
        returnStatus = 2
    if singular:
        returnStatus = -2

    if verbose:
        print()
        # pbar.finish()
        if iterations > maxIterations:
            print("\t -> No convergence before max iterations")
        if deltaPhiNorm <= deltaPhiMin:
            print("\t -> Converged")
        if singular:
            print("\t -> Singular")

    return {'transformation': currentTransformation,
            'Phi':            Phi,
            'returnStatus':   returnStatus,
            'iterations':     iterations,
            'residualField':  residualField,
            'phaseField':     phaseField,
            'logLikelyhood':  LL,
            'deltaPhiNorm':   deltaPhiNorm}


################################################################
# helper functions for correlation with different modalities
################################################################

def gaussianMixtureParameters(im1, im2, BINS=64, NPHASES=2, im1threshold=0, im2threshold=0, distanceMaxima=None, fitDistance=None, GRAPHS=False, INTERACTIVE=False, sliceAxis=0, rootPath=".", suffix=""):
    """
    This function, given two different modality images, builds the joint histogram in BINS bins,
    and fits NPHASES peaks with bivariate Gaussian distributions.

    Parameters
    ----------
        im1 : 3D numpy array of floats
            One image,     values should be rescaled to 0:BIN-1

        im2 : 3D numpy array of floats
            Another image, values should be rescaled to 0:BIN-1

        BINS : int, optional
            Number of bins for the joint histogram, recommend 2^x
            Default = 64

        NPHASES : int, optional
            Number of phases to automatically fit
            Default = 2

        im1threshold : float, optional

        im2threshold : float, optional

        distanceMaxima : float, optional

        fitDistance : float, optional

        GRAPHS : bool, optional

        INTERACTIVE : bool, optional

        sliceAxis=0

        rootPath="."

        suffix=""

    Returns
    -------
        gaussianParameters : list of lists
            List of NPHASES components, containing the parameters of the bivariate Gaussian fit for each phase:
            [0] = GLOBALphi -- Normlised "Height" of the fit
            [1] = GLOBALmu1 -- Mean in F of bivairate Gaussian 
            [2] = GLOBALmu2 -- Mean in G of bivairate Gaussian 
            [3] = a         -- 
            [4] = b         --
            [5] = c         --


        p : BINSxBINS 2D numpy array of floats
            The normalised joint histogram, the sum of which will be =1 if all of your image values are 0:BIN-1
    """

    # To fit 2D likelyhood with gaussian ellipsoids
    from scipy.optimize import curve_fit

    # To find maxima in likelyhood which correspond to phases
    import skimage.feature

    # for interactive graphs
    if INTERACTIVE:
        GRAPHS = True
        plt.ion()

    # DEFINE the global variables needed for curve fitting
    GLOBALmu1 = 0.0  # mean of the f image
    GLOBALmu2 = 0.0  # mean of the g image
    GLOBALphi = 0.0  # number of hits (value of the maxima)

    # DEFINE fitting functions
    # https://en.wikipedia.org/wiki/Gaussian_function#Two-dimensional_Gaussian_function
    # def gaussian2Delliptical( XY, GLOBALphi, GLOBALmu2, GLOBALmu1, a, b, c ):
    # Thsi needs to be in here in order to pass GLOBALphi as a global variable.
    # Perhaps it should be optimised?
    def computeLambda(a, b, c, x, GLOBALmu1, y, GLOBALmu2):
        return numpy.longfloat(0.5*(a*(x - GLOBALmu1)**2 + 2.0*b*(x - GLOBALmu1)*(y - GLOBALmu2) + c*(y - GLOBALmu2)**2))

    def gaussian2Delliptical(XY, a, b, c):
        # invert x and y on purpose to be consistent with H
        grid = numpy.array(numpy.meshgrid(XY[1], XY[0]))
        field = numpy.zeros(grid.shape[1:3])
        for ny in range(grid.shape[2]):
            y = grid[0, 0, ny]
            for nx in range(grid.shape[1]):
                x = grid[1, nx, 0]
                field[nx, ny] = float(GLOBALphi) * numpy.exp(-computeLambda(a, b, c, x, GLOBALmu1, y, GLOBALmu2))
        return field.ravel()

    # START function

    im1min = im1.min()
    im1max = im1.max()
    im2min = im2.min()
    im2max = im2.max()

    # f,g discretisation
    X = numpy.linspace(0, BINS-1, BINS)
    Y = numpy.linspace(0, BINS-1, BINS)

    print("\tim1 from {:.2f} to {:.2f}".format(im1min, im1max))
    print("\tim2 from {:.2f} to {:.2f}".format(im2min, im2max))

    # Calculate probability distribution p(f,g)
    p, _, _ = numpy.histogram2d(im1.ravel(), im2.ravel(), bins=BINS, range=[[0.0, BINS], [0.0, BINS]], normed=False, weights=None)
    p /= float(len(im1.ravel()))
    p_sum = p.sum()

    print("\tp normalisation: {:.2f}".format(p_sum))

    # write joint histogram in a dat file for tikz
    # if DATA:
    #     tmp = p.copy()
    #     with open("GaussianMixture_jointHistogram-{}-{}.dat".format(0, suffix), "w") as f:
    #         string = "{}\t {}\t {}\n".format("x", "y", "c")
    #         f.write(string)
    #         for xbin in range(tmp.shape[0]):
    #             x = (xbin+0.5)/tmp.shape[0]
    #             for ybin in range(tmp.shape[1]):
    #                 y = (ybin+0.5)/tmp.shape[1]
    #                 if tmp[xbin, ybin]:
    #                     string = "{}\t {}\t {}\n".format(x, y, tmp[xbin, ybin])
    #                     f.write(string)

    # Get disordered maxima of the joint histogram
    print("\tFind maxima")
    if distanceMaxima is None:
        distanceMaxima = int(BINS/25.0)
    print("\t\tMin distance between maxima: {:.0f}".format(distanceMaxima))
    maxima = skimage.feature.peak_local_max(p, min_distance=int(distanceMaxima))
    nMax = len(maxima)

    if(nMax < NPHASES):
        print("\t\t{} phases asked but only {} maxima...".format(NPHASES, nMax))
    NPHASES = min(NPHASES, nMax)

    # print "\t\t Number of maxima: {:2}".format(nMax)
    if nMax == 0: # no cover
        print("In gaussian fit: no maxium found... Stoping...")
        exit()

    # Organise maxima into muF, muG, p(f,g) the sort at take the maximum
    maxTmp = numpy.zeros((nMax, 3))
    for i, (f, g) in enumerate(maxima):
        if f > im1threshold or g > im2threshold:
            maxTmp[i] = [f, g, p[f, g]]
        # print("\t\t max {:2} --- f: {:.2f}   g: {:.2f}   hits: {}".format(i+1,*maxTmp[i]))

    nMax = 0
    percentage = 0.1
    while nMax < NPHASES:
        maxSorted = [m for m in maxTmp[maxTmp[:, 2].argsort()[::-1]] if float(m[2]) > percentage*float(p_sum)]
        nMax = len(maxSorted)
        print("\t\t{:02d} maxima found over the {} needed with {:.2e} times of the total count".format(nMax, NPHASES, percentage))
        percentage /= 10.0

    for i, (GLOBALmu1, GLOBALmu2, GLOBALphi) in enumerate(maxSorted):
        print("\t\tMaximum {}:\t mu1={:.2f}\t mu2={:.2f}\t Phi={:.2e}".format(i+1, GLOBALmu1, GLOBALmu2, GLOBALphi))
    print("")

    # output of the function: list of fitting gaussian parameters
    # size NPHASES x 6, the 6 parameters being GLOBALlogPhi, GLOBALmu1, GLOBALmu2, a, b, c
    gaussianParameters = numpy.zeros((NPHASES, 6)).astype('<f4')

    # loop over phases
    maxEllipsoid = numpy.zeros_like(p)
    for iPhase in range(NPHASES):
        GLOBALmu1, GLOBALmu2, GLOBALphi = maxSorted[iPhase]
        print("\tPhase {:2}:\t\t mu1={:.2f}\t mu2={:.2f}\t Phi={:.2e}".format(iPhase+1, GLOBALmu1, GLOBALmu2, GLOBALphi))
        if fitDistance is None:
            fitDistance = BINS/2.0

        # fit the probability distribution p(f,g) with an gaussian ellipsoids
        pFit = p.copy()

        for nf in range(pFit.shape[0]):
            for ng in range(pFit.shape[1]):
                posF = nf
                posG = ng
                dist = numpy.sqrt((posF-GLOBALmu1)**2.0 + (posG-GLOBALmu2)**2.0)  # cicrle
                # dist = abs(posF-GLOBALmu1)+abs(posG-GLOBALmu2) # square
                if dist > fitDistance:
                    pFit[nf, ng] = 0.0

        (a, b, c), _ = curve_fit(gaussian2Delliptical, (X, Y), pFit.ravel(), p0=(1, 1, 1))
        print("\t\tFit:\t\t a={:.2f}\t b={:.2f}\t c={:.2f}\t Hessian: {:.2f}".format(a, b, c, a*c-b**2))
        while a*c-b**2 < 0:
            print("\t\t\tWarning: Hessian < 0")
            print("\t\t\t         The gaussian doesn't have a local maximum.")
            fitDistance /= 2.0
            print("\t\t\t         Try with fit distance = {} ".format(fitDistance))

            for nf in range(pFit.shape[0]):
                for ng in range(pFit.shape[1]):
                    posF = nf/float(pFit.shape[0]-1)
                    posG = ng/float(pFit.shape[1]-1)
                    dist = numpy.sqrt((posF-GLOBALmu1)**2.0 + (posG-GLOBALmu2)**2.0)  # cicrle
                    # dist = abs(posF-GLOBALmu1)+abs(posG-GLOBALmu2) # square
                    if dist > fitDistance:
                        pFit[nf, ng] = 0.0

            (a, b, c), _ = curve_fit(gaussian2Delliptical, (X, Y), pFit.ravel(), p0=(1, 1, 1))
            print("\t\tFit:\t\t a={:.2f}\t b={:.2f}\t c={:.2f}\t Hessian: {:.2f}".format(a, b, c, a*c-b**2))

        # compute covariance function
        cov = scipy.linalg.inv(numpy.array([[a, b], [b, c]]))
        print("\t\tCov:\t\t 1,1={:.4f}\t 1,2={:.4f}\t 2,2={:.4f}".format(cov[0, 0], cov[1, 0], cov[1, 1]))

        gaussianParameters[iPhase, 0] = GLOBALphi
        gaussianParameters[iPhase, 1] = GLOBALmu1
        gaussianParameters[iPhase, 2] = GLOBALmu2
        gaussianParameters[iPhase, 3] = a
        gaussianParameters[iPhase, 4] = b
        gaussianParameters[iPhase, 5] = c

        currentEllipsoid = gaussian2Delliptical((X, Y), a, b, c).reshape((len(X), len(Y)))

        maxEllipsoid = numpy.maximum(maxEllipsoid, currentEllipsoid)

        if GRAPHS:
            plt.clf()
            plt.suptitle("Gaussian Mixture fitting Phase number {}".format(iPhase+1))
            plt.subplot(221)
            plt.title("im1 (from {:.2f} to {:.2f})".format(im1.min(), im1.max()))
            plt.axis('off')
            if sliceAxis == 0:
                plt.imshow(im1[im1.shape[0]//2, :, :], vmin=0.0, vmax=BINS)
            elif sliceAxis == 1:
                plt.imshow(im1[:, im1.shape[1]//2, :], vmin=0.0, vmax=BINS)
            elif sliceAxis == 2:
                plt.imshow(im1[:, :, im1.shape[2]//2], vmin=0.0, vmax=BINS)
            plt.colorbar()

            plt.subplot(222)
            plt.title("im2 (from {:.2f} to {:.2f})".format(im2.min(), im2.max()))
            plt.axis('off')
            if sliceAxis == 0:
                plt.imshow(im2[im2.shape[0]//2, :, :], vmin=0.0, vmax=BINS)
            elif sliceAxis == 1:
                plt.imshow(im2[:, im2.shape[1]//2, :], vmin=0.0, vmax=BINS)
            elif sliceAxis == 2:
                plt.imshow(im2[:, :, im2.shape[2]//2], vmin=0.0, vmax=BINS)
            plt.colorbar()

            plt.subplot(223)
            tmp = p.copy()
            tmp[p <= 0] = numpy.nan
            tmp = numpy.log(tmp)
            plt.title("Log Probability log(p(im1,im2))")
            plt.imshow(tmp.T, origin='lower', extent=[0.0, BINS, 0.0, BINS])
            for gp in maxSorted:
                plt.plot(gp[0], gp[1], 'b*')
            plt.plot(GLOBALmu1, GLOBALmu2, 'r*')
            fig = plt.gcf()
            ax = fig.gca()
            ax.add_artist(plt.Circle((GLOBALmu1, GLOBALmu2), fitDistance, color='r', fill=False))
            plt.xlabel("im1")
            plt.ylabel("im2")
            plt.colorbar()

            plt.subplot(224)
            tmp = currentEllipsoid.copy()
            tmp[currentEllipsoid <= 0] = numpy.nan
            tmp = numpy.log(tmp)
            plt.title("Gaussian ellipsoid")
            plt.imshow(tmp.T, origin='lower', extent=[0.0, BINS, 0.0, BINS])
            plt.plot(GLOBALmu1, GLOBALmu2, 'r*')
            plt.xlabel("im1")
            plt.ylabel("im2")
            plt.colorbar()

            if INTERACTIVE:
                plt.show()
                plt.pause(1.0)
            else:
                plt.savefig('{}/GaussianMixture_jointHistogram-{}-{}.png'.format(rootPath, iPhase+1, suffix), dpi=600)

        # p -= currentEllipsoid

        # if DATA:  # write joint histogram in a dat file for tikz
        #     tmp = p.copy()
        #     # tmp_sum = tmp.sum()
        #     with open("GaussianMixture_jointHistogram-{}-{}.dat".format(iPhase+1, suffix), "w") as f:
        #         string = "{}\t {}\t {}\n".format("x", "y", "c")
        #         f.write(string)
        #         for xbin in range(tmp.shape[0]):
        #             x = (xbin+0.5)/tmp.shape[0]
        #             for ybin in range(tmp.shape[1]):
        #                 y = (ybin+0.5)/tmp.shape[1]
        #                 if tmp[xbin, ybin]:
        #                     string = "{}\t {}\t {}\n".format(x, y, float(tmp[xbin, ybin]))
        #                     f.write(string)

        print("")  # end of phase loop

    if INTERACTIVE:
        plt.ioff()
        plt.close()

    # write phase histogram in a dat file for tikz
    # if DATA:
    #     print("\tSave phase repartition")
    #     levels = [10**float(e) for e in numpy.arange(-8,0) ]
    #
    #     contour
    #     plt.clf()
    #     tmp = maxEllipsoid.copy()
    #     plt.title("Maximum gaussian ellispoid")
    #     X = numpy.linspace(0, 1, BINS)
    #     Y = numpy.linspace(0, 1, BINS)
    #     CS = plt.contour(X, Y, tmp.T,  levels=levels)
    #     for gp in maxSorted:
    #     plt.plot(gp[0], gp[1], 'b*')
    #     plt.xlabel("f")
    #     plt.ylabel("g")
    #     plt.colorbar()
    #     plt.savefig('GaussianMixture_phaseContour-{}.png'.format(suffix), dpi=600)

    return gaussianParameters, p


def phaseDiagram(gaussianParameters, jointHistogram, voxelCoverage=None, sigmaMax=9, BINS=64, GRAPHS=False, INTERACTIVE=False, suffix="", rootPath="."):
    """
    To be commented too
    """

    if INTERACTIVE:
        GRAPHS = True
        plt.ion()

    def distanceMax(gaussianParameter):
        phi, muf, mug, a, b, c = gaussianParameter
        return (a*(x-muf)**2+2.0*b*(x-muf)*(y-mug)+c*(y-mug)**2)-numpy.log(phi)

    def distanceMahalanobis(gaussianParameter):
        phi, muf, mug, a, b, c = gaussianParameter
        return numpy.sqrt((a*(x-muf)**2+2.0*b*(x-muf)*(y-mug)+c*(y-mug)**2))

    if voxelCoverage == 1.0 or voxelCoverage is None:
        coverage = 1.0
        phase = numpy.zeros((BINS, BINS), dtype='<u1')
        # define corresponding level
        for xbin in range(BINS):
            x = (xbin+0.5)
            for ybin in range(BINS):
                y = (ybin+0.5)
                distances = numpy.array([distanceMax(gp) for gp in gaussianParameters])
                i = numpy.argmin(distances)
                distanceMin = distances[i]
                phase[xbin, ybin] = i+1
        print("\tVoxel coverage = 100 %")

        if GRAPHS:
            NPHASES = len(gaussianParameters)
            plt.clf()
            plt.title("Phase diagram: voxel coverage = 100%")
            plt.imshow(phase.T, origin='lower', extent=[0.0, BINS, 0.0, BINS], vmin=-0.5, vmax=NPHASES+0.5, cmap=mpl.cm.get_cmap(cmapPhases, NPHASES+1))
            plt.colorbar(ticks=numpy.arange(0, NPHASES+1))
            for gp in gaussianParameters:
                plt.plot(gp[1], gp[2], 'b*')
            plt.xlabel("f")
            plt.ylabel("g")

            if INTERACTIVE:
                plt.show()
                plt.pause(1.0)

    else:
        sigma = numpy.arange(1, sigmaMax+1, 1)[::-1]

        # phases = numpy.zeros((len(sigma), BINS, BINS), dtype='<u1')
        for n, sig in enumerate(sigma):
            phase = numpy.zeros((BINS, BINS), dtype='<u1')
            # define corresponding level
            for xbin in range(BINS):
                x = (xbin+0.5)
                for ybin in range(BINS):
                    y = (ybin+0.5)
                    distancesMax = numpy.array([distanceMax(gp) for gp in gaussianParameters])
                    distancesMah = numpy.array([distanceMahalanobis(gp) for gp in gaussianParameters])
                    i = numpy.argmin(distancesMax)
                    distanceMin = distancesMah[i]

                    if distanceMin < sig:
                        # phases[n, xbin, ybin] = i+1
                        phase[xbin, ybin] = i+1

            coverage = jointHistogram[phase > 0].sum()

            if GRAPHS:
                NPHASES = len(gaussianParameters)
                plt.clf()
                plt.title("Phase diagram for {:.0f}-sigma: voxel coverage = {:.2f}%".format(sig, 100*coverage))
                plt.imshow(phase.T, origin='lower', extent=[0.0, BINS, 0.0, BINS], vmin=-0.5, vmax=NPHASES+0.5, cmap=mpl.cm.get_cmap(cmapPhases, NPHASES+1))
                plt.colorbar(ticks=numpy.arange(0, NPHASES+1))
                for gp in gaussianParameters:
                    plt.plot(gp[1], gp[2], 'b*')
                plt.xlabel("f")
                plt.ylabel("g")

                if INTERACTIVE:
                    plt.show()
                    plt.pause(1.0)
                else:
                    plt.savefig('{}/GaussianMixture_phaseDiagram-{:.0f}sig-{}.png'.format(rootPath, sig, suffix), dpi=600)

            print("\t{:.0f}-sigma: voxel coverage = {:.2f}".format(sig, 100*coverage), end="")
            if coverage > voxelCoverage:
                print(" (> {:.2f}%)".format(100*voxelCoverage))
            else:
                print(" (< {:.2f}%) -> Returning this phase diagram.".format(100*voxelCoverage))
                break

    if GRAPHS and not INTERACTIVE:
        plt.savefig('{}/GaussianMixture_phaseDiagram-{}.png'.format(rootPath, suffix), dpi=600)

    if INTERACTIVE:
        plt.ioff()
        plt.close()

    # phase diagram for different levels
    # for n, sig in enumerate(sigma):
    #     plt.clf()
    #     tmp = phases[n].astype('<f4')
    #     tmp[tmp == 0] = numpy.nan
    #     plt.title("Phases repartition for sigma {}".format(sigma))
    #     plt.imshow(tmp.T, origin='lower', extent=[0.0, 1.0, 0.0, 1.0], vmin=-0.5, vmax=NPHASES+0.5, cmap=mpl.cm.get_cmap(cmapPhases, NPHASES+1))
        # plt.colorbar(ticks=numpy.arange(0, NPHASES+1))
    #     for gp in gaussianParameters:
    #         plt.plot(gp[1], gp[2], 'b*')
    #     plt.xlabel("f")
    #     plt.ylabel("g")
    #     plt.savefig('GaussianMixture_phaseDiagram-level{:02d}-{}.png'.format(n, suffix), dpi=600)

    # import spam.helpers
    # spam.helpers.writeStructuredVTK(cellData={"phases": phases},
    #                aspectRatio=(1.0, 1.0, 1.0), fileName="GaussianMixture_phaseDiagram-{}.vtk".format(suffix))
    # tifffile.imsave("{}/GaussianMixture_phaseDiagram-{}.tif".format(rootPath, suffix), phase)

    return phase, coverage


def checkerBoard(im1, im2, n=5, inv=False, rescale=True):
    """
    This function generates a "checkerboard" mix of two 2D images of the same size.
    This is useful to see if they have been properly aligned, especially if the two images are 
    quantitatively different (i.e., one is a neutron tomography and the other is an x-ray tomography).

    Parameters
    ----------
        im1 : 2D numpy array
            This is the first image

        im2 :  2D/3D numpy array
            This is the second image, should be same shape as first image

        n : integer, optional
            The number of divisions of the checkerboard to aim for.
            Default = 5

        inv : bool, optional
            Whether im2 should be -im2 in the checkerboard.
            Default = False

        rescale : bool, optional
            Whether greylevels should be rescaled with spam.helpers.rescale.
            Default = True

    Returns
    -------
        im1G : checkerBoard mix of im1 and im2
    """
    if inv:  c = -1.0
    else:    c = 1.0

    if rescale:
        import spam.helpers
        im1 = spam.helpers.rescale(im1)
        im2 = spam.helpers.rescale(im2)

    # 2D version
    if len(im1.shape) == 2:
        # initialize
        im1G = im1.copy()

        # get number of pixel / square based on min size
        nP = int(min(im1.shape)/n)

        for x in range(im1.shape[0]):
            for y in range(im1.shape[1]):
                if int((x % (2*nP))/nP) + int((y % (2*nP))/nP) - 1:
                    im1G[x, y] = c*im2[x, y]
    else:
        print("checkerBoard works only with dim2 images")
        return 0

    return im1G

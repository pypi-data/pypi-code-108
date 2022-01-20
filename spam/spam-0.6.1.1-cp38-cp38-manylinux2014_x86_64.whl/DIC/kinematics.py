"""
Library of SPAM functions for post processing a deformation field.
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

import spam.deformation
import numpy
import tifffile
import scipy.spatial
import multiprocessing
import progressbar

nProcessesDefault = multiprocessing.cpu_count()

def estimateLocalQuadraticCoherency(points, displacements, neighbourRadius=None, nNeighbours=None, epsilon=0.1, nProcesses=nProcessesDefault, verbose=False):
    '''
    This function computes the local quadratic coherency (LQC) of a set of displacement vectors as per Masullo and Theunissen 2016.
    LQC is the average residual between the point's displacement and a second-order (parabolic) surface Phi.
    The quadratic surface Phi is fitted to the point's closest N neighbours and evaluated at the point's position.
    Neighbours are selected based on: radius (default option) or number (activated if nNeighbours is not None).
    A point with a LQC value smaller than a threshold (0.1 in Masullo and Theunissen 2016) is classified as coherent

    Parameters
    ----------
        points : n x 3 numpy array of floats
            Coordinates of the points Z, Y, X

        displacements : n x 3 numpy array of floats
            Displacements of the points

        neighbourRadius: float, optional
            Distance in pixels around the point to extract neighbours.
            This OR nNeighbours must be set.
            Default = None

        nNeighbours : int, optional
            Number of the nearest neighbours to consider
            This OR neighbourRadius must be set.
            Default = None

        epsilon: float, optional
            Background error as per (Westerweel and Scarano 2005)
            Default = 0.1

        nProcesses : integer, optional
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : boolean, optional
            Print progress?
            Default = True

    Returns
    -------
        LQC: n x 1 array of floats
            The local quadratic coherency for each point

    Note
    -----
        Based on: https://gricad-gitlab.univ-grenoble-alpes.fr/DVC/pt4d
    '''

    # initialise the coherency matrix
    LQC = numpy.ones((points.shape[0]), dtype=float)

    # build KD-tree for quick neighbour identification
    treeCoord = scipy.spatial.KDTree(points)

    # check if neighbours are selected based on radius or based on number, default is radius
    if (nNeighbours is None) == (neighbourRadius is None):
        print("spam.DIC.estimateLocalQuadraticCoherency(): One and only one of nNeighbours and neighbourRadius must be passed")
    if nNeighbours is not None:
        ball = False
    elif neighbourRadius is not None:
        ball = True

    # calculate coherency for each point
    global coherencyOnePoint
    def coherencyOnePoint(point):
        # select neighbours based on radius
        if ball:
            radius  = neighbourRadius
            indices = numpy.array(treeCoord.query_ball_point(points[point], radius))
            # make sure that at least 27 neighbours are selected
            while len(indices) <= 27:
                radius *= 2
                indices = numpy.array(treeCoord.query_ball_point(points[point], radius))
            N = len(indices)
        # select neighbours based on number
        else:
            _, indices = treeCoord.query(points[point], k=nNeighbours)
            N = nNeighbours

        # fill in point+neighbours positions for the parabolic surface coefficients
        X = numpy.zeros((N, 10), dtype=float)
        for i, neighbour in enumerate(indices):
            pos     = points[neighbour]
            X[i, 0] = 1
            X[i, 1] = pos[0]
            X[i, 2] = pos[1]
            X[i, 3] = pos[2]
            X[i, 4] = pos[0] * pos[1]
            X[i, 5] = pos[0] * pos[2]
            X[i, 6] = pos[1] * pos[2]
            X[i, 7] = pos[0] * pos[0]
            X[i, 8] = pos[1] * pos[1]
            X[i, 9] = pos[2] * pos[2]

        # keep point's index
        i0 = numpy.where(indices == point)[0][0]

        # fill in disp
        u = displacements[indices, 0]
        v = displacements[indices, 1]
        w = displacements[indices, 2]
        UnormMedian = numpy.median(numpy.linalg.norm(displacements[indices], axis=1))

        # deviation of each disp vector from local median
        sigma2 = (u-numpy.median(u))**2 + (v-numpy.median(v))**2 + (w-numpy.median(w))**2

        # coefficient for gaussian weighting
        K = (numpy.sqrt(sigma2).sum())/N
        K += epsilon

        # fill in gaussian weighting diag components
        Wg = numpy.exp(-0.5* sigma2 * K**(-0.5))
        # create the diag matrix
        Wdiag = numpy.diag(Wg)

        # create matrices to solve with least-squares
        XtWX     = numpy.dot(X.T, numpy.dot(Wdiag, X))
        XtWXInv  = numpy.linalg.inv(XtWX) # TODO: check for singular matrix
        XtWUu    = numpy.dot(X.T, numpy.dot(Wdiag, u))
        XtWUv    = numpy.dot(X.T, numpy.dot(Wdiag, v))
        XtWUw    = numpy.dot(X.T, numpy.dot(Wdiag, w))

        # solve least-squares to compute the coefficients of the parabolic surface
        au = numpy.dot(XtWXInv, XtWUu)
        av = numpy.dot(XtWXInv, XtWUv)
        aw = numpy.dot(XtWXInv, XtWUw)

        # evaluate parabolic surface at point's position
        phiu = numpy.dot(au, X[i0, :])
        phiv = numpy.dot(av, X[i0, :])
        phiw = numpy.dot(aw, X[i0, :])

        # compute normalised residuals
        Cu = (phiu - u[i0])**2 / (UnormMedian + epsilon)**2
        Cv = (phiv - v[i0])**2 / (UnormMedian + epsilon)**2
        Cw = (phiw - w[i0])**2 / (UnormMedian + epsilon)**2

        # return coherency as the average normalised residual
        return point, (Cu + Cv + Cw)/3

    if verbose:
        pbar = progressbar.ProgressBar(maxval=points.shape[0]).start()
        finishedPoints = 0

    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(coherencyOnePoint, range(points.shape[0])):
            if verbose:
                finishedPoints += 1
                pbar.update(finishedPoints)
            LQC[returns[0]] = returns[1]
        pool.close()
        pool.join()

    if verbose: pbar.finish()

    return LQC


def estimateDisplacementFromQuadraticFit(fieldCoords, displacements, pointsToEstimate, neighbourRadius=None, nNeighbours=None, epsilon=0.1, nProcesses=nProcessesDefault, verbose=False):
    '''
    This function estimates the displacement of an incoherent point based on a local quadratic fit
    of the displacements of N coherent neighbours, as per Masullo and Theunissen 2016.
    A quadratic surface Phi is fitted to the point's closest coherent neighbours.
    Neighbours are selected based on: radius (default option) or number (activated if nNeighbours is not None)

    Parameters
    ----------
        fieldCoords : n x 3 numpy array of floats
            Coordinates of the points Z, Y, X where displacement is defined

        displacements : n x 3 numpy array of floats
            Displacements of the points

        pointsToEstimate : m x 3  numpy array of floats
            Coordinates of the points Z, Y, X where displacement should be estimated

        neighbourRadius: float, optional
            Distance in pixels around the point to extract neighbours.
            This OR nNeighbours must be set.
            Default = None

        nNeighbours : int, optional
            Number of the nearest neighbours to consider
            This OR neighbourRadius must be set.
            Default = None

        epsilon: float, optional
            Background error as per (Westerweel and Scarano 2005)
            Default = 0.1

        nProcesses : integer, optional
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : boolean, optional
            Print progress?
            Default = True

    Returns
    -------
        displacements: m x 3 array of floats
            The estimated displacements at the requested positions.

    Note
    -----
        Based on https://gricad-gitlab.univ-grenoble-alpes.fr/DVC/pt4d
    '''
    estimatedDisplacements = numpy.zeros_like(pointsToEstimate)

    # build KD-tree of coherent points for quick neighbour identification
    treeCoord = scipy.spatial.KDTree(fieldCoords)

    # check if neighbours are selected based on radius or based on number, default is radius
    if (nNeighbours is None) == (neighbourRadius is None):
        print("spam.DIC.estimateDisplacementFromQuadraticFit(): One and only one of nNeighbours and neighbourRadius must be passed")

    ball = None
    if nNeighbours is not None:
        ball = False
    elif neighbourRadius is not None:
        ball = True

    # estimate disp for each incoherent point
    global dispOnePoint
    def dispOnePoint(pointToEstimate):
        # select neighbours based on radius
        if ball:
            radius = neighbourRadius
            indices = numpy.array(treeCoord.query_ball_point(pointsToEstimate[pointToEstimate], radius))
            # make sure that at least 27 neighbours are selected
            while len(indices) <= 27:
                radius *= 2
                indices = numpy.array(treeCoord.query_ball_point(pointsToEstimate[pointToEstimate], radius))
            N = len(indices)
        # select neighbours based on number
        else:
            _, indices = treeCoord.query(pointsToEstimate[pointToEstimate], k=nNeighbours)
            N = nNeighbours

        # fill in neighbours positions for the parabolic surface coefficients
        X = numpy.zeros((N, 10), dtype=float)
        for i, neighbour in enumerate(indices):
            pos     = fieldCoords[neighbour]
            X[i, 0] = 1
            X[i, 1] = pos[0]
            X[i, 2] = pos[1]
            X[i, 3] = pos[2]
            X[i, 4] = pos[0] * pos[1]
            X[i, 5] = pos[0] * pos[2]
            X[i, 6] = pos[1] * pos[2]
            X[i, 7] = pos[0] * pos[0]
            X[i, 8] = pos[1] * pos[1]
            X[i, 9] = pos[2] * pos[2]

        # fill in point's position for the evaluation of the parabolic surface
        pos0   = pointsToEstimate[pointToEstimate]
        X0     = numpy.zeros((10), dtype=float)
        X0[0]  = 1
        X0[1]  = pos0[0]
        X0[2]  = pos0[1]
        X0[3]  = pos0[2]
        X0[4]  = pos0[0] * pos0[1]
        X0[5]  = pos0[0] * pos0[2]
        X0[6]  = pos0[1] * pos0[2]
        X0[7]  = pos0[0] * pos0[0]
        X0[8]  = pos0[1] * pos0[1]
        X0[9]  = pos0[2] * pos0[2]

        # fill in disp of neighbours
        u = displacements[indices, 0]
        v = displacements[indices, 1]
        w = displacements[indices, 2]
        UnormMedian = numpy.median(numpy.linalg.norm(displacements[indices], axis=1))

        # deviation of each disp vector from local median
        sigma2 = (u-numpy.median(u))**2 + (v-numpy.median(v))**2 + (w-numpy.median(w))**2

        # coefficient for gaussian weighting
        K = (numpy.sqrt(sigma2).sum())/N
        K += epsilon

        # fill in gaussian weighting diag components
        Wg = numpy.exp(-0.5* sigma2 * K**(-0.5)) # careful I think the first 0.5 was missing
        # create the diag matrix
        Wdiag = numpy.diag(Wg)

        # create matrices to solve with least-squares
        XtWX    = numpy.dot(X.T, numpy.dot(Wdiag, X))
        XtWXInv  = numpy.linalg.inv(XtWX) # TODO: check for singular matrix
        XtWUu   = numpy.dot(X.T, numpy.dot(Wdiag, u))
        XtWUv   = numpy.dot(X.T, numpy.dot(Wdiag, v))
        XtWUw   = numpy.dot(X.T, numpy.dot(Wdiag, w))

        # solve least-squares to compute the coefficients of the parabolic surface
        au = numpy.dot(XtWXInv, XtWUu)
        av = numpy.dot(XtWXInv, XtWUv)
        aw = numpy.dot(XtWXInv, XtWUw)

        # evaluate parabolic surface at incoherent point's position
        phiu = numpy.dot(au, X0)
        phiv = numpy.dot(av, X0)
        phiw = numpy.dot(aw, X0)

        return pointToEstimate, [phiu, phiv, phiw]

    # Iterate through flat field of Fs
    if verbose:
        pbar = progressbar.ProgressBar(maxval=pointsToEstimate.shape[0]).start()
        finishedPoints = 0

    # Run multiprocessing filling in FfieldFlatGood, which will then update FfieldFlat
    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(dispOnePoint, range(pointsToEstimate.shape[0])):
            if verbose:
                finishedPoints += 1
                pbar.update(finishedPoints)
            estimatedDisplacements[returns[0]] = returns[1]
        pool.close()
        pool.join()

    if verbose: pbar.finish()

    # overwrite bad points displacements
    return estimatedDisplacements


def interpolatePhiField(fieldCoords, PhiField, pointsToInterpolate, nNeighbours=None, neighbourRadius=None, interpolateF="all", neighbourDistanceWeight='inverse', checkPointSurrounded=False, nProcesses=nProcessesDefault, verbose=False):
    """
    This function interpolates components of a Phi field at a given number of points, using scipy's KD-tree to find neighbours.

    Parameters
    ----------
        fieldCoords : 2D array
            nx3 array of n points coordinates (ZYX)
            centre where each deformation function Phi has been measured

        PhiField : 3D array
            nx4x4 array of n points deformation functions

        pointsToInterpolate : 2D array
            mx3 array of m points coordinates (ZYX)
            Points where the deformation function Phi should be interpolated

        nNeighbours : int, optional
            Number of the nearest neighbours to consider
            This OR neighbourRadius must be set.
            Default = None

        neighbourRadius: float, optional
            Distance in pixels around the point to extract neighbours.
            This OR nNeighbours must be set.
            Default = None

        interpolateF : string, optional
            Interpolate the whole Phi, just the rigid part, or just the displacement?
            Corresponding options are 'all', 'rigid', 'no'
            Default = "all"

        neighbourDistanceWeight : string, optional
            How to weight neigbouring points?
            Possible approaches: inverse of distance, gaussian weighting, straight average, median
            Corresponding options: 'inverse', 'gaussian', 'mean', 'median'

        checkPointSurrounded : bool, optional
            Only interpolate points whose neighbours surround them in Z, Y, X directions
            (or who fall exactly on a give point)?
            Default = False

        nProcesses : integer, optional
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : bool, optional
            follow the progress of the function.
            Default = False

    Returns
    -------
        PhiField : mx4x4 array
            Interpolated **Phi** functions at the requested positions
    """
    tol = 1e-6 # OS is responsible for the validitidy of this magic number

    numberOfPointsToInterpolate = pointsToInterpolate.shape[0]
    # create the k-d tree of the coordinates of good points, we need this to search for the k nearest neighbours easily
    #   for details see: https://en.wikipedia.org/wiki/K-d_tree &
    #   https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.spatial.KDTree.query.html
    treeCoord = scipy.spatial.KDTree(fieldCoords)

    # extract the Phi matrices of the bad points
    outputPhiField = numpy.zeros((numberOfPointsToInterpolate, 4, 4), dtype=PhiField.dtype)

    assert interpolateF in ["all", "rigid", "no"], "spam.DIC.interpolatePhiField(): interpolateF argument should either be 'all', 'rigid', or 'no'"
    assert neighbourDistanceWeight in ["inverse", "gaussian", "mean", "median"], "spam.DIC.interpolatePhiField(): neighbourDistanceWeight argument should be 'inverse', 'gaussian', 'mean', or 'median'"
    # check if neighbours are selected based on radius or based on number, default is radius
    assert (nNeighbours is None) != (neighbourRadius is None), "spam.DIC.interpolatePhiField(): One and only one of nNeighbours and neighbourRadius must be passed"

    if nNeighbours is not None:
        ball = False
    elif neighbourRadius is not None:
        ball = True

    global interpolateOnePoint
    def interpolateOnePoint(pointNumber):
        pointToInterpolate = pointsToInterpolate[pointNumber]
        outputPhi = numpy.zeros((4, 4), dtype=PhiField.dtype)
        outputPhi[-1] = [0, 0, 0, 1]
        if interpolateF == 'no':
            outputPhi[0:3, 0:3] = numpy.eye(3)

        #######################################################
        ### Find neighbours
        #######################################################
        if ball:
            # Ball lookup
            indices = treeCoord.query_ball_point(pointToInterpolate, neighbourRadius)
            if len(indices) == 0:
                # No point!
                return pointNumber, numpy.eye(4) * numpy.nan
            else:
                distances = numpy.linalg.norm(pointToInterpolate - fieldCoords[indices], axis=1)
        else:
            # Number of Neighbour lookup
            distances, indices = treeCoord.query(pointToInterpolate, k=nNeighbours)
        indices   = numpy.array(indices)
        distances = numpy.array(distances)

        #######################################################
        ### Check if there is only one neighbour
        #######################################################
        if indices.size == 1:
            if checkPointSurrounded:
                # unless they're the same point, can't be surrounded
                if not numpy.allclose(fieldCoords[indices], pointToInterpolate):
                    return pointNumber, numpy.eye(4)*numpy.nan
            
            if interpolateF in ["all", "rigid"]: # We need to interpolate all 12 components of Phi
                outputPhi = PhiField[indices].copy()
                if interpolateF == "rigid":
                    outputPhi = spam.deformation.computeRigidPhi(outputPhi)
            else: # interpolate only displacements
                outputPhi[0:3, -1] = PhiField[indices, 0:3, -1].copy()
            
            return pointNumber, outputPhi

        #######################################################
        ### If > 1 neighbour, interpolate Phi or displacements
        #######################################################
        else:
            if neighbourDistanceWeight == 'inverse':
                weights = (1/(distances+tol))
            elif neighbourDistanceWeight == 'gaussian':
                # This could be an input variable VVVVVVVVVVVVVVVVVVVVVV--- the gaussian weighting distance
                weights = numpy.exp(-distances**2/numpy.max(distances/2)**2)
            elif neighbourDistanceWeight == 'mean':
                weights = numpy.ones_like(distances)
            elif neighbourDistanceWeight == 'median':
                # is this the equivalent kernel to a median, we think so...
                weights = numpy.zeros_like(distances)
                weights[len(distances)//2] = 1

            if checkPointSurrounded:
                posMax = numpy.array([fieldCoords[indices, i].max() for i in range(3)])
                posMin = numpy.array([fieldCoords[indices, i].min() for i in range(3)])
                if not numpy.logical_and(numpy.all(pointToInterpolate >= posMin),
                                         numpy.all(pointToInterpolate <= posMax)):
                    return pointNumber, numpy.eye(4)*numpy.nan

            if interpolateF == 'no':
                outputPhi[0:3,-1] = numpy.sum(PhiField[indices, 0:3,-1] * weights[:, numpy.newaxis],                axis=0) / weights.sum()
            else:
                outputPhi[:-1]    = numpy.sum(PhiField[indices, :-1]    * weights[:, numpy.newaxis, numpy.newaxis], axis=0) / weights.sum()

                if interpolateF == "rigid":
                    outputPhi = spam.deformation.computeRigidPhi(outputPhi)

            return pointNumber, outputPhi


    if verbose:
        print("\nStarting Phi field interpolation (with {} process{})".format(nProcesses, 'es' if nProcesses > 1 else ''))
        widgets = [progressbar.Bar(), ' ', progressbar.AdaptiveETA()]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=numberOfPointsToInterpolate)
        pbar.start()
        finishedNodes = 0

    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(interpolateOnePoint, range(numberOfPointsToInterpolate)):
            # Update progres bar if point is not skipped
            if verbose:
                pbar.update(finishedNodes)
                finishedNodes += 1

            outputPhiField[returns[0]]  = returns[1]
        pool.close()
        pool.join()

    if verbose: pbar.finish()

    return outputPhiField


def mergeRegularGridAndDiscrete(regularGrid=None, discrete=None, labelledImage=None, binningLabelled=1, alwaysLabel=True):
    """
    This function corrects a Phi field from the spam-ldic script (measured on a regular grid)
    by looking into the results from one or more spam-ddic results (measured on individual labels)
    by applying the discrete measurements to the grid points.

    This can be useful where there are large flat zones in the image that cannot
    be correlated with small correlation windows, but can be identified and
    tracked with a spam-ddic computation (concrete is a good example).

    Parameters
    -----------
        regularGrid : dictionary
            Dictionary containing readCorrelationTSV of regular grid correlation script, `spam-ldic`.
            Default = None

        discrete : dictionary or list of dictionaries
            Dictionary (or list thereof) containing readCorrelationTSV of discrete correlation script, `spam-ddic`.
            File name of TSV from DICdiscrete client, or list of filenames
            Default = None

        labelledImage : 3D numpy array of ints, or list of numpy arrays
            Labelled volume used for discrete computation
            Default = None

        binningLabelled : int
            Are the labelled images and their PhiField at a different bin level than
            the regular field?
            Default = 1

        alwaysLabel : bool
            If regularGrid point falls inside the label, should we use the
            label displacement automatically?
            Otherwise if the regularGrid point has converged should we use that?
            Default = True (always use Label displacement)

    Returns
    --------
        Either dictionary or TSV file
            Output matrix, with number of rows equal to spam-ldic (the node spacing of the regular grid) and with columns:
            "NodeNumber", "Zpos", "Ypos", "Xpos", "Zdisp", "Ydisp", "Xdisp", "deltaPhiNorm", "returnStatus", "iterations"
    """
    import spam.helpers

    # If we have a list of input discrete files, we also need a list of labelled images
    if type(discrete) == list:
        if type(labelledImage) != list:
            print("spam.deformation.deformationFunction.mergeRegularGridAndDiscrete(): if you pass a list of discreteTSV you must also pass a list of labelled images")
            return
        if len(discrete) != len(labelledImage):
            print("spam.deformation.deformationFunction.mergeRegularGridAndDiscrete(): len(discrete) must be equal to len(labelledImage)")
            return
        nDiscrete = len(discrete)

    # We have only one TSV and labelled image, it should be a number array
    else:
        if type(labelledImage) != numpy.ndarray:
            print("spam.deformation.deformationFunction.mergeRegularGridAndDiscrete(): with a single discrete TSV file, labelledImage must be a numpy array")
            return
        discrete = [discrete]
        labelledImage = [labelledImage]
        nDiscrete = 1

    output = {}

    # Regular grid is the master, and so we copy dimensions and positions
    output['fieldDims']   = regularGrid['fieldDims']
    output['fieldCoords'] = regularGrid['fieldCoords']

    output['PhiField']      = numpy.zeros_like(regularGrid['PhiField'])
    output['iterations']    = numpy.zeros_like(regularGrid['iterations'])
    output['deltaPhiNorm']  = numpy.zeros_like(regularGrid['deltaPhiNorm'])
    output['returnStatus']  = numpy.zeros_like(regularGrid['returnStatus'])
    output['pixelSearchCC'] = numpy.zeros_like(regularGrid['returnStatus'])
    output['error']         = numpy.zeros_like(regularGrid['returnStatus'])
    output['mergeSource']   = numpy.zeros_like(regularGrid['iterations'])

    # from progressbar import ProgressBar
    # pbar = ProgressBar()

    # For each point on the regular grid...
    #for n, gridPoint in pbar(enumerate(regularGrid['fieldCoords'].astype(int))):
    for n, gridPoint in enumerate(regularGrid['fieldCoords'].astype(int)):
        # Find labels corresponding to this grid position for the labelledImage images
        labels = []
        for m in range(nDiscrete):
            labels.append(int(labelledImage[m][int(gridPoint[0] / float(binningLabelled)),
                                               int(gridPoint[1] / float(binningLabelled)),
                                               int(gridPoint[2] / float(binningLabelled))]))
        labels = numpy.array(labels)

        # Is the point inside a discrete label?
        if (labels == 0).all() or (not alwaysLabel and regularGrid['returnStatus'][n] == 2):
            ### Use the REGULAR GRID MEASUREMENT
            # If we're not in a label, copy the results from DICregularGrid
            output['PhiField'][n]      = regularGrid['PhiField'][n]
            output['deltaPhiNorm'][n]  = regularGrid['deltaPhiNorm'][n]
            output['returnStatus'][n]  = regularGrid['returnStatus'][n]
            output['iterations'][n]    = regularGrid['iterations'][n]
            #output['error'][n]         = regularGrid['error'][n]
            #output['pixelSearchCC'][n] = regularGrid['pixelSearchCC'][n]
        else:
            ### Use the DISCRETE MEASUREMENT
            # Give precedence to earliest non-zero-labelled discrete field, conflicts not handled
            m = numpy.where(labels != 0)[0][0]
            label = labels[m]
            #print("m,label = ", m, label)
            tmp = discrete[m]['PhiField'][label].copy()
            tmp[0:3, -1] *= float(binningLabelled)
            translation = spam.deformation.decomposePhi(tmp, PhiCentre=discrete[m]['fieldCoords'][label] * float(binningLabelled), PhiPoint=gridPoint)['t']
            # This is the Phi we will save for this point -- take the F part of the labelled's Phi
            phi = discrete[m]['PhiField'][label].copy()
            # ...and add the computed displacement as applied to the grid point
            phi[0:3, -1] = translation

            output['PhiField'][n]      = phi
            output['deltaPhiNorm'][n]  = discrete[m]['deltaPhiNorm'][label]
            output['returnStatus'][n]  = discrete[m]['returnStatus'][label]
            output['iterations'][n]    = discrete[m]['iterations'][label]
            #output['error'][n]         = discrete[m]['error'][label]
            #output['pixelSearchCC'][n] = discrete[m]['pixelSearchCC'][label]
            output['mergeSource'][n]   = m+1

    #if fileName is not None:
        #TSVheader = "NodeNumber\tZpos\tYpos\tXpos\tFzz\tFzy\tFzx\tZdisp\tFyz\tFyy\tFyx\tYdisp\tFxz\tFxy\tFxx\tXdisp"
        #outMatrix = numpy.array([numpy.array(range(output['fieldCoords'].shape[0])),
                                 #output['fieldCoords'][:, 0],     output['fieldCoords'][:, 1],    output['fieldCoords'][:, 2],
                                 #output['PhiField'][:, 0, 0],     output['PhiField'][:, 0, 1],    output['PhiField'][:, 0, 2],    output['PhiField'][:, 0, 3],
                                 #output['PhiField'][:, 1, 0],     output['PhiField'][:, 1, 1],    output['PhiField'][:, 1, 2],    output['PhiField'][:, 1, 3],
                                 #output['PhiField'][:, 2, 0],     output['PhiField'][:, 2, 1],    output['PhiField'][:, 2, 2],    output['PhiField'][:, 2, 3]]).T

        #outMatrix = numpy.hstack([outMatrix, numpy.array([output['iterations'],
                                                          #output['returnStatus'],
                                                          #output['deltaPhiNorm'],
                                                          #output['mergeSource']]).T])
        #TSVheader = TSVheader+"\titerations\treturnStatus\tdeltaPhiNorm\tmergeSource"

        #numpy.savetxt(fileName,
                      #outMatrix,
                      #fmt='%.7f',
                      #delimiter='\t',
                      #newline='\n',
                      #comments='',
                      #header=TSVheader)
    #else:
    return output


def getDisplacementFromNeighbours(labIm, DVC, fileName, method='getLabel', centresOfMass=None, previousDVC=None):
    """
    This function computes the displacement as the mean displacement from the neighbours, for non-converged grains using a TSV file obtained from `spam-ddic` script. Returns a new TSV file with the new Phi (composed only by the displacement part). 

    The generated TSV can be used as an input for `spam-ddic`. 

    Parameters
    -----------
        lab : 3D array of integers
            Labelled volume, with lab.max() labels

        DVC : dictionary
            Dictionary with deformation field, obtained from `spam-ddic` script, and read using `spam.helpers.tsvio.readCorrelationTSV()` with `readConvergence=True, readPSCC=True, readLabelDilate=True`

        fileName : string
            FileName including full path and .tsv at the end to write

        method : string, optional
            Method to compute the neighbours using `spam.label.getNeighbours()`.
            'getLabel' : The neighbours are the labels inside the subset obtained through spam.getLabel()
            'mesh' : The neighbours are computed using a tetrahedral connectivity matrix
            Default = 'getLabel'

        centresOfMass : lab.max()x3 array of floats, optional
            Centres of mass in format returned by ``centresOfMass``.
            If not defined (Default = None), it is recomputed by running ``centresOfMass``

        previousDVC : dictionary, optional
            Dictionary with deformation field, obtained from `spam-ddic` script, and read using `spam.helpers.tsvio.readCorrelationTSV()` for the previous step.
            This allows the to compute only the displacement increment from the neighbours, while using the F tensor from a previous (converged) step.
            If `previousDVS = None`, then the resulting Phi would be composed only by the displacement of the neighbours.
            Default = None

    Returns
    --------
        Dictionary
            TSV file with the same columns as the input
    """
    import spam.label

    # Compute centreOfMass if needed
    if centresOfMass == None:
        centresOfMass = spam.label.centresOfMass(labIm)
    # Get number of labels
    numberOfLabels = (labIm.max() + 1).astype('u4')
    # Create Phi field
    PhiField = numpy.zeros((numberOfLabels, 4, 4), dtype='<f4')
    # Rest of arrays
    try:
        iterations = DVC['iterations']
        returnStatus = DVC['returnStatus']
        deltaPhiNorm = DVC['deltaPhiNorm']
        PSCC = DVC['pixelSearchCC']
        labelDilateList = DVC['LabelDilate']
        error = DVC['error']

        # Get the problematic labels
        probLab = numpy.where(DVC['returnStatus']!= 2)[0]
        # Remove the 0 from the wrongLab list
        probLab = probLab[~numpy.in1d(probLab, 0)]
        # Get neighbours
        neighbours = spam.label.getNeighbours(labIm, probLab, method = method)
        # Solve first the converged particles - make a copy of the PhiField
        for i in range(numberOfLabels):
            PhiField[i] = DVC['PhiField'][i]
        # Work on the problematic labels
        widgets = [progressbar.FormatLabel(''), ' ', progressbar.Bar(), ' ', progressbar.AdaptiveETA()]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(probLab))
        pbar.start()
        for i in range(0, len(probLab), 1):
            wrongLab = probLab[i]
            neighboursLabel = neighbours[i]
            t = []
            for n in neighboursLabel:
                # Check the return status of each neighbour 
                if DVC['returnStatus'][n] == 2:
                    # We dont have a previous DVC file loaded
                    if previousDVC is None:
                        # Get translation, rotation and zoom from Phi
                        nPhi = spam.deformation.deformationFunction.decomposePhi(DVC['PhiField'][n])
                        # Append the results
                        t.append(nPhi['t'])
                    # We have a previous DVC file loaded
                    else:
                        # Get translation, rotation and zoom from Phi at t=step
                        nPhi = spam.deformation.deformationFunction.decomposePhi(DVC['PhiField'][n])
                        # Get translation, rotation and zoom from Phi at t=step-1
                        nPhiP = spam.deformation.deformationFunction.decomposePhi(previousDVC['PhiField'][n])
                        # Append the incremental results
                        t.append(nPhi['t']-nPhiP['t'])
            # Transform list to array
            if not t:
                # This is a non-working label, take care of it
                Phi = spam.deformation.computePhi({'t': [0,0,0]})
                PhiField[wrongLab] = Phi
            else:
                t = numpy.asarray(t)
                # Compute mean
                meanT = numpy.mean(t, axis = 0)
                # Reconstruct 
                transformation = {'t': meanT}
                Phi = spam.deformation.computePhi(transformation)
                # Save
                if previousDVC is None:
                    PhiField[wrongLab] = Phi
                else:
                    PhiField[wrongLab] = previousDVC['PhiField'][wrongLab]
                    # Add the incremental displacement
                    PhiField[wrongLab][:-1,-1] += Phi[:-1,-1]
            # Update the progressbar
            widgets[0] = progressbar.FormatLabel("{}/{} ".format(i, numberOfLabels))
            pbar.update(i)
        # Save
        outMatrix = numpy.array([numpy.array(range(numberOfLabels)), 
                                centresOfMass[:, 0], centresOfMass[:, 1], centresOfMass[:, 2],
                                PhiField[:, 0, 3], PhiField[:, 1, 3], PhiField[:, 2, 3], 
                                PhiField[:, 0, 0], PhiField[:, 0, 1], PhiField[:, 0, 2], 
                                PhiField[:, 1, 0], PhiField[:, 1, 1], PhiField[:, 1, 2], 
                                PhiField[:, 2, 0], PhiField[:, 2, 1], PhiField[:, 2, 2], 
                                PSCC, error, iterations, returnStatus, deltaPhiNorm, labelDilateList]).T
        numpy.savetxt(fileName, 
                      outMatrix, 
                      fmt='%.7f', 
                      delimiter='\t',
                      newline='\n', 
                      comments='', 
                      header="Label\tZpos\tYpos\tXpos\t" + 
                              "Zdisp\tYdisp\tXdisp\t" + 
                              "Fzz\tFzy\tFzx\t" + 
                              "Fyz\tFyy\tFyx\t" + 
                              "Fxz\tFxy\tFxx\t" + 
                              "pixelSearchCC\terror\titerations\treturnStatus\tdeltaPhiNorm\tLabelDilate") 
    except:
        print('spam.deformation.deformationField.getDisplacementFromNeighbours(): Missing information in the input TSV. Make sure you are reading iterations, returnStatus, deltaPhiNorm, pixelSearchCC, LabelDilate, and error.')
        print('spam.deformation.deformationField.getDisplacementFromNeighbours(): Aborting') 


def applyRegistrationToPoints(Phi, PhiCentre, points, applyF='all', nProcesses=nProcessesDefault, verbose=False):
    """
    This function takes a whole-image registration and applies it to a set of points

    Parameters
    ----------

        Phi : 4x4 numpy array of floats
            Measured Phi function to apply to points

        PhiCentre : 3-component list of floats
            Origin where the Phi is measured (normally the middle of the image unless masked)

        points : nx3 numpy array of floats
            Points to apply the Phi to

        applyF : string, optional
            The whole Phi is *always* applied to the positions of the points to get their displacement.
            This mode *only* controls what is copied into the F for each point, everything, only rigid, or only displacements?
            Corresponding options are 'all', 'rigid', 'no'
            Default = "all"

        nProcesses : integer, optional
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : boolean, optional
            Print progress?
            Default = True

    Returns
    -------
        PhiField : nx4x4 numpy array of floats
            Output Phi field
    """
    assert applyF in ["all", "rigid", "no"], "spam.DIC.applyRegistrationToPoints(): applyF should be 'all', 'rigid', or 'no'"

    numberOfPoints = points.shape[0]

    PhiField = numpy.zeros((numberOfPoints, 4, 4), dtype=float)

    if applyF == "rigid":
        PhiRigid = spam.deformation.computeRigidPhi(Phi)

    global applyPhiToPoint
    def applyPhiToPoint(n):
        # We have a registration to apply to all points.
        # This is done in 2 steps:
        #   1. by copying the registration's little F to the Fs of all points (depending on mode)
        #   2. by calling the decomposePhi function to compute the translation of each point
        if applyF == "all":
            outputPhi = Phi.copy()
        elif applyF == "rigid":
            outputPhi = PhiRigid.copy()
        else: # applyF is displacement only
            outputPhi = numpy.eye(4)
        outputPhi[0:3, -1] = spam.deformation.decomposePhi(Phi,
                                                           PhiCentre=PhiCentre,
                                                           PhiPoint=points[n])["t"]
        return n, outputPhi

    if verbose:
        pbar = progressbar.ProgressBar(maxval=numberOfPoints).start()
        finishedPoints = 0

    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(applyPhiToPoint, range(numberOfPoints)):
            if verbose:
                finishedPoints += 1
                pbar.update(finishedPoints)
            PhiField[returns[0]] = returns[1]
        pool.close()
        pool.join()

    if verbose: pbar.finish()

    return PhiField


def mergeRegistrationAndDiscreteFields(regTSV, discreteTSV, fileName, regTSVBinRatio=1):
    """
    This function merges a registration TSV with a discrete TSV.
    Can be used to create the first guess for `spam-ddic`, using the registration over the whole file, and a previous result from `spam-ddic`.


    Parameters
    -----------

        regTSV : dictionary
            Dictionary with deformation field, obtained from a registrion, usually from the whole sample, and read using `spam.helpers.tsvio.readCorrelationTSV()`

        discreteTSV : dictionary
            Dictionary with deformation field, obtained from `spam-ddic` script, and read using `spam.helpers.tsvio.readCorrelationTSV()`

        fileName : string
            FileName including full path and .tsv at the end to write

        regTSVBinRatio : float, optional
            Change translations from regTSV, if it's been calculated on a differently-binned image. Default = 1

    Returns
    --------
        Dictionary
            TSV file with the same columns as the input
    """

    # Create a first guess
    phiGuess = discreteTSV['PhiField'].copy()
    # Main loop
    for lab in range(discreteTSV['numberOfLabels']):
        # Initial position of a grain
        iniPos = discreteTSV['fieldCoords'][lab]
        # Position of the label at T+1
        deformPos = iniPos + discreteTSV['PhiField'][lab][:-1,-1]
        # Compute the extra displacement and rotation
        extraDisp = spam.deformation.decomposePhi(regTSV['PhiField'][0], 
                                                  PhiCentre = regTSV['fieldCoords'][0], 
                                                  PhiPoint = deformPos)['t']
        # Add the extra disp to the phi guess
        phiGuess[lab][:-1,-1] += extraDisp*regTSVBinRatio

    # Save
    outMatrix = numpy.array([numpy.array(range(discreteTSV['numberOfLabels'])),
                             discreteTSV['fieldCoords'][:, 0], 
                             discreteTSV['fieldCoords'][:, 1], 
                             discreteTSV['fieldCoords'][:, 2], 
                             phiGuess[:, 0, 3], phiGuess[:, 1, 3], phiGuess[:, 2, 3], 
                             phiGuess[:, 0, 0], phiGuess[:, 0, 1], phiGuess[:, 0, 2], 
                             phiGuess[:, 1, 0], phiGuess[:, 1, 1], phiGuess[:, 1, 2], 
                             phiGuess[:, 2, 0], phiGuess[:, 2, 1], phiGuess[:, 2, 2], 
                             numpy.zeros(((discreteTSV['numberOfLabels'])), dtype='<f4'), 
                             discreteTSV['iterations'], 
                             discreteTSV['returnStatus'], 
                             discreteTSV['deltaPhiNorm']]).T
    numpy.savetxt(fileName, 
                  outMatrix, 
                  fmt='%.7f', 
                  delimiter='\t', 
                  newline='\n', 
                  comments='', 
                  header="Label\tZpos\tYpos\tXpos\t" + 
                         "Zdisp\tYdisp\tXdisp\t" + 
                         "Fzz\tFzy\tFzx\t" + 
                         "Fyz\tFyy\tFyx\t" + 
                         "Fxz\tFxy\tFxx\t" + "PSCC\titerations\treturnStatus\tdeltaPhiNorm")




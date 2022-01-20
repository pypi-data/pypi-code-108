"""
Library of SPAM functions for dealing with fields of Phi or fields of F
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

# 2020-02-24 Olga Stamati and Edward Ando
import spam.deformation
import numpy
import progressbar
import spam.label
import multiprocessing

# Global number of processes
nProcessesDefault = multiprocessing.cpu_count()

def FfieldRegularQ8(displacementField, nodeSpacing, nProcesses=nProcessesDefault, verbose=True):
    """
    This function computes the transformation gradient field F from a given displacement field.
    Please note: the transformation gradient tensor: F = I + du/dx.

    This function computes du/dx in the centre of an 8-node cell (Q8 in Finite Elements terminology) using order one (linear) shape functions.

    Parameters
    ----------
        displacementField : 4D array of floats
            The vector field to compute the derivatives.
            #Its shape is (nz, ny, nx, 3)

        nodeSpacing : 3-component list of floats
            Length between two nodes in every direction (*i.e.,* size of a cell)

        nProcesses : integer, optional
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : boolean, optional
            Print progress?
            Default = True

    Returns
    -------
        F : (nz-1) x (ny-1) x (nx-1) x 3x3 array of n cells
            The field of the transformation gradient tensors
    """
    # import spam.DIC.deformationFunction
    #import spam.mesh.strain

    # Define dimensions
    dims = list(displacementField.shape[0:3])

    # Q8 has 1 element fewer than the number of displacement points
    cellDims = [n - 1 for n in dims]

    # Check if a 2D field is passed
    if dims[0] == 1:
        # Add a ficticious layer of nodes and cells in Z direction
        dims[0] += 1
        cellDims[0] += 1
        nodeSpacing[0] += 1

        # Add a ficticious layer of equal displacements so that the strain in z is null
        displacementField = numpy.concatenate((displacementField, displacementField))

    numberOfCells = cellDims[0]*cellDims[1]*cellDims[2]
    dims = tuple(dims)
    cellDims = tuple(cellDims)

    # Transformation gradient tensor F = du/dx +I
    Ffield = numpy.zeros((cellDims[0], cellDims[1], cellDims[2], 3, 3))
    FfieldFlat = Ffield.reshape((numberOfCells, 3, 3))

    # Define the coordinates of the Parent Element
    # we're using isoparametric Q8 elements
    lid = numpy.zeros((8, 3)).astype('<u1')  # local index
    lid[0] = [0, 0, 0]
    lid[1] = [0, 0, 1]
    lid[2] = [0, 1, 0]
    lid[3] = [0, 1, 1]
    lid[4] = [1, 0, 0]
    lid[5] = [1, 0, 1]
    lid[6] = [1, 1, 0]
    lid[7] = [1, 1, 1]


    # Calculate the derivatives of the shape functions
    # Since the center is equidistant from all 8 nodes, each one gets equal weighting
    SFderivative = numpy.zeros((8, 3))
    for node in range(8):
        # (local nodes coordinates) / weighting of each node
        SFderivative[node, 0] = (2.0 * (float(lid[node, 0]) - 0.5)) / 8.0
        SFderivative[node, 1] = (2.0 * (float(lid[node, 1]) - 0.5)) / 8.0
        SFderivative[node, 2] = (2.0 * (float(lid[node, 2]) - 0.5)) / 8.0

    # Compute the jacobian to go from local(Parent Element) to global base
    jacZ = 2.0 / float(nodeSpacing[0])
    jacY = 2.0 / float(nodeSpacing[1])
    jacX = 2.0 / float(nodeSpacing[2])

    if verbose:
        pbar = progressbar.ProgressBar(maxval=numberOfCells).start()
        finishedCells = 0

    # Loop over the cells
    global computeOneQ8
    def computeOneQ8(cell):
        zCell, yCell, xCell = numpy.unravel_index(cell, cellDims)

        # Check for nans in one of the 8 nodes of the cell
        if not numpy.all(numpy.isfinite(displacementField[zCell:zCell + 2, yCell:yCell + 2, xCell:xCell + 2])):
            F = numpy.zeros((3, 3)) * numpy.nan

        # If no nans start the strain calculation
        else:
            # Initialise the gradient of the displacement tensor
            dudx = numpy.zeros((3, 3))

            # Loop over each node of the cell
            for node in range(8):
                # Get the displacement value
                d = displacementField[int(zCell + lid[node, 0]), int(yCell + lid[node, 1]), int(xCell + lid[node, 2]), :]

                # Compute the influence of each node to the displacement gradient tensor
                dudx[0, 0] += jacZ * SFderivative[node, 0] * d[0]
                dudx[1, 1] += jacY * SFderivative[node, 1] * d[1]
                dudx[2, 2] += jacX * SFderivative[node, 2] * d[2]
                dudx[1, 0] += jacY * SFderivative[node, 1] * d[0]
                dudx[0, 1] += jacZ * SFderivative[node, 0] * d[1]
                dudx[2, 1] += jacX * SFderivative[node, 2] * d[1]
                dudx[1, 2] += jacY * SFderivative[node, 1] * d[2]
                dudx[2, 0] += jacX * SFderivative[node, 2] * d[0]
                dudx[0, 2] += jacZ * SFderivative[node, 0] * d[2]
            # Adding a transpose to dudx, it's ugly but allows us to pass #142
            F = numpy.eye(3)+dudx.T
        return cell, F

    # Run multiprocessing
    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(computeOneQ8, range(numberOfCells)):
            if verbose:
                finishedCells += 1
                pbar.update(finishedCells)
            FfieldFlat[returns[0]] = returns[1]
        pool.close()
        pool.join()

    if verbose: pbar.finish()

    return Ffield


def FfieldRegularGeers(displacementField, nodeSpacing, neighbourRadius=1.5, nProcesses=nProcessesDefault, verbose=True):
    """
    This function computes the transformation gradient field F from a given displacement field.
    Please note: the transformation gradient tensor: F = I + du/dx.

    This function computes du/dx as a weighted function of neighbouring points.
    Here is implemented the linear model proposed in:
    "Computing strain fields from discrete displacement fields in 2D-solids", Geers et al., 1996

    Parameters
    ----------
        displacementField : 4D array of floats
            The vector field to compute the derivatives.
            Its shape is (nz, ny, nx, 3).

        nodeSpacing : 3-component list of floats
            Length between two nodes in every direction (*i.e.,* size of a cell)

        neighbourRadius : float, optional
            Distance in nodeSpacings to include neighbours in the strain calcuation.
            Default = 1.5*nodeSpacing which will give radius = 1.5*min(nodeSpacing)

        mask : bool, optional
            Avoid non-correlated NaN points in the displacement field?
            Default = True

        nProcesses : integer, optional
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : boolean, optional
            Print progress?
            Default = True

    Returns
    -------
        Ffield: nz x ny x nx x 3x3 array of n cells
            The field of the transformation gradient tensors

    Note
    ----
        Taken from the implementation in "TomoWarp2: A local digital volume correlation code", Tudisco et al., 2017
    """
    import scipy.spatial

    ##Define dimensions
    dims = displacementField.shape[0:3]
    nNodes = dims[0]*dims[1]*dims[2]
    displacementFieldFlat = displacementField.reshape(nNodes, 3)

    # Check if a 2D field is passed
    twoD = False
    if dims[0] == 1: twoD = True

    #Deformation gradient tensor F = du/dx +I
    Ffield = numpy.zeros((dims[0], dims[1], dims[2], 3, 3))
    FfieldFlat = numpy.zeros((nNodes, 3, 3))

    if twoD:
        fieldCoordsFlat = numpy.mgrid[0:1:1,
                                      nodeSpacing[1]:dims[1]*nodeSpacing[1]+nodeSpacing[1]:nodeSpacing[1],
                                      nodeSpacing[2]:dims[2]*nodeSpacing[2]+nodeSpacing[2]:nodeSpacing[2]].reshape(3, nNodes).T
    else:
        fieldCoordsFlat = numpy.mgrid[nodeSpacing[0]:dims[0]*nodeSpacing[0]+nodeSpacing[0]:nodeSpacing[0],
                                      nodeSpacing[1]:dims[1]*nodeSpacing[1]+nodeSpacing[1]:nodeSpacing[1],
                                      nodeSpacing[2]:dims[2]*nodeSpacing[2]+nodeSpacing[2]:nodeSpacing[2]].reshape(3, nNodes).T

    #Get non-nan displacements
    goodPointsMask = numpy.isfinite(displacementField[:,:,:,0].reshape(nNodes))
    badPointsMask  = numpy.isnan(   displacementField[:,:,:,0].reshape(nNodes))
    #Flattened variables
    fieldCoordsFlatGood       = fieldCoordsFlat[goodPointsMask]
    displacementFieldFlatGood = displacementFieldFlat[goodPointsMask]
    #set bad points to nan
    FfieldFlat[badPointsMask] = numpy.eye(3) * numpy.nan

    #build KD-tree for neighbour identification
    treeCoord = scipy.spatial.KDTree(fieldCoordsFlatGood)

    # Output array for good points
    FfieldFlatGood = numpy.zeros_like(FfieldFlat[goodPointsMask])

    # Function for parallel mode
    global geersOnePoint
    def geersOnePoint(goodPoint):
        #This is for the linear model, equation 15 in Geers
        centralNodePosition       = fieldCoordsFlatGood[goodPoint]
        centralNodeDisplacement   = displacementFieldFlatGood[goodPoint]
        sX0X0 = numpy.zeros((3, 3))
        sX0Xt = numpy.zeros((3, 3))
        m0    = numpy.zeros((3))
        mt    = numpy.zeros((3))

        ## Option 2: KDTree on distance
        # KD-tree will always give the current point as zero-distance
        ind = treeCoord.query_ball_point(centralNodePosition, neighbourRadius*max(nodeSpacing))

        # We know that the current point will also be included, so remove it from the index list.
        ind = numpy.array(ind)
        ind = ind[ind != goodPoint]
        nNeighbours = len(ind)
        nodalRelativePositionsRef = numpy.zeros((nNeighbours, 3)) # Delta_X_0 in paper
        nodalRelativePositionsDef = numpy.zeros((nNeighbours, 3)) # Delta_X_t in paper

        for neighbour, i in enumerate(ind):
            # Relative position in reference configuration
            #                                         absolute position of this neighbour node
            #                                                                  minus abs position of central node
            nodalRelativePositionsRef[neighbour, :] = fieldCoordsFlatGood[i] - centralNodePosition

            # Relative position in deformed configuration (i.e., plus displacements)
            #                                         absolute position of this neighbour node
            #                                                                  plus displacement of this neighbour node
            #                                                                                                minus abs position of central node
            #                                                                                                                       minus displacement of central node
            nodalRelativePositionsDef[neighbour, :] = fieldCoordsFlatGood[i] + displacementFieldFlatGood[i] - centralNodePosition - centralNodeDisplacement

            for u in range(3):
                for v in range(3):
                    #sX0X0[u, v] += nodalRelativePositionsRef[neighbour, u] * nodalRelativePositionsRef[neighbour, v]
                    #sX0Xt[u, v] += nodalRelativePositionsRef[neighbour, u] * nodalRelativePositionsDef[neighbour, v]
                    # Proposed solution for #142 for direction of rotation
                    sX0X0[v, u] += nodalRelativePositionsRef[neighbour, u] * nodalRelativePositionsRef[neighbour, v]
                    sX0Xt[v, u] += nodalRelativePositionsRef[neighbour, u] * nodalRelativePositionsDef[neighbour, v]

            m0 += nodalRelativePositionsRef[neighbour, :]
            mt += nodalRelativePositionsDef[neighbour, :]

        sX0X0 = nNeighbours*sX0X0
        sX0Xt = nNeighbours*sX0Xt

        A = sX0X0 - numpy.dot(m0, m0)
        C = sX0Xt - numpy.dot(m0, mt)
        F = numpy.zeros((3, 3))

        if twoD:
            A = A[1:, 1:]
            C = C[1:, 1:]
            try:
                F[1:, 1:] = numpy.dot(numpy.linalg.inv(A), C)
                F[0, 0] = 1.0
            except numpy.linalg.linalg.LinAlgError:
                #print("spam.deformation.deformationField.FfieldRegularGeers(): LinAlgError: A", A)
                pass
        else:
            try:
                F = numpy.dot(numpy.linalg.inv(A), C)
            except numpy.linalg.linalg.LinAlgError:
                #print("spam.deformation.deformationField.FfieldRegularGeers(): LinAlgError: A", A)
                pass

        return goodPoint, F

    # Iterate through flat field of Fs
    if verbose:
        pbar = progressbar.ProgressBar(maxval=fieldCoordsFlatGood.shape[0]).start()
        finishedPoints = 0

    # Run multiprocessing filling in FfieldFlatGood, which will then update FfieldFlat
    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(geersOnePoint, range(fieldCoordsFlatGood.shape[0])):
            if verbose:
                finishedPoints += 1
                pbar.update(finishedPoints)
            FfieldFlatGood[returns[0]] = returns[1]

    if verbose: pbar.finish()

    FfieldFlat[goodPointsMask] = FfieldFlatGood
    return FfieldFlat.reshape(dims[0], dims[1], dims[2], 3, 3)


def FfieldBagi(points, connectivity, displacements, nProcesses=nProcessesDefault, verbose=True):
    """
    Calculates transformation gradient function using Bagi's 1996 paper, especially equation 3 on page 174.
    Required inputs are connectivity matrix for tetrahedra (for example from spam.mesh.triangulate) and
    nodal positions in reference and deformed configurations.

    Parameters
    ----------
        points : m x 3 numpy array
            M Particles' points in reference configuration

        connectivity : n x 4 numpy array
            Delaunay triangulation connectivity generated by spam.mesh.triangulate for example

        displacements : m x 3 numpy array
            M Particles' displacement

        nProcesses : integer, optional
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : boolean, optional
            Print progress?
            Default = True

    Returns
    -------
        Ffield: nx3x3 array of n cells
            The field of the transformation gradient tensors
    """
    import spam.mesh

    Ffield = numpy.zeros([connectivity.shape[0], 3, 3], dtype='<f4')

    connectivity = connectivity.astype(numpy.uint)

    # define dimension
    D = 3.0

    # Import modules

    # Construct 4-list of 3-lists of combinations constituting a face of the tet
    combs = [[0, 1, 2],
             [1, 2, 3],
             [2, 3, 0],
             [0, 1, 3]]
    unode = [3, 0, 1, 2]

    # Precompute tetrahedron Volumes
    tetVolumes = spam.mesh.tetVolumes(points, connectivity)

    # Initialize arrays for tet strains
    # print("spam.mesh.bagiStrain(): Constructing strain from Delaunay and Displacements")

    # Loop through tetrahdra to get avec1, uPos1
    global computeOneTet
    def computeOneTet(tet):
        # Get the list of IDs, centroids, center of tet
        tetIDs = connectivity[tet, :]
        # 2019-10-07 EA: Skip references to missing particles
        #if max(tetIDs) >= points.shape[0]:
            #print("spam.mesh.unstructured.bagiStrain(): this tet has node > points.shape[0], skipping")
            #pass
        #else:
        if True:
            tetCoords = points[tetIDs, :]
            tetDisp = displacements[tetIDs, :]
            tetCen = numpy.average(tetCoords, axis=0)
            if numpy.isfinite(tetCoords).sum() + numpy.isfinite(tetDisp).sum() != 3*4*2:
                if verbose: print("spam.mesh.unstructured.bagiStrain(): nans in position or displacement, skipping")
                # Compute strains
                F = numpy.zeros((3,3))*numpy.nan
            else:
                # Loop through each face of tet to get avec, upos (Bagi, 1996, pg. 172)
                # aVec1 = numpy.zeros([4, 3], dtype='<f4')
                # uPos1 = numpy.zeros([4, 3], dtype='<f4')
                # uPos2 = numpy.zeros([4, 3], dtype='<f4')
                dudx = numpy.zeros((3, 3), dtype='<f4')

                for face in range(4):
                    faceNorm = numpy.cross(tetCoords[combs[face][0]] - tetCoords[combs[face][1]],
                                           tetCoords[combs[face][0]] - tetCoords[combs[face][2]])

                    # Get a norm vector to face point towards center of tet
                    faceCen = numpy.average(tetCoords[combs[face]], axis=0)
                    tmpnorm = faceNorm / (numpy.linalg.norm(faceNorm))
                    facetocen = tetCen - faceCen
                    if (numpy.dot(facetocen, tmpnorm) < 0):
                        tmpnorm = -tmpnorm

                    # Divide by 6 (1/3 for 1/Dimension; 1/2 for area from cross product)
                    # See first eqn., Bagi, 1996, pg. 172.
                    # aVec1[face] = tmpnorm*numpy.linalg.norm(faceNorm)/6

                    # Undeformed positions
                    # uPos1[face] = tetCoords[unode[face]]
                    # Deformed positions
                    # uPos2[face] = tetComs2[unode[face]]

                    dudx += numpy.tensordot(tetDisp[unode[face]], tmpnorm * numpy.linalg.norm(faceNorm) / 6, axes=0)

                dudx /= float(tetVolumes[tet])

                F = numpy.eye(3) + dudx
            return tet, F

    # Iterate through flat field of Fs
    if verbose:
        pbar = progressbar.ProgressBar(maxval=connectivity.shape[0]).start()
        finishedTets = 0

    # Run multiprocessing
    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(computeOneTet, range(connectivity.shape[0])):
            if verbose:
                finishedTets += 1
                pbar.update(finishedTets)
            Ffield[returns[0]] = returns[1]
        pool.close()
        pool.join()

    if verbose: pbar.finish()

    return Ffield


def decomposeFfield(Ffield, components, twoD=False, nProcesses=nProcessesDefault, verbose=True):
    """
    This function takes in an F field (from either FfieldRegularQ8, FfieldRegularGeers, FfieldBagi) and
    returns fields of desired transformation components.

    Parameters
    ----------
        Ffield : multidimensional x 3 x 3 numpy array of floats
            Spatial field of Fs

        components : list of strings
            These indicate the desired components consistent with spam.deformation.decomposeF or decomposePhi

        twoD : bool, optional
            Is the Ffield in 2D? This changes the strain calculation.
            Default = False

        nProcesses : integer, optional
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : boolean, optional
            Print progress?
            Default = True

    Returns
    -------
        Dictionary containing appropriately reshaped fields of the transformation components requested.

        Keys:
            vol, dev, volss, devss are scalars
            r and z are 3-component vectors
            e and U are 3x3 tensors
    """
    # The last two are for the 3x3 F field
    fieldDimensions  = Ffield.shape[0:-2]
    fieldRavelLength = numpy.prod(numpy.array(fieldDimensions))
    FfieldFlat       = Ffield.reshape(fieldRavelLength, 3, 3)

    output = {}
    for component in components:
        if component == 'vol' or component == 'dev' or component == 'volss' or component == 'devss':
            output[component] = numpy.zeros(fieldRavelLength)
        if component == 'r' or component == 'z':
            output[component] = numpy.zeros((fieldRavelLength, 3))
        if component == 'U' or component == 'e':
            output[component] = numpy.zeros((fieldRavelLength, 3, 3))

    # Function for parallel mode
    global decomposeOneF
    def decomposeOneF(n):
        F = FfieldFlat[n]
        if numpy.isfinite(F).sum() == 9:
            decomposedF = spam.deformation.decomposeF(F, twoD=twoD)
            return n, decomposedF
        else:
            return n, {'r': numpy.array([numpy.nan] * 3),
                      'z': numpy.array([numpy.nan] * 3),
                      'U': numpy.eye(3) * numpy.nan,
                      'e': numpy.eye(3) * numpy.nan,
                      'vol': numpy.nan,
                      'dev': numpy.nan,
                      'volss': numpy.nan,
                      'devss': numpy.nan}

    # Iterate through flat field of Fs
    if verbose:
        pbar = progressbar.ProgressBar(maxval=fieldRavelLength).start()
        finishedPoints = 0

    # Run multiprocessing
    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(decomposeOneF, range(fieldRavelLength)):
            if verbose:
                finishedPoints += 1
                pbar.update(finishedPoints)
            for component in components:
                output[component][returns[0]] = returns[1][component]
        pool.close()
        pool.join()

    if verbose: pbar.finish()

    # Reshape on the output
    for component in components:
        if component == 'vol' or component == 'dev' or component == 'volss' or component == 'devss':
            output[component] = numpy.array(output[component]).reshape(fieldDimensions)

        if component == 'r' or component == 'z':
            output[component] = numpy.array(output[component]).reshape(Ffield.shape[0:-1])

        if component == 'U' or component == 'e':
            output[component] = numpy.array(output[component]).reshape(Ffield.shape)

    return output


def decomposePhiField(PhiField, components, twoD=False, nProcesses=nProcessesDefault, verbose=True):
    """
    This function takes in a Phi field (from readCorrelationTSV?) and
    returns fields of desired transformation components.

    Parameters
    ----------
        PhiField : multidimensional x 4 x 4 numpy array of floats
            Spatial field of Phis

        components : list of strings
            These indicate the desired components consistent with spam.deformation.decomposePhi

        twoD : bool, optional
            Is the PhiField in 2D? This changes the strain calculation.
            Default = False

        nProcesses : integer, optional
            Number of processes for multiprocessing
            Default = number of CPUs in the system

        verbose : boolean, optional
            Print progress?
            Default = True

    Returns
    -------
        Dictionary containing appropriately reshaped fields of the transformation components requested.

        Keys:
            vol, dev, volss, devss are scalars
            t, r, and z are 3-component vectors
            e and U are 3x3 tensors
    """
    # The last two are for the 4x4 Phi field
    fieldDimensions  = PhiField.shape[0:-2]
    fieldRavelLength = numpy.prod(numpy.array(fieldDimensions))
    PhiFieldFlat     = PhiField.reshape(fieldRavelLength, 4, 4)

    output = {}
    for component in components:
        if component == 'vol' or component == 'dev' or component == 'volss' or component == 'devss':
            output[component] = numpy.zeros(fieldRavelLength)
        if component == 't' or component == 'r' or component == 'z':
            output[component] = numpy.zeros((fieldRavelLength, 3))
        if component == 'U' or component == 'e':
            output[component] = numpy.zeros((fieldRavelLength, 3, 3))

    # Function for parallel mode
    global decomposeOnePhi
    def decomposeOnePhi(n):
        Phi = PhiFieldFlat[n]
        if numpy.isfinite(Phi).sum() == 16:
            decomposedPhi = spam.deformation.decomposePhi(Phi, twoD=twoD)
            return n, decomposedPhi
        else:
            return n, {'t': numpy.array([numpy.nan] * 3),
                       'r': numpy.array([numpy.nan] * 3),
                       'z': numpy.array([numpy.nan] * 3),
                       'U': numpy.eye(3) * numpy.nan,
                       'e': numpy.eye(3) * numpy.nan,
                       'vol': numpy.nan,
                       'dev': numpy.nan,
                       'volss': numpy.nan,
                       'devss': numpy.nan}

    # Iterate through flat field of Fs
    if verbose:
        pbar = progressbar.ProgressBar(maxval=fieldRavelLength).start()
        finishedPoints = 0

    # Run multiprocessing
    with multiprocessing.Pool(processes=nProcesses) as pool:
        for returns in pool.imap_unordered(decomposeOnePhi, range(fieldRavelLength)):
            if verbose:
                finishedPoints += 1
                pbar.update(finishedPoints)
            for component in components:
                output[component][returns[0]] = returns[1][component]
        pool.close()
        pool.join()

    if verbose: pbar.finish()

    # Reshape on the output
    for component in components:
        if component == 'vol' or component == 'dev' or component == 'volss' or component == 'devss':
            output[component] = numpy.array(output[component]).reshape(*PhiField.shape[0:-2])

        if component == 't' or component == 'r' or component == 'z':
            output[component] = numpy.array(output[component]).reshape(*PhiField.shape[0:-2], 3)

        if component == 'U' or component == 'e':
            output[component] = numpy.array(output[component]).reshape(*PhiField.shape[0:-2], 3, 3)

    return output


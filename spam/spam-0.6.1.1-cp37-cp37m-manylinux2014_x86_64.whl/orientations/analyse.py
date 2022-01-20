import numpy, math
import numpy.matlib
import scipy, scipy.special
from scipy.stats import chi2
from scipy.linalg import null_space

def fitVonMisesFisher(orientations, confVMF=None, confMu=None, confKappa=None):
    """
    This function fits a vonMises-Fisher distribution to a set of N 3D unit vectors.
    The distribution is characterised by a mean orientation mu and a spread parameter kappa.

    Parameters
    -----------
        orientations : Nx3 array of floats
            Z, Y and X components of each vector.

        confVMF : float
            Confidence interval for the test on the vMF distribution
            Used for checking wheter the data can be modeled with a vMF distribution
            Default = 95%

        confMu : float
            Confidence interval for the test on the mean orientation mu
            Used for computing the error on the mean orientation
            Default = 95%

        confKappa : float
            Confidence interval for the test on kappa
            Used for computing the error on kappa
            Default = 95%

    Returns
    --------
        Dictionary containing:

            Keys:
                orientations : Nx3 array of floats
                    Z, Y and X components of each vector that is located in the same quadrant as the mean orientation

                mu : 1x3 array of floats
                    Z, Y and X components of mean orientation.

                theta : float
                    Inclination angle of the mean orientation in degrees - angle with the Z axis

                alpha : float
                    Azimuth angle of the mean orientation in degrees - angle in the X-Y plane

                R : float
                    Mean resultant length
                    First order measure of concentration (ranging between 0 and 1)

                kappa : int
                    Spread of the distribution, must be > 0.
                    Higher values of kappa mean a higher concentration along the main orientation 

                vectorsProj : Nx3 array of floats
                    Z, Y and X components of each vector projected along the mean orientation

                fisherTest : bool
                    Boolean representing the result of the test on the vMF distribution
                    1 = The data can be modeled with a vMF distribution
                    0 = The data cannot be modeled with a vMF distribution

                fisherTestVal : float
                    Value to be compared against the critical value, taken from a Chi-squared distrition

                muTest : float
                    Error associated to the mean orientation
                    Defined as the semi-vertical angle of the cone that comprises the distribution

                kappaTest : 1x2 list of floats
                    Maximum and minimum value of kappa, given the confidence interval

    Notes
    -----

        The calculation of kappa implemented from Tanabe, A., et al., (2007). Parameter estimation for von Mises_Fisher distributions. doi: 10.1007/s00180-007-0030-7

    """

    # Check that the vectors are 3D
    assert orientations.shape[1] == 3, '\n spam.orientations.fitVonMisesFisher: The vectors must be an array of Nx3'

    # If needed, assign confidence intervals
    if confVMF is None:
        confVMF = 0.95 
    if confMu is None:
        confMu = 0.95 
    if confKappa is None:
        confKappa = 0.95
    # Check the values of the confidence intervals
    assert confVMF > 0 and confVMF < 1, '\n spam.orientations.fitVonMisesFisher: The confidence interval for confVMF should be between 0 and 1'
    assert confMu > 0 and confMu < 1, '\n spam.orientations.fitVonMisesFisher: The confidence interval for confMu should be between 0 and 1'
    assert confKappa > 0 and confKappa < 1, '\n spam.orientations.fitVonMisesFisher: The confidence interval for confKappa should be between 0 and 1'

    # Create result dictionary
    res = {}
    # Remove possible vectors [0, 0, 0]
    orientations = orientations[numpy.where(numpy.sum(orientations, axis = 1) != 0)[0]]
    # Normalize all the vectors from http://stackoverflow.com/questions/2850743/numpy-how-to-quickly-normalize-many-vectors
    norms = numpy.apply_along_axis( numpy.linalg.norm, 1, orientations )
    orientations = orientations / norms.reshape( -1, 1 )
    # Read Number of Points
    numberOfPoints = orientations.shape[0]
    # 1. Get raw-orientation with SVD and flip accordingly
    vectSVD = meanOrientation(orientations)
    # Flip accordingly to main direction
    for i in range(numberOfPoints):
        vect = orientations[i, :]
        # Compute angle between both vectors
        delta1 = numpy.degrees(numpy.arccos( (numpy.dot(vectSVD, vect)) / ( numpy.linalg.norm(vectSVD)* numpy.linalg.norm(vect))))
        delta2 = numpy.degrees(numpy.arccos( (numpy.dot(vectSVD, -1*vect)) / ( numpy.linalg.norm(vectSVD)* numpy.linalg.norm(-1*vect))))
        if delta1 < delta2:
            orientations[i, :] = vect
        else:
            orientations[i, :] = -1*vect
    res.update({'orientations':orientations})
    # 2. Compute parameters of vMF
    # Compute mean orientation
    mu = numpy.sum(orientations, axis = 0) / numpy.linalg.norm(numpy.sum(orientations, axis = 0))
    res.update({'mu':mu})
    # Decompose mean orientation into polar coordinates
    thetaR = numpy.arccos(mu[0])
    alphaR = numpy.arctan2(mu[1],mu[2])
    if alphaR < 0: alphaR = alphaR + 2*numpy.pi
    res.update({'theta':numpy.degrees(thetaR)})
    res.update({'alpha':numpy.degrees(alphaR)})
    # Compute mean resultant length
    R = numpy.linalg.norm(numpy.sum(orientations, axis = 0)) / numberOfPoints
    res.update({'R':R})
    # Compute rotation matrix - needed for projecting all vector around mu
    #   Taken from pg 194 from MardiaJupp - Fisher book eq. 3.9 is wrong!
    rotMatrix = numpy.array([[numpy.cos(thetaR)  , numpy.sin(thetaR)*numpy.sin(alphaR), numpy.sin(thetaR)*numpy.cos(alphaR) ],
                            [0                   , numpy.cos(alphaR)                  , -1*numpy.sin(alphaR)                ],
                            [-1*numpy.sin(thetaR), numpy.cos(thetaR)*numpy.sin(alphaR), numpy.cos(thetaR)*numpy.cos(alphaR) ]])
    # Project vectors - needed for computing kappa
    orientationsProj = numpy.zeros((numberOfPoints,3))
    for i in range(numberOfPoints):
        orientationsProj[i, :] = rotMatrix.dot(orientations[i,:])
        if orientationsProj[i, 0] < 0: orientationsProj[i, :] = -1*orientationsProj[i, :]  
    res.update({'vectorsProj':orientationsProj})
    # Compute Kappa
    Z_bar = numpy.sum(orientationsProj[:,0]) / len(orientationsProj)
    Y_bar = numpy.sum(orientationsProj[:,1]) / len(orientationsProj)
    X_bar = numpy.sum(orientationsProj[:,2]) / len(orientationsProj)
    R = numpy.sqrt(Z_bar**2 + Y_bar**2 + X_bar**2)
    # First Kappa guess
    k_t = R*(3-1)/(1-R**2)
    error_i = 5
    # Main Iteration
    while error_i > 0.001: #t is step i, T is step i+1
        I_1 = scipy.special.iv(3/2-1,k_t)
        I_2 = scipy.special.iv(3/2,k_t)
        k_T = R*k_t*(I_1 / I_2)
        error_i = 100*(numpy.abs(k_T - k_t) / k_t)
        k_t = k_T.copy()
    # Add results
    res.update({'kappa':k_t})
    # 3. Tests
    # Test for vMF distribution - Can we really model the data with a vMF distribution?
    valCritic = scipy.stats.chi2.ppf(1-confVMF, 3) 
    test = 3*(R**2) / numberOfPoints
    if test < valCritic: 
        fisherFit = True 
    else:
        fisherFit = False 
    res.update({'fisherTest':fisherFit})
    res.update({'fisherTestVal':test})
    # Test the location of mu - compute the semi-vertical angle of the cone
    d = 0
    for vect in orientations:
        d += (numpy.sum(vect*mu))**2
    d = 1 - (1/numberOfPoints)*d
    sigma = numpy.sqrt(d / (numberOfPoints*R**2))
    angle = numpy.degrees(numpy.arcsin(numpy.sqrt(-1*numpy.log(1-confMu))*sigma))
    res.update({'muTest':angle})
    # Test the value of Kappa - compute interval for Kappa - eq. 5.37 Fisher
    kappaDown =  0.5*chi2.ppf(0.5*(1-confKappa), 2*numberOfPoints - 2)/(numberOfPoints - numberOfPoints*R)
    kappaUp =  0.5*chi2.ppf(1-0.5*(1-confKappa), 2*numberOfPoints - 2)/(numberOfPoints - numberOfPoints*R)
    res.update({'kappaTest':[kappaDown, kappaUp]})
    return res


def meanOrientation(orientations):
    """
    This function performs a Singular Value Decomposition (SVD) on a series of 3D unit vectors to find the main direction of the set

    Parameters
    -----------
        orientations : Nx3 numpy array of floats
                        Z, Y and X components of direction vectors.
                        Non-unit vectors are normalised.

    Returns
    --------
        orientationVector : 1x3 numpy arrayRI*numpy.cos(thetaI) of floats
                        Z, Y and X components of direction vector.

    Notes
    -----
        Implementation taken from https://www.ltu.se/cms_fs/1.51590!/svd-fitting.pdf

    """

    # Read Number of Points
    numberOfPoints = orientations.shape[0]
    # Remove possible vectors [0, 0, 0]
    orientations = orientations[numpy.where(numpy.sum(orientations, axis = 1) != 0)[0]]
    # Normalise all the vectors from http://stackoverflow.com/questions/2850743/numpy-how-to-quickly-normalize-many-vectors
    norms = numpy.apply_along_axis( numpy.linalg.norm, 1, orientations )
    orientations = orientations / norms.reshape( -1, 1 )
    # Include the negative part
    orientationsSVD = numpy.concatenate((orientations, -1*orientations), axis=0)
    # Compute the centre
    meanVal = numpy.mean(orientationsSVD, axis=0)
    # Center array
    orientationsCenteredSVD  = orientationsSVD - meanVal
    # Run SVD
    svd =  numpy.linalg.svd(orientationsCenteredSVD.T, full_matrices=False)
    # Principal direction
    orientationVector = svd[0][:,0]
    # Flip (if needed) to have a positive Z value
    if orientationVector[0] < 0: orientationVector = -1*orientationVector
    return orientationVector

def fabricTensor(orientations):
    """
    Calculation of a second order fabric tensor from 3D unit vectors representing orientations

    Parameters
    ----------
        orientations: Nx3 array of floats
            Z, Y and X components of direction vectors
            Non-unit vectors are normalised.

    Returns
    -------
        N: 3x3 array of floats
            normalised second order fabric tensor
            with N[0,0] corresponding to z-z, N[1,1] to y-y and N[2,2] x-x

        F: 3x3 array of floats
            fabric tensor of the third kind (deviatoric part)
            with F[0,0] corresponding to z-z, F[1,1] to y-y and F[2,2] x-x

        a: float
            scalar anisotropy factor based on the deviatoric part F

    Note
    ----
        see [Kanatani, 1984] for more information on the fabric tensor
        and [Gu et al, 2017] for the scalar anisotropy factor

        Function contibuted by Max Wiebicke (Dresden University)
    """
    # from http://stackoverflow.com/questions/2850743/numpy-how-to-quickly-normalize-many-vectors
    norms = numpy.apply_along_axis(numpy.linalg.norm, 1, orientations)
    orientations = orientations / norms.reshape(-1, 1)
    # create an empty array
    N = numpy.zeros((3, 3))
    size = len(orientations)
    for i in range(size):
        orientation = orientations[i]
        tensProd = numpy.outer(orientation, orientation)
        N[:, :] = N[:, :] + tensProd
    # fabric tensor of the first kind
    N = N / size
    # fabric tensor of third kind
    F = (N - (numpy.trace(N) * (1. / 3.)) * numpy.eye(3, 3)) * (15. / 2.)
    # scalar anisotropy factor
    a = math.sqrt(3. / 2. * numpy.tensordot(F, F, axes=2))

    return N, F, a

def projectOrientation(vector, coordSystem, projectionSystem):
    """
    This functions projects a 3D vector from a given coordinate system into a 2D plane given by a defined projection.

    Parameters
    ----------
        vector: 1x3 array of floats
            Vector to be projected
            For cartesian system: ZYX
            For spherical system: r, tetha (inclination), phi (azimuth) in Radians

        coordSystem: string
            Coordinate system of the vector
            Either "cartesian" or "spherical"

        projectionSystem : string
            Projection to be used
            Either "lambert", "stereo" or "equidistant"

    Returns
    -------
        projection_xy: 1x2 array of floats
            X and Y coordinates of the projected vector

        projection_theta_r: 1x2 array of floats
            Theta and R coordinates of the projected vector in radians

    """

    projection_xy_local      = numpy.zeros( (2) )
    projection_theta_r_local = numpy.zeros( (2) )

    # Reshape the vector and check for errors in shape
    try:
        vector = numpy.reshape(vector, (3,1))
    except:
        print('\n spam.orientations.projectOrientation: The vector must be an array of 1x3')
        return

    if coordSystem == "spherical":
        # unpack vector 

        r, theta, phi = vector

        x = r * math.sin( theta ) * math.cos( phi )
        y = r * math.sin( theta ) * math.sin( phi )
        z = r * math.cos( theta )

    elif coordSystem == "cartesian":

        # unpack vector 
        z, y, x = vector
        # we're in cartesian coordinates, (x-y-z mode) Calculate spherical coordinates
        # passing to 3d spherical coordinates too...
        # From: https://en.wikipedia.org/wiki/Spherical_coordinate_system
        #  Several different conventions exist for representing the three coordinates, and for the order in which they should be written.
        #  The use of (r, θ, φ) to denote radial distance, inclination (or elevation), and azimuth, respectively, is common practice in physics, and is specified by ISO standard 80000-2 :2009, and earlier in ISO 31-11 (1992).
        r     = numpy.sqrt( x**2 + y**2 + z**2 )
        theta = math.acos( z / r )   # inclination
        phi   = math.atan2( y, x )   # azimuth

    else:
        print('\n spam.orientations.projectOrientation: Wrong coordinate system')
        return

    if projectionSystem == "lambert":          # dividing by sqrt(2) so that we're projecting onto a unit circle
        projection_xy_local[0] = x*(math.sqrt(2/(1+z)))
        projection_xy_local[1] = y*(math.sqrt(2/(1+z)))

        # sperhical coordinates -- CAREFUL as per this wikipedia page: https://en.wikipedia.org/wiki/Lambert_azimuthal_equal-area_projection
        #   the symbols for inclination and azimuth ARE INVERTED WITH RESPEST TO THE SPHERICAL COORDS!!!
        projection_theta_r_local[0] = phi 
        #                                                  HACK: doing math.pi - angle in order for the +z to be projected to 0,0
        projection_theta_r_local[1] = 2 * math.cos( ( math.pi - theta ) / 2 )

        # cylindrical coordinates
        #projection_theta_r_local[0] = phi
        #projection_theta_r_local[1] = math.sqrt( 2.0 * ( 1 + z ) )

    elif projectionSystem == "stereo":
        projection_xy_local[0] = x / ( 1 - z )
        projection_xy_local[1] = y / ( 1 - z )

        # https://en.wikipedia.org/wiki/Stereographic_projection uses a different standard from the page on spherical coord Spherical_coordinate_system
        projection_theta_r_local[0] = phi
        #                                        HACK: doing math.pi - angle in order for the +z to be projected to 0,0
        #                                                                             HACK: doing math.pi - angle in order for the +z to be projected to 0,0
        projection_theta_r_local[1] = numpy.sin( math.pi - theta ) / ( 1 - numpy.cos( math.pi - theta ) )

    elif projectionSystem == "equidistant":
        # https://en.wikipedia.org/wiki/Azimuthal_equidistant_projection
        # TODO: To be checked, but this looks like it should -- a straight down projection.
        projection_xy_local[0] = math.sin( phi )
        projection_xy_local[1] = math.cos( phi )

        projection_theta_r_local[0] = phi
        projection_theta_r_local[1] = numpy.cos( theta - math.pi/2 )

    else:
        print('\n spam.orientations.projectOrientation: Wrong projection system')
        return

    return projection_xy_local, projection_theta_r_local


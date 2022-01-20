import numpy, math
import numpy.matlib
import scipy, scipy.special
from scipy.stats import chi2
from scipy.linalg import null_space

def generateIsotropic(N):
    """
    There is no analytical solution for putting equally-spaced points on a unit sphere.
    This Saff and Kuijlaars spiral algorithm gets close.

    Parameters
    ----------
        N : integer
            Number of points to generate

    Returns
    -------
        orientations : Nx3 numpy array
            Z,Y,X unit vectors of orientations for each point on sphere

    Note
    ----------
        For references, see:
        http://www.cgafaq.info/wiki/Evenly_distributed_points_on_sphere

        Which in turn was based on:
        http://sitemason.vanderbilt.edu/page/hmbADS

        From:
        Rakhmanov, Saff and Zhou: **Minimal Discrete Energy on the Sphere**, Mathematical Research Letters, Vol. 1 (1994), pp. 647-662:
        https://www.math.vanderbilt.edu/~esaff/texts/155.pdf

        Also see discussion here:
        http://groups.google.com/group/sci.math/browse_thread/thread/983105fb1ced42c/e803d9e3e9ba3d23#e803d9e3e9ba3d23%22%22
    """

    # Check that it is an integer
    assert isinstance(N,int), '\n spam.orientations.generateIsotropic: Number of vectors should be an integer'
    # Check value of number of vectors
    assert N > 0, '\n spam.orientations.generateIsotropic: Number of vectors should be > 0'

    M = int(N)*2

    s         = 3.6 / math.sqrt(M)

    delta_z   = 2 / float(M)
    z         = 1 - delta_z/2

    longitude = 0

    points = numpy.zeros( (N,3) )

    for k in range( N ):
        r           = math.sqrt( 1 - z*z )
        points[k,2] = math.cos( longitude ) * r
        points[k,1] = math.sin( longitude ) * r 
        points[k,0] = z
        z           = z - delta_z
        longitude   = longitude + s/r
    return points


def generateIcosphere(subDiv):
    """
    This function creates an unit icosphere (convex polyhedron made from triangles) starting from an icosahedron (polyhedron with 20 faces) and then making subdivision on each triangle. 
    The number of faces is  20*(4**subDiv).

    Parameters
    ----------
        subDiv : integer
            Number of times that the initial icosahedron is divided. 
            Suggested value: 3

    Returns
    -------
        icoVerts: numberOfVerticesx3 numpy array
            Coordinates of the vertices of the icosphere

        icoFaces: numberOfFacesx3 numpy array
            Indeces of the vertices that compose each face

        icoVectors: numberOfFacesx3
            Vectors normal to each face

    Note
    ----------
        From: https://sinestesia.co/blog/tutorials/python-icospheres/
    """
    # Chech that it is an integer
    assert isinstance(subDiv,int), '\n spam.orientations.generateIcosphere: Number of subDiv should be an integer'
    assert subDiv > 0, print('\n spam.orientations.generateIcosphere: Number of subDiv should be > 0')

    # 1. Internal functions

    middle_point_cache = {}

    def vertex(x, y, z):
        """ Return vertex coordinates fixed to the unit sphere """

        length = numpy.sqrt(x**2 + y**2 + z**2)

        return [i / length for i in (x,y,z)]

    def middle_point(point_1, point_2):
        """ Find a middle point and project to the unit sphere """

        # We check if we have already cut this edge first
        # to avoid duplicated verts
        smaller_index = min(point_1, point_2)
        greater_index = max(point_1, point_2)

        key = '{0}-{1}'.format(smaller_index, greater_index)

        if key in middle_point_cache:
            return middle_point_cache[key]
        # If it's not in cache, then we can cut it
        vert_1 = icoVerts[point_1]
        vert_2 = icoVerts[point_2]
        middle = [sum(i)/2 for i in zip(vert_1, vert_2)]
        icoVerts.append(vertex(middle[0], middle[1], middle[2]))
        index = len(icoVerts) - 1
        middle_point_cache[key] = index
        return index

    # 2. Create the initial icosahedron 
    # Golden ratio
    PHI = (1 + numpy.sqrt(5)) / 2
    icoVerts = [
            vertex(-1,  PHI, 0),
            vertex( 1,  PHI, 0),
            vertex(-1, -PHI, 0),
            vertex( 1, -PHI, 0),
            vertex(0, -1, PHI),
            vertex(0,  1, PHI),
            vertex(0, -1, -PHI),
            vertex(0,  1, -PHI),
            vertex( PHI, 0, -1),
            vertex( PHI, 0,  1),
            vertex(-PHI, 0, -1),
            vertex(-PHI, 0,  1),
            ]

    icoFaces = [
            # 5 faces around point 0
            [0, 11, 5],
            [0, 5, 1],
            [0, 1, 7],
            [0, 7, 10],
            [0, 10, 11],
            # Adjacent faces
            [1, 5, 9],
            [5, 11, 4],
            [11, 10, 2],
            [10, 7, 6],
            [7, 1, 8],
            # 5 faces around 3
            [3, 9, 4],
            [3, 4, 2],
            [3, 2, 6],
            [3, 6, 8],
            [3, 8, 9],
            # Adjacent faces
            [4, 9, 5],
            [2, 4, 11],
            [6, 2, 10],
            [8, 6, 7],
            [9, 8, 1],
            ]

    # 3. Work on the subdivisions
    for i in range(subDiv):
        faces_subDiv = []
        for tri in icoFaces:
            v1 = middle_point(tri[0], tri[1])
            v2 = middle_point(tri[1], tri[2])
            v3 = middle_point(tri[2], tri[0])
            faces_subDiv.append([tri[0], v1, v3])
            faces_subDiv.append([tri[1], v2, v1])
            faces_subDiv.append([tri[2], v3, v2])
            faces_subDiv.append([v1, v2, v3])
        icoFaces = faces_subDiv

    # 4. Compute the normal vector to each face
    icoVectors = []
    for tri in icoFaces:
        # Get the points
        P1 = numpy.array(icoVerts[tri[0]])
        P2 = numpy.array(icoVerts[tri[1]])
        P3 = numpy.array(icoVerts[tri[2]])
        # Create two vector
        v1 = P2 - P1
        v2 = P2 - P3
        v3 = numpy.cross(v1,v2)
        norm = vertex(*v3)
        icoVectors.append(norm)

    return icoVerts, icoFaces, icoVectors


def generateVonMisesFisher(mu, kappa, N=1):
    """
    This function generates a set of N 3D unit vectors following a vonMises-Fisher distribution, centered at a mean orientation mu and with a spread K.

    Parameters
    -----------
        mu : 1x3 array of floats
            Z, Y and X components of mean orientation.
            Non-unit vectors are normalised.

        kappa : int
            Spread of the distribution, must be > 0.
            Higher values of kappa mean a higher concentration along the main orientation

        N : int
            Number of vectors to generate

    Returns
    --------
        orientations : Nx3 array of floats
            Z, Y and X components of each vector.

    Notes
    -----
        Sampling method taken from https://github.com/dlwhittenbury/von-Mises-Fisher-Sampling

    """

    def randUniformCircle(N):
        # N number of orientations
        v = numpy.random.normal(0,1,(N,2))
        v = numpy.divide(v,numpy.linalg.norm(v,axis=1,keepdims=True))
        return v

    def randTmarginal(kappa, N=1):
        # Start of algorithm 
        b = 2 / (2.0 * kappa + numpy.sqrt(4.0 * kappa**2 + 2**2 ))
        x0 = (1.0 - b) / (1.0 + b)
        c = kappa * x0 + 2 * numpy.log(1.0 - x0**2)
        orientations = numpy.zeros((N,1))
        # Loop over number of orientations 
        for i in range(N):
            # Continue unil you have an acceptable sample 
            while True: 
                # Sample Beta distribution
                Z = numpy.random.beta( 1, 1 )
                # Sample Uniform distributionNR
                U = numpy.random.uniform(low=0.0,high=1.0)
                # W is essentially t
                W = (1.0 - (1.0 + b) * Z) / (1.0 - (1.0 - b) * Z)
                # Check whether to accept or reject 
                if kappa * W + 2*numpy.log(1.0 - x0*W) - c >= numpy.log(U):
                    # Accept sample
                    orientations[i] = W
                    break
        return orientations

    # Check for non-scalar value of kappa
    assert numpy.isscalar(kappa), '\n spam.orientations.generateVonMisesFisher: kappa should a scalar'
    assert kappa > 0, '\n spam.orientations.generateVonMisesFisher: kappa should be > 0'
    assert N > 1, '\n spam.orientations.generateVonMisesFisher: The number of vectors should be > 1'

    try:
        mu = numpy.reshape( mu, (1,3))
    except:
        print('\n spam.orientations.generateVonMisesFisher: The main orientation vector must be an array of 1x3')
        return
    # Normalize mu
    mu = mu/numpy.linalg.norm(mu)
    #  check that N > 0!
    # Array to store orientations 
    orientations = numpy.zeros((N,3))
    #  Component in the direction of mu (Nx1)
    t = randTmarginal(kappa,N) 
    # Component orthogonal to mu (Nx(p-1))
    xi = randUniformCircle(N) 
    # Component in the direction of mu (Nx1).
    orientations[:,[0]] = t 
    # Component orthogonal to mu (Nx(p-1))
    orientations[:,1:] = numpy.matlib.repmat(numpy.sqrt(1 - t**2), 1, 2) * xi
    # Rotation of orientations to desired mu
    O = scipy.linalg.null_space(mu)
    R = numpy.concatenate((mu.T,O),axis=1)
    orientations = numpy.dot(R,orientations.T).T

    return orientations

"""
Library of SPAM functions for generating 3D spheroids
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

def makeBlurryNoisySpheroid(dims, centres, axisLengthsAC, orientations, blur=0, noise=0, flatten=True, background=0.25, foreground=0.75):
    """
    This function creates a sheroid or series of spheroids in a 3D volume, adding noise and blur if requested.
    Note that this does not handle the partial volume effect like kalisphera, and so some blur or downscaling is recommended!

    The base code is from https://sbrisard.github.io/posts/20150930-orientation_correlations_among_rice_grains-06.html

    Parameters
    ----------
        dims : 3-component list
            Dimensions of volume to create

        centre : 1D or 2D numpy array
            Either a 3-component vector, or an Nx3 array of centres to draw with respect to 0,0,0 in `vol`

        axisLengthsAC : 1D or 2D numpy array of floats
            Half-axis lengths for each spheroid. If c>a, a prolate (rice-like) is generated; while a>c yields an oblate (lentil-like).
            This is either a 2-component array for 1 particle, or a Nx2 array of values.

        orientations : 1D or 2D numpy array of floats
            Orientation vectors of the axis of rotational symmetry for the spheroid.
            This is either a 3-component ZYX array for 1 particle, or a Nx3 array of values.

        blur : float, optional
            Standard deviation of the blur kernel (in ~pixels)
            Default = 0

        noise : float, optional
            Standard devitaion of the noise (in greylevels), reminder background=0 and sphere=1
            Default = 0

        flatten : bool, optional
            Flatten greyvalues >1 to 1 (caused by overlaps)?
            Default = True

        background : float, optional
            Desired mean greyvalue of the background
            Default = 0.25

        foreground : float, optional
            Desired mean greyvalue of the background
            Default = 0.75

    Returns
    -------
        vol : the input array
    """
    # 3D
    D = 3

    vol = numpy.zeros(dims, dtype='<f4')

    centres = numpy.array(centres)
    axisLengthsAC = numpy.array(axisLengthsAC)
    orientations = numpy.array(orientations)
    dims = numpy.array(dims)

    if len(centres.shape) == 1:
        nParticles = 1

        # There is just one spheroid
        centres = numpy.array([centres])

        assert len(axisLengthsAC.shape) == 1
        assert axisLengthsAC.shape[0] == 2
        axisLengthsAC = numpy.array([axisLengthsAC])

        assert len(orientations.shape) == 1
        assert orientations.shape[0]   == 3
        assert numpy.isclose(numpy.linalg.norm(orientations), 1)
        orientations = numpy.array([orientations])

    elif len(centres.shape) == 2:
        nParticles = centres.shape[0] 

        # more than one spheroid
        assert len(axisLengthsAC.shape) == 2
        assert axisLengthsAC.shape[0] == nParticles 
        assert axisLengthsAC.shape[1] == 2

        assert len(orientations.shape) == 2
        assert orientations.shape[0]   == nParticles
        assert orientations.shape[1]   == 3

    def spheroidDistanceFunction(x, invQ):
        """
        Ordering of points: ``x[i, ...]`` is the i-th coordinate
        """
        y = numpy.tensordot(invQ, x, axes=([-1], [0]))
        numpy.multiply(x, y, y)
        return numpy.sum(y, axis=0)

    # pool?
    for centre, axisLengthAC, orientation in zip(centres, axisLengthsAC, orientations):
        # Preamble
        p    = numpy.outer(orientation, orientation)
        q    = numpy.eye(D, dtype=numpy.float64) - p
        Q    = axisLengthAC[1]**2*p+axisLengthAC[0]**2*q
        invQ = p/axisLengthAC[1]**2+q/axisLengthAC[0]**2

        # Must implement local bounding box calculation here...
        bb = numpy.sqrt(numpy.diag(Q))


        h = 1
        #bb = dims
        i_max = numpy.ceil(bb/h-0.5)
        bb = i_max*h
        shape = 2*i_max+1

        slices = [slice(-x, x, i*1j) for (x, i) in zip(bb, shape)]
        x = numpy.mgrid[slices]

        # Thresholding distance function!!
        spheroidLocal = spheroidDistanceFunction(x, invQ) < 1

        spheroidLocalShape = numpy.array(spheroidLocal.shape).astype(int)
        spheroidLocalHalfWindow = (spheroidLocalShape - 1) / 2 
        #GP 2021-06-23: Round to the closest int
        centre = numpy.floor(centre)
        spheroidGlobalTop = (centre-spheroidLocalHalfWindow).astype(int)
        spheroidGlobalBot = (centre+spheroidLocalHalfWindow+1).astype(int)

        # How much the local BB is going over the edges of the image
        spheroidOffsetTop = numpy.zeros(3, dtype=int)
        spheroidOffsetBot = numpy.zeros(3, dtype=int)
        if spheroidGlobalTop[0] < 0: spheroidOffsetTop[0] = -spheroidGlobalTop[0]
        if spheroidGlobalTop[1] < 0: spheroidOffsetTop[1] = -spheroidGlobalTop[1]
        if spheroidGlobalTop[2] < 0: spheroidOffsetTop[2] = -spheroidGlobalTop[2]

        if spheroidGlobalBot[0] > dims[0]-1: spheroidOffsetBot[0] = spheroidGlobalBot[0] - dims[0]
        if spheroidGlobalBot[1] > dims[1]-1: spheroidOffsetBot[1] = spheroidGlobalBot[1] - dims[1]
        if spheroidGlobalBot[2] > dims[2]-1: spheroidOffsetBot[2] = spheroidGlobalBot[2] - dims[2]

        sliceGlobal = (slice(spheroidGlobalTop[0]+spheroidOffsetTop[0],spheroidGlobalBot[0]-spheroidOffsetBot[0]),
                       slice(spheroidGlobalTop[1]+spheroidOffsetTop[1],spheroidGlobalBot[1]-spheroidOffsetBot[1]),
                       slice(spheroidGlobalTop[2]+spheroidOffsetTop[2],spheroidGlobalBot[2]-spheroidOffsetBot[2]))
        sliceLocal  = (slice(spheroidOffsetTop[0],spheroidLocalShape[0]-spheroidOffsetBot[0]),
                       slice(spheroidOffsetTop[1],spheroidLocalShape[1]-spheroidOffsetBot[1]),
                       slice(spheroidOffsetTop[2],spheroidLocalShape[2]-spheroidOffsetBot[2]))

        vol[sliceGlobal] += spheroidLocal[sliceLocal]        

    if flatten: vol[vol>1]=1

    if blur != 0:
        import scipy.ndimage
        vol = scipy.ndimage.filters.gaussian_filter(vol, sigma=blur)

    if noise != 0:
        vol += numpy.random.normal(size=dims, scale=noise)

    vol *= float(foreground)-float(background)
    vol += float(background)

    return vol


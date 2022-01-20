"""
Library of SPAM functions for generating partial volume balls, see Tengattini et al. 2015
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

from . import kalispheraToolkit

real_t = '<f8'
# also need to select double or float in kalisphera C call


def makeSphere(vol, centre, radius):
    """
    This function creates a sphere in a given 3D volume,
    with analytically-calculated partial-volume effects.
    Background is assumed to have a greyvalue of zero,
    and a fully-occupied sphere voxel is considered to
    have a greyvalue of 1.

    Greyvalues are added to the volume, so spheres can be
    added to an existing background.

    Parameters
    ----------
        vol : 3D numpy array of doubles
            A 3D image of greylevels (typically zeros) into which sphere(s) should be added

        centre : 1D or 2D numpy array
            Either a 3-component vector, or an Nx3 matrix of sphere centres to draw with respect to 0,0,0 in `vol`

        radius : float or 1D numpy array
            Raduis(ii) of spheres to draw in `vol`


    Returns
    -------
        None : function updates vol
    """

    if len(vol.shape) != 3:
        print("\tkalisphera.makeSphere(), need 3D vol array")
        return -1

    centre = numpy.array(centre, dtype=real_t)

    # Turn centre into a numpy array in case it is passed as a list-of-lists
    if len(centre.shape) == 1:
        centre = numpy.array([centre])

    if len(centre.shape) == 2:
        if type(radius) == float or type(radius) == int:
            # print("\tkalisphera.makeSphere.run(), Got single radius for multiple spheres... fine")
            radius = [radius] * centre.shape[0]

        if len(radius) == centre.shape[0]:
            for centre, radius in zip(centre, radius):
                volTemp = numpy.zeros_like(vol, dtype=real_t)
                # For compatibility with scipy centre of mass
                # centre+=0.5
                # print centre, radius
                # print vol.sum()
                kalispheraToolkit.kalisphera(volTemp, numpy.array(centre).astype(real_t), float(radius))
                # print vol.sum()
                vol += volTemp  # .copy()
            return 0

        else:
            print("\tkalisphera.makeSphere(), Got multiple radii, but different number from number of centres")
            return -1

def makeBlurryNoisySphere(dims, centre, radius, blur=0, noise=0, flatten=True, background=0.25, foreground=0.75):
    """
    This function creates a sphere or series of spheres in a 3D volume,
    with analytically-calculated partial-volume effects.

    This function can flattens overlaps, then adds gaussian blur
    and then gaussian noise to `makeSphere`.

    Parameters
    ----------
        dims : 3-component list
            Dimensions of volume to create

        centre : 1D or 2D numpy array
            Either a 3-component vector, or an Nx3 array of sphere centres to draw with respect to 0,0,0 in `vol`

        radius : float or 1D numpy array
            Radius(ii) of spheres to draw in `vol`

        blur : float, optional
            Standard deviation of the blur kernel (in ~pixels)
            Default = 0

        noise : float, optional
            Standard devitaion of the noise (in greylevels), noise is on the scale: background=0 and sphere=1
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
            Note this is different return behaviour than makeSphere, which doesn't return anything!!
    """
    assert(foreground > background)

    vol = numpy.zeros(dims, dtype=real_t)

    makeSphere(vol, centre, radius)

    if flatten: vol[vol>1]=1

    if blur != 0:
        import scipy.ndimage
        vol = scipy.ndimage.filters.gaussian_filter(vol, sigma=blur)

    if noise != 0:
        vol += numpy.random.normal(size=dims, scale=noise)

    vol *= float(foreground)-float(background)
    vol += float(background)

    return vol

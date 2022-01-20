"""
Library of SPAM functions for dealing with structured meshes
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




This module offers a set of tools in order to manipulate structured meshes.

>>> # import module
>>> import spam.mesh


The strucutred VTK files used to save the data have the form:

.. code-block:: text

    # vtk DataFile Version 2.0
    VTK file from spam: spam.vtk
    ASCII

    DATASET STRUCTURED_POINTS
    DIMENSIONS nx ny nz
    ASPECT_RATIO lx ly lz
    ORIGIN ox oy oz

    POINT_DATA nx x ny x nz

    SCALARS myNodalField1 float
    LOOKUP_TABLE default
        nodalValue_1
        nodalValue_2
        nodalValue_3
        ...

    VECTORS myNodalField2 float
    LOOKUP_TABLE default
        nodalValue_1_X nodalValue_1_Y nodalValue_1_Z
        nodalValue_2_X nodalValue_2_Y nodalValue_2_Z
        nodalValue_3_X nodalValue_3_Y nodalValue_3_Z
        ...

    CELL_DATA (nx-1) x (ny-1) x (nz-1)

    SCALARS myCellField1 float
    LOOKUP_TABLE default
        cellValue_1
        cellValue_2
        cellValue_3
        ...

where nx, ny and nz are the number of nodes in each axis, lx, ly, lz, the mesh length in each axis and ox, oy, oz the spatial postiion of the origin.

"""

import numpy


def createCylindricalMask(shape, radius, voxSize=1.0, centre=None):
    """
    Create a image mask of a cylinder in the z direction.

    Parameters
    ----------
        shape: array, int
            The shape of the array the where the cylinder is saved

        radius: float
            The radius of the cylinder

        voxSize: float (default=1.0)
            The physical size of a voxel

        centre: array of floats of size 2, (default None)
            The center [y,x] of the axis of rotation of the cylinder.
            If None it is taken to be the centre of the array.

    Returns
    -------
        cyl: array, bool
            The cylinder

    """
    import numpy

    cyl = numpy.zeros(shape).astype(bool)

    if centre is None:
        centre = [float(shape[1]) / 2.0, float(shape[2]) / 2.0]

    for iy in range(cyl.shape[1]):
        y = (float(iy) + 0.5) * float(voxSize)
        for ix in range(cyl.shape[2]):
            x = (float(ix) + 0.5) * float(voxSize)
            dist = numpy.sqrt((x - centre[1])**2 + (y - centre[0])**2)
            if dist < radius:
                cyl[:, iy, ix] = True

    return cyl


def structuringElement(radius=1, order=2, margin=0, dim=3):
    """
    This function construct a structural element.

    Parameters
    -----------
        radius : int, default=1
            The `radius` of the structural element

            .. code-block:: text

                radius = 1 gives 3x3x3 arrays
                radius = 2 gives 5x5x5 arrays
                ...
                radius = n gives (2n+1)x(2n+1)x(2n+1) arrays

        order : int, default=2
            Defines the shape of the structuring element by setting the order of the norm
            used to compute the distance between the centre and the border.

            A representation for the slices of a 5x5x5 element (size=2) from the center to on corner (1/8 of the cube)

            .. code-block:: text

                order=numpy.inf: the cube
                1 1 1    1 1 1    1 1 1
                1 1 1    1 1 1    1 1 1
                1 1 1    1 1 1    1 1 1

                order=2: the sphere
                1 0 0    0 0 0    0 0 0
                1 1 0    1 1 0    0 0 0
                1 1 1    1 1 0    1 0 0

                order=1: the diamond
                1 0 0    0 0 0    0 0 0
                1 1 0    1 0 0    0 0 0
                1 1 1    1 1 0    1 0 0

        margin : int, default=0
            Gives a 0 valued margin of size margin.

        dim : int, default=3
            Spatial dimension (2 or 3).

    Returns
    --------
        array
            The structural element
    """
    import numpy

    tb = tuple([2 * radius + 2 * margin + 1 for _ in range(dim)])
    ts = tuple([2 * radius + 1 for _ in range(dim)])
    c = numpy.abs(numpy.indices(ts) - radius)
    d = numpy.zeros(tb)
    s = tuple([slice(margin, margin + 2 * radius + 1) for _ in range(dim)])
    d[s] = numpy.power(numpy.sum(numpy.power(c, order), axis=0), 1.0 / float(order)) <= radius
    return d.astype('<u1')


def createLexicoCoordinates(lengths, nNodes, origin=(0, 0, 0)):
    """
    Create a list of coordinates following the lexicographical order.

    Parameters
    ----------
        lengths : array of floats
            The length of the cuboids in every directions.
        nNodes : array of int
            The number of nodes of the mesh in every directions.
        origin : array of floats
            The coordinates of the origin of the mesh.

    Returns
    -------
        array
            The list of coordinates. ``shape=(nx*ny*nz, 3)``

    """
    import numpy

    x = numpy.linspace(origin[0], lengths[0] + origin[0], nNodes[0])
    y = numpy.linspace(origin[1], lengths[1] + origin[1], nNodes[1])
    z = numpy.linspace(origin[2], lengths[2] + origin[2], nNodes[2])
    cx = numpy.tile(x, (1, nNodes[1] * nNodes[2]))
    cy = numpy.tile(numpy.sort(numpy.tile(y, (1, nNodes[0]))), (1, nNodes[2]))
    cz = numpy.sort(numpy.tile(z, (1, nNodes[0] * nNodes[1])))
    return numpy.transpose([cx[0], cy[0], cz[0]])

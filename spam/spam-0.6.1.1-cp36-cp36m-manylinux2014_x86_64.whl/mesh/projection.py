"""
Library of SPAM functions for projecting morphological field onto tetrahedral meshes
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
from spam.mesh.meshToolkit import crpacking
from spam.mesh.meshToolkit import projmorpho


def packSpheres(totalVolumeFraction, rejectionLength, phases,
                origin=[0, 0, 0], lengths=[1, 1, 1], nCells=[100, 100, 100],
                inside=True, convertToField=True,
                domainType="cube", fieldName=None,
                vtkSpheres=False, vtkField=False):
    """This function packs one or several sets (phase) of spheres of deferent radii
    and create the corresponding distance fields (one per set).

    The packing algorithm is an iterative process based collective rearrangement.

    Parameters
    ----------
        totalVolumeFraction: float
            The total volume fraction of all the phases
        rejectionLength: float
            The minimal distance between two spheres surfaces
        phases: array
            A 2D array containing the phases parameteres.
            A row corresponds to a phase and a column to a parameter:

                * column 0: the minimal ray of the spheres of the phase
                * column 1: the maximal ray of the spheres of the phase
                * column 2: the relative volume fraction of the phase

            Its shape is: number of phases by 3.
        inside: bool, default=True
            Defines whether or not the spheres have to be completly inside the domain or if they can intersect it.
            The centres remain always inside the domain.
        lengths: array, default=[1, 1, 1]
            The size of the domain the spheres are packed into.
            The axis order is `zyx`.
        origin: array, default=[0, 0, 0]
            The origin of the domain.
            The axis order is `zyx`.
        domainType: string, default='cube'
            The domain type the spheres are packed into.
            Options are:

                * ``cube``: which corresponds to a cuboid. ``lengths`` is then the length of the cuboids.
                * ``cylinder``: which corresponds to a cylinder which height is in the `z` axis.

        convertToField: bool, default=True
            Convert the objects into a distance field (needed for projection)
        fieldName: string, default=None
            If not None, the field is saved in a file `fieldName.dat`.
            It's format is:

            .. code-block:: text

                lengthX, lengthY, lengthZ
                originX, originY, originZ
                nCellsX, nCellY, nCellZ
                fieldValue0
                fieldValue1
                fieldValue2
                ...

        nCells: array, default=[100,100,100]
            The number of cells of the structured mesh used to discretise the distance field.
            The axis order is `zyx`.
        vtkSpheres: bool, default=False
            Save vtk files of the spheres for each iterations of the packing algorithm.
        vtkField: bool, default=False
            Save vtk files of the distance field at the end.

    Returns
    -------
        (spheres, fields): (nSpheres x 4 numpy array, nPhases x 3D numpy array)
            **spheres**: array of spheres ``[z, y, x, r, p]``
            **fields**: array of 3D fields (one for each phase)


    Example
    -------
        >>> phases = [ [0.5, 1.5, 0.4],
                       [1.5, 4,   0.6] ]
        Correspond to 2 phases.
        phase 1: with radii from 0.5 to 1.5 corresponding to 40% of the total volume fraction
        phase 2: with radii from 1.5 to 4.0 corresponding to 60% of the total volume fraction
        >>> projection.packSpheres( 0.4, 0.1, phases, lengths=[15.0,50.0,20.0], nCells=[30,100,40] )
        Yields a 40% total volume fraction with rejection length of 0.1
        in a cuboid of size z=15, y=50, x=20
        with a discretisation of the distance field of 30, 100 and 40 cells respectively.

    WARNING
    -------
        This function deals with structured mesh thus ``x`` and ``z`` axis are swapped **in python**.

    """
    # condition inputs for crPacking c++ constructor
    param = [totalVolumeFraction, rejectionLength]
    phases = numpy.array(phases)
    if len(phases.shape) == 1:
        for j in range(3):
            param.append(phases[j])
        param.append(1)
    else:
        for i in range(phases.shape[0]):
            for j in range(3):
                param.append(phases[i][j])
            param.append(i + 1)

    # swith axis
    delta = [_ for _ in reversed(lengths)]
    origi = [_ for _ in reversed(origin)]
    cells = [_ for _ in reversed(nCells)]

    i = 1 if inside else 0

    cr = crpacking(param, delta, origi, cells, i, "default" if fieldName is None else fieldName, "", domainType)
    cr.createSpheres()
    # convert to z, y, x, radius, phase
    spheres = [[z, y, x, r, p] for r, x, y, z, p in numpy.array(cr.packSpheres(do_write_objects_vtk=vtkSpheres))]
    if convertToField:
        fields = [f.reshape((cells[2] + 1, cells[1] + 1, cells[0] + 1)) for f in numpy.array(cr.convertToField())]
        if fieldName is not None:
            cr.writeField()
        if vtkField:
            cr.writeFieldVTK()

    else:
        fields = False

    return spheres, fields


def packSpheresFromList(objects,
                        rejectionLength,
                        origin=[0, 0, 0], lengths=[1, 1, 1], nCells=[100, 100, 100],
                        inside=True, convertToField=True,
                        domainType="cube", fieldName=None,
                        vtkSpheres=False, vtkField=False):
    """This function packs a set of spheres predefine spheres and create the corresponding distance fields (one per set).
    The predefined position are taken as initial condition to the packing algorithm.

    The packing algorithm is an iterative process based collective rearrangement.

    Parameters
    ----------
        objects: nSpheres times 5 float array
            The list of objects. Rows correspond to a sphere and the 5 columns correspond to (z, y, x) position of the centre, radius and phase number.
        rejectionLength: float
            The minimal distance between two spheres surfaces
        inside: bool, default=True
            Defines whether or not the spheres have to be completly inside the domain or if they can intersect it.
            The centres remain always inside the domain.
        lengths: array, default=[1, 1, 1]
            The size of the domain the spheres are packed into.
            The axis order is `zyx`.
        origin: array, default=[0, 0, 0]
            The origin of the domain.
            The axis order is `zyx`.
        domainType: string, default='cube'
            The domain type the spheres are packed into.
            Options are:

                * ``cube``: which corresponds to a cuboid. ``lengths`` is then the length of the cuboids.
                * ``cylinder``: which corresponds to a cylinder which height is in the `z` axis.

        convertToField: bool, default=True
            Convert the objects into a distance field (needed for projection)
        fieldName: string, default=None
            If not None, the field is saved in a file `fieldName.dat`.
            It's format is:

            .. code-block:: text

                lengthX, lengthY, lengthZ
                originX, originY, originZ
                nCellsX, nCellY, nCellZ
                fieldValue0
                fieldValue1
                fieldValue2
                ...

        nCells: array, default=[100,100,100]
            The number of cells of the structured mesh used to discretise the distance field.
            The axis order is `zyx`.
        vtkSpheres: bool, default=False
            Save vtk files of the spheres for each iterations.
        vtkField: bool, default=False
            Save vtk files of the distance field at the end.

    Returns
    -------
        (spheres, fields): (nSpheres x 4 numpy array, nPhases x 3D numpy array)
            **spheres**: array of spheres ``[z, y, x, r, p]``
            **fields**: array of 3D fields (one for each phase)


    WARNING
    -------
        This function deals with structured mesh thus ``x`` and ``z`` axis are swapped **in python**.

    """
    # condition inputs for crPacking c++ constructor
    param = [0.0, rejectionLength, 1.0, 1.0, 1.0, 1.0]

    # swith axis
    delta = [_ for _ in reversed(lengths)]
    origi = [_ for _ in reversed(origin)]
    cells = [_ for _ in reversed(nCells)]

    # deal with objects
    objects = numpy.array(objects)

    if objects.shape[1] == 5:
        # swap axis spheres
        tmp = objects[:, 0].copy()
        objects[:, 0] = objects[:, 2]
        objects[:, 2] = tmp
        # permutation to put radius first (thanks crpacking!)
        radii = objects[:, 3].copy()
        objects[:, 1:4] = objects[:, 0:3]
        objects[:, 0] = radii
    elif objects.shape[1] == 7:
        # swap axis ellipsoids
        tmp = objects[:, 0].copy()
        objects[:, 0] = objects[:, 2]
        objects[:, 2] = tmp
        tmp = objects[:, 3].copy()
        objects[:, 3] = objects[:, 5]
        objects[:, 5] = tmp

    # create phasesValues
    phasesValues = numpy.unique(objects[:, -1]).astype('<u8').tolist()

    i = 1 if inside else 0

    cr = crpacking(param, delta, origi, cells, i, "dummy" if fieldName is None else fieldName, "", domainType)
    cr.setObjects(objects, phasesValues)
    spheres = numpy.array(cr.packSpheres(do_write_objects_vtk=vtkSpheres))
    if convertToField:
        fields = [f.reshape((cells[2] + 1, cells[1] + 1, cells[0] + 1)) for f in numpy.array(cr.convertToField())]
        if fieldName is not None:
            cr.writeField()
        if vtkField:
            cr.writeFieldVTK()
    else:
        fields = False

    return spheres, fields


def distanceFieldFromObjects(objects, origin=[0, 0, 0], lengths=[1, 1, 1], nCells=[100, 100, 100],
                             fieldName=None, vtkField=False):
    """
    This function reads a list of objects and creates the corresponding distance field.

    Parameters
    ----------
        objects: array
            The list of objects. Each line corresponds to an object and each column to a property.
            The objects available are:

                        * spheres, with 4 columns: centreZ, centreY, centreX, radius, phaseValue
                        * ellipsoids, with 6 columns: centreZ, centreY, centreX, radiusZ, radiusY, radiusX, phaseValue

        lengths: array, default=[1, 1, 1]
            The size of the domain the objects are packed into (needed to create the distance field).
            The axis order is `zyx`.

        origin: array, default=[0, 0, 0]
            The origin of the domain (needed to create the distance field).
            The axis order is `zyx`.

        nCells: array, default=[100,100,100]
            The number of cells of the structured mesh used to discretise the distance field.
            The axis order is `zyx`.

        fieldName: string, default=None
            If not None, the field is saved in a file `fieldName.dat`.
            It's format is:

            .. code-block:: text

                lengthX, lengthY, lengthZ
                originX, originY, originZ
                nCellsX, nCellY, nCellZ
                fieldValue0
                fieldValue1
                fieldValue2
                ...

        vtkField: bool, default=False
            Save vtk files of the distance field at the end.

    Returns
    -------
        fields: nPhases x 3D numpy array
            **fields**: array of 3D fields (one for each phase)

    WARNING
    -------
        This function deals with structured mesh thus ``x`` and ``z`` axis are swapped **in python**.
    """
    # swith axis
    delta = [_ for _ in reversed(lengths)]
    origi = [_ for _ in reversed(origin)]
    cells = [_ for _ in reversed(nCells)]

    objects = numpy.array(objects)

    if objects.shape[1] == 5:
        # swap axis spheres
        tmp = objects[:, 0].copy()
        objects[:, 0] = objects[:, 2]
        objects[:, 2] = tmp
        # permutation to put radius first (thanks crpacking!)
        radii = objects[:, 3].copy()
        objects[:, 1:4] = objects[:, 0:3]
        objects[:, 0] = radii
    elif objects.shape[1] == 7:
        # swap axis ellipsoids
        tmp = objects[:, 0].copy()
        objects[:, 0] = objects[:, 2]
        objects[:, 2] = tmp
        tmp = objects[:, 3].copy()
        objects[:, 3] = objects[:, 5]
        objects[:, 5] = tmp

    # create phasesValues
    phasesValues = numpy.unique(objects[:, -1]).astype('<u8').tolist()

    cr = crpacking([], delta, origi, cells, 1, "default" if fieldName is None else fieldName, "", "")
    cr.setObjects(objects, phasesValues)
    fields = [f.reshape((cells[2] + 1, cells[1] + 1, cells[0] + 1)) for f in numpy.array(cr.convertToField())]
    if fieldName is not None:
        cr.writeField()
    if vtkField:
        cr.writeFieldVTK()

    return fields


def projectField(mesh, fields, thresholds=[0.0], nSkip=1, writeConnectivity=None, vtkMesh=False):
    """
    This function project a set distance fields onto an unstructured mesh.

    Each distance fields corresponds to a phase and the interface between
    the two phases is set by the thresholds.

    Parameters
    ----------
        mesh: string or dict({'node': n x 3 numy array, 'cells': m x 4 numpy array})
            The mesh is an unstructured 3D mesh of tetrahedra.
            If string: path to the file that contains the unstructured mesh. It currently takes ``gmsh`` format files.
            If dict:

                - mesh['points'] should be an array of the `n` node positions (n x 3)
                - mesh['cells'] should be the connectivity matrix of the `m` elements (m x 4)

        fields: array of string or dictionary
            The fields should be continuous (not binary), like a distance field, for a better projection. They are discretised over a regular mesh (lexicographical order). Each field corresponds to a phase.
            If string: Array of pathes to the fields files.
            If dict: should contain

                - fields["origin"]: coordinates of the origin of the field (3 x 1)
                - fields["lengths"]: lengths of fields domain of definition (3 x 1)
                - fields["nCells"]: number of cells of the field discretisation (3 x 1)
                - fields["values"]: array of the n 3D fields (nFields x 3D numpy array)

        thresholds: array of floats
            The list of thresholds.

        writeConnectivity: string, default=None
            When not None, it writes a text file called `writeConnectivity` the list of node and the list of elements
                    which format is:

                    .. code-block:: text

                        COORdinates ! number of nodes
                        nodeId, 0, x, y, z
                        ...

                        ELEMents ! number of elemens
                        elemId, 0, elemType, n1, n2, n3, n4, subVol, interX, interY, interZ
                        ...

                    where:

                        * ``n1, n2, n3, n4`` is the connectivity
                        * ``subVol`` is the sub volume of the terahedron inside the inclusion
                        * ``interX, interY, interZ`` are to componants of the interface vector
                        * ``elemType`` is the type of element. Their meaning depends on the thresholds and the number of phase. Correspondance can be found in the function output after the key word **MATE** like:

                        .. code-block:: text

                            <projmorpho::set_materials
                            .        field 1
                            .        .       MATE,1: background
                            .        .       MATE,2: phase 1
                            .        .       MATE,3: interface phase 1 with background
                            .        field 2
                            .        .       MATE,1: background
                            .        .       MATE,4: phase 2
                            .        .       MATE,5: interface phase 2 with background
                            >

                    Sub volumes and interface vector are only relevant for interfaces.

        vtkMesh: bool, default=False
            Writes the VTK of interpolated fields and materials.
            If writeConnectivity is None it names it "spam.vtk" otherwise `writeConnectivity`.vtk

        nSkip: int, default=1
            In the gmsh file, number of number to ignore between the
            element type (second number, 4 for tetrahedra) and the connectivity.

        vtkMesh: bool, default=False
            Save vtk file of the mesh.

    Returns
    -------
        (connectivity, materials): (nElem x 4 numpy array, nElem x 5 numpy array)
            **connectivity**: the classical connectivity matrix
            **materials**: for each element ``elemType, subVol, interX, interY, interZ`` (see outputFile for details).

    """
    # init projmorpho
    pr = projmorpho("spam" if writeConnectivity is None else writeConnectivity, thresholds)

    # transform mesh file to array:
    if isinstance(mesh, str):
        import meshio
        tmp = meshio.read(mesh)
        points = tmp.points
        cells = tmp.cells_dict.get("tetra")

    else:
        points = mesh['points']
        cells = mesh['cells']

    # DEBUG: Artificially add unused node
    # points = numpy.insert(points, 10, [-1.0,-1.0,-1.0], axis=0)
    # for i, node_number_x4 in enumerate(cells):
    #     for j, node_number in enumerate(node_number_x4):
    #         if cells[i, j] >= 10:
    #             cells[i, j] += 1

    # test if unused nodes
    cells_set = set(cells.ravel())  # ordered numbering in connectivity
    n_points_used = len(cells_set)

    if n_points_used != points.shape[0]:
        print("Deleting points before projection")

        # removing unused nodes
        points_to_delete = []
        n_deleted = 0
        for new, old in enumerate(cells_set):
            # check if holes in the connectivity matrix
            if new != old - n_deleted:
                points_to_delete.append(new + n_deleted)
                n_deleted += 1
                # print(new, old, n_deleted, old - n_deleted)
        points = numpy.delete(points, points_to_delete, axis=0)

        print("Renumbering connectivity matrix")
        # renumbering connectivity matrix accordingly
        new_node_numbering = {old: new + 1 for new, old in enumerate(cells_set)}
        for i, node_number_x4 in enumerate(cells):
            for j, node_number in enumerate(node_number_x4):
                if new_node_numbering[cells[i, j]] != cells[i, j]:
                    cells[i, j] = new_node_numbering[cells[i, j]]
    del cells_set

    # check if cell number start by 1 or 0
    if cells.min() == 0:
        print("Shift connectivity by 1 to start at 1")
        cells += 1

    pr.setMesh(points, cells.ravel())

    if isinstance(fields, dict):
        # fields values
        values = fields["values"]
        # origin
        origin = [_ for _ in reversed(fields["origin"])]
        # nPoints
        nPoints = [n + 1 for n in reversed(fields["nCells"])]
        # field size
        lengths = [_ for _ in reversed(fields["lengths"])]
        # ravel fields values
        values = [v.ravel() for v in values]
        pr.setField(values, lengths, nPoints, origin)
    else:
        fields = [fields] if isinstance(fields, str) else fields
        pr.setFieldFromFile(fields)

    pr.interpolateField()
    pr.setMaterials()
    c = numpy.array(pr.getConnectivity()).reshape(cells.shape)
    m = numpy.array(pr.getMaterials())
    if writeConnectivity:
        pr.writeMeshProjection()
    if vtkMesh:
        pr.writeMeshProjectionVTK()
        pr.writeInterfacesVTK()

    return c, m


def distanceField(phases, phaseID=1):
    """
    This function tranforms an array/image of integers into a continuous field.
    It works for segmented binary/trinary 3D images or arrays of integers.
    It has to be run for each phase seperately.

    It uses of the **Distance Transform Algorithm**.
    For every voxel belonging to a phase a value indicating the distance
    (in voxels) of that point to the nearest background point is computed.
    The DTA is computed for the inverted image as well and the computed distances
    are setting to negative values.
    The 2 distance fields are merged into the final continuuos distance field where:

        * positive numbers: distances from the phase to the nearest background voxel
        * negative values: distances from the background to the nearest phase voxel
        * zero values: the interface between the considered phase and the background

    Parameters
    -----------
        phases : array
            The input image/array (each phase should be represented with only one number)

        phaseID : int, default=1
            The integer indicating the phase which distance field you want to calculate

    Returns
    --------
        distance field of the phase: array

    Example
    --------
        >>> import tifffile
        >>> im = tifffile.imread( "mySegmentedImage.tif" )
        In this image the inclusions are labelled 1 and the matrix 0
        >>> di = projection.distanceField( im, phase=1 )
        The resulting distance field is made of float between -1 and 1

    """
    import numpy
    from scipy import ndimage

    # create binary image from phases and phaseID
    binary = numpy.zeros_like(phases, dtype=numpy.bool)
    binary[phases == phaseID] = True

    # Create the complementary binary image
    binaryNot = numpy.logical_not(binary)

    # Step 4: Calculate the distance algorithm for the 2 binary images

    binaryDist = ndimage.morphology.distance_transform_edt(binary).astype('<f4')
    binaryNotDist = ndimage.morphology.distance_transform_edt(binaryNot).astype('<f4')

    # normalise if needed

    # if normalise:
    #     binaryDist = binaryDist / binaryDist.max()

    # if normalise:
    #     binaryNotDist = binaryNotDist.astype(numpy.float32)
    #     binaryNotDist = binaryNotDist / binaryNotDist.max()

    # Step 5: Merge the 2 distance fields into the final one
    binaryNotDist = (-1.0) * binaryNotDist
    binaryNotDist = binaryNotDist + binaryDist

    return binaryNotDist


def saveFieldFile(im, lengths=[1.0, 1.0, 1.0], origin=[0, 0, 0], fileName='spam.dat'):
    """
    This function creates the input file (field file) for Projmorpho
    based on a tifffile (image) or an array

    The file structure is:

    .. code-block:: bash

        row 1: field length vector:   lx, ly, lz
        row 2: field origin vector:    x,  y,  z
        row 3: shape of the field3nd: nx, ny, nz) which are (im.shape[2], im.shape[1], im.shape[0])
        row 4: field value

        ...    field values organised in lexicographical order.

        row n: field value

    Parameters
    -----------
        im: array
            The input image/array field

        lengths: array, default=[1,1,1]
            The physical dimensions of the field (*e.g.*, in mm).
            Its length has to be 3 representing direction z, y, and x.

        origin: array, default=[0,0,0]
            The origin of the field.
            Its length has to be 3 representing direction z, y, and x.

        fileName : string, default='spam.vtk'
            Name of the output file.

    """
    with open(fileName, 'w') as f:
        f.write('{}, {}, {}\n'.format(*reversed(lengths)))
        f.write('{}, {}, {}\n'.format(*reversed(origin)))
        f.write('{}, {}, {}\n'.format(*reversed(im.shape)))
        for v in im.reshape(-1):
            f.write('{}\n'.format(v))
    f.close()


# if __name__ == '__main__':
#     totalVolumeFraction = 0.1
#     rejectionLength = 0.01
#     phases = [[0.04, 0.05, 0.8], [0.02, 0.02, 0.2]]
#     vtkSpheres = False
#     vtkField = True
#     convertToField = True
#     fieldName = "a"
#     origin = [0, 0, 0]
#     lengths = [1, 2, 0.5]
#     nCells = [20, 40, 10]
#     # spheres, values = packSpheres(totalVolumeFraction, rejectionLength, phases, origin=origin, lengths=lengths, nCells=nCells, convertToField=convertToField, inside=True, fieldName=fieldName, vtkSpheres=vtkSpheres, vtkField=vtkField)
#     #
#     # print(spheres)
#     # print(fields)
#     #
#     fieldName = "a2"
#     fieldName = "OneSphere"
#     spheres = [[0.5, 0.5, 0.5, 0.5, 1]]
#     spheres, fields = packSpheresFromList(spheres, rejectionLength, convertToField=convertToField, inside=True, fieldName=fieldName, vtkSpheres=vtkSpheres, vtkField=vtkField)
#
#     # print(spheres)
#
#     # spheres = [[0.5, 0.5, 0.5, 0.5, 1]]
#     # field = distanceFieldFromObjects(spheres, fieldName=fieldName, vtkField=vtkField)
#     # print(field)
#     #
#     # import spam.mesh.unstructured as umesh
#     # points, cells = umesh.createCuboid(lengths, 0.02, gmshFile="myMesh", vtkFile="myMesh")
#     # mesh = {"points": points, "cells": cells}
#     #
#     # # print(projmorpho)
#     # mesh = "myMesh.msh"
#     # # fields = {"origin": origin, "lengths": lengths, "nCells": nCells, "values": values}
#     # fields = ["a_phase_0.dat", "a_phase_1.dat"]
#     # connectivity, materials = projectField(mesh, fields, writeConnectivity="projection", vtkMesh=True)

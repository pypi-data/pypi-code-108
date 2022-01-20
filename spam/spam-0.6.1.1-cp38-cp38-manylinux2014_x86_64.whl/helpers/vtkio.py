"""
Library of SPAM functions for reading and writing VTK files with meshio sometimes
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


"""
This module offers a set functions in order to read and writes VTK files.

This module is mainly made of ``meshio`` wrappers adapted to ``spam``.
The types of data currently handled are:

    * Structured meshes of cuboids
    * Unstructured meshes of tetrahedrs
    * List of objects (TODO)

WARNING
-------
    Python dependencies
        * ``meshio``

VTK files are assumed to be in X,Y,Z format, and numpy arrays are in Z,Y,X, so the following
policy is followed:

  - position arrays are simply reversed so Z comes out first
  - scalar arrays are left as they are
  - vectors and matrices are assumed to be positional (a surface vector for example) and are reversed
"""
import six
import numpy
import meshio
#from numba import jit

# Structured meshes


def readStructuredVTK(f, fieldAsked=None):
    """
    Read a plain text VTK.

    By default read the full text and put all fields in a dictionnay.
    Specific fields can be selected with `fieldAsked`.

    Parameters
    ----------
        f : string
            Name of the VTK file.

        fieldAsked : array of string, default=None
            List of the field names.

    Returns
    -------
        fields : dict
            Dictionnary of all the fields without nodal or cell distinctions.

        .. code-block:: python

            fields = { 'field1name':[field1value1, field1value2, ...],
                       'field2name':[field2value1, field2value2, ...],
                       ...}

    Note
    ----
        The outputs are kept flattened.
    """

    # read the full file
    with open(f) as content_file:
        content = [l.strip() for l in content_file if l.strip()]

    # find line numbers of principal key words
    pl = {l.split()[0]: i
          for i, l in enumerate(content)
          if l.split()[0] in ['CELLS', 'POINTS', 'CELL_DATA', 'POINT_DATA']}

    # find keys in the file
    nl = {}
    keys_found = {}
    if('POINT_DATA' in pl):
        nl.update({'POINT_DATA': int(content[pl['POINT_DATA']].split()[1])})
        keys_found.update({l.split()[1]: [pl['POINT_DATA'] + i, content[pl['POINT_DATA'] + i].split()[0], 'POINT_DATA'] for i, l in enumerate(content[pl['POINT_DATA']:]) if l.split()[0] in ['SCALARS', 'VECTORS', 'TENSORS']})

    # not used in regular mesh (implicit node position)
    # if('POINTS' in pl):
    #     nl.update({'POINTS': int(content[pl['POINTS']].split()[1])})
    #     keys_found.update({'POINTS': [pl['POINTS'], 'VECTORS', 'POINTS']})

    if('CELL_DATA' in pl):
        nl.update({'CELL_DATA': int(content[pl['CELL_DATA']].split()[1])})
        keys_found.update({l.split()[1]: [pl['CELL_DATA'] + i, content[pl['CELL_DATA'] + i].split()[0], 'CELL_DATA'] for i, l in enumerate(content[pl['CELL_DATA']:]) if l.split()[0] in ['SCALARS', 'VECTORS', 'TENSORS']})

    # not used in regular mesh (implicit connectivity)
    # if('CELLS' in pl):
    #     nl.update({'CELLS': int(content[pl['CELLS']].split()[1])})
    #     keys_found.update({'CELLS': [pl['CELLS'], 'TETRA', 'CELLS']})

    # get relevant keys
    if fieldAsked is None:
        keys_valid = keys_found
    elif isinstance(fieldAsked, list):
        keys_valid = {k: keys_found[k] for k in fieldAsked if k in keys_found}
    elif isinstance(fieldAsked, str) and fieldAsked in keys_found:
        keys_valid = {fieldAsked: keys_found[fieldAsked]}
    else:
        keys_valid = {}

    # fill output
    fields = {}
    for l in keys_valid.items():
        dict_skip = {'CELLS': {'TETRA': 1},
                     'POINTS': {'VECTORS': 1},
                     'CELL_DATA': {'SCALARS': 2, 'VECTORS': 1, 'TENSORS': 1},
                     'POINT_DATA': {'SCALARS': 2, 'VECTORS': 1, 'TENSORS': 1}
                     }
        l_skip = dict_skip[l[1][2]][l[1][1]]
        l_start = l_skip + l[1][0]
        l_end = l_start + nl[l[1][2]]
        # hack for the scalar case to avoir list of single element lists
        if l[1][1] == 'SCALARS':
            fields.update({l[0]: numpy.array([float(r) for r in content[l_start:l_end]])})
        else:
            fields.update({l[0]: numpy.array([[float(c) for c in reversed(r.split())] for r in content[l_start:l_end]])})

    return fields


def writeStructuredVTK(aspectRatio=[1.0, 1.0, 1.0],
                       origin=[0.0, 0.0, 0.0],
                       cellData={},
                       pointData={},
                       fileName='spam.vtk'):
    """
    Write a plain text regular grid vtk from:
        * 3D arrays for 3D scalar fields
        * 4D arrays for 3D vector fields

    Parameters
    ----------
        aspectRatio : size 3 array, float
            Length between two nodes in every direction `e.i.` size of a cell
            Default = [1, 1, 1]

        origin : size 3 array float
            Origin of the grid
            Default = [0, 0, 0]

        cellData : dict ``{'field1name':field1,'field2name':field2, ...}``
            Cell fields, not interpolated by paraview.
            The field values are reshaped into a flat array in the lexicographic order.
            ``field1`` and ``field2`` are ndimensional array (3D arrays are scalar fields and 4D array are vector valued fields).

        pointData : dict ``{'field1name':field1,'field2name':field2, ...}``
            Nodal fields, interpolated by paraview. ``pointData`` has the same shape as ``cellData``.

        fileName : string
            Name of the output file.
            Default = 'spam.vtk'

    """
    # WARNING
    # -------
    # This function deals with structured mesh thus ``x`` and ``z`` axis are swapped **in python**.
    # check dimensions

    dimensions = []

    if len(cellData) + len(pointData) == 0:
        print('spam.helpers.writeStructuredVTK() Empty files. Not writing {}'.format(fileName))
        return 0

    if len(cellData):
        dimensionsCell = list(cellData.values())[0].shape[:3]
        for k, v in six.iteritems(cellData):
            if set(dimensionsCell) != set(v.shape[:3]):
                print('spam.helpers.writeStructuredVTK() Inconsistent cell field sizes {} != {}'.format(dimensionsCell, v.shape[:3]))
                return 0
        dimensions = [n + 1 for n in dimensionsCell]

    if len(pointData):
        dimensionsPoint = list(pointData.values())[0].shape[:3]
        for k, v in six.iteritems(pointData):
            if set(dimensionsPoint) != set(v.shape[:3]):
                print('spam.helpers.writeStructuredVTK() Inconsistent point field sizes {} != {}'.format(dimensionsPoint, v.shape[:3]))
                return 0
        dimensions = dimensionsPoint

    if len(cellData) and len(pointData):
        if set([n + 1 for n in dimensionsCell]) != set(dimensionsPoint):
            print('spam.helpers.writeStructuredVTK() Inconsistent point VS cell field sizes. Point size should be +1 for each axis.')

    with open(fileName, 'w') as f:
        # header
        f.write('# vtk DataFile Version 2.0\n')
        f.write('VTK file from spam: {}\n'.format(fileName))
        f.write('ASCII\n\n')
        f.write('DATASET STRUCTURED_POINTS\n')

        f.write('DIMENSIONS {} {} {}\n'.format(*reversed(dimensions)))
        f.write('ASPECT_RATIO {} {} {}\n'.format(*reversed(aspectRatio)))
        f.write('ORIGIN {} {} {}\n\n'.format(*reversed(origin)))

        # pointData
        if len(pointData) == 1:
            f.write('POINT_DATA {}\n\n'.format(dimensions[0] * dimensions[1] * dimensions[2]))
            _writeFieldInVtk(pointData, f)
        elif len(pointData) > 1:
            f.write('POINT_DATA {}\n\n'.format(dimensions[0] * dimensions[1] * dimensions[2]))
            for k in pointData:
                _writeFieldInVtk({k: pointData[k]}, f)

        # cellData
        if len(cellData) == 1:
            f.write('CELL_DATA {}\n\n'.format((dimensions[0] - 1) * (dimensions[1] - 1) * (dimensions[2] - 1)))
            _writeFieldInVtk(cellData, f)
        elif len(cellData) > 1:
            f.write('CELL_DATA {}\n\n'.format((dimensions[0] - 1) * (dimensions[1] - 1) * (dimensions[2] - 1)))
            for k in cellData:
                _writeFieldInVtk({k: cellData[k]}, f)

        f.write('\n')


def writeGlyphsVTK(coordinates,
                   pointData,
                   fileName='spam.vtk'):
    """
    Write a plain text glyphs vtk.

    Parameters
    ----------
        coordinates : ``n`` by 3 array of float
            Coordinates of the centre of all ``n`` glyphs

        pointData : dict ``{'field1name':field1,'field2name':field2, ...}``
            Value attached to each glyph.
            ``field1`` and ``field2`` are ``n`` by 1 arrays for scalar values and ``n`` by 3 for vector values.

        fileName : string, default='spam.vtk'
            Name of the output file.

    """
    # WARNING
    # -------
    # This function deals with structured mesh thus ``x`` and ``z`` axis are swapped **in python**.

    # check dimensions

    dimension = coordinates.shape[0]

    if len(pointData):
        for k, v in six.iteritems(pointData):
            if dimension != v.shape[0]:
                print('spam.helpers.writeGlyphsVTK() Inconsistent point field sizes {} != {}'.format(dimension, v.shape[0]))
                return 0
    else:
        print('spam.helpers.writeGlyphsVTK() Empty files. Not writing {}'.format(fileName))
        return

    with open(fileName, 'w') as f:
        # header
        f.write('# vtk DataFile Version 2.0\n')
        # f.write('VTK file from spam: {}\n'.format(fileName))
        f.write('Unstructured grid legacy vtk file with point scalar data\n')
        f.write('ASCII\n\n')

        # coordinates
        f.write('DATASET UNSTRUCTURED_GRID\n')
        f.write('POINTS {:.0f} float\n'.format(dimension))
        for coord in coordinates:
            f.write('    {} {} {}\n'.format(*reversed(coord)))

        f.write('\n')

        # pointData
        if len(pointData) == 1:
            f.write('POINT_DATA {}\n\n'.format(dimension))
            _writeFieldInVtk(pointData, f, flat=True)
        elif len(pointData) > 1:
            f.write('POINT_DATA {}\n\n'.format(dimension))
            for k in pointData:
                _writeFieldInVtk({k: pointData[k]}, f, flat=True)

        f.write('\n')


def _writeFieldInVtk(data, f, flat=False):
    """
    Private helper function for writing vtk fields
    """

    for key in data:
        field = data[key]

        if flat:
            # SCALAR flatten (n by 1)
            if(len(field.shape) == 1):
                f.write('SCALARS {} float\n'.format(key.replace(" ", "_")))
                f.write('LOOKUP_TABLE default\n')
                for item in field:
                    f.write('    {}\n'.format(item))
                f.write('\n')

            # VECTORS flatten (n by 3)
            elif(len(field.shape) == 2 and field.shape[1] == 3):
                f.write('VECTORS {} float\n'.format(key.replace(" ", "_")))
                for item in field:
                    f.write('    {} {} {}\n'.format(*reversed(item)))
                f.write('\n')

        else:
            # SCALAR not flatten (n1 by n2 by n3)
            if(len(field.shape) == 3):
                f.write('SCALARS {} float\n'.format(key.replace(" ", "_")))
                f.write('LOOKUP_TABLE default\n')
                for item in field.reshape(-1):
                    f.write('    {}\n'.format(item))
                f.write('\n')

            # VECTORS (n1 by n2 by n3 by 3)
            elif(len(field.shape) == 4 and field.shape[3] == 3):
                f.write('VECTORS {} float\n'.format(key.replace(" ", "_")))
                for item in field.reshape((field.shape[0] * field.shape[1] * field.shape[2], field.shape[3])):
                    f.write('    {} {} {}\n'.format(*reversed(item)))
                f.write('\n')

            # TENSORS (n1 by n2 by n3 by 3 by 3)
            elif(len(field.shape) == 5 and field.shape[3] * field.shape[4] == 9):
                f.write('TENSORS {} float\n'.format(key.replace(" ", "_")))
                for item in field.reshape((field.shape[0] * field.shape[1] * field.shape[2], field.shape[3] * field.shape[4])):
                    f.write('    {} {} {}\n    {} {} {}\n    {} {} {}\n\n'.format(*reversed(item)))
                f.write('\n')
            else:
                print("spam.helpers.vtkio._writeFieldInVtk(): I'm in an unknown condition!")


# Unstructured meshes
def writeUnstructuredVTK(points,
                         connectivity,
                         elementType='tetra',
                         pointData={},
                         cellData={},
                         fileName='spam.vtk'):
    """
    Writes a binary VTK using ``meshio`` selecting only the tetrahedra.

    Parameters
    ----------
        points : 2D numpy array
            The coordinates of the mesh nodes (zyx)
            Each line is [zPos, yPos, xPos]

        connectivity : 2D numpy array
            The connectivity matrix of the tetrahedra elements
            Each line is [node1, node2, node3, node4]

        elementType : string
            The type of element used for the mesh
            Default = 'tetra'

        cellData : dict
            Cell fields, not interpolated by paraview.

            .. code-block:: python

                cellData = { 'field1name':field1,'field2name':field2 ...}

            where field1 and field2 are 1D or 2D arrays. 1D arrays are scalar fields and 2D array are vector valued fields.

        pointData : dict
            Nodal fields, interpolated by paraview. ``pointData`` has the same shape as ``cellData``.

            .. code-block:: python

                pointData = { 'field1name':field1,'field2name':field2 ...}

        fileName : string
            Name of the output file.
            Default='spam.vtk'

    """
    # VTK files are assumed to be in X,Y,Z format, and numpy arrays are in Z,Y,X, so the following
    # policy is follwed:
    #   - position arrays are simply reversed so Z comes out first
    #   - scalar arrays are left as they are
    #   - vectors and matrices are assumed to be positional (a surface vector for example) and are reversed
    #   - node numbering in connectivity matrix is changed to ensure a positive Jacobian for each element

    # Anything bigger than a scalar field in pointData should be flipped
    for key, value in pointData.items():
        # print("writeUnstructuredVTK(): pointData",key,pointData[key].shape)
        if len(pointData[key].shape) > 1:
            if pointData[key].shape[1] > 1:
                pointData[key] = pointData[key][:, ::-1]

    # Anything bigger than a scalar field in cellData should be flipped
    for key, value in cellData.items():
        # print("writeUnstructuredVTK(): cellData",key,cellData[key].shape)
        if len(cellData[key].shape) > 1:
            if cellData[key].shape[1] > 1:
                cellData[key] = cellData[key][:, ::-1]

    # change node numbering in connectivity matrix for tetrahedra elements
    if elementType == 'tetra':
        tmp = connectivity.copy()
        connectivity[:, 1] = tmp[:, 3]
        connectivity[:, 3] = tmp[:, 1]

    meshio.write_points_cells(fileName,
                              points[:, ::-1],
                              {elementType: connectivity},
                              point_data=pointData if len(pointData) else None,
                              cell_data={k: [v] for k, v in cellData.items()} if len(cellData) else None)


def readUnstructuredVTK(fileName):
    """
    Read a binary VTK using ``meshio`` selecting only the tetrahedra.

    Parameters
    ----------
        fileName : string
            Name of the input file.

    Returns
    -------
        points : array
            The list of node coordinates (zyx).

       connectivity : array
            The connectivity matrix (cell id starts at 0).

        pointData : dict
            Nodal fields, interpolated by paraview.

        cellData : dict
            Cell fields, not interpolated by paraview.

    """
    # VTK files are assumed to be in X,Y,Z format, and numpy arrays are in Z,Y,X, so the following
    # policy is follwed:
    #   - position arrays are simply reversed so Z comes out first
    #   - scalar arrays are left as they are
    #   - vectors and matrices are assumed to be positional (a surface vector for example) and are reversed
    #   - node numbering in connectivity matrix is changed to ensure a positive Jacobian for each element

    mesh = meshio.read(fileName)

    # Reverse points order into z-first
    points = mesh.points[:, ::-1]
    cellData = dict({})
    pointData = dict({})

    # Make sure that any non-scalar fields are flipped so that z is in the right place in numpy
    for key, values in mesh.cell_data.items():
        for value in values:
            # Inspect first item and make sure it's nut just a number
            if isinstance(value[0], (list, tuple, numpy.ndarray)):
                cellData[key] = value[:, ::-1]
            else:
                cellData[key] = value

    # Make sure that any non-scalar fields are flipped so that z is in the right place in numpy
    for key, value in six.iteritems(mesh.point_data):
        # Inspect first item and make sure it's nut just a number
        if isinstance(value[0], (list, tuple, numpy.ndarray)):
            pointData[key] = value[:, ::-1]
        else:
            pointData[key] = value

    connectivity = mesh.cells_dict['tetra']
    # change node numbering in connectivity matrix
    tmp = connectivity.copy()
    connectivity[:, 1] = tmp[:, 3]
    connectivity[:, 3] = tmp[:, 1]

    return points, connectivity, pointData, cellData


def TIFFtoVTK(fileName, voxelSize=1.0):
    """
    Convert a tifffile to a vtk file for paraview.
    It saves it with the same base name.

    Parameters
    ----------
        fileName : string
            The name of the tif file to convert
    """
    import os
    import tifffile
    import spam.mesh

    # convert to array [fileName] if single name
    fileName = fileName if isinstance(fileName, (list, tuple)) else [fileName]

    # read the tifffile
    im = tifffile.imread(fileName[0])
    print("spam.helpers.TIFFtoVTK: image shape: ", im.shape)
    nCells = numpy.array(im.shape)

    # create coordinates
    points = spam.mesh.createLexicoCoordinates([voxelSize * n for n in nCells], [n + 1 for n in nCells])
    print("spam.helpers.TIFFtoVTK: points shape: ", points.shape)
    print("spam.helpers.TIFFtoVTK: 0 min max: ", points[:, 0].min(), points[:, 0].max())
    print("spam.helpers.TIFFtoVTK: 1 min max: ", points[:, 1].min(), points[:, 1].max())
    print("spam.helpers.TIFFtoVTK: 2 min max: ", points[:, 2].min(), points[:, 2].max())

    # create connectivity
    cells = _loop_for_tifToVTK(nCells)
    print("spam.helpers.TIFFtoVTK: cells shape: ", cells.shape)

    # create VTK
    f = os.path.splitext(fileName[0])[0]
    if len(fileName) == 1:
        meshio.write_points_cells(f"{f}.vtk", points, {"hexahedron": cells}, cell_data={"grey": [im.T.ravel()]})
    else:
        with meshio.xdmf.TimeSeriesWriter(f"{f}.xmf") as writer:
            writer.write_points_cells(points, [("hexahedron", cells)])
            for i, name in enumerate(fileName):
                im = tifffile.imread(name)
                writer.write_data(i, cell_data={"grey": [im.T.ravel()]})


#@jit(nopython=True)
def _loop_for_tifToVTK(nCells):
    cells = numpy.zeros((numpy.prod(nCells), 8), dtype=numpy.uint)
    nx, ny, nz = nCells
    i = 0
    for z in range(nz):
        for y in range(ny):
            for x in range(nx):
                n = x + ((nx + 1) * y) + ((nx + 1) * (ny + 1)) * z
                cells[i][0] = n
                cells[i][1] = n + 1
                cells[i][2] = n + nx + 2
                cells[i][3] = n + nx + 1
                for j in range(4):
                    cells[i][4 + j] = cells[i][j] + ((nx + 1) * (ny + 1))
                i += 1
    return cells

# if __name__ == "__main__":
#     tifToVTK(["/home/roubin/nx/xr_bin16.tif", "/home/roubin/nx/ne_bin16.tif"])

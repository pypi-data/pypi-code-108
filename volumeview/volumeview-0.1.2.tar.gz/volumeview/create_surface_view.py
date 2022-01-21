import os
import math
import numpy as np
import figurl as fig
import kachery_client as kc

def create_surface_view(*,
    vertices: np.ndarray, # n x 3
    faces: np.ndarray # m x 3 - triangular mesh
):
    assert vertices.ndim == 2, 'Vertices must be 2-dimensional array (second dimension size 3)'
    assert vertices.shape[1] == 3
    assert faces.ndim == 2, 'Faces must be 2-dimensional array (second dimension size 3)'
    assert faces.shape[1] == 3
    assert vertices.dtype in [np.float32], f'Unsupported data type for vertices: {vertices.dtype}'
    assert faces.dtype in [np.int16, np.int32], f'Unsupported data type for faces: {faces.dtype}'
    data = {
        'type': 'surface',
        'numVertices': int(vertices.shape[0]),
        'numFaces': int(faces.shape[0]),
        'vertices': vertices,
        'faces': faces
    }
    F = fig.Figure(view_url='gs://figurl/volumeview-2', data=data)
    return F

def _parse_vtk_unstructured_grid(vtk_path: str):
    x = vtk_to_mesh_dict(vtk_path, format='UnstructuredGrid')
    vertices = np.array(x['vertices'], dtype=np.float32).T
    faces = np.array(x['faces'], dtype=np.int32)
    ifaces = np.array(x['ifaces'], dtype=np.int32)

    # verify that this is a triangular mesh
    assert ifaces[0] == 0, 'Must be a triangular mesh'
    for i in range(1, len(ifaces)):
        assert ifaces[i] == ifaces[i - 1] + 3, 'Must be a triangular mesh'
    
    faces = np.reshape(faces, (math.floor(len(faces) / 3), 3))

    return vertices, faces
    
def vtk_to_mesh_dict(vtk_path: str, format: str) -> dict:
    import numpy as np
    from vtk.util.numpy_support import vtk_to_numpy
    from vtk import vtkUnstructuredGridReader, vtkXMLPolyDataReader
    import vtk.numpy_interface.dataset_adapter as dsa

    if format == 'UnstructuredGrid':
        reader = vtkUnstructuredGridReader()
    elif format == 'XMLPolyData':
        reader = vtkXMLPolyDataReader()
    else:
        raise Exception(f'Unexpected format: {format}')
    reader.SetFileName(vtk_path)
    reader.Update()
    X = reader.GetOutput()
    Y = dsa.WrapDataObject(X)

    vertices0 = vtk_to_numpy(Y.Points) # 3 x n
    vertices = vertices0.T.tolist()
    if format == 'XMLPolyData':
        faces0 = vtk_to_numpy(Y.Polygons)
    else:
        faces0 = vtk_to_numpy(Y.Cells)
    ifaces = []
    faces = []
    i = 0
    while i < len(faces0):
        num_points = faces0[i]
        i = i + 1
        ifaces.append(len(faces))
        for j in range(num_points):
            faces.append(int(faces0[i]))
            i = i + 1

    return {
        'vertices': vertices,
        'ifaces': ifaces,
        'faces': faces
    }
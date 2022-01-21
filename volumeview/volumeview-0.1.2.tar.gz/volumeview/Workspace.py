from typing import List
import os
import numpy as np
import kachery_client as kc
import figurl as fig
from figurl.core.serialize_wrapper import _serialize


class Workspace:
    def __init__(self) -> None:
        self._grids: List[WorkspaceGrid] = []
        self._surfaces: List[WorkspaceSurface] = []
        self._grid_vector_fields: List[WorkspaceGridVectorField] = []
        self._grid_scalar_fields: List[WorkspaceGridVectorField] = []
        self._grid_regions: List[WorkspaceGridRegion] = []
        self._surface_vector_fields: List[WorkspaceSurfaceVectorField] = []
        self._surface_scalar_fields: List[WorkspaceSurfaceVectorField] = []
        self._surface_regions: List[WorkspaceSurfaceRegion] = []
    def add_grid(self, *, name: str, Nx: int, Ny: int, Nz: int, x0: float, y0: float, z0: float, dx: float, dy: float, dz: float):
        X = WorkspaceGrid(name=name, Nx=Nx, Ny=Ny, Nz=Nz, x0=x0, y0=y0, z0=z0, dx=dx, dy=dy, dz=dz)
        self._grids.append(X)
        return X
    def add_surface(self, *, name: str, vertices: np.ndarray, faces: np.ndarray):
        X = WorkspaceSurface(name=name, vertices=vertices, faces=faces)
        self._surfaces.append(X)
        return X
    def add_grid_vector_field(self, *, name: str, grid: 'WorkspaceGrid', data: np.ndarray):
        X = WorkspaceGridVectorField(name=name, grid=grid, data=data)
        self._grid_vector_fields.append(X)
        return X
    def add_grid_scalar_field(self, *, name: str, grid: 'WorkspaceGrid', data: np.ndarray):
        X = WorkspaceGridScalarField(name=name, grid=grid, data=data)
        self._grid_scalar_fields.append(X)
        return X
    def add_grid_region(self, *, name: str, grid: 'WorkspaceGrid', data: np.ndarray):
        X = WorkspaceGridRegion(name=name, grid=grid, data=data)
        self._grid_regions.append(X)
        return X
    def add_surface_vector_field(self, *, name: str, surface: 'WorkspaceSurface', data: np.ndarray):
        X = WorkspaceSurfaceVectorField(name=name, surface=surface, data=data)
        self._surface_vector_fields.append(X)
        return X
    def add_surface_scalar_field(self, *, name: str, surface: 'WorkspaceSurface', data: np.ndarray):
        X = WorkspaceSurfaceScalarField(name=name, surface=surface, data=data)
        self._surface_scalar_fields.append(X)
        return X
    def add_surface_region(self, *, name: str, surface: 'WorkspaceSurface', data: np.ndarray):
        X = WorkspaceSurfaceRegion(name=name, surface=surface, data=data)
        self._surface_regions.append(X)
        return X
    def create_figure(self):
        FIGURL_CHANNEL = os.getenv('FIGURL_CHANNEL')
        assert FIGURL_CHANNEL, 'Environment variable not set: FIGURL_CHANNEL'
        data = {
            'type': 'workspace',
            'grids': [],
            'surfaces': [],
            'gridVectorFields': [],
            'gridScalarFields': [],
            'gridRegions': [],
            'surfaceVectorFields': [],
            'surfaceScalarFields': [],
            'surfaceRegions': []
        }
        for grid in self._grids:
            data['grids'].append({
                'name': grid._name,
                'Nx': grid._Nx,
                'Ny': grid._Ny,
                'Nz': grid._Nz,
                'x0': grid._x0,
                'y0': grid._y0,
                'z0': grid._z0,
                'dx': grid._dx,
                'dy': grid._dy,
                'dz': grid._dz
            })
        for surface in self._surfaces:
            assert surface._vertices.dtype in [np.float32]
            assert surface._faces.dtype in [np.int16, np.int32]
            vertices_uri = kc.store_json(_serialize(surface._vertices))
            kc.upload_file(vertices_uri, channel=FIGURL_CHANNEL, single_chunk=True)
            faces_uri = kc.store_json(_serialize(surface._faces))
            kc.upload_file(faces_uri, channel=FIGURL_CHANNEL, single_chunk=True)
            data['surfaces'].append({
                'name': surface._name,
                'vertices': vertices_uri,
                'faces': faces_uri
            })
        for X in self._grid_vector_fields:
            assert X._data.dtype in [np.float32]
            data_uri = kc.store_json(_serialize(X._data))
            kc.upload_file(data_uri, channel=FIGURL_CHANNEL, single_chunk=True)
            data['gridVectorFields'].append({
                'name': X._name,
                'gridName': X._grid._name,
                'data': data_uri
            })
        for X in self._grid_scalar_fields:
            assert X._data.dtype in [np.float32]
            data_uri = kc.store_json(_serialize(X._data))
            kc.upload_file(data_uri, channel=FIGURL_CHANNEL, single_chunk=True)
            data['gridScalarFields'].append({
                'name': X._name,
                'gridName': X._grid._name,
                'data': data_uri
            })
        for X in self._grid_regions:
            assert X._data.dtype in [np.uint8]
            data_uri = kc.store_json(_serialize(X._data))
            kc.upload_file(data_uri, channel=FIGURL_CHANNEL, single_chunk=True)
            data['gridRegions'].append({
                'name': X._name,
                'gridName': X._grid._name,
                'data': data_uri
            })
        for X in self._surface_vector_fields:
            assert X._data.dtype in [np.float32]
            data_uri = kc.store_json(_serialize(X._data))
            kc.upload_file(data_uri, channel=FIGURL_CHANNEL, single_chunk=True)
            data['surfaceVectorFields'].append({
                'name': X._name,
                'surfaceName': X._surface._name,
                'data': data_uri
            })
        for X in self._surface_scalar_fields:
            assert X._data.dtype in [np.float32]
            data_uri = kc.store_json(_serialize(X._data))
            kc.upload_file(data_uri, channel=FIGURL_CHANNEL, single_chunk=True)
            data['surfaceScalarFields'].append({
                'name': X._name,
                'surfaceName': X._surface._name,
                'data': data_uri
            })
        for X in self._surface_regions:
            assert X._data.dtype in [np.uint8]
            data_uri = kc.store_json(_serialize(X._data))
            kc.upload_file(data_uri, channel=FIGURL_CHANNEL, single_chunk=True)
            data['surfaceRegions'].append({
                'name': X._name,
                'surfaceName': X._surface._name,
                'data': data_uri
            })
        F = fig.Figure(view_url='gs://figurl/volumeview-2', data=data)
        return F

class WorkspaceGrid:
    def __init__(self, *, name: str, Nx: int, Ny: int, Nz: int, x0: float, y0: float, z0: float, dx: float, dy: float, dz: float) -> None:
        self._name = name
        self._Nx = Nx
        self._Ny = Ny
        self._Nz = Nz
        self._x0 = x0
        self._y0 = y0
        self._z0 = z0
        self._dx = dx
        self._dy = dy
        self._dz = dz

class WorkspaceSurface:
    def __init__(self, *, name: str, vertices: np.ndarray, faces: np.ndarray) -> None:
        self._name = name
        self._vertices = vertices
        self._faces = faces

class WorkspaceGridVectorField:
    def __init__(self, *, name: str, grid: WorkspaceGrid, data: np.ndarray) -> None:
        self._name = name
        self._grid = grid
        self._data = data

class WorkspaceGridScalarField:
    def __init__(self, *, name: str, grid: WorkspaceGrid, data: np.ndarray) -> None:
        self._name = name
        self._grid = grid
        self._data = data

class WorkspaceGridRegion:
    def __init__(self, *, name: str, grid: WorkspaceGrid, data: np.ndarray) -> None:
        self._name = name
        self._grid = grid
        self._data = data

class WorkspaceSurfaceVectorField:
    def __init__(self, *, name: str, surface: WorkspaceSurface, data: np.ndarray) -> None:
        self._name = name
        self._surface = surface
        self._data = data

class WorkspaceSurfaceScalarField:
    def __init__(self, *, name: str, surface: WorkspaceSurface, data: np.ndarray) -> None:
        self._name = name
        self._surface = surface
        self._data = data

class WorkspaceSurfaceRegion:
    def __init__(self, *, name: str, surface: WorkspaceSurface, data: np.ndarray) -> None:
        self._name = name
        self._surface = surface
        self._data = data
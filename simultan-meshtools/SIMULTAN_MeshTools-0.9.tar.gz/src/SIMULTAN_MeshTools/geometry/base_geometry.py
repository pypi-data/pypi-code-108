import numpy as np
from uuid import uuid1
import logging
from copy import copy

from .utils import generate_surface_mesh

logger = logging.getLogger('PySimultanRadiation')

from .extended_geometry import VertexExt, EdgeExt, EdgeLoopExt, FaceExt, VolumeExt


class GeoBaseClass(object):

    def __init__(self, *args, **kwargs):

        self.id = int.from_bytes(uuid1().bytes, byteorder='big', signed=True) >> 64
        self.name = kwargs.get('name', 'unnamed geometry')


class Vertex(VertexExt, GeoBaseClass):

    def __init__(self, *args, **kwargs):
        GeoBaseClass.__init__(self, *args, **kwargs)
        self.position = kwargs.get('position', np.array([0, 0, 0]))
        VertexExt.__init__(self, *args, **kwargs)


class Edge(EdgeExt, GeoBaseClass):

    def __init__(self, *args, **kwargs):
        GeoBaseClass.__init__(self, *args, **kwargs)
        self.vertices = kwargs.get('vertices', None)
        EdgeExt.__init__(self, *args, **kwargs)


class EdgeLoop(EdgeLoopExt, GeoBaseClass):

    def __init__(self, *args, **kwargs):
        GeoBaseClass.__init__(self, *args, **kwargs)

        self.edges = kwargs.get('edges', None)
        self.edge_orientations = kwargs.get('edge_orientations', None)

        EdgeLoopExt.__init__(self, *args, **kwargs)

    @property
    def points(self):

        points = np.zeros([self.edges.__len__(), 3])

        if self.edge_orientations[0] == 1:
            points[0, :] = self.edges[0].vertices[0].position
        else:
            points[0, :] = self.edges[0].vertices[1].position

        for i, edge in enumerate(self.edges):
            if self.edge_orientations[i] == 1:
                points[i, :] = edge.vertices[1].position
            else:
                points[i, :] = edge.vertices[0].position

        return points


class Face(FaceExt, GeoBaseClass):

    def __init__(self, *args, **kwargs):
        GeoBaseClass.__init__(self, *args, **kwargs)

        self.boundary = kwargs.get('boundary', None)
        self.holes = kwargs.get('holes', [])
        self.hole_faces = kwargs.get('hole_faces', [])
        self.construction = kwargs.get('construction', None)

        FaceExt.__init__(self, *args, **kwargs)

    @property
    def points(self):
        return self.boundary.points


class Volume(VolumeExt, GeoBaseClass):

    def __init__(self, *args, **kwargs):
        GeoBaseClass.__init__(self, *args, **kwargs)

        self.faces = kwargs.get('faces', [])

        VolumeExt.__init__(self, *args, **kwargs)


class Terrain(GeoBaseClass):

    def __init__(self, *args, **kwargs):
        GeoBaseClass.__init__(self, *args, **kwargs)

        self._mesh = None

        self.vertices = kwargs.get('vertices')
        self.edges = kwargs.get('edges')
        self.edge_loops = kwargs.get('edge_loops')
        self.faces = kwargs.get('faces')

    @property
    def mesh(self):
        if self._mesh is None:
            logger.info(f'Terrain: {self.name}, {self.id}: generating surface mesh...')
            self.mesh = self.faces[0].mesh
            logger.info(f'Terrain: {self.name}, {self.id}: Surface mesh generation successful')
        return self._mesh

    @mesh.setter
    def mesh(self, value):
        self._mesh = value

    def export_vtk(self, filename):
        logger.info(f'Terrain: {self.name}, {self.id}: exporting vtk to {filename}')
        self.mesh.write(filename)
        logger.info(f'Terrain: {self.name}, {self.id}: export successful')


class Sky(Terrain):

    def __init__(self, *args, **kwargs):

        Terrain.__init__(self, *args, **kwargs)

        self.mesh_size = kwargs.get('mesh_size', 9999)

        self.mesh_min_size = kwargs.get('mesh_min_size', 0.1)
        self.mesh_max_size = kwargs.get('mesh_max_size', 10)

        self.surface_mesh_method = kwargs.get('surface_mesh_method', 'robust')

    @property
    def mesh(self):
        if self._mesh is None:
            self.mesh = self.create_surface_mesh()
        return self._mesh

    @mesh.setter
    def mesh(self, value):
        self._mesh = value

    def create_surface_mesh(self):

        faces = copy(self.faces)
        edge_loops = []
        [(edge_loops.append(x.boundary), edge_loops.extend(x.holes)) for x in faces]
        edge_loops = set(edge_loops)
        edges = []
        [edges.extend(x.edges) for x in edge_loops]
        edges = set(edges)
        vertices = []
        [vertices.extend([x.vertices[0], x.vertices[1]]) for x in edges]
        vertices = set(vertices)

        try:
            mesh = generate_surface_mesh(vertices=vertices,
                                         edges=edges,
                                         edge_loops=edge_loops,
                                         faces=faces,
                                         model_name=str(self.id),
                                         lc=self.mesh_size,
                                         min_size=self.mesh_min_size,
                                         max_size=self.mesh_max_size,
                                         method=self.surface_mesh_method)
        except Exception as e:
            logger.error(f'{self.name}; {self.id}: Error while creating surface mesh:\n{e}')
            return

        return mesh

    def export_vtk(self, filename):
        logger.info(f'Sky: {self.name}, {self.id}: exporting vtk to {filename}')
        self.mesh.write(filename)
        logger.info(f'Sky: {self.name}, {self.id}: export successful')

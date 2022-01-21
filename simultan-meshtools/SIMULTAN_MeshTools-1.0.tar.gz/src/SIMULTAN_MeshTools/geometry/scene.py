from uuid import uuid4
import numpy as np
from ..logger import logger
from .utils import generate_mesh, generate_surface_mesh, generate_terrain, generate_sky
import sys
# from collections import Counter
# from copy import copy
# import trimesh
from trimesh import Trimesh
import traceback


class Scene(object):

    def __init__(self, *args, **kwargs):
        """
        Class with the geometry which should be ray_traced; creates mesh with all necessary informations.

        @keyword name: Name of the template; type: str
        @keyword id: id of the template; type: uuid4; default: new generated uuid4
        @keyword faces: list of PySimultanRadiation.Geometry.extended_face.ExtendedFace; default: []
        """

        self._mesh = None
        self._hull_mesh = None
        self._surface_mesh = None
        self.mesh_size = kwargs.get('mesh_size', 1)
        self.mesh_min_size = kwargs.get('mesh_min_size', 0.5)
        self.mesh_max_size = kwargs.get('mesh_max_size', 10)

        self.surface_mesh_method = kwargs.get('surface_mesh_method', 'robust')

        self.name = kwargs.get('name', 'Unnamed Scene')
        self.id = kwargs.get('id', uuid4())

        self.vertices = kwargs.get('vertices', [])
        self.edges = kwargs.get('edges', [])
        self.edge_loops = kwargs.get('edge_loops', [])
        self.faces = kwargs.get('faces', [])
        self.volumes = kwargs.get('volumes', [])

        self._hull_faces = kwargs.get('_hull_faces', None)
        self._internal_faces = kwargs.get('_internal_faces', None)

        self._face_ids = None

        self.topo_done = False
        self.face_side_topo_done = False

        self.terrain_height = kwargs.get('terrain_height', 0)
        self._terrain = None
        self._sky = None
        self.terrain = kwargs.get('terrain', None)
        self.sky = kwargs.get('sky', None)

        logger.debug(f'Created new scene {self.name}; {self.id}')

    @property
    def terrain(self):
        if self._terrain is None:
            self.terrain = self.generate_terrain()
        return self._terrain

    @terrain.setter
    def terrain(self, value):
        self._terrain = value

    @property
    def sky(self):
        if self._sky is None:
            self.sky = self.generate_sky()
        return self.sky

    @sky.setter
    def sky(self, value):
        self._sky = value

    @property
    def hull_faces(self):
        if self._hull_faces is None:
            if not self.topo_done:
                self.create_topology()
            self._hull_faces = [x for x in self.faces if x.hull_face]
        return self._hull_faces

    @property
    def internal_faces(self):
        if self._internal_faces is None:
            if not self.topo_done:
                self.create_topology()
            self._internal_faces = [x for x in self.faces if x.internal_faces]
        return self._internal_faces

    @property
    def hull_mesh(self):
        if self._hull_mesh is None:
            self.hull_mesh = self.create_hull_surface_mesh()
        return self._hull_mesh

    @hull_mesh.setter
    def hull_mesh(self, value):
        self._hull_mesh = value

    @property
    def face_ids(self):
        if self._face_ids is None:
            self._face_ids = np.array([x.id for x in self.faces])
        return self._face_ids

    @property
    def faces_with_construction(self):
        return [x for x in self.faces if (x.construction is not None)]

    @property
    def faces_with_undefined_construction(self):
        return [x for x in self.faces if (x.construction is None)]

    @property
    def walls(self):
        return [x for x in self.faces_with_construction if (not x.construction.is_window)]

    @property
    def windows(self):
        return [x for x in self.faces_with_construction if x.construction.is_window]

    @property
    def mesh(self):
        if self._mesh is None:
            self.mesh = self.create_mesh(dim=3)
        return self._mesh

    @mesh.setter
    def mesh(self, value):
        self._mesh = value

    @property
    def surface_mesh(self):
        if self._surface_mesh is None:
            self.surface_mesh = self.create_surface_mesh()
        return self._surface_mesh

    @surface_mesh.setter
    def surface_mesh(self, value):
        self._surface_mesh = value

    def create_hull_surface_mesh(self):

        logger.info(f'Scene: {self.name}; {self.id}: creating hull surface mesh...')

        try:
            mesh = generate_surface_mesh(vertices=self.vertices,
                                         edges=self.edges,
                                         edge_loops=self.edge_loops,
                                         faces=self.hull_faces,
                                         model_name=str(self.id),
                                         lc=self.mesh_size,
                                         min_size=self.mesh_min_size,
                                         max_size=self.mesh_max_size,
                                         method=self.surface_mesh_method)

        except Exception as e:
            logger.error(f'{self.name}; {self.id}: Error while creating hull surface mesh:\n{e}\n{traceback.format_exc()}\n{sys.exc_info()[2]}')
            return

        logger.info(f'{self.name}; {self.id}: hull surface mesh creation successful')

        return mesh

    def create_surface_mesh(self, *args, **kwargs):

        vertices = kwargs.get('faces', self.vertices)
        edges = kwargs.get('edges', self.edges)
        edge_loops = kwargs.get('edge_loops', self.edge_loops)
        faces = kwargs.get('faces', self.faces)

        add_mesh_properties = kwargs.get('add_mesh_properties', True)

        mesh_size_from_faces = kwargs.get('mesh_size_from_faces', True)
        method = kwargs.get('method', self.surface_mesh_method)
        mesh_size = kwargs.get('mesh_size', self.mesh_size)
        min_size = kwargs.get('min_size', self.mesh_min_size)
        max_size = kwargs.get('max_size', self.mesh_max_size)

        logger.info(f'Scene: {self.name}; {self.id}: creating surface mesh:')

        try:
            mesh = generate_surface_mesh(vertices=vertices,
                                         edges=edges,
                                         edge_loops=edge_loops,
                                         faces=faces,
                                         model_name=str(self.id),
                                         lc=mesh_size,
                                         min_size=min_size,
                                         max_size=max_size,
                                         method=method,
                                         mesh_size_from_faces=mesh_size_from_faces)

        except Exception as e:
            logger.error(f'{self.name}; {self.id}: Error while creating surface mesh:\n{e}\n{traceback.format_exc()}\n{sys.exc_info()[2]}')
            return

        if (mesh is not None) and add_mesh_properties:
            mesh = self.add_mesh_properties(mesh)

        logger.info(f'Scene: {self.name}; {self.id}: surface mesh creation successful')

        return mesh

    def create_mesh(self, *args, **kwargs):

        dim = kwargs.get('dim', 3)

        vertices = kwargs.get('faces', self.vertices)
        edges = kwargs.get('edges', self.edges)
        edge_loops = kwargs.get('edge_loops', self.edge_loops)
        faces = kwargs.get('faces', self.faces)
        volumes = kwargs.get('volumes', self.volumes)

        add_mesh_properties = kwargs.get('add_mesh_properties', True)

        mesh_size = kwargs.get('mesh_size', self.mesh_size)
        min_size = kwargs.get('min_size', self.mesh_min_size)
        max_size = kwargs.get('max_size', self.mesh_max_size)
        mesh_size_from_faces = kwargs.get('mesh_size_from_faces', self.mesh_max_size)

        logger.info(f'Scene: {self.name}; {self.id}: creating volume mesh:')

        try:
            mesh = generate_mesh(vertices=vertices,
                                 edges=edges,
                                 edge_loops=edge_loops,
                                 faces=faces,
                                 volumes=volumes,
                                 model_name=str(self.id),
                                 lc=mesh_size,
                                 min_size=min_size,
                                 max_size=max_size,
                                 dim=dim,
                                 mesh_size_from_faces=mesh_size_from_faces)
        except Exception as e:
            logger.error(f'Scene {self.name}; {self.id}: Error while creating volume mesh:\n{e}')
            return

        if (mesh is not None) and add_mesh_properties:
            mesh = self.add_mesh_properties(mesh)

        logger.info(f'Scene: {self.name}; {self.id}: volume mesh creation successful')

        return mesh

    def export_face_mesh_vtk(self, face, filename=None):

        import meshio

        if filename is None:
            filename = face.name + '.vtk'

        # replace Umlaute
        special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}
        filename = filename.translate(special_char_map)

        points = self.mesh.points
        cells = [("triangle",
                  self.mesh.cells[1].data[self.mesh.cell_sets[str(face.id)][1], :])]

        mesh = meshio.Mesh(
            points,
            cells
        )
        mesh.write(
            filename,  # str, os.PathLike, or buffer/open file
            # file_format="vtk",  # optional if first argument is a path; inferred from extension
        )

    def add_mesh_properties(self, mesh=None):

        try:
            tri_mesh = Trimesh(vertices=mesh.points,
                               faces=mesh.cells_dict['triangle'])
        except Exception as e:
            raise e

        logger.info(f'Scene: {self.name}; {self.id}: adding properties to surface mesh...')

        if mesh is None:
            mesh = self.mesh

        if not self.topo_done:
            self.create_topology()

        materials_ids = {}
        room_ids = {}
        room_id = 0
        mat_id = 0

        # num_elem_types = mesh.cells.__len__()
        tri_elem_type_index = [i for i, x in enumerate(mesh.cells) if x.type == 'triangle'][0]

        mesh.cells = [mesh.cells[tri_elem_type_index]]

        material_data = np.full(mesh.cells[0].__len__(), np.NaN, dtype=float)
        opaque = np.full(mesh.cells[0].__len__(), np.NaN, dtype=float)
        side1_zone = np.full(mesh.cells[0].__len__(), np.NaN, dtype=float)
        side2_zone = np.full(mesh.cells[0].__len__(), np.NaN, dtype=float)
        hull_face = np.full(mesh.cells[0].__len__(), 1, dtype=float)
        internal_face = np.full(mesh.cells[0].__len__(), 0, dtype=float)
        g_value = np.full(mesh.cells[0].__len__(), 0, dtype=float)
        eps = np.full(mesh.cells[0].__len__(), 0, dtype=float)
        foi = np.full(mesh.cells[0].__len__(), 0, dtype=float)
        area = tri_mesh.area_faces
        normals = tri_mesh.face_normals

        for key, value in mesh.cell_sets.items():
            res = np.argwhere(self.face_ids == int(key))
            if res:
                face_id = res[0, 0]
            else:
                continue
            # face_id = np.argwhere(self.face_ids == int(key))[0, 0]
            face = self.faces[face_id]
            cell_ids = value[tri_elem_type_index]

            g_value[cell_ids] = face.g_value
            eps[cell_ids] = face.eps

            hull_face[cell_ids] = int(face.hull_face)
            internal_face[cell_ids] = int(face.internal_face)

            foi[cell_ids] = int(face.foi)

            room1 = face.side_1_volume
            if room1 is not None:
                if room1 not in room_ids.keys():
                    room_ids[room1] = room_id
                    room_id += 1
                side1_zone[cell_ids] = room_ids[room1]

            room2 = face.side_2_volume
            if room2 is not None:
                if room2 not in room_ids.keys():
                    room_ids[room2] = room_id
                    room_id += 1
                side2_zone[cell_ids] = room_ids[room2]

            construction = self.faces[face_id].construction
            if construction is None:
                logger.warning(f'face without construction: {face.name}, ID: {face.id}')
                material_data[cell_ids] = np.NaN
                opaque[cell_ids] = 1
            else:
                if construction not in materials_ids.keys():
                    materials_ids[construction] = mat_id
                    mat_id += 1
                material_data[cell_ids] = materials_ids[construction]
                opaque[cell_ids] = int(not construction.is_window)

        # handle terrain and sky
        if self._terrain is not None:
            for face in self._terrain.faces:
                if str(face.id) in mesh.cell_sets.keys():
                    value = mesh.cell_sets[str(face.id)]
                    cell_ids = value[tri_elem_type_index]
                    hull_face[cell_ids] = 1
                    internal_face[cell_ids] = 0
                    opaque[cell_ids] = 1
                    foi[cell_ids] = 0

        if self._sky is not None:
            for face in self._sky.faces:
                if str(face.id) in mesh.cell_sets.keys():
                    value = mesh.cell_sets[str(face.id)]
                    cell_ids = value[tri_elem_type_index]
                    hull_face[cell_ids] = 0
                    internal_face[cell_ids] = 0
                    opaque[cell_ids] = 1

        mesh.cell_data['material'] = [material_data]
        mesh.cell_data['opaque'] = [opaque]
        mesh.cell_data['hull_face'] = [hull_face]
        mesh.cell_data['internal_face'] = [internal_face]
        mesh.cell_data['side1_zone'] = [side1_zone]
        mesh.cell_data['side2_zone'] = [side2_zone]
        mesh.cell_data['g_value'] = [g_value]
        mesh.cell_data['eps'] = [eps]
        mesh.cell_data['foi'] = [foi]

        mesh.cell_data['area'] = [area]
        mesh.cell_data['normals'] = [normals]

        return mesh

    def export_mesh(self, file_name):
        if self.mesh is None:
            logger.error(f'{self}: mesh is None')
            return
        self.mesh.write(file_name)

    def export_surf_mesh(self, file_name):
        if self.surface_mesh is None:
            logger.error(f'{self}: surface_mesh is None')
            return
        self.surface_mesh.write(file_name)

    def create_topology(self):

        logger.info(f'Scene: {self.name}; {self.id}: creating topology')

        # faces = copy(self.faces)
        # [faces.extend(x.faces) for x in self.volumes]
        # occurrences = Counter(faces)
        #
        # hull_faces = [k for (k, v) in occurrences.items() if v in [1, 2]]
        # inside_faces = [k for (k, v) in occurrences.items() if v == 3]
        # # no_occurance = [k for (k, v) in occurrences.items() if v == 1]
        # # np.array([x.hull_face for x in self.faces])
        #
        # for face in hull_faces:
        #     face.hull_face = True
        #     face.internal_face = True
        #
        # for face in inside_faces:
        #     face.internal_face = True
        #     face.hull_face = False

        self.topo_done = True

        logger.info(f'Scene: {self.name}; {self.id}: Topology creation successful')

        # np.array([x.hull_face for x in self.faces])
        # generate_surface_mesh(faces=no_occurance, method='robust').write('no_occurrence.vtk')

    def generate_face_side_topology(self):

        logger.info(f'Scene: {self.name}; {self.id}: creating face-side topology')

        # for volume in self.volumes:
        #     if not volume.is_watertight:
        #         logger.error(f'{self.name}, {self.id}: Volume is not watertight')
        #
        #     if not volume.is_watertight:
        #         trimesh.repair.fix_winding(volume.surface_trimesh)
        #
        #     surface_normals = np.array([x.normal for x in volume.faces])
        #     first_cell_ids = [volume.surface_mesh.cell_sets[str(x.id)][1][0] for x in volume.faces]
        #     origins = volume.surface_trimesh.triangles_center[first_cell_ids, :]
        #
        #     inside = volume.surface_trimesh.contains(origins + 0.05 * surface_normals)
        #
        #     for i, face in enumerate(volume.faces):
        #         if inside[i]:
        #             face.side2 = volume
        #         else:
        #             face.side1 = volume

        self.face_side_topo_done = True

    def generate_terrain(self, mesh_size=999, mesh_size_from_faces=False):

        logger.info(f'Scene: {self.name}; {self.id}: creating terrain...')

        hull_mesh = generate_surface_mesh(vertices=self.vertices,
                                          edges=self.edges,
                                          edge_loops=self.edge_loops,
                                          faces=self.hull_faces,
                                          model_name=str(self.id),
                                          lc=mesh_size,
                                          min_size=self.mesh_min_size,
                                          max_size=self.mesh_max_size,
                                          method='robust',
                                          mesh_size_from_faces=mesh_size_from_faces)

        terrain = generate_terrain(hull_mesh, self.terrain_height, mesh_size=50)
        logger.info(f'Scene: {self.name}; {self.id}: Terrain generation successful')

        return terrain

    def add_terrain(self):

        logger.info(f'Scene: {self.name}; {self.id}: adding terrain...')

        self.vertices.extend(self.terrain.vertices)
        self.edges.extend(self.terrain.edges)
        self.edge_loops.extend(self.terrain.edge_loops)
        self.faces.extend(self.terrain.faces)

        logger.info(f'Scene: {self.name}; {self.id}: terrain added successful')

    def generate_sky(self):

        logger.info(f'Scene: {self.name}; {self.id}: generating sky')

        return generate_sky(self.hull_mesh, self.terrain_height)

    def add_sky(self):

        logger.info(f'Scene: {self.name}; {self.id}: adding sky')

        self.vertices.extend(self.sky.vertices)
        self.edges.extend(self.sky.edges)
        self.edge_loops.extend(self.sky.edge_loops)
        self.faces.extend(self.sky.faces)

    def generate_shading_analysis_mesh(self, mesh_size=99999, add_terrain=True):

        logger.info(f'Scene: {self.name}; {self.id}: generating mesh for shading analysis...')

        if bool(add_terrain):
            if self._terrain is None:
                _ = self.terrain

            # generate surface mesh:
            faces = {*self.faces, *self.terrain.faces}
        else:
            faces = {*self.faces}

        edge_loops = set()
        {(edge_loops.add(x.boundary), edge_loops.update(x.holes)) for x in faces}
        edges = set()
        [edges.update(x.edges) for x in edge_loops]
        vertices = set()
        [vertices.update([x.vertices[0], x.vertices[1]]) for x in edges]

        mesh = self.create_surface_mesh(vertices=vertices,
                                        edges=edges,
                                        edge_loops=edge_loops,
                                        faces=faces,
                                        model_name=str(self.id),
                                        mesh_size=mesh_size,
                                        min_size=mesh_size,
                                        max_size=mesh_size,
                                        method='robust',
                                        mesh_size_from_faces=False,
                                        add_mesh_properties=False)

        if mesh is None:
            logger.error(f"Scene: {self.name}; {self.id}: Could not create mesh for shading analysis.\nRetry with very robust method...")

            mesh = self.create_surface_mesh(vertices=vertices,
                                            edges=edges,
                                            edge_loops=edge_loops,
                                            faces=faces,
                                            model_name=str(self.id),
                                            mesh_size=mesh_size,
                                            min_size=mesh_size,
                                            max_size=mesh_size,
                                            method='very robust',
                                            mesh_size_from_faces=False,
                                            add_mesh_properties=False)

            if mesh is None:
                logger.error(f"Scene: {self.name}; {self.id}: Could not create mesh for shading analysis.")

        mesh = self.add_mesh_properties(mesh)

        logger.info(f'Scene: {self.name}; {self.id}: Mesh generation for shading analysis successful')

        return mesh

    def export_shading_analysis_mesh(self, file_name, mesh_size=9999):

        logger.info(f'Scene: {self.name}; {self.id}: exporting mesh for  mesh...')

        mesh = self.generate_shading_analysis_mesh(mesh_size=mesh_size)

        mesh.write(file_name)

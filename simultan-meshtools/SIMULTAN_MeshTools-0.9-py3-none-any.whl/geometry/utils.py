import pygmsh
from pygmsh.common.polygon import Polygon
import gmsh
import numpy as np
import logging
from pygmsh.helpers import extract_to_meshio
import trimesh
import vg

from GeometryViewer.Model.Geometry import GeometricOrientation

import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger('PySimultanRadiation')


def mesh_planar_face(face, mesh_size=0.1):

    with pygmsh.geo.Geometry() as geom:

        holes = None
        if face.holes.__len__() > 0:
            holes = [Polygon(geom, x.points,
                             holes=None,
                             mesh_size=mesh_size,
                             ) for x in face.holes]

        geom.add_polygon(
            face.points,
            holes=holes,
            mesh_size=mesh_size,
        )

        if face.holes.__len__() > 0:
            [geom.remove(x) for x in holes]

        mesh = geom.generate_mesh(dim=2, verbose=False)

    return mesh


def generate_mesh(*args, **kwargs):

    vertices = kwargs.get('vertices', [])
    edges = kwargs.get('edges', [])
    edge_loops = kwargs.get('edge_loops', [])
    faces = kwargs.get('faces', [])
    volumes = kwargs.get('volumes', [])
    model_name = kwargs.get('model_name', None)
    lc = kwargs.get('lc', 1)    # Node default mesh size
    min_size = kwargs.get('min_size', 0.5)
    max_size = kwargs.get('max_size', 10)
    verbose = kwargs.get('verbose', False) # show gmsh-output
    mesh_size_from_faces = kwargs.get('mesh_size_from_faces', True)
    dim = kwargs.get('dim', 3)  # dimension of the mesh: 2:surface-mesh, 3:volume-mesh

    logger.info((f'Generating mesh:\n'
                 f'Number Vertices: {vertices.__len__()}\n'
                 f'Number Edges: {edges.__len__()}\n'
                 f'Number EdgeLoops: {edge_loops.__len__()}\n'
                 f'Number faces: {faces.__len__()}\n'
                 f'Number volumes: {volumes.__len__()}\n'
                 f'dim: {dim}\n'
                 f'....'
                 ))

    gmsh.initialize([])
    gmsh.model.add(f'{model_name}')

    id_getter = kwargs.get('id_getter', lambda x: x.id)

    try:

        geo = gmsh.model.geo

        vertex_lookup = dict(zip(vertices, range(vertices.__len__())))
        point_mesh_sizes = np.full(vertices.__len__(), lc)

        if mesh_size_from_faces:
            for face in faces:
                try:
                    vertex_indices = np.array([vertex_lookup[x] for x in face.vertices])
                    point_mesh_sizes[vertex_indices[point_mesh_sizes[vertex_indices] > face.mesh_size]] = face.mesh_size
                except Exception as e:
                    logger.error(f'Error adding mesh_size for face {face.name}, {face.id}: {e}')

        lc_p = lc
        for i, vertex in enumerate(vertices):
            if mesh_size_from_faces:
                lc_p = point_mesh_sizes[i]
            geo.addPoint(vertex.position[0], vertex.position[1], vertex.position[2], lc_p, i+1)

        gmsh.model.geo.synchronize()

        edge_lookup = dict(zip(edges, range(edges.__len__())))
        for i, edge in enumerate(edges):
            try:
                geo.addLine(vertex_lookup[edge.vertices[0]]+1, vertex_lookup[edge.vertices[1]]+1, i+1)
            except Exception as e:
                logger.error(f'Error adding edge {edge}:\n{e}')
        gmsh.model.geo.synchronize()

        edge_loop_lookup = dict(zip(edge_loops, range(edge_loops.__len__())))
        for i, edge_loop in enumerate(edge_loops):
            try:
                if isinstance(edge_loop.edge_orientations[0], GeometricOrientation):
                    edge_orientations = [1 if x == GeometricOrientation.Forward else -1 for x in edge_loop.edge_orientations]
                else:
                    edge_orientations = edge_loop.edge_orientations

                ids = np.array([edge_lookup[x]+1 for x in edge_loop.edges]) * np.array(edge_orientations)
                geo.addCurveLoop(ids, i+1)
            except Exception as e:
                logger.error(f'Error creating CurveLoop for {edge_loop.id}, {edge_loop.gmsh_id}:\n{e}')
        gmsh.model.geo.synchronize()

        face_lookup = dict(zip(faces, range(faces.__len__())))
        for i, face in enumerate(faces):
            try:
                edge_loop_ids = [edge_loop_lookup[face.boundary]+1] + [edge_loop_lookup[x]+1 for x in face.holes]
                geo.addPlaneSurface(edge_loop_ids, i+1)
            except Exception as e:
                logger.error(f'Error creating CurveLoop for {face.name},{face.id}, {face.gmsh_id}:\n{e}')
        gmsh.model.geo.synchronize()

        volume_lookup = dict(zip(volumes, range(volumes.__len__())))
        for i, volume in enumerate(volumes):
            geo.addSurfaceLoop([face_lookup[x]+1 for x in faces], i+1)
            geo.addVolume([i+1], i+1)

        gmsh.model.geo.synchronize()

        # add physical domains for faces:
        for face in faces:
            ps = gmsh.model.addPhysicalGroup(2, [face_lookup[face]+1])
            gmsh.model.setPhysicalName(2, ps, str(id_getter(face)))

        # add physical domains for volumes:
        for volume in volumes:
            ps = gmsh.model.addPhysicalGroup(3, [volume_lookup[volume]+1])
            gmsh.model.setPhysicalName(3, ps, str(volume.id))

        gmsh.model.geo.synchronize()

        gmsh.option.setNumber("General.Terminal", 1 if verbose else 0)
        gmsh.option.setNumber("Mesh.MeshSizeMin", min_size)
        gmsh.option.setNumber("Mesh.MeshSizeMax", max_size)

        # Finally, while the default "Frontal-Delaunay" 2D meshing algorithm
        # (Mesh.Algorithm = 6) usually leads to the highest quality meshes, the
        # "Delaunay" algorithm (Mesh.Algorithm = 5) will handle complex mesh size fields
        # better - in particular size fields with large element size gradients:
        # gmsh.option.setNumber("Mesh.Algorithm", 5)

        if volumes.__len__() == 0:
            dim = 2

        gmsh.model.mesh.generate(dim)
        mesh = extract_to_meshio()

    except Exception as e:
        logger.error(f'Error creating mesh for {model_name}:\n{e}')
        gmsh.finalize()
        raise e

    gmsh.finalize()

    if dim == 2:
        logger.info((f'Mesh generation successful:\n'
                     f'Number Vertices: {mesh.points.shape[0]}\n'
                     f"Number Triangles: {mesh.cells_dict['triangle'].shape[0]}\n"
                     ))
    elif dim == 3:
        logger.info((f'Mesh generation successful:\n'
                     f'Number Vertices: {mesh.points.shape[0]}\n'
                     f"Number Triangles: {mesh.cells_dict['triangle'].shape[0]}\n"
                     f"Number Tetra: {mesh.cells_dict['tetra'].shape[0]}\n"
                     ))

    return mesh


def generate_surface_mesh(*args, **kwargs):

    vertices = kwargs.get('vertices', [])
    edges = kwargs.get('edges', [])
    edge_loops = kwargs.get('edge_loops', [])
    faces = kwargs.get('faces', [])
    model_name = kwargs.get('model_name', None)
    lc = kwargs.get('lc', 1)
    min_size = kwargs.get('min_size', 0.5)
    max_size = kwargs.get('max_size', 10)
    verbose = kwargs.get('verbose', False)
    mesh_size_from_faces = kwargs.get('mesh_size_from_faces', True)
    method = kwargs.get('method', 'robust')

    logger.info((f'Generating surface mesh:\n'
                 f'Number Vertices: {vertices.__len__()}\n'
                 f'Number Edges: {edges.__len__()}\n'
                 f'Number EdgeLoops: {edge_loops.__len__()}\n'
                 f'Number faces: {faces.__len__()}\n'
                 f'Method: {method}\n'
                 f'....'
                 ))

    if method == 'robust':
        with pygmsh.geo.Geometry() as geom:
            model = geom.__enter__()

            polys = {}

            for face in faces:

                holes = []

                if mesh_size_from_faces:
                    mesh_size = face.mesh_size
                else:
                    mesh_size = lc

                if face.holes.__len__() > 0:

                    holes = [geom.add_polygon(x.points,
                                              holes=None,
                                              mesh_size=mesh_size,
                                              ) for x in face.holes]

                poly = geom.add_polygon(
                    face.points,
                    holes=holes,
                    mesh_size=mesh_size,
                )
                polys[str(face.id)] = poly

                if face.holes.__len__() > 0:
                    [geom.remove(x) for x in holes]

            [model.add_physical(value, key) for key, value in polys.items()]
            mesh = geom.generate_mesh(dim=2, verbose=verbose)

    elif method == 'very robust':

        tri_msh = trimesh.Trimesh()

        for face in faces:
            tri_msh = trimesh.util.concatenate([tri_msh, face.trimesh])

    else:
        mesh = generate_mesh(vertices=vertices,
                             edges=edges,
                             edge_loops=edge_loops,
                             faces=faces,
                             model_name=model_name,
                             lc=lc,                      # Node default mesh size
                             dim=2,                     # dimension of the mesh: 2:surface-mesh, 3:volume-mesh
                             min_size=min_size,
                             max_size=max_size,
                             verbose=verbose,           # show gmsh-output
                             mesh_size_from_faces=mesh_size_from_faces)

    logger.info((f'Surface mesh generation successful:\n'
                 f'Number Vertices: {mesh.points.shape[0]}\n'
                 f"Number Triangles: {mesh.cells_dict['triangle'].shape[0]}\n"
                 ))

    return mesh


def generate_terrain(hull_mesh, terrain_height, border_dist=150, mesh_size=50):
    from .base_geometry import Vertex, Edge, EdgeLoop, Face, Terrain

    terrain = Terrain(vertices=[],
                      edges=[],
                      edge_loops=[],
                      faces=[])

    surf_mesh = trimesh.Trimesh(vertices=hull_mesh.points,
                                faces=hull_mesh.cells[1].data)

    surf_mesh.remove_unreferenced_vertices()
    surf_mesh.merge_vertices()
    surf_mesh.remove_duplicate_faces()
    trimesh.repair.fix_winding(surf_mesh)

    path = surf_mesh.section(np.array([0, 0, 1]), np.array([0, 0, terrain_height]))

    # if path is None:
    #     return terrain

    # create terrain face:

    # x_ext = surf_mesh.bounds[1, 0] - surf_mesh.bounds[0, 0]
    # y_ext = surf_mesh.bounds[1, 1] - surf_mesh.bounds[0, 1]

    # outer loop:
    p0 = Vertex(position=np.array([surf_mesh.bounds[0, 0] - border_dist,
                                   surf_mesh.bounds[0, 1] - border_dist,
                                   terrain_height]))

    p1 = Vertex(position=np.array([surf_mesh.bounds[1, 0] + border_dist,
                                   surf_mesh.bounds[0, 1] - border_dist,
                                   terrain_height]))

    p2 = Vertex(position=np.array([surf_mesh.bounds[1, 0] + border_dist,
                                   surf_mesh.bounds[1, 1] + border_dist,
                                   terrain_height]))

    p3 = Vertex(position=np.array([surf_mesh.bounds[0, 0] - border_dist,
                                   surf_mesh.bounds[1, 1] + border_dist,
                                   terrain_height]))

    e0 = Edge(vertices=[p0, p1])
    e1 = Edge(vertices=[p1, p2])
    e2 = Edge(vertices=[p2, p3])
    e3 = Edge(vertices=[p3, p0])

    el0 = EdgeLoop(edges=[e0, e1, e2, e3], edge_orientations=[1] * 4)

    holes = []
    all_edges = [e0, e1, e2, e3]
    edge_loops = [el0]

    # simplify path:
    points = []
    if path is not None:

        planar_path, to_3D = path.to_planar()
        simple_path = planar_path.simplify()

        path = simple_path.to_3D(to_3D)

        # holes
        points = [None] * path.vertices.shape[0]
        for i, vertex in enumerate(path.vertices):
            points[i] = Vertex(position=np.array(vertex))

        for line in path.entities:
            # create edges:
            if not line.closed:
                continue

            more_simple_path = simplify_path(path.vertices, line.points)

            # edges = [None] * (line.nodes.shape[0])
            # for i, node in enumerate(line.nodes):
            #    edges[i] = Edge(vertices=[points[node[0]], points[node[1]]])
            edges = [None] * (more_simple_path.__len__()-1)
            for i in range(more_simple_path.__len__()-1):
                edges[i] = Edge(vertices=[points[more_simple_path[i]], points[more_simple_path[i+1]]])

            # edges[i+1] = Edge(vertices=[points[more_simple_path[-1]], points[more_simple_path[0]]])

            all_edges.extend(edges)
            edge_loop = EdgeLoop(edges=edges, edge_orientations=[1] * edges.__len__())
            edge_loops.append(edge_loop)
            holes.append(edge_loop)

    terrain_face = Face(name='Terrain', boundary=el0, holes=holes, mesh_size=mesh_size, foi=False)

    terrain.vertices = [*points, p0, p1, p2, p3]
    terrain.edges = all_edges
    terrain.edge_loops = edge_loops
    terrain.faces = [terrain_face]

    # terrain = Terrain(vertices=[*points, p0, p1, p2, p3],
    #                   edges=all_edges,
    #                   edge_loops=edge_loops,
    #                   faces=[terrain_face])

    return terrain


def generate_sky(hull_mesh, terrain_height, border_dist=150):

    from .base_geometry import Vertex, Edge, EdgeLoop, Face, Sky

    surf_mesh = trimesh.Trimesh(vertices=hull_mesh.points,
                                faces=hull_mesh.cells[1].data)

    # outer loop:


    """
    z = border_dist:
    
    ^ y
    |       
    |   p3 -----------------p2
    |   |                   |
    |   |                   |
    |   |                   |
    |   p0 -----------------p1
    |
    -------------------------------> x
    
    
    z = border_dist:
    
    ^ y
    |       
    |   p7 -----------------p6
    |   |                   |
    |   |                   |
    |   |                   |
    |   p4 -----------------p5
    |
    -------------------------------> x
    
    """
    p0 = Vertex(position=np.array([surf_mesh.bounds[0, 0] - border_dist,
                                   surf_mesh.bounds[0, 1] - border_dist,
                                   terrain_height]))

    p1 = Vertex(position=np.array([surf_mesh.bounds[1, 0] + border_dist,
                                   surf_mesh.bounds[0, 1] - border_dist,
                                   terrain_height]))

    p2 = Vertex(position=np.array([surf_mesh.bounds[1, 0] + border_dist,
                                   surf_mesh.bounds[1, 1] + border_dist,
                                   terrain_height]))

    p3 = Vertex(position=np.array([surf_mesh.bounds[0, 0] - border_dist,
                                   surf_mesh.bounds[1, 1] + border_dist,
                                   terrain_height]))

    p4 = Vertex(position=np.array([surf_mesh.bounds[0, 0] - border_dist,
                                   surf_mesh.bounds[0, 1] - border_dist,
                                   surf_mesh.bounds[1, 2] + border_dist]))

    p5 = Vertex(position=np.array([surf_mesh.bounds[1, 0] + border_dist,
                                   surf_mesh.bounds[0, 1] - border_dist,
                                   surf_mesh.bounds[1, 2] + border_dist]))

    p6 = Vertex(position=np.array([surf_mesh.bounds[1, 0] + border_dist,
                                   surf_mesh.bounds[1, 1] + border_dist,
                                   surf_mesh.bounds[1, 2] + border_dist]))

    p7 = Vertex(position=np.array([surf_mesh.bounds[0, 0] - border_dist,
                                   surf_mesh.bounds[1, 1] + border_dist,
                                   surf_mesh.bounds[1, 2] + border_dist]))

    # face 1
    f1e0 = Edge(vertices=[p0, p1])
    f1e1 = Edge(vertices=[p1, p5])
    f1e2 = Edge(vertices=[p5, p4])
    f1e3 = Edge(vertices=[p4, p0])

    f1el = EdgeLoop(edges=[f1e0, f1e1, f1e2, f1e3], edge_orientations=[1] * 4)
    f1 = Face(name='Sky1', boundary=f1el, mesh_size=20, foi=False)

    # face 2
    f2e0 = Edge(vertices=[p1, p2])
    f2e1 = Edge(vertices=[p2, p6])
    f2e2 = Edge(vertices=[p6, p5])
    # f2e3 = Edge(vertices=[p5, p1])

    f2el = EdgeLoop(edges=[f2e0, f2e1, f2e2, f1e1], edge_orientations=[1, 1, 1, -1])
    f2 = Face(name='Sky2', boundary=f2el, mesh_size=20, foi=False)

    # face 3
    f3e0 = Edge(vertices=[p2, p3])
    f3e1 = Edge(vertices=[p3, p7])
    f3e2 = Edge(vertices=[p7, p6])
    # f3e3 = Edge(vertices=[p6, p2])

    f3el = EdgeLoop(edges=[f3e0, f3e1, f3e2, f2e1], edge_orientations=[1, 1, 1, -1])
    f3 = Face(name='Sky3', boundary=f3el, mesh_size=20, foi=False)

    # face 4
    f4e0 = Edge(vertices=[p3, p0])
    f4e1 = Edge(vertices=[p0, p4])
    f4e2 = Edge(vertices=[p4, p7])
    # f4e3 = Edge(vertices=[p7, p3])

    f4el = EdgeLoop(edges=[f4e0, f4e1, f4e2, f3e1], edge_orientations=[1, 1, 1, -1])
    f4 = Face(name='Sky4', boundary=f4el, mesh_size=20, foi=False)

    # face 5
    # f5e0 = Edge(vertices=[p4, p5])
    # f5e1 = Edge(vertices=[p0, p4])
    # f5e2 = Edge(vertices=[p4, p7])
    # f5e3 = Edge(vertices=[p7, p3])

    f5el = EdgeLoop(edges=[f1e2, f2e2, f3e2, f4e2], edge_orientations=[-1, -1, -1, -1])
    f5 = Face(name='Sky5', boundary=f5el, mesh_size=20, foi=False)

    sky = Sky(vertices=[p0, p1, p2, p3, p4, p5, p6, p7],
              edges=[f1e0, f1e1, f1e2, f1e3,
                     f2e0, f2e1, f2e2,
                     f3e0, f3e1, f3e2,
                     f4e0, f4e1, f4e2,
                     f5el],
              edge_loops=[f1el, f2el, f3el, f4el],
              faces=[f1, f2, f3, f4, f5])

    return sky


def simplify_path(vertices, points):

    new_points = [points[0]]

    loop_points = points[1:]

    for i, point in enumerate(loop_points[0:-1]):

        length = np.linalg.norm(vertices[new_points[-1], :] - vertices[point])

        if length < 0.05:
            continue

        v1 = vertices[new_points[-1]] - vertices[point]
        v2 = vertices[new_points[-1]] - vertices[loop_points[i+1]]

        angle = vg.angle(v1 / np.linalg.norm(v1), v2 / np.linalg.norm(v2), assume_normalized=True)

        if angle < 1:
            continue

        new_points.append(point)

    new_points.append(points[0])

    return new_points


def cell_data_to_point_data(mesh):

    pass


def calc_aoi(irradiation_vector, face_normals, deg=True):
    if deg:
        return np.rad2deg(np.arccos(
            np.clip(trimesh.util.diagonal_dot(face_normals, irradiation_vector['irradiation_vector']), -1.0, 1.0)))
    else:
        return np.arccos(
            np.clip(trimesh.util.diagonal_dot(face_normals, irradiation_vector['irradiation_vector']), -1.0, 1.0))


if __name__ == '__main__':

    pass

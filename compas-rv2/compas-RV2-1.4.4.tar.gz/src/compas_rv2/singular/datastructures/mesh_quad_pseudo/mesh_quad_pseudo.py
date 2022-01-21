from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.utilities import geometric_key

from ..mesh_quad import QuadMesh
from compas_rv2.singular.utilities import list_split


class PseudoQuadMesh(QuadMesh):

    def __init__(self):
        super(PseudoQuadMesh, self).__init__()
        self.attributes['face_pole'] = {}

    @classmethod
    def from_vertices_and_faces_with_poles(cls, vertices, faces, poles=[]):
        pole_map = tuple([geometric_key(pole) for pole in poles])
        mesh = cls.from_vertices_and_faces(vertices, faces)
        for fkey in mesh.faces():
            face_vertices = mesh.face_vertices(fkey)
            if len(face_vertices) == 3:
                mesh.attributes['face_pole'][fkey] = face_vertices[0]
                for vkey in face_vertices:
                    if geometric_key(mesh.vertex_coordinates(vkey)) in pole_map:
                        mesh.attributes['face_pole'].update({fkey: vkey})
                        break
        return mesh

    @classmethod
    def from_vertices_and_faces_with_face_poles(cls, vertices, faces, face_poles={}):
        mesh = cls.from_vertices_and_faces(vertices, faces)
        mesh.attributes['face_pole'] = face_poles
        return mesh

    def poles(self):
        return list(set(self.attributes['face_pole'].values()))

    def is_pole(self, vkey):
        return vkey in set(self.poles())

    def is_face_pseudo_quad(self, fkey):
        return fkey in set(self.attributes['face_pole'].keys())

    def is_vertex_pole(self, vkey):
        return vkey in set(self.attributes['face_pole'].values())

    def is_vertex_full_pole(self, vkey):
        return all([self.is_face_pseudo_quad(fkey) for fkey in self.vertex_faces(vkey)])

    def is_vertex_partial_pole(self, vkey):
        return self.is_vertex_pole(vkey) and not self.is_vertex_full_pole(vkey)

    def vertex_pole_faces(self, vkey):
        return [fkey for fkey, pole in self.attributes['face_pole'].items() if pole == vkey]

    def face_opposite_edge(self, u, v):
        """Returns the opposite edge in the quad face.

        Parameters
        ----------
        u : int
            The identifier of the edge start.
        v : int
            The identifier of the edge end.

        Returns
        -------
        (w, x) : tuple
            The opposite edge.

        """

        fkey = self.halfedge[u][v]
        # if quad
        if len(self.face_vertices(fkey)) == 4:
            w = self.face_vertex_descendant(fkey, v)
            x = self.face_vertex_descendant(fkey, w)
            return (w, x)
        # if pseudo quad
        if len(self.face_vertices(fkey)) == 3:
            pole = self.attributes['face_pole'][fkey]
            w = self.face_vertex_descendant(fkey, v)
            if u == pole:
                return (w, u)
            if v == pole:
                return (v, w)
            else:
                return (pole, pole)

    def collect_strip(self, u0, v0):
        """Returns all the edges in the strip of the input edge.

        Parameters
        ----------
        u : int
            The identifier of the edge start.
        v : int
            The identifier of the edge end.

        Returns
        -------
        strip : list
            The list of the edges in strip.
        """

        if self.halfedge[u0][v0] is None:
            u0, v0 = v0, u0

        edges = [(u0, v0)]

        count = self.number_of_edges()
        while count > 0:
            count -= 1

            u, v = edges[-1]
            w, x = self.face_opposite_edge(u, v)

            if (x, w) == edges[0]:
                break

            edges.append((x, w))

            if w == x or w not in self.halfedge[x] or self.halfedge[x][w] is None:
                edges = [(v, u) for u, v in reversed(edges)]
                u, v = edges[-1]
                if u == v or v not in self.halfedge[u] or self.halfedge[u][v] is None:
                    break

        return edges

    def collect_strips(self):
        """Collect the strip data.

        Returns
        -------
        strip : int
            The number of strips.

        """

        edges = [(u, v) if self.halfedge[u][v] is not None else (v, u) for u, v in self.edges()]

        nb_strip = -1
        while len(edges) > 0:
            nb_strip += 1

            u0, v0 = edges.pop()
            strip_edges = self.collect_strip(u0, v0)
            self.attributes['strips'].update({nb_strip: strip_edges})

            for u, v in strip_edges:
                if u != v:
                    if (u, v) in edges:
                        edges.remove((u, v))
                    elif (v, u) in edges:
                        edges.remove((v, u))

        return self.strips(data=True)

    def has_strip_poles(self, skey):
        return self.attributes['strips'][skey][0][0] == self.attributes['strips'][skey][0][1] \
            or self.attributes['strips'][skey][-1][0] == self.attributes['strips'][skey][-1][1]

    def is_strip_closed(self, skey):
        """Output whether a strip is closed.

        Parameters
        ----------
        skey : hashable
            A strip key.

        Returns
        -------
        bool
            True if the strip is closed. False otherwise.

        """

        return not self.has_strip_poles(skey) and not self.is_edge_on_boundary(*self.attributes['strips'][skey][0])

    def is_vertex_singular(self, vkey):
        """Output whether a vertex is quad mesh singularity.

        Parameters
        ----------
        vkey : int
            The vertex key.

        Returns
        -------
        bool
            True if the vertex is a quad mesh singularity. False otherwise.

        """

        if self.is_vertex_pole(vkey):
            return True
        elif (self.is_vertex_on_boundary(vkey) and self.vertex_degree(vkey) != 3) \
                or (not self.is_vertex_on_boundary(vkey) and self.vertex_degree(vkey) != 4):
            return True

        else:
            return False

    def vertex_index(self, vkey):
        """Compute vertex index.

        Parameters
        ----------
        vkey : int
            The vertex key.

        Returns
        -------
        int
            Vertex index.

        """

        if self.vertex_degree(vkey) == 0:
            return 0

        if self.is_vertex_pole(vkey):
            if self.is_vertex_full_pole(vkey):
                if self.is_vertex_on_boundary(vkey):
                    return 1.0 / 2.0
                else:
                    return 1.0
            else:
                adapted_valency = sum([not self.is_face_pseudo_quad(fkey) for fkey in self.vertex_faces(vkey)])
                if self.is_vertex_on_boundary(vkey):
                    adapted_valency += 1
                regular_valency = 4.0 if not self.is_vertex_on_boundary(vkey) else 3.0
                return (regular_valency - adapted_valency) / 4.0
        else:
            regular_valency = 4.0 if not self.is_vertex_on_boundary(vkey) else 3.0
            return (regular_valency - self.vertex_degree(vkey)) / 4.0

    def strip_faces(self, skey):
        """Return the faces of a strip.

        Parameters
        ----------
        skey : hashable
            A strip key.

        Returns
        -------
        list
            The faces of the strip.

        """

        faces = []
        edges = self.strip_edges(skey)
        for i, (u, v) in enumerate(edges):
            if i == 0 and u == v:
                x, w = edges[1]
                faces.append(self.halfedge[w][x])
            elif i == len(edges) - 1 and u == v:
                pass
            else:
                if self.halfedge[u][v] is not None:
                    faces.append(self.halfedge[u][v])
        return faces

    def face_strips(self, fkey):
        """Return the two strips of a face.

        Parameters
        ----------
        fkey : hashable

        Returns
        -------
        list
            The two strips of the face.
        """

        if self.is_face_pseudo_quad(fkey):
            pole = self.attributes['face_pole'][fkey]
            # print(pole, fkey, self.face_vertices(fkey))
            u = self.face_vertex_descendant(fkey, pole)
            v = self.face_vertex_descendant(fkey, u)
            return [self.edge_strip((pole, u)), self.edge_strip((u, v))]
        else:
            return [self.edge_strip((u, v)) for u, v in list(self.face_halfedges(fkey))[:2]]

    def delete_face_in_strips(self, fkey):
        """Delete face in strips.

        Parameters
        ----------
        old_vkey : hashable
            The old vertex key.
        new_vkey : hashable
            The new vertex key.

        """

        self.attributes['strips'] = {skey: [(u, v) for u, v in self.strip_edges(skey) if u == v or (
            self.halfedge[u][v] != fkey and self.halfedge[v][u] != fkey)] for skey in self.strips()}

    def singularity_polyedges(self):
        """Collect the polyedges connected to singularities.

        Returns
        -------
        list
            The polyedges connected to singularities.

        """

        # poles = set(self.poles())
        # keep only polyedges connected to singularities or along the boundary
        polyedges = [polyedge for key, polyedge in self.polyedges(data=True)
                     if (self.is_vertex_singular(polyedge[0]) and not self.is_pole(polyedge[0]))
                     or (self.is_vertex_singular(polyedge[-1]) and not self.is_pole(polyedge[-1]))
                     or self.is_edge_on_boundary(polyedge[0], polyedge[1])]

        # get intersections between polyedges for split
        vertices = [vkey for polyedge in polyedges for vkey in set(polyedge)]
        split_vertices = [vkey for vkey in self.vertices() if vertices.count(vkey) > 1]

        # split singularity polyedges
        return [split_polyedge for polyedge in polyedges
                for split_polyedge in list_split(polyedge, [polyedge.index(vkey) for vkey in split_vertices if vkey in polyedge])]

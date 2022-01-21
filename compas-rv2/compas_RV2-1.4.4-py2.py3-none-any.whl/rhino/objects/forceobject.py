from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Point
from compas.geometry import Scale
from compas.geometry import Translation
from compas.geometry import Rotation
from compas.utilities import i_to_rgb

import compas_rhino

from .meshobject import MeshObject


__all__ = ["ForceObject"]


class ForceObject(MeshObject):
    """Scene object for RV2 force diagrams.
    """

    SETTINGS = {
        'layer': "RV2::ForceDiagram",
        'show.vertices': True,
        'show.edges': True,
        'color.vertices': [0, 255, 255],
        'color.vertices:is_fixed': [0, 255, 255],
        'color.edges': [0, 0, 255],
        'color.tension': [255, 0, 0]
    }

    @property
    def vertex_xyz(self):
        """dict : The view coordinates of the mesh object."""
        origin = Point(0, 0, 0)
        if self.anchor is not None:
            xyz = self.mesh.vertex_attributes(self.anchor, 'xyz')
            point = Point(* xyz)
            T1 = Translation.from_vector(origin - point)
            S = Scale.from_factors([self.scale] * 3)
            R = Rotation.from_euler_angles(self.rotation)
            T2 = Translation.from_vector(self.location)
            X = T2 * R * S * T1
        else:
            S = Scale.from_factors([self.scale] * 3)
            R = Rotation.from_euler_angles(self.rotation)
            T = Translation.from_vector(self.location)
            X = T * R * S
        mesh = self.mesh.transformed(X)
        vertex_xyz = {vertex: mesh.vertex_attributes(vertex, 'xy') + [0.0] for vertex in mesh.vertices()}
        return vertex_xyz

    def draw(self):
        """Draw the objects representing the force diagram.
        """
        layer = self.settings["layer"]
        self.artist.layer = layer
        self.artist.clear_layer()
        self.clear()
        if not self.visible:
            return
        self.artist.vertex_xyz = self.vertex_xyz

        # ======================================================================
        # Groups
        # ------
        # Create groups for vertices and edges.
        # These groups will be turned on/off based on the visibility settings of the diagram
        # ======================================================================

        group_vertices = "{}::vertices".format(layer)
        group_edges = "{}::edges".format(layer)

        if not compas_rhino.rs.IsGroup(group_vertices):
            compas_rhino.rs.AddGroup(group_vertices)

        if not compas_rhino.rs.IsGroup(group_edges):
            compas_rhino.rs.AddGroup(group_edges)

        # ======================================================================
        # Vertices
        # --------
        # Draw the vertices and add them to the vertex group.
        # ======================================================================

        vertices = list(self.mesh.vertices())
        color = {vertex: self.settings["color.vertices"] for vertex in vertices}
        guids = self.artist.draw_vertices(vertices, color)
        self.guid_vertex = zip(guids, vertices)
        compas_rhino.rs.AddObjectsToGroup(guids, group_vertices)

        if self.settings["show.vertices"]:
            compas_rhino.rs.ShowGroup(group_vertices)
        else:
            compas_rhino.rs.HideGroup(group_vertices)

        # ======================================================================
        # Edges
        # --------
        # Draw the edges and add them to the edge group.
        # ======================================================================

        edges = list(self.mesh.edges())
        colors = {}
        t_colors = {}

        for edge in edges:
            primal = self.mesh.primal_edge(edge)
            if self.mesh.primal.edge_attribute(primal, '_is_tension'):
                colors[edge] = self.settings['color.tension']
            else:
                colors[edge] = self.settings['color.edges']

        colors.update(t_colors)

        # color analysis
        if self.scene and self.scene.settings['RV2']['show.forces']:

            lengths = [self.mesh.edge_length(*edge) for edge in edges]
            lmin = min(lengths)
            lmax = max(lengths)
            for edge, length in zip(edges, lengths):
                if lmin != lmax:
                    colors[edge] = i_to_rgb((length - lmin) / (lmax - lmin))

            # c_lengths = [self.mesh.edge_length(*edge) for edge in colors.keys()]
            # c_min = min(c_lengths)
            # c_max = max(c_lengths)

            # if t_colors:

            #     t_lengths = [self.mesh.edge_length(*edge) for edge in t_colors.keys()]
            #     t_min = min(t_lengths)
            #     t_max = max(t_lengths)

            #     for edge, length in zip(colors.keys(), c_lengths):
            #         if c_min != c_max:
            #             colors[edge] = i_to_blue((length - c_min) / (c_max - c_min))
            #     for edge, length in zip(t_colors.keys(), t_lengths):
            #         if t_min != t_max:
            #             colors[edge] = i_to_red((length - t_min) / (t_max - t_min))
            # else:
            #     for edge, length in zip(colors.keys(), c_lengths):
            #         if c_min != c_max:
            #             colors[edge] = i_to_rgb((length - c_min) / (c_max - c_min))

        guids = self.artist.draw_edges(edges, colors)
        self.guid_edge = zip(guids, edges)
        compas_rhino.rs.AddObjectsToGroup(guids, group_edges)

        if self.settings["show.edges"]:
            compas_rhino.rs.ShowGroup(group_edges)
        else:
            compas_rhino.rs.HideGroup(group_edges)

        # ======================================================================
        # Labels
        # ------
        # Add labels for the angle deviations.
        # ======================================================================

        if self.scene and self.scene.settings['RV2']['show.angles']:
            tol = self.scene.settings['RV2']['tol.angles']
            edges = list(self.mesh.edges())
            angles = self.mesh.edges_attribute('_a', keys=edges)
            amin = min(angles)
            amax = max(angles)
            if (amax - amin)**2 > 0.001**2:
                text = {}
                color = {}
                for edge, angle in zip(edges, angles):
                    if angle > tol:
                        text[edge] = "{:.0f}".format(angle)
                        color[edge] = i_to_rgb((angle - amin) / (amax - amin))
                guids = self.artist.draw_edgelabels(text, color)
                self.guid_edgelabel = zip(guids, edges)

        # self.redraw()

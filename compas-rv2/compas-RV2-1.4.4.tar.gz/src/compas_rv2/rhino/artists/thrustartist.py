from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import sqrt

import compas_rhino

from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import length_vector

from .meshartist import MeshArtist


class ThrustArtist(MeshArtist):
    """A customised `MeshArtist` for the RV2 `ThrustDiagram`."""

    def draw_selfweight(self, vertices, color, scale, tol):
        """Draw the selfweight at each vertex of the diagram.

        Parameters
        ----------
        color : list or tuple
            The RGB color specification for selfweight vectors.
            The specification must be in integer format, with each component between 0 and 255.
        scale : float
            The scaling factor for the selfweight force vectors.

        Returns
        -------
        list
            A list of tuples, with each tuple containing a vertex identifier
            paired with the guid of the corresponding selfweight force vector in Rhino.

        Notes
        -----
        The magnitude of selfweight is calculated by the tributary area of the vertex of the loaded faces times its thickness `t`.
        """
        vertex_xyz = self.vertex_xyz
        lines = []

        for vertex in vertices:
            a = vertex_xyz[vertex]
            area = self.mesh.vertex_tributary_area(vertex)
            thickness = self.mesh.vertex_attribute(vertex, 't')
            weight = area * thickness
            load = scale_vector((0, 0, 1), scale * weight)
            b = add_vectors(a, load)
            lines.append({'start': a, 'end': b, 'color': color, 'arrow': "start"})
        return compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def draw_loads(self, vertices, color, scale, tol):
        """Draw the externally applied loads at all vertices of the diagram.

        Parameters
        ----------
        color : list or tuple
            The RGB color specification for load forces.
            The specification must be in integer format, with each component between 0 and 255.
        scale : float
            The scaling factor for the load force vectors.

        Returns
        -------
        list
            A list of tuples, with each tuple containing a vertex identifier
            paired with the guid of the corresponding load force vector in Rhino.

        Notes
        -----
        The magnitude of the externally applied load at a vetex the attribute  `pz`.
        """
        vertex_xyz = self.vertex_xyz
        lines = []

        for vertex in vertices:
            a = vertex_xyz[vertex]
            live = self.mesh.vertex_attribute(vertex, 'pz')
            load = scale_vector((0, 0, 1), scale * live)
            b = add_vectors(a, load)
            lines.append({'start': a, 'end': b, 'color': color, 'arrow': "start"})
        return compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def draw_reactions(self, vertices, color, scale, tol):
        """Draw the reaction forces at the anchored vertices of the diagram.

        Parameters
        ----------
        color : list or tuple
            The RGB color specification for reaction forces.
            The specification must be in integer format, with each component between 0 and 255.
        scale : float
            The scaling factor for the reaction force vectors.

        Returns
        -------
        list
            A list of tuples, with each tuple containing a vertex identifier
            paired with the guid of the corresponding reaction force vector in Rhino.

        Notes
        -----
        The reaction forces are the opposite of residual forces at anchored vertices.
        The residual force components are stored per vertex in the `rx`, `ry`, and `rz` attributes.

        """
        vertex_xyz = self.vertex_xyz
        lines = []
        for vertex in vertices:
            a = vertex_xyz[vertex]
            r = self.mesh.vertex_attributes(vertex, ['_rx', '_ry', '_rz'])
            r = scale_vector(r, scale)
            if length_vector(r) < tol:
                continue
            b = add_vectors(a, r)
            lines.append({'start': a, 'end': b, 'color': color, 'arrow': "start"})
        return compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def draw_residuals(self, vertices, color, scale, tol):
        """Draw the vertical component of the residual forces at the non-anchored vertices of the diagram.

        Parameters
        ----------
        color : list or tuple
            The RGB color specification for residual forces.
            The specification must be in integer format, with each component between 0 and 255.
        scale : float
            The scaling factor for the residual force vectors.

        Returns
        -------
        list
            A list of tuples, with each tuple containing a vertex identifier
            paired with the guid of the corresponding residual force vector in Rhino.

        Notes
        -----
        The residual force components are stored per vertex in the `rx`, `ry`, and `rz` attributes.

        """
        vertex_xyz = self.vertex_xyz
        lines = []
        for vertex in vertices:
            a = vertex_xyz[vertex]
            r = self.mesh.vertex_attributes(vertex, ['_rx', '_ry', '_rz'])
            r = scale_vector(r, scale)
            if length_vector(r) < tol:
                continue
            b = add_vectors(a, r)
            lines.append({'start': a, 'end': b, 'color': color, 'arrow': "start"})
        return compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def draw_pipes(self, edges, color, scale, tol):
        vertex_xyz = self.vertex_xyz
        cylinders = []
        for edge in edges:
            u, v = edge
            start = vertex_xyz[u]
            end = vertex_xyz[v]
            force = self.mesh.edge_attribute(edge, '_f')
            force = scale * force
            if force < tol:
                continue
            radius = sqrt(force / pi)
            if isinstance(color, dict):
                pipe_color = color[edge]
            else:
                pipe_color = color
            cylinders.append({
                'start': start,
                'end': end,
                'radius': radius,
                'color': pipe_color
            })
        return compas_rhino.draw_cylinders(cylinders, layer=self.layer, clear=False, redraw=False)

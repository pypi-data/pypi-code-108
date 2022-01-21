from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import angle_vectors_xy
from compas.geometry import cross_vectors

from compas_tna.diagrams import ForceDiagram
from .meshmixin import MeshMixin


class ForceDiagram(MeshMixin, ForceDiagram):
    """The RV2 ForceDiagram.

    Examples
    --------
    The :class:`ForceDiagram` is constructed from the :class:`FormDiagram` using
    :func:`ForceDiagram.from_formdiagram`. In RV2 this is dones as part of the
    TNA initialisation process.

    >>> force = FroceDiagram.from_formdiagram(form)
    """

    def primal_edge(self, key):
        """Get the corresponding edge in the FormDiagram.

        Parameters
        ----------
        key : tuple
            The identifier of the edge in this diagram.

        Returns
        -------
        tuple
            The identifier of the edge in the other/primal diagram.

        Raises
        ------
        KeyError
            If the dual edge does not exist.

        """
        f1, f2 = key
        for u, v in self.primal.face_halfedges(f1):
            if self.primal.halfedge[v][u] == f2:
                return u, v
        raise KeyError(key)

    def update_angle_deviations(self):
        """Compute the angle deviation with the corresponding edge in the FormDiagram.
        """
        for edge in self.edges():
            edge_ = self.primal_edge(edge)
            uv = self.edge_vector(*edge)
            uv_ = self.primal.edge_vector(*edge_)
            a = angle_vectors_xy(uv, cross_vectors(uv_, (0, 0, 1)), deg=True)
            if self.primal.edge_attribute(edge_, '_is_tension'):
                a = 180 - a
            self.edge_attribute(edge, '_a', a)
            self.primal.edge_attribute(edge_, '_a', a)

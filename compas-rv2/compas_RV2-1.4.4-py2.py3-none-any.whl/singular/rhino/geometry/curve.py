from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_rhino.geometry import RhinoCurve


class RhinoCurve(RhinoCurve):

    def __init__(self):
        super(RhinoCurve, self).__init__()

    def divide(self, number_of_segments, over_space=False):
        points = []
        compas_rhino.rs.EnableRedraw(False)
        if over_space:
            space = self.space(number_of_segments + 1)
            if space:
                points = [list(compas_rhino.rs.EvaluateCurve(self.guid, param)) for param in space]
        else:
            points = compas_rhino.rs.DivideCurve(self.guid, number_of_segments, create_points=False, return_points=True)
            points[:] = map(list, points)
        compas_rhino.rs.EnableRedraw(True)
        return points

    def length(self):
        """Return the length of the curve.

        Returns
        -------
        float
            The curve's length.
        """
        return compas_rhino.rs.CurveLength(self.guid)

    def tangents(self, points):
        tangents = []
        if compas_rhino.rs.IsPolyCurve(self.guid):
            pass
        elif compas_rhino.rs.IsCurve(self.guid):
            for point in points:
                param = compas_rhino.rs.CurveClosestPoint(self.guid, point)
                vector = list(compas_rhino.rs.CurveTangent(self.guid, param))
                tangents.append(vector)
        else:
            raise Exception('Object is not a curve.')
        return tangents

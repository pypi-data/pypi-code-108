from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rhino.geometry import RhinoPoint


class RhinoPoint(RhinoPoint):

    @property
    def xyz(self):
        return self.geometry.X, self.geometry.Y, self.geometry.Z

    def closest_point(self, *args, **kwargs):
        return self.xyz

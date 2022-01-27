# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from sylib.machinelearning.ensemble import EnsembleDescriptor


class PipelineDescriptor(EnsembleDescriptor):

    def __init__(self, **kwargs):
        super(PipelineDescriptor, self).__init__(**kwargs)
        self.set_steps([], [])

    def set_steps(self, names, descs):
        self._descs = descs
        self._names = names

    def set_x_names(self, x_names):
        for name, d, s in self.get_models():
            d.set_x_names(x_names)
            if d.y_names is None:
                break
            x_names = d.y_names

    def set_y_names(self, y_names):
        for name, d, s in list(self.get_models())[::-1]:
            d.set_y_names(y_names)
            if d.x_names is None:
                break
            y_names = d.x_names

    @property
    def y_names(self):
        if not self.has_models():
            return None

        _, desc, _ = list(self.get_models())[-1]
        return desc.y_names

    @property
    def x_names(self):
        if not self.has_models():
            return None

        _, desc, _ = list(self.get_models())[0]
        return desc.x_names

    def post_fit(self, skl):
        for name, d, s in self.get_models():
            d.skl = s
            d.post_fit(s)
        # Post fit operations may have updated x/y names - so propagate again
        self.set_x_names(list(self.get_models())[0][1].x_names)
        self.set_y_names(list(self.get_models())[-1][1].y_names)

    def has_models(self):
        return len(list(self.get_models())) > 0

    def get_models(self):
        return zip(self._names, self._descs, [skl for _, skl in self.skl.steps])

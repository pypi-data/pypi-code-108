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
from Qt import QtCore, QtWidgets

import copy

from sylib.machinelearning.descriptors import Descriptor
from sylib.machinelearning.model import set_model_tooltip


class EnsembleDescriptor(Descriptor):

    def __init__(self, **kwargs):
        super(EnsembleDescriptor, self).__init__(**kwargs)
        self.skl = None

    def new(self, skl):
        new_obj = super(EnsembleDescriptor, self).new()
        new_obj.skl = skl
        return new_obj

    @property
    def attributes(self):
        attributes = list(self._attributes)

        for name, d, s in self.get_models():
            attrs = d.attributes
            for attr in attrs:
                d = copy.deepcopy(attr)
                d['name'] = name+'__'+d['name']
                attributes.append(d)
        return attributes

    def get_attribute(self, skl, attribute):
        if attribute in self._attributes:
            return getattr(skl, attribute)

        first_split = attribute.find('__')
        model_name = attribute[:first_split]
        attribute = attribute[first_split+2:]
        for name, d, s in self.get_models():
            if name == model_name:
                return d.get_attribute(s, attribute)
        raise AttributeError('No model matching attribute prefix found')

    @property
    def parameters(self):
        params = dict(self._parameters)

        for name, d, s in self.get_models():
            pars = d.parameters
            for key, value in pars.items():
                d = copy.deepcopy(value)
                d['skl_name'] = name+'__'+d['skl_name']
                params[name+'__'+key] = d
        return params

    @property
    def types(self):
        types = dict(self._types)
        if self.skl is None:
            return types

        for name, d, s in self.get_models():
            tps = d.types
            for key, value in tps.items():
                d = copy.deepcopy(value)
                types[name+'__'+key] = d
        return types

    def get_models(self):
        """Returns list of (name, desc, skl) for each contained estimator"""
        raise NotImplementedError()

    def post_fit(self, skl):
        self.skl = skl
        for name, desc, s in self.get_models():
            desc.skl = s
            desc.post_fit(s)

    def visualize(self, skl, layout):
        self._select_listview = QtWidgets.QListWidget()
        self._select_listview.setMinimumWidth(50)

        self._vsplitter = QtWidgets.QSplitter()
        self._vsplitter.setOrientation(QtCore.Qt.Vertical)

        self._models_layout = QtWidgets.QVBoxLayout()
        self._models_layout.addWidget(self._vsplitter)
        self._models_group = QtWidgets.QGroupBox()
        self._models_group.setLayout(self._models_layout)

        self._hsplitter = QtWidgets.QSplitter()
        self._hsplitter.addWidget(self._select_listview)
        self._hsplitter.addWidget(self._models_group)
        self._hsplitter.setSizes([50, 400])
        self._hsplitter.setCollapsible(0, False)
        self._hsplitter.setCollapsible(1, False)
        self._hsplitter.setHandleWidth(1)
        self._hsplitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self._hsplitter)

        for name, d, s in self.get_models():
            self._select_listview.addItem(str(name))

        def index_changed(index):
            vsplitter = self._vsplitter
            # Delete all old content
            for old_idx in range(vsplitter.count())[::-1]:
                # wdg = vlayout.itemAt(old_idx).widget()
                wdg = vsplitter.widget(old_idx)
                wdg.deleteLater()
                # vlayout.removeWidget(wdg)
                # wdg.deleteLater()  #.setParent(None)

            # Render new visualization
            models = list(self.get_models())
            if len(models) == 0:
                vsplitter.addWidget(QtWidgets.QLabel(
                    "No scikit-learn model available"))
                return

            name, d, s = models[index]
            self._models_group.setTitle(d.name)
            if s is not None:
                set_model_tooltip(d, s, self._models_group)
                d.visualize(s, vsplitter)
            else:
                vsplitter.addWidget(QtWidgets.QLabel(
                    "No scikit-learn model available"))

        index_changed(0)
        self._select_listview.currentRowChanged[int].connect(index_changed)


class VotingClassifierDescriptor(EnsembleDescriptor):

    def __init__(self, **kwargs):
        super(VotingClassifierDescriptor, self).__init__(**kwargs)
        self.set_children([], [])

    def set_children(self, names, descriptors):
        self._descs = descriptors
        self._names = names

    def set_x_names(self, x_names):
        self.x_names = x_names
        for d in self._descs:
            d.set_x_names(x_names)

    def set_y_names(self, y_names):
        self.y_names = y_names
        for d in self._descs:
            d.set_y_names(y_names)

    def get_models(self):
        skl = self.skl
        names = self._names
        descs = self._descs
        try:
            skls = skl.estimators_
        except AttributeError:
            return [(name, desc, None) for name, desc in zip(names, descs)]
        return list(zip(names, descs, skls))


class MultiOutputClassifierDescriptor(EnsembleDescriptor):

    def __init__(self, **kwargs):
        super(MultiOutputClassifierDescriptor, self).__init__(**kwargs)
        self.set_child(None)
        self._descriptors = None

    def set_child(self, descriptor):
        self._desc = descriptor

    def set_x_names(self, x_names):
        self.x_names = x_names
        if self._descriptors is not None:
            for d in self._descriptors:
                d.set_x_names(self.x_names)
                d.set_y_names(self.y_names)

    def set_y_names(self, y_names):
        self.y_names = y_names
        if self._descriptors is None:
            self._descriptors = [copy.deepcopy(self._desc) for _ in y_names]
        for d in self._descriptors:
            d.set_x_names(self.x_names)
            d.set_y_names(self.y_names)

    def get_models(self):
        skl = self.skl
        names = self.y_names
        if names is None:
            return []

        descs = self._descriptors
        if descs is None:
            return []
        try:
            skls = skl.estimators_
        except AttributeError:
            return [(name, desc, None) for name, desc in zip(names, descs)]
        return list(zip(names, descs, skls))

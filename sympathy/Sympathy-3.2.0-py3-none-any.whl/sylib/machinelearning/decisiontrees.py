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
from Qt import QtWidgets
from Qt import QtSvg

import os
import tempfile
import sklearn
import sklearn.tree
import sklearn.preprocessing
import numpy as np

from sympathy.platform import os_support

from sylib.machinelearning.utility import find_dot
from sylib.machinelearning.descriptors import Descriptor


class DecisionTreeDescriptor(Descriptor):

    def build_widgets(self, layout):
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Expanding)
        self.scroll_area.setMinimumHeight(400)

        self.svg_widget = QtSvg.QSvgWidget()
        self.svg_widget.setMinimumSize(50, 50)
        self.svg_widget.setMaximumSize(50, 50)
        self.scroll_area.setWidget(self.svg_widget)
        layout.addWidget(self.scroll_area)
        if isinstance(layout, QtWidgets.QSplitter):
            layout.setStretchFactor(layout.count()-1, 100)
        else:
            layout.setStretchFactor(self.scroll_area, 100)

        self.hbox_widget = QtWidgets.QWidget()
        self.hbox = QtWidgets.QHBoxLayout()

        self.zoom_in = QtWidgets.QPushButton("Zoom In")
        self.zoom_out = QtWidgets.QPushButton("Zoom Out")
        self.hbox.addWidget(self.zoom_in)
        self.hbox.addWidget(self.zoom_out)
        self.hbox_widget.setMaximumHeight(50)

        self.hbox_widget.setLayout(self.hbox)
        layout.addWidget(self.hbox_widget)
        if isinstance(layout, QtWidgets.QSplitter):
            layout.setStretchFactor(layout.count()-1, 0)
        else:
            layout.setStretchFactor(self.hbox_widget, 0)

    def setup_visualization(self):
        self.gui_zoom = 1.0

    def build_tree(self, tree, classes=None):
        dot = find_dot()
        if not dot:
            return

        fd1, self.tmpdot = tempfile.mkstemp(
            prefix="decisiontree-", suffix=".dot")
        fd2, self.tmpsvg = tempfile.mkstemp(
            prefix="decisiontree-", suffix=".svg")
        os.close(fd1)
        os.close(fd2)

        with open(self.tmpdot, 'w') as f:
            args = {
                "filled": True, "rounded": True, "out_file": f, "max_depth": 10
            }
            if self.x_names is not None:
                args['feature_names'] = self.x_names
            if classes is not None:
                args['class_names'] = [str(obj) for obj in classes]

            sklearn.tree.export_graphviz(tree, **args)

        os_support.Popen_no_console(
            [dot, self.tmpdot, '-Tsvg', '-o',  self.tmpsvg]).communicate()

        self.svg_widget.load(self.tmpsvg)
        self.set_zoom()
        os.remove(self.tmpdot)
        os.remove(self.tmpsvg)

    def set_zoom(self):
        size = self.svg_widget.sizeHint()
        width = int(size.width()*self.gui_zoom)
        height = int(size.height()*self.gui_zoom)
        self.svg_widget.setMinimumSize(width, height)
        self.svg_widget.setMaximumSize(width, height)
        self.scroll_area.setMinimumHeight(min(400, max(50, height+5)))

    def visualize(self, skl, layout):
        super(DecisionTreeDescriptor, self).visualize(skl, layout)

        try:
            if skl.classes_ is None:
                raise AttributeError
        except AttributeError:
            label = QtWidgets.QLabel("Model not fitted")
            layout.addWidget(label)
            return

        if not find_dot():
            layout.addWidget(QtWidgets.QLabel(
                "Graphviz/dot not found - need to install and configure under "
                "Preferences > Debug"))
            return

        self.setup_visualization()
        self.build_widgets(layout)
        self.hbox.addStretch(1)

        def do_build_tree():
            try:
                self.build_tree(skl, skl.classes_)
            except TypeError:
                # For older scikit-learn version we may get a type
                # error since the behaviour of export_graphviz have
                # changed, we make a try with the old method also:
                self.build_tree(skl.tree_, skl.classes_)

        def zoom_in_clicked():
            self.gui_zoom = min(4.0, self.gui_zoom * np.sqrt(2))
            self.set_zoom()

        def zoom_out_clicked():
            self.gui_zoom /= np.sqrt(2)
            self.set_zoom()

        self.zoom_in.clicked.connect(zoom_in_clicked)
        self.zoom_out.clicked.connect(zoom_out_clicked)
        do_build_tree()


class RandomForestDescriptor(DecisionTreeDescriptor):

    def setup_visualization(self):
        super(RandomForestDescriptor, self).setup_visualization()
        self.selected_index = 0

    def visualize(self, skl, layout):
        # sic! We intentionally skip one level of inheritance
        super(DecisionTreeDescriptor, self).visualize(skl, layout)

        try:
            skl.classes_
        except AttributeError:
            label = QtWidgets.QLabel("Model not fitted")
            layout.addWidget(label)
            return

        if not find_dot():
            layout.addWidget(QtWidgets.QLabel(
                "Graphviz/dot not found - need to install and configure under "
                "Preferences > Debug"))
            return

        self.setup_visualization()
        self.build_widgets(layout)

        self.estimator_select = QtWidgets.QSpinBox()
        self.estimator_select.setMinimum(0)
        self.estimator_select.setMaximum(len(skl.estimators_)-1)
        self.hbox.addWidget(QtWidgets.QLabel("Select estimator:"))
        self.hbox.addWidget(self.estimator_select)
        self.hbox.addStretch(1)

        def estimator_selected(index):
            self.selected_index = index
            try:
                classes = skl.classes_
            except AttributeError:
                classes = None
            if len(skl.estimators_) > 0:
                self.build_tree(skl.estimators_[index], classes)

        def zoom_in_clicked():
            self.gui_zoom = min(4.0, self.gui_zoom * np.sqrt(2))
            self.set_zoom()

        def zoom_out_clicked():
            self.gui_zoom /= np.sqrt(2)
            self.set_zoom()

        self.estimator_select.valueChanged[int].connect(estimator_selected)
        self.zoom_in.clicked.connect(zoom_in_clicked)
        self.zoom_out.clicked.connect(zoom_out_clicked)
        estimator_selected(0)


class IsolationForestDescriptor(RandomForestDescriptor):
    def visualize(self, skl, layout):
        try:
            # Attribute only exist when model is fitted, fake classes_
            # attribute so that the above tree constructors know that it is
            # fitted
            skl.max_samples_
            skl.classes_ = None
        except AttributeError:
            pass
        super(IsolationForestDescriptor, self).visualize(skl, layout)

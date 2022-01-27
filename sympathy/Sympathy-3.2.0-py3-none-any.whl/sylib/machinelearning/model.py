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
import os

from Qt import QtWidgets
from Qt.QtCore import Qt

from sympathy.api.nodeconfig import Port
from sympathy.api import typeutil
from sylib.machinelearning.descriptors import Descriptor
from sylib.machinelearning.utility import encode, decode

_dirname = os.path.abspath(os.path.dirname(__file__))


def set_model_tooltip(desc, skl, widget):
    text = desc.describe_skl(skl)
    text += ("\nInput names: " + desc.xnames_as_text()
             + "\nOutput names: " + desc.ynames_as_text())
    widget.setToolTip(text)


class ModelViewer(typeutil.ViewerBase):
    def __init__(self, data=None, console=None, parent=None):
        super().__init__(parent)
        self._data = data
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)

        data.load()
        self.rebuild_ui()

    def data(self):
        return self._data()

    def update_data(self, data):
        self._data = data
        self._data.load()
        self.rebuild_ui()

    def rebuild_ui(self):
        desc = self._data.get_desc()
        skl = self._data.get_skl()
        for i in reversed(range(self._layout.count())):
            widget = self._layout.takeAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(1)

        if desc is not None:
            heading = QtWidgets.QLabel(
                "<center><h2>{0}</h2></center>".format(desc.name))
            heading.setMaximumHeight(40)
            self.splitter.addWidget(heading)
            if skl is not None:
                set_model_tooltip(desc, skl, heading)
            desc.visualize(skl, self.splitter)

        self._layout.addWidget(self.splitter)
        self._layout.setStretchFactor(self.splitter, 10)


@typeutil.typeutil('sytypealias model = sytext')
class File(typeutil.TypeAlias):

    def _extra_init(self, gen, data, filename, mode, scheme, source):
        self._desc = None
        self._skl = None

    @classmethod
    def icon(cls):
        return os.path.join(_dirname, 'port_model.svg')

    @classmethod
    def viewer(cls):
        return ModelViewer

    def set_skl(self, skl):
        """Sets the scikit-learn API object of this model"""
        self._skl = skl

    def get_skl(self):
        """Return the scikit-learn API object of this model"""
        return self._skl

    def set_desc(self, desc):
        """Sets the parameter descriptor object for this model"""
        self._desc = desc

    def get_desc(self):
        """Return the parameter descriptor object for this model"""
        return self._desc

    def save(self):
        """Encode this object so that it can be passed between
        nodes in sympathy"""
        obj = self._desc.on_save(self._skl)
        self.set((obj, self._desc))
        # self.set((self._skl, self._desc))

    def load(self):
        """Decode data from the internal representation used to pass
        between nodes in sympathy"""
        data = self.get()
        if data is not None:
            obj, self._desc = data
            self._skl = self._desc.on_load(obj)
            # self._skl, self._desc = data
        else:
            self._skl = None
            self._desc = Descriptor()

    def set(self, data):
        self._data.set(encode(data))

    def get(self):
        text = self._data.get()
        if not text:
            return None
        return decode(text)

    def source(self, other, shallow=False):
        self.set(other.get())


def ModelPort(description, name=None, n=None):
    return Port.Custom('model', description, name=name, n=n)


def ModelsPort(description, name=None, n=None):
    return Port.Custom('[model]', description, name=name, n=n)

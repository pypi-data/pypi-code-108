# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = [
    "H. Payno",
]
__license__ = "MIT"
__date__ = "30/09/2020"


from silx.gui import qt
import sys


class ObjectInspector(qt.QWidget):
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        self.__model = qt.QStandardItemModel()

        self._treeInspectorView = qt.QTreeView(self)
        self._treeInspectorView.setModel(self.__model)
        self.layout().addWidget(self._treeInspectorView)

    def setObject(self, object):
        self.__model.clear()
        root_item = qt.QStandardItem("{}".format(str(object)))
        size_item = qt.QStandardItem(
            "{} (M bytes)".format(sys.getsizeof(object) * 10e-6)
        )
        self.__model.invisibleRootItem().appendRow((root_item, size_item))

        def add_sub_elmts(parent_item, python_obj):
            if hasattr(python_obj, "__dict__"):
                for i_elmt, elmt in enumerate(python_obj.__dict__):
                    if hasattr(object, elmt):
                        children_obj = getattr(object, elmt)
                        # TODO: check if is a property or is a function
                        item = qt.QStandardItem("{}".format(elmt))
                        # TODO: add size
                        size_item = qt.QStandardItem(
                            "{} (M bytes)".format(sys.getsizeof(children_obj) * 10e-6)
                        )
                        parent_item.appendRow((item, size_item))

                        # TODO: add children
                        add_sub_elmts(parent_item=item, python_obj=children_obj)

        add_sub_elmts(parent_item=root_item, python_obj=object)

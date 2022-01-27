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
import re
import copy
import inspect
import sklearn
import sklearn.base
import numpy as np

from sylib.machinelearning.descriptors import Descriptor
from sylib.machinelearning.utility import value_to_tables
from sympathy.api import table
from sympathy.platform.viewer import ListViewer
from sympathy.platform.table_viewer import TableViewer
from sylib.machinelearning.utility import value_to_tables
from sympathy.api.exceptions import sywarn

from Qt import QtWidgets

class MLPClassifierDescriptor(Descriptor):
    pass

class SkorchDescriptor(Descriptor):

    def set_info(self, info, doc_class=None):
        """
        Takes a list of dictionaries or lists of itself recursively that
        together gives all information about the parameters described by
        this descriptor object.

        Each dictionary should contain the following keys:
        - name: the name of this parameter
        - desc: the description of this parameter
        - type: the type of this parameter using one of the special
                type constructors
        """

        self.info = info
        self.descriptions = {}
        self._types = {}
        self._parameters = {}
        self.dispnames = {}

        def process_info(info):
            if isinstance(info, list):
                return list(map(process_info, info))
            elif isinstance(info, str):
                # Strings inside lists act as names of parameter groups
                return None
            elif not isinstance(info, dict):
                raise ValueError

            # Attempt to automatically extract documentation from the
            # corresponding sklearn docstring
            if 'desc' not in info and doc_class is not None:
                info['desc'] = self.lookup_doc(
                    'Parameters', info['name'], doc_class, skip_first=True)
            elif 'desc' in info and not isinstance(info['desc'],
                                                   str):
                info['desc'] = self.lookup_doc(
                    'Parameters', info['name'], info['desc'], skip_first=True)
            else:
                pass

            self.descriptions[info['name']] = info['desc']
            self._types[info['name']] = info['type']
            if 'skl_name' not in info:
                info['skl_name'] = info['name']
            self._parameters[info['name']] = info
            self.dispnames[info['name']] = info['dispname']

        process_info(info)

    def parameter_tab(self, skl, notebook):
        """Builds a tab containing parameters of model"""
        rows = 0 if skl is None else 1
        cols = len(self.descriptions)
        if cols == 0:
            return

        table_widget = QtWidgets.QTableWidget(rows, cols)
        table_widget.setToolTip("Lists all parameters and their "
                                "currently given value for the model")

        tbl = table.File()
        if skl is None:
            for name in self.parameters.keys():
                tbl.set_column_from_array(name, np.array([]))
        else:
            params = skl.get_params()
            for name in self.parameters.keys():
                if name in params:
                    type_ = self.types[name]
                    value = type_.to_string(params[name])
                    tbl.set_column_from_array(self.dispnames[name], np.array([value]))
                else:
                    tbl.set_column_from_array(
                        self.dispnames[name], np.ma.array([''], mask=[True]))

        viewer = TableViewer(table_=tbl, plot=False, show_title=False)
        viewer._data_preview._preview_table.setMinimumHeight(100)
        notebook.addTab(viewer, "Parameters")

    def attribute_tabs(self, skl, notebook):
        """Builds tabs for visualizing the attributes of the model."""

        attributes = self.attributes
        if len(attributes) == 0:
            return

        for attr_dict in attributes:
            name = attr_dict['name']
            dispname = attr_dict['dispname']
            try:
                value = self.get_attribute(skl, name)
            except AttributeError:
                continue
            except ValueError:
                continue

            cnames = None
            rnames = None
            if 'cnames' in attr_dict:
                cnames = attr_dict['cnames'](self, skl)
            if 'rnames' in attr_dict:
                rnames = attr_dict['rnames'](self, skl)
            doc = attr_dict['desc']

            tbls = value_to_tables(value, dispname, cnames=cnames, rnames=rnames)
            if len(tbls) == 0:
                continue
            elif len(tbls) == 1:
                viewer = TableViewer(
                    table_=tbls[0], plot=False, show_title=False)
                viewer._data_preview._preview_table.setMinimumHeight(100)
                viewer.setToolTip(doc)
            else:
                viewer = ListViewer(viewer=TableViewer(
                    table_=table.File(), plot=False,
                    show_title=False), data_list=tbls)
                viewer._row_changed(0)
                viewer.setToolTip(doc)
            notebook.addTab(viewer, dispname)
            notebook.setTabToolTip(notebook.count()-1, doc)

    def get_attribute(self, skl, attribute):
        if getattr(skl, attribute):
            return [{'Epoch': getattr(skl, attribute)[_]['epoch'],
                'Duration': getattr(skl, attribute)[_]['dur'],
                'Training loss': getattr(skl, attribute)[_]['train_loss'],
                'Validation loss': getattr(skl, attribute)[_]['valid_loss'] if 'valid_loss' in getattr(skl, attribute)[_] else np.nan} 
                for _ in range(len(getattr(skl, attribute)))]
        else:
            return getattr(skl, attribute)

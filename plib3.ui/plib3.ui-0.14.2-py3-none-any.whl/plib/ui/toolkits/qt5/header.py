#!/usr/bin/env python3
"""
Module QT5.HEADER -- Python Qt 5 Header Objects
Sub-Package UI.TOOLKITS.QT5 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for headers.
"""

from PyQt5 import QtWidgets as qt

from plib.ui.defs import *


resize_mode_map = {
    WIDTH_STRETCH: qt.QHeaderView.Stretch,
    WIDTH_CONTENTS: qt.QHeaderView.ResizeToContents,
}


class PQtHeaderBase(object):
    # Mixin for header objects
    
    label_list = None
    labels_initialized = False
    
    def _update(self, data):
        # Hack to get around weirdness in Qt 4/5 table widget API
        self.label_list = [str(value) for value in data]
        super(PQtHeaderBase, self)._update(data)
    
    def _set_labels_from_list(self, label_list):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _header_item(self, index):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_label(self, index, label):
        if self.label_list is not None:
            # First time setting labels, do it this way
            self._set_labels_from_list(self.label_list)
            self.label_list = None
        if self.labels_initialized:
            # This allows labels to be changed after the initial setup
            item = self._header_item(index)
            item.setText(index, label)
        elif index == (len(self) - 1):
            # End of initial run
            self.labels_initialized = True
    
    def _header_view(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def _set_width(self, index, width):
        mode = resize_mode_map.get(width, qt.QHeaderView.Interactive)
        view = self._header_view()
        view.setSectionResizeMode(index, mode)
        if width > 0:
            view.resizeSection(index, width)
    
    def _set_readonly(self, index, readonly):
        pass


class PQtHeaderWidget(object):
    # Mixin for widgets that have headers
    
    def header_object(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_header_font_object(self, font_name, font_size, bold, italic):
        self.header_object().setFont(self.qt_font_object(
            font_name, font_size, bold, italic))

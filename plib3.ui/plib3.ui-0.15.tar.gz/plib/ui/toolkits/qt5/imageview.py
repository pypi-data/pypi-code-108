#!/usr/bin/env python3
"""
Module QT5.IMAGEVIEW -- Python Qt 5 Image View Objects
Sub-Package UI.TOOLKITS.PYSIDE2 of Package PLIB3 -- Python UI Toolkits
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 5 UI objects for the panel widgets.
"""

from PyQt5 import QtCore as qtc, QtGui as qtg, QtWidgets as qt

from plib.ui.base.imageview import PImageViewBase

from .app import PQtWidgetMeta, PQtWidgetBase


class PImageView(qt.QScrollArea, PQtWidgetBase, PImageViewBase,
                 metaclass=PQtWidgetMeta):
    
    image_view = None
    
    def __init__(self, manager, parent, filename=None, geometry=None):
        qt.QScrollArea.__init__(self, parent)
        self.setAlignment(qtc.Qt.AlignTop | qtc.Qt.AlignLeft)
        PImageViewBase.__init__(self, manager, parent, filename=filename, geometry=geometry)
    
    @staticmethod
    def supported_formats():
        # This must not be called until after the application object is created
        return [bytes(f).decode() for f in qtg.QImageReader.supportedImageFormats()]
    
    def load_from_file(self, filename):
        pixmap = qtg.QPixmap(filename)
        self.image_view = qt.QLabel()
        self.image_view.setAlignment(qtc.Qt.AlignTop | qtc.Qt.AlignLeft)
        self.image_view.setPixmap(pixmap)
        self.setWidget(self.image_view)
    
    def get_image_size(self):
        size = self.image_view.pixmap().size()
        return size.width(), size.height()
    
    def zoom_to(self, width, height):
        pixmap = self.image_view.pixmap()
        self.image_view.setPixmap(pixmap.scaled(width, height, qtc.Qt.KeepAspectRatio))
        self.image_view.resize(width, height)
    
    def rotate_90(self, clockwise):
        width, height = self.get_image_size()
        transform = qtg.QTransform()
        transform.rotate(90.0 * (1.0 if clockwise else -1.0))
        pixmap = self.image_view.pixmap()
        self.image_view.setPixmap(pixmap.transformed(transform))
        self.image_view.resize(height, width)

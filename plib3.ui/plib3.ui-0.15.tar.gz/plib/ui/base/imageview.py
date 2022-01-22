#!/usr/bin/env python3
"""
Module IMAGEVIEW -- UI Image View Widget
Sub-Package UI.BASE of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""


from .app import PWidgetBase


class PImageViewBase(PWidgetBase):
    
    def __init__(self, manager, parent, filename=None, geometry=None):
        PWidgetBase.__init__(self, manager, parent, geometry=geometry)
        self.filename = filename
        if filename:
            self.load_from_file(filename)
    
    supported_formats = None  # must implement in toolkit subclass as static method
    
    def load_from_file(self, filename):
        # Must implement in toolkit subclass
        raise NotImplementedError
    
    def get_image_size(self):
        # Must implement in toolkit subclass
        raise NotImplementedError
    
    def zoom_to(self, width, height):
        # Must implement in toolkit subclass
        raise NotImplementedError
    
    def zoom_by(self, factor):
        w, h = self.get_image_size()
        self.zoom_to(w * factor, h * factor)
    
    def fit_to_window(self):
        w, h = self.get_size()
        self.zoom_to(w, h)
    
    def rotate_90(self, clockwise):
        # Must implement in toolkit subclass
        raise NotImplementedError
    
    def rotate_left(self):
        self.rotate_90(False)
    
    def rotate_right(self):
        self.rotate_90(True)

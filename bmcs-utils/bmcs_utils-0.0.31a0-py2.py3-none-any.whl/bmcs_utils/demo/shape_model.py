
from bmcs_utils.trait_types import \
    Float, Int, Bool, FloatRangeEditor, Instance, Range, ProgressEditor, FloatEditor
from bmcs_utils.model import Model
from bmcs_utils.item import Item
from bmcs_utils.view import View
import numpy as np

class CSShape(Model):
    """Cross sectional shape"""
    def update_plot(self, axes):
        pass

class Rectangle(CSShape):
    """Rectangular cross section"""
    H = Float(10, desc=r'first material parameter')
    B = Float(5, desc='input parameter')

    ipw_view = View(
        Item('H'),
        Item('B')
    )

class Circle(CSShape):
    """Circular shape"""
    R = Float(10, desc=r'first material parameter')

    ipw_view = View(
        Item('R'),
    )


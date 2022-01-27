# test inspect tab
# Derek Fujimoto
# Feb 2021

from numpy.testing import *
import numpy as np
from bfit.gui.popup_units import popup_units
from bfit.gui.bfit import bfit

# filter unneeded warnings
import pytest
pytestmark = pytest.mark.filterwarnings('ignore:2020')

def with_bfit(year, run):
    def wrapper2(function):
        def wrapper(*args, **kwargs):
            # make gui
            b = bfit(None, True)
            tab = b.fileviewer
            
            tab.year.set(year)
            tab.runn.set(run)
            tab.get_data()
            
            units = popup_units(b)
            
            try:
                return function(*args, **kwargs, b=b, tab=tab, units=units)
            finally:
                b.on_closing()
                del b      
        return wrapper
    return wrapper2
    
@with_bfit(year=2020, run=40010)
def test_units_rescale(b=None, tab=None, units=None):
    units.input['1n'][0].set('1')
    units.set()
    tab.draw('inspect')
    ax = b.plt.gca('inspect')    
    assert ax.get_xticks()[0] == 40000, "Data rescaled by 1000"

@with_bfit(year=2020, run=40010)
def test_units_rename(b=None, tab=None, units=None):
    test_unit = 'test_unit'
    
    units.input['1n'][1].set('test_unit')
    units.set()
    tab.draw('inspect')
    ax = b.plt.gca('inspect')    
    assert ax.get_xlabel()[-len(test_unit)-1:-1] == test_unit, \
            "Units rename %s != %s" % (ax.get_xlabel(), test_unit)

@with_bfit(year=2020, run=40010)
def test_units_defaults_legacy(b=None, tab=None, units=None):
    units.input['1n'][1].set('default')
    units.set()
    tab.draw('inspect')
    ax = b.plt.gca('inspect')    
    assert ax.get_xlabel() == 'Voltage (default)', "xlabel not Voltage (default), is: %s" % ax.get_xlabel()
    assert ax.get_xticks()[0] == 40000, "Data not scaled to mV, tick zero is: %s" % str(ax.get_xticks()[0])

# umcomment when a run is saved which this can be run on. 
# ~ @with_bfit(year=2020, run=40010)
# ~ def test_units_defaults_new(b=None, tab=None, units=None):
    # ~ units.input['1n'][1].set('default')
    # ~ units.set()
    # ~ tab.draw('inspect')
    # ~ ax = b.plt.gca('inspect')    
    # ~ assert ax.get_xlabel() == 'Voltage (V)', "xlabel not Voltage (V), is: %s" % ax.get_xlabel()
    # ~ assert ax.get_xticks()[0] == 40, "Data not scaled to volts, tick zero is: %s" % str(ax.get_xticks()[0])    

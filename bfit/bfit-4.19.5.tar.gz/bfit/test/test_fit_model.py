# test fit results with model
from numpy.testing import *
import numpy as np
from bfit.gui.popup_fit_results import popup_fit_results
from bfit.gui.bfit import bfit

# filter unneeded warnings
import pytest
pytestmark = pytest.mark.filterwarnings('ignore:2020')

def with_bfit(function):
    
    def wrapper(*args, **kwargs):
        # make gui
        b = bfit(None, True)
        tab = b.fit_files
        tab2 = b.fetch_files
        b.notebook.select(2)
        
        tab2.year.set(2020)
        tab2.run.set('40123 40127, 40129')
        tab2.get_data()
        tab.populate()
        b.draw_fit.set(False)
        
        try:
            return function(*args, **kwargs, b=b, fittab=tab, fetchtab=tab2)
        finally:
            b.on_closing()
            del b
            
    return wrapper

@with_bfit
def test_par_detection(b=None, fittab=None, fetchtab=None):
    
    # set inputs
    res = popup_fit_results(b)
    res.entry.insert('1.0', 'y = a*x+b')
    res.get_input()
    
    assert all([k in res.new_par['name'].values for k in 'ab'])
    assert len(res.new_par['name'].values) == 2

    
@with_bfit
def test_fit_accuracy(b=None, fittab=None, fetchtab=None):
    
    # set inputs
    res = popup_fit_results(b)
    res.entry.insert('1.0', 'y = a*x+b')
    res.get_input()
    
    res.xaxis.set('Temperature (K)')
    res.yaxis.set('Temperature (K)')
    
    # do fit
    res.do_fit()
    
    # check chi2
    assert res.chi < 0.1

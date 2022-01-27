# Test deadtime corrections popup
from numpy.testing import *
import numpy as np
import pandas as pd
import bdata as bd
from bfit.gui.bfit import bfit
from bfit.gui.popup_deadtime import popup_deadtime

# filter unneeded warnings
import pytest
pytestmark = pytest.mark.filterwarnings('ignore:2020')

def with_bfit(function):
    
    def wrapper(*args, **kwargs):
        # make gui
        b = bfit(None, True)
        tab = b.fileviewer
        tab2 = b.fetch_files
        
        # get data
        tab.year.set(2020)
        tab.runn.set(40123)
        tab.get_data()
            
        tab2.year.set(2020)
        tab2.run.set('40123 40127')
            
        # test
        try:
            return function(*args, **kwargs, b=b)
        finally:
            b.on_closing()
            del b
            
    return wrapper

@with_bfit
def test_default_run_set(b=None):
    
    dead = popup_deadtime(b)
    assert_equal(dead.year.get(), b.fileviewer.data.year, err_msg='Year not copied')
    assert_equal(dead.run.get(), b.fileviewer.data.run, err_msg='Run not copied')

@with_bfit
def test_find_free(b=None):
    
    dead = popup_deadtime(b)
    
    # both free
    dead.fix_dt.set(False)
    dead.fix_c.set(False)
    dead.find()
    
    assert dead.dt != 0
    assert dead.c != 1

@with_bfit
def test_find_fixed_c(b=None):
    
    dead = popup_deadtime(b)
    
    # fixed helicity
    dead.fix_dt.set(False)
    dead.fix_c.set(True)
    dead.find()
    
    assert dead.dt != 0
    assert dead.c == 1

@with_bfit
def test_find_fixed_dt(b=None):
    
    dead = popup_deadtime(b)
    
    # fixed deadtime
    dead.fix_dt.set(True)
    dead.fix_c.set(False)
    dead.find()
    
    assert dead.dt == 0
    assert dead.c != 1
    
@with_bfit
def test_find_fixed_both(b=None):
    
    dead = popup_deadtime(b)
    
    # fixed deadtime
    dead.fix_dt.set(True)
    dead.fix_c.set(True)
    dead.find()
    
    assert dead.dt == 0
    assert dead.c == 1
    
@with_bfit
def test_draw(b=None):
    
    dead = popup_deadtime(b)
    dead.find()
    dead.draw()

@with_bfit
def test_activate(b=None):
    
    dead = popup_deadtime(b)

    # activate off
    assert b.deadtime_switch.get() == False
    assert_equal(b.deadtime, 0, "Global deadtime initial state")
    
    # find to activate
    dead.find()
    assert b.deadtime_switch.get() == True

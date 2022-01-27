# test inspect tab
# Derek Fujimoto
# Feb 2021
from numpy.testing import *
import numpy as np
import matplotlib.pyplot as plt
from bfit.gui.bfit import bfit
import bdata as bd
import os

# filter unneeded warnings
import pytest
pytestmark = pytest.mark.filterwarnings('ignore:2020')
plt.ion()

def with_bfit(function):
    
    def wrapper(*args, **kwargs):
        # make gui
        b = bfit(None, True)
        tab = b.fileviewer
        
        try:
            function(*args, **kwargs, tab=tab, b=b)
        finally:
            b.on_closing()
            del b
            
    return wrapper

def test_fetch_20():    fetch(40123, 2020, '20')
def test_fetch_1f():    fetch(40033, 2020, '1f')
def test_fetch_1w():    fetch(40037, 2020, '1w')
def test_fetch_1n():    fetch(40011, 2020, '1n')
def test_fetch_2h():    fetch(45539, 2019, '2h')
def test_fetch_2e():    fetch(40326, 2019, '2e')
def test_draw_20():     draw(40123, 2020, '20')
def test_draw_1f():     draw(40033, 2020, '1f')
def test_draw_1w():     draw(40037, 2020, '1w')
def test_draw_1n():     draw(40011, 2020, '1n')

@pytest.mark.filterwarnings('ignore:2019')
@pytest.mark.filterwarnings('ignore:divide by zero')
@pytest.mark.filterwarnings('ignore:Warning')
@pytest.mark.filterwarnings('ignore:invalid value')
def test_draw_2h():     draw(45539, 2019, '2h')

def test_draw_2e():     draw(40326, 2019, '2e')

@with_bfit
def fetch(r, y, mode, tab=None, b=None):    
    
    tab.year.set(y)
    tab.runn.set(r)
    
    try:
        tab.get_data()
    except Exception as err: 
        print(err)
        raise AssertionError("fileviewer fetch %s (%d.%d) data" % (mode, y, r))
    
    assert_equal(tab.data.run, r, "fileviewer fetch %s (%d.%d) data accuracy" % (mode, y, r))
    
@with_bfit
def draw(r, y, mode, tab=None, b=None):

    # get data
    tab.year.set(y)
    tab.runn.set(r)
    tab.get_data()
    
    # draw
    n = len(tab.entry_asym_type['values'])
    
    for i in range(n):
        
        # switch draw types
        tab.entry_asym_type.current(i)
        draw_type = tab.asym_type.get()
        
        # draw
        try:
            tab.draw(figstyle='inspect')
        except Exception as err: 
            print(err)
            raise AssertionError("fileviewer draw %s in mode %s" % (mode, draw_type), 'inspect')
        
        b.plt.clf('inspect')
        
        if mode == '2e':
            b.do_close_all()
    
@with_bfit
def test_draw_new(tab=None, b=None):    
    
    tab.year.set(2020)
    b.draw_style.set('new')
    tab.runn.set(40123)
    
    for r in range(3):
        tab.get_data()
        tab.draw('inspect')
    assert_equal(len(b.plt.plots['inspect']), 3, 'fileviewer draw new')

@with_bfit
def test_draw_stack(tab=None, b=None):
    
    tab.year.set(2020)
    b.draw_style.set('stack')
    
    for r in (40123, 40127):
        tab.runn.set(r)
        tab.get_data()
        tab.draw('inspect')
    
    ax = b.plt.gcf('inspect').axes[0]
    assert_equal(len(ax.draw_objs), 2, 'fileviewer stack')
    
@with_bfit
def test_draw_redraw(tab=None, b=None):

    tab.year.set(2020)
    b.draw_style.set('redraw')
        
    for r in (40123, 40127):
        tab.runn.set(r)
        tab.get_data()
        tab.draw('inspect')
    
    ax = b.plt.gcf('inspect').axes[0]
    assert_equal(len(ax.draw_objs), 1, 'fileviewer redraw')
    
@with_bfit    
def test_autocomplete(tab=None, b=None):
  
    tab.year.set(2020)
    tab.runn.set(402)
    tab.get_data()
    assert_equal(tab.data.run, 40299, 'fileviewer autocomplete fetch')
    
@with_bfit    
def test_load_run_from_file(tab=None, b=None):
    
    # load a file
    dat = bd.bdata(40123, 2020)
    
    # get file location
    if 'BNMR_ARCHIVE' in os.environ:
        path = os.path.join(os.environ['BNMR_ARCHIVE'],'2020','040123.msr')
    else:
        path = os.path.join(os.environ['HOME'],'.bdata','bnmr','2020','040123.msr')
    
    # load file
    tab.load_file(filename=path)
    
    # check inputs disabled
    assert tab.entry_year['state'] == 'disabled', 'year state == disabled'
    assert tab.entry_runn['state'] == 'disabled', 'runn state == disabled'
    
    # check that run loaded
    assert tab.data.title == dat.title, 'tab data loaded correctly'
    
    # check that fetch loads correct data
    tab.get_data()
    assert tab.data.title == dat.title, 'tab data loaded correctly'
    
    # turn off load file
    tab.load_file(filename='')
  
    # check inputs enabled
    assert tab.entry_year['state'] == 'normal', 'year state == normal'
    assert tab.entry_runn['state'] == 'normal', 'runn state == normal'

    # check that runs now fetch properly as normal
    tab.runn.set(40127)
    tab.year.set(2020)
    tab.get_data()
    assert tab.data.title == bd.bdata(40127, 2020).title, 'tab data loaded correctly'
    

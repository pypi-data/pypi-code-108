# Test exporting asymmetries
from numpy.testing import *
import numpy as np
import pandas as pd
import bdata as bd
from bfit.gui.bfit import bfit
import os

# filter unneeded warnings
import pytest
pytestmark = pytest.mark.filterwarnings('ignore:2020')

# test file name
filename = 'TESTFILE.csv'

def with_bfit(function):
    
    def wrapper(*args, **kwargs):
        # make gui
        b = bfit(None, True)
        tab = b.fetch_files
        tab2 = b.fileviewer
        b.notebook.select(2)
        
        tab.year.set(2020)
        tab.run.set('40123 40127')
        tab.get_data()
        
        tab2.runn.set(40123)
        tab2.year.set(2020)
        tab2.get_data()
        
        try:
            return function(*args, **kwargs, b=b)
        finally:
            b.on_closing()
            del b
            
    return wrapper

def check_columns(filename):
    
    # load file
    df = pd.read_csv(filename, comment='#')
    
    # check columns
    columns = ['time_s', 
                'positive_helicity', 
                'positive_helicity_err',
                'negative_helicity', 
                'negative_helicity_err', 
                'forward_counter',
                'forward_counter_err', 
                'backward_counter', 
                'backward_counter_err',
                'combined', 
                'combined_err']
    for c in df.columns:
        assert c in columns
    
    # check column length
    assert len(df.columns) == len(columns)

def check_content(data, filename):
    
    # load file
    df = pd.read_csv(filename, comment='#')
    
    # get asymmetry
    asym = data.asym()
    
    # check time
    assert_array_almost_equal(df['time_s'],                asym['time_s'], err_msg='time compare')
    
    # check combined
    assert_array_almost_equal(df['combined'],              asym['c'][0], err_msg='combined compare')
    assert_array_almost_equal(df['combined_err'],          asym['c'][1], err_msg='combined error compare')
    
    # check split hel
    assert_array_almost_equal(df['positive_helicity'],     asym['p'][0], err_msg='positive helicity compare')
    assert_array_almost_equal(df['positive_helicity_err'], asym['p'][1], err_msg='positive helicity error compare')
    
    assert_array_almost_equal(df['negative_helicity'],     asym['n'][0], err_msg='negative helicity compare')
    assert_array_almost_equal(df['negative_helicity_err'], asym['n'][1], err_msg='negative helicity error compare')
    
    # check split detector
    assert_array_almost_equal(df['forward_counter'],       asym['f'][0], err_msg='forward counter compare')
    assert_array_almost_equal(df['forward_counter_err'],   asym['f'][1], err_msg='forward counter error compare')
    
    assert_array_almost_equal(df['backward_counter'],      asym['b'][0], err_msg='backward counter compare')
    assert_array_almost_equal(df['backward_counter_err'],  asym['b'][1], err_msg='backward counter error compare')

@with_bfit
def test_export_fileviewer_columns(b=None):
    
    # export
    b.fileviewer.export(filename)
    
    # test
    check_columns(filename)
    
    # clean
    os.remove(filename)

@with_bfit
def test_export_fileviewer_content(b=None):
    
    # export
    b.fileviewer.export(filename)
    
    # get bdata object
    data = b.fileviewer.data
    
    # test
    check_content(data, filename)
    
    # clean
    os.remove(filename)

@with_bfit
def test_export_fetch_files_columns(b=None):
    
    # export
    b.fetch_files.export(directory='.')
    
    # test
    check_columns('2020_40123.csv')
    check_columns('2020_40127.csv')
    
    # clean
    os.remove('2020_40123.csv')
    os.remove('2020_40127.csv')

@with_bfit
def test_export_fetch_files_content(b=None):
    
    # export
    b.fetch_files.export(directory='.')
    
    # get bdata object
    datalines = b.fetch_files.data_lines

    # test
    check_content(datalines['2020.40123'].bdfit, '2020_40123.csv')
    check_content(datalines['2020.40127'].bdfit, '2020_40127.csv')
    
    # clean
    os.remove('2020_40123.csv')
    os.remove('2020_40127.csv')
    

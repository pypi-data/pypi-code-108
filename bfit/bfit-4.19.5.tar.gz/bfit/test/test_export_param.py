# Test exporting fit parameters

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
        tab2 = b.fit_files
        b.notebook.select(2)
        b.draw_fit.set(False)
        
        # get data
        tab.year.set(2021)
        tab.run.set('40063 40054')
        tab.get_data()
        
        # fit
        tab2.populate()
        
        # test
        try:
            return function(*args, **kwargs, b=b)
        finally:
            b.on_closing()
            del b
            
    return wrapper

def check_columns(filename, columns):
    
    # load file
    df = pd.read_csv(filename, comment='#')
    
    # check columns
    for c in columns:
        assert c in df.columns, ('"%s" not included' % c)
    
    for c in df.columns:
        assert c in columns, ("'%s' included when it shouldn't be" % c)
    
    # check column length
    assert_equal(len(df.columns), len(columns))

@with_bfit
def test_columns_no_fit(b=None):
    
    b.fit_files.export(filename = filename)
    
    # get columns, no fit parameters (exp fit)
    columns = list(b.fit_files.xaxis_combobox['values'][4:])
    
    # add missing columns: errors
    new_columns = []
    for c in columns:
        
        # nmr values only
        if c in ['Cryo Lift Set (mm)',
                 'Cryo Lift Read (mm)']:
            continue
            
        # no fit values
        if c in ['Chi-Squared', 'T1', 'Error T1']:
            continue
        
        # copy values
        new_columns.append(c)
        
        # error-less quantities
        if c not in ['Unique Id',
                     'Run Number',
                     'Sample',
                     'Run Duration (s)',
                     'Start Time',
                     'Title',
                     'Year',
                     'NBM Rate (count/s)',
                     'Sample Rate (count/s)',
                     'Chi-Squared',
                     ]:
            new_columns.append('Error '+c)
        
    check_columns(filename, new_columns)

    # clean
    os.remove(filename)
    
@with_bfit
def test_columns_with_fit(b=None):
    
    b.fit_files.do_fit()
    b.fit_files.export(filename = filename)
    
    # get columns, no fit parameters (exp fit)
    columns = list(b.fit_files.xaxis_combobox['values'][1:])
    
    # add missing columns: errors
    new_columns = []
    for c in columns:
        
        # nmr values only
        if c in ['Cryo Lift Set (mm)',
                 'Cryo Lift Read (mm)']:
            continue
            
        # copy values
        new_columns.append(c)
        
        # error-less quantities
        if c not in ['Unique Id',
                     'Run Number',
                     'Sample',
                     'Run Duration (s)',
                     'Start Time',
                     'Title',
                     'Year',
                     'NBM Rate (count/s)',
                     'Sample Rate (count/s)',
                     'Chi-Squared',
                     ]:
                         
            if c in ['1_T1', 'amp']:
                new_columns.append('Error+ '+c)
                new_columns.append('Error- '+c)
            else:
                new_columns.append('Error '+c)
            
    columns = new_columns
        
    # add missing columns: run number, shared, fixed
    for name in b.data['2021.40063'].parnames:
        columns.append('fixed '+name)
        columns.append('shared '+name)
    
    del columns[columns.index('all the above')]
    del columns[columns.index('Error all the above')]
    
    check_columns(filename, columns)
    
    # clean
    os.remove(filename)

@with_bfit
def test_content(b=None):
    
    # set up and get data
    b.fit_files.do_fit()
    b.fit_files.export(filename = filename)
    df = pd.read_csv(filename, comment='#').loc[0]
    data = b.data['%d.%d' % (df['Year'], df['Run Number'])]
    
    # checker shortcut
    def chk(title, value):
        assert_almost_equal(df[title], value, err_msg='Compare %s'%title,
                            decimal=3)
    
    # check parameters
    chk('1_T1', data.fitpar.loc['1_T1', 'res'])
    chk('Error- 1_T1', data.fitpar.loc['1_T1', 'dres-'])
    chk('Error+ 1_T1', data.fitpar.loc['1_T1', 'dres+'])
    
    chk('amp', data.fitpar.loc['amp', 'res'])
    chk('Error- amp', data.fitpar.loc['amp', 'dres-'])
    chk('Error+ amp', data.fitpar.loc['amp', 'dres+'])
    
    # check parameters
    chk('Temperature (K)', data.temperature.mean)
    chk('Error Temperature (K)', data.temperature.std)
    
    chk('1000/T (1/K)', 1000/data.temperature.mean)
    chk('Error 1000/T (1/K)', 1000*data.temperature.std/data.temperature.mean**2)
    
    chk('Impl. Energy (keV)', data.beam_kev)
    chk('Error Impl. Energy (keV)', data.beam_kev_err)
    
    chk('Platform Bias (kV)', data.nmr_bias.mean)
    chk('Error Platform Bias (kV)', data.nmr_bias.std)
    
    chk('B0 Field (T)', data.field)
    chk('Error B0 Field (T)', data.field_std)
    
    assert df['Sample'] == data.sample, 'Sample'
    assert df['Title'] == data.title, 'Title'
    
    chk('RF Level DAC', data.rf_dac.mean)
    chk('Error RF Level DAC', data.rf_dac.std)
    
    chk('Chi-Squared', data.chi)
    
    chk('Run Duration (s)', data.duration)
    
    chk('Start Time', data.start_time)
    
    chk('Year', data.year)
    
    chk('CryoEx Mass Flow', data.cryo_read.mean)
    chk('Error CryoEx Mass Flow', data.cryo_read.std)
    
    chk('Laser Power (V)', data.las_pwr.mean)
    chk('Error Laser Power (V)', data.las_pwr.std)
    
    chk('Laser Wavelength (nm)', data.las_lambda.mean)
    chk('Error Laser Wavelength (nm)', data.las_lambda.std)
    
    chk('Laser Wavenumber (1/cm)', data.las_wavenum.mean)
    chk('Error Laser Wavenumber (1/cm)', data.las_wavenum.std)
    
    chk('Target Bias (kV)', data.target_bias.mean)
    chk('Error Target Bias (kV)', data.target_bias.std)
    
    chk('NBM Rate (count/s)', np.sum([data.hist['NBM'+c].data 
                                     for c in ['B+', 'B-', 'F+', 'F-']])/data.duration)
    chk('Sample Rate (count/s)', np.sum([data.hist[c].data 
                                     for c in ['B+', 'B-', 'F+', 'F-']])/data.duration)
    
    assert df['fixed 1_T1'] == data.fitpar.loc['1_T1', 'fixed'], 'fixed 1_T1'
    assert df['shared 1_T1'] == data.fitpar.loc['1_T1', 'shared'], 'shared 1_T1'
    assert df['fixed amp'] == data.fitpar.loc['amp', 'fixed'], 'fixed amp'
    assert df['shared amp'] ==data.fitpar.loc['amp', 'shared'], 'shared amp'
    
    # clean
    os.remove(filename)
    

# Calculators for various quantities about the BNMR experiment
# Derek Fujimoto 
# Jan 2022
import pandas as pd
import numpy as np
import os
    
data_location = os.path.join(os.path.dirname(__file__),                             
                            'data', 
                            'nmr_antenna_data.csv')

def nqr_B0_hh6(amps=None, gauss=None):
    """
        Convert field to current and vice versa for bNQR HH6 magnet. 
        
        Errors are derived from RMS of residuals for the overall fit
        
        Input: either current (amps) OR field (gauss)
        Returns: (other unit, error)
    """    
    if amps is not None: 
        val = amps*3.56091338+1.57410913
        err = 0.006755
        return (val, err)
    elif gauss is not None:
        val = (gauss-1.57410913)/3.56091338
        err = 0.001897
        return (val, err)

def nqr_B0_hh3(amps=None, gauss=None):
    """
        Convert field to current and vice versa for bNQR HH3 magnet. 
        
        Errors are derived from RMS of residuals for the overall fit
        
        Input: either current (amps) OR field (gauss)
        Returns: (other unit, error)
    """    
    if amps is not None: 
        val = amps*2.21309+0.17476
        err = 0.05791
        return (val, err)
    elif gauss is not None:
        val = (gauss-0.17476)/2.21309
        err = 0.02617
        return (val, err)

def nmr_B1(mV=None, gauss=None, freq=41.27):
    """
        Convert field to peak-peak antenna voltage and vice versa for bNMR B1 magnet. 
        
        Error unknown. Talk to Gerald.
        
        Input: either voltage (mV) OR field (gauss)
                nu: frequency of the signal in MHz
        Returns: (other unit, error)
    """    
    if mV is not None: 
        val = mV*0.0396/freq
        err = 0
        return (val, err)
    elif gauss is not None:
        val = gauss/0.0396*freq
        err = 0
        return (val, err)

def nmr_atten(dac=None, power=None):
    """
        Convert DAC value to B1 power attenuation and vice versa for bNMR B1 magnet. 
        
        Input: either dac OR power (percent)
        Returns: other unit
    """    
    
    data = get_atten_data()
    
    if dac is not None: 
        data.sort_values('rf_level_control (DAC)', inplace=True)
        return np.interp(dac, 
                         data['rf_level_control (DAC)'],
                         data['power (%)'],
                         left=100,
                         right=0)
        
    elif power is not None:
        if power == 0:
            return 2047
        else:
            data.sort_values('power (%)', inplace=True)
            return int(np.interp(power, 
                             data['power (%)'].values, 
                             data['rf_level_control (DAC)'].values,
                             left=0,
                             right=2047))

def get_atten_data():
    """
        Get the dataframe needed for the attenuation calculation
    """
    data = pd.read_csv(data_location, comment="#")

    # normalize 
    df_max = data['antenna_amplitude (mV)'].max()
    data['power (%)'] = data['antenna_amplitude (mV)']/df_max*100
    
    return data

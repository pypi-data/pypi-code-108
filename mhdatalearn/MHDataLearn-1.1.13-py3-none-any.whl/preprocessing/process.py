# -*- coding: utf-8 -*-
"""
This module contains the function toexecute all 
preprocessing functions (from clean.py and calculate.py)
on a dataset (which can be specified as training or a
new unseen dataset) in preparation for ml model
training and selection.
"""

from MHDataLearn.preprocessing.clean import (data_types, 
                                             age_check, 
                                             gender_replace,
                                             marital_replace,
                                             accom_replace, 
                                             employ_replace,
                                             mhclass_replace
                                             )
from MHDataLearn.preprocessing.calculate import (calc_age_admit, 
                                                 check_emergency,
                                                 calc_readmit, 
                                                 calc_readmit, 
                                                 emergency_readmit,
                                                 check_emergency, 
                                                 los_train, 
                                                 los_current,
                                                 postcode_to_lsoa,
                                                 lsoa_to_imd
                                                 )

import pandas as pd
import numpy as np


def wrangle_data(df_temp, test= "training", imd=False):
    """
    Parameters
    ----------
    df_temp : main dataset
        
    test : True means wrangle data on historical dataset
           False means wrangle data on current dataset
                 and caluclaue LOS to today

    imd :   True means postcode will be used to calculate a
                deprivation score called 'imd_dec' which is
                the Index of Multiple Deprivation decile 
                (Warning: this requires download of a ~750mb 
                file and so may take several minutes)
            False means 'imd_dec' will not be calculated

    Returns
    -------
    df : main dataset
        all varibles encoded ready for modelling and appropriate
        flags added

    """
    df = df_temp.copy()
    df = data_types(df)
    df = mhclass_replace(df)
    df = gender_replace(df)
    df = marital_replace(df)
    df = accom_replace(df)
    df = employ_replace(df)
    df = calc_age_admit(df)
    df = age_check(df)
    if imd:
        df = postcode_to_lsoa(df)
        df = lsoa_to_imd(df)
    if test == "training":
        df = calc_readmit(df)
        df = check_emergency(df)
        df = emergency_readmit(df)
        df = los_train(df)
        print('Training data has been cleansed')
    else:
        df = los_current(df)
        print('Current data has been cleansed')
    return df
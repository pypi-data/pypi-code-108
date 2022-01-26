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
    print('Cleaning data types...', end = '')
    df = data_types(df)
    print('Complete')
    print('Cleaning MHCareClusterSuperClass variable...', end = '')
    df = mhclass_replace(df)
    print('Complete')
    print('Cleaning Gender variable...', end = '')
    df = gender_replace(df)
    print('Complete')
    print('Cleaning Marital variable...', end = '')
    df = marital_replace(df)
    print('Complete')
    print('Cleaning Accommodation variable...', end = '')
    df = accom_replace(df)
    print('Complete')
    print('Cleaning Employment variable...', end = '')
    df = employ_replace(df)
    print('Complete')
    print('Calculating Age at Admission...', end = '')
    df = calc_age_admit(df)
    print('Complete')
    print('Checking ages are valid and imputing missing values...', end = '')
    df = age_check(df)
    print('Complete')
    if imd:
        print('Converting Postcodes to LSOA')
        print('This may take several minutes, please be patient...', end = '')
        df = postcode_to_lsoa(df)
        print('Complete')
        print('Converting LSOA to IMD Deciles...', end = '')
        df = lsoa_to_imd(df)
        print('Complete')
    if test == "training":
        print('Identifying emergency readmissions...', end = '')
        df = calc_readmit(df)
        df = check_emergency(df)
        df = emergency_readmit(df)
        print('Complete')
        print('Calculating length of stays...', end = '')
        df = los_train(df)
        print('Complete')
        print('PREPROCESSING OF TRAINING DATA IS COMPLETE')
    else:
        df = los_current(df)
        print('Complete')
        print('PREPROCESSING OF TRAINING DATA IS COMPLETE')
    return df
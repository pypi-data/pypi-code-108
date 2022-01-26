# -*- coding: utf-8 -*-
"""
This module contains the function to load a user
specified file or the dummy data provided with
the package
"""

import pandas as pd
import numpy as np

url = "https://raw.githubusercontent.com/krisjb/MHDataLearn/main/Data/"\
        "DummyData.csv"

def load_data(filepath=url):
    """
    Loads local data file as dataframe from specified filepath
    If no filepath specified, loads dummy dataset from web

    Parameters
    ----------
    filepath : user specified filepath
    
    Returns
    -------
    df : DataFrame
    """
    
    df = pd.read_csv(filepath)
    return df

load_data()

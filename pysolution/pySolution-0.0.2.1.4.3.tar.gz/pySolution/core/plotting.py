from .helper_functions import *
from .run_model import *
import pandas as pd
import numpy as np
from .debye_huckel_model import *
from .osmotic import *
import matplotlib.pyplot as plt
from .density_script import *

def plot_osmotic_coefficient_temperature(df, T_lower = 273.15, T_upper = 373.15, n = 100):
    T = np.linspace(T_lower, T_upper, n)
    phi = []
    
    for temp in T:
        phi.append(osmotic_coefficient(df, temp))
    
    fig=plt.figure(figsize=(6,6))
    
    plt.plot(T, phi)
    plt.xlabel('Temperature (K)')
    plt.ylabel('Osmotic coefficient')
    
    plt.show()
    

def plot_activity_water_temperature(df, T_lower = 273.15, T_upper = 373.15, n = 100):
    T = np.linspace(T_lower, T_upper, n)
    a_h2o = []
    
    for temp in T:
        a_h2o.append(np.log(activity_h2o(lower_ionic_df, temp)))
    
    fig=plt.figure(figsize=(6,6))
    
    plt.plot(T, a_h2o)
    plt.xlabel('Temperature (K)')
    plt.ylabel('log(a_water)')
    
    plt.show()
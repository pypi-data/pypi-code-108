from .helper_functions import *
from .run_model import *
import pandas as pd
import numpy as np
from .debye_huckel_model import *
from .osmotic import *
import matplotlib.pyplot as plt
from .density_script import *
import pkg_resources


def activity_coeff_dict(df, T = 298.15):
    components = np.array(df['Component'])
    d = {}
    
    for comp in components:
        d[comp] = pitzer_activity_coefficient(df, comp, T)
    
    return d

def results(df, T = 298.15, option = 'activity coefficient'):
    """
    options: activity coefficient, osmotic coefficient, ionic strength, density
    """
    print("=================================================")
    print("DENSITY : " + str(density(df, T)) + " kg/L")
    print("=================================================")
    
    rho = density(df, T)
    I = 0
    for conc, charge in zip(df['Concentration (mol/L)'], df['Charge']):
        I = I + (conc * (1/rho))*(charge**2)
    
    print("IONIC STRENGTH : ", str(0.5*I))
      
    print("=================================================")
    print("ACTIVITY COFFICIENT RESULTS")
    print("=================================================")
    
    d = activity_coeff_dict(df, T)
    for comp in np.array(df['Component']):
        print("ACTIVITY COEFFICIENT FOR " + comp + " : " + str(d[comp]))
    
    print("=================================================")
    print("OSMOTIC COEFFICIENT : ", str(osmotic_coefficient(df, T)))
    print("=================================================")
    
    if option.lower() == 'activity coefficient':
        return d
    elif option.lower() == 'osmotic coefficient':
        return osmotic_coefficient(df, T)
    elif option.lower() == 'density':
        return density(df, T)
    elif option.lower() == 'ionic strength':
        return 0.5*I
    
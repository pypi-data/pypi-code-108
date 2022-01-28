import pandas as pd
import numpy as np
from .density_script import *

def debye_huckel(df, target_ion, T = 298.15):
    A = 0.5085
    z_i = float(df[df['Component'] == target_ion]['Charge'])
    rho = density(df, T)
    
    molality = []
    for conc in df['Concentration (mol/L)']:
        molality.append(conc * (1/rho))
    
    d = {'Component' : np.array(df['Component']),
         'Molality' : molality,
         'Charge' : np.array(df['Charge'])
        }
    
    I = 0
    for m_i, z_i in zip(molality, np.array(df['Charge'])):
        I = I + m_i*(z_i)**2
    
    I = 0.5*I
    return np.exp(-A* z_i**2 * np.sqrt(I))
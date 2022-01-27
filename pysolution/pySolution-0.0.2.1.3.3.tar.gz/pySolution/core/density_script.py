from .helper_functions import *
from .run_model import *
import pandas as pd
import numpy as np

def density(df, T = 298.15):
    """
    density of saline solutions (in g/cm3 or kg/L)
    """
    empirical_para = pd.read_excel("empirical_parameters.xlsx")
    with open('density_temp.pickle', 'rb') as f:
        clf = pickle.load(f)
    
    rho_25 = clf.predict([[298.15]])[0]
    rho_T = clf.predict([[T]])[0]
    
    Mw = 18.02
    v_w = 18
    
    xi_Mi = 0
    xi_sum = 0
    vi_xi = 0
    alpha_xi = 0
    
    for comp, conc in zip(df['Component'], df['Concentration (mol/L)']):
        xi = conc/(1000/18.02 + sum(np.array(df['Concentration (mol/L)'])))
        Mi = float(empirical_para[empirical_para['Ion'] == comp]['M_i'])
        vi = float(empirical_para[empirical_para['Ion'] == comp]['v_i'])
        alpha_i = float(empirical_para[empirical_para['Ion'] == comp]['a_i'])
        
        xi_Mi = xi_Mi + xi*Mi
        xi_sum = xi_sum + conc/(1000/18.02 + sum(np.array(df['Concentration (mol/L)'])))
        vi_xi = vi_xi + vi*xi
        alpha_xi = alpha_xi + alpha_i*xi
    
    numerator = xi_Mi + (1 - xi_sum)*Mw
    denominator = vi_xi + v_w*(1 - xi_sum) + alpha_xi*(1 - xi_sum)
       
    model_density = numerator/denominator
    
    return rho_T + model_density - rho_25
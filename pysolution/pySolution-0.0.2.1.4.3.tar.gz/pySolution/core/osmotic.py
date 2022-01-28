import pandas as pd
import numpy as np
from math import *
from .helper_functions import *
from .run_model import *
from .density_script import *
import pkg_resources

def activity_h2o(df, T = 298.15):
    return np.exp(-(1/density(df, T)) * np.sum(df['Concentration (mol/L)']) * 
                 osmotic_coefficient(df) * 18.02/1000)

def osmotic_coefficient(df, T = 298.15):
    mixing_path = pkg_resources.resource_filename('pySolution', 'core/mixing_parameters.xlsx')
    binary_path = pkg_resources.resource_filename('pySolution', 'core/binary_parameters.xlsx')
    
    binary_para = pd.read_excel(binary_path)
    mixing_para = pd.read_excel(mixing_path)
    
    rho = density(df, T)
    
    molality = []
    for conc in np.array(df['Concentration (mol/L)']):
        molality.append(conc*(1/rho))
    
    d = {'Component' : np.array(df['Component']),
         'Molality' : molality,
         'Charge' : np.array(df['Charge'])
        }
    
    df = pd.DataFrame(d)
    
    Z = Z_calc(df)
    A_ = A_calc(T)
    I = ionic_strength(df)
    b = 1.2
    
    cations = []
    anions = []

    for comp in df['Component']:
        if '+' in comp:
            cations.append(comp)
        elif '-' in comp:
            anions.append(comp)
    
    all_anion_combo = ion_combination(anions)
    all_cation_combo = ion_combination(cations)
    
    #first term
    first_term = 2*(1/sum(df['Molality']))
    
    #second term
    second_term = (-A_ * I**(3/2))/(1 + b*sqrt(I))
    
    #third term
    third_term = 0
    for c_a in cation_anion(cations, anions):
        c_phi = 0
        beta_0 = 0
        beta_1 = 0
        beta_2 = 0
        alpha = 0
        alpha_1 = 0
        alpha_2 = 0
        
        m_c = float(df[df['Component'] == c_a[0]]['Molality'])
        z_c = float(df[df['Component'] == c_a[0]]['Charge'])
        
        m_a = float(df[df['Component'] == c_a[1]]['Molality'])
        z_a = float(df[df['Component'] == c_a[1]]['Charge'])
        
        c_phi = float(binary_para.loc[(binary_para["Cation"] == c_a[0]) & 
                                       (binary_para["Anion"] == c_a[1]), "C (phi)"])
        
        C_ca = c_phi/(2*sqrt(abs(z_c) * abs(z_a)))
        
        beta_0 = float(binary_para.loc[(binary_para["Cation"] == c_a[0]) & 
                                       (binary_para["Anion"] == c_a[1]), "Beta (0)"])
        beta_1 = float(binary_para.loc[(binary_para["Cation"] == c_a[0]) & 
                                       (binary_para["Anion"] == c_a[1]), "Beta (1)"])
        beta_2 = float(binary_para.loc[(binary_para["Cation"] == c_a[0]) & 
                                       (binary_para["Anion"] == c_a[1]), "Beta (2)"])
        
        if abs(z_c) == 1 or abs(z_a) == 1:
            #monovalent electrolyte
            alpha = 2
            B_ca_phi = beta_0 + beta_1*np.exp(-alpha*sqrt(I))
        elif abs(z_c) == 2 and abs(z_a) == 2:
            #2-2 electrolyte
            alpha_1 = 1.4
            alpha_2 = 12
            B_ca_phi = beta_0 + beta_1*np.exp(-alpha_1*sqrt(I)) + beta_2*np.exp(-alpha_2*sqrt(I))
        else:
            #3-2, 4-2 electrolyte
            alpha_1 = 2
            alpha_2 = 50
            B_ca_phi = beta_0 + beta_1*np.exp(-alpha_1*sqrt(I)) + beta_2*np.exp(-alpha_2*sqrt(I))
        
        third_term = third_term + (m_c*m_a*(B_ca_phi + Z*C_ca))
    
    fourth_term = 0

    for c_c in all_cation_combo:
        theta_cc = 0
        phi_cc = 0
        
        m_c = float(df[df['Component'] == c_c[0]]['Molality'])
        m_c_prime = float(df[df['Component'] == c_c[1]]['Molality'])
        
        z_c = float(df[df['Component'] == c_c[0]]['Charge'])
        z_c_prime = float(df[df['Component'] == c_c[1]]['Charge'])
        
        e_theta_cc, e_theta_cc_prime = E_theta_prime(abs(z_c), abs(z_c_prime), A_, I)
        
        for index, row in mixing_para.iterrows():
                l_o = [row["i"], row["j"]]
                if (c_c[0] in l_o) and (c_c[1] in l_o):
                    theta_cc = row["theta_ij"]
        
        #phi_cc = theta_cc + e_theta_cc + I*e_theta_cc_prime
        phi_cc = theta_cc + e_theta_cc + I*e_theta_cc_prime
        
        m_a_psi_cca = 0
        
        for a in anions:
            m_a = float(df[df['Component'] == a]['Molality'])
            for index, row in mixing_para.iterrows():
                l_o = [row["i"], row["j"], row["k"]]
                if (c_c[0] in l_o) and (c_c[1] in l_o) and (a in l_o):
                    psi_cca = row["psi_ijk"]
            
            m_a_psi_cca = m_a_psi_cca + (m_a * psi_cca)
        
        fourth_term = fourth_term + (m_c * m_c_prime * (phi_cc + m_a_psi_cca))
        
    fifth_term = 0
    for a_a in all_anion_combo:
        theta_aa = 0
        phi_aa = 0
        
        m_a = float(df[df['Component'] == a_a[0]]['Molality'])
        m_a_prime = float(df[df['Component'] == a_a[1]]['Molality'])
        
        z_a = float(df[df['Component'] == a_a[0]]['Charge'])
        z_a_prime = float(df[df['Component'] == a_a[1]]['Charge'])
        
        e_theta_aa, e_theta_aa_prime = E_theta_prime(abs(z_a), abs(z_a_prime), A_, I)
        
        for index, row in mixing_para.iterrows():
                l_o = [row["i"], row["j"]]
                if (a_a[0] in l_o) and (a_a[1] in l_o):
                    theta_aa = row["theta_ij"]
        
        #phi_aa = theta_aa + e_theta_aa + I*e_theta_aa_prime
        phi_aa = theta_aa + e_theta_aa + I*e_theta_aa_prime
        
        m_c_psi_aac = 0
        
        for c in cations:
            m_c = float(df[df['Component'] == c]['Molality'])
            for index, row in mixing_para.iterrows():
                l_o = [row["i"], row["j"], row["k"]]
                if (a_a[0] in l_o) and (a_a[1] in l_o) and (c in l_o):
                    psi_aac = row["psi_ijk"]
            
            m_c_psi_aac = m_a_psi_cca + (m_c * psi_aac)
        
        fifth_term = fifth_term + (m_a * m_a_prime * (phi_aa + m_c_psi_aac))
    
    return 1 + first_term*second_term + third_term + fourth_term + fifth_term #so far, i need 4th and 5th terms
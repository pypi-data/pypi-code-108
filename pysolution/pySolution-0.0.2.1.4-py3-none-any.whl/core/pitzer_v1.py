import pandas as pd
import numpy as np
import pickle
from math import *
from scipy.optimize import fsolve
import multiprocessing as mp
from joblib import Parallel, delayed
import proplot as pplt
import random
import itertools
from itertools import product
import scipy.integrate as integrate
import scipy.special as special

from .helper_functions import *
from .density_script import *

def cation_activity_coefficient(df, target_ion, T = 298.15):
    empirical_path = pkg_resources.resource_filename('pySolution', 'core/empirical_parameters.xlsx')
    binary_path = pkg_resources.resource_filename('pySolution', 'core/binary_parameters.xlsx')
    
    binary_para = pd.read_excel(binary_path)
    mixing_para = pd.read_excel(empirical_path)
    A_ = A_calc(T)
    rho = density(df, T)
    
    molality = []
    for conc in np.array(df['Concentration (mol/L)']):
        molality.append(conc*(1/rho))
    
    d = {'Component' : np.array(df['Component']),
         'Molality' : molality,
         'Charge' : np.array(df['Charge'])
        }
    
    df = pd.DataFrame(d)
    I = ionic_strength(df)
    F = F_calc(df, A_)
    Z = Z_calc(df)
    zM = float(df[df['Component'] == target_ion]['Charge'])
    
    cations = []
    anions = []

    for comp in df['Component']:
        if '+' in comp:
            cations.append(comp)
        elif '-' in comp:
            anions.append(comp)
    
    all_anion_combo = ion_combination(anions)
    all_cation_combo = ion_combination(cations)
    #first summation term
    first_term = 0

    for a in anions:
        #initialize beta terms and c_phi
        beta_0 = 0
        beta_1 = 0
        beta_2 = 0
        c_phi = 0

        #molality of anion "a"
        m_a = float(df[df['Component'] == a]['Molality'])
        z_a = float(df[df['Component'] == a]['Charge'])

        #get beta_0, beta_1, beta_2 of "Ma"
        beta_0 = float(binary_para.loc[(binary_para["Cation"] == target_ion) & 
                                       (binary_para["Anion"] == a), "Beta (0)"])
        beta_1 = float(binary_para.loc[(binary_para["Cation"] == target_ion) & 
                                       (binary_para["Anion"] == a), "Beta (1)"])
        beta_2 = float(binary_para.loc[(binary_para["Cation"] == target_ion) & 
                                       (binary_para["Anion"] == a), "Beta (2)"])
        c_phi = float(binary_para.loc[(binary_para["Cation"] == target_ion) & 
                                       (binary_para["Anion"] == a), "C (phi)"])

        Cma = c_phi/(2*sqrt(abs(zM) * abs(z_a)))

        if abs(zM) == 1 or abs(z_a) == 1:
            alpha = 2
            g_original, _ = g(alpha*sqrt(I))
            Bma = beta_0 + beta_1*g_original

        else:
            if abs(zM) == 2 and abs(z_a) == 2:
                alpha_1 = 1.4
                alpha_2 = 12
            else:
                alpha_1 = 2
                alpha_2 = 50

            g_original_1, _ = g(alpha_1*sqrt(I))
            g_original_2, _ = g(alpha_2*sqrt(I))

            Bma = beta_0 + beta_1*g_original_1 + beta_2*g_original_2

        first_term = first_term + m_a*(2*Bma + Z*Cma)
    
    #second summation term
    second_term = 0

    for c in cations:
        theta_Mc = 0
        phi_Mc = 0

        #molality of anion "c"
        m_c = float(df[df['Component'] == c]['Molality'])
        z_c = float(df[df['Component'] == c]['Charge'])

        if target_ion != c:
            for index, row in mixing_para.iterrows():
                l_o = [row["i"], row["j"]]
                if (target_ion in l_o) and (c in l_o):
                    theta_Mc = row["theta_ij"]

            X_mc = 6*abs(zM)*abs(z_c)*A_*sqrt(I)
            X_mm = 6*zM*zM*A_*sqrt(I)
            X_cc = 6*z_c*z_c*A_*sqrt(I)

            e_theta_Mc, _ = E_theta_prime(abs(zM), abs(z_c), A_, I)
            phi_Mc = theta_Mc + e_theta_Mc
            
        else:
            pass

        ma_psi = 0
        for a in anions:
            m_a = float(df[df['Component'] == a]['Molality'])
            for index, row in mixing_para.iterrows():
                l_o = [row["i"], row["j"], row["k"]]
                if (target_ion in l_o) and (c in l_o) and (a in l_o):
                    psi_ijk = row["psi_ijk"]

            ma_psi = ma_psi + (m_a * psi_ijk)

        second_term = second_term + m_c*(2*phi_Mc + ma_psi)
    
    #third term
    third_term = 0

    for a_a in all_anion_combo:
        m_a = float(df[df['Component'] == a_a[0]]['Molality'])
        m_a_prime = float(df[df['Component'] == a_a[1]]['Molality'])

        for index, row in mixing_para.iterrows():
            l_o = [row["i"], row["j"], row["k"]]
            if (a_a[0] in l_o) and (a_a[1] in l_o) and (target_ion in l_o):
                psi_ijk = row["psi_ijk"]

        third_term = third_term + (m_a * m_a_prime * psi_ijk)
    
    #fourth term
    fourth_term = 0

    for c_a in cation_anion(cations, anions):
        c_phi = 0

        m_c = float(df[df['Component'] == c_a[0]]['Molality'])
        zC = float(df[df['Component'] == c_a[0]]['Charge'])

        m_a = float(df[df['Component'] == c_a[1]]['Molality'])
        zA = float(df[df['Component'] == c_a[0]]['Charge'])

        c_phi = float(binary_para.loc[(binary_para["Cation"] == c_a[0]) & 
                                       (binary_para["Anion"] == c_a[1]), "C (phi)"])

        C_ca = c_phi/(2*sqrt(abs(zC) * abs(zA)))

        fourth_term = fourth_term + (m_c*m_a*C_ca)

    fourth_term = abs(zM)*fourth_term
    
    return np.exp((zM**2 * F) + first_term + second_term + third_term + fourth_term)

def anion_activity_coefficient(df, target_ion, T = 298.15):
    empirical_path = pkg_resources.resource_filename('pySolution', 'core/empirical_parameters.xlsx')
    binary_path = pkg_resources.resource_filename('pySolution', 'core/binary_parameters.xlsx')
    
    binary_para = pd.read_excel(binary_path)
    mixing_para = pd.read_excel(empirical_path)
    A_ = A_calc(T)
    rho = density(df, T)
    
    molality = []
    for conc in np.array(df['Concentration (mol/L)']):
        molality.append(conc*(1/rho))
    
    d = {'Component' : np.array(df['Component']),
         'Molality' : molality,
         'Charge' : np.array(df['Charge'])
        }
    
    df = pd.DataFrame(d)
    
    A_ = A_calc()
    I = ionic_strength(df)
    F = F_calc(df, A_)
    Z = Z_calc(df)
    zX = float(df[df['Component'] == target_ion]['Charge'])

    cations = []
    anions = []

    for comp in df['Component']:
        if '+' in comp:
            cations.append(comp)
        elif '-' in comp:
            anions.append(comp)
    
    all_anion_combo = ion_combination(anions)
    all_cation_combo = ion_combination(cations)
    
    #first summation term
    first_term = 0

    for c in cations:
        #initialize beta terms and c_phi
        beta_0 = 0
        beta_1 = 0
        beta_2 = 0
        c_phi = 0

        #molality of anion "a"
        m_c = float(df[df['Component'] == c]['Molality'])
        z_c = float(df[df['Component'] == c]['Charge'])

        #get beta_0, beta_1, beta_2 of "Ma"
        beta_0 = float(binary_para.loc[(binary_para["Cation"] == c) & 
                                       (binary_para["Anion"] == target_ion), "Beta (0)"])
        beta_1 = float(binary_para.loc[(binary_para["Cation"] == c) & 
                                       (binary_para["Anion"] == target_ion), "Beta (1)"])
        beta_2 = float(binary_para.loc[(binary_para["Cation"] == c) & 
                                       (binary_para["Anion"] == target_ion), "Beta (2)"])
        c_phi = float(binary_para.loc[(binary_para["Cation"] == c) & 
                                       (binary_para["Anion"] == target_ion), "C (phi)"])

        Ccx = c_phi/(2*sqrt(abs(zX) * abs(z_c)))

        if abs(zX) == 1 or abs(z_c) == 1:
            alpha = 2
            g_original, _ = g(alpha*sqrt(I))
            Bcx = beta_0 + beta_1*g_original

        else:
            if abs(zX) == 2 and abs(z_c) == 2:
                alpha_1 = 1.4
                alpha_2 = 12
            else:
                alpha_1 = 2
                alpha_2 = 50

            g_original_1, _ = g(alpha_1*sqrt(I))
            g_original_2, _ = g(alpha_2*sqrt(I))

            Bcx = beta_0 + beta_1*g_original_1 + beta_2*g_original_2

        first_term = first_term + m_c*(2*Bcx + Z*Ccx)
    
    #second summation term
    second_term = 0

    for a in anions:
        theta_Xa = 0
        phi_Xa = 0

        #molality of anion "c"
        m_a = float(df[df['Component'] == a]['Molality'])
        z_a = float(df[df['Component'] == a]['Charge'])

        if target_ion != a:
            for index, row in mixing_para.iterrows():
                l_o = [row["i"], row["j"]]
                if (target_ion in l_o) and (a in l_o):
                    theta_Xa = row["theta_ij"]

            X_Xa = 6*abs(zX)*abs(z_a)*A_*sqrt(I)
            X_XX = 6*zX*zX*A_*sqrt(I)
            X_aa = 6*z_a*z_a*A_*sqrt(I)

            e_theta_Xa, _ = E_theta_prime(abs(zX), abs(z_a), A_, I)
            phi_Xa = theta_Xa + e_theta_Xa

        else:
            pass

        mc_psi = 0
        for c in cations:
            m_c = float(df[df['Component'] == c]['Molality'])
            for index, row in mixing_para.iterrows():
                l_o = [row["i"], row["j"], row["k"]]
                if (target_ion in l_o) and (c in l_o) and (a in l_o):
                    psi_ijk = row["psi_ijk"]

            mc_psi = mc_psi + (m_c * psi_ijk)

        second_term = second_term + m_a*(2*phi_Xa + mc_psi)
    
    #third term
    third_term = 0

    for c_c in all_cation_combo:
        m_c = float(df[df['Component'] == c_c[0]]['Molality'])
        m_c_prime = float(df[df['Component'] == c_c[1]]['Molality'])

        for index, row in mixing_para.iterrows():
            l_o = [row["i"], row["j"], row["k"]]
            if (c_c[0] in l_o) and (c_c[1] in l_o) and (target_ion in l_o):
                psi_ijk = row["psi_ijk"]

        third_term = third_term + (m_c * m_c_prime * psi_ijk)
    
    #fourth term
    fourth_term = 0

    for c_a in cation_anion(cations, anions):
        c_phi = 0

        m_c = float(df[df['Component'] == c_a[0]]['Molality'])
        zC = float(df[df['Component'] == c_a[0]]['Charge'])

        m_a = float(df[df['Component'] == c_a[1]]['Molality'])
        zA = float(df[df['Component'] == c_a[0]]['Charge'])

        c_phi = float(binary_para.loc[(binary_para["Cation"] == c_a[0]) & 
                                       (binary_para["Anion"] == c_a[1]), "C (phi)"])

        C_ca = c_phi/(2*sqrt(abs(zC) * abs(zA)))

        fourth_term = fourth_term + (m_c*m_a*C_ca)

    fourth_term = abs(zX)*fourth_term
    
    return np.exp((zX**2 * F) + first_term + second_term + third_term + fourth_term)
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

def cation_anion(cation, anion):
    """
    sigma(c) sigma(a)
    nested for loop for:
    
    algorithm
    for c in cation:
        for a in anion:
            #commit operation
    """
    c_a = []
    for x,y in product(cation, anion):
        c_a.append([x,y])
    
    return c_a

def ion_combination(ions):
    """
    returns all possible combinations of cations/anions
    ions -> either a list of cations or anions
    """
    all_pairs = []
    for L in range(0, len(ions) + 1):
        for subset in itertools.combinations(ions, L):
            if len(subset) == 2:
                all_pairs.append(list(subset))
    
    return all_pairs

def J_0_1(X):
    integral_0 = integrate.quad(lambda Y: (1 - exp(-(X/Y)*exp(-Y)))*Y**2, 0, inf)[0]
    integral_1 = integrate.quad(lambda Y: (1 - (1 + (X/Y)*exp(-Y))*exp(-(X/Y)*exp(-Y)))*Y**2, 0, inf)[0]
    
    J0 = (1/4)*X - 1 + (1/X)*integral_0
    J1 = (1/4)*X - (1/X)*integral_1
    
    return J0, J1

def E_theta_prime(zi, zj, A, I):
    X_ij = 6*zi*zj*A*sqrt(I)
    X_ii = 6*zi*zi*A*sqrt(I)
    X_jj = 6*zj*zj*A*sqrt(I)
    
    J0_ij, J1_ij = J_0_1(X_ij)
    J0_ii, J1_ii = J_0_1(X_ii)
    J0_jj, J1_jj = J_0_1(X_jj)
    
    e_theta_ij = ((zi*zj)/(4*I))*(J0_ij - 0.5*J0_ii - 0.5*J0_jj)
    e_theta_prime_ij = ((zi*zj)/(8*I**2))*(J1_ij - 0.5*J1_ii - 0.5*J1_jj) - e_theta_ij/I
    
    return e_theta_ij, e_theta_prime_ij

def g(X):
    g_original = (2*(1 - (1+X)*exp(-X)))/(X**2)
    g_prime = (-2*(1 - (1 + X + 0.5*X**2)*exp(-X)))/(X**2)
    
    return g_original, g_prime

def dielectric_constant(T = 298.15):
    """
    prediction of dielectric constant of h2o
    """
    with open('dielectric_model_h2o.pickle', 'rb') as f:
        clf = pickle.load(f)
    
    return clf.predict([[T - 273.15]])[0]
    
def A_calc(T = 298.15):
    """
    default:
    dielectric constant (D) = 78.2
    temperature (T) = 298.15 K
    """
    D = dielectric_constant(T)
    return 1400684*(1/(D*T))**(3/2)

def ionic_strength(test_df):
    I = 0
    for conc, charge in zip(test_df['Molality'], test_df['Charge']):
        I = I + conc*(charge**2)

    I = 0.5*I
    
    return I

def Cmx(c_phi, zm, zx):
    return c_phi/(2*sqrt(abs(zm)*abs(zx)))

def Z_calc(test_df):
    Z = 0
    for i, charge in zip(test_df['Molality'], test_df['Charge']):
        Z = Z + i*abs(charge)
    
    return Z

def F_calc(test_df, A_):
    binary_para = pd.read_excel("binary_parameters.xlsx")
    mixing_para = pd.read_excel("mixing_parameters.xlsx")
    b = 1.2
    I = ionic_strength(test_df)
    
    cations = []
    anions = []

    for comp in test_df['Component']:
        if '+' in comp:
            cations.append(comp)
        elif '-' in comp:
            anions.append(comp)
    
    all_anion_combo = ion_combination(anions)
    all_cation_combo = ion_combination(cations)
    
    first_term = 0
    for c_a in cation_anion(cations, anions):
        m_c = float(test_df[test_df['Component'] == c_a[0]]['Molality'])
        m_a = float(test_df[test_df['Component'] == c_a[1]]['Molality'])
        z_c = float(test_df[test_df['Component'] == c_a[0]]['Charge'])
        z_a = float(test_df[test_df['Component'] == c_a[1]]['Charge'])
        
        beta_1 = float(binary_para.loc[(binary_para["Cation"] == c_a[0]) & 
                                       (binary_para["Anion"] == c_a[1]), "Beta (1)"])
        
        beta_2 = float(binary_para.loc[(binary_para["Cation"] == c_a[0]) & 
                                       (binary_para["Anion"] == c_a[1]), "Beta (2)"])
        if abs(z_c) == 1 or abs(z_a) == 1:
            alpha = 2
            _, g_prime = g(alpha*np.sqrt(I))
            B_prime_ca = beta_1*(g_prime/I)
        elif abs(z_c) == 2 and abs(z_a) == 2:
            alpha_1 = 1.4
            alpha_2 = 12
            _, g_prime_1 = g(alpha_1*np.sqrt(I))
            _, g_prime_2 = g(alpha_2*np.sqrt(I))
            B_prime_ca = beta_1*(g_prime_1/I) + beta_2*(g_prime_2/I)
        else:
            alpha_1 = 2
            alpha_2 = 50
            _, g_prime_1 = g(alpha_1*np.sqrt(I))
            _, g_prime_2 = g(alpha_2*np.sqrt(I))
            B_prime_ca = beta_1*(g_prime_1/I) + beta_2*(g_prime_2/I)
        
        first_term = first_term + m_c*m_a*B_prime_ca
    
    second_term = 0
    for c_c in all_cation_combo:
        m_c = float(test_df[test_df['Component'] == c_c[0]]['Molality'])
        m_c_prime = float(test_df[test_df['Component'] == c_c[1]]['Molality'])
        
        z_c = float(test_df[test_df['Component'] == c_c[0]]['Charge'])
        z_c_prime = float(test_df[test_df['Component'] == c_c[1]]['Charge'])
        
        e_theta_cc, e_theta_prime_cc = E_theta_prime(z_c, z_c_prime, A_, I)
        second_term = second_term + (m_c*m_c_prime*e_theta_prime_cc)
    
    third_term = 0
    for a_a in all_anion_combo:
        m_a = float(test_df[test_df['Component'] == a_a[0]]['Molality'])
        m_a_prime = float(test_df[test_df['Component'] == a_a[1]]['Molality'])
        
        z_a = float(test_df[test_df['Component'] == a_a[0]]['Charge'])
        z_a_prime = float(test_df[test_df['Component'] == a_a[1]]['Charge'])
        
        e_theta_aa, e_theta_prime_aa = E_theta_prime(z_a, z_a_prime, A_, I)
        third_term = third_term + (m_a*m_a_prime*e_theta_prime_aa)
        
    return -A_*((sqrt(I))/(1 + b*sqrt(I)) + (2/b)*np.log(1 + b*sqrt(I))) + first_term + second_term + third_term
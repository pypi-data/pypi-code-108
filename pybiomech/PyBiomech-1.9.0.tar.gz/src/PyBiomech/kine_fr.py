"""
.. module:: kine_fr
   :synopsis: helper module for kinematics for foot-rig

"""


import numpy as np
from .kine import getVersor

    


def tibiaFR(mkrs, s='R'):

    TIMM = mkrs['TIMM']
    TILM = mkrs['TILM']
    CFA = mkrs['CFA']

    O = (TIMM + TILM) / 2.
    
    Z = getVersor(TIMM - TILM)
    if s == 'R':
        Z = -Z
    X = getVersor(np.cross(TIMM - CFA, TILM - CFA))
    Y = getVersor(np.cross(Z, X))
    
    R = np.array((X.T, Y.T, Z.T))   # 3 x 3 x N
    R = np.transpose(R, (2,1,0))  # N x 3 x 3

    return R, O



def talusFR(mkrs, s='R'):

    TAHC = mkrs['TAHC']
    TAMP = mkrs['TAMP']
    TAML = mkrs['TAML']

    O = TAMP.copy()
    
    X = getVersor(TAHC - TAMP)
    Y = getVersor(np.cross(TAHC - TAMP, TAML - TAMP))
    Z = getVersor(np.cross(X, Y))

    R = np.array((X.T, Y.T, Z.T))   # 3 x 3 x N
    R = np.transpose(R, (2,1,0))  # N x 3 x 3

    return R, O



def calcaneusFR(mkrs, s='R'):

    CT = mkrs['CT']
    CMTT = mkrs['CMTT']
    CAF = mkrs['CAF']
    
    O = CMTT.copy()
    
    X = getVersor(CT - CMTT)
    Z = getVersor(np.cross(CT - CAF, CMTT - CAF))
    Y = getVersor(np.cross(Z, X))
    
    R = np.array((X.T, Y.T, Z.T))   # 3 x 3 x N
    R = np.transpose(R, (2,1,0))  # N x 3 x 3

    return R, O



def navicularFR(mkrs, s='R'):

    NAC = mkrs['NAC']
    NAAF = mkrs['NAAF']
    NAM = mkrs['NAM']
    
    O = NAC.copy()
    
    X = getVersor(NAAF - NAC)
    Y = getVersor(np.cross(NAC - NAM, NAAF - NAM))
    Z = getVersor(np.cross(X, Y))
    
    R = np.array((X.T, Y.T, Z.T))   # 3 x 3 x N
    R = np.transpose(R, (2,1,0))  # N x 3 x 3

    return R, O



def cuboidFR(mkrs, s='R'):

    CUPS = mkrs['CUPS']
    CUAS = mkrs['CUAS']
    CUPP = mkrs['CUPP']
    
    O = CUPS.copy()
    
    X = getVersor(CUAS - CUPS)
    Z = getVersor(np.cross(CUPS - CUPP, CUAS - CUPP))
    Y = getVersor(np.cross(Z, X))
    
    R = np.array((X.T, Y.T, Z.T))   # 3 x 3 x N
    R = np.transpose(R, (2,1,0))  # N x 3 x 3

    return R, O



def firstMetatarsalFR(mkrs, s='R'):

    MT1H = mkrs['MT1H']
    MT1I = mkrs['MT1I']
    MT1S = mkrs['MT1S']
    
    O = MT1I.copy()
    
    X = getVersor(MT1H - MT1I)
    Z = getVersor(np.cross(MT1H - MT1S, MT1I - MT1S))
    Y = getVersor(np.cross(Z, X))
    
    R = np.array((X.T, Y.T, Z.T))   # 3 x 3 x N
    R = np.transpose(R, (2,1,0))  # N x 3 x 3

    return R, O
    
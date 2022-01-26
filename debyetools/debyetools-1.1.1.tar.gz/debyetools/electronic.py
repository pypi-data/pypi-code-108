import numpy as np
from scipy.optimize import leastsq

NAv  = 0.6022140857e24
kB   = 0.138064852e-22

class Electronic:
    """
    Implementation of the electronic contribution to the free energy.

    :param float params: N(Ef)(V) function parameters.
    """
    def __init__(self,*params):
        self.r=1
        for n,q in enumerate(params):
            setattr(self,'q'+str(n),q)

    def NfV(self,V):
        """
        N(Ef)(V)

        :param float V: Volume.
        """
        return self.q0*V**0 + self.q1*V**1 + self.q2*V**2 + self.q3*V**3
    def dNfVdV_T(self,V):
        return 3*V**2*self.q3+2*V*self.q2+self.q1
    def d2NfVdV2_T(self,V):
        return 6*V*self.q3+2*self.q2
    def d3NfVdV3_T(self,V):
        return 6*self.q3
    def d4NfVdV4_T(self,V):
        return 0

    def E(self,T,V):
        return (1/6)*np.pi**2*NAv*self.r*kB**2*T**2*self.NfV(V)/(0.160218e-18)
    def S(self,T,V):
        return (2/6)*np.pi**2*NAv*self.r*kB**2*T*self.NfV(V)/(0.160218e-18)
    def F(self,T,V):
        """
        Electronic contribution to the free energy.

        :param float T: Temperature.
        :param float V: Volume.
        """
        return - (1/6)*np.pi**2*NAv*self.r*kB**2*T**2*self.NfV(V)/(0.160218e-18)
    def d2FdT2_V(self,T,V):
        return - 2*np.pi**2*NAv*self.r*kB**2*self.NfV(V)*(1/6)/(0.160218e-18)
    def d2FdV2_T(self,T,V):
        return - (1/6)*np.pi**2*NAv*self.r*kB**2*T**2*self.d2NfVdV2_T(V)/(0.160218e-18)
    def d3FdV3_T(self,T,V):
        return - (1/6)*np.pi**2*NAv*self.r*kB**2*T**2*self.d3NfVdV3_T(V)/(0.160218e-18)
    def d4FdV4_T(self,T,V):
        return - (1/6)*np.pi**2*NAv*self.r*kB**2*T**2*self.d4NfVdV4_T(V)/(0.160218e-18)

    def d2FdVdT(self,T,V):
        return -2*np.pi**2*NAv*self.r*kB**2*T*self.dNfVdV_T(V)*(1/6)/(0.160218e-18)
    def d3FdV2dT(self,T,V):
        return -2*np.pi**2*NAv*self.r*kB**2*T*self.d2NfVdV2_T(V)*(1/6)/(0.160218e-18)
    def d3FdVdT2(self,T,V):
        return -2*np.pi**2*NAv*self.r*kB**2*self.dNfVdV_T(V)*(1/6)/(0.160218e-18)

def fit_electronic(Vs, p_el,E,N,Ef):
    """
    Fitting procedure for the N(Ef)(V) function.

    :param list_of_floats Vs: Volumes.
    :param list_of_floats p_el: Initial parameters.
    :param list_of_lists_of_floats E: Matrix with energies at each level for each volume.
    :param list_of_lists_of_floats N: Matrix with densities of state at each level for each volume.
    :param list_of_floats Ef: Fermi levels as function of temperature.

    :retun list_of_floats: optimized parameters.
    """

    V = np.array(Vs)
    ix_V0=10
    EfV0 = float(Ef[ix_V0])
    ixs=[i for i,x in enumerate(E[ix_V0]) if x>=Ef[ix_V0]]
    E1 = float(E[ix_V0][ixs[0]-1])
    E2 = float(E[ix_V0][ixs[0]])
    N1 = float(N[ix_V0][ixs[0]-1])
    N2 = float(N[ix_V0][ixs[0]])
    NfV0 = (EfV0 - E1)*(N2 - N1)/(E2 - E1) + N1
    NfV = np.array([NfV0*np.sqrt(ef/EfV0) for ef in Ef][8:-1])
    P2 = leastsq(NfV2m, p_el, args=(V[8:-1], NfV),maxfev=1000)
    P2 = P2[0]

    return P2

def NfV_poly_fun(V, _A, _B, _C, _D):
    #A, B, C = A*1e-1, B*(-1e4), C*1e-9
    return _A + _B*V + _C*V**2 + _D*V**3

def NfV2m(P, Vdata, NfVdata):
    NfVcalc = [NfV_poly_fun(Vi, P[0], P[1], P[2], P[3]) for Vi in Vdata]
    # print('NfVcalc', NfVcalc, 'NfVdata', NfVdata)
    return NfVcalc-NfVdata

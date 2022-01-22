import numpy as np
from scipy.optimize import fmin

from debyetools.anharmonicity import Anharmonicity, intAnharmonicity
from debyetools.electronic import Electronic
from debyetools.defects import Defects
from debyetools.vibrational import Vibrational
import debyetools.potentials as pots
from debyetools.debfunct import D_3, dD_3dx, d2D_3dx2, d3D_3dx3
hbar = 0.1054571800e-33
NAv  = 0.6022140857e24
kB   = 0.138064852e-22


class nDeb:
    """
    Instantiate an object that contains all the parameters for the evaluation of
    the thermodynamic properties of a certain element or compound. Also contains
    the method that implements an original Debye formalism for the calculation of
    the thermodynamic properties

    :param float nu: Poisson's ratio.
    :param float m: mass in Kg/mol-at
    :param list_of_floats p_intanh: Intrinsic anharmonicity parameters: a0, m0, V0.
    :param list_of_floats p_EOS: Equation of state parameters.
    :param list_of_floats p_electronic: Electronic contribution parameters.
    :param list_of_floats p_defects: Mono-vacancies defects contribution parameters: Evac00,Svac00,Tm,a,P2,V0.
    :param list_of_floats p_anh: Excess contribution parameters.
    :param string EOS_name: The EOS or potential to use as internal energy description.
    """
    def __init__(self, nu, m, p_intanh, EOS, p_electronic, p_defects, p_anh,*args,units='J/mol'):
        a0, m0 = p_intanh
        q0,q1,q2,q3 = p_electronic
        Evac00,Svac00,Tm,a = p_defects
        s0,s1,s2 = p_anh

        self.nu, self.r, self.m = nu, 1, m


        self.kv = (2./3.*((2. + 2.*nu)/(3.-6.*nu))**(3./2.) + 1./3.*((1. + nu)/(3. - 3.*nu))**(3./2.))**(-1./3.)

        self.anh = Anharmonicity(s0,s1,s2)
        self.intanh = intAnharmonicity(a0,m0,EOS.V0)
        self.el = Electronic(q0,q1,q2,q3)
        self.deff = Defects(Evac00,Svac00,Tm,a,EOS.V0*EOS.d2E0dV2_T(EOS.V0),EOS.V0)

        self.EOS = EOS#getattr(pots,EOS_name)(*args,units=units, parameters = p_EOS)
        # self.EOS.pEOS = p_EOS
        self.vib = Vibrational(nu, self.EOS, m, self.intanh)

        r=1
        self.xDcte = hbar*6**(1/3.)*(np.pi**2*NAv*r)**(1/3.)

    def G(self,T,V, P):
        """
        Helmholtz free energy.

        :param float T: Temperature.
        :param float V: Volume.
        :param float P: Pressure.

        :return float: Free energy.
        """

        E_0 = self.EOS.E0(V)

        Fvib = self.vib.F(T,V)#3*r*NAv*kB*(tD*3/8 + T*np.log(1-np.exp(-x))  - D3*T/3)
        Fa = self.anh.F(T,V)
        Fdef = self.deff.F(T,V)
        Fel = self.el.F(T,V)
        _F = E_0 + Fvib + Fel + Fdef + Fa
        return _F + P*V

    def min_G(self,T, initial_V, P):
        """
        Procedure for the calculation of the volume as function of temperature.

        :param list_of_floats T: Temperature.
        :param float initial_V: initial guess.

        :return list_of_floats: Temperature.
        :return list_of_floats: Equilibrium Volume as function of the temperature.
        """
        V0i=initial_V
        V=[]
        for Ti in T:
            f2min = lambda Vi: self.G(Ti,Vi,P=P)
            V0i = fmin(f2min,x0=V0i,disp=False)[0]
            V.append(V0i)

        newV = np.array(V)
        del V

        ixs = np.where(newV<=1.5*newV[0])
        Tmax = T[-1]
        T,V = T[ixs],newV[ixs]

        return T,V

    def eval_props(self, T, V, P):
        """
        Evaluates the thermodynamic properties of a given compound/element at (T,V).

        :params float T: The temperature in Kelvin.
        :params float V: The volume in "units".

        :return float: The heat capacity for the moment.
        """
        nu, r, m = self.nu,self.r,self.m

        kv = self.kv

        self.vib.set_int_anh(T, V)
        self.vib.set_theta(T, V)

        d2E0dV2_T = self.EOS.d2E0dV2_T(V)
        d3E0dV3_T = self.EOS.d3E0dV3_T(V)
        d4E0dV4_T = self.EOS.d4E0dV4_T(V)

        d2E0dT2_V = 0
        d2E0dVdT  = 0
        d3E0dV2dT  = 0
        d3E0dVdT2  = 0

        d2FvibdT2_V = self.vib.d2FdT2_V(T, V)#3*r*NAv*((ex-1)*T*(T**2*d2tDdT2_V*tD-4*(dtDdT_V*T-tD)**2)*D3+3*tD*(d2tDdT2_V*tD*ex*T**2-T**2*d2tDdT2_V*tD+8*(dtDdT_V*T-tD)**2)*(1/8))*kB/(tD**2*(ex-1)*T**2)
        d2FvibdV2_T = self.vib.d2FdV2_T(T, V)#3*r*NAv*kB*(8*dtDdV_T**2*tD*dD3dx-8*dtDdV_T**2*D3*T+8*d2tDdV2_T*D3*tD*T+3*d2tDdV2_T*tD**2)/(8*tD**2)
        d3FvibdV3_T = self.vib.d3FdV3_T(T, V)#3*r*(T**2*(d3tDdV3_T*tD**2-3*dtDdV_T*d2tDdV2_T*tD+2*dtDdV_T**3)*D3+(3*dtDdV_T*d2tDdV2_T*T*tD**2-2*dtDdV_T**3*T*tD)*dD3dx+d2D3dx2*dtDdV_T**3*tD**2+3*d3tDdV3_T*tD**3*T*(1/8))*kB*NAv/(T*tD**3)
        d4FvibdV4_T = self.vib.d4FdV4_T(T, V)#-12*r*(T**3*(-(1/4)*d4tDdV4_T*tD**3+(d3tDdV3_T*dtDdV_T+3*d2tDdV2_T**2*(1/4))*tD**2-3*dtDdV_T**2*d2tDdV2_T*tD+3*dtDdV_T**4*(1/2))*D3-tD*(T**2*((d3tDdV3_T*dtDdV_T+3*d2tDdV2_T**2*(1/4))*tD**2-3*dtDdV_T**2*d2tDdV2_T*tD+3*dtDdV_T**4*(1/2))*dD3dx+(1/32)*(3*((16*dtDdV_T**2*d2tDdV2_T*tD*T-8*dtDdV_T**4*T)*d2D3dx2+tD*(8*d3D3dx3*dtDdV_T**4*(1/3)+d4tDdV4_T*tD*T**2)))*tD))*kB*NAv/(T**2*tD**4)
        d2FvibdVdT  = self.vib.d2FdVdT(T, V) # 3*r*(dD3dx*(dtDdT_V/T-tD/T**2)*T+D3+3*dtDdT_V*(1/8))*kB*dtDdV_T*NAv/tD+3*r*(D3*T+3*tD*(1/8))*kB*d2tDdVdT*NAv/tD-3*r*(D3*T+3*tD*(1/8))*kB*dtDdV_T*NAv*dtDdT_V/tD**2
        d3FvibdV2dT = self.vib.d3FdV2dT(T,V)#-3*r*(T**2*((-T*d3tDdV2dT-d2tDdV2_T)*tD**2+(T*d2tDdV2_T*dtDdT_V+2*T*dtDdV_T*d2tDdVdT+dtDdV_T**2)*tD-2*T*dtDdT_V*dtDdV_T**2)*D3-tD*((-d2tDdV2_T*tD**2+(T*d2tDdV2_T*dtDdT_V+2*T*dtDdV_T*d2tDdVdT+dtDdV_T**2)*tD-2*T*dtDdT_V*dtDdV_T**2)*T*dD3dx+3*tD*(8*dtDdV_T**2*(T*dtDdT_V-tD)*d2D3dx2*(1/3)+tD*d3tDdV2dT*T**2)*(1/8)))*kB*NAv/(T**2*tD**3)
        d3FvibdVdT2 = self.vib.d3FdVdT2(T,V)#-(6*(T**3*((-(1/2)*d3tDdVdT2*T-d2tDdVdT)*tD**2+(((1/2)*d2tDdT2_V*T+dtDdT_V)*dtDdV_T+dtDdT_V*d2tDdVdT*T)*tD-dtDdT_V**2*dtDdV_T*T)*D3-(T**2*(-tD**2*d2tDdVdT+(((1/2)*d2tDdT2_V*T+dtDdT_V)*dtDdV_T+dtDdT_V*d2tDdVdT*T)*tD-dtDdT_V**2*dtDdV_T*T)*dD3dx+(1/16)*(3*(8*dtDdV_T*(T*dtDdT_V-tD)**2*d2D3dx2*(1/3)+tD*d3tDdVdT2*T**3))*tD)*tD))*r*kB*NAv/(T**3*tD**3)

        d2FeldT2_V  = self.el.d2FdT2_V(T,V)
        d2FeldV2_T  = self.el.d2FdV2_T(T,V)
        d3FeldV3_T  = self.el.d3FdV3_T(T,V)
        d4FeldV4_T  = self.el.d4FdV4_T(T,V)
        d2FeldVdT   = self.el.d2FdVdT(T,V)
        d3FeldV2dT   = self.el.d3FdV2dT(T,V)
        d3FeldVdT2   = self.el.d3FdVdT2(T,V)

        d2FdefdT2_V = self.deff.d2FdT2_V(T,V)
        d2FdefdV2_T = self.deff.d2FdV2_T(T,V)
        d3FdefdV3_T = self.deff.d3FdV3_T(T,V)
        d4FdefdV4_T = self.deff.d4FdV4_T(T,V)
        d2FdefdVdT  = self.deff.d2FdVdT(T,V)
        d3FdefdV2dT  = self.deff.d3FdV2dT(T,V)
        d3FdefdVdT2  = self.deff.d3FdVdT2(T,V)

        d2FadT2_V   = self.anh.d2FdT2_V(T,V)
        d2FadV2_T   = self.anh.d2FdV2_T(T,V)
        d3FadV3_T   = self.anh.d3FdV3_T(T,V)
        d4FadV4_T   = self.anh.d4FdV4_T(T,V)
        d2FadVdT    = self.anh.d2FdVdT(T,V)
        d3FadV2dT    = self.anh.d3FdV2dT(T,V)
        d3FadVdT2    = self.anh.d3FdVdT2(T,V)

        d2FdT2_V = d2E0dT2_V + d2FvibdT2_V + d2FeldT2_V + d2FdefdT2_V + d2FadT2_V
        d2FdV2_T = d2E0dV2_T + d2FvibdV2_T + d2FeldV2_T + d2FdefdV2_T + d2FadV2_T
        d3FdV3_T = d3E0dV3_T + d3FvibdV3_T + d3FeldV3_T + d3FdefdV3_T + d3FadV3_T
        d4FdV4_T = d4E0dV4_T + d4FvibdV4_T + d4FeldV4_T + d4FdefdV4_T + d4FadV4_T
        d2FdVdT  = d2E0dVdT + d2FvibdVdT + d2FeldVdT + d2FdefdVdT + d2FadVdT
        d3FdV2dT  = d3E0dV2dT + d3FvibdV2dT + d3FeldV2dT + d3FdefdV2dT + d3FadV2dT
        d3FdVdT2  = d3E0dVdT2 + d3FvibdVdT2 + d3FeldVdT2 + d3FdefdVdT2 + d3FadVdT2

        tD        = self.vib.tD
        g    = -V/(tD)*self.vib.dtDdV_T
        dPdV_T = - d2FdV2_T
        d2PdV2_T = - d3FdV3_T
        d3PdV3_T = - d4FdV4_T
        Kt = - V*dPdV_T
        dKtdV_T = - dPdV_T - V*d2PdV2_T
        dKtdP_T = dKtdV_T/dPdV_T
        d2KtdV2_T = -2*d2PdV2_T-V*d3PdV3_T
        d2KtdP2_T = (d2KtdV2_T/dPdV_T-dKtdV_T*d2PdV2_T/dPdV_T**2)/dPdV_T
        Ktp = dKtdP_T
        Ktpp = d2KtdP2_T
        Cv = -T*d2FdT2_V
        dPdT_V = - d2FdVdT
        dVdT_P = - dPdT_V/dPdV_T
        a  = 1/V*dVdT_P


        Cp = -T*( d2FdT2_V - (d2FdVdT)**2 / d2FdV2_T)

        Ks = Kt*Cp/Cv
        dCpdV_T = T*(2*d2FdVdT*d2FdV2_T*d3FdV2dT-d2FdVdT**2*d3FdV3_T-d3FdVdT2*d2FdV2_T**2)/d2FdV2_T**2
        dCvdV_T = -T*d3FdVdT2
        dKsdV_T = dKtdV_T*Cp/Cv+Kt*dCpdV_T/Cv-Kt*Cp*dCvdV_T/Cv**2

        dKsdP_T = dKsdV_T/dPdV_T
        Ksp = dKsdP_T
        G = self.G(T, V, P=P)

        Evib = self.vib.E(T,V)
        Eel = self.el.E(T,V)
        Edef = self.deff.E(T,V)
        Ea = self.anh.E(T,V)
        E0 = d2E0dV2_T = self.EOS.E0(V)
        E = E0 + Evib + Eel + Edef + Ea

        Svib = self.vib.S(T,V)
        Sel = self.el.S(T,V)
        Sdef = self.deff.S(T,V)
        Sa = self.anh.S(T,V)
        S = Svib + Sel + Sdef + Sa

        Fvib = self.vib.F(T,V)
        Evib = self.vib.E(T,V)
        Svib = self.vib.S(T,V)

        Cvvib = -T*d2FvibdT2_V
        dE0dV_T = self.EOS.dE0dV_T(V)
        Pcold = -dE0dV_T
        return {'T':T,'V':V,'tD':tD,'g':g,'Kt':Kt,'Ktp':Ktp,'Ktpp':Ktpp,
                'Cv':Cv,'a':a,'Cp':Cp,'Ks':Ks,'Ksp':Ksp,
                'G':G,'E':E,'S':S,'E0':E0,'Fvib':Fvib,'Evib':Evib,'Svib':Svib,
                'Cvvib':Cvvib,'Pcold':Pcold,'dPdT_V':dPdT_V,'G^2':Ktp**2-2*Kt*Ktpp}

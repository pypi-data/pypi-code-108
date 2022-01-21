import numpy as np
from debyetools.debfunct import D_3, dD_3dx, d2D_3dx2, d3D_3dx3
hbar = 0.1054571800e-33
NAv  = 0.6022140857e24
kB   = 0.138064852e-22
r = 1
class Vibrational:
    """
    Instanceiate the vibrational contribution to the free energy and its derivatives for the calculation of the thermodynamic properties.

    :param float nu: Poisson's ratio.
    :param potential_instance EOS_obj: Equation of state object.
    :param float m: Mass in Kg/mol-at.
    :param intAnharmonicity_instance intanh: Intrinsic anharmonicity object.
    """
    def __init__(self, nu, EOS_obj, m, intanh):
        self.EOS = EOS_obj
        self.kv = (2./3.*((2. + 2.*nu)/(3.-6.*nu))**(3./2.) + 1./3.*((1. + nu)/(3. - 3.*nu))**(3./2.))**(-1./3.)
        self.m = m
        self.intanh = intanh

        self.xDcte = hbar*6**(1/3.)*(np.pi**2*NAv*r)**(1/3.)

    def set_int_anh(self, T, V):
        """
        Calculates intrinsic anharmonicity correction to the Debye temperature and its derivatibes.

        :param float T: Temperature.
        :param float V: Volume.
        """
        self.Anh         = self.intanh.Anh(T,V)
        self.dAnhdT_V    = self.intanh.dAnhdT_V()
        self.dAnhdV_T    = self.intanh.dAnhdV_T(T,V)
        self.d2AnhdVdT   = self.intanh.d2AnhdVdT(T)
        self.d2AnhdV2_T  = self.intanh.d2AnhdV2_T(T,V)
        self.d2AnhdT2_V  = self.intanh.d2AnhdT2_V()
        self.d3AnhdV2dT  = self.intanh.d3AnhdV2dT(T,V)
        self.d3AnhdVdT2  = self.intanh.d3AnhdVdT2(T)
        self.d3AnhdV3_T  = self.intanh.d3AnhdV3_T(T,V)
        self.d4AnhdV4_T  = self.intanh.d4AnhdV4_T(T,V)

    def set_theta(self, T, V):
        """
        Calculates the Debye Temperature and its derivatives.

        :param float T: Temperature.
        :param float V: Volume.
        """
        kv = self.kv
        m = self.m
        d2E0dV2_T = self.EOS.d2E0dV2_T(V)
        d3E0dV3_T = self.EOS.d3E0dV3_T(V)
        d4E0dV4_T = self.EOS.d4E0dV4_T(V)
        d5E0dV5_T = self.EOS.d5E0dV5_T(V)
        d6E0dV6_T = self.EOS.d6E0dV6_T(V)
        dP0dV   = - d2E0dV2_T
        d2P0dV2 = - d3E0dV3_T
        d3P0dV3 = - d4E0dV4_T
        d4P0dV4 = - d5E0dV5_T
        d5P0dV5 = - d6E0dV6_T
        vDPrm  = - dP0dV/(r*m)
        vDsqrt = np.sqrt( vDPrm)
        vD      = kv*V*vDsqrt
        dvDdV   = kv*vDsqrt-kv*V*d2P0dV2/(2*vDsqrt*r*m)
        d2vDdV2 = -kv*d2P0dV2/(vDsqrt*r*m)-kv*V*d2P0dV2**2/(4*(vDPrm)**(3/2)*r**2*m**2)-kv*V*d3P0dV3/(2*vDsqrt*r*m)
        d3vDdV3 = -3*kv*d2P0dV2**2/(4*(vDPrm)**(3/2)*r**2*m**2)-3*kv*d3P0dV3/(2*vDsqrt*r*m)-3*kv*V*d2P0dV2**3/(8*(vDPrm)**(5/2)*r**3*m**3)-3*kv*V*d2P0dV2*d3P0dV3/(4*(vDPrm)**(3/2)*r**2*m**2)-kv*V*d4P0dV4/(2*vDsqrt*r*m)
        d4vDdV4 = -3*kv*(d2P0dV2)**3/(2*(-dP0dV/(r*m))**(5/2)*r**3*m**3)-3*kv*(d2P0dV2)*(d3P0dV3)/((-dP0dV/(r*m))**(3/2)*r**2*m**2)-2*kv*(d4P0dV4)/(np.sqrt(-dP0dV/(r*m))*r*m)-15*kv*V*(d2P0dV2)**4/(16*(-dP0dV/(r*m))**(7/2)*r**4*m**4)-9*kv*V*(d2P0dV2)**2*(d3P0dV3)/(4*(-dP0dV/(r*m))**(5/2)*r**3*m**3)-3*kv*V*(d3P0dV3)**2/(4*(-dP0dV/(r*m))**(3/2)*r**2*m**2)-kv*V*(d2P0dV2)*(d4P0dV4)/((-dP0dV/(r*m))**(3/2)*r**2*m**2)-kv*V*(d5P0dV5)/(2*np.sqrt(-dP0dV/(r*m))*r*m)
        xD      = self.xDcte*(1/V)**(1/3.)/kB
        dxDdV   = - self.xDcte/(3*kB*V**(4/3.))
        d2xDdV2 = 4*self.xDcte/(9*kB*V**(7/3.))
        d3xDdV3 = -28*self.xDcte/(27*V**(10/3)*kB)
        d4xDdV4 = 280*self.xDcte/(81*V**(13/3)*kB)
        self.tD = xD*vD*self.Anh
        self.dtDdV_T   = dxDdV*vD*self.Anh + xD*dvDdV*self.Anh + xD*vD*self.dAnhdV_T
        self.dtDdT_V   = xD*vD*self.dAnhdT_V
        self.d2tDdV2_T = d2xDdV2*vD*self.Anh + 2*dxDdV*dvDdV*self.Anh + 2*dxDdV*vD*self.dAnhdV_T + xD*d2vDdV2*self.Anh + 2*xD*dvDdV*self.dAnhdV_T + xD*vD*self.d2AnhdV2_T
        self.d2tDdT2_V = xD*vD*self.d2AnhdT2_V
        self.d2tDdVdT  = dxDdV*vD*self.dAnhdT_V + xD*dvDdV*self.dAnhdT_V + xD*vD*self.d2AnhdVdT
        self.d3tDdV3_T = d3xDdV3*vD*self.Anh + 3*d2xDdV2*dvDdV*self.Anh + 3*d2xDdV2*vD*self.dAnhdV_T + 3*dxDdV*d2vDdV2*self.Anh + 6*dxDdV*dvDdV*self.dAnhdV_T + 3*dxDdV*vD*self.d2AnhdV2_T + xD*d3vDdV3*self.Anh + 3*xD*d2vDdV2*self.dAnhdV_T + 3*xD*dvDdV*self.d2AnhdV2_T + xD*vD*self.d3AnhdV3_T
        self.d3tDdV2dT = d2xDdV2*vD*self.dAnhdT_V + 2*dxDdV*dvDdV*self.dAnhdT_V + 2*dxDdV*vD*self.d2AnhdVdT + xD*d2vDdV2*self.dAnhdT_V + 2*xD*dvDdV*self.d2AnhdVdT + xD*vD*self.d3AnhdV2dT
        self.d3tDdVdT2 = dxDdV*vD*self.d2AnhdT2_V + xD*dvDdV*self.d2AnhdT2_V + xD*vD*self.d3AnhdVdT2
        self.d4tDdV4_T = xD*vD*self.d4AnhdV4_T + d4xDdV4*vD*self.Anh + 4*d3xDdV3*dvDdV*self.Anh + 4*d3xDdV3*vD*self.dAnhdV_T + 6*d2xDdV2*d2vDdV2*self.Anh + 12*d2xDdV2*dvDdV*self.dAnhdV_T + 6*d2xDdV2*vD*self.d2AnhdV2_T + 4*dxDdV*d3vDdV3*self.Anh + 12*dxDdV*d2vDdV2*self.dAnhdV_T + 12*dxDdV*dvDdV*self.d2AnhdV2_T + 4*dxDdV*vD*self.d3AnhdV3_T + xD*d4vDdV4*self.Anh + 4*xD*d3vDdV3*self.dAnhdV_T + 6*xD*d2vDdV2*self.d2AnhdV2_T + 4*xD*dvDdV*self.d3AnhdV3_T

    def E(self, T, V):
        x = self.tD/T
        D3 = D_3(x)

        return -(3*(self.dtDdT_V*T-self.tD))*r*NAv*kB*(T*D3+3*self.tD*(1/8))/self.tD

    def S(self, T, V):
        x = self.tD/T
        D3 = D_3(x)
        
        return -3*kB*(np.log(1-np.exp(-self.tD/T))*self.tD+(self.dtDdT_V*T-4*self.tD*(1/3))*D3+3*self.dtDdT_V*self.tD*(1/8))*r*NAv/self.tD
    def F(self, T, V):
        """
        Vibration Helmholtz free energy.

        :param float T: Temperature.
        :param float V: Volume.
        """
        d2E0dV2_T = self.EOS.d2E0dV2_T(V)
        if type(V) == np.ndarray:
            if min(d2E0dV2_T)<0:return 1
        kv = self.kv
        m = self.m

        dP0dV   = - d2E0dV2_T

        Anh         = self.intanh.Anh(T,V)
        xDcte = self.xDcte
        xD      = xDcte*(1/V)**(1/3.)/kB
        vDPrm  = - dP0dV/(r*m)
        vDsqrt = np.sqrt( vDPrm)
        vD      = kv*V*vDsqrt
        tD        = xD*vD*Anh

        x = tD/T
        D3 = D_3(x)
        return 3*r*NAv*kB*(tD*3/8 + T*np.log(1-np.exp(-x))  - D3*T/3)
    def d2FdT2_V(self,T,V):
        """
        (d2F(T,V)/dT2)_V

        :param float T: Temperature.
        :param float V: Volume.
        """
        x = self.tD/T
        ex = np.exp(x)
        D3      = D_3(x)
        return 3*r*NAv*((ex-1)*T*(T**2*self.d2tDdT2_V*self.tD-4*(self.dtDdT_V*T-self.tD)**2)*D3+3*self.tD*(self.d2tDdT2_V*self.tD*ex*T**2-T**2*self.d2tDdT2_V*self.tD+8*(self.dtDdT_V*T-self.tD)**2)*(1/8))*kB/(self.tD**2*(ex-1)*T**2)

    def d2FdV2_T(self,T,V):
        """
        (d2F(T,V)/dV2)_T

        :param float T: Temperature.
        :param float V: Volume.
        """
        x = self.tD/T
        D3      = D_3(x)
        dD3dx   = dD_3dx(x,D3)
        return 3*r*NAv*kB*(8*self.dtDdV_T**2*self.tD*dD3dx-8*self.dtDdV_T**2*D3*T+8*self.d2tDdV2_T*D3*self.tD*T+3*self.d2tDdV2_T*self.tD**2)/(8*self.tD**2)

    def d3FdV3_T(self,T,V):
        """
        (d3F(T,V)/dV3)_T

        :param float T: Temperature.
        :param float V: Volume.
        """
        x = self.tD/T
        D3      = D_3(x)
        dD3dx   = dD_3dx(x,D3)
        d2D3dx2 = d2D_3dx2(x,D3,dD3dx)
        return 3*r*(T**2*(self.d3tDdV3_T*self.tD**2-3*self.dtDdV_T*self.d2tDdV2_T*self.tD+2*self.dtDdV_T**3)*D3+(3*self.dtDdV_T*self.d2tDdV2_T*T*self.tD**2-2*self.dtDdV_T**3*T*self.tD)*dD3dx+d2D3dx2*self.dtDdV_T**3*self.tD**2+3*self.d3tDdV3_T*self.tD**3*T*(1/8))*kB*NAv/(T*self.tD**3)

    def d4FdV4_T(self,T,V):
        """
        (d4F(T,V)/dV4)_T

        :param float T: Temperature.
        :param float V: Volume.
        """
        x = self.tD/T
        D3      = D_3(x)
        dD3dx   = dD_3dx(x,D3)
        d2D3dx2 = d2D_3dx2(x,D3,dD3dx)
        d3D3dx3 = d3D_3dx3(x,D3,dD3dx,d2D3dx2)

        return -12*r*(T**3*(-(1/4)*self.d4tDdV4_T*self.tD**3+(self.d3tDdV3_T*self.dtDdV_T+3*self.d2tDdV2_T**2*(1/4))*self.tD**2-3*self.dtDdV_T**2*self.d2tDdV2_T*self.tD+3*self.dtDdV_T**4*(1/2))*D3-self.tD*(T**2*((self.d3tDdV3_T*self.dtDdV_T+3*self.d2tDdV2_T**2*(1/4))*self.tD**2-3*self.dtDdV_T**2*self.d2tDdV2_T*self.tD+3*self.dtDdV_T**4*(1/2))*dD3dx+(1/32)*(3*((16*self.dtDdV_T**2*self.d2tDdV2_T*self.tD*T-8*self.dtDdV_T**4*T)*d2D3dx2+self.tD*(8*d3D3dx3*self.dtDdV_T**4*(1/3)+self.d4tDdV4_T*self.tD*T**2)))*self.tD))*kB*NAv/(T**2*self.tD**4)

    def d2FdVdT(self,T,V):
        """
        (d2F(T,V)/dVdT)

        :param float T: Temperature.
        :param float V: Volume.
        """
        x = self.tD/T
        D3      = D_3(x)
        dD3dx   = dD_3dx(x,D3)
        return 3*r*(dD3dx*(self.dtDdT_V/T-self.tD/T**2)*T+D3+3*self.dtDdT_V*(1/8))*kB*self.dtDdV_T*NAv/self.tD+3*r*(D3*T+3*self.tD*(1/8))*kB*self.d2tDdVdT*NAv/self.tD-3*r*(D3*T+3*self.tD*(1/8))*kB*self.dtDdV_T*NAv*self.dtDdT_V/self.tD**2

    def d3FdV2dT(self,T,V):
        """
        (d3F(T,V)/dV2dT)

        :param float T: Temperature.
        :param float V: Volume.
        """
        x = self.tD/T
        D3      = D_3(x)
        dD3dx   = dD_3dx(x,D3)
        d2D3dx2 = d2D_3dx2(x,D3,dD3dx)

        return -3*r*(T**2*((-T*self.d3tDdV2dT-self.d2tDdV2_T)*self.tD**2+(T*self.d2tDdV2_T*self.dtDdT_V+2*T*self.dtDdV_T*self.d2tDdVdT+self.dtDdV_T**2)*self.tD-2*T*self.dtDdT_V*self.dtDdV_T**2)*D3-self.tD*((-self.d2tDdV2_T*self.tD**2+(T*self.d2tDdV2_T*self.dtDdT_V+2*T*self.dtDdV_T*self.d2tDdVdT+self.dtDdV_T**2)*self.tD-2*T*self.dtDdT_V*self.dtDdV_T**2)*T*dD3dx+3*self.tD*(8*self.dtDdV_T**2*(T*self.dtDdT_V-self.tD)*d2D3dx2*(1/3)+self.tD*self.d3tDdV2dT*T**2)*(1/8)))*kB*NAv/(T**2*self.tD**3)

    def d3FdVdT2(self,T,V):
        """
        (d3F(T,V)/dVdT2)

        :param float T: Temperature.
        :param float V: Volume.
        """
        x = self.tD/T
        D3      = D_3(x)
        dD3dx   = dD_3dx(x,D3)
        d2D3dx2 = d2D_3dx2(x,D3,dD3dx)

        return -(6*(T**3*((-(1/2)*self.d3tDdVdT2*T-self.d2tDdVdT)*self.tD**2+(((1/2)*self.d2tDdT2_V*T+self.dtDdT_V)*self.dtDdV_T+self.dtDdT_V*self.d2tDdVdT*T)*self.tD-self.dtDdT_V**2*self.dtDdV_T*T)*D3-(T**2*(-self.tD**2*self.d2tDdVdT+(((1/2)*self.d2tDdT2_V*T+self.dtDdT_V)*self.dtDdV_T+self.dtDdT_V*self.d2tDdVdT*T)*self.tD-self.dtDdT_V**2*self.dtDdV_T*T)*dD3dx+(1/16)*(3*(8*self.dtDdV_T*(T*self.dtDdT_V-self.tD)**2*d2D3dx2*(1/3)+self.tD*self.d3tDdVdT2*T**3))*self.tD)*self.tD))*r*kB*NAv/(T**3*self.tD**3)

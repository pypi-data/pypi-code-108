#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 19:53:24 2018

@author: benjamin
"""

import numpy as np
from .utils import forcecompute

class Oscillator: #  < Network
    # Waveguide is a class that defines a vocal tract waveguide
    #### Properties
    ##### Input
    rest_position = None
    x_position = None
    up_height = None
    down_height = None
    initial_length = None
    initial_mass = None
    initial_stiffness = None
    initial_coupling_stiffness = None
    initial_damping = None
    Qr = None
    Qrc = None
    contact_damping = None
    contact_stiffness = None
    fundamental_frequency = None
    low_frequency_abduction = None
    partial_abduction = None
    model = 'ishi'
    length = None
    width = None
    etha_k1 = None
    etha_k2 = None
    etha_h1 = None
    etha_h2 = None

    # Instantaneous Output
    output_length = None
    isContact = None
    height_vector = None
    mass = None
    stiffness = None
    damping = None
    coupling_stiffness = None
    bernoulli = None
    resistance = None
    inductance = None
    separation_height = None
    mass_position = None
    mass_position_nm1 = None
    mass_position_nm2 = None
    inst_flow = None
    flow_nm1 = 0
    upstream_pressure = None
    downstream_pressure = None
    applied_force = None
    Qu1 = 0
    Qu2 = 0
#         DC_flow = None;

    # Output matrix
    height_vector_output = None
    mass_position_matrix = None
    mass_matrix = None
    stiffness_matrix = None
    damping_matrix = None
    coupling_stiffness_matrix = None

     # Constructor method
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    # Import methods
    def updateimpedance( self, Const, aChink, ain, ac, lc):
        # Update the glottis impedance

        rho = Const.rho
        co_mu = Const.mu
        sep = Const.sep
        armin = Const.amin
        kiter = Const.k_iter
        T = Const.T

        xvec = self.x_position
        lg = self.length
        selfmod = self.model
        yt = self.mass_position

        agp = self.oscillation_factor[kiter]
        h1i = np.sum(yt[:,0]*agp)+self.low_frequency_abduction[kiter]/lg
        h2i = np.sum(yt[:,1]*agp)+self.low_frequency_abduction[kiter]/lg
        h0i = self.up_height[kiter]
        h3i = self.down_height[kiter]
        Hvec = np.array([ h0i, h1i, h2i, h3i ])
        self.height_vector = Hvec

        ### Glottis shape
        x0 = xvec[0]
        x1 = xvec[1]
        x2 = xvec[2]
        dgl = xvec[3]-xvec[0]
        h0 = Hvec[0]
        h1i = Hvec[1]
        h2i = Hvec[2]
        if selfmod == 'smooth':
            A0 = (h1i-h0)/(x1-x0) # slope, part 1
            A1 = (h2i-h1i)/(x2-x1) # slope, part 2

            #### Separation point
            if (h1i>0) and (h2i>0): # No contact between masses
                if (h1i!=h2i): # if h1 different than h2
                    hsi = sep*h1i
                else:
                    hsi = h2i # separation height is h2
                if (h1i>=h2i) or (hsi>=h2i): #
                    hsi = h2i
            else:
                hsi = armin/lg   # if contact, separation height is 0 (set to eps to avoid singularities)

            Ag22 = 1/(hsi*lg+aChink)**2
            Rg2 = 0.5*rho/(lg**2)*(1/(hsi**2)-1/(h0**2))  # Bernoulli

            if (h1i!=h2i): # if plate 2 is non-horizontal
                Rg = 0.5*12*co_mu/lg*(1/A0*(1/(h0**2)-1/(h1i**2)) + 1/A1*(1/(h1i**2)-1/(hsi**2))) # viscous term
                Lg = rho/lg*(1/A0*np.log(h1i/h0)+1/A1*np.log(hsi/h1i)) # inertia
            else:  # if plate 2 is horizontal
                Rg = 12*co_mu/lg*(0.5/A0*(1/(h0**2)-1/(h1i**2)) + (x2-x1)/(h1i**3)) # viscous term
                Lg = rho/lg*(1/A0*np.log(h1i/h0)+(x2-x1)/h1i) # inertia
        elif  selfmod=='ishi':
            ag1 = h1i*lg
            ag2 = h2i*lg
            Rk1 = 0.19*rho/(ag1)**2
            Rk2 = (0.5 - ag2/ain*(1-ag2/ain)) / (ag2**2)*rho
            Lg1 = rho*(x1-x0)/ag1
            Lg2 = rho*(x2-x1)/ag2
            Rv1 = 12*co_mu*lg**2*(x1-x0)/(ag1**3)
            Rv2 = 12*co_mu*lg**2*(x2-x1)/(ag2**3)
            Rg2 = Rk1+Rk2
            Rg = np.array([Rv1, Rv2])
            Lg = np.array([Lg1,Lg2])
            hsi = min(h1i,h2i)
            hsi = max(hsi,armin/lg)#
            Ag22 = 1/(hsi*lg+aChink)**2

        if not Const.unst:
            Lg = Lg*0
        if Const.model =='smooth':
            Rg = np.array([Rg, Rg]/2)
            Lg = np.array([Lg, Lg]/2)

        self.mass_position = yt * agp
        if type(self) is Glottis:            
            Ac2 = 1/ac**2
            rv_sum = (12*lg*dgl*Ag22*np.sqrt(Ag22)+8*np.pi*lc*Ac2)*co_mu
            # rv_sum = 12*(dgl*Ag22+lc.*Ac2)*co_mu;
            rk_sum = 1.38*rho*(Ac2+Ag22)
            # rv_sum = Rg+8*pi*lc.*Ac2*co_mu;
            # rk_sum = 1.38*rho*Ac2+Rg2;
            Udc = (-rv_sum+np.sqrt(rv_sum*rv_sum+4*rk_sum*self.upstream_pressure))/(2*rk_sum)
    #        if ( isempty(Udc) or isnan(Udc) ); Udc = 0; end
        #     self.DC_flow = Udc;

            self.DC_flow = self.DC_flow+(Udc-self.DC_flow)*2*np.pi*500*T
            Udc = self.DC_flow
            self.area = np.max((armin, abs(hsi*lg)+aChink))

        self.bernoulli = Rg2
        self.resistance = Rg
        self.inductance = Lg
        self.separation_height = hsi

        return  Rg2, Rg, Lg, hsi, Udc

    def updateparam( self, Const ):
        # Adapt the values of the mass and stiffness of vocal folds to match the
        # fundamental frequency fo

        kiter = Const.k_iter
        fo = self.fundamental_frequency[kiter]
        dab = max(0.1,1-self.partial_abduction[kiter])
        mvfi = self.initial_mass

        if (np.isinf(fo) or np.isnan(fo) or fo <= 1 ):
            fo = 1

        mvfo = mvfi*dab
        kvfo = 4*np.pi**2*fo**2*mvfo
        kco = np.array([ kvfo[0,0], kvfo[1,0] ])*self.Qrc
        rvfo = self.Qr*np.sqrt(kvfo*mvfo/2)

        #### CHECK for contact
        kctc = self.contact_stiffness
        rctc = self.contact_damping
        self.isContact = False

        if (self.height_vector[1] <= Const.blim):  # contact at the 1st mass location
            kvfo[:,0] = kctc*kvfo[:,0] # New stiffness for 1st mass
            rvfo[:,0] = rctc*np.sqrt(kvfo[:,0]*mvfo[:,0]/2)#rvf(:,1)+2*sqrt(kvf(:,1).*mvf(:,1)); # New damping for 1st mass
            self.isContact = True

        if (self.height_vector[2] <= Const.blim): # contact at the 2nd mass location
            kvfo[:,1] = kctc*kvfo[:,1] # New stiffness for 2nd mass
            rvfo[:,1] = rctc*np.sqrt(kvfo[:,1]*mvfo[:,1]/2) #rvf(:,2)+2*sqrt(kvf(:,2).*mvf(:,2)); # New damping for 2nd mass
            self.isContact = True

        self.mass = mvfo
        self.stiffness = kvfo
        self.coupling_stiffness = kco
        self.damping = rvfo

        return mvfo, kvfo, rvfo, kco

    def updatemassishiflan(self, Const):

        ### Glottis shape
        rho = Const.rho
        T = Const.T

        etha_k1 = self.etha_k1
        etha_k2 = self.etha_k2
        etha_h1 = self.etha_h1
        etha_h2 = self.etha_h2
        xvec = self.x_position
        lg = self.length

        ytm1 = self.mass_position_nm1
        ytm2 = self.mass_position_nm2
        ago = self.low_frequency_abduction[Const.k_iter]
        U1 = self.inst_flow
        m1 = self.mass[1,0]
        m2 = self.mass[1,1]
        k1 = self.stiffness[1,0]
        k2 = self.stiffness[1,1]
        kc = self.coupling_stiffness[0]
        Ps = self.upstream_pressure

        x0 = xvec[0]
        x1 = xvec[1]
        x2 = xvec[2] #x3 = xvec(4)
        d1 = x1-x0
        d2 = x2-x1
        # h0 = hvec[0] h1i = hvec(2) h2i = hvec(3) h3 = hvec(4)

        y1m1 = np.sum(ytm1[:,0])
        y2m1 = np.sum(ytm1[:,1])
        y1m2 = np.sum(ytm2[:,0])
        y2m2 = np.sum(ytm2[:,1])
        ag1m1 = y1m1*lg + ago
        ag2m1 = y2m1*lg + ago
        ago1 = ago
        ago2 = ago
        h1 = 3*k1
        h2 = 3*k2

        # Pressure acting on m1
        Pm1 =  Ps - 1.37*rho/2*(U1/(ag1m1))**2 \
        - 0.5*( self.resistance[0]*U1+2*self.inductance[0]/T*U1-self.Qu1 )
        self.Qu1 = 4/T*self.inductance[0]*U1-self.Qu1

        F1 = d1*lg*Pm1 # Force due to Pm1

        # Pressure acting on m2
        F2 = d2*lg*( Pm1 - 0.5*(np.sum(self.resistance))*U1
                    -2*(np.sum(self.inductance))/T*U1+self.Qu2
                    -rho/2*U1**2*( 1/ag2m1**2-1/ag1m1**2 ) )
        self.Qu2 = 4/T*(np.sum(self.inductance))*U1-self.Qu2

        # Damping ratio
        r1 = 2*0.1*np.sqrt(m1*k1)
        r2 = 2*0.6*np.sqrt(m2*k2)

        # Computation of every possible case.
        #1 and 2 open
        y1oo = ( m1/T**2*(2*y1m1-y1m2) + \
            r1/T*y1m1-k1*etha_k1*y1m1**3 - \
            kc*(y1m1-y2m1) + F1) \
            /( m1/T**2+r1/T+k1 )
        y2oo = ( m2/T**2*(2*y2m1-y2m2) + \
            r2/T*y2m1-k2*etha_k2*y2m1**3 - \
            kc*(y2m1-y1m1) + F2) \
            /( m2/T**2+r2/T+k2 )

        # 1 open and 2 closed
        r2 = 2*1.6*np.sqrt(m2*k2)
        y1of = ( m1/T**2*(2*y1m1-y1m2) + \
            r1/T*y1m1-k1*etha_k1*y1m1**3 -\
            kc*(y1m1-y2m1) +Ps*d1*lg)\
            /( m1/T**2+r1/T+k1 )
        y2of = ( m2/T**2*(2*y2m1-y2m2) + \
            r2/T*y2m1-k2*etha_k2*y2m1**3 -\
            kc*(y2m1-y1m1) + Ps*d2*lg - \
            h2*(ago2*0.5/lg+etha_h2*(y2m1+ago2*0.5/lg)**3) )\
            /( m2/T**2+r2/T+k2+h2)

        # 1 closed and 2 open
        r1 = 2*1.1*np.sqrt(m1*k1)
        r2 = 2*0.6*np.sqrt(m2*k2)
        y1fo = ( m1/T**2*(2*y1m1-y1m2) + \
            r1/T*y1m1-k1*etha_k1*y1m1**3 -\
            kc*(y1m1-y2m1) + Ps*d1*lg - \
            h1*(ago1*0.5/lg+etha_h1*(y1m1+ago1*0.5/lg)**3))\
            /( m1/T**2+r1/T+k1+h1 )
        y2fo = ( m2/T**2*(2*y2m1-y2m2) + \
            r2/T*y2m1-k2*etha_k2*y2m1**3 -\
            kc*(y2m1-y1m1) + 0)\
            /( m2/T**2+r2/T+k2 )

        # 1 and 2 closed
        r2 = 2*1.6*np.sqrt(m2*k2)
        y1ff = ( m1/T**2*(2*y1m1-y1m2) + \
            r1/T*y1m1-k1*etha_k1*y1m1**3 -\
            kc*(y1m1-y2m1) + Ps*d1*lg - \
            h1*(ago1*0.5/lg+etha_h1*(y1m1+ago1*0.5/lg)**3))\
            /( m1/T**2+r1/T+k1+h1 )
        y2ff = ( m2/T**2*(2*y2m1-y2m2) + \
            r2/T*y2m1-k2*etha_k2*y2m1**3 -\
            kc*(y2m1-y1m1) + 0 - \
            h2*(ago2*0.5/lg+etha_h2*(y2m1+ago2*0.5/lg)**3) )\
            /( m2/T**2+r2/T+k2+h2)

        if y1oo > -ago1/(2*lg):
            if y2oo > -ago2/(2*lg):
                y1 = y1oo
                y2 = y2oo
            else:
                y1 = y1of
                y2 = y2of
        else:
            if y2fo > -ago2/(2*lg):
                #           1 closed 2 open
                y1 = y1fo
                y2 = y2fo
            else:
                #           1 closed 2 closed
                y1 = y1ff
                y2 = y2ff

        ytm2 = ytm1
        yt = np.hstack((y1/2*np.ones((2,1)), y2/2*np.ones((2,1))))
        ytm1 = yt

        self.mass_position_nm2 = ytm2
        self.mass_position_nm1 = ytm1
        self.mass_position = yt
        self.applied_force = np.array([F1, F2])

        return yt, ytm1, ytm2

    def updatemassposition(self, Const):
        
        Fvf = self.applied_force
        fs = 1/Const.T
        kc = self.coupling_stiffness
        mvf = self.mass
        ke = self.stiffness
        re = self.damping
        ytm1 = self.mass_position_nm1
        ytm2 = self.mass_position_nm2
        yt = np.zeros((2,2))
        # activation = self.activation[Const.k_iter]
        activation = 1

        F1u = np.sum(Fvf[:,0])
        F2u = np.sum(Fvf[:,1])
        F1d = F1u
        F2d = F2u
        kcup = kc[0]
        kcdown = kc[1]

        tmp1_A = mvf[0,0]*fs**2+ke[0,0]+re[0,0]*fs+kc[0]
        tmp1_B = mvf[0,0]*fs**2*(2*ytm1[0,0]-ytm2[0,0])+re[0,0]*fs*ytm1[0,0]
        tmp2_A = mvf[0,1]*fs**2+ke[0,1]+re[0,1]*fs+kc[0]
        tmp2_B = mvf[0,1]*fs**2*(2*ytm1[0,1]-ytm2[0,1])+re[0,1]*fs*ytm1[0,1]

        yt[0,0] = (F1u+tmp1_B+(kcup/tmp2_A)*(F2u+tmp2_B))/(tmp1_A-(kcup**2)/tmp2_A)
        yt[0,1] = (F2u+tmp2_B+(kcup/tmp1_A)*(F1u+tmp1_B))/(tmp2_A-(kcup**2)/tmp1_A)

        tmp1_A = mvf[1,0]*fs**2+ke[1,0]+re[1,0]*fs+kc[1]
        tmp1_B = mvf[1,0]*fs**2*(2*ytm1[1,0]-ytm2[1,0])+re[1,0]*fs*ytm1[1,0]
        tmp2_A = mvf[1,1]*fs**2+ke[1,1]+re[1,1]*fs+kc[1]
        tmp2_B = mvf[1,1]*fs**2*(2*ytm1[1,1]-ytm2[1,1])+re[1,1]*fs*ytm1[1,1]

        yt[1,0] = (F1d+tmp1_B+(kcdown/tmp2_A)*(F2d+tmp2_B))/(tmp1_A-(kcdown**2)/tmp2_A)
        yt[1,1] = (F2d+tmp2_B+(kcdown/tmp1_A)*(F1d+tmp1_B))/(tmp2_A-(kcdown**2)/tmp1_A)
        ytm2 = ytm1
        ytm1 = yt

        self.mass_position_nm2 = ytm2
        self.mass_position_nm1 = ytm1
        self.mass_position = yt*activation

        return yt, ytm1, ytm2

    def appliedforce(self, Const):
        # Compute the applied force on vocal folds

        sep = Const.sep
        T = Const.T

        xvec = self.x_position
        Hvec = self.height_vector
        (x0, x1, x2, x3) = xvec
        (h0, h1i, h2i, h3) = Hvec

        Ps = self.upstream_pressure
        Psup = self.downstream_pressure
        DeltaPi = Ps-Psup
        Ug = self.inst_flow
        Ugim1 = self.flow_nm1
        lg = self.length

        A = [(h1i-h0)/(x1-x0),
             (h2i-h1i)/(x2-x1),
             (h3-h2i)/(x3-x2)]
        B = [h0-A[0]*x0,
             h1i-A[1]*x1,
             h2i-A[2]*x2]

        if (h1i>0) and (h2i>0): # No contact between masses
            if (h1i!=h2i): # if h1 different than h2
                 hsi = sep*h1i
                 xsi = (hsi-h1i)/A[1]+x1
            else:
                 xsi = x2 # if h1 = h2
                 hsi = h2i # separation height is h2
            if (h1i>=h2i) or (hsi>=h2i): #
                hsi = h2i
                xsi = x2   # separation point is x2
        else:
            hsi = 1e-11   # if contact, separation is 0
            xsi = 1e-11   #

        if DeltaPi>=0:
            dUg_tmp = (Ug-Ugim1)/T
            Fvf = forcecompute(Ug,lg,dUg_tmp,Ps,Psup,xvec,h1i,h2i,A,B,h0,xsi,hsi, Const)
        else:
            dUg_tmp = (-Ug-Ugim1)/T
            Fvf = forcecompute(Ug,lg,dUg_tmp,Psup-Ps,0,xvec,h2i,h1i,A,B,h0,xsi,hsi, Const)

        Ugim1 = Ug
        self.flow_nm1 = Ug
        self.applied_force = Fvf

        return Fvf, Ugim1


class Glottis(Oscillator):
#GLOTTIS Summary of this class goes here
#   Detailed explanation goes here

    # Input
    subglottal_pressure = None

    # Output
    #### Instantaneous
    DC_flow = 0
    max_opening = 4e-5
    area = None

    #### Time evolution
    DC_vector = None

      # Constructor method
    def __init__(self, **kwargs):
        isArg = False
        for key, value in kwargs.items():
            setattr(self, key, value)
            isArg = True
        if not isArg:

            Qam = 1
            Qak = 1
            Qam2 = 0.2
            Qak2 = 0.2

            rho_folds = 1020
            hfolds = 1e-2*(0.065+0.05+0.115)#3e-3
            kspring = 10

            self.rest_position = 5e-5*np.ones((2,2))
            self.mass_position = 5e-5*np.ones((2,2))
            self.width = 0.003
            x1 = self.width/(1+Qam2)  # 1st mass
            x2 = self.width   # 2nd mass
            x3 = x2+x1*1e-11  # end of constriction
            self.x_position = np.array([ 0, x1, x2, x3 ])
            self.length = 0.016

            self.Qr = 0.2
            self.Qrc = 0.5

            # Mechanical parameters
            m1ui = rho_folds*self.length*self.width*hfolds/(1+Qam2)/2*1.2 # upper mass 1 (kg)
            k1ui = kspring # upper spring stiffness 1 (N/m)
            r1ui = self.Qr*np.sqrt(k1ui*m1ui/2) # damping of the upper mass 1
            m2ui = m1ui*Qam2 # upper mass 2 (kg)
            k2ui = k1ui*Qak2 # upper spring stiffness 2 (N/m)
            kcui = k1ui*self.Qrc # upper coupling spring (N/m)
            r2ui = self.Qr*np.sqrt(k2ui*m2ui/2) # damping of upper mass 2
            m1di = m1ui*Qam  # lower mass 1 (kg)
            k1di = k1ui*Qak  # lower spring stiffness 1 (N/m)
            m2di = m2ui*Qam  # lower mass 2 (kg)
            r1di = self.Qr*np.sqrt(k1di*m1di/2) # damping of lower mass 1
            k2di = k2ui*Qak # lower spring stiffness 2 (N/m)
            kcdi = kcui*Qak  # lower coupling stiffness (N/m)
            r2di = self.Qr*np.sqrt(k2di*m2di/2) # damping of lower mass 2

            self.initial_mass = np.array([ [m1ui, m2ui], [ m1di, m2di] ]) # mass matrix
            self.initial_stiffness = np.array([ [ k1ui, k2ui], [ k1di, k2di ] ])# stiffness matrix
            self.initial_damping = np.array([ [ r1ui, r2ui], [ r1di, r2di ] ]) # damping matrix
            self.initial_coupling_stiffness = np.array([ kcui, kcdi ]) # coupling stiffness

            self.etha_k1 = 100
            self.etha_k2 = 100
            self.etha_h1 = 500
            self.etha_h2 = 500
            self.contact_stiffness = 4
            self.contact_damping = 2.2
            self.upstream_pressure = 0
            self.downstream_pressure = 0

class Tongue(Oscillator):
    # Tongue Summary of this class goes here
    #   Detailed explanation goes here


    position = None
    oscillation_factor = None
    Qdown = 0
    Qup = 0
    waveguide = None
    num_oscillators = None
    contact_stiffness = 1.5
    contact_damping = 1.2

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def updatepressure(self,  objwvg, Const):

        T = Const.T
        ptt = self.position
        utt = objwvg.flow_time[ptt]
        uttp1 = objwvg.flow_time[ptt+1]
        self.flow_inst = objwvg.flow_time[ptt-1]
        self.upstream_pressure = objwvg.pressure_time[ptt-1] - (objwvg.Rj[ptt-1]+2/T*objwvg.Lj[ptt-1]+objwvg.Rcp[ptt-1])*utt+self.Qup
        self.downstream_pressure = objwvg.pressure_time[ptt+1] - (objwvg.Rj[ptt+1]+2/T*objwvg.Lj[ptt+1]+objwvg.Rcp[ptt+1])*utt-self.Qdown

        self.Qup = 4/T*objwvg.Lj[ptt-1]*utt-self.Qup
        self.Qdown = 4/T*objwvg.Lj[ptt+1]*uttp1-self.Qdown


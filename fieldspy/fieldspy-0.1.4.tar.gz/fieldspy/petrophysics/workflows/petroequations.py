import numpy as np 
import pandas as pd 
from scipy.interpolate import interp1d
from scipy.stats import hmean, gmean
from pydantic import BaseModel, Field, validator
from enum import Enum

class PetrophysicsEstimator(BaseModel):
    description: str = Field(None)

def vshale_gr(gr_curve,gr_sand,gr_shale,type='linear'):
    """vshale_gr [summary]

    Parameters
    ----------
    gr_curve : [type]
        [description]
    gr_sand : [type]
        [description]
    gr_shale : [type]
        [description]
    type : str, optional
        [description], by default 'linear'

    Returns
    -------
    [type]
        [description]

    Raises
    ------
    ValueError
        [description]
    """
    gr_curve=np.atleast_1d(gr_curve)
    gr_sand=np.atleast_1d(gr_sand)
    gr_shale=np.atleast_1d(gr_shale)
    igr=(gr_curve-gr_sand)/(gr_shale-gr_sand)
    igr[igr < 0.0] = 0.0
    igr[igr > 1.0] = 1.0
    #https://www.geoloil.com/VshModels.php
    if type == 'linear':
        vsh = igr
    elif type == 'clavier':
        vsh = 1.7 - np.sqrt(3.38 - np.power(igr+0.7,2))
    elif type == 'stieber':
        vsh = igr/(3-2*igr)
    elif type == 'larionov_old':
        vsh = 0.33 * (np.power(2,2*igr)-1)
    elif type == 'larionov_tertiary':
        vsh = 0.083 * (np.power(2,3.7*igr)-1)
    else:
        raise ValueError(f'method especified [ {type} ] does not exist')

    return vsh


class VshGrEnum(str,Enum):
    linear = 'linear'
    clavier = 'clavier'
    stieber = 'stieber'
    larionov_old = 'larionov_old'
    larionov_tertiary = 'larionov_tertiary'
    
class VshaleGr(PetrophysicsEstimator):
    gr_sand: float = Field(None, gt=0)
    gr_shale: float = Field(None, gt=0)
    method: VshGrEnum = Field(VshGrEnum.linear)
    col_name: str = 'vsh_gr'
    gr_curve: str = Field(None)
    
    @validator(gr_shale,check_fields=False)
    def check_grshale_gt_grsand(cls,v,values):
        assert v > values['gr_sand'], f"gr_shale {v} must be greater than gr_sand {values['gr_sand']}"
        return v
    
    def forward(self,gr):
        return vshale_gr(gr,self.gr_sand,self.gr_shale,type=self.method.value)
    
    def forward_log(self,df):
        vsh = vshale_gr(df[self.gr_curve],self.gr_sand,self.gr_shale,type=self.method.value)
        return pd.Series(vsh,index=df.index,name=self.col_name)
    
#-----------------------------------------------------------------------------------
def vshale_dn(rho_curve, ntr_curve, rho_ma=2.65, rho_f=1.0, hi_shl=0.46,rho_shl=2.43):
    """vshale_dn [summary]

    Parameters
    ----------
    rho_curve : [type]
        [description]
    ntr_curve : [type]
        [description]
    rho_ma : float, optional
        [description], by default 2.65
    rho_f : float, optional
        [description], by default 1.0
    hi_shl : float, optional
        [description], by default 0.46
    rho_shl : float, optional
        [description], by default 2.43

    Returns
    -------
    [type]
        [description]
    """
    rho_curve= np.atleast_1d(rho_curve)
    ntr_curve= np.atleast_1d(ntr_curve)
    rho_ma = np.atleast_1d(rho_ma)
    rho_f = np.atleast_1d(rho_f)
    hi_shl = np.atleast_1d(hi_shl)
    rho_shl = np.atleast_1d(rho_shl)
    vsh = (rho_curve - rho_ma + ntr_curve*(rho_ma-rho_f))/(rho_shl - rho_ma + hi_shl*(rho_ma-rho_f))
    vsh[vsh < 0.0] = 0.0
    vsh[vsh > 1.0] = 1.0
    return vsh

class VshaleDN(PetrophysicsEstimator):
    rho_matrix: float = Field(2.65, gt=0)
    rho_fluid: float = Field(1.0, gt=0)
    hi_shale: float = Field(0.46)
    rho_shale : float = Field(2.43, gt=0)
    col_name: str = 'vsh_dn'
    rho_curve: str = Field(None)
    ntr_curve: str = Field(None)
       
    def forward(self,rho,ntr):
        return vshale_dn(
            rho, 
            ntr, 
            rho_ma=self.rho_matrix, 
            rho_f=self.rho_fluid, 
            hi_shl=self.hi_shale,
            rho_shl=self.rho_shale
        )
        
    def forward_log(self,df):
        return vshale_dn(
            df[self.rho_curve], 
            df[self.ntr_curve], 
            rho_ma=self.rho_matrix, 
            rho_f=self.rho_fluid, 
            hi_shl=self.hi_shale,
            rho_shl=self.rho_shale
        )
        
    

#-----------------------------------------------------------------------------------

def phi_rho(rho_curve,rho_ma=2.65,rho_f=1.0):
    """phi_rho [summary]

    Parameters
    ----------
    rho_curve : [type]
        [description]
    rho_ma : float, optional
        [description], by default 2.65
    rho_f : float, optional
        [description], by default 1.0

    Returns
    -------
    [type]
        [description]
    """
    rho_curve=np.atleast_1d(rho_curve)
    rho_ma=np.atleast_1d(rho_ma)
    rho_f=np.atleast_1d(rho_f)
    phi_rho_curve=(rho_ma-rho_curve)/(rho_ma-rho_f)
    phi_rho_curve[phi_rho_curve < 0.0] = 0.0
    phi_rho_curve[phi_rho_curve > 1.0] = 1.0
    return phi_rho_curve

class PhiRho(PetrophysicsEstimator):
    rho_matrix: float = Field(2.65, gt=0)
    rho_fluid: float = Field(1.0,gt=0)
    col_name: str = 'phi_rho'
    rho_curve: str = Field(None)
    
    def forward(self,x):
        return phi_rho(x, rho_ma = self.rho_matrix, rho_f=self.rho_fluid)
    
    def forward_log(self,df):
        return phi_rho(df[self.rho_curve], rho_ma = self.rho_matrix, rho_f=self.rho_fluid)

#-----------------------------------------------------------------------------------

def phie(phi_curve,vsh_curve):
    """phie [summary]

    Parameters
    ----------
    phi_curve : [type]
        [description]
    vsh_curve : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    phi_curve=np.atleast_1d(phi_curve)
    vsh_curve=np.atleast_1d(vsh_curve)
    phie_curve=phi_curve*(1 -vsh_curve)
    phie_curve[phie_curve < 0.0] = 0.0
    phie_curve[phie_curve > 0.3] = 0.3
    return phie_curve

class Phie(PetrophysicsEstimator):
    col_name: str = 'phie'
    phi_curve: str = Field(None)
    vsh_curve: str = Field(None)
    
    def forward(self,phi,vsh):
        return phie(phi,vsh)
    
    def forward_log(self,df):
        return phie(
            df[self.phi_curve],
            df[self.vsh_curve]
        )

#-----------------------------------------------------------------------------------

class PhiaMethodEnum(str,Enum):
    arithmetic = 'arithmetic'
    geometric = 'geometric'
    harmonic = 'harmonic'
    

def phia(phi_rho_curve, ntr_curve, method='geometric'):
    """phia [summary]

    Parameters
    ----------
    phi_rho_curve : [type]
        [description]
    ntr_curve : [type]
        [description]
    method : str, optional
        [description], by default 'geometric'

    Returns
    -------
    [type]
        [description]
    """
    phi_rho_curve = np.atleast_1d(phi_rho_curve)
    ntr_curve = np.atleast_1d(ntr_curve)
    c = np.stack([phi_rho_curve,ntr_curve], axis=1)
    if method == 'mean':
        phia_curve = np.mean(c,axis=1)
    elif method== 'geometric':
        phia_curve = gmean(c,axis=1)
    elif method=='harmonic':
        phia_curve = hmean(c,axis=1)
    return phia_curve

class PhiAverage(PetrophysicsEstimator):
    method: PhiaMethodEnum = Field(PhiaMethodEnum.geometric.value)
    col_name: str = 'phia'
    phi1_curve: str = Field(None)
    phi2_curve: str = Field(None)
    
    def forward(self,phi1,phi2):
        return phia(phi1,phi2,method=self.method)
    
    def forward_log(self,df):
        return phia(
            df[self.phi1_curve],
            df[self.phi2_curve],
            method=self.method
        )    
        

#-----------------------------------------------------------------------------------

class SwMethodsEnum(str,Enum):
    archie = 'archie'
    smdx = 'smdx'
    indo = 'indo'
    fertl = 'fertl'

def sw(rt_curve,phi_curve,rw,vsh_curve=None,a=0.62,m=2.15,n=2,rsh=4.0,alpha=0.3,method="archie"):
    """sw [summary]

    Parameters
    ----------
    rt_curve : [type]
        [description]
    phi_curve : [type]
        [description]
    rw : [type]
        [description]
    vsh_curve : [type], optional
        [description], by default None
    a : float, optional
        [description], by default 0.62
    m : float, optional
        [description], by default 2.15
    n : int, optional
        [description], by default 2
    rsh : float, optional
        [description], by default 4.0
    alpha : float, optional
        [description], by default 0.3
    method : str, optional
        [description], by default "archie"

    Returns
    -------
    [type]
        [description]
    """
    a=np.atleast_1d(a)
    m=np.atleast_1d(m)
    n=np.atleast_1d(n)
    vsh = np.atleast_1d(vsh_curve) if vsh_curve is not None else None
    rsh=np.atleast_1d(rsh)
    alpha=np.atleast_1d(alpha)
    rt=np.atleast_1d(rt_curve)
    phi = np.atleast_1d(phi_curve)
    rw=np.atleast_1d(rw)
    if method == "archie":
        sw_curve=np.power(((a*rw)/(rt*np.power(phi,m))),1/n)
    elif method == "smdx": #https://www.spec2000.net/14-sws.htm
        C=((1-vsh)*a*rw)/np.power(phi,m)
        D=C*vsh/(2 * rsh)
        E=C/rt
        sw_curve=np.power(np.sqrt(D**2 + E) - D, 2/n)
    elif method == "indo":
        #https://geoloil.com/Indonesia_SW.php
        #A=np.sqrt(1 /rt)
        #B=(np.power(vsh,(1 -(vsh/2)))/np.sqrt(rsh))
        #C=np.sqrt(np.power(phi,m)/(a*rw))
        #sw_curve=np.power((A/(B+C)),2/n)

        #http://nafta.wiki/display/GLOSSARY/Indonesia+Model+%28Poupon-Leveaux%29+@model
        A_inv = 1 + np.sqrt((np.power(vsh,2-vsh)*rw)/(phi*rsh))
        A = 1/A_inv
        sw_curve = np.power((A*rw)/(np.power(phi,m)*rt),1/n)
    elif method == "fertl":
        A=np.power(phi,-m/2)
        B=(a*rw)/rt
        C=((alpha*vsh)/2)**2
        sw_curve=A*((np.sqrt(B+C))-np.sqrt(C))
    sw_curve[sw_curve < 0.0] = 0.0
    sw_curve[sw_curve > 1.0] = 1.0
    
    return sw_curve

class Sw(PetrophysicsEstimator):
    a: float = Field(0.62)
    m: float = Field(2.15)
    n: float = Field(2.0)
    rsh: float = Field(4.0)
    alpha: float = Field(0.3) 
    method: SwMethodsEnum = Field(SwMethodsEnum.archie)
    col_name: str = 'sw'
    rt_curve: str = Field(None)
    phi_curve: str = Field(None)
    vsh_curve: str = Field(None)
    rw: float = Field(None)
    
    def forward(self,rt,phi,rw=None,vsh=None):
        if rw is None:
            rw = self.rw
        return sw(
            rt,
            phi,
            rw,
            vsh_curve=vsh,
            a = self.a,
            m = self.m,
            n = self.n,
            rsh = self.rsh,
            alpha = self.alpha,
            method = self.method.value
        )

    def forward_log(self,df):
        return sw(
            df[self.vsh_curve],
            df[self.phi_curve],
            self.rw,
            vsh_curve = None if self.vsh_curve is None else df[self.vsh_curve],
            a = self.a,
            m = self.m,
            n = self.n,
            rsh = self.rsh,
            alpha = self.alpha,
            method = self.method.value
        )
        
def depth_temperature(depth, surface_temperature=77 ,gradient=1):
    """depth_temperature [summary]

    Parameters
    ----------
    depth : [type]
        [description]
    surface_temperature : int, optional
        [description], by default 77
    gradient : int, optional
        [description], by default 1

    Returns
    -------
    [type]
        [description]
    """
    depth = np.atleast_1d(depth)
    
    t = (gradient/100) * depth + surface_temperature 
    return t

class DepthTemperature(PetrophysicsEstimator):
    gradient: float = Field(1.0, gt=0)
    surface_temperature: float = Field(60.0, gt=0)
    col_name: str = 'temperature'
    depth_curve: str = Field(None)
    
    def forward(self,depth):
        return depth_temperature(
            depth, 
            self.surface_temperature,
            self.gradient
        )
        
    def forward_log(self,df):
        return depth_temperature(
            df[self.depth_curve], 
            self.surface_temperature,
            self.gradient
        )
        
        
def rw_temp_convert(rw,t1,t2, temp_unit='f'):
    """rw_temp_convert [summary]

    Parameters
    ----------
    rw : [type]
        [description]
    t1 : [type]
        [description]
    t2 : [type]
        [description]
    temp_unit : str, optional
        [description], by default 'f'

    Returns
    -------
    [type]
        [description]
    """
    rw = np.atleast_1d(rw)
    t1 = np.atleast_1d(t1)
    t2 = np.atleast_1d(t2)
    
    if temp_unit=='f':
        c = np.array([6.77])
    else:
        c = np.array([21.5])
    
    rw2 = rw*((t1 + c)/(t2 + c))
    return rw2

class RwConverter(PetrophysicsEstimator):
    rw: float = Field(...)
    temperature: float = Field(...)
    temp_unit: str = Field('f')
    col_name: str = 'rw_temp'
    temp_curve: str = Field(None)
    
    def forward(self,to_temp):
        return rw_temp_convert(
            self.rw,
            self.temperature,
            to_temp,
            temp_unit=self.temp_unit
        )
        
def rw_salinity(temp, salinity,temp_unit='f'):
    """rw [summary]

    Parameters
    ----------
    temp : [type]
        [description]
    salinity : [type]
        [description]
    temp_unit : str, optional
        [description], by default 'f'

    Returns
    -------
    [type]
        [description]
    """
    
    # 1) Convert from Celcius to Farenheit
    if temp_unit=='c':
        tf = 1.8*temp + 32.0
    else:
        tf=temp
    
    # 2) Calculate Resistivity in Ohm meters
    rw = np.power((400000.0/(tf*salinity)),0.88)
    
    return rw

class RwSalinity(PetrophysicsEstimator):
    temperature: float = Field(..., gt=0)
    temp_unit: str = Field('f')
    col_name: str = 'rw_salinity'
    salinity_curve: str = Field(None)
    
    def forward(self,salinity):
        return rw_salinity(
            self.temperature,
            salinity,
            temp_unit=self.temp_unit
        )
        


def facies_dnp(rho_curve, ntr_curve,pef_curve,**kw):
    """facies_dnp [summary]

    Parameters
    ----------
    rho_curve : [type]
        [description]
    ntr_curve : [type]
        [description]
    pef_curve : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    rho_curve = np.atleast_1d(rho_curve)
    ntr_curve = np.atleast_1d(ntr_curve)
    pef_curve = np.atleast_1d(pef_curve)
    phi_rho_curve = phi_rho(rho_curve,**kw)
    phia_curve = phia(phi_rho_curve,ntr_curve)
    
    u = pef_curve*((rho_curve + 0.1833)/1.07)
    uma = (u - 0.398 * phia_curve)/(1-phia_curve)
    dga = (rho_curve - phia_curve)/(1-phia_curve)
    return uma, dga

def perm_timur(phie,swir,dperm=4.4,eperm=2.0,fluid='oil'):
    if fluid=="oil":
        Cperm=3400
    elif fluid=="gas":
        Cperm=340
    k=Cperm * np.power(phie,dperm) / np.power(swir,eperm)
    return k

class PermTimur(PetrophysicsEstimator):
    dperm: float = Field(4.4)
    eperm: float = Field(2.0)
    fluid: str = Field('oil')
    col_name: str = 'perm_timur'
    phie_curve: str = Field(None)
    swir_curve: float = Field(None)
    
    def forward(self,phie,swir=None):
        if swir is None:
            swir = self.swir_curve
        return perm_timur(
            phie,
            swir,
            dperm=self.dperm,
            eperm = self.eperm,
            fluid=self.fluid
        )

    def forward_log(self,df):
        return perm_timur(
            df[self.phie_curve],
            df[self.swir_curve],
            dperm=self.dperm,
            eperm = self.eperm,
            fluid=self.fluid
        )

def perm_morris(phie_curve,swir,dperm=6.0,eperm=2.0,fluid='oil'):
    if fluid=="oil":
        Cperm=65000
    elif fluid=="gas":
        Cperm=6500
    k=Cperm * np.power(phie,dperm) / np.power(swir,dperm) 
    return k

class PermMorris(PetrophysicsEstimator):
    dperm: float = Field(6.0)
    eperm: float = Field(2.0)
    fluid: str = Field('oil')
    col_name: str = 'perm_morris'
    phie_curve: str = Field(None)
    swir_curve: float = Field(None)

    def forward(self,phie,swir=None):
        if swir is None:
            swir = self.swir_curve
        return perm_morris(
            phie,
            swir,
            dperm=self.dperm,
            eperm = self.eperm,
            fluid=self.fluid
        )

    def forward_log(self,df):
        return perm_morris(
            df[self.phie_curve],
            df[self.swir_curve],
            dperm=self.dperm,
            eperm = self.eperm,
            fluid=self.fluid
        )
        
def perm_coates(phie, swir):
    k=(10.0*phie)**4 *((1.0-swir)/swir)**2
    return k

class PermCoates(PetrophysicsEstimator):
    col_name: str = 'perm_coates'
    phie_curve: str = Field(None)
    swir_curve: float = Field(None)
    
    def forward(self,phie,swir=None):
        if swir is None:
            swir = self.swir_curve
        return perm_coates(phie, swir)
    
    def forward_log(self,df):
        return perm_coates(
            df[self.phie_curve], 
            df[self.phie_curve]
        )

def rw2(T, Wse, verbose=False,Celcius=False):    
    """rw2 [    Uses method from textbook "Petrophysics" by Djebbar and Donaldson.
    
    Supposedly more accurate than the approach used in calc_Rw because Hx and 
    RwT account for non-linearlity in resistivity as a function of salinity.]

    Parameters
    ----------
    T : [type]
        [description]
    Wse : [type]
        [description]
    verbose : bool, optional
        [description], by default False
    Celcius : bool, optional
        [description], by default False

    Returns
    -------
    [type]
        [description]
    """

    
    #  Calculations:
    
    # 1) Convert from Celcius to Farenheit
    if Celcius==True:
        Tf = 9.0/5.0*T + 32.0
    else:
        Tf=T
    
    # 2) Calculate reference water resistivity @ 75 Degrees Farenheit
    Rw75 = 1.0/(2.74*10**-4 * Wse**0.955) + 0.0123
    
    # 3) Calculate nonlinear correction factors
    Xh = 10.0**(-0.3404*np.log10(Rw75) + 0.6414)
    
    # 4) Calculate Water Resistivity at Temperature T1.  Output is Ohm-m
    Rw = Rw75 * (75.0 + Xh)/(Tf + Xh)
       
    return Rw

def flow_capacity(height,perm_curve,pay_curve):
    """flow_capacity [summary]

    Parameters
    ----------
    height : [type]
        [description]
    perm_curve : [type]
        [description]
    pay_curve : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    perm_curve=np.nan_to_num(np.atleast_1d(perm_curve))
    pay_curve=np.nan_to_num(np.atleast_1d(pay_curve))
    height=np.atleast_1d(height)
    
    kh=height*perm_curve*pay_curve
    khcum=np.cumsum(kh)
    kht=np.sum(kh)
    khnorm=1-(khcum/kht)
    return kh, khnorm


class FlowCapacity(PetrophysicsEstimator):
    depth_curve: str = Field(None)
    perm_curve: str = Field(None)
    pay_curve: str = Field(None)   
    
    def forward(self,depth,perm_curve,pay_curve):
        h = np.gradient(depth)
        return flow_capacity(h,perm_curve,pay_curve)  

    def forward_log(self,df):
        h = np.gradient(df[self.depth_curve])
        return flow_capacity(
            h,
            df[self.perm_curve],
            df[self.pay_curve]
        )
            
    
      
"""
https://www.spec2000.net/14-swtdt.htm
PHIe = effective porosity (fractional)
SIGMA = TDT capture cross section log reading (capture units)
SIGMAM = capture cross section matrix value (capture units)
SIGW = capture cross section for water (capture units)
SIGHY = capture cross section for hydrocarbons (capture units)
SIGSH = capture cross section for shale (capture units)
SWtdt = water saturation from TDT (fractional)
Vsh = shale volume (fractional)
WS = water salinity (ppm NaCl)
"""
def sw_pnn(phie,vsh, sigma,sighy,sigsh,ws=None,sigw=None,sigmam=None):
    """sw_pnn [summary]

    Parameters
    ----------
    phie : [type]
        [description]
    vsh : [type]
        [description]
    sigma : [type]
        [description]
    sighy : [type]
        [description]
    sigsh : [type]
        [description]
    ws : [type], optional
        [description], by default None
    sigw : [type], optional
        [description], by default None
    sigmam : [type], optional
        [description], by default None

    Returns
    -------
    [type]
        [description]
    """

    phie=np.atleast_1d(phie)
    vsh=np.atleast_1d(vsh)
    sigma=np.atleast_1d(sigma)
    sighy=np.atleast_1d(sighy)
    sigsh=np.atleast_1d(sigsh)

    if sigw is None:
        sigw = 22 + 0.000404*ws 
    if sigmam is None:
        sigmam = (sigma - phie*sigw)/(1-phie)

    _a = sigma - sigmam 
    _b = phie*(sighy - sigmam)
    _c = vsh*(sigsh - sigmam)
    _d = phie*(sigw - sighy)
    sw = (_a - _b - _c)/(_d)
    sw[phie<=0] = 1.0

    return sw

def rw_from_sp(rmf=None, rmf_temp=75, res_temp=None, ssp=None,temp_unit='f', rw_75=False):
    """rw_from_sp [summary]

    Parameters
    ----------
    rmf : [type], optional
        [description], by default None
    rmf_temp : int, optional
        [description], by default 75
    res_temp : [type], optional
        [description], by default None
    ssp : [type], optional
        [description], by default None
    temp_unit : str, optional
        [description], by default 'f'
    rw_75 : bool, optional
        [description], by default False

    Returns
    -------
    [type]
        [description]
    """

    #https://www.spec2000.net/05-7rwsp.htm
    # 1) Convert from Celcius to Farenheit
    if temp_unit=='c':
        rmf_temp = 1.8*rmf_temp + 32.0
        res_temp = 1.8*res_temp + 32.0

    # Convert rmf @ rmf_temp to res_temp
    rmf_res = rw_temp_convert(rmf,rmf_temp,res_temp, temp_unit='f')

    #Estimate Mud filtrate equivalent resistivity
    if rmf_res > 0.1:
        rmfe = rmf_res*0.85
    else:
        rmfe = (146*rmf_res-5)/(337*rmf_res + 77)
    #Ksp
    ksp = 60 +0.122*res_temp

    #RSP
    rsp = np.power(10,-ssp/ksp)
    # Rwe. Equivalent Water Resistivity
    rwe = rmfe / rsp

    # Estimate Water resistivity from Equivalent water resistivity
    if rwe > 0.12:
        rw = np.power(10,0.69*rwe-0.24) - 0.58
    else:
        rw = (77*rwe + 5)/(146 - 337*rwe)

    if rw_75:
        rw = rw_temp_convert(rw,res_temp,75, temp_unit='f')

    return rw

def salinity_from_rw(rw=None, temp=75,temp_unit='f'):
    """salinity_from_rw [summary]

    Parameters
    ----------
    rw : [type], optional
        [description], by default None
    temp : int, optional
        [description], by default 75
    temp_unit : str, optional
        [description], by default 'f'

    Returns
    -------
    [type]
        [description]
    """
    if temp_unit=='c':
        temp = 1.8*temp + 32.0

    # Convert rmf @ rmf_temp to res_temp
    if temp != 75:
        rw_75 = rw_temp_convert(rw,temp,75, temp_unit='f')
    else:
        rw_75 = rw 

    exp = (3.562-np.log10(rw_75-0.0123))/(0.955)
    sal = np.power(10,exp)

    return sal



    



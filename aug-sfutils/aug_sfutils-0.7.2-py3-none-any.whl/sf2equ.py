"""Equilibrium object from shotfile"""

import logging
import numpy as np
from scipy.integrate import cumtrapz

from aug_sfutils import sfobj, SFREAD, parse_kwargs, cocos

logger = logging.getLogger('aug_sfutils.sf2equ')


class EQU:
    """Reads the whole equilibrium shotfile
    Reduces 1D profiles to within separatrix,
    Calculates a few useful derived quantities
    Accepts a time sub-interval via tbeg, tend keywords
    """

    def __init__(self, nshot, **kwargs):

        """
        Input
        ---------
        nshot: int
            shot number
        diag: str
            diagnsotics used for mapping (EQI, EQH, ...)
        exp: str
            experiment (AUGD)
        ed:  int
            edition
        tbeg: float
            initial time [s]
        tend: float
            final time [s]
        """

        exp  = parse_kwargs.parse_kw( ('exp', 'experiment'), kwargs, default='AUGD')
        diag = parse_kwargs.parse_kw( ('diag', 'diagnostic'), kwargs, default='EQH')
        ed   = parse_kwargs.parse_kw( ('ed', 'edition'), kwargs, default=0)

        self.sf = SFREAD(nshot, diag, ed=ed, exp=exp)

        if self.sf.status:

            ## Shot number
            self.shot = nshot 

            ## Shotfile exp
            self.exp = exp
            
            ## Shotfile diag
            self.diag = diag

            ## Actual shotfile edition (> 0)
            self.ed = self.sf.ed

            ## COCOs number
            self.cocos = 17

            ## Time grid of equilibrium shotfile
            self.time = self.sf.getobject('time')
            nt = len(self.time)
            parmv = self.sf.getparset('PARMV')
            nR = parmv['M'] + 1
            nZ = parmv['N'] + 1
            ## R of PFM cartesian grid [m]
            self.Rmesh = self.sf.getobject('Ri')[: nR, 0]
            ## z of PFM cartesian grid [m]
            self.Zmesh = self.sf.getobject('Zj')[: nZ, 0]

            Lpf = self.sf.getobject('Lpf').T
            ## For 1D profiles: #points within separatrix
            self.lpfp = Lpf%10000 # inside sep
            ## For 1D profiles: #points in SOL
            self.lpfe = (Lpf - self.lpfp)//10000 #outside sep
            ## Spatial index sorted from inside to outside, at each time
            self.ind_sort = []
            for jt in range(nt):
                ind_core = np.arange(self.lpfp[jt], -1, -1)
                ind_sol  = np.arange(self.lpfp[jt] + 3, self.lpfp[jt] + 3 + self.lpfe[jt])
                self.ind_sort.append(np.append(ind_core, ind_sol))
        else:
            logger.error('Problems opening %s:%s:%d for shot %d' %(exp, diag, ed, nshot))
            return

        logger.info('Reading equ scalars')
        self.read_scalars()
        logger.info('Reading equ 1d profiles')
        self.read_profiles()
        logger.info('Reading equ PFM')
        self.read_pfm()

        logger.info('COCO %d' %self.cocos)

# Sign of Ip, Bt (positive=ccw from above), valid for COCOS=17 (CLISTE)
        self.ip_ccw = np.sign((self.psix - self.psi0).mean())
        self.bt_ccw = np.sign(np.nanmean(self.jpol))

        jcoco = self.cocos%10 - 1
        ebp   = self.cocos//10
        psi_sign = -self.ip_ccw*cocos.sigma['bp'][jcoco]*cocos.sigma['rphiz'][jcoco]
        psi_2pi  = (2.*np.pi)**ebp
        self.psi_fac = psi_sign*psi_2pi
        self.phi_sign = self.bt_ccw*cocos.sigma['rphiz'][jcoco]

        if 'tbeg' in kwargs.keys():
            tbeg = kwargs['tbeg']
        else:
            tbeg = np.min(self.time)
        if 'tend' in kwargs.keys():
            tend = kwargs['tend']
        else:
            tend = np.max(self.time)

        (indt, ) = np.where((self.time >= tbeg) & (self.time <= tend))
        if len(indt) == 0:
            indt = [np.argmin(np.abs(self.time - tbeg))]

        self.time = self.time[indt]
        nt = len(self.time)
        nrho = np.max(self.lpfp) + 1

        self.psi0 = self.psi0[indt]
        self.psix = self.psix[indt]

        for key in self.ssqnames:
            self.__dict__[key] = self.__dict__[key][indt]
        for key in ('pfl', 'tfl', 'ffp', 'rinv', 'q', \
             'area',  'vol',  'pres',  'jpol', \
            'darea', 'dvol', 'dpres', 'djpol') :
            if self.__dict__[key] is not None:
                self.__dict__[key] = self.__dict__[key][indt, :nrho]

        ## Geometric major axis [m]
        self.R0 = 1.65
        ## Central magnetic field F/R [T]
        self.B0 = self.jpol[..., 0]*2e-7/self.R0
        ## Magnetic field on magnetic axxis [T]
        self.Baxis = self.jpol[..., 0]*2e-7/self.Rmag
        ## Normalised poloidal flux [Vs]
        self.psiN = (self.pfl             - self.psi0[..., None]) / \
                    (self.psix[..., None] - self.psi0[..., None])

        grad_area = np.apply_along_axis(np.gradient, -1, self.area)

        if self.ffp is not None:
            self.jav = 2.*np.pi*self.dpres/self.rinv + self.ffp*self.rinv/2e-7
            curr_prof = np.cumsum(self.jav*grad_area, axis=-1)
        ## Plasma current [A] as integral of current density
            self.ip = curr_prof[..., -1]

        self.q[..., -1] = 2*self.q[..., -2] - self.q[..., -3]
        ## Unnormalised rho toroidal
        self.rho_tor = np.sqrt(np.abs(self.tfl/(np.pi*self.B0[..., None])))
        ## Normalised rho toroidal
        self.rho_tor_n = np.zeros_like(self.tfl)
        self.rhotor_trapz = np.zeros_like(self.tfl) # for RABBIT
        ## Normalised toroidal flux [Vs]
        self.tfln = np.zeros_like(self.tfl)
        for jt in range(nt):
            tf = self.tfl[jt]
            torflux_trapz = cumtrapz(-self.q[jt], x=self.pfl[jt], initial=0.)
            self.tfln[jt, :] = tf/tf[-1]
            self.rho_tor_n[jt, 1:] = np.sqrt((tf[1:] - tf[0])/(tf[-1] - tf[0]))
            self.rhotor_trapz[jt, 1:] = np.sqrt( torflux_trapz[1:] / (torflux_trapz[-1] - torflux_trapz[0]) )

        self.pfm = self.pfm[:, :, indt]


    def read_pfm(self):

        """
        Reads PFM matrix
        """

        nt = len(self.time)
        nR = len(self.Rmesh)
        nZ = len(self.Zmesh)
        ## Poloidal flux matrix [Vs]
        self.pfm = self.sf.getobject('PFM')[: nR, : nZ, :nt]


    def read_ssq(self):

        """
        Creating attributes corresponding to SSQNAM.
        Beware: in different shotfiles, for a given j0 
        SSQ[j0, time] can represent a different variable.
        This routine handles it consistently.
        """

        ssqs   = self.sf.getobject('SSQ') # Time is second
        ssqnam = self.sf.getobject('SSQnam')

        nt = len(self.time)
        ## Names of SSQ parameters
        self.ssqnames = []
        for jssq in range(ssqnam.shape[1]):
            tmp = b''.join(ssqnam[:, jssq]).strip()
            lbl = tmp.decode('utf8')
            if lbl.strip() != '':
                if lbl not in self.ssqnames: # avoid double names
                    self.ssqnames.append(lbl)
                    ## Scalar quantities
                    self.__dict__[lbl] = ssqs[jssq, :nt]


    def read_scalars(self):

        """
        Reads R, z, psi at magnetic axis and separatrix, only if attribute 'r0' is missing.
        equ_map.r0 is deleted at any equ_map.Open, equ_map.Close call.
        """

        self.read_ssq()

        nt = len(self.time)
# Position of mag axis, separatrixx

        PFxx = self.sf.getobject('PFxx')[:, :nt]
        ikCAT = np.argmin(abs(PFxx[1:, :] - PFxx[0, :]), axis=0) + 1
        if all(PFxx[2]) == 0: ikCAT[:] = 1  #troubles with TRE equilibrium 

        ## Poloidal flux at magnetic axis [Vs]
        self.psi0 = PFxx[0, :nt]
        ## Poloidal flux at separatrix [Vs]
        self.psix = PFxx[ikCAT, np.arange(nt)]

        try:
            ## Plasma current[A]
            self.ipipsi = self.sf.getobject('IpiPSI')[:nt]
        except:
            logger.exception('Signal IpiPSI not found')


    def read_profiles(self):
        """Reading 1D quantities, including some derivatives"""

        ## Toroidal flux(t, rho) [Vs]
        self.tfl = self.get_profile('TFLx')
        ## Poloidal flux (t, rho) [Vs]
        self.pfl = self.get_profile('PFL')
        ## Safety factor(t, rho)
        self.q     = self.get_profile('Qpsi')
        ## FF'
        self.ffp   = self.get_profile('FFP')
        self.rinv  = self.get_profile('Rinv')
        self.r2inv = self.get_profile('R2inv')
        self.bave  = self.get_profile('Bave')
        self.b2ave = self.get_profile('B2ave')

        ## dVolume/dPsi [m**3/Vs]
        self.vol , self.dvol  = self.get_mixed('Vol')
        ## dArea/dPsi [m**2/Vs]
        self.area, self.darea = self.get_mixed('Area')
        ## dPres/dPsi [Pa/Vs]
        self.pres, self.dpres = self.get_mixed('Pres')
        self.jpol, self.djpol = self.get_mixed('Jpol')


    def get_profile(self, var_name):

        """
        var_name: str
            name of the quantity, like
            Qpsi       q_value vs PFL
            Bave       <B>vac
            B2ave      <B^2>vac
            FFP        ff'
            Rinv       <1/R>
            R2inv      <1/R^2>
            FTRA       fraction of the trapped particles
        Output:
            array(t, rho) with some metadata (units, description)
        """

        nt = len(self.time)

        profs = ('TFLx', 'PFL', 'FFP', 'Qpsi', 'Rinv', 'R2inv', 'Bave', 'B2ave')

        if var_name not in profs:
            logger.error('SignalGroup %s unknown' %var_name)
            return None

        tmp = self.sf.getobject(var_name)
        if tmp is None:
            return None
        var = tmp[:, :nt]

        nrho = np.max(self.lpfp + 1 + self.lpfe)
        
        var_sorted = sfobj.SFOBJ(np.zeros((nt, nrho)), sfho=tmp)
        for jt in range(nt):
            sort_wh = self.ind_sort[jt]
            nr = len(sort_wh)
            var_sorted [jt, :nr] = var[sort_wh, jt]
            if nr < nrho:
                var_sorted[jt, nr:] = var_sorted[jt, nr-1]

        return var_sorted


    def get_mixed(self, var_name):

        """
        var_name: str
            name of the quantity, like
            Jpol       poloidal current,
            Pres       pressure
            Vol        plasma Volume
            Area       plasma Area
        Output:
            array-pair (quantity(t, rho), derivative(t, rho)) with some metadata (units, description)
        """

        nt = len(self.time)
        mixed = ('Vol', 'Area', 'Pres', 'Jpol')

# Pairs prof, d(prof)/d(psi)

        if var_name not in mixed:
            logger.error('%s not one of the mixed quanties Vol, Area, Pres, Jpol' %var_name)
            return None, None

        tmp = self.sf.getobject(var_name)
        var  = tmp[ ::2, :nt]
        dvar = tmp[1::2, :nt]

        nrho = np.max(self.lpfp + 1 + self.lpfe)
        info  = type('', (), {})()
        dinfo = type('', (), {})()
        for key, val in tmp.__dict__.items():
            if key != 'data':
                info.__dict__[key] = val
                if key == 'phys_unit':
                    dinfo.__dict__[key] = '%s/%s' %(val, self.pfl.phys_unit)
                else:
                    dinfo.__dict__[key] = val
        var_sorted  = sfobj.SFOBJ( np.zeros((nt, nrho)), sfho=info)
        dvar_sorted = sfobj.SFOBJ( np.zeros((nt, nrho)), sfho=dinfo)
        for jt in range(nt):
            sort_wh = self.ind_sort[jt]
            nr = len(sort_wh)
            var_sorted [jt, :nr] = var [sort_wh, jt]
            dvar_sorted[jt, :nr] = dvar[sort_wh, jt]
            if nr < nrho:
                var_sorted [jt, nr:] = var_sorted[jt, nr-1]

        return var_sorted, dvar_sorted


if __name__ == '__main__':


    nshot = 28053
    eqm = EQU(nshot)
    logger.info(eqm.ssqnames)

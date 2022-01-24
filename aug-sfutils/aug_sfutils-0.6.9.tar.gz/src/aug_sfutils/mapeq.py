"""
Equilibrium utilities library
"""

import sys, time, logging
import numpy as np
from scipy.ndimage.interpolation import map_coordinates
from scipy.interpolate import UnivariateSpline, interp1d, InterpolatedUnivariateSpline, RectBivariateSpline
from aug_sfutils import cocos

logger = logging.getLogger('aug_sfutils.mapeq')
logger.setLevel(logging.INFO)


def get_nearest_index(tim_eq, tarr):
    """Find nearest time index for a given time.
    For internal use only.
    """

    tim_eq = np.atleast_1d(np.array(tim_eq, dtype=np.float32))
    if len(tim_eq) == 1:
        unique_idx = [0]
        index_idx = {0: [0]}
    else:
        tarr = np.minimum(np.maximum(tarr, tim_eq[0]), tim_eq[-1])
        idx = interp1d(tim_eq, np.arange(len(tim_eq)), kind='nearest', assume_sorted=True)(tarr)
        idx = idx.astype(np.int32)
        unique_idx = np.unique(idx)
        index_idx = {}
        for i in unique_idx:
            (index_idx[i], ) = np.where(idx == i)

    return unique_idx, index_idx


def rho2rho(eqm, rho_in, t_in=None, \
           coord_in='rho_pol', coord_out='rho_tor', extrapolate=False):

    """Mapping from/to rho_pol, rho_tor, r_V, rho_V, Psi, r_a
    r_V is the STRAHL-like radial coordinate

    Input
    ----------
    eqm: equilibrium object
    t_in : float or 1darray or None
        time (eqm.time if None)
    rho_in : float, ndarray
        radial coordinates, 1D (time constant) or 2D+ (time variable) of size (nt,nx,...)
    coord_in:  str ['rho_pol', 'rho_tor' ,'rho_V', 'r_V', 'Psi','r_a']
        input coordinate label
    coord_out: str ['rho_pol', 'rho_tor' ,'rho_V', 'r_V', 'Psi','r_a']
        output coordinate label
    extrapolate: bool
        extrapolate rho_tor, r_V outside the separatrix

    Output
    -------
    rho : 2d+ array (nt, nr, ...)
    converted radial coordinate
    """

    logger.debug('Start rho2rho')
    if t_in is None:
        t_in = eqm.time

    tarr = np.atleast_1d(t_in)
    rho = np.atleast_1d(rho_in)

    nt_in = np.size(tarr)

    if rho.ndim == 1:
        rho = np.tile(rho, (nt_in, 1))

# Trivial case
    if coord_out == coord_in: 
        return rho
 
    unique_idx, index_idx =  get_nearest_index(eqm.time, tarr)

    if coord_in in ['rho_pol', 'Psi']:
        label_in = eqm.pfl
        lbl_in = 'pfl'
    elif coord_in == 'rho_tor':
        label_in = eqm.tfl
        lbl_in = 'tfl'
    elif coord_in in ['rho_V','r_V']:
        label_in = eqm.vol
        R0 = eqm.Rmag
        lbl_in = 'vol'
    elif coord_in == 'r_a':
        R, _ = rhoTheta2rz(eqm, eqm.pfl, [0, np.pi], coord_in='Psi')
        label_in = (R[:, 0] - R[:, 1]).T**2
        lbl_in = 'r_a'
    else:
        raise Exception('unsupported input coordinate')

    if coord_out in ['rho_pol', 'Psi']:
        label_out = eqm.pfl
        lbl_out = 'pfl'
    elif coord_out == 'rho_tor':
        label_out = eqm.tfl
        lbl_out = 'tfl'
    elif coord_out in ['rho_V','r_V']:
        label_out = eqm.vol
        R0 = eqm.Rmag
        lbl_out = 'vol'
    elif coord_out == 'r_a':
        R, _ = rhoTheta2rz(eqm, eqm.pfl[unique_idx], [0, np.pi], \
                    t_in=eqm.time[unique_idx], coord_in='Psi')
        label_out = np.zeros_like(eqm.pfl)
        label_out[unique_idx, :] = (R[:, 0] - R[:, 1])**2
        lbl_out = 'r_a'
    else:
        raise Exception('unsupported output coordinate')

    psi_sign = np.sign(eqm.psi_fac)
    PFL  = psi_sign*eqm.pfl
    PSIX = psi_sign*eqm.psix
    PSI0 = psi_sign*eqm.psi0
    rho_output = np.zeros_like(rho)

    for i in unique_idx:
  
# Calculate a normalized input and output flux 

        mag_out, sep_out = np.interp([PSI0[i], PSIX[i]],  PFL[i], label_out[i])
        if lbl_in != lbl_out:
            mag_in, sep_in = np.interp([PSI0[i], PSIX[i]],  PFL[i], label_in[i])
        else:
            mag_in = mag_out
            sep_in = sep_out

        if (abs(sep_out - mag_out) < 1e-4) or (abs(sep_in - mag_in) < 1e-4): #corrupted timepoint
            continue

# Normalize between 0 and 1
        rho_out = (label_out[i] - mag_out)/(sep_out - mag_out)
        rho_in  = (label_in [i] - mag_in )/(sep_in  - mag_in )

        rho_out[(rho_out > 1) | (rho_out < 0)] = 0  #remove rounding errors
        rho_in[ (rho_in  > 1) | (rho_in  < 0)] = 0

        rho_out = np.r_[np.sqrt(rho_out), 1]
        rho_in  = np.r_[np.sqrt(rho_in ), 1]

        ind = (rho_out==0) | (rho_in==0)
        rho_out, rho_in = rho_out[~ind], rho_in[~ind]
        
# Profiles can be noisy!  smooth spline must be used
        sortind = np.unique(rho_in, return_index=True)[1]
        w = np.ones_like(sortind)*rho_in[sortind]
        w = np.r_[w[1]/2, w[1:], 1e3]
        ratio = rho_out[sortind]/rho_in[sortind]
        rho_in = np.r_[0, rho_in[sortind]]
        ratio = np.r_[ratio[0], ratio]

        s = UnivariateSpline(rho_in, ratio, w=w, k=4, s=5e-3,ext=3)  #BUG s = 5e-3 can be sometimes too much, sometimes not enought :( 

        jt = index_idx[i]
        rho_ = np.copy(rho[jt])

        r0_in = 1
        if coord_in == 'r_V' :
            r0_in  = np.sqrt(sep_in/ (2*np.pi**2*R0[i]))
        r0_out = 1
        if coord_out == 'r_V' :
            r0_out = np.sqrt(sep_out/(2*np.pi**2*R0[i]))

        if coord_in == 'Psi' :
            rho_  = np.sqrt(np.maximum(0, (rho_ - eqm.psi0[i])/(eqm.psix[i] - eqm.psi0[i])))

# Evaluate spline

        rho_output[jt] = s(rho_.flatten()/r0_in).reshape(rho_.shape)*rho_*r0_out/r0_in

        if np.any(np.isnan(rho_output[jt])):  # UnivariateSpline failed
            rho_output[jt] = np.interp(rho_/r0_in, rho_in, ratio)*rho_*r0_out/r0_in
            
        if not extrapolate:
            rho_output[jt] = np.minimum(rho_output[jt],r0_out) # rounding errors

        rho_output[jt] = np.maximum(0,rho_output[jt]) # rounding errors

        if coord_out  == 'Psi':
            rho_output[jt]  = rho_output[jt]**2*(eqm.psix[i] - eqm.psi0[i]) + eqm.psi0[i]

    logger.debug('End rho2rho')
    return rho_output


def rz2brzt(eqm, r_in, z_in, t_in=None):

    """calculates Br, Bz, Bt profiles
    Input
    ----------
    eqm: equilibrium object
    r_in : ndarray
        R coordinates 
        1D, size(nrz_in) or 2D, size (nt, nrz_in)
    z_in : ndarray
        Z coordinates 
        1D, size(nrz_in) or 2D, size (nt, nrz_in)
    t_in : float or 1darray or None
        time (eqm.time if None)

    Output
    -------
    interpBr : ndarray
        profile of Br(nt, nrz_in)
    interpBz : ndarray
        profile of Bz(nt, nrz_in)
    interpBt : ndarray
        profile of Bt(nt, nrz_in)
    """

    if t_in is None:
        t_in = eqm.time
        
    tarr = np.atleast_1d(t_in)
    r_in = np.atleast_1d(r_in)
    z_in = np.atleast_1d(z_in)

    nt = np.size(tarr)
    nrz_in = r_in.shape[-1]

    if r_in.shape != z_in.shape:
        logger.error('r_in and z_in must have the same shape')
        return

    if r_in.ndim == 2 and r_in.shape[0] != nt:
        logger.error('Time array missmatching first dim of r_in')
        return

    if np.size(r_in, 0)!= nt:
        r_in = np.tile(r_in, nt).reshape((nt, nrz_in))
        z_in = np.tile(z_in, nt).reshape((nt, nrz_in))

    interpBr = np.zeros((nt, nrz_in), dtype=np.float32)
    interpBz = np.zeros((nt, nrz_in), dtype=np.float32)
    interpBt = np.zeros((nt, nrz_in), dtype=np.float32)

    from scipy.constants import mu_0
    nr, nz = len(eqm.Rmesh), len(eqm.Zmesh)
    dr = (eqm.Rmesh[-1] - eqm.Rmesh[0])/float(nr - 1)
    dz = (eqm.Zmesh[-1] - eqm.Zmesh[0])/float(nz - 1)

    unique_idx, index_idx =  get_nearest_index(eqm.time, tarr)

    for i in unique_idx:

        jt = index_idx[i]
        Psi = eqm.pfm[:, :, i]
        Br = np.apply_along_axis(np.gradient, 1,  Psi)/eqm.Rmesh[:, None]
        Bz = np.apply_along_axis(np.gradient, 0, -Psi)/eqm.Rmesh[:, None]
        fBt = interp1d(eqm.pfl[i], eqm.jpol[i], kind='linear', fill_value='extrapolate')
        Bt = fBt(Psi)*mu_0/eqm.Rmesh[:, None]
        r = r_in[jt] #np.squeeze(r_in[jt])
        z = z_in[jt] #np.squeeze(z_in[jt])
        f_br = RectBivariateSpline(eqm.Rmesh, eqm.Zmesh, Br, kx=2, ky=2)
        f_bz = RectBivariateSpline(eqm.Rmesh, eqm.Zmesh, Bz, kx=2, ky=2)
        f_bt = RectBivariateSpline(eqm.Rmesh, eqm.Zmesh, Bt, kx=2, ky=2)
        interpBr[jt] = f_br(r, z, grid=False)
        interpBz[jt] = f_bz(r, z, grid=False)
        interpBt[jt] = f_bt(r, z, grid=False)

    return interpBr/(-abs(eqm.psi_fac)*dz), \
           interpBz/(-abs(eqm.psi_fac)*dr), \
           interpBt/eqm.psi_fac * eqm.phi_sign


def Bmesh(eqm, t_in=None):

    """calculates Br, Bz, Bt profiles
    Input
    ----------
    eqm: equilibrium object
    t_in : float or 1darray or None
        time (eqm.time if None)

    Output
    -------
    Br : ndarray
        profile of Br on the PFM grid
    Bz : ndarray
        profile of Bz on the PFM grid
    interpBt : ndarray
        profile of Bt on the PFM grid
    """

    if t_in is None:
        t_in = eqm.time

    tarr = np.atleast_1d(t_in)
    nt = len(tarr)

# Poloidal current 

    from scipy.constants import mu_0

    nr = len(eqm.Rmesh)
    nz = len(eqm.Zmesh)
    dr = (eqm.Rmesh[-1] - eqm.Rmesh[0])/float(nr - 1)
    dz = (eqm.Zmesh[-1] - eqm.Zmesh[0])/float(nz - 1)

    unique_idx, index_idx =  get_nearest_index(eqm.time, tarr)

    Br = np.zeros((nt, nr, nz), dtype=np.float32)
    Bz = np.zeros_like(Br)
    Bt = np.zeros_like(Br)
    for i in unique_idx:

        jt = index_idx[i]
        Psi = eqm.pfm[:, :, i]
# Eq 12 in COCOs paper
        Br[jt] = np.apply_along_axis(np.gradient, 1,  Psi)/eqm.Rmesh[:, None]
        Bz[jt] = np.apply_along_axis(np.gradient, 0, -Psi)/eqm.Rmesh[:, None]
        fBt = interp1d(eqm.pfl[i], eqm.jpol[i], kind='linear', fill_value='extrapolate')
        Bt[jt] = fBt(Psi)*mu_0/eqm.Rmesh[:, None]

    return Br/(-abs(eqm.psi_fac)*dz), \
           Bz/(-abs(eqm.psi_fac)*dr), \
           Bt/eqm.psi_fac * eqm.phi_sign


def rz2rho(eqm, r_in, z_in, t_in=None, coord_out='rho_pol', extrapolate=True):

    """
    Equilibrium mapping routine, map from R,Z -> rho (pol,tor,r_V,...)
    Fast for a large number of points

    Input
    ----------
    eqm: equilibrium object
    t_in : float or 1darray or None
        time (eqm.time if None)
    r_in : ndarray
        R coordinates 
        1D (time constant) or 2D+ (time variable) of size (nt,nx,...)
    z_in : ndarray
        Z coordinates 
        1D (time constant) or 2D+ (time variable) of size (nt,nx,...)
    coord_out: str
        mapped coordinates - rho_pol,  rho_tor, r_V, rho_V, Psi
    extrapolate: bool
        extrapolate coordinates (like rho_tor) for values larger than 1

    Output
    -------
    rho : 2D+ array (nt,nx,...)
    Magnetics flux coordinates of the points
    """

    if t_in is None:
        t_in = eqm.time

    tarr = np.atleast_1d(t_in)
    r_in = np.atleast_2d(r_in)
    z_in = np.atleast_2d(z_in)

    dr = (eqm.Rmesh[-1] - eqm.Rmesh[0])/(len(eqm.Rmesh) - 1)
    dz = (eqm.Zmesh[-1] - eqm.Zmesh[0])/(len(eqm.Zmesh) - 1)

    nt_in = np.size(tarr)

    if np.size(r_in, 0) == 1:
        r_in = np.tile(r_in, (nt_in, 1))
    if np.size(z_in, 0) == 1:
        z_in = np.tile(z_in, (nt_in, 1))

    if r_in.shape!= z_in.shape:
        raise Exception('Wrong shape of r_in or z_in')
    
    if np.size(r_in,0) != nt_in:
        raise Exception('Wrong shape of r_in %s, nt=%d' %(str(r_in.shape), nt_in))
    if np.size(z_in,0) != nt_in:
        raise Exception('Wrong shape of z_in %s, nt=%d' %(str(z_in.shape), nt_in))
    if np.shape(r_in) != np.shape(z_in):
        raise Exception( 'Not equal shape of z_in and r_in %s,%s'\
                        %(str(z_in.shape), str(z_in.shape)) )

    Psi = np.empty((nt_in,)+r_in.shape[1:], dtype=np.single)

    scaling = np.array([dr, dz])
    offset  = np.array([eqm.Rmesh[0], eqm.Zmesh[0]])
    
    unique_idx, index_idx =  get_nearest_index(eqm.time, tarr)

    for i in unique_idx:
        jt = index_idx[i]
        coords = np.array((r_in[jt], z_in[jt]))
        index = ((coords.T - offset) / scaling).T
        Psi[jt] =  map_coordinates(eqm.pfm[:, :, i], index, mode='nearest',
                                   order=2, prefilter=True)

    rho_out = rho2rho(eqm, Psi, t_in=t_in, extrapolate=extrapolate, \
              coord_in='Psi', coord_out=coord_out)

    return rho_out


def rho2rz(eqm, rho_in, t_in=None, coord_in='rho_pol', all_lines=False):

    """
    Get R, Z coordinates of a flux surfaces contours

    Input
    ----------
    eqm: equilibrium object
    t_in : float or 1darray
        time (eqm.time if None)
    rho_in : 1darray,float
        rho coordinates of the searched flux surfaces
    coord_in: str
        mapped coordinates - rho_pol or rho_tor
    all_lines: bool:
        True - return all countours , False - return longest contour

    Output
    -------
    rho : array of lists of arrays [npoinst,2]
        list of times containg list of surfaces for different rho 
        and every surface is decribed by 2d array [R,Z]
    """

    if t_in is None:
        t_in = eqm.time

    tarr  = np.atleast_1d(t_in)
    rhoin = np.atleast_1d(np.array(rho_in, dtype=np.float32))

    rho_in = rho2rho(eqm, rhoin, t_in=t_in, \
             coord_in=coord_in, coord_out='Psi', extrapolate=True )

    from matplotlib import _contour

    nt = len(tarr)
    nr = len(eqm.Rmesh)
    nz = len(eqm.Zmesh)

    R, Z = np.meshgrid(eqm.Rmesh, eqm.Zmesh)
    Rsurf = np.empty(nt, dtype='object')
    zsurf = np.empty(nt, dtype='object')
    unique_idx, index_idx = get_nearest_index(eqm.time, tarr)

    for i in unique_idx:

        jt = index_idx[i]
        Flux = rho_in[jt[0]]

# matplotlib's contour creation
        try:
            cgen = _contour.QuadContourGenerator(R, Z, eqm.pfm[:nr, :nz, i].T, None, True, 0)
        except Exception as e:
            logger.exception(R.shape, Z.shape, eqm.pfm[:nr, :nz, i].T.shape)
            raise e 

        Rs_t = []
        zs_t = []

        for jfl, fl in enumerate(Flux):
            segs = cgen.create_contour(fl)
            n_segs = len(segs)
            if n_segs == 0:
                if fl == eqm.psi0[i]:
                    Rs_t.append(np.atleast_1d(eqm.Rmag[i]))
                    zs_t.append(np.atleast_1d(eqm.Zmag[i]))
                else:
                    Rs_t.append(np.zeros(1))
                    zs_t.append(np.zeros(1))
                continue
            elif all_lines: # for open field lines
                line = np.vstack(segs)
            else:  #longest filed line, default
                line = []
                for l in segs:
                    if len(l) > len(line):
                        line = l

            R_surf, z_surf = list(zip(*line))
            R_surf = np.array(R_surf, dtype = np.float32)
            z_surf = np.array(z_surf, dtype = np.float32)
            if not all_lines:
                ind = (z_surf >= eqm.Zunt[i])
                if len(ind) > 1:
                    R_surf = R_surf[ind]
                    z_surf = z_surf[ind]
            Rs_t.append(R_surf)
            zs_t.append(z_surf)
   
        for j in jt:
            Rsurf[j] = Rs_t
            zsurf[j] = zs_t

    return Rsurf, zsurf


def cross_surf(eqm, rho=1., r_in=1.65, z_in=0, line_m=2, theta_in=0, t_in=None, coord_in='rho_pol'):

    """
    Computes intersections of a line with any flux surface.

    Input:
    ----------
    eqm: equilibrium object
    rho: float or 1D array(nt)
        coordinate of the desired flux surface
    t_in: float or 1darray(nt)
        time (eqm.time in case of None)
    r_in: float
        R position of the point
    z_in: float
        z position of the point
    theta_in: float
        angle of the straight line with respect to horizontal-outward
    coord_in:  str ['rho_pol', 'rho_tor' ,'rho_V', 'r_V', 'Psi','r_a']
        input coordinate label

    Output:
    ----------
    Rout: 3darray size(nt, 2)
        R-position of intersections
    zout: 3darray size(nt, 2)
        z-position of intersections
    """

    if t_in is None:
        t_in = eqm.time

    tarr = np.atleast_1d(t_in)
    rho  = np.atleast_1d(rho)
    r_in = np.float32(r_in)
    z_in = np.float32(z_in)

    unique_idx, index_idx = get_nearest_index(eqm.time, tarr)

    n_line = int(200*line_m) + 1 # 1 cm, but then there's interpolation!
    t = np.linspace(-line_m, line_m, n_line, dtype=np.float32)

    line_r = t*np.cos(theta_in) + r_in
    line_z = t*np.sin(theta_in) + z_in

    rho_line = rz2rho(eqm, line_r, line_z, t_in=eqm.time[unique_idx], \
                           coord_out=coord_in, extrapolate=True)

    nt_in = len(tarr)
    Rout = np.nan*np.ones((nt_in, 2), dtype=np.float32)
    zout = np.nan*np.ones((nt_in, 2), dtype=np.float32)
    for i, ii in enumerate(unique_idx):
        jt = index_idx[ii]
        if len(rho) == 1:
            rho_ref = rho[0]
        else:
            rho_ref = rho[jt[0]]
        ind_cross = np.argwhere(np.diff(np.sign(rho_line[i] - rho_ref))).flatten()

        if len(ind_cross) > 2:
            logger.warning('More than 2 intersections at t=%.3f', tarr[jt[0]])
            continue

        if len(ind_cross) == 0:
            logger.warning('No intersections found at t=%.3f', tarr[jt[0]])
            continue

        pos = 0
        for j in ind_cross:
            if rho_line[i, j + 1] > rho_line[i, j]:
                ind = [j, j + 1]
            else:
                ind = [j + 1, j]
            ztmp = np.interp(rho_ref, rho_line[i, ind], line_z[ind])
            if ztmp >= eqm.Zunt[ii] and ztmp <= eqm.Zoben[ii]:
                zout[jt, pos] = ztmp
                Rout[jt, pos] = np.interp(rho_ref, rho_line[i, ind], line_r[ind])
                pos += 1
    del line_r, line_z, rho_line

    return Rout, zout


def cross_sep(eqm, r_in=1.65, z_in=0, line_m=2., theta_in=0, t_in=None):

    """
    Computes intersections of a line with any flux surface.

    Input:
    ----------
    eqm: equilibrium object
    t_in: float or 1darray
        time (eqm.time in case of None)
    r_in: float
        R position of the point
    z_in: float
        z position of the point
    theta_in: float
        angle of the straight line with respect to horizontal-outward

    Output:
    ----------
    Rout: 3darray size(nt, nx, 2)
        R-position of intersections
    zout: 3darray size(nt, nx, 2)
        z-position of intersections
    """

    if t_in is None:
        t_in = eqm.time
    tarr = np.atleast_1d(t_in)
    unique_idx, index_idx = get_nearest_index(eqm.time, tarr)

    psi_sep = eqm.pfl[unique_idx, max(eqm.lpfp)]

    return cross_surf(eqm, rho=psi_sep, r_in=r_in, z_in=z_in, line_m=line_m, theta_in=theta_in, t_in=t_in, coord_in='Psi')


def rhoTheta2rz(eqm, rho, theta_in, t_in=None, coord_in='rho_pol', n_line=201):
    
    """
    This routine calculates the coordinates R, z of the intersections of
    a ray starting at the magnetic axis with fluxsurfaces 
    at given values of some radial coordinate.
    (slower than countours)

    Input:
    ----------
    rho: float or 1D array (nr) or nD array (nt,nr,...)
        coordinate of the desired flux surface inside LCFS!
    t_in: float or 1darray
        time (eqm.time in case of None)
    theta_in: float or 1D array n_theta
        angle of the straight line with respect to horizontal-outward, in radians!!
    coord_in:  str ['rho_pol', 'rho_tor' ,'rho_V', 'r_V', 'Psi','r_a']
        input coordinate label

    Output:
    ----------
    R ,  z: 3d+ array size(nt, n_theta, nr,...)
    """

    if t_in is None:
        t_in = eqm.time

    tarr = np.atleast_1d(t_in)

    nt_in = len(tarr)

    rho  = np.atleast_1d(rho)
    if rho.ndim == 1:
        rho = np.tile(rho, (nt_in, 1))

    theta_in = np.atleast_1d(theta_in)[:, None]
    ntheta = len(theta_in)

    unique_idx, index_idx = get_nearest_index(eqm.time, tarr)

# n_line = 201 <=> 5 mm, but then there's interpolation!

    line_r = np.empty((len(unique_idx), ntheta, n_line))
    line_z = np.empty((len(unique_idx), ntheta, n_line))

    line_m = .9 # line length: 0.9 m
    t = np.linspace(0, 1, n_line)**.5*line_m
    c, s = np.cos(theta_in), np.sin(theta_in)
   
    tmpc = c*t
    tmps = s*t
    for i, ii in enumerate(unique_idx):
        line_r[i] = tmpc + eqm.Rmag[ii]
        line_z[i] = tmps + eqm.Zmag[ii]
 
    rho_line = rz2rho(eqm, line_r, line_z, eqm.time[unique_idx], \
                           coord_out=coord_in , extrapolate=True)

    R = np.empty((nt_in, ntheta) + rho.shape[1:], dtype=np.float32)
    z = np.empty((nt_in, ntheta) + rho.shape[1:], dtype=np.float32)

    jcoco = eqm.cocos%10 - 1
    if coord_in == 'Psi':
        rho_line[:,:,0] = eqm.psi0[unique_idx][:,None]
        rho_line *= -eqm.ip_ccw*cocos.sigma['bp'][jcoco]
        rho      *= -eqm.ip_ccw*cocos.sigma['bp'][jcoco]
    else:
        #solve some issues very close to the core
        rho_line[:,:,0] = 0

    for i, ii in enumerate(unique_idx):
        jt = index_idx[ii]
        for k in range(ntheta):
            rho_lin = rho_line[i, k]
            (tmp, ) = np.where(np.diff(rho_lin) > 0)
            imax = tmp[-1] + 1
            rspl = InterpolatedUnivariateSpline(rho_lin[:imax], \
                   line_r[i, k, :imax], k=2) 
            
            R[jt, k] = rspl(rho[jt].flatten()).reshape(rho[jt].shape)

            zspl = InterpolatedUnivariateSpline( \
                   rho_line[i, k, :imax], line_z[i, k, :imax], k=2)
            z[jt, k] = zspl(rho[jt].flatten()).reshape(rho[jt].shape)

    return R, z


def mag_theta_star(eqm, t_in, n_rho=400, n_theta=200, rz_grid=False ):
    
    """
    Computes theta star 

    Input:
    ----------
    eqm: equilibrium object
    t_in: float 
        time point for the evaluation
    n_rho: int
        number of flux surfaces equaly spaced from 0 to 1 of rho_pol
    n_theta: int
        number of poloidal points 
    rz_grid: bool
        evaluate theta star on the grid

    Output:
    ----------
    R, z, theta: 3d arrays size(n_rho, n_theta)
    """

    rho = np.linspace(0, 1, n_rho+1)[1:]
    theta = np.linspace(0, 2*np.pi, n_theta, endpoint=False)

    magr, magz = rhoTheta2rz(eqm, rho, theta, t_in=t_in, coord_in='rho_pol')
    magr, magz = magr[0].T, magz[0].T
    
    r0 = np.interp(t_in, eqm.time, eqm.Rmag)
    z0 = np.interp(t_in, eqm.time, eqm.Zmag)

    drdrho, drtheta = np.gradient(magr)
    dzdrho, dztheta = np.gradient(magz)
    dpsidrho, dpsitheta = np.gradient(np.tile(rho**2, (n_theta, 1)).T )

    grad_rho = np.dstack((drdrho, dzdrho, dpsidrho ))
    grad_theta = np.dstack((drtheta, dztheta, dpsitheta))
    normal = np.cross(grad_rho, grad_theta, axis=-1)

    dpsi_dr = -normal[:, :, 0]/(normal[:, :, 2] + 1e-8) #Bz
    dpsi_dz = -normal[:, :, 1]/(normal[:, :, 2] + 1e-8) #Br

#WARNING not defined on the magnetics axis

    dtheta_star = ((magr - r0)**2 + (magz - z0)**2)/(dpsi_dz*(magz - z0) + dpsi_dr*(magr - r0))/magr
    theta = np.arctan2(magz - z0, - magr + r0)
    
    theta = np.unwrap(theta - theta[:, (0, )], axis=1)
    
    from scipy.integrate import cumtrapz

# Definition of the theta star by integral
    theta_star = cumtrapz(dtheta_star, theta, axis=1, initial=0)
    correction = (n_theta - 1.)/n_theta

    theta_star/= theta_star[:, (-1, )]/(2*np.pi)/correction  #normalize to 2pi

    if not rz_grid:
        return magr, magz, theta_star

# Interpolate theta star on a regular grid 
    cos_th, sin_th = np.cos(theta_star), np.sin(theta_star)
    Linterp = LinearNDInterpolator(np.c_[magr.ravel(),magz.ravel()], cos_th.ravel(),0)
         
    nx = 100
    ny = 150

    rgrid = np.linspace(magr.min(), magr.max(), nx)
    zgrid = np.linspace(magz.min(), magz.max(), ny)

    R,Z = np.meshgrid(rgrid, zgrid)
    cos_grid = Linterp(np.c_[R.ravel(), Z.ravel()]).reshape(R.shape)
    Linterp.values[:, 0] = sin_th.ravel() #trick save a some  computing time
    sin_grid = Linterp(np.c_[R.ravel(), Z.ravel()]).reshape(R.shape)  

    theta_star = np.arctan2(sin_grid, cos_grid)

    return rgrid, zgrid, theta_star


def get_q_surf(eqm, qvalue=1., t_in=None, coord_out='rho_tor'):
    """
    Computes the most external magnetic-surface with a given q-value
    If the value is not found, it returns np.nan at that time point

    Input:
    -----------
    eqm: equilibrium object
    qvalue: float > 0
        Desired q-value for magnetic surface
    t_in : float or 1darray or None
        time (eqm.time if None)
    coord_out: str ['rho_pol', 'rho_tor' ,'rho_V', 'r_V', 'Psi','r_a']
        output coordinate label

    Output:
    -----------
    Float or list rho_surf, same size as t_in
    """

    qvalue = float(qvalue)
    if t_in is None:
        t_in = eqm.time
    tarr = np.atleast_1d(t_in)
    unique_idx, index_idx = get_nearest_index(eqm.time, tarr)

    rho_surf = np.zeros_like(tarr)
    rho_q = rho2rho(eqm, eqm.pfl[unique_idx], t_in=eqm.time[unique_idx], coord_in='Psi', coord_out=coord_out)
    qprof = np.abs(eqm.q)
    for ienum, i in enumerate(unique_idx):
        (nrho, ) = eqm.lpfp[i]
        jmin = np.argmin(qprof[i, :nrho])
        q_surf = np.interp(qvalue, qprof[i, jmin:nrho], rho_q[ienum, jmin:nrho], left=np.nan, right=np.nan)
        for j in index_idx[i]:
            rho_surf[j] = q_surf

    return np.squeeze(rho_surf)


def to_geqdsk(eqm, t_in=0.):
    """
    Parameters
    ----------
    eqm: instance of aug_sfutils.sf2equ.EQU
    t_in : float
        Time in seconds.

    Returns
    -------
    dict :
        Dictionary containing CLISTE results in OMFIT geqdsk format.
        Note that this dictionary does not contain yet all processed results typical of 
        omfit_classes.omfit_eqdsk.OMFITgeqdsk objects.
    """

    equ = cocos.coco2coco(eqm, cocos_out=1)

    jt = np.argmin(np.abs(equ.time - t_in))

    psi_in  = equ.pfl[jt]

    geq = {}

    geq['CASE'] = np.array(['  CLISTE ', '    ', '   ', ' #' + str(equ.shot), '  %.2fs' % t_in, '  ' + 'EQI'], dtype='<U8')
    
    # separatrix R and Z
    geq['RBBBS'], geq['ZBBBS'] = rho2rz(equ, 0.999, t_in=equ.time[jt], all_lines=False)
    geq['RBBBS'] = geq['RBBBS'][0][0]
    geq['ZBBBS'] = geq['ZBBBS'][0][0]

    # R,Z of limiter structures
    geq['RLIM'] = [1.035, 1.050, 1.090, 1.140, 1.235, 1.340, 1.430, 1.505, 1.630, 1.770, 1.970, 2.110, 2.170, 2.205, 2.210, 2.175, 2.130, 2.010, 1.890, 1.705, 1.645, 1.580, 1.458, 1.325, 1.235, 1.286, 1.280, 1.245, 1.125, 1.060, 1.035]

    geq['ZLIM'] = [0.000, 0.250, 0.500, 0.700, 0.965, 1.100, 1.150, 1.190, 1.150, 1.085, 0.780, 0.540, 0.390, 0.210, 0.000, -0.150, -0.280, -0.500, -0.680, -0.860, -0.966, -1.208, -1.060, -1.060, -1.126, -0.976, -0.892, -0.820, -0.634, -0.300, 0.000]

    geq['NW'] = len(equ.Rmesh)
    geq['NH'] = len(equ.Zmesh)
    
    geq['RLEFT']   = equ.Rmesh[0]
    geq['RDIM']    = equ.Rmesh[-1] - equ.Rmesh[0]
    geq['ZDIM']    = equ.Zmesh[-1] - equ.Zmesh[0]
    geq['RMAXIS']  = equ.Rmag[jt]
    geq['ZMAXIS']  = equ.Zmag[jt]
    geq['SIMAG']   = psi_in[0]
    geq['SIBRY']   = psi_in[-1]
    geq['CURRENT'] = equ.ip[jt]
    geq['BCENTR']  = equ.B0[jt]
    geq['RCENTR']  = equ.R0  ##[jt]   # TODO this seems to be time-independent?
    geq['ZMID']    = 0.5*(equ.Zmesh[-1] + equ.Zmesh[0])
    geq['PSIRZ']   = equ.pfm[:, :, jt].T

    # Interpolate onto an equidistant Psi-grid
    psi_grid = np.linspace(psi_in[0], psi_in[-1], len(equ.Rmesh))

    geq['QPSI']   = np.interp(psi_grid, psi_in, equ.q[jt])
    geq['PRES']   = np.interp(psi_grid, psi_in, equ.pres[jt])
    geq['PPRIME'] = np.interp(psi_grid, psi_in, equ.dpres[jt])
    geq['FPOL']   = np.interp(psi_grid, psi_in, 2.e-7*equ.jpol[jt] )
    geq['FFPRIM'] = np.interp(psi_grid, psi_in, -2*np.pi*equ.ffp[jt])

    return geq

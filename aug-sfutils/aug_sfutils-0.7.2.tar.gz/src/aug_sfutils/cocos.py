"""
COCOS utilities
See https://crppwww.epfl.ch/~sauter/cocos/Sauter_COCOS_Tokamak_Coordinate_Conventions.pdf
Especially Table I page 8
"""

import logging
import numpy as np

logger = logging.getLogger('aug_sfutils.cocos')

# Table I page 8

sigma = { \
    'bp'       : [ 1,  1, -1, -1,  1,  1, -1, -1], \
    'rphiz'    : [ 1, -1,  1, -1,  1, -1,  1, -1], \
    'rhothephi': [ 1,  1, -1, -1, -1, -1,  1,  1]}

explain = {'rphiz'    : {1: '(R, phi, Z) r'    , -1: '(R, Z, phi) l'}, \
           'rhothephi': {1: '(rho, the, phi) r', -1: '(rho, phi, the) l'    } }

for key, val in sigma.items():
    sigma[key] = np.array(val)


def check_coco(equ_in, ip_shot='ccw', bt_shot='cw'):
    """
    Routine to assess the COCO of a given equilibrium object

    Input
    --------
    equ_in: equilibrium object
        Tokamak equilibrium

    Output
    --------
    ncoco: int
        COCO number
    """

# dpsi_sign positive if psi_sep > psi0
    dpsi_sign = np.sign(np.mean(equ_in.psix) - np.mean(equ_in.psi0))
# Known plasma discharge
    ccw_ip = 1 if(ip_shot == 'ccw') else -1 # AUG default: 1
    ccw_bt = 1 if(bt_shot == 'ccw') else -1 # AUG default: -1

# Table III

    sign_q  = np.sign(np.nanmean(equ_in.q))
    sign_ip = np.sign(np.nanmean(equ_in.ipipsi))
    sign_bt = np.sign(np.nanmean(equ_in.jpol))
    sigma_rphiz = sign_ip*ccw_ip
    sigma_bp    = dpsi_sign*sign_ip
# Eq 45
    sigma_rhothephi = sign_q*sign_ip*sign_bt
    logger.debug(sigma_bp, sigma_rphiz, sigma_rhothephi)
    for jc, rhothephi in enumerate(sigma['rhothephi']):
        if(sigma['bp'   ][jc] == sigma_bp    and \
           sigma['rphiz'][jc] == sigma_rphiz and \
           rhothephi          == sigma_rhothephi):
            ncoco = jc + 1
            break

# Find out 2*pi factor for Psi

    dphi = np.gradient(equ_in.tfl, axis=1)
    dpsi = np.gradient(equ_in.pfl, axis=1)

# Radial+time average
# It is either q_ratio ~ 1 (COCO > 10) or ~ 2*pi (COCO < 10)
    q_ratio = np.abs(np.nanmean(dphi/(equ_in.q*dpsi)))
    logger.debug('Ratio %8.4f' %q_ratio)
    if q_ratio < 4:
        ncoco += 10

    return ncoco


def coco2coco(equ_in, cocos_out=11):
    """
    Routine to transform an equilibrium object to any wished output COCO

    Input
    --------
    equ_in: equilibrium object
        Tokamak equilibrium
    cocos_out: int
        Wished COC for output equilibrium

    Output
    --------
    equ_out: equilibrium object
        Tokamak equilibrium with COCO=cocos_out
    """

# Assuming SI for both equ_in and equ_out

    cocos_in = equ_in.cocos
    logger.info('COCOS conversion from %d to %d' %(cocos_in, cocos_out))
    jc_in   = cocos_in %10 - 1
    jc_out  = cocos_out%10 - 1
    ebp_in  = cocos_in//10
    ebp_out = cocos_out//10
#    sign_ip_in = np.sign(np.nanmean(equ_in.ipipsi))
# Equation 9, table I, equation 39, 45
    q_sign   = sigma['rhothephi'][jc_in]*sigma['rhothephi'][jc_out]
    phi_sign = sigma['rphiz'][jc_in]*sigma['rphiz'][jc_out]
    psi_sign = sigma['rphiz'][jc_in]*sigma['bp'][jc_in] * sigma['rphiz'][jc_out]*sigma['bp'][jc_out]
    psi_2pi  = (2.*np.pi)**(ebp_out - ebp_in)
    psi_fac = psi_sign*psi_2pi
    try:
        logger.debug(np.mean(equ_in.jav), phi_sign)
    except:
        pass

    equ_out = type('', (), {})()

    for key, val in equ_in.__dict__.items():
        if val is None:
            continue
        if key in ('B0', 'jpol', 'jav', 'tfl', 'ip', 'ipipsi', 'phi_sign'):
            equ_out.__dict__[key] = phi_sign*val
        elif key in ('psi0', 'psix', 'pfl', 'pfm', 'psi_fac'):
            equ_out.__dict__[key] = psi_fac*val
        elif key in ('dpres', 'darea', 'dvol', 'ffp'):
            equ_out.__dict__[key] = val/psi_fac
        elif key in ('djpol', ):
            equ_out.__dict__[key] = val/psi_fac * phi_sign
        elif key in ('q', 'q0', 'q25', 'q50', 'q75', 'q95'):
            equ_out.__dict__[key] = q_sign*val
        else:
            equ_out.__dict__[key] = val
    equ_out.cocos = cocos_out

    return equ_out

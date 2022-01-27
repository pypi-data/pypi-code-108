# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 20:24:31 2021

@author: Alexander Southan
"""

import numpy as np


def eds_to_volume_fraction(eds, rho_polymer=1, rho_swelling=1,
                           eds_mode='subtracted', output='polymer'):
    """
    Equilibrium degree of swelling to polymer or solvent volume fraction.

    Additivity of volumes is assumed, i.e. there is no volume contraction or
    other similar mixing effects during swelling.

    Parameters
    ----------
    eds : float or ndarray
        The measured equilibrium degree(s) of swelling. Can be a float for a
        single value or an ndarray for multiple values.
    rho_polymer : float, optional
        The density of the polymer in the dry state. The default is 1.
    rho_h2o : float, optional
        The density of the swelling medium. The default is 1.
    eds_mode : string, optional
        The way the eds was calculated.
        'subtracted' means:
            eds = (swollen_mass-dry_mass)/dry_mass
        'plain' means:
            eds = swollen_mass/dry_mass
        The default is 'subtracted'.
    output : string, optional
        The value that will be returned. With 'polymer', the polymer volume
        fraction will be returned, with 'solvent' the volume fraction of the
        swelling medium. The default is 'polymer'.

    Returns
    -------
    float or ndarray
        The polymer volume fraction in the swollen material.

    """
    eds = np.asarray(eds)

    if eds_mode == 'subtracted':
        eds = eds
    elif eds_mode == 'plain':
        eds = eds.copy() - 1
    else:
        raise ValueError('No valid value for eds_mode given.')

    v_2s = 1/(eds*rho_swelling/rho_polymer+1)
    if output == 'polymer':
        return v_2s
    elif output == 'solvent':
        return 1-v_2s
    else:
        raise ValueError('No valid value for output given.')

# -*- coding: utf-8 -*-
# This file is part of HeCalc, which calculates (U-Th)/He dates and uncertainties
# Copyright (C) 2021 Peter E. Martin <pemartin92@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
This module takes a dataset and runs Monte Carlo uncertainty modeling.

It contains functions for the Monte Carlo modeling and to generate
histograms and parameterize those histograms if a user so desires.
"""

from scipy.stats import skewnorm as sk
from scipy.optimize import curve_fit
import numpy as np
from .date_calculation import get_date

def make_histogram(mc, parameterize):
    '''
    Create histograms and potentially parameterize them as skew-normal
    probability distribution functions.
    
    Parameters
    ----------
    mc : Array-like
        The list of numbers to place in a histogram
        
    parameterize : bool
        whether to parameterize the histogram
        
    Returns
    -------
    Generates a dictionary with the histogram and potentially parameters.
    the histogram is returned as a list of the bin centers and a list of
    the number of samples within the bin. The parameters areassociated
    with the key "fit distribution", and are a list of the three parameters
    (skewness, location, scale) to calculate a skew-normal distribution
    '''
    # Generate histogram with bins centered
    bins = int(len(mc)/1000)
    if bins>1000:
        bins = 1000
    elif bins<10:
        bins = 10
    histo = list(np.histogram(mc, bins=bins))[::-1]
    histo[0] = (histo[0][1:] + histo[0][:-1]) / 2
    
    # Get stats for skewnormal function if the user called for parameterization
    if parameterize:
        mean = np.mean(mc)
        med = np.median(mc)
        s = np.std(mc)
        skewness = 3*(mean-med)/s
        a = skewness*10
        try:
            p0 = [a, mean, s]
            c, cov = curve_fit(sk.pdf, histo[0], histo[1], p0)
        except:
            print('parameterization unsuccessful, returning only histogram')
            return {'histogram': histo,
                    'fit distribution': [None, None, None]}
        return {'histogram': histo,
                'fit distribution': [c[0],c[1],c[2]]}
    return {'histogram': histo}

def monte_carlo(mc_number, He, He_s=0,
                U238=0, U235=None, Th232=0, Sm147=0,
                Ft238=1, Ft235=1, Ft232=1, Ft147=1,
                U238_s=0, U235_s=None, Th232_s=0, Sm147_s=0,
                Ft238_s=0, Ft235_s=0, Ft232_s=0, Ft147_s=0,
                histogram=False, parameterize=False):
    '''
    Performs Monte Carlo modeling for a (U-Th)/He dataset. Note that
    while all radionuclides are optional and default to 0, at least one
    *MUST* be >0.
    
    Parameters
    ----------
    mc_number : int
        The number of monte carlo cycles to perform
        
    He : float
        The amount of helium measured. The exact units are unimportant
        as long as they are consistent with the other radionuclides
    
    He_s : float, optional
        The uncertainty in He, in the same units
        
    U238 : float, optional
        The amount of 238U measured
        
    U238_s : float, optional
        The uncertainty in 238U
        
    U235 : float, optional
        The amount of 2385U measured. If no 235U is provided, it is assumed
        to be present at the standard ratio of 137.818 238U/235U
        
    U235_s : float, optional
        The uncertainty in 235U, if measured.
        
    Th232 : float, optional
        The amount of Th232 measured
        
    Th232_s : float, optional
        The uncertainty in Th232
        
    Sm147 : float, optional
        The amount of Sm147 measured
        
    Sm147_s : float, optional
        The uncertainty in Sm147
    
    Ft238 : float, optional
        The alpha ejection correction for 238U. Should be between 0-1.
        
    Ft238_s : float, optional
        The uncertainty in Ft238
        
    Ft235 : float, optional
        The alpha ejection correction for 235U. Should be between 0-1.
        
    Ft235_s : float, optional
        The uncertainty in Ft235
        
    Ft232 : float, optional
        The alpha ejection correction for 232Th. Should be between 0-1.
        
    Ft232_s : float, optional
        The uncertainty in Ft232
        
    Ft147 : float, optional
        The alpha ejection correction for 147Sm. Should be between 0-1.
        
    Ft147_s : float, optional
        The uncertainty in Ft147
        
    histogram : bool, optional
        Whether to generate a histogram for the Monte Carlo results
        
    parameterize : bool, optional
        Whether to parameterize the histogram with a skew-normal distribution.
        If histogram is False, parameterize will not be used
        
    Returns
    -------
    Produces a dictionary with entries for the raw and alpha-ejection corrected
    results. Each entry is a dictionary with mean, +/- 68% CI, and % skew. If
    histogram is true, the histogram for each is returned as a list of the bin
    centers and a list of the number of samples within the bin. The parameters
    are associated with the key "fit distribution", and are a list of the three
    parameters (skewness, location, scale) to calculate a skew-normal distribution
    '''
    # Generate arrays of each datum using its uncertainty
    # This is strictly gaussian for now, but could include
    # additional distributions or even arbitrary distributions
    # in the future.
    He = np.random.normal(He, He_s, mc_number)
    U238 = np.random.normal(U238, U238_s, mc_number)
    if U235 == None:
        U235 = U238/137.818
    else:
        U235 = np.random.normal(U235, U235_s, mc_number)
    Th232 = np.random.normal(Th232, Th232_s, mc_number)
    Sm147 = np.random.normal(Sm147, Sm147_s, mc_number)
    Ft238 = np.random.normal(Ft238, Ft238_s, mc_number)
    Ft235 = np.random.normal(Ft235, Ft235_s, mc_number)
    Ft232 = np.random.normal(Ft232, Ft232_s, mc_number)
    Ft147 = np.random.normal(Ft147, Ft147_s, mc_number)
    
    # Call the get_date function to calculate a date for each
    # of the randomly generated data
    MonteCarlo_t = get_date(He, U238, U235, Th232, Sm147,
                            Ft238, Ft235, Ft232, Ft147)
        
    # Create a dictionary to save results to
    mc_results = {'raw date': {},
                  'corrected date': {}}
    # Produce statistics and save
    for t in ['raw date', 'corrected date']:
        mean = np.mean(MonteCarlo_t[t])
        CIs = np.percentile(MonteCarlo_t[t], [15.865, 84.135])
        # CI_low = mean-CIs[0]
        # CI_high = CIs[1]-mean
        mc_results[t]['mean'] = mean
        mc_results[t]['+68% CI'] = CIs[1]
        mc_results[t]['-68% CI'] = CIs[0]
        # mc_results[t]['% Skew'] = (((CI_high/CI_low)-1)*100)
        if histogram:
            histogram_out = make_histogram(MonteCarlo_t[t], parameterize)
            mc_results[t]['histogram'] = histogram_out['histogram']
            if parameterize:
                mc_results[t]['a'] = histogram_out['fit distribution'][0]
                mc_results[t]['u'] = histogram_out['fit distribution'][1]
                mc_results[t]['s'] = histogram_out['fit distribution'][2]
    
    return mc_results
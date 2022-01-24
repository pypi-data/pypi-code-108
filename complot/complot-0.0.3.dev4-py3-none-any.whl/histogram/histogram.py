################################################################################
#                                                                              #
#                                  HISTOGRAM                                   #
#                                                                              #
################################################################################

from scipy.stats import chi2
from scipy.optimize import fsolve
import math
import numpy as np
from scipy.interpolate import interp1d

from collections import namedtuple


_chist = namedtuple('complot_histogram',
                    ['bins', 'counts', 'yerr', 'xerr', 'norm'])


__all__ = ['hist', 'compare_hist', 'compute_pulls', 'errors_poisson', 
           'errors_sW2', 'compute_pdfpulls']


def errors_poisson(data, a=0.318):
  """
  Uses chisquared info to get the poisson interval.
  """
  low, high = chi2.ppf(a/2, 2*data) / 2, chi2.ppf(1-a/2, 2*data + 2) / 2
  return np.array(data-low), np.array(high-data)


def errors_sW2(x, weights=None, range=None, bins=60):
  if weights is not None:
    values = np.histogram(x, bins, range, weights=weights*weights)[0]
  else:
    values = np.histogram(x, bins, range)[0]
  return np.sqrt(values)

# Function to compute pulls and pdfpulls {{{

def compute_pulls(ref_counts:np.ndarray, counts:np.ndarray, counts_l:np.ndarray,
              counts_h:np.ndarray)->np.ndarray:
  """
  This function takes an array of ref_counts (reference histogram) and three
  arrays of the objective histogram: counts, counts_l (counts' lower limit) and
  counts_h (counts' higher limit). It returns the pull of counts wrt ref_counts.
  """
  residuals = counts - ref_counts;
  pulls = np.where(residuals>0, residuals/counts_l, residuals/counts_h)
  return pulls


def compute_pdfpulls(x_pdf:np.ndarray, y_pdf:np.ndarray, x_hist:np.ndarray,
                     y_hist:np.ndarray, y_l:np.ndarray, y_h:np.ndarray)->np.ndarray:
  """
  This function compares one histogram with a pdf. The pdf is given with two
  arrays x_pdf and y_pdf, these are interpolated (and extrapolated if needed),
  contructing a cubic spline. The histogram takes x_hist (bins), y_hist(counts),
  y_l (counts's lower limit) and y_h (counts' upper limit). The result is a
  pull array between the histogram and the pdf.
  (the pdf is expected to be correctly normalized)
  """
  s = interp1d(x_pdf, y_pdf, kind='cubic', fill_value='extrapolate')
  residuals = y_hist - s(x_hist);
  pulls = np.where(residuals>0, residuals/y_l, residuals/y_h)
  return pulls

# }}}


def hist(data, bins=None, weights=None, center_of_mass=False, density=False,
         **kwargs):
  """
  This function is a wrap arround np.histogram so it behaves similarly to it.
  Besides what np.histogram offers, this function computes the center-of-mass
  bins ('cmbins') and the lower and upper limits for bins and counts.
  """

  # Histogram data
  counts, edges = np.histogram(data, bins=bins, weights=weights, density=False,
                               **kwargs)
  cbins = 0.5 * (edges[1:] + edges[:-1])
  #norm = counts.sum()
  #norm = np.trapz(counts,bincs)
  norm = np.sum(counts)*(cbins[1]-cbins[0])

  # Compute the mass-center of each bin
  if center_of_mass:
    for k in range(0,len(edges)-1):
      if counts[k] != 0:
        cbins[k] = np.median( data[(data>=edges[k]) & (data<=edges[k+1])] )

  # compute yerr
  if weights is not None:
    y_errl, y_errh = errors_poisson(counts)
    y_errl = y_errl**2 + errors_sW2(data, weights=weights, bins=bins, **kwargs)**2
    y_errh = y_errh**2 + errors_sW2(data, weights=weights, bins=bins, **kwargs)**2
    y_errl = np.sqrt(y_errl); y_errh = np.sqrt(y_errh)
  else:
    y_errl, y_errh = errors_poisson(counts)

  x_errh = edges[1:] - cbins
  x_errl = cbins - edges[:-1]


  # Normalize if asked so
  if density:
    counts = counts/norm; y_errl = y_errl/norm;  y_errh = y_errh/norm


  result = _chist(cbins, counts, [y_errl, y_errh], [x_errl, x_errh], norm)

  return result


def compare_hist(reference, target, reference_weights=None,
                 target_weights=None, density=False, *args, **kwargs):
  """
  This function compares to histograms in data=[ref, obj] with(/out) weights
  It returns two hisrogram ipo-objects, obj one with pulls, and both of them
  normalized to one.

  Parameters
  ----------
  reference
  target
  reference_weights
  target_weights :
  density
  """
  _reference = hist(reference, weights=reference_weights, density=False,
                    *args, **kwargs)
  _target = hist(target, weights=target_weights, density=False, *args,
                 **kwargs)
  _reference_norm = 1
  _target_norm = 1
  if density:
    _reference_norm = 1/ _reference.counts.sum()
    _target_norm = 1 / _reference.counts.sum()
  _reference.counts = _reference.counts * _reference_norm
  _reference.yerr = [y * _reference_norm for y in _reference.yerr]
  _target.counts = _target.counts * _reference_norm
  _target.yerr = [y * _target_norm for y in _target.yerr]
  pulls = compute_pulls(_reference.counts, _target.counts, *_target.yerr)
  return _reference, _target, pulls


# vim:foldmethod=marker

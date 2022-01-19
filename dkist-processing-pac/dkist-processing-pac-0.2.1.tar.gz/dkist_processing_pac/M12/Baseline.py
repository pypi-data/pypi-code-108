import pickle
import time
import numpy as np
import lmfit
from astropy.io import fits as pyfits
from astropy.time import Time
from dkist_processing_pac import TelescopeModel
from dkist_processing_pac.tag import tag
from dkist_processing_pac.data import S122

def main(map_file, telescope_db, outpre, thinx=10, thiny=10, update_db=False, plot=True, **fit_kwargs):
    """Top-level function for fitting t12 from a 3D stokes map

    This function reads in the data, sets up a TelescopeModel and calls the main fitting function. It then processes
    and distributes the results. The main result is a python pickle file containing the fitter output. Optionally,
    the telescope database can be updated and a fit plot generated.

    The 3D stokes map should be a single FITS file with all data in a single ImageHDU. Those data must have shape
    (X, Y, lambda, 4).

    Parameters
    ----------
    map_file : str
        Location of 3D stokes map

    telescope_db : str
        Location of file containing telescope model parameters as function of date and wavelength

    outpre : str
        Prefix to use when saving fit results. The saved fits and, optionally, fit plot will be saved as OUTPRE.pkl
        and OUTPRE.pdf, respectively.

    thinx : int
        Only load every thinx spatial column from the 3D stokes map

    thiny : int
        Only load every thiny spatial row from the 3D stokes map

    update_db : bool
        If True, update the telescope_db with the new t12 value

    plot : bool
        If True, save a plot showing the Q/V correlation coefficient as a function of t12

    fit_kwargs : dict
        Any arguments to be passed to lmfit.minimizer.Minimizer.minimize().

    Returns
    -------
    `lmfit.minimizer.MinimizerResult`
        Fit result object for t12 fit

    `TelescopeModel.TelescopeModel`
        Telescope Model with best-fit parameters
    """
    hdus = pyfits.open(map_file)
    wavelength = hdus[0].header[S122['Wavelength']]
    try:
        obstime = Time(hdus[0].header['DATE-OBS'], format='fits')
    except ValueError:
        obstime = Time(hdus[0].header['DATE-OBS'], format='iso')

    print('{}: loaded map file {}'.format(tag(), map_file))

    full_map = np.stack([h.data[::thiny, ::thinx, :] for h in hdus[1:]], -1)
    hdus.close()
    del hdus
    print('{}: extracted map with every ({}, {}) other pixel'.format(tag(), thinx, thiny))

    print('{}: initializing Telescope Model'.format(tag()))
    TM = TelescopeModel.TelescopeModel(0,0,0)
    TM.load_from_database(telescope_db, obstime.mjd, wavelength)

    print('{}: starting t12 fitter'.format(tag()))
    # I love that this if statement works in all cases
    if ('method' not in fit_kwargs.keys() or fit_kwargs['method'] == 'brute') and plot:
        fit_kwargs['keep'] = 'all'
    fit_out = fit_t12(full_map, TM, **fit_kwargs)

    if update_db:
        print('{}: updating {} with new t12 value'.format(tag(), telescope_db))
        TM.save_to_database(telescope_db, obstime.mjd, wavelength)

    if plot:
        print('{}: generating fit plot'.format(tag()))
        plotfile = outpre + '.pdf'
        plot_fit(fit_out, plotfile)

    with open(outpre + '.pkl', 'wb') as f:
        print('{}: saving results to {}'.format(tag(), f.name))
        pickle.dump(fit_out, f)

    return fit_out, TM

def compute_ratio(QUV, I):
    """Compute normalized Stokes parameter.

    See eq. 1 in "DKIST Polarization Calibration: Determination of M12 group parameters", C. Beck Feb. 2018
    """
    return np.nansum(np.abs(QUV) / I, axis=2)

def correlation_coefficient(QU, V):
    """Compute the linear correlation coefficient between two Stokes signals.

    See eq. 2 in "DKIST Polarization Calibration: Determination of M12 group parameters", C. Beck Feb. 2018

    To minimize the impact of noisy data we use medians instead of sums. The logic being that using a mean is
    mathematically equivalent to sum (because it's a ratio) and a median is more robust to outliers than a mean.
    """
    V_term = V - np.median(V)
    QU_term = QU - np.median(QU)

    numerator = np.median(V_term * QU_term)
    denominator = np.sqrt(np.median(V_term**2)) * np.sqrt(np.median(QU_term**2))

    return numerator / denominator

def total_correlation(params, full_maps, TM, t1):
    """The minimization function for fitting t12

    First we update the TelescopeModel, then we recompute the 3D stokes map with M12 removed, and finally compute the
    linear correlation coefficient.

    Currently only the correlation between stokes Q and V is considered.

    Parameters
    ----------
    params : `lmfit.parameter.Parameters`
        The parameters to be fit. Should just be t12

    full_maps : numpy.ndarray
        3D stokes maps

    TM : `TelescopeModel.TelescopeModel`
        Model describing the state of DKIST's mirrors. We only use the .M12 property from this object.

    t1 : float
        Time at which the fit started. Used for status updates.

    Returns
    -------
    float
        The linear correlation coefficient between Q and V
    """
    parvals = params.valuesdict()
    TM.t12 = parvals['t12']

    new_map = np.sum(np.linalg.inv(TM.M12) * full_maps[:, :, :, None, :], axis=4)

    Q = compute_ratio(new_map[:, :, :, 1], new_map[:, :, :, 0])
    U = compute_ratio(new_map[:, :, :, 2], new_map[:, :, :, 0])
    V = compute_ratio(new_map[:, :, :, 3], new_map[:, :, :, 0])

    C_q = correlation_coefficient(Q, V)
    C_u = correlation_coefficient(U, V)
    #C_tot = np.sqrt(C_q**2 + C_u**2)

    print_status(TM, C_u, t1)

    return C_u

def fit_t12(full_maps, TM, method='brute', **fit_kwargs):
    """The main fitting function for t12

    First we initialize the fit parameters and then send them off to lmfit for fitting.

    Parameters
    ----------
    full_maps : numpy.ndarray
        The 3D stokes maps

    TM : `TelescopeModel.TelescopeModel`
        Model describing the state of DKIST's mirrors. We only use the .M12 property from this object.

    method : str
        Fitting method to use. Any method available to `lmfit` is valid, but this should probably be 'brute'

    fit_kwargs : dict
        Any arguments to pass to `lmfit.minimize`

    Returns
    -------
    `lmfit.minimize.MinimizerResult`
        Fit result object for t12 fit
    """
    if method == 'brute' and 'Ns' not in fit_kwargs.keys():
        fit_kwargs['Ns'] = 100

    params = lmfit.Parameters()
    params.add('t12', value=TM.t12, min=145 * np.pi / 180., max=215 * np.pi / 180.)

    print('{}: starting minimizer with method {} and kwargs {}'.format(tag(), method, fit_kwargs))
    print_header()

    t1 = time.time()
    mini = lmfit.Minimizer(total_correlation, params, fcn_args=(full_maps, TM, t1))
    fit_out = mini.minimize(method=method, params=params, **fit_kwargs)

    print('\n{:}: minimization completed. Best t12 value: {:7.4f}'.format(tag(), fit_out.params['t12'].value))

    return fit_out

def print_header():
    """Print the header that defines columns in the fit status message
    """
    header_str = '{:>20}{:>20}{:>20}'.format('t12', 'C', 't_elapsed')

    print(header_str)

def print_status(TM, C_tot, t1):
    """Print current parameter values, the value of the linear correlation coefficient, and the elapsed fit time
    """
    status_str = '{:}{:20.6e}{:20.6e}'.format('\r',TM.t12,C_tot)

    dt = time.time() - t1
    time_unit = ' s'
    if dt > 120:
        dt /= 60
        time_unit = ' m'
    status_str += '{:18.1f}{:}'.format(dt, time_unit)

    print(status_str, end="", flush=True)

def plot_fit(fit_obj, output):
    """Plot the linear correlation coefficient as a function of t12

    This function is only valid if the 'brute' method was used to fit t12.

    Parameters
    ----------
    fit_obj : `lmfit.minimize.MinimizerResult`
        Fit result object for t12 fit

    output : str
        Location to save the plot
    """
    import matplotlib.pyplot as plt

    if fit_obj.method != 'brute':
        print("{}: Fitting method was not 'brute'. Cannot generate plot.".format(tag()))
        return

    a = np.array([[c.params['t12'].value, c.score] for c in fit_obj.candidates]).T

    ax = plt.figure().add_subplot(111)
    ax.set_xlabel(r'$\tau_{12}$')
    ax.set_ylabel(r'$C_{QV}$')

    ax.plot(a[0], a[1], '.', color='k', ms=1)
    bestval = fit_obj.params['t12'].value
    ax.axvline(bestval, ls=':', color='r', lw=0.8)
    ymax = ax.get_ylim()[1]
    ax.text(bestval, ymax, r'$\tau_{12} = $' + '{:5.3f}'.format(bestval),
            horizontalalignment='center', verticalalignment='bottom')

    ax.figure.savefig(output)

    return

def command_line():
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(description="Compute the M12 tau parameter using the baseline method. This method "
                                                 "requires a single file containing 3D Stokes maps of a region with "
                                                 "strong polarization. The dimensions of this file should be "
                                                 "(X, Y, lambda, 4).",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('map_file', help='FITS file containing 3D stokes maps')
    parser.add_argument('outpre', help='Output prefix to save fitting results. Results will live in OUTPRE.pkl')
    parser.add_argument('-t', '--telescope-db', help='Database listing telescope parameters as function of obstime and '
                                                     'wavelength', nargs=1, default=['telescope_db.txt'])
    parser.add_argument('-x', '--thin-x', help='Only load 1 in every thin-x x dimension spatial locations',
                        nargs=1, default=[10], type=int)
    parser.add_argument('-y', '--thin-y', help='Only load in every thin-y y dimension spatial locations',
                        nargs=1, default=[10], type=int)
    parser.add_argument('-u', '--update-db', help='Update the telescope database with the new tau_12 value',
                        action='store_true')
    parser.add_argument('-p', '--plot', help='Generate plot of tau_12 fit. Plot will be saved to OUTPRE.pdf',
                        action='store_true')

    args = parser.parse_args()

    if not os.path.exists(args.map_file):
        print('Could not find map file {}. Aborting'.format(args.map_file))
        sys.exit(1)

    if not os.path.exists(args.telescope_db[0]):
        print('Could not find telescope db {}. Aborting'.format(args.telescope_db[0]))
        sys.exit(1)

    main(args.map_file, args.telescope_db[0], args.outpre,
         update_db=args.update_db, plot=args.plot, thinx=args.thin_x[0], thiny=args.thin_y[0])

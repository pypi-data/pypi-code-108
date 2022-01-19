import corner
import pickle
import time
import re
import os
import numpy as np
from glob import glob
from astropy.io import fits as pyfits
from dkist_processing_pac import FittingFramework, CUModel, Data, TelescopeModel
from dkist_processing_pac.tag import tag
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages as PDF

def main_MCMC(aux_dir, **mckwargs):
    """Read in a directory of PA&C fits and run MCMC analysis to explore the fit parameter space.

    Parameters
    ----------
    aux_dir : str
        Path to a directory containing the "auxiliary" fitting information. This is usually generated automatically by
        `pac_demod` or `pac_tele`.

    outpre : str
        Prefix to use when saving the results of MCMC analysis

    mckwargs : dict
        A dictionary of options to pass to the MCMC algorithm.

    Returns
    -------
    None
    """
    pickle_list = glob('{}/fitobj*.pkl'.format(aux_dir))
    print('{}: found fits for {} detector positions'.format(tag(), len(pickle_list)))

    for p in pickle_list:
        xpos, ypos, lpos = re.search('_(\d{4})(\d{4})(\d{4})\.pkl', p).groups()
        print('{}: analyzing position ({}, {}, {}) from {}'.format(tag(), int(xpos), int(ypos), int(lpos), p))
        analyze_pickle(p, '{}/mcmcsav_{}{}{}'.format(aux_dir, xpos, ypos, lpos), **mckwargs)

    return

def analyze_pickle(pickle_file, outpre, plot_burn=0, **mckwargs):
    """Run MCMC analysis on a single PA&C fit object

    An MCMC algorithm is first used to explore the parameter space of all free variables found in the fit object.
    Corner and Trace plots are then produced to aid the user in interpreting the MCMC results.

    Parameters
    ----------
    pickle_file : str
        Path to the pickel (*.pkl) file containing `lmfit` fit objects. This is probably generated automatically by
        `pac_demod` or `pac_tele`.

    outpre : str
        Prefix to use when saving MCMC results.

    plot_burn : int
        Number of MCMC samples to burn ONLY WHEN PLOTTING. This is useful if no samples were burned during the actual
        MCMC run and you want to test different burn amounts when analyzing the results.

    mckwargs : dict
        Additional arguments to pass to the MCMC algorithm.

    Returns
    -------
    lmfit.Minimizer
        The original fitting object from the base PA&C fits

    lmfit.MinimizerResult
        The original fit result object from the vase PA&C fits

    lmfit.MinimizerResult
        The result object that contains the results of the MCMC run

    """
    with open(pickle_file, 'rb') as f:
        fitter = pickle.load(f)
        mini_res = pickle.load(f)

    expand_param_range(mini_res, factor=100)
    print('{}:  starting MCMC analysis with keywords {}'.format(tag(), mckwargs))
    mcmc_res = run_MCMC(fitter, mini_res, **mckwargs)

    print('{}:  plotting results'.format(tag()))
    plot_MCMC(mcmc_res, mini_res, outpre, plot_burn=plot_burn)

    pkl_save_name = outpre + '.pkl'
    print('{}:  saving results to {}'.format(tag(), pkl_save_name))
    with open(pkl_save_name, 'wb') as f:
        pickle.dump(fitter, f)
        pickle.dump(mini_res, f)
        pickle.dump(mcmc_res, f)

    return fitter, mini_res, mcmc_res

def run_MCMC(fitter, minimize_results, burn=0, steps=100, nwalkers=256, **mckwargs):
    """Initialize and run MCMC analysis on fit PA&C fit object

    The `emcee` package is used to perform the MCMC analysis

    Parameters
    ----------
    fitter : lmfit.Minimizer
        Fit object of the original PA&C parameter fits

    minimize_results : lmfit.MinimizerResult
        Fitting results of the original PA&C parameter fits

    burn : int
        The number of MCMC steps to discard from the beginning of the Markov Chain. This is used to allow the walkers
        to settle into a suitably stochastic state.

    steps : int
        The number of steps for each MCMC walker to take

    nwalkers : int
        The number of MCMC walkers to use

    mckwargs : dict
        Any additional parameters to pass to `emcee`

    Returns
    -------
    lmfit.MinimizerResult
        Fit result object containing the results of MCMC analysis. Most usefully, the MCMC chain.

    """
    FittingFramework.print_header(minimize_results.params)
    t1 = time.time()
    fitter.userargs = (*fitter.userargs[:-1], t1)
    mcmc_results = fitter.emcee(burn=burn, steps=steps, nwalkers=nwalkers, params=minimize_results.params, **mckwargs)
    print('\n{}: completed in {:4.3f} s'.format(tag(), time.time() - t1))

    return mcmc_results

def expand_param_range(fit_results, params='all', factor=30):
    """Expand the original PA&C fit parameter ranges to allow for a broader search by the MCMC walkers

    This is a very good idea to do because if the MCMC walkers are prevented from exploring the entire distribution of
    each parameter then the resulting conclusions about credibility regions will be invalid

    Parameters
    ----------
    fit_results : lmfit.MinimizerResult
        Fitting results of the original PA&C parameter fits

    params : str or list
        The name or list of names of parameters to expand. The given parameters must exist in fit_results.var_names.
        If set to 'all' then all free parameters that are found will be expanded.

    factor : float
        The percentage by which to expand the parameters. The minimum and maximum will be shifted by factor% of their
        original values.
    """
    if params == 'all':
        params = fit_results.var_names
    elif type(params) is not list:
        params = [params]

    for p in params:
        fit_results.params[p].min *= 1 - factor / 100 * np.sign(fit_results.params[p].min)
        fit_results.params[p].max *= 1 + factor / 100 * np.sign(fit_results.params[p].max)

def plot_MCMC(mcres, minimize_results, outpre, plot_burn=0):
    """Plot corner and trace plots for an MCMC run and save them to disk.

    The plots also report the credibility region for each parameter and show the compare the mean and median of the MCMC
    samples to the original fit value.

    Parameters
    ----------
    mcres : lmfit.MinimizerResults
        Results from an lmfit MCMC run

    minimize_results : lmfit.MinimizerResults
        Results from original PA&C parameter fitting

    outpre : str
        Prefix for output files. The files are OUTPRE_corner.pdf and OUTPRE_traces.pdf

    plot_burn : int
        The number of MCMC samples to exclude at the start of the chain

    Returns
    -------
    numpy.ndarray
        The best-fit parameter values from the original PA&C fit

    numpy.ndarray
        The median parameter values from the MCMC run
    """
    labels = texify_labels(mcres)

    minimizer_truths = np.array([minimize_results.params.valuesdict()[p] for p in minimize_results.var_names])
    mc_meds = np.median(mcres.flatchain, axis=0)
    mc_means = np.mean(mcres.flatchain, axis=0)
    if '__lnsigma' in mcres.var_names:
        minimizer_truths = np.append(minimizer_truths, mc_meds[-1])
    flatchain = mcres.chain[:, plot_burn:, :].reshape(-1, mcres.chain.shape[-1])
    cfig = corner.corner(flatchain, labels=labels,
                         show_titles=True, title_kwargs={'fontsize': 12})

    truth_colors = ['#1b9e77','#d95f02','#7570b3']
    numvars = mcres.chain.shape[-1]
    axes = np.array(cfig.axes).reshape((numvars, numvars))
    for i in range(numvars):
        ax = axes[i, i]
        ax.axvline(minimizer_truths[i], color=truth_colors[0])
        ax.axvline(mc_meds[i], color=truth_colors[1])
        ax.axvline(mc_means[i], color=truth_colors[2])

    for yi in range(numvars):
        for xi in range(yi):
            ax = axes[yi, xi]
            ax.axvline(minimizer_truths[xi], color=truth_colors[0])
            ax.axvline(mc_meds[xi], color=truth_colors[1])
            ax.axvline(mc_means[xi], color=truth_colors[2])
            ax.axhline(minimizer_truths[yi], color=truth_colors[0])
            ax.axhline(mc_meds[yi], color=truth_colors[1])
            ax.axhline(mc_means[yi], color=truth_colors[2])
            ax.plot(minimizer_truths[xi], minimizer_truths[yi], 's', color=truth_colors[0])
            ax.plot(mc_meds[xi], mc_meds[yi], 's', color=truth_colors[1])
            ax.plot(mc_means[xi], mc_means[yi], 's', color=truth_colors[2])

    axes[0, 1].text(0,0.2, 'minimzer value', color=truth_colors[0], transform=axes[0, 1].transAxes, fontsize=14)
    axes[0, 1].text(0,0.3, 'MCMC median', color=truth_colors[1], transform=axes[0, 1].transAxes, fontsize=14)
    axes[0, 1].text(0,0.4, 'MCMC mean', color=truth_colors[2], transform=axes[0, 1].transAxes, fontsize=14)

    cfig.savefig(outpre + '_corner.pdf')

    pp = PDF(outpre + '_traces.pdf')
    for i in range(numvars):
        if i % 3 == 0:
            fig = plt.figure()
        ax = fig.add_subplot(3,1,(i % 3) + 1)
        for j in range(mcres.chain.shape[0]):
            ax.plot(mcres.chain[j,plot_burn:,i], color='k', alpha=0.2, lw=0.6)
        ax.set_ylabel(labels[i])
        ax.axhline(minimizer_truths[i], color=truth_colors[0], ls='-', lw=0.6)
        ax.axhline(mc_meds[i], color=truth_colors[1], ls='-', lw=0.6)
        ax.axhline(mc_means[i], color=truth_colors[2], ls='-', lw=0.6)
        if i % 3 == 2:
            fig.subplots_adjust(hspace=0.0001)
            pp.savefig(fig)

    # If we ended on a non-full page we need to save it to the PDF
    if i % 3 != 2:
        fig.subplots_adjust(hspace=0.0001)
        pp.savefig(fig)

    pp.close()
    plt.close('all')

    return minimizer_truths, mc_meds


def texify_labels(mcres):
    """Convert the variable names used by lmfit to nice-looking latex labels for plotting

    Only parameters that were varried during the fit are converted.

    This function uses regular expressions for no reason at all and is perhaps too complicated.

    Parameters
    ----------
    mcres : lmfit.MinimzerResults
        Results from an lmfit fitting run

    Returns
    -------
    list
        List containing latex-style variable names
    """

    labels = []
    for l in mcres.var_names:
        if l == '__lnsigma':
            labels.append(r'$\mathrm{ln}\sigma$')
            continue
        try:
            tmp = re.sub('^ret0(.*)_', r'\\delta_{0,\1}_', l)
            tmp = re.sub('^dret(.*)_', r'\\Delta\\delta_{\1}_', tmp)
            tmp = re.sub('^theta(.*)_', r'\\theta_{\1}_', tmp)
            tmp = re.sub(r'_CS(\d\d)', r'^{\1}', tmp)
            tmp = re.sub(r'_(\w+)', r'_{\1}', tmp)
            tmp = re.sub(r'\^{0(\d)}', r'^{\1}', tmp)
            tmp = re.sub(r'^t(\d\d)', r'\\tau_{\1}', tmp)
            tmp = re.sub(r'^x(\d\d)', r'X_{\1}', tmp)
            tmp = r'$' + tmp + r'$'
        except:
            labels.append(l)

        labels.append(tmp)

    return labels

def main_demod_err(data_dir, demod_file, output, suffix='*.FITS', telescope_db='telescope_db.txt', overwrite=True,
                   skip_darks=True, plot=True):
    """Create uncertainty estimates for a given demodulation matrix using the results of MCMC analysis.

    The result is the uncertainty analog of the output of `pac_demod` along with some optional diagnostic plots. Just
    like the main demodulation matrices, the uncertainty estimates will be contained in the 1st ImageHDU of a FITS file
    in an array of shape (X, Y, 4, M), even if X = Y = 1.

    Parameters
    ----------
    data_dir : str
        Path to directory containing data related to a single Calibration Sequence

    demod_file : str
        Path to the demodulation file produced by running `pac_demod` on the data in data_dir

    output : str
        Path to output file

    suffix : str
        File suffix to use when loading the Calibration Sequence data from data_dir. The file mask is DATA_DIR/*SUFFIX

    telescope_db : str
        Path to database of telescope parameters as a function of time and wavelength

    overwrite : bool
        If True then output will be overwritten if it exists

    plot : bool
        If True then a plots showing the distribution of values for each entry of the demodulation matrix will be
         created. Each of the (X, Y) positions gets its own plot and they are all saved to OUTPUT.pdf

    skip_darks : bool
        If True (default) then don't include and dark steps of the CS in fitting

    Returns
    -------

    """
    dirname = os.path.dirname(demod_file) or '.'
    pickle_path = '{}/fitaux'.format(dirname)

    try:
        tmpkl = glob('{}/mcmcsav*.pkl'.format(pickle_path))[0]
    except IndexError:
        raise FileNotFoundError('Cannot find any MCMC results in {}'.format(dirname))

    with open(tmpkl, 'rb') as f:
        fitter = pickle.load(f)
    linear = 'b_CS00' in fitter.params.keys()

    PCD = Data.Drawer(data_dir, suffix, skip_darks=skip_darks)
    TM = TelescopeModel.TelescopeModel(PCD.azimuth, PCD.elevation, PCD.table_angle)
    if linear:
        from dkist_processing_pac.linear_retarder import CULinearRetarderModel
        CS = CULinearRetarderModel.CalibrationSequence(PCD.theta_pol_steps, PCD.theta_ret_steps,
                                                       PCD.pol_in, PCD.ret_in, PCD.timeobs)
    else:
        CS = CUModel.CalibrationSequence(PCD.theta_pol_steps, PCD.theta_ret_steps, PCD.pol_in, PCD.ret_in,
                                         PCD.dark_in, PCD.timeobs)
    print('{}: loaded polcal data from {}'.format(tag(), data_dir))

    print('{}: updating polarizer py value'.format(tag()))
    wave = PCD.wavelength
    CS.set_py_from_database(wave)

    print('{}: loading telescope database from {}'.format(tag(), telescope_db))
    mean_time = 0.5 * (PCD.date_bgn + PCD.date_end)
    TM.load_from_database(telescope_db, mean_time, wave)

    numx, numy, numl = PCD.shape
    demod_err = np.zeros((numx, numy, numl, 4, PCD.nummod), dtype=np.float32)

    pickle_list = glob('{}/mcmcsav*.pkl'.format(pickle_path))
    print('{}: found fits for {} detector positions'.format(tag(), len(pickle_list)))

    if plot:
        plot_prefix = '.'.join(output.split('.')[:-1]) or output
        plotfile = '{}.pdf'.format(plot_prefix)
        pp = PDF(plotfile)

    for i in range(numx):
        for j in range(numy):
            for l in range(numl):
                print('{}: computing err for position ({}, {}, {})'.format(tag(), i, j, l))

                I = PCD[i, j, l]
                pickle_file = '{}/mcmcsav_{:04}{:04}{:04}.pkl'.format(pickle_path, i, j, l)
                if not os.path.exists(pickle_file):
                    raise FileNotFoundError('Cannot find MCMC results {} for position ({}, {})'.format(pickle_file, i, j))

                if linear:
                    demod_stack = get_linear_demod_stack(pickle_file, I, TM, CS)
                else:
                    demod_stack = get_demod_stack(pickle_file, I, TM, CS)

                if plot:
                    fig = plot_demod_err(demod_stack)
                    fig.suptitle('Position ({}, {}) from {}'.format(i, j, pickle_file))
                    pp.savefig(fig)
                    plt.close(fig)

                demod_err[i, j, l] = np.std(demod_stack, axis=0)

    demod_hdus = pyfits.open(demod_file)
    primary = pyfits.PrimaryHDU(header=demod_hdus[0].header)
    primary.header['OBJECT'] = 'Demodulation matrix uncertainty'

    demod_hdu = pyfits.ImageHDU(demod_err, header=demod_hdus[1].header)
    demod_hdu.header['OBJECT'] = 'Demodulation matrix uncertainty'
    pyfits.HDUList([primary, demod_hdu]).writeto(output, overwrite=overwrite)

    if plot:
        print('{}: saving plots to {}'.format(tag(), plotfile))
        pp.close()

    return demod_err, demod_stack

#TODO: Update this to be more flexible with fit parameters
def get_demod_stack(pickle_file, I, TM, CS, numload=None):
    """Compute a demodulation matrix for every MCMC step represented in a MCMC results file.

    Demodulation matrices are computed with `FitModels.fit_modulation_matrix`.

    Parameters
    ----------
    pickle_file : str
        Location of MCMC results pickle file

    I : numpy.ndarray
        Array of shape (M, N) containing the observed intensity values where M is the number of modulation states and
        N is the number of CS steps

    TM : TelescopeModel.TelescopeModel
        An object describing the telescope configuration at each step in the CS

    CS : CUModel.CalibrationSequence
        An object describing the CU configuration at each step in the CS

    numload : int
        The maximum number of MCMC steps to load. Useful for debuggin.

    Returns
    -------
    numpy.ndarray
        Array of shape (Z, 4, M) where Z is the min(numload, number of MCMC steps). Each of the Z arrays is a single
        demodulation matrix.
    """
    with open(pickle_file, 'rb') as f:
        fitter = pickle.load(f)
        results = pickle.load(f)
        mcres = pickle.load(f)
    flatchain = mcres.flatchain
    numsteps = flatchain.shape[0]
    print('{}: loaded MCMC results from {}'.format(tag(), pickle_file))

    demod_list = []
    for k in range(numsteps)[:numload]:
        print('\r{}: reading MCMC steps: {}/{} ({}%)'.format(tag(), k + 1, numsteps,
                                                             int((k + 1) / numsteps * 100)), end='', flush=True)
        CS.ret_0_h[0] = flatchain['ret0h_CS00'][k]
        CS.dret_h[0] = flatchain['dreth_CS00'][k]
        CS.ret_0_45[0] = flatchain['ret045_CS00'][k]
        CS.dret_45[0] = flatchain['dret45_CS00'][k]
        CS.ret_0_r[0] = flatchain['ret0r_CS00'][k]
        CS.dret_r[0] = flatchain['dretr_CS00'][k]

        S = (TM.TM @ CS.CM @ TM.M12 @ CS.s_in).T

        O = FittingFramework.fit_modulation_matrix(I, S)
        demod_list.append(np.linalg.pinv(O))

    print('')
    demod_stack = np.stack(demod_list, 0)

    return demod_stack

def get_linear_demod_stack(pickle_file, I, TM, CS, numload=None):
    """Compute a demodulation matrix for every MCMC step represented in a MCMC results file.

    This function expects the fits to been done with a CU linear retarder model.

    Demodulation matrices are computed with `FitModels.fit_modulation_matrix`.

    Parameters
    ----------
    pickle_file : str
        Location of MCMC results pickle file

    I : numpy.ndarray
        Array of shape (M, N) containing the observed intensity values where M is the number of modulation states and
        N is the number of CS steps

    TM : TelescopeModel.TelescopeModel
        An object describing the telescope configuration at each step in the CS

    CS : CULinearRetarderModel.CalibrationSequence
        An object describing the CU configuration at each step in the CS

    numload : int
        The maximum number of MCMC steps to load. Useful for debuggin.

    Returns
    -------
    numpy.ndarray
        Array of shape (Z, 4, M) where Z is the min(numload, number of MCMC steps). Each of the Z arrays is a single
        demodulation matrix.
    """
    with open(pickle_file, 'rb') as f:
        fitter = pickle.load(f)
        results = pickle.load(f)
        mcres = pickle.load(f)
    flatchain = mcres.flatchain
    numsteps = flatchain.shape[0]
    print('{}: loaded MCMC results from {}'.format(tag(), pickle_file))

    demod_list = []
    for k in range(numsteps)[:numload]:
        print('\r{}: reading MCMC steps: {}/{} ({}%)'.format(tag(), k + 1, numsteps,
                                                             int((k + 1) / numsteps * 100)), end='', flush=True)
        CS.ret_0[0] = flatchain['ret0_CS00'][k]
        CS.dret[0] = flatchain['dret_CS00'][k]
        CS.theta_off[0] = flatchain['theta_off_CS00'][k]
        try:
            CS.diatten[0] = flatchain['b_CS00'][k]
        except KeyError:
            pass

        S = (TM.TM @ CS.CM @ TM.M12 @ CS.s_in).T

        O = FittingFramework.fit_modulation_matrix(I, S)
        demod_list.append(np.linalg.pinv(O))

    print('')
    demod_stack = np.stack(demod_list, 0)

    return demod_stack

def plot_demod_err(demod_stack, output=None):
    """Make a plot showing the distributions of values for each entry in a demodulation matrix

    The stddev and stddev/mean will be printed in each cell

    Parameters
    ----------
    demod_stack : numpy.ndarray
        Array of shape (Z, 4, M) where Z is the min(numload, number of MCMC steps). Each of the Z arrays is a single
        demodulation matrix. Probably the output of `get_demod_stack`.

    output : str
        If True then save the generated plot to the specified file.

    Returns
    -------
    matplotlib.figure.Figure
        Figure object containing the grid of plots that represents the distribution of the demodulation matrix
    """
    print('{}: generating demodulation uncertainty plot'.format(tag()))

    nummod = demod_stack.shape[2]

    std = np.std(demod_stack, axis=0)
    mean = np.mean(demod_stack, axis=0)

    fig = plt.figure(figsize=(16,22))
    axes = fig.subplots(nummod,4,gridspec_kw={'wspace': 0.02,
                                              'left': 0.05, 'right': 0.95, 'bottom': 0.03, 'top':0.95})

    lims = []
    for i in range(nummod):
        for j in range(4):
            ax = axes[i, j]
            ax.hist(demod_stack[:,j,i], histtype='stepfilled')
            ax.set_yticks([])
            ax.text(0.98, 0.9, r'$\sigma_D = {:5.2e}$'.format(std[j, i]), transform=ax.transAxes,
                    horizontalalignment='right')
            ax.text(0.98, 0.8, r'$\frac{{\sigma_D}}{{\left<D\right>}} = {:5.2e}$'.format(std[j, i]/mean[j, i]),
                    transform=ax.transAxes, horizontalalignment='right')
            lims.append(ax.get_xlim())

    half_width = 0.5 * np.max(np.diff(np.array(lims), axis=1))
    for ax in fig.axes:
        mid = np.mean(ax.get_xlim())
        ax.set_xlim(mid - half_width, mid + half_width)

    fig.subplots_adjust(wspace=0.01)

    if output is not None:
        fig.savefig(output)

    return fig

def command_line_MCMC():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Compute PA&C fit uncertainties using Markov-Chain Monte Carlo (MCMC) '
                                                 'analysis. This program operates on the auxiliary output of '
                                                 '"pac_demod" or "pac_tele", which is generated with the "-S" option.')
    parser.add_argument('aux_dir', help='Directory containing auxiliary fit information')
    parser.add_argument('-b', '--burn', nargs=1, default=[0], type=int, help='Number of MCMC steps to burn')
    parser.add_argument('-N', '--num-steps', nargs=1, default=[100], type=int,
                        help='Number of MCMC steps for each walker to take')
    parser.add_argument('-w', '--num-walkers', nargs=1, default=[256], type=int, help='Number of MCMC walkers to use')
    args = parser.parse_args()

    if os.path.exists(args.aux_dir):
        sys.exit(main_MCMC(args.aux_dir, burn=args.burn[0], nwalkers=args.num_walkers[0], steps=args.num_steps[0]))
    else:
        print('Directory {} does not exist. Aborting.'.format(args.aux))
        sys.exit(1)

def command_line_demod_err():
    import argparse
    import sys
    from dkist_processing_pac import generic

    parser = argparse.ArgumentParser(description='Generate demodulation matrix uncertainties using the results of '
                                                 'Markov-Chain Monte Carlo (MCMC) analysis of CU parameter fits. This '
                                                 'program operates on the output of "pac_mcmc".')
    parser.add_argument('data_dir', help='Directory containing a single Calibration Sequence. This is the same '
                                         'directory that was the input to "pac_demod".')
    parser.add_argument('demod_file', help='The Demodulation matrix file generated by "pac_demod"')
    parser.add_argument('output', help='Location of FITS file to save uncertainty on Demodulation matrices')
    parser.add_argument('-s', '--suffix', help='File suffix to filter data. File mask is data_dir/*suffix',
                        default='.FITS')
    parser.add_argument('-t', '--telescope-db', help='Location of database containing telescope parameters as a '
                                                     'function of date and wavelength', nargs=1, default=[])
    parser.add_argument('-p', '--plot', action='store_true', help='Generate plots showing the value distribution of '
                                                                  'each entry in the Demodulation matrices')
    parser.add_argument('-D', '--use-darks', action='store_false', help='Include any DARK CS steps in the fit')
    args = parser.parse_args()

    if not args.telescope_db:
        telescope_db = generic.get_default_telescope_db()
    else:
        telescope_db = args.telescope_db[0]

    if not os.path.exists(args.data_dir):
        print('Directory {} does not exist. Aborting.'.format(args.data_dir))
        sys.exit(1)

    if not os.path.exists(args.demod_file):
        print('Demodulation matrices file {} does not exist. Aborting.'.format(args.demod_file))
        sys.exit(1)

    main_demod_err(args.data_dir, args.demod_file, args.output, suffix=args.suffix,
                   telescope_db=telescope_db, plot=args.plot, skip_darks=args.use_darks)


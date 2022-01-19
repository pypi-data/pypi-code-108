import os
import copy
import multiprocessing as mp
import pickle
import time
import numpy as np
import lmfit
from queue import Empty as QueueEmptyError
from dkist_processing_pac import TelescopeModel, CUModel, Data, generic
from dkist_processing_pac.tag import tag, is_mp
from dkist_processing_pac.data import CONSTANTS
from dkist_processing_pac.data.required_params import elliptical

try:
    TERMCOL = int(os.popen('stty size', 'r').read().split()[1])
except:
    TERMCOL = 80

def run_fits(dirlist, suffix='.FITS', skip_darks=True, **kwargs):
    DRSR = Data.Dresser()

    for drwr_loc in dirlist:
        # fitaux is a special directory that can be generated automatically for saving fit statistics
        #  the [-6:] is a poor-man's regex; ensure that fitaux is at the end of the dirname. We don't want to stop
        #  someone from using fitaux_is_my_dir_for_some_reason as a location to save fit results
        if drwr_loc[-6:] == 'fitaux':
            continue
        tmp_drawer = Data.Drawer(drwr_loc, suffix, skip_darks=skip_darks)
        DRSR.add_drawer(tmp_drawer)

        print('{}: loaded polcal data from {}'.format(tag(), drwr_loc))

    return run_core(DRSR, **kwargs)

def run_core(dresser, telescope_db='telescope_db.txt', fit_mode='baseline', init_set='default',
             fit_TM=True, method='leastsq', pickle_path=None, threads=1, super_name='',
             **fit_kwargs):
    """Top-level function to ingest data and setup fitting of Telescope and CU parameters.

    First read all PolCal data from files, then create corresponding CU and Telescope objects, and, finally, kick off
    the fit.

    Data are expected to live in a nested directory structure where each sub-directory contains data from a single
    Calibration Sequence. Any number of CS's are allowed, and a subset of the sub-directories can be selected via the
    numCS parameter.

    Information related to the time and CU and Telescope states are read directly from the FITS headers of the data.
    The Telescope Model mirror parameters are pulled from the provided database, but the CU model is initialized with
    no assumptions.

    Parameters
    ----------
    dirlist : list
       List of directories from which to load Drawer data. Each directory should contain a single Drawer.

    suffix : str
        Filter to select specific files. File mask is top_level_dir/sub_dir/*suffix

    telescope_db : str
        Path to the database of Telescope Model mirror parameters. See TelescopeModel.TelescopeModel.load_from_database
        for more information.

    fit_mode : str
        The PA&C fit recipe to use for fitting

    fit_TM : bool
        If True then vary the M36 mirror parameters during the fit

    skip_darks : bool
        If True (default) then don't include and dark steps of the CS in fitting

    pickle_path : str
        Location of directory within which to save fitting statistics for later analysis

    method : str
        Fitting method to use. Valid values are:
        - `'differential_evolution'`: differential evolution (default)
        - `'leastsq'`: Levenberg-Marquardt
        - `'least_squares'`: Least-Squares minimization, using Trust Region Reflective method by default
        - `'brute'`: brute force method
        - '`nelder`': Nelder-Mead
        - `'lbfgsb'`: L-BFGS-B
        - `'powell'`: Powell
        - `'cg'`: Conjugate-Gradient
        - `'newton'`: Newton-Congugate-Gradient
        - `'cobyla'`: Cobyla
        - `'tnc'`: Truncate Newton
        - `'trust-ncg'`: Trust Newton-Congugate-Gradient
        - `'dogleg'`: Dogleg
        - `'slsqp'`: Sequential Linear Squares Programming

        For more details on the fitting methods please refer to the
        `SciPy docs <http://docs.scipy.org/doc/scipy/reference/optimize.html>`__.

    fit_kwargs : dict
        Options to be passed to the minimizer being used

    Returns
    -------
    `Data.CUModelParams`
        Object containing the best fit CU parameters

    `Data.TMModelParams`
        Object containing the best fit TM parameters

    `TelescopModel.TelescopeModel`
        Best fit Telescope Model

    Notes
    -----
    The shape of the input data controls how much spatial information is extracted from the fits; a separate fit is
    performed for each pixel in the input data. In many cases the input shape will be (1, 1), in which case no spatial
    information is extracted. The other extreme is to do no pre-binning of the data and fit a different set of
    parameters (and modulation matrices) for every single pixel of the instrument detector, although this will probably
    take a very long time.
    """

    mode_opts = generic.init_fit_mode(fit_mode, dresser.wavelength, fit_TM, init_set=init_set)
    generic.verify_fit_mode(mode_opts, fit_TM)
    use_T = mode_opts['switches']['use_T']
    use_M12 = mode_opts['switches']['use_M12']
    global_transmission = mode_opts['switches']['global_transmission']
    global_retardance = mode_opts['switches']['global_retardance']

    # We need to initialize a dummy CU model
    dummy = np.zeros(1)
    CS = CUModel.CalibrationSequence(*([dummy] * 6))
    CS.init_with_dresser(dresser)  # And now actually fill it with the correct configurations

    TM = TelescopeModel.TelescopeModel(dresser.azimuth, dresser.elevation, dresser.table_angle)

    print('{}: updating polarizer py value'.format(tag()))
    wave = dresser.wavelength
    CS.set_py_from_database(wave)

    print('{}: loading telescope database from {}'.format(tag(), telescope_db))
    mean_time = 0.5 * (dresser.date_bgn + dresser.date_end)
    TM.load_from_database(telescope_db, mean_time, wave)

    numx, numy, numl = dresser.shape
    if fit_TM:
        print('{}: shape of Dresser data: ({}, {}, {})'.format(tag(), numx, numy, numl))
    else:
        print('{}: shape of Drawer data: ({}, {}, {})'.format(tag(), numx, numy, numl))
    print('{}: number of modulator states: {}'.format(tag(), dresser.nummod))
    print('{}: number of CS steps: {}'.format(tag(), dresser.numsteps))

    print('{}: fitting CU parameters'.format(tag()))
    CU_params = Data.CUModelParams(numx, numy, numl, dresser.numdrawers, dresser.nummod,
                                   fit_mode=fit_mode, init_set=init_set,
                                   header=dresser.drawers[0].data_list[0][0].header)
    TM_params = Data.TelescopeModelParams(numx, numy, numl, header=dresser.drawers[0].data_list[0][0].header)

    if threads > 1:
        print('{}: starting fits with {} threads'.format(tag(), threads))
        o = multiproc_drawer_fit(dresser, TM, CS, mode_opts, CU_params, TM_params, numx, numy, numl, int(threads), pickle_path,
                                 method=method, fit_TM=fit_TM, use_T=use_T, use_M12=use_M12, super_name=super_name,
                                 global_transmission=global_transmission, global_retardance=global_retardance,
                                 **fit_kwargs)
    else:
        o = singleproc_drawer_fit(dresser, TM, CS, mode_opts, CU_params, TM_params, numx, numy, numl, pickle_path,
                                  method=method, fit_TM=fit_TM, use_T=use_T, use_M12=use_M12,
                                  global_transmission=global_transmission, global_retardance=global_retardance,
                                  **fit_kwargs)

    return CU_params, TM_params, o[-1]

def singleproc_drawer_fit(Dresser, TM, CS, mode_opts, CU_params, TM_params, numx, numy, numl, pickle_path, fit_TM=False,
                          **kwargs):

    t1 = time.time()
    I_clear = Dresser.I_clear
    for i in range(numx):
        for j in range(numy):
            for k in range(numl):
                if fit_TM:
                    print('{}:  using StoCCinG at position = ({}, {}, {})'.format(tag(), i, j, k))
                else:
                    print('{}:  using SoCC at position = ({}, {}, {})'.format(tag(), i, j, k))
                I_cal, I_unc = Dresser[i, j, k]
                try:
                    TMf, CSf, minimizer, fit_out = fit_parameters(I_cal, I_unc, I_clear, copy.deepcopy(TM),
                                                                  copy.deepcopy(CS), mode_opts, fit_TM=fit_TM, **kwargs)
                except ValueError as e:
                    if 'NaN values detected' in str(e):
                        print('{}: NaN values detected either in input or fitting calculations. Assigning garbage results.'.format(tag()))
                        fit_out = None
                        TMf = None
                        minimizer = None
                    else:
                        raise

                CU_params[i, j, k] = fit_out
                TM_params[i, j, k] = TMf

                if pickle_path is not None:
                    pickle_name = '{}/fitobj_{:04n}{:04n}{:04n}.pkl'.format(pickle_path, i, j, k)
                    print('{}: saving auxiliary fitting data to {}'.format(tag(), pickle_name))
                    with open(pickle_name, 'wb') as f:
                        pickle.dump(minimizer, f)
                        pickle.dump(fit_out, f)

    print('{}: all fits took {:.1f} s'.format(tag(), time.time() - t1))

    return CU_params, TM_params, TMf

def multiproc_drawer_fit(Dresser, TM, CS, mode_opts, CU_params, TM_params, numx, numy, numl, numthread, pickle_path,
                         super_name='', **kwargs):

    # How many fits will be run on each thread?
    num_points = numx * numy * numl
    fits_per_thread = int(num_points / numthread)
    if num_points / numthread % 1 > 0:
        fits_per_thread += 1

    # These loops set up a list of mp processes. They have not been started.
    jobs = []
    lock = mp.Lock()
    queue = mp.Queue()
    thread_pos_inputs = [[] for _ in range(numthread)]
    f = 0
    print('{}: constructing jobs'.format(tag()))
    while f < num_points:
        for k in range(numthread):
            pos = np.unravel_index(f, (numx, numy, numl))
            thread_pos_inputs[k].append(pos)
            f += 1
            if f >= num_points:
                break

    print('{}: {} threads will be started with <= {} fits per thread'.format(tag(), numthread, fits_per_thread))
    if super_name:
        name_pre = '{}: '.format(super_name)
    else:
        name_pre = ''
    for k in range(numthread):
        print('{}: thread {} will fit positions {}'.format(tag(), k, thread_pos_inputs[k]))
        args = [Dresser, copy.deepcopy(TM), copy.deepcopy(CS), mode_opts, thread_pos_inputs[k],
                pickle_path, lock, queue]
        jobs.append(mp.Process(target=do_SoCC_fit,
                               args=args,
                               kwargs=kwargs,
                               name='{}Thread {} X'.format(name_pre, k)))

    # Now start the jobs
    t1 = time.time()
    for p in jobs:
        p.start()

    # And now we loop until all outputs have been captured
    num_completed = 0
    num_timeouts = 0
    status_str = '{:}: FIT STATUS: {:} of {:} points fit in {:.1f} s. There are {:} threads still active and the Queue contains {:} result(s)'
    try:
        while num_completed < num_points:
            print(status_str.format(tag(), num_completed, num_points, time.time() - t1,
                                    [x.is_alive() for x in jobs].count(True), queue.qsize()))
            try:
                # queue.get() blocks until there is something in the queue
                ii, jj, kk, fo, TMf = queue.get(timeout=CONSTANTS['multiproc_queue_timeout'])
            except QueueEmptyError:
                # For reasons that I can't figure out sometimes the queue hangs. Thus the timeout. Here we catch the
                # resulting error and simply print a message. The loop will repeat and usually just calling queue.get() again
                # will kick the queue out of whatever funk it was in.
                print('{:}: FIT STATUS: Queue timeout ({:}s) reached'.format(tag(), CONSTANTS['multiproc_queue_timeout']))
                num_timeouts += 1
                if num_timeouts >= CONSTANTS['multiproc_max_timeouts']:
                    print('{}: FIT STATUS: Max timeouts ({}) reached. Breaking out of fit loop, '
                          'this may cause some errors.'.format(tag(), CONSTANTS['multiproc_max_timeouts']))
                    for p in jobs:
                        p.terminate()
                    break
            else:
                CU_params[ii, jj, kk] = fo
                TM_params[ii, jj, kk] = TMf
                num_completed += 1

            time.sleep(0.05)  # This is possibly unnecessary due to the block of queue.get(), but it's left here
                              #  because a) setting the *_params requires file IO, and b) just to be paranoid.
                              #  That said, the synchronus nature of this loop (caused by .get() blocking) means
                              #  this wait can probably safely be removed.
    except KeyboardInterrupt:
        print("{}: FIT STATUS: KEYBOARD INTERRUPT! There are {} threads still active and the Queue contains {} "
              "result(s). You're going to see a lot of errors".format(tag(),
                                                                      [x.is_alive() for x in jobs].count(True),
                                                                      queue.qsize()))
        print('{}: FIT STATUS: Only {} of {} fits completed. '
              'Now attempting to join the remaining threads.'.format(tag(), num_completed, num_points))

    print('{}: done with loop in {:.1f} s'.format(tag(), time.time() - t1))
    print('{}: There are still {} active threads and the queue has {} objects in it'.format(tag(), [x.is_alive() for x in jobs].count(True),
                                                                                            queue.qsize()))
    # Next, make sure we wait for all jobs to complete before moving on. Because of how we constructed the previous
    #  while loop, this might not matter at all.
    try:
        for p in jobs:
            p.join()
    except KeyboardInterrupt:
        print('{}: FIT STATUS: KEYBOARD INTERRUPT! Join() was stopped. Goodbye and good luck.'.format(tag()))

    # Finally, we'll cleanup the Queue. This is not only good practice, but also an attempt to address some reports
    #  from the field that resources are not released and can eventually clog a system if the user is calling run_fits()
    #  many/multiple times in the same python session.
    print('{}: Cleaning up mp Queue'.format(tag()))
    try:
        queue.close()
        queue.join_thread()
    except KeyboardInterrupt:
        print('{}: FIT STATUS: KEYBOARD INTERRUPT! The Queue cleanup was stopped. You monster! '
              'Fitting results are unaffected, but resources might not have been freed.'.format(tag()))

    print('{}: all fits took {:.1f} s'.format(tag(), time.time() - t1))

    return CU_params, TM_params, TM

def do_SoCC_fit(Dresser, TM, CS, mode_opts, pos_list, pickle_path, lock, queue, **kwargs):


    I_clear = Dresser.I_clear
    proc = mp.current_process()
    for pos in pos_list:
        i, j, k = pos
        with lock:
            I_cal, I_unc = Dresser[pos]
        proc.name = proc.name.replace('X', 'POS ({}, {}, {})'.format(i, j, k))
        print('{}: Starting fit of SoCC at position = ({}, {}, {})'.format(tag(), i, j, k))
        try:
            TMf, CSf, minimizer, fit_out = fit_parameters(I_cal, I_unc, I_clear, TM, CS, mode_opts, **kwargs)
        except ValueError as e:
            if 'NaN values detected' in str(e) or 'DLASCL' in str(e):
                print(
                    '{}: NaN values detected either in input or fitting calculations. Assigning garbage results.'.format(
                        tag()))
                fit_out = None
                TMf = None
                minimizer = None
            else:
                raise

        # A potential cause of the queue.get() hangs discussed above in multiproc_drawer_fit is that the queue.put()
        # call will hang indefinitely if the queue is "full" in some sense that is different than what is discussed
        # in the multiprocessing documentation. Unfortunately there seems to be no way to check for this condition. Thus
        # here we make sure that we don't put() to the queue until there is a sufficiently small number of items in the
        # queue. The idea is that we can set the multiproc_queue_objectlimit to be very small so that we'll never
        # overload the queue. The way multiproc_drawer_fit is constructed, the queue should be depopulated almost as
        # fast as items are pushed to it. Thus, this check is primarily designed to avoid a large number of threads
        # pushing their results all at once.
        while queue.qsize() >= CONSTANTS['multiproc_queue_objectlimit']:
            print('{}: FIT STATUS: Queue object limit ({}) reached. '
                  'This process is waiting to put its results on the queue.'.format(tag(),
                                                                                    CONSTANTS['multiproc_queue_objectlimit']))
            time.sleep(5)

        queue.put([i, j, k, fit_out, TMf])

        if pickle_path is not None:
            with lock:
                pickle_name = '{}/fitobj_{:04n}{:04n}{:04n}.pkl'.format(pickle_path, i, j, k)
                print('{}: saving auxiliary fitting data to {}'.format(tag(), pickle_name))
                with open(pickle_name, 'wb') as f:
                    pickle.dump(minimizer, f)
                    pickle.dump(fit_out, f)

        proc.name = proc.name.replace('POS ({}, {}, {})'.format(i, j, k), 'X')
        del I_cal

    queue.close()
    return

def generate_parameters(I_clear: np.ndarray,
                        TM: TelescopeModel.TelescopeModel,
                        CS: CUModel.CalibrationSequence,
                        mode_opts: dict,
                        nummod: int,
                        fit_TM: bool = True) -> lmfit.Parameters:
    """Create a Parameters set for an arbitrarily complex set of CS data.

    The TelescopeModel parameters are hardwired, but the CS can contain any number of single CalibrationSequences and
    therefore any number of CS parameter sets.

    Parameters
    ----------
    I_clear : numpy.ndarray
        1D array containing the average clear flux for each CS used

    TM : TelescopeModel.TelescopeModel
        An object describing the telescope configuration at each step in the CS

    CS : CUModel.CalibrationSequence
        An object describing the CU configuration at each step in the CS

    mode_opts : `configparser.ConfigParser`
        The options specified by a PA&C fitting recipe

    nummod : int
        The number of modulation states that will be fit. Used to define the modulation matrix variables.

    fit_TM : bool
        If True the Telescope Model parameters are allowed to vary in the fit

    global_tranmission : bool
        If True then all t_pol's will be the same and all t_ret's will be the same.

    global_retardance : bool
        If True then all 3 elliptical retardance parameters wll be the same for all CS's.

    Returns
    -------
    lmfit.Parameters
        Object containing information about the parameters to be used in the fit
    """

    params = lmfit.Parameters()

    ## Add telescope mirror parameters
    #
    telescope_pars = ['x34', 't34', 'x56', 't56']
    for tp in telescope_pars:
        if fit_TM:
            val = mode_opts[tp]['value']
        else:
            val = getattr(TM, tp)
        params.add(tp, value=val, vary=fit_TM,
                   min=mode_opts[tp]['min'],
                   max=mode_opts[tp]['max'])

    ## This will be a switch that defines how we treat the modulation matrix variables.
    ##  If ANY CU parameter has no bounds then we'll release the bounds on the modulation matrix as well.
    #
    CU_bounds = mode_opts['switches']['fit_bounds']

    ## Add CU Model parameters
    #
    # Add all CU parameters (except I_sys)
    for s in mode_opts.keys():
        if s == 'switches' or s == 'I_sys' or s in telescope_pars:
            continue

        if s in elliptical['global']:
            # Global parameters get a single value for all CSs
            params.add(s, **mode_opts[s])
        else:
            # These parameters are fit for every CS and thus we need a separate instance for each CS
            for i in range(CS.numdrawers):
                params.add('{}_CS{:02n}'.format(s, i), **mode_opts[s])

    # Now add I_sys. This is separate because I_sys is set relative to the actual data values
    if 'I_sys' in elliptical['global']:
        val = np.mean(I_clear)
        params.add('I_sys',
                   value=val,
                   min=val * mode_opts['I_sys']['min'],
                   max=val * mode_opts['I_sys']['max'],
                   vary=mode_opts['I_sys']['vary'])
    else:
        for i in range(CS.numdrawers):
            val = I_clear[i]
            params.add('I_sys_CS{:02n}'.format(i),
                       value=val,
                       min=val * mode_opts['I_sys']['min'],
                       max=val * mode_opts['I_sys']['max'],
                       vary=mode_opts['I_sys']['vary'])

    ## Set global transmission
    #
    if mode_opts['switches']['global_transmission']:
        # Kind of a hack; if global transmission is desired then we tie all transmissions to the first transmission
        pol_expr_str = '1. * t_pol_CS00'
        ret_expr_str = '1. * t_ret_CS00'
        for i in range(1, CS.numdrawers): # Start at 1 so we don't infinitely recurse on the "global" value
            params['t_pol_CS{:02n}'.format(i)].set(expr=pol_expr_str)
            params['t_ret_CS{:02n}'.format(i)].set(expr=ret_expr_str)

    ## Set global retardance values
    #   This is kind of a hack right now. If this ever makes it out of TelCal testing then I should modify how
    #    CalibrationSequence objects load parameters and change global-ness via the required_params.py file
    if mode_opts['switches']['global_retardance']:
        expr_str_h = '1. * ret0h_CS00'
        expr_str_45 = '1. * ret045_CS00'
        expr_str_r = '1. * ret0r_CS00'
        for i in range(1, CS.numdrawers):
            params['ret0h_CS{:02n}'.format(i)].set(expr=expr_str_h)
            params['ret045_CS{:02n}'.format(i)].set(expr=expr_str_45)
            params['ret0r_CS{:02n}'.format(i)].set(expr=expr_str_r)

    ## Add the modulation matrix variables
    #
    for m in range(nummod):
        for s in ['I', 'Q', 'U', 'V']:
            if CU_bounds:
                if s == 'I':
                    minval, maxval = 0.5, 1.5
                else:
                    minval, maxval = -1.5, 1.5
            else:
                minval, maxval = -np.inf, np.inf
            params.add('modmat_{}{}'.format(m, s), value=0, min=minval, max=maxval)

    # Now set modmat_0I to 1 and fix it. This ensures all the normalization stuff stays in I_sys
    params['modmat_0I'].set(value=1, vary=False)

    return params


def fit_parameters(I_cal, I_unc, I_clear, TM, CS, mode_opts, noprint=False,
                   method='differential_evolution', fit_TM=True, use_T=True, use_M12=True, global_transmission=False,
                   global_retardance=False, **fit_kwargs):
    """High-level fit-management function for determining the Telescope and CU parameters

    All this does is generate an appropriate parameter set and send it off to the minimizer.

    Due to the typically large number of parameters and complex chisq space, differential evolution is the recommended
    fitting method.

    Parameters
    ----------
    I_cal : numpy.ndarray
        Array of shape (M, N) containing the observed intensity values

    I_unc : numpy.ndarray
        Array of shape (M, N) containing uncertainties associated with I_cal

    I_clear : numpy.ndarray
        1D array containing the average clear flux for each separate CS used

    TM : TelescopeModel.TelescopeModel
        An object describing the telescope configuration at each step in the CS

    CS : CUModel.CalibrationSequence
        An object describing the CU configuration at each step in the CS

    mode_opts : `configparser.ConfigParser`
        The options specified by a PA&C fitting recipe

    method : str
        The fitting method to use. Valid values are:
        - `'differential_evolution'`: differential evolution (default)
        - `'leastsq'`: Levenberg-Marquardt
        - `'least_squares'`: Least-Squares minimization, using Trust Region Reflective method by default
        - `'brute'`: brute force method
        - '`nelder`': Nelder-Mead
        - `'lbfgsb'`: L-BFGS-B
        - `'powell'`: Powell
        - `'cg'`: Conjugate-Gradient
        - `'newton'`: Newton-Congugate-Gradient
        - `'cobyla'`: Cobyla
        - `'tnc'`: Truncate Newton
        - `'trust-ncg'`: Trust Newton-Congugate-Gradient
        - `'dogleg'`: Dogleg
        - `'slsqp'`: Sequential Linear Squares Programming

        For more details on the fitting methods please refer to the
        `SciPy docs <http://docs.scipy.org/doc/scipy/reference/optimize.html>`__.

    fit_TM : bool
        If True the Telescope Model parameters are allowed to vary in the fit

    fit_kwargs : dict
        Options to be passed to the minimizer being used

    noprint : bool
        If True don't print a live update of the free parameters, even if the fit is single-threaded

    Returns
    -------
    TelescopeModel.TelescopeModel
        Object containing the best fit Telescope Model

    CUModel.CalibrationSequence
        Object containing the best fit CU Model

    lmfit.Minimizer
        Minimizer object

    lmfit.MinimizerResult
        A container that holds the results of and stats about the fit
    """
    nummod = I_cal.shape[0]
    params = generate_parameters(I_clear, TM, CS, mode_opts, nummod, fit_TM=fit_TM)

    print('{}: initializing modulation matrix'.format(tag()))
    initialize_modulation_matrix(params, I_cal, TM, CS, use_T=use_T, use_M12=use_M12)

    print('{}: starting minimizer'.format(tag()))

    if not is_mp():
        print_header(params, noprint=noprint)

    modmat = np.zeros((I_cal.shape[0], 4), dtype=np.float64)
    t1 = time.time()
    mini = lmfit.Minimizer(compare_I, params, fcn_args=(I_cal, I_unc, TM, CS, modmat, t1),
                           fcn_kws={'use_T': use_T, 'use_M12': use_M12, 'noprint': noprint})
    fit_out = mini.minimize(method=method, params=params, **fit_kwargs)

    if not (is_mp() or noprint):
        print()

    print('{:}: minimization completed in {:4.1f} s. Chisq = {:8.2e}, redchi = {:8.2e}'.format(tag(), time.time() - t1,
                                                                                               fit_out.chisqr,
                                                                                               fit_out.redchi))

    return TM, CS, mini, fit_out


def compare_I(params, I_cal, I_unc, TM, CS, modmat, t1, use_T=True, use_M12=True, noprint=False):
    """The fitness/fitting function for fitting Telescope and CU parameters.

    First, a modulation matrix is determined and then used to generate some model output data. These data are then
    compared to the observed output data.

    Parameters
    ----------
    params : lmfit.Parameters
        Object containing information about the parameters to be used in the fit

    I_cal : numpy.ndarray
        Array of shape (M, N) containing the observed intensity for each modulator state (M) in each CS step (N).

    TM : TelescopeModel.TelescopeModel
       An object describing the telescope configuration at each step in the CS

    CS : CUModel.CalibrationSequence
        An object describing the CU configuration at each step in the CS

    t1 : float
        Time the fit was started, in seconds since the Unix Epoch.

    use_T : bool
        If True then include the M36 Mueller matrix

    use_M12 : bool
        If True then include the M12 Mueller matrix

    noprint : bool
        If True don't print a live update of the free parameters, even if the fit is single-threaded

    Returns
    -------
    numpy.ndarray
        Array of shape (M * N,) containing the difference between the observed and modeled data, normalized by the
        observed data. lmfit.minimize handles the squaring and summing internally.
    """
    parvals = params.valuesdict()
    TM.x34 = parvals['x34']
    TM.t34 = parvals['t34']
    TM.x56 = parvals['x56']
    TM.t56 = parvals['t56']

    CS.load_pars_from_dict(parvals)

    S = generate_S(TM, CS, use_T=use_T, use_M12=use_M12)
    #O = fit_modulation_matrix(I_cal, S)
    O = fill_modulation_matrix(parvals, modmat)

    I_mod = generate_model_I(O, S)

    diff = np.ravel((I_mod - I_cal) / I_unc)

    if not (is_mp() or noprint):
        print_status(params, diff, t1)

    return diff


def generate_S(TM, CS, use_T=True, use_M12=True):
    """Compute the Stokes vector immediately after the Calibration Unit

    Parameters
    ----------
    TM : TelescopeModel.TelescopeModel
        The TelescopeModel object used for fitting

    CS : CUModel.CalibrationSequence
        The CalibrationSequence object used for fitting

    use_T : bool
        If True then include the M36 Mueller matrix

    use_M12 : bool
        If True then include the M12 Mueller matrix

    Returns
    -------
    numpy.ndarray
        (4, N) array containing the CU output Stokes vector at each step in the CS
    """
    S = np.diag(np.ones(4, dtype=np.float64))
    if use_T:
        S = S @ TM.TM

    S = S @ CS.CM

    if use_M12:
        S = S @ TM.M12

    S = np.sum(S * CS.S_in[:, None, :], axis=2).T

    return S

def fit_modulation_matrix(I_cal, S):
    """Find a modulation matrix, O, that satisfies I = O T s.

    In our case the problem will most likely be massively over-constrained so we use a least-squares fit to find O.

    Parameters
    ----------
    M -> number of modulator states
    N -> number of steps in Calibration Sequence

    I_cal : numpy.ndarray
        Array of shape (M, N) containing the observed intensity values

    S : numpy.ndarray
        Array of shape (4, N) containing the model Stokes vector input to the instrument (i.e., after M6)

    Returns
    -------
    numpy.ndarray
        Array of shape (M, 4) containing the instrument modulation matrix.

    """
    # linalg.lstsq solves x for Ax = B, but in our case we want to solve O for I = O S.
    #  Fortunately we can use the identity Ax = B <-> x.T A.T = B.T and therefore recast our problem into the proper
    #  form: I.T = S.T O.T

    res = np.linalg.lstsq(S.T, I_cal.T, rcond=None)
    O = res[0].T

    #O /= np.max(O[:,0])
    O /= O[0,0]

    return O

def initialize_modulation_matrix(params, I_cal, TM, CS, use_T=True, use_M12=True):
    parvals = params.valuesdict()
    TM.x34 = parvals['x34']
    TM.t34 = parvals['t34']
    TM.x56 = parvals['x56']
    TM.t56 = parvals['t56']

    CS.load_pars_from_dict(parvals)

    S = generate_S(TM, CS, use_T=use_T, use_M12=use_M12)
    O = fit_modulation_matrix(I_cal, S)

    for m in range(O.shape[0]):
        for i, s in enumerate(['I', 'Q', 'U', 'V']):
            params['modmat_{}{}'.format(m,s)].set(value=O[m, i])

    # Just in case
    params['modmat_0I'].set(value=1)

def fill_modulation_matrix(parvals, modmat):

    nummod = modmat.shape[0]
    for m in range(nummod):
        for i, s in enumerate(['I', 'Q', 'U', 'V']):
            modmat[m, i] = parvals['modmat_{}{}'.format(m, s)]

    return modmat

def generate_model_I(O, S):
    """Given models for the telescope, CU, and modulation matrix, construct ideal output data.

    The "input" light is taken from the CalibrationSequence object and is probably unpolarized light ([1,0,0,0]).

    Parameters
    ----------
    O : numpy.ndarray
        Array of shape (M, 4) containing the instrument modulation matrix.

    S : numpy.ndarray
        Array of shape (4, N) containing the model Stokes vector input to the instrument (i.e., after M6)

    Returns
    -------
    numpy.ndarray
        Array of shape (M, N) containing the modeled intensity in each modulation state at each step of the CS.
    """

    I_mod = O @ S

    return I_mod


def print_status(params, diff, t1):
    """Print the current state of the fit.

    If the full suite of free parameters is too large to fit in a single terminal window then an appropriate number of
    free parameters will be hidden and their presence indicated with a '...'. If the current terminal has less than 25
    columns then this function will not stop wrapping. Use a bigger terminal!

    This is a separate function so that the logic to fit the message to the current terminal is isolated. To avoid a
    ton of system calls during fitting the terminal width is only computed on import.

    Parameters
    ----------
    params : lmfit.Parameters
        Object containing information about the parameters to be used in the fit

    diff : float
        Sqrt(chi^2). The minimization parameter used by the fit.

    t1 : float
        The time at which the fit was started (UNIX format)
    """
    status_str = '\r'

    next_width = 10
    truncated = False
    for v in params.keys():
        if params[v].vary:
            if next_width > TERMCOL - 25:
                truncated = True
                continue

            if np.log10(np.abs(params[v].value) + 1) >= 5:
                status_str += '{:>10.3e}'.format(params[v].value)
            else:
                status_str += '{:>10.3f}'.format(params[v].value)
            next_width += 10

    if truncated:
        status_str += '{:>5}'.format('...')

    status_str += '{:10.3e}'.format(np.sum(diff**2))

    dt = time.time() - t1
    time_unit = ' s'
    if dt > 120:
        dt /= 60
        time_unit = ' m'
    status_str += '{:8.1f}{:}'.format(dt, time_unit)

    print(status_str, end="", flush=True)

#TODO: Print initial values as well
def print_header(params, noprint=False):
    """Print fixed parameters and a header that defines columns in the free-parameter status message.

    If the full suite of free parameters is too large to fit in a single terminal window then an appropriate number of
    parameters will be hidden and their presence indicated with a '...'. If the current terminal has less than 25
    columns then this function will not stop wrapping. Use a bigger terminal!

    This is a separate function so that the logic to fit the message to the current terminal is isolated. The terminal
    width is computed once on import.

    Parameters
    ----------
    params : lmfit.Parameters
        Object containing information about the parameters to be used in the fit

    noprint : bool
        If True then the column headers for live updates of the free parameters will not be printed
    """
    fixed_str = 'Fixed parameters:\n'
    init_str = 'Starting values:\n'
    I_sys_str = 'I_sys starting values:\n'
    free_str = ''

    next_free_width = 10
    truncated = False
    for v in params.keys():
        if 'I_sys' in v:
            I_sys_str += '{:<10} : {:5.3f}\n'.format(v.replace('CS', ''), params[v].value)

        if params[v].vary:
            if 'I_sys' not in v:
                init_str += '{:<10} : {:5.3f}\n'.format(v.replace('CS', ''), params[v].value)
            if next_free_width > TERMCOL - 25:
                truncated = True
                continue

            free_str += '{:>10}'.format(v.replace('CS', ''))
            next_free_width += 10
        else:
            fixed_str += '{:<10} : {:5.3f}\n'.format(v.replace('CS', ''), params[v].value)

    if not noprint:
        I_sys_str += '\nFree parameters:'

        if truncated:
            free_str += '{:>5}'.format('...')

        free_str += '{:>10}{:>10}'.format('chisq', 't_elapsed')

    else:
        I_sys_str += '\nFree parameter live update suppressed'

    print(fixed_str)
    print(init_str)
    print(I_sys_str)
    if not noprint:
        print(free_str)

import numpy as np
from dkist_processing_pac import Data, CUModel, TelescopeModel, generic, FittingFramework
from dkist_processing_pac.tag import tag

def prep_fit(dirlist, suffix='.FITS', telescope_db=None, fit_mode='baseline', init_set='default', fit_TM=True,
             skip_darks=True):
    """Do the setup of a fit and return the relevant variables (Dresser, CS, TM, and params)

    The purpose is to save some console time during debugging.
    """
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

    mode_opts = generic.init_fit_mode(fit_mode, DRSR.wavelength, fit_TM, init_set=init_set)
    global_transmission = mode_opts['switches']['global_transmission']

    # We need to initialize a dummy CU model
    dummy = np.zeros(1)
    CS = CUModel.CalibrationSequence(*([dummy] * 6))
    CS.init_with_dresser(DRSR)  # And now actually fill it with the correct configurations

    TM = TelescopeModel.TelescopeModel(DRSR.azimuth, DRSR.elevation, DRSR.table_angle)

    print('{}: updating polarizer py value'.format(tag()))
    wave = DRSR.wavelength
    CS.set_py_from_database(wave)

    print('{}: loading telescope database from {}'.format(tag(), telescope_db))
    if telescope_db is None:
        telescope_db = generic.get_default_telescope_db()
    mean_time = 0.5 * (DRSR.date_bgn + DRSR.date_end)
    TM.load_from_database(telescope_db, mean_time, wave)

    numx, numy, numl = DRSR.shape
    if fit_TM:
        print('{}: shape of Dresser data: ({}, {}, {})'.format(tag(), numx, numy, numl))
    else:
        print('{}: shape of Drawer data: ({}, {}, {})'.format(tag(), numx, numy, numl))
    print('{}: number of modulator states: {}'.format(tag(), DRSR.nummod))
    print('{}: number of CS steps: {}'.format(tag(), DRSR.numsteps))

    nummod = DRSR.nummod
    I_clear = DRSR.I_clear
    params = FittingFramework.generate_parameters(I_clear, TM, CS, mode_opts, nummod, fit_TM=fit_TM)

    return DRSR, CS, TM, mode_opts, params

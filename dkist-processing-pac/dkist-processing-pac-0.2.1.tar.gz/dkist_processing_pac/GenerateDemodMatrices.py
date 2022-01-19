import os
import numpy as np
from astropy.io import fits as pyfits
from dkist_processing_pac import Data, CUModel, TelescopeModel, FittingFramework, generic
from dkist_processing_pac.tag import tag


def main(data_dir, CU_par_file, dmod_output, overwrite=True, suffix='.FITS', telescope_db='telescope_db.txt',
         skip_darks=True):
    """Load previously-computed CU model parameters and use them to compute demodulation matrices.

    This function also requires a Drawer of PolCal data, which should be the exact same data used to fit the CU
    parameters. It is OK (and expected) that these data and the CU parameters themselves will be resampled from the
    field-sampling used to fit the CU parameters. This allows the Instrument Partners to define different Regions of
    Calibration Unit Homogeneity for the fit of parameters and the calculation of demodulation matrices.

    If the input PolCal data have shape (X, Y, M, N) where (X, Y) are the field shape of the data, M is the number
    of modulation states, and N is the number of CS steps then the resulting demodulation matrices will have shape
    (X, Y, 4, M) and will be saved to the first ImageHDU of a single FITS file. The header for this FITS file is a copy
    of the header in the Drawer's first CS step.

    Parameters
    ----------
    data_dir: str
        Location of the directory containing reduced data from a single PolCal sequence (i.e., a Drawer)

    CU_par_file : str
        Location of file containing a set of CU model parameters at each (x, y) field location in the Drawer

    dmod_output : str
        Location in which to save the final demodulation matrices

    overwrite : bool
        If True then ``dmod_output`` will be overwritten if it exists

    suffix : str
        Only files in ``data_dir`` with this suffix will be loaded

    telescope_db : str
        Location of the file containing Telescope Model parameters as a function of time and wavelength

    skip_darks : bool
        If True (default) then don't include and dark steps of the CS in fitting

    """
    if os.path.exists(dmod_output) and not overwrite:
        raise IOError('File {} already exists and overwrite is False'.format(dmod_output))

    DRWR = Data.Drawer(data_dir, suffix=suffix, skip_darks=skip_darks)
    print('{}: loaded SoCC from {}'.format(tag(), data_dir))

    CMP = Data.CUModelParams(*(DRWR.shape + (1, DRWR.nummod)))
    CMP.loadfits(CU_par_file)
    print('{}: loaded CU Model Parameters from {}'.format(tag(), CU_par_file))

    demodulation = core_demod(DRWR, CMP, telescope_db)

    print('{}: saving demodulation matrices to {}'.format(tag(), dmod_output))
    primary = pyfits.PrimaryHDU(header=DRWR.data_list[0][0].header)
    primary.header['OBJECT'] = 'Demodulation matrix'

    dmod_hdu = pyfits.ImageHDU(demodulation, header=DRWR.data_list[0][0].header)
    dmod_hdu.header['OBJECT'] = 'Demodulation matrix'
    pyfits.HDUList([primary, dmod_hdu]).writeto(dmod_output, overwrite=overwrite)
    del DRWR
    CMP.cleanup()

    return

def DC_main(dresser: Data.Dresser, cu_params: Data.CUModelParams, telescope_db: str) -> np.ndarray:

    if len(dresser.drawers) == 0:
        raise ValueError('The provided dresser has no Drawers!')
    if len(dresser.drawers) > 1:
        raise ValueError('The provided dresser has more than one Drawer')

    drawer = dresser.drawers[0]

    return core_demod(drawer, cu_params, telescope_db)

def core_demod(drawer: Data.Drawer, cu_params: Data.CUModelParams, telescope_db: str) -> np.ndarray:

    mode_opts = generic.init_fit_mode(cu_params.fit_mode, drawer.wavelength, False, cu_params.init_set)
    use_T = mode_opts['switches']['use_T']
    use_M12 = mode_opts['switches']['use_M12']

    CS = CUModel.CalibrationSequence(drawer.theta_pol_steps, drawer.theta_ret_steps, drawer.pol_in, drawer.ret_in,
                                     drawer.dark_in, drawer.timeobs)
    TM = TelescopeModel.TelescopeModel(drawer.azimuth, drawer.elevation, drawer.table_angle)

    print('{}: updating polarizer py value'.format(tag()))
    wave = drawer.wavelength
    CS.set_py_from_database(wave)

    print('{}: loading telescope database from {}'.format(tag(), telescope_db))
    mean_time = 0.5 * (drawer.date_bgn + drawer.date_end)
    TM.load_from_database(telescope_db, mean_time, wave)
    numx, numy, numl = drawer.shape
    nummod = drawer.nummod
    demodulation = np.zeros((numx, numy, numl, 4, nummod), dtype=np.float64)

    print('{}: shape of Drawer: ({}, {}, {})'.format(tag(), numx, numy, numl))
    print('{}: computing demoduation matrices'.format(tag()))
    for i in range(numx):
        for j in range(numy):
            for k in range(numl):
                print('{}:  position = ({}, {}, {})'.format(tag(), i, j, k))
                I_cal = drawer[i, j, k]
                CS.load_pars_from_dict(cu_params[i, j, k])

                print('{}:  fitting modulation matrix to best CU model'.format(tag()))
                S = FittingFramework.generate_S(TM, CS, use_T=use_T, use_M12=use_M12)
                try:
                    O = FittingFramework.fit_modulation_matrix(I_cal, S)
                except ValueError as e:
                    if 'illegal value' in str(e):
                        print('{}:  Garbage results detected. Setting pass-through demodulation matrix.'.format(tag()))
                        O = np.zeros((nummod, 4))
                        O[:, 0] = 1./nummod
                    else:
                        raise

                print('{}:  computing inverse of modulation matrix'.format(tag()))
                demodulation[i, j, k, :, :] = np.linalg.pinv(O)

    return demodulation

def command_line():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Generate demodulation matrices from a single Calibration Sequence. '
                                     'The data directory specified must contain a separate FITS file for each step in '
                                     'the CS that has already been processed by the instrument reduction code. The '
                                     'CU par file is the output of `pac_cu_par`.')
    parser.add_argument('data_dir', help='Directory containing a single Calibration Sequence')
    parser.add_argument('CU_pars', help='FITS file containing best fit Calibration Unit parameters')
    parser.add_argument('output', help='Location of FITS file to save demodulation matrices')
    parser.add_argument('-f', '--force', action='store_true', help='Overwrite outputs')
    parser.add_argument('-t', '--telescope-db', help='Database listing telescope parameters as function of obstime and '
                                                     'wavelength. This option is ignored if telescope_db is defined in '
                                                     'a provided CONFIG_FILE (-c).', default=None)
    parser.add_argument('-s', '--suffix', help='File suffix to filter data. File mask is data_dir/*suffix',
                        default='.FITS')
    parser.add_argument('-D', '--use-darks', action='store_false', help='Include any DARK CS steps in the fit')
    args = parser.parse_args()

    if args.telescope_db is None:
        args.telescope_db = generic.get_default_telescope_db()

    if os.path.exists(args.data_dir):
        sys.exit(main(args.data_dir, args.CU_pars, args.output, suffix=args.suffix, overwrite=args.force,
                      telescope_db=args.telescope_db, skip_darks=args.use_darks))
    else:
        print('Directory {} does not exist. Aborting.'.format(args.data_dir))
        sys.exit(1)


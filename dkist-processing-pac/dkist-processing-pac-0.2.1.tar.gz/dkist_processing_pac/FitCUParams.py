import ast
import os
from configparser import ConfigParser
from dkist_processing_pac import FittingFramework, generic, Data
from dkist_processing_pac.tag import tag


def main(data_dir, CU_par_output, overwrite=False, save_stats=False, suffix='.FITS',
         telescope_db='telescope_db.txt', **kwargs):
    """Launch a fit for CU parameters on a single Drawer (i.e., data from a single PolCal sequence)

    The result is a single file that contains the best-fit CU parameters (and all parameters that were fixed). This file
    can then be resampled by the Instrument Partners to whatever sampling they need for the calculation of the actual
    demodulation matrices.

    Input data representing the PolCal sequence are read from the provided directory and assumed to have the following
    format. Each of the N steps in the CS exists as a single file with M HDUs (one for each modulator state), each
    with shape (X, Y). The resulting CU parameter file will have a single HDU with a single array of shape (X, Y, Z),
    where Z is the number of parameters in the CU model.

    Different combinations of free/fixed parameters are specified in the PA&C fitting recipe database. A recipe is
    loaded via the ``fit_mode`` keyword.

    Parameters
    ----------
    data_dir : str
        Location of the directory containing reduced data from a single PolCal sequence (i.e., a Drawer)

    CU_par_output : str
        Location in which to save the CU parameter file

    overwrite : bool
        If True then ``CU_par_output`` will be overwritten if it already exists

    save_stats : bool
        If True then a directory called "fitaux" will be created along side ``CU_par_output``. This directory will
        contain pickle objects with auxiliary fit information for use by QA routines

    suffix : str
        Only files in ``data_dir`` with this suffix will be loaded

    telescope_db : str
        Location of the file containing Telescope Model parameters as a function of time and wavelength

    kwargs : dict
        Any additional arguments to pass to the `FittingFramework`

    """
    if os.path.exists(CU_par_output) and not overwrite:
        raise IOError('File {} already exists and overwrite is False'.format(CU_par_output))

    print('{}: starting CU parameter fitting using SoCC found in {}'.format(tag(), data_dir))

    if save_stats:
        dirname = os.path.dirname(CU_par_output) or '.'
        pickle_path = '{}/fitaux'.format(dirname)
        os.makedirs(pickle_path, exist_ok=True)
    else:
        pickle_path = None

    CU_params, TM_params, _ = FittingFramework.run_fits([data_dir], suffix=suffix, fit_TM=False,
                                                        telescope_db=telescope_db, pickle_path=pickle_path, **kwargs)
    print('{}: saving best-fit CU parameters to {}'.format(tag(), CU_par_output))
    DRWR = Data.Drawer(data_dir, suffix=suffix)
    CU_params.writeto(CU_par_output, header=DRWR.data_list[0][0].header, overwrite=overwrite)
    CU_params.cleanup()
    TM_params.cleanup()

    return


def command_line():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Compute demodulation matrices from a single Calibration Sequence. '
                                     'The data directory specified must contain a separate FITS file for each step in '
                                     'the CS that has already been processed by the instrument reduction code.')
    parser.add_argument('data_dir', help='Directory containing a single Calibration Sequence', nargs='?')
    parser.add_argument('output', help='Location of FITS file to save demodulation matrices', nargs='?',
                        default='dmod.fits')
    parser.add_argument('-f', '--force', action='store_true', help='Overwrite outputs')
    parser.add_argument('-c', '--config', help='Load program parameters from supplied configuration INI file',
                        metavar='CONFIG_FILE')
    parser.add_argument('-t', '--telescope-db', help='Database listing telescope parameters as function of obstime and '
                                                     'wavelength. This option is ignored if telescope_db is defined in '
                                                     'a provided CONFIG_FILE (-c).',
                        nargs=1, default=[])
    parser.add_argument('-s', '--suffix', help='File suffix to filter data. File mask is data_dir/*suffix',
                        default='.FITS')
    parser.add_argument('-S', '--save-fit', action='store_true', help='Save lmfit-style fitting statistics')
    parser.add_argument('-m', '--fit-mode', help='The fitting recipe to use', default='baseline')
    parser.add_argument('-R', '--init-set', help='Name of the initial value set to use', default='default',
                        metavar='SET_NAME')
    parser.add_argument('-d', '--default', help='Generate a configuration file with the standard default values',
                        metavar='CONFIG_FILE')
    parser.add_argument('-D', '--use-darks', action='store_false', help='Include any DARK CS steps in the fit')
    args = parser.parse_args()

    if args.default is not None:
        generic.gen_default_config(args.default)
        sys.exit(0)

    kwargs = {'fit_mode': args.fit_mode,
              'skip_darks': args.use_darks,
              'init_set': args.init_set}
    if not args.telescope_db:
        kwargs['telescope_db'] = generic.get_default_telescope_db()
    else:
        kwargs['telescope_db'] = args.telescope_db[0]

    if args.config is not None:
        config = ConfigParser()
        config.optionxform = str
        config.read(args.config)
        kwargs.update(dict(config['Main']))
        for k in kwargs.keys():
            try:
                kwargs[k] = ast.literal_eval(kwargs[k])
            except:
                pass

    if args.data_dir is None:
        print('You must specify the location of the data directory')
        sys.exit(1)

    if os.path.exists(args.data_dir):
        sys.exit(main(args.data_dir, args.output, suffix=args.suffix, overwrite=args.force,
                      save_stats=args.save_fit, **kwargs))
    else:
        print('Directory {} does not exist. Aborting.'.format(args.data_dir))
        sys.exit(1)
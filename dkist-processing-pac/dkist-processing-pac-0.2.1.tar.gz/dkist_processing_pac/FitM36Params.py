from configparser import ConfigParser
from glob import glob
import ast
import os
from dkist_processing_pac import FittingFramework, generic
from dkist_processing_pac.tag import tag


def main(top_level_dir, CU_output, TM_output, overwrite=False, save_stats=False, suffix='.FITS',
         telescope_db='telescope_db.txt', numCS=None, update_db=False, **kwargs):
    """Launch a fit for Telescope Model M36 group parameters using data from multiple PolCal sequences (i.e., a Dresser)

    The resulting best-fit values for the M36 parameters are pushed to the PA&C Telescope database iff ``update_db`` is
    True, otherwise they are simply printed to stdout and saved as header entries in the Telescope Mueller matrix output
    file. That Mueller matrix contains two HDUs; the first contains the Mueller matrix for M3 up to but not including
    M7 and the second contains the Mueller matrix for M12. The usefulness of this file is questionable because it the
    Mueller matrices will only be valid for a single geometry of the Telescope (which is specified in the header).

    Fitting M36 parameters requires multiple PolCal sequences (Drawers). Each Drawer should live in its own directory
    within the provided top-level directory. Each Drawer directory is assumed to have the following format: Each of the
    N steps in the CS exists as a single file with M HDUs (one for each modulator state), each with shape (X, Y). The
    resulting CU parameter file will have a single HDU with a single array of shape (X, Y, Z), where Z is the number of
    parameters in the CU model.

    Different combinations of free/fixed parameters are specified in the PA&C fitting recipe database. A recipe is
    loaded via the ``fit_mode`` keyword.

    Parameters
    ----------
    top_level_dir : str
        Location of directory containing sub-directories for each Drawer to be used for the fit

    TM_output : str
        Location in which to save a Telescope Mueller matrix FITS file. See above for file format and limitation.

    numCS : int
        Number of Drawers to use. If numCS < the total number of Drawers found in ``top_level_dir`` then only the first
        ``numCS`` drawers will be used.

    update_db : bool
        If True then the PA&C Telescope Model database will be updated with the best-fit values from the fit

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

    if os.path.exists(TM_output) and not overwrite:
        raise IOError('File {} already exists and overwrite is False'.format(TM_output))

    # These next two lines are why I love python
    dirlist = sorted([i for i in glob('{}/*'.format(top_level_dir)) if os.path.isdir(i)])
    dirlist = dirlist[:numCS]

    if save_stats:
        dirname = os.path.dirname(TM_output) or '.'
        pickle_path = '{}/fitaux'.format(dirname)
        os.makedirs(pickle_path, exist_ok=True)
    else:
        pickle_path = None

    CU_params, TM_params, best_TM = FittingFramework.run_fits(dirlist, suffix=suffix, telescope_db=telescope_db,
                                                              pickle_path=pickle_path, fit_TM = True, **kwargs)

    print('{}: saving best-fit CU parameters to {}'.format(tag(), CU_output))
    CU_params.writeto(CU_output, overwrite=overwrite)
    CU_params.cleanup()
    print('{}: saving best-fit TM parameters to {}'.format(tag(), TM_output))
    TM_params.writeto(TM_output, overwrite=overwrite)
    TM_params.cleanup()

    if update_db:
        best_TM.save_to_database(telescope_db)

    return

def command_line():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Use a set of Calibration Sequences to compute the Telescope mirror'
                                     "parameters. Accuracy is improved by using more CS's, but only to a point."
                                     'The data directory should contain a series of Calibration Sequences, each in its '
                                     'own subdirectory. Each CS should contain a single FITS file for each step in '
                                     'the CS that has already been reduced by instrument reduction code.')
    parser.add_argument('top_dir', help='Top-level directory containing Calibration Sequence subdirectories', nargs='?')
    parser.add_argument('CU_output', help='Location of FITS file to save Calibration Unit Parameters', nargs='?',
                        default='CMP.fits')
    parser.add_argument('TM_output', help='Location of FITS file to save Telescope Model Parameters', nargs='?',
                        default='TMP.fits')
    parser.add_argument('-N', '--numCS', type=int,
                        help="Number of CS's to use for the fit. If unspecified then all CS's found will be used")
    parser.add_argument('-t', '--telescope-db', help='Database listing telescope parameters as function of obstime and '
                                                     'wavelength',
                        nargs=1, default=[])
    parser.add_argument('-u', '--update-db', action='store_true',
                        help='Update the Telescope Database with the new values')
    parser.add_argument('-f', '--force', action='store_true', help='Overwrite outputs')
    parser.add_argument('-c', '--config', help='Load program parameters from supplied configuration INI file',
                        metavar='CONFIG_FILE')
    parser.add_argument('-m', '--fit-mode', help='The fitting recipe to use', default='baseline')
    parser.add_argument('-R', '--init-set', help='Name of the initial value set to use', default='default',
                        metavar='SET_NAME')
    parser.add_argument('-s', '--suffix', help='File suffix to filter data. File mask is data_dir/*suffix',
                        default='.FITS')
    parser.add_argument('-S', '--save-fit', action='store_true', help='Save lmfit-style fitting statistics')
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

    if args.top_dir is None:
        print('You must specify the location of the top-level data directory')
        sys.exit(1)

    if os.path.exists(args.top_dir):
        sys.exit(main(args.top_dir, args.CU_output, args.TM_output, suffix=args.suffix, overwrite=args.force,
                      numCS=args.numCS, update_db=args.update_db, save_stats=args.save_fit, **kwargs))
    else:
        print('Directory {} does not exist. Aborting.'.format(args.data_dir))
        sys.exit(1)

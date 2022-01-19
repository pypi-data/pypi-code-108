import hashlib
import numpy as np
from dkist_processing_pac.data import CONSTANTS

def compute_X12(i2q, i2u):
    """Compute the X12 mirror parameter from measures of continuum polarization

    For now this assumes no rotation b/t M2 and the CU. This might change in the future.

    Parameters
    ----------
    i2q : float
        Q/I in a continuum region

    i2u : float
        U/I in a continuum region

    Returns
    -------
    float
        X12 mirror parameter

    """
    X12 = np.sqrt((1 - i2q) / (1 + i2q))

    return X12

def update_xtalk_database(i2q, i2u, instrument_name, date, wave, notes='', db_file=None):
    """Update the monitoring database that contains every measurement of X12 from all science programs

    Each entry is given a unique hash in addition to keeping track of instrument, date, and wavelength. This ensures
    that potential race-condition collisions don't happen.

    Parameters
    ----------
    i2q : float
        Q/I in a continuum region

    i2u : float
        Q/U in a continuum region

    instrument_name : str
        The name of the instrument providing this information. Truncated to 20 characters.

    date : float
        The current time/time of observations in MJD

    wave : float
        The wavelength of observations in nm

    notes : str
        Any user notes. Spaces will be converted to _

    db_file : str
        If provided, the path to the X12 database file. If None then the default file will be loaded.

    Returns
    -------
    None
    """
    X12 = compute_X12(i2q, i2u)

    info_str = '{}{}{}{}{}'.format(instrument_name, date, i2q, i2u, X12)
    hash_str = hashlib.sha256(info_str.encode()).hexdigest()

    if db_file is None:
        db_file = CONSTANTS['xtalk_db_file']

    with open(db_file, 'a') as f:
        f.write('{:66}{:20.20} {:20.20} {:20.10f} {:7.2f} {:10.6f} {:10.6f} {:10.6f}\n'.format(hash_str,
                                                                                               instrument_name.replace(' ','_'),
                                                                                               notes.replace(' ','_'),
                                                                                               date, wave,
                                                                                               i2q, i2u, X12))

    return

def get_updated_X12(db_file=None):
    """Return the 'best' X12 value from the monitoring database.

    Right now this just returns the most recent value. This will probably change at some point.

    Parameters
    ----------
    db_file : str
        If provided, the path to the X12 database file. If None then the default file will be loaded.

    Returns
    -------
    float
        The most up-to-date value of X12
    """
    if db_file is None:
        db_file = CONSTANTS['xtalk_db_file']

    mjd, wave, X12 = np.loadtxt(db_file, usecols=(3, 4, 7), unpack=True)

    sidx = np.argsort(mjd)

    return X12[sidx[-1]]

def write_blank_db_file(db_file=None):
    """Generate a blank X12 monitoring file.

    Really this just writes the header

    Parameters
    ----------
    db_file : str
        If provided, the path to the X12 database file. If None then the default file will be loaded.

    Returns
    -------
    None
    """
    if db_file is None:
        db_file = CONSTANTS['xtalk_db_file']

    with open(db_file, 'w') as f:
        f.write('# {:64}{:20} {:20} {:>20} {:>7} {:>10} {:>10} {:>10}\n\n'.format('Unique hash',
                                                                                 'Instrument Name',
                                                                                 'Notes', 'Date [MJD]', 'Wave',
                                                                                 'Q/I','Q/U','X12'))

    return

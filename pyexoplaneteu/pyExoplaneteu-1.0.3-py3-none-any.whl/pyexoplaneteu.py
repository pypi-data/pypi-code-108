#!/usr/bin/env python
import os
from urllib import request
from socket import timeout
import time
import math
import csv
import pprint
from collections import OrderedDict

from .utils import float_cols

# the link in the "Download CSV" button
download_link = 'http://exoplanet.eu/catalog/csv'

# to get the directory where SWEET-Cat data will be stored
from .config import get_data_dir

# Jup -> Earth
mjup2mearth = 317.8284065946748
rjup2rearth = 11.209

# solar system
mass_solar_system = [0.330, 4.87, 5.97, 0.642, 1898, 568, 86.8, 102] # 10^24 kg
diam_solar_system = [4879, 12104, 12756, 6792, 142984, 120536, 51118, 49528] # km
init_solar_system = ['M', 'V', 'E', 'M', 'J', 'S', 'U', 'N']


def download_data(verbose=True, throw=True):
    """ Download exoplanet.eu data and save it to `exoplanetEU.csv` """

    try:
        with request.urlopen(download_link, timeout=4) as response:
            data = response.read()
    except (request.HTTPError, request.URLError) as error:
        if throw:
            raise error
    except timeout as error:
        if throw:
            raise error
    else:
        print('Access successful.')

    local_file = os.path.join(get_data_dir(), 'exoplanetEU.csv')
    with open(local_file, 'wb') as f:
        f.write(data)

    if verbose:
        print(f'Saved exoplanet.eu data to {local_file}')


def check_data_age():
    """ How old is `exoplanetEU.csv`, in days """
    local_file = os.path.join(get_data_dir(), 'exoplanetEU.csv')
    age = time.time() - os.path.getmtime(local_file) # in sec
    return age / (60*60*24) # in days


class DataDict(OrderedDict):
    numpy_entries = False
    units = 'jup'

    __doc__ = "exoplanet.eu: a catalog of parameters for known exoplanets.\n" + \
              "The catalog and more information can be found " \
              "at http://exoplanet.eu\n" + \
              "This dictionary has the catalog columns as its keys; " \
              "see the `.columns()` method.\n" + \
              "Entries are lists, see `to_numpy()` to convert them to numpy arrays."
    def __init__(self, *args, **kwargs):
        super(DataDict, self).__init__(self, *args, **kwargs)

    def __getitem__(self, key):
        # allows to do data['key_nonan'] to get data['key'] without NaNs as well
        # as data[0] to get all columns for the 0th entry in the table
        if isinstance(key, int):
            return {k:v[key] for k, v in self.items()}

        if key.endswith('_nonan'):
            val = super().__getitem__(key.replace('_nonan',''))
            try:
                if self.numpy_entries:
                    from numpy import isnan
                    val = val[~isnan(val)]
                else:
                    val = [v for v in val if not math.isnan(v)]
            except TypeError:
                # this column does not have floats
                pass
        else:
            val = super().__getitem__(key)

        return val

    def __str__(self):
        return 'exoplanet.eu data'
    def __repr__(self):
        return f'exoplanet.eu data: dictionary with {self.size} entries. '+\
                'Use .columns() to get the column labels.'
    def _repr_pretty_(self, p, cycle):
        return p.text(self.__repr__())

    def __len__(self):
        return len(self.__getitem__('name'))

    def columns(self):
        """ List the available columns """
        pprint.pprint(list(self.keys()), compact=True)

    @property
    def size(self):
        return len(self.__getitem__('name'))

    def to_numpy(self, inplace=True):
        """ 
        Convert entries to numpy arrays. If `inplace` is True convert
        the entries in place, else return a new dictionary.
        """
        try:
            from numpy import asarray # this assumes numpy is installed
        except ImportError:
            print('Please install numpy to use this function')

        newself = self if inplace else DataDict()
        for k, v in self.items():
            newself[k] = asarray(v)
        newself.numpy_entries = True
        if not inplace:
            return newself

    def jup2earth(self):
        # convert mass
        cols = (
            'mass', 'mass_error_min', 'mass_error_max', 'mass_sini',
            'mass_sini_error_min', 'mass_sini_error_max'
            )

        for c in cols:
            if self.numpy_entries:
                self[c] *= mjup2mearth
            else:
                self[c] = [m*mjup2mearth for m in self[c]]

        # convert radius
        cols = ('radius', 'mass_error_min', 'radius_error_max')

        for c in cols:
            if self.numpy_entries:
                self[c] *= rjup2rearth
            else:
                self[c] = [r*rjup2rearth for r in self[c]]

        self.units = 'earth'


    def errorbar(self, col1, col2, col1_error_lim=None, col2_error_lim=None,
                 logx=False, logy=False, show_SS=False):
        try:
            import matplotlib.pyplot as plt
            from numpy import c_, zeros, isnan, max
        except ImportError:
            print('Please install numpy and matplotlib to use this function')

        assert col1 in self, f'column {col1} not found'
        assert col2 in self, f'column {col2} not found'
        x_errors = col1+'_error_min' in self
        y_errors = col2+'_error_min' in self

        if x_errors:
            xerr = c_[self[col1+'_error_min'], self[col1+'_error_max']].T
        else:
            xerr = zeros((2, self.size))
        xerr[isnan(xerr)] = 0.

        if col1_error_lim:
            m = (max(xerr, axis=0) / self[col1]) < col1_error_lim
            xerr[:, m] = 0
        print(xerr)

        if y_errors:
            yerr = c_[self[col2+'_error_min'], self[col2+'_error_max']].T
        else:
            yerr = zeros((2, self.size))

        fig, ax = plt.subplots()
        markers, caps, bars = ax.errorbar(self[col1], self[col2], yerr=yerr,
                                          xerr=xerr, fmt='o', capsize=0,
                                          ecolor='k')
        # loop through bars and caps and set the alpha value
        [bar.set_alpha(0.2) for bar in bars]
        [cap.set_alpha(0.2) for cap in caps]

        if show_SS:
            if 'mass' in col1 and 'radius' in col2:
                rSS = [d/2 for d in diam_solar_system]
                mSS = [m for m in mass_solar_system]
                if self.units == 'jup':
                    Rjup = rSS[4]; Mjup = mSS[4]
                    rSS = [r/Rjup for r in rSS]
                    mSS = [m/Rjup for m in mSS]

                elif self.units == 'earth':
                    Rearth = rSS[2]; Mearth = mSS[2]
                    rSS = [r/Rearth for r in rSS]
                    mSS = [m/Mearth for m in mSS]

                ax.plot(mSS, rSS, 'o', ms=10, color='r', alpha=0.2)
                for i, (m, r) in enumerate(zip(mSS, rSS)):
                    ax.text(m, r, init_solar_system[i], fontsize=6,
                            ha='center', va='center')


        logx = 'log' if logx else 'linear'
        logy = 'log' if logy else 'linear'
        ax.set(xscale=logx, yscale=logy)






def read_data(verbose=True):

    def apply_float_to_column(data, key):
        data[key] = [float(v) if v!='' else math.nan for v in data[key]]

    # read the file
    local_file = os.path.join(get_data_dir(), 'exoplanetEU.csv')
    with open(local_file) as csvfile:
        reader = csv.DictReader(csvfile)
        lines = [row for row in reader]

    # lines is a list of (ordered) dicts; transform it to a (ordered) dict of lists
    data = OrderedDict({k: [dic[k] for dic in lines] for k in lines[0]})

    # column labels were read automatically by the csv.DictReader
    labels = list(data.keys())

    # but the first label erroneously includes a "#"
    labels[0] = 'name'
    data['name'] = data.pop('# name')

    nlab, nlin = len(labels), len(lines)
    if verbose:
        print(f'There are {nlab} columns with {nlin} entries each in `exoplanetEU.csv`')

    data = DataDict(**data)
    data.move_to_end('name', last=False) # put this key back at the beginning,
    # just for clarity

    # transform some columns to floats
    for col in float_cols:
        apply_float_to_column(data, col)

    return data


def get_data(verbose=False):
    local_file = os.path.join(get_data_dir(), 'exoplanetEU.csv')

    if not os.path.exists(local_file):
        if verbose:
            print ('Downloading exoplanet.eu data')
        download_data(verbose=verbose)

    age = check_data_age()
    if age > 5:
        if verbose:
            print(
                'Data in `exoplanetEU.csv` is older than 5 days, downloading.')
        download_data(verbose=verbose, throw=False)
    else:
        if verbose:
            print('Data in `exoplanetEU.csv` is recent.')

    data = read_data(verbose=verbose)
    return data


if __name__ == '__main__':
    data = get_data()
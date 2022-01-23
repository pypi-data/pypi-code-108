try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.omfit_path import OMFITpath

import xarray as xr
import pandas as pd

__all__ = ['OMFITmatrix']


class OMFITmatrix(SortedDict, OMFITpath):
    """
    OMFITmatrix leverages both xarray and pandas as an efficient way of storing matrices to file.
    Internally, the data is stored as an xarray.DataArray under self['data'].
    """

    def __init__(self, filename, bin=None, zip=None, **kw):
        r"""
        :param filename: path to file.

        :param bin: def None, filetype is unknown,
                    if True,              NetCDF,
                    if False,             ASCII.

        :param zip: def None, compression is unknown,
                    if False,                switched off,
                    if True,                           on.

        :param \**kw: keywords for OMFITpath.__init__()
        """

        SortedDict.__init__(self)
        OMFITpath.__init__(self, filename, **kw)
        self.OMFITproperties['bin'] = bin
        self.OMFITproperties['zip'] = zip
        self.dynaLoad = True

    def __tree_repr__(self):

        r = 'FILE: %s   (%s' % (os.path.split(self.filename)[1], sizeof_fmt(self.filename, ' '))
        try:
            assert self.OMFITproperties['bin'] is not None
            if self.OMFITproperties['zip']:
                r += ', ' + ('zlibbed' if self.OMFITproperties['bin'] else 'gzipped')
            else:
                r += ', plain'
            r += ' ' + ('NetCDF' if self.OMFITproperties['bin'] else 'ASCII')
        except Exception:
            pass
        r += ')'
        try:
            assert np.shape(self['data'])
            r += '   DATA: ' + 'x'.join(['{:,}'.format(s) for s in np.shape(self['data'])])
        except Exception:
            pass
        return r, []

    @dynaLoad
    def load(self, bin=None, zip=None, xrkw={}, **pdkw):
        r"""
        https://xarray.pydata.org/en/stable/generated/xarray.open_dataarray.html
        https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html

        :param bin: def None, load through xarray first, then through pandas,
                    if True,               xarray only,
                    if False,              pandas only.

        :param zip: def False, compression is switched off,
                    if True,                           on.

        :param    xrkw: keywords for xarray.open_dataarray()

        :param \**pdkw: keywords for pandas.read_csv()

        :return bin, zip: resulting values for binary, zipped.
        """

        # allow creation of empty files
        if not os.path.exists(self.filename) or not os.path.getsize(self.filename):
            self['data'] = None
            return None, None

        # load defaults
        if bin is None:
            bin = self.OMFITproperties['bin']
        if zip is None:
            zip = self.OMFITproperties['zip']

        # read NetCDF through xarray
        try:

            if bin is False:
                raise Exception('binary only')

            xrkw.setdefault('engine', 'netcdf4')
            self['data'] = xr.open_dataarray(self.filename, **xrkw)
            self['data'].values
            self['data'].close()

            bin = True
            try:
                zip = self['data'].encoding['zlib']
            except Exception:
                zip = False

        # read ASCII through pandas
        except Exception as e:

            if bin is True or not np.any([m in repr(e) for m in ['binary only', 'NetCDF: Unknown file format']]):
                raise

            pdkw.setdefault('header', None)
            pdkw.setdefault('delim_whitespace', True)
            pdkw.setdefault('index_col', False)
            pdkw.setdefault('compression', 'gzip' if zip else None)

            self['data'] = xr.DataArray(pd.read_csv(self.filename, **pdkw))

            bin = False
            zip = pdkw['compression'] == 'gzip'

        finally:

            # save defaults
            self.OMFITproperties['bin'] = bin
            self.OMFITproperties['zip'] = zip

        return bin, zip

    @dynaSave
    def save(self, bin=None, zip=None, xrkw={}, **pdkw):
        r"""
        https://xarray.pydata.org/en/stable/generated/xarray.DataArray.to_netcdf.html
        https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_csv.html

        :param bin: def None, save through xarray first, then pandas,
                    if True,               xarray only,
                    if False,              pandas only.

        :param zip: def False, compression is switched off,
                    if True,                           on.

        :param    xrkw: keywords for xarray.to_netcdf()

        :param \**pdkw: keywords for pandas.to_csv()

        :return bin, zip: resulting values for binary, zipped.
        """

        if self.dynaLoad:
            return None, None

        # load defaults
        if bin is None:
            bin = self.OMFITproperties['bin']
        if zip is None:
            zip = self.OMFITproperties['zip']

        # save NetCDF through xarray
        try:

            if bin is False:
                raise Exception('binary only')

            self['data'].encoding = {'zlib': bool(zip), 'shuffle': bool(zip), 'complevel': int(bool(zip))}

            self['data'].to_netcdf(self.filename, **xrkw)
            self['data'].close()

            bin = True

        # save ASCII through pandas
        except Exception as e:

            if bin is True or str(e) != 'binary only':
                raise

            pdkw.setdefault('header', None)
            pdkw.setdefault('sep', ' ')
            pdkw.setdefault('index', False)
            pdkw.setdefault('compression', 'gzip' if zip else None)
            pdkw.setdefault('na_rep', 'nan')

            self['data'].to_pandas().to_csv(self.filename, **pdkw)

            bin = False

        finally:

            # save defaults
            self.OMFITproperties['bin'] = bin
            self.OMFITproperties['zip'] = bool(zip)

        return bin, zip

    def close(self, **kw):
        r"""
        :param \**kw: keywords for self.save()
        """

        if self.dynaLoad:
            return
        self.save(**kw)
        SortedDict.clear(self)
        self.dynaLoad = True

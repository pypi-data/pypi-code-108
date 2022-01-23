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

from omfit_classes import utils_math
from omfit_classes.utils_math import smooth, nu_conv, is_uncertain, get_array_hash, uinterp1d
from omfit_classes.sortedDict import OMFITdataset

import numpy as np
import numbers
from uncertainties import unumpy
import warnings

warnings.filterwarnings('always', category=FutureWarning, message='The Panel class is removed from pandas.*')
import xarray.core.dataset

Dataset = xarray.core.dataset.Dataset
_load = Dataset.load

import xarray.core.dataarray

DataArray = xarray.core.dataarray.DataArray


def exportDataset(data, path, complex_dim='i', *args, **kw):
    r"""
    Method for saving xarray Dataset to NetCDF, with support for boolean, uncertain, and complex data
    Also, attributes support OMFITexpressions, lists, tuples, dicts

    :param data: Dataset object to be saved

    :param path: filename to save NetCDF to

    :param complex_dim: str. Name of extra dimension (0,1) assigned to (real, imag) complex data.

    :param \*args: arguments passed to Dataset.to_netcdf function

    :param \**kw: keyword arguments passed to Dataset.to_netcdf function

    :return: output from Dataset.to_netcdf function

    **ORIGINAL Dataset.to_netcdf DOCUMENTATION**

    """
    from omfit_classes.omfit_base import OMFITexpression, evalExpr

    if os.path.dirname(path) and not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    data = copy.deepcopy(data)

    def clean_attrs(da):
        for k, v in list(da.attrs.items()):
            if '/' in k:
                da.attrs[k.replace('/', '_slash_')] = v
                del da.attrs[k]
                k = k.replace('/', '_slash_')
            if isinstance(v, OMFITexpression):
                v = evalExpr(v)
                da.attrs[k] = v
            if isinstance(v, bool):
                da.attrs[k + '__boolean'] = str(v)
                del da.attrs[k]
            elif isinstance(v, dict):
                da.attrs[k + '__dict'] = repr(v)
                del da.attrs[k]
            elif isinstance(v, list):
                da.attrs[k + '__list'] = repr(v)
                del da.attrs[k]
            elif isinstance(v, tuple):
                da.attrs[k + '__list'] = repr(v)
                del da.attrs[k]
            elif v is None:
                da.attrs[k] = ''
            else:
                try:
                    if is_uncertain(v):
                        da.attrs[k + '__uncertainty'] = unumpy.std_devs(v)
                        da.attrs[k] = unumpy.nominal_values(v)
                    elif np.any(np.atleast_1d(np.iscomplex(v))):
                        da.attrs[k + '__imaginary'] = np.imag(v)
                        da.attrs[k] = np.real(v)
                    elif hasattr(v, 'dtype') and v.dtype == np.complex:  # catches complex array with all 0 imaginary
                        da.attrs[k + '__imaginary'] = np.imag(v)
                        da.attrs[k] = np.real(v)
                except Exception:
                    pass

    # Remove illegal characters from variable names
    for k in list(data.variables.keys()):
        if '/' in k:
            data[k.replace('/', '_slash_')] = data[k]
            del data[k]

    # Deal with boolean and uncertain values
    for k in list(data.variables.keys()):
        clean_attrs(data[k])
        if data[k].values.dtype.name == 'bool':
            data[k + '__boolean'] = data[k].astype('u1')
            del data[k]
        else:
            try:
                if len(data[k].values) and is_uncertain(data[k].values):
                    data[k + '__uncertainty'] = copy.deepcopy(data[k])
                    data[k + '__uncertainty'].values[:] = unumpy.std_devs(data[k + '__uncertainty'].values)
                    data[k].values[:] = unumpy.nominal_values(data[k].values)
            except Exception:
                pass
    clean_attrs(data)

    # Deal with complex values
    ida = DataArray([0, 1], coords={complex_dim: [0, 1]}, dims=(complex_dim,))
    rda = DataArray([1, 0], coords={complex_dim: [0, 1]}, dims=(complex_dim,))
    for k, v in list(data.data_vars.items()):
        if np.any(np.iscomplex(v.values)) or (hasattr(v.values, 'dtype') and v.values.dtype == complex):
            data[k] = v.real * rda + v.imag * ida

    # Use the Dataset.to_netcdf method
    import warnings

    with warnings.catch_warnings():
        import yaml

        if hasattr(yaml, 'YAMLLoadWarning'):
            warnings.filterwarnings('ignore', category=yaml.YAMLLoadWarning)
        return data.to_netcdf(path=path, *args, **kw)


def importDataset(filename_or_obj=None, complex_dim='i', *args, **kw):
    r"""
    Method for loading from xarray Dataset saved as netcdf file, with support for boolean, uncertain, and complex data.
    Also, attributes support OMFITexpressions, lists, tuples, dicts

    :param filename_or_obj: str, file or xarray.backends.*DataStore
        Strings are interpreted as a path to a netCDF file or an OpenDAP URL
        and opened with python-netCDF4, unless the filename ends with .gz, in
        which case the file is gunzipped and opened with scipy.io.netcdf (only
        netCDF3 supported). File-like objects are opened with scipy.io.netcdf
        (only netCDF3 supported).

    :param complex_dim: str, name of length-2 dimension (0,1) containing (real, imag) complex data.

    :param \*args: arguments passed to xarray.open_dataset function

    :param \**kw: keywords arguments passed to xarray.open_dataset function

    :return: xarray Dataset object containing the loaded data

    **ORIGINAL xarray.open_dataset DOCUMENTATION**
    """
    import xarray

    # If appropriate call the original load function
    if not len(args) and not len(kw) and not isinstance(filename_or_obj, str):
        _load(filename_or_obj)
        return

    # automatically close files to avoid OS Error of too many files being open
    if isinstance(filename_or_obj, str) and os.path.isfile(filename_or_obj):
        if (compare_version(xarray.__version__, '0.9.2') >= 0) and (compare_version(xarray.__version__, '0.11.0') < 0):
            kw.setdefault("autoclose", True)

    data = xarray.open_dataset(filename_or_obj, *args, **kw)
    if (compare_version(xarray.__version__, '0.9.2') >= 0) and (compare_version(xarray.__version__, '0.11.0') < 0):
        # Manually trigger loading in view of `autoclose`
        data.load()

    def clean_attrs(da):
        for k, v in list(da.attrs.items()):
            if k.endswith('__list') or k.endswith('__dict') or k.endswith('__tuple'):
                del da.attrs[k]
                k = '__'.join(k.split('__')[:-1])
                da.attrs[k] = eval(v)
            elif k.endswith('__boolean'):
                k = k[: -len('__boolean')]
                da.attrs[k] = bool(v)
                del da.attrs[k + '__boolean']
            elif k.endswith('__uncertainty'):
                k = k[: -len('__uncertainty')]
                da.attrs[k] = unumpy.uarray(da.attrs[k], v)
                del da.attrs[k + '__uncertainty']
            elif k.endswith('__imaginary'):
                k = k[: -len('__imaginary')]
                da.attrs[k] = da.attrs[k] + 1j * da.attrs[k + '__imaginary']
                del da.attrs[k + '__imaginary']
            if '_slash_' in k:
                da.attrs[k.replace('_slash_', '/')] = da.attrs[k]
                del da.attrs[k]

    # Deal with illegal characters in names, boolean, and uncertain values
    for k in list(data.variables.keys()):
        clean_attrs(data[k])
        if k.endswith('__boolean'):
            k = k[: -len('__boolean')]
            data[k] = data[k + '__boolean']
            data[k].values = data[k].values[:].astype(bool)
            del data[k + '__boolean']
        elif k.endswith('__uncertainty'):
            k = k[: -len('__uncertainty')]
            data[k].values = unumpy.uarray(data[k].values[:], data[k + '__uncertainty'].values[:])
            del data[k + '__uncertainty']
    for k in list(data.variables.keys()):
        if '_slash_' in k:
            k = k.replace('_slash_', '/')
            data[k] = data[k.replace('/', '_slash_')]
            del data[k.replace('/', '_slash_')]
    clean_attrs(data)

    # Make a copy to avoid any open files that prevent pickling due to a thread.lock problem
    newset = Dataset()
    newset.attrs = copy.deepcopy(data.attrs)
    for k, v in list(data.data_vars.items()):
        if complex_dim in v.dims:
            newdata = v.loc[{complex_dim: 0}] + 1j * v.loc[{complex_dim: 1}]
            newdata.attrs = v.attrs
            newdata.name = v.name
            newset.update(newdata.to_dataset())
        else:
            newset.update(v.to_dataset())
    data.close()
    data = newset

    # load bytes as strings
    for k, v in data.variables.items():
        if isinstance(v.values, bytes):
            data.assign(**{k: b2s(v.values)})
    for k, v in data.attrs.items():
        data.attrs[k] = b2s(v)

    return data


xarray.core.dataset.Dataset = Dataset
import xarray

importDataset.__doc__ += xarray.open_dataset.__doc__
exportDataset.__doc__ += Dataset.to_netcdf.__doc__
xarray.Dataset = Dataset
from xarray import *

__all__ = [
    'reindex_interp',
    'reindex_conv',
    'split_data',
    'smooth_data',
    'exportDataset',
    'importDataset',
    'OMFITncDataset',
    'OMFITncDynamicDataset',
    'pandas_read_json',
    'DataFrame',
]
if not np.any([('sphinx' in k and not 'sphinxcontrib' in k) for k in sys.modules]):
    __all__.extend(['DataArray', 'Dataset'])

from scipy.interpolate import RegularGridInterpolator


def reindex_interp(data, method='linear', copy=True, interpolate_kws={'fill_value': np.nan}, **indexers):
    r"""Conform this object onto a new set of indexes, filling in
    missing values using interpolation. If only one indexer is specified,
    utils.uinterp1d is used. If more than one indexer is specified,
    utils.URegularGridInterpolator is used.

    :params copy : bool, optional
        If `copy=True`, the returned array's dataset contains only copied
        variables. If `copy=False` and no reindexing is required then
        original variables from this array's dataset are returned.

    :params method : {'linear'}, optional
        Method to use for filling index values in ``indexers`` not found on
        this data array:
        * linear: Linear interpolation between points

    :params interpolate_kws : dict, optional
        Key word arguments passed to either uinterp1d (if len(indexers)==1) or
        URegularGridInterpolator.

    :params \**indexers : dict
        Dictionary with keys given by dimension names and values given by
        arrays of coordinates tick labels. Any mis-matched coordinate values
        will be filled in with NaN, and any mis-matched dimension names will
        simply be ignored.

    :return: Another dataset array, with new coordinates and interpolated data.

    See Also:

    DataArray.reindex_like
    align
    """
    # see if it is already handled
    try:
        ds = data.reindex(method=method, copy=copy, **indexers)
        # xarray method converts complex arrays into object arrays
        if method is None:
            if isinstance(data, Dataset):
                for k in list(data.data_vars.keys()):
                    ds[k] = ds[k].astype(data[k].dtype)
            else:
                ds = ds.astype(data.dtype)
        return ds
    except Exception:
        pass

    # handle Datasets for user's convenience
    if isinstance(data, Dataset):
        ds = data.apply(reindex_interp, keep_attrs=True, method=method, copy=copy, interpolate_kws=interpolate_kws, **indexers)
    elif isinstance(data, DataArray):
        # Reindexing to get the copy doesn't work if the indexers are not in the dims
        if np.all([k not in data.dims for k in list(indexers.keys())]):
            if copy:
                return data.copy()
            return data
        # dumb reindexing to get the new object
        ds = data.reindex(method=None, copy=copy, **indexers)
        # form 1D interpolator
        if len(indexers) == 1:
            akey = list(indexers.keys())[0]
            axis = data.dims.index(akey)
            pts = data[data.dims[axis]]
            values = data.values
            fi = uinterp1d(pts, values, axis=axis, kind=method, copy=copy, **interpolate_kws)
            newpts = indexers[akey]
        # form multi-dimensional interpolator
        else:
            args = np.array([data[k].data for k in data.dims])
            values = data.values
            fi = URegularGridInterpolator(tuple(args), values, method=method, **interpolate_kws)
            newpts = np.array(np.meshgrid(*[ds[k].data for k in ds.dims])).T.reshape(-1, ds.ndim)
        # perform actual interpolation
        ds.values = fi(newpts).reshape(ds.shape)
    else:
        raise TypeError('Input must be DataArray or Dataset')

    return ds


def reindex_conv(data, method='gaussian', copy=True, window_sizes={}, causal=False, interpolate=False, std_dev=2, **indexers):
    r"""Conform this object onto a new set of indexes, filling values along changed dimensions
    using nu_conv on each in the order they are kept in the data object.

    :param copy: bool, optional
        If `copy=True`, the returned array's dataset contains only copied
        variables. If `copy=False` and no reindexing is required then
        original variables from this array's dataset are returned.

    :param method: str/function, optional
        Window function used in nu_conv for filling index values in ``indexers``.

    :param window_sizes: dict, optional
        Window size used in nu_conv along each dimension specified in indexers.
        Note, no convolution is performed on dimensions not explicitly given in indexers.

    :param causal: bool, optional
        Passed to nu_conv, where it forces window function f(x>0)=0.

    :param \**indexers: dict
        Dictionary with keys given by dimension names and values given by
        arrays of coordinate's tick labels. Any mis-matched coordinate values
        will be filled in with NaN, and any mis-matched dimension names will
        simply be ignored.

    :param interpolate: False or number
        Parameter indicating to interpolate data so that there are `interpolate`
        number of data points within a time window

    :param std_dev: str/int.
       Accepted strings are 'propagate' or 'none'. Future options will include 'mean', and 'population'.
       Setting to an integer will convolve the error uncertainties to the std_dev power before taking the std_dev root.

    :return: DataArray
        Another dataset array, with new coordinates and interpolated data.

    See Also:

    DataArray.reindex_like
    align
    """

    # handle Datasets for user's convinience
    if isinstance(data, Dataset):
        ds = data.apply(
            reindex_conv,
            keep_attrs=True,
            method=method,
            copy=copy,
            window_sizes=window_sizes,
            causal=causal,
            interpolate=interpolate,
            std_dev=std_dev,
            **indexers,
        )

    elif isinstance(data, DataArray):
        # Reindexing to get the copy doesn't work if the indexers are not in the dims
        if np.all([k not in data.dims for k in list(indexers.keys())]):
            if copy:
                return data.copy()
            return data
        # dumb reindexing to get the new object
        ds = data.reindex(method=None, copy=copy, **indexers)
        values = data.values
        for k, v in list(indexers.items()):
            if k in data.dims:
                axis = data.dims.index(k)
                xi = data[k]
                xo = ds[k]
                ws = window_sizes.get(k, None)
                values = nu_conv(
                    values,
                    xi=data[k].values,
                    xo=ds[k].values,
                    causal=causal,
                    window_function=method,
                    window_size=ws,
                    axis=axis,
                    interpolate=interpolate,
                    std_dev=std_dev,
                )
                ds.values = values
    else:
        raise TypeError('Input must be DataArray or Dataset')

    return ds


def split_data(data, **indexers):
    """
    Split the OMFITdataArray in two wherever the step in a given coordinate
    exceeds the specified limit.

    :param indexers: dict-like with key,value pairs corresponding to dimension labels and step size.

    Example:

    >> dat = OMFITdataArray([0.074,-0.69,0.32,-0.12,0.14],coords=[[1,2,5,6,7],dims=['time'],name='random_data')
    >> dats=dat.split(time=2)])
    >> print(dats)

    """
    coords = SortedDict(indexers)
    k = list(coords.keys())[0]
    v = coords.pop(k)
    newdata = []

    start = 0
    for i, d in enumerate(np.diff(data[k])):
        if d > v:
            temp = data.isel(**{k: slice(start, i + 1)})
            if coords:
                temp = temp.split(coords)
            newdata.append(temp)
            start = i + 1
    temp = data.isel(**{k: slice(start, i + 1)})
    if coords:
        temp = temp.split(coords)
    newdata.append(temp)

    return newdata


def smooth_data(data, window_size=11, window_function='hanning', axis=0):
    """
    One dimensional smoothing. Every projection of the DataArray values
    in the specified dimension is passed to the OMFIT nu_conv smoothing function.

    :param axis: Axis along which 1D smoothing is applied.
    :type axis: int,str (if data is DataArray or Dataset)

    Documentation for the smooth function is below.

    """
    if isinstance(data, Dataset):
        ds = data.apply(smooth, keep_attrs=True, axis=axis, window_size=window_size, window=window_function)
    else:
        if isinstance(axis, str):
            if axis in data.dims:
                axis = list(data.dims).index(axis)
            else:
                raise ValueError('{dim} not in dims {dims}'.format(dim=dim, dims=data.dims))
        akey = data.dims[axis]
        x = data[akey]
        # reorder args so y (data) is first
        def afun(*args, **kwargs):
            args = list(args)
            args.insert(0, args.pop(1))
            return nu_conv(*args, **kwargs)

        ds = apply_along_axis(afun, axis, data, x, x, window_size, window_function=window_function)

    return ds


smooth_data.__doc__ += utils_math.nu_conv.__doc__


class OMFITncDataset(OMFITobject, OMFITdataset):
    """
    Class that merges the power of Datasets with OMFIT dynamic loading of objects
    """

    def __init__(self, filename, lock=False, exportDataset_kw={}, data_vars=None, coords=None, attrs=None, **kw):
        r"""
        :param filename: Path to file

        :param lock: Prevent in memory changes to the DataArray entries contained

        :param exportDataset_kw: dictionary passed to exportDataset on save

        :param data_vars: see xarray.Dataset

        :param coords: see xarray.Dataset

        :param attrs: see xarray.Dataset

        :param \**kw: arguments passed to OMFITobject
        """
        if exportDataset_kw:
            kw['exportDataset_kw'] = exportDataset_kw
        OMFITobject.__init__(self, filename, **kw)
        self.lock = lock
        if data_vars or coords or attrs:
            if not (os.stat(self.filename).st_size):
                self.dynaLoad = False
            else:
                raise ValueError('Cannot specify `filename` with data and `data_vars`, or `coords` or `attrs` at the same time')
        else:
            self.dynaLoad = True
        OMFITdataset.__init__(self, data_vars=data_vars, coords=coords, attrs=attrs)
        self._loaded_hash = hash(())
        self._dynamic_keys = []

    def __str__(self):
        return "File {:}\n{:}".format(self.filename, str(self.to_dataset()))

    def set_lock(self, lock=True):
        """Make all the DataArrays immutable and disable inplace updates"""
        self.lock = lock
        # lock/unlock all the array data and attributes
        for k, v in self.variables.items():
            # assumes all values are DataArrays
            v.values.flags.writeable = not lock

    def __hash__(self):
        """
        Return an hash representing the current state of the data
        """
        hashes = [hash(frozenset(list(self._dataset.attrs.items())))]  # assumes attrs is not nested (i think the netcdf does too)
        for k, v in self.variables.items():
            hashes.append(get_array_hash(v.values))  # assumes all items are DataArrays
            hashes.append(hash(frozenset(list(v.attrs.items()))))
        return hash(tuple(hashes))

    @dynaLoad
    def load(self):
        """
        Loads the netcdf into memory using the importDataset function.
        """
        # To speedup the saving, we calculate a hash of the data at load time
        # so that we can verify if the data ever changed, and if not then we do not
        # need to save from the OMFIT tree to NetCDF, with great speedup benefit

        lock = self.lock
        self.set_lock(False)

        data = Dataset()
        if len(self.filename) and os.path.exists(self.filename) and os.stat(self.filename).st_size:
            data = importDataset(self.filename)
        self._dataset.update(data)
        self._dataset.attrs = data.attrs

        # save a small memory footprint record of what things looked like on loading
        self._loaded_hash = self.__hash__()

        # let decorated methods know it doesn't need to be (re)loaded
        self.dynaLoad = False

        # make values immutable if was originally locked
        self.set_lock(lock)

    def _check_need_to_save(self):
        """
        Determine if the data has changed and the file needs to be re-written.

        :return: bool. True if data has changed in some way since loading or if filename changed.
        """
        # check if file path has changed
        if not (len(self.link) and os.path.exists(self.link) and os.stat(self.link).st_size):
            return True
        elif not self.__hash__() == self._loaded_hash:
            # check if any of the keys, values or attrs changed
            return True

        return False

    @dynaSave
    def save(self, force_write=False, **kw):
        r"""
        Saves file using system move and copy commands if data in memory is unchanged,
        and the exportDataset function if it has changed.

        Saving NetCDF files takes much longer than loading them. Since 99% of the times NetCDF files are not edited
        but just read, it makes sense to check if any changes was made before re-saving the same file from scratch.
        If the files has not changed, than one can just copy the "old" file with a system copy.

        :param force_write: bool. Forces the (re)writing of the file, even if the data is unchanged.

        :param \**kw: keyword arguments passed to Dataset.to_netcdf function
        """
        changed = self._check_need_to_save()
        if force_write or changed:
            if changed:
                printi(
                    'The data has been edited. Saving {:} from scratch... '.format(self.filename.split('/')[-1])
                    + 'if file is big this may take some time.'
                )
            else:
                printi('Saving {:} from scratch... '.format(self.filename.split('/')[-1]) + 'if file is big this may take some time.')

            exportDataset_kw = {}
            if 'exportDataset_kw' in self.OMFITproperties:
                exportDataset_kw = self.OMFITproperties['exportDataset_kw']
            exportDataset_kw.update(kw)

            if os.path.exists(self.filename):
                os.remove(self.filename)
            exportDataset(self.to_dataset(), path=self.filename, **exportDataset_kw)
        else:
            OMFITobject.save(self)

    def __setitem__(self, item, value):
        if self.lock:
            raise ValueError("Cannot setitem of locked OMFITncDataset")
        else:
            return OMFITdataset.__setitem__(self, item, value)


class dynamic_quantity(object):
    def __init__(self, obj, function_name):
        self.obj = obj
        self.function_name = function_name

    def __call__(self, *args, **kw):
        tmp = getattr(self.obj, self.function_name)(*args, **kw)
        self.obj._dynamic_keys.pop(self.obj._dynamic_keys.index(self.function_name))
        return tmp

    def __tree_repr__(self):
        return getattr(self.obj, self.function_name).__doc__.strip().split('\n')[0].strip('.'), []


class OMFITncDynamicDataset(OMFITncDataset):
    def __init__(self, filename, **kw):
        self.update_dynamic_keys(self.__class__)
        OMFITncDataset.__init__(self, filename, **kw)

    def update_dynamic_keys(self, cls):
        self._dynamic_keys[:] = [x[0] for x in [x for x in inspect.getmembers(cls, predicate=inspect.ismethod) if x[0].startswith('calc_')]]

    def __getitem__(self, key):
        """
        Dynamically call methods if quantities are not there
        """
        # show dynamic quantity in the OMFIT GUI tree
        if key in self._dynamic_keys:
            return dynamic_quantity(self, key)
        # evaluate dynamic quantities
        elif 'calc_' + key in self._dynamic_keys:
            getattr(self, 'calc_' + key)()
            self._dynamic_keys.pop(self._dynamic_keys.index('calc_' + key))
        # return entry in the Dataset
        return OMFITncDataset.__getitem__(self, key)

    # def calc_test_fun(self):
    #    """Dummy while we develop"""
    #    self['test_fun'] = DataArray([1, 2, 3], dims=['x'], coords={'x': [1, 2, 3]})

    def keys(self):
        return np.unique(self._dynamic_keys + OMFITncDataset.keys(self))

    def save(self, *args, **kw):
        tmp = copy.deepcopy(self._dynamic_keys)
        try:
            self._dynamic_keys[:] = []
            OMFITncDataset.save(self, *args, **kw)
        finally:
            self._dynamic_keys[:] = tmp


############################################ Monkey-patch xarray plotting

from xarray.plot.plot import _PlotMethods


def _uplot(data, ax=None, **kw):
    """
    Stop uarrays from killing plots.
    Uses uerrorbar for 1d then uses xarray to label everything.
    Uses xarray on nominal values of 2D, etc.

    """
    from matplotlib import pyplot

    if ax is None:
        ax = pyplot.gca()
    rm = False
    da_tmp = data.copy()
    # replace uncertainty objects with their nominal values and use uerrorbar
    if is_uncertain(data.values):
        da_tmp.values = unumpy.nominal_values(data.values)
        if data.ndim == 1:
            x = data[data.dims[0]]
            if len(x) and not isinstance(x.values[0], numbers.Number):
                x = np.arange(len(x))
            from omfit_classes.utils_plot import uerrorbar

            pl = uerrorbar(x, data.values, ax=ax, **kw)
            rm = True
    # replace string coordinates with indices
    for k in da_tmp.dims:
        if len(da_tmp[k].values) and not isinstance(da_tmp[k].values[0], numbers.Number):
            da_tmp.coords[k + '_label'] = da_tmp[k].astype('str')
            da_tmp[k] = np.arange(len(da_tmp[k]))

    # contour plot complex data
    if len(da_tmp.dims) > 1 and np.any(np.iscomplex(da_tmp)):
        da_tmp = np.abs(da_tmp)

    # check if there are any pyplot figures open
    nfig = len(pyplot.get_fignums())

    # use the xarray plotting magic
    l = _PlotMethods(da_tmp.real)(ax=ax, **kw)
    if len(da_tmp.dims) == 1 and np.any(np.iscomplex(da_tmp)):
        kwi = dict(**kw)
        kwi['color'] = l[0].get_color()
        kwi.pop('linestyle', '')
        kwi['ls'] = '--'
        l = _PlotMethods(da_tmp.imag)(ax=ax, **kwi)

    # xarray will have opened a new Figure if we used a FigureNotebook
    if nfig == 0:
        pyplot.close(pyplot.figure(1))

    # for string coordinates: dynamic labeling using the original sting array
    for k in data.dims:
        if len(data[k].values) and not isinstance(data[k].values[0], numbers.Number):
            if ax.get_xlabel() == str(k):

                def myformatter(x, p, da_tmp=da_tmp, data=data, k=k):
                    i = np.abs(da_tmp[k] - x).argmin()
                    return data[k].values[i]

                # if not downsampling the labels, include all the labels right on their index
                if hasattr(ax.xaxis.get_major_locator(), '_nbins') and len(da_tmp[k]) <= ax.xaxis.get_major_locator()._nbins:
                    ax.set_xticks(da_tmp[k].values)
                # enables dynamic labeling for when there are too many values to have a tick at each index
                ax.xaxis._funcformatter = myformatter
                ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(ax.xaxis._funcformatter))
                ax.figure.canvas.draw()
            if ax.get_ylabel() == str(k):

                def myformatter(x, p, da_tmp=da_tmp, data=data, k=k):
                    i = np.abs(da_tmp[k].values - x).argmin()
                    return data[k].values[i]

                # if not downsampling the labels, include all the labels right on their index
                if hasattr(ax.yaxis.get_major_locator(), '_nbins') and len(da_tmp[k]) <= ax.yaxis.get_major_locator()._nbins:
                    ax.set_yticks(da_tmp[k].values)
                # enables dynamic labeling for when there are too many values to have a tick at each index
                ax.yaxis._funcformatter = myformatter
                ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(ax.yaxis._funcformatter))
                ax.figure.canvas.draw()

    # remove the xarray line on top of uerrorbar if necessary (used xarray for labeling etc.)
    if rm:
        ax.lines.pop()
    else:
        pl = l
    return pl


_uplot.__doc__ = DataArray.plot.__doc__
DataArray.plot = _uplot

############################################

from pandas import read_json as pandas_read_json
from pandas import DataFrame

############################################
if '__main__' == __name__:
    test_classes_main_header()

    from omfit_classes.omfit_base import OMFITexpression, evalExpr
    import numpy as np

    filename = OMFITsrc + '/../samples/TS.nc'
    nc = importDataset(filename)

    # behaviour breaks between xarray 0.13.0 and 0.14.0
    nc['n_e'].data = np.zeros(nc['n_e'].data.shape)
    nc['n_e'].reset_coords(['ELM_phase', 'ELM_until_next', 'ELM_since_last', 'subsystem'], drop=True)
    nc['n_e'] *= 2
    assert np.all(~np.isnan(nc['n_e'].data))

    nc['n_e'].attrs['shot'] = OMFITexpression('12345')

    import pickle

    pickle.dumps(nc)

    tmp_dir = tempfile.mkdtemp()
    exportDataset(nc, '/%s/export_dataset.nc' % tmp_dir)
    os.system('rm -rf %s' % tmp_dir)

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

from omfit_classes.utils_math import is_uncertain

import numpy as np

with warnings.catch_warnings():
    # Have to trap this warning here to allow import outside of framework
    warnings.filterwarnings("ignore", category=ImportWarning, message="can't resolve package.*")
    import netCDF4
from uncertainties.unumpy.core import nominal_values, std_devs

__all__ = ['OMFITnc', 'OMFITncData', 'OMFITncDataTmp']


class OMFITnc(SortedDict, OMFITobject):
    r"""
    OMFIT class used to interface with NETCDF files
    This class is based on the netCDF4 library which supports the following file formats:
    'NETCDF4', 'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC', 'NETCDF3_64BIT'
    NOTE: This class constains OMFITncData class objects.

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class and the netCDF4.Dataset() method at loading
    """

    def __init__(self, filename, **kw):
        OMFITobject.__init__(self, filename, **kw)
        SortedDict.__init__(self, sorted=True)
        self.dynaLoad = True
        self.warnIDL = False

    def __setitem__(self, k, v):
        if getattr(self, 'warnIDL', False):
            if re.search(r'\W', k):
                printw(
                    'WARNING: [%s]: Only keys with alphanumeric and underscore '
                    'characters are compatible with IDL NetCDF reader (`readnc`)' % k
                )
            if re.match(r'[\d_]', k) and not k.endswith('__') and not k == '_globals':
                printw('WARNING: [%s]: Object keys must start with a letter to be ' 'compatible with IDL NetCDF reader (`readnc`)' % k)
        SortedDict.__setitem__(self, k, v)

    @dynaLoad
    def load(self, **kw):
        r"""
        Method used to load the content of the file specified in the .filename attribute

        :param \**kw: keyword dictionary which is passed to the netCDF4.Dataset function

        :return: None
        """

        if not (len(self.filename) and os.path.exists(self.filename) and os.stat(self.filename).st_size):
            self['__format__'] = kw.pop('format', 'NETCDF3_CLASSIC')
            self['__dimensions__'] = SortedDict(sorted=True)
            return

        self.clear()

        with netCDF4.Dataset(self.filename, **kw) as f:
            self['__format__'] = f.file_format

            # global dataset attributes
            for uattr in f.ncattrs():
                attr = str(uattr)
                self.setdefault('_globals', SortedDict())
                try:
                    self['_globals'][attr] = ast.literal_eval(repr(b2s(getattr(f, uattr))))
                except Exception:
                    self['_globals'][attr] = getattr(f, uattr)

            # load the dimensions
            self["__dimensions__"] = SortedDict(sorted=True)
            for udim in list(f.dimensions.keys()):
                dim = str(udim)
                self["__dimensions__"][dim] = f.dimensions[udim].__len__()

            # variables
            for uvar in f.variables:
                var = str(uvar)
                if '_unc_' in var:
                    continue
                printd(var, topic='NetCDF')
                try:
                    self[var] = OMFITncData(variable=uvar, filename=self.filename)
                    self[var].dynaLoad = False
                    self[var]['__dimensions__'] = tuple(map(str, f.variables[uvar].dimensions))
                    for attribute in f.variables[uvar].ncattrs():
                        self[var][b2s(attribute)] = f.variables[uvar].getncattr(attribute)
                    self[var]['__dtype__'] = f.variables[uvar].dtype
                    self[var]['__varid__'] = f.variables[uvar]._varid
                    self[var].dynaLoad = True
                except Exception as _excp:
                    self[var] = OMFITncData()
                    self[var]['data'] = '>> error in OMFIT during load << ' + repr(_excp)
                    warnings.warn('Variable ' + var + ' in file ' + self.filename + ' could not be loaded: %s' % repr(_excp))

            self.warnIDL = True

    def _check_need_to_save(self):
        """
        Saving NetCDF files takes much longer than loading them. Since 99% of the times NetCDF files are not edited
        but just read, it makes sense to check if any changes was made before re-saving the same file from scratch.
        If the files has not changed, than one can just copy the "old" file with a system copy.

        :return:
            * 0 if data in the file is identical

            * 1 if some variables have been deleted

            * -1 if data in the file has been edited
        """
        if not (len(self.link) and os.path.exists(self.link) and os.stat(self.link).st_size):
            return 1

        else:
            printd('old file exists', topic='NetCDF')

            f = netCDF4.Dataset(self.link)

            # dimensions
            for udim in list(f.dimensions.keys()):
                dim = str(udim)
                if self["__dimensions__"][dim] != f.dimensions[udim].__len__():
                    printi(dim + ' was modified')
                    return 1
            printd('ok dimensions', topic='NetCDF')

            # globals
            A = set(self.get('_globals', SortedDict()).keys())
            B = set(f.ncattrs())
            if len(A) > len(B):
                printd('Globals were added', topic='NetCDF')
                return 1
            if len(A) < len(B):
                printd('Globals were deleted', topic='NetCDF')
                return 1
            if len(A.difference(B)):
                printd('Global names were edited', topic='NetCDF')
                return 1
            if len(B.difference(A)):
                printd('Global names were edited', topic='NetCDF')
                return 1
            printd('ok number of globals', topic='NetCDF')

            for uattr in f.ncattrs():
                attr = str(uattr)
                try:
                    value = ast.literal_eval(repr(getattr(f, uattr)))
                except Exception:
                    value = getattr(f, uattr)
                if np.array(np.array(value) != np.array(self['_globals'][attr])).any():
                    printd('Gloabl ' + attr + ' was modified', topic='NetCDF')
                    return 1
            printd('ok globals', topic='NetCDF')

            # what variables
            A = set([k for k in self.keys(filter=hide_ptrn) if not isinstance(self[k], OMFITncDataTmp) and k != '_globals'])
            B = set(f.variables.keys())
            if len(A) > len(B):
                printd('Variables were added', topic='NetCDF')
                return 1
            if len(A) < len(B):
                printd('Variables were deleted', topic='NetCDF')
                return 1
            if len(A.difference(B)):
                printd('Variable names were edited', topic='NetCDF')
                return 1
            if len(B.difference(A)):
                printd('Variable names were edited', topic='NetCDF')
                return 1
            printd('ok number of variables', topic='NetCDF')

            # variables content
            for uvar in list(f.variables.keys()):
                var = str(uvar)
                if self[var].dynaLoad:
                    continue
                try:
                    if len(self[var].diff(OMFITncData(f.variables[uvar]))[0]):
                        printd('Variable ' + var + ' was modified', topic='NetCDF')
                        return 1
                except Exception as _excp:
                    printd('Bad variable', topic='NetCDF')
                    return -1
            printd('ok variables', topic='NetCDF')

            return 0

    @dynaSave
    def save(self, zlib=False, complevel=4, shuffle=True, quiet=False, force=False):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        The zlib, complevel, and shuffle keywords are passed on to the createVariable method.

        :param zlib: default False, switch on netCDF compression.

        :param complevel: default 4, compression level (1=fastest, 9=slowest).

        :param shuffle: default True, shuffle data.

        :param quiet: default False, suppress output to the console.

        :param force: default False, force save from scratch/as new file.

        :return: None
        """
        if (not self._check_need_to_save()) and (not force):
            OMFITobject.save(self)
            return

        if not quiet:
            printi('The data in the NetCDF file has been edited. Saving from scratch... if file is big this may take some time.')
            printi('Zlib: %s   complevel: %s  shuffle: %s' % (zlib, complevel, shuffle))

        # make sure to load the entire file before saving
        for var in list(self.keys()):
            if isinstance(self[var], OMFITncDataTmp) or not isinstance(self[var], OMFITncData):
                continue
            uvar = str(var)

            if self[var].dynaLoad:
                self[var].load()
                self[var].dynaLoad = False

        # start the actual saving
        f = netCDF4.Dataset(self.filename, 'w', format=self['__format__'])

        # dimensions
        for dim in self['__dimensions__']:
            f.createDimension(dim, self['__dimensions__'][dim])

        # global dataset attributes
        if '_globals' in list(self.keys()):
            for attr in self['_globals']:
                uattr = str(attr)
                setattr(f, uattr, self['_globals'][attr])
        # To properly track uncertainties, the actual fundamental uncertainties must be tracked
        # as well as the derivatives of each variable with respect to those uncertainties
        unc_vars = {}
        # variables
        for var in list(self.keys()):
            if isinstance(self[var], OMFITncDataTmp) or not isinstance(self[var], OMFITncData):
                continue
            uvar = str(var)

            # handle int64
            if isinstance(np.atleast_1d(self[var]['data'])[0], np.int64):
                self[var]['data'] = np.int32(self[var]['data'])

            if self[var]['__dtype__'] is None:
                try:
                    self[var]['__dtype__'] = np.atleast_1d(nominal_values(self[var]['data'])).dtype
                except ValueError:
                    self[var]['__dtype__'] = np.atleast_1d(self[var]['data']).dtype

            if '__dimensions__' not in self[var] or self[var]['__dimensions__'] is None:
                shp = []
                if np.iterable(self[var]['data']):
                    tmp = np.array(self[var]['data'])  # to make it into an array
                    shp0 = list(tmp.shape)  # shape of the array
                    if self[var]['__dtype__'].name.lower().startswith('s'):  # strings have one extra dimension
                        shp0 += [max(list(map(lambda x: len(x), tmp.flatten())))]
                    for dim in shp0:
                        if 'OMFIT_size_' + str(dim) not in self['__dimensions__']:
                            f.createDimension('OMFIT_size_' + str(dim), dim)
                            self['__dimensions__']['OMFIT_size_' + str(dim)] = dim
                        shp.append('OMFIT_size_' + str(dim))
                self[var]['__dimensions__'] = tuple(shp)

            is_unc = is_uncertain(self[var]['data'])
            if uvar not in list(f.variables.keys()):
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', UserWarning)  # Avoids endian-ness warnings
                    if self[var]['__dtype__'].name.lower().startswith('s'):
                        f.createVariable(uvar, 'S1', self[var]['__dimensions__'])
                    else:
                        f.createVariable(
                            uvar, self[var]['__dtype__'], self[var]['__dimensions__'], zlib=zlib, complevel=complevel, shuffle=shuffle
                        )
            if is_unc and np.iterable(self[var]['data']):
                printd('%s has uncertainties' % uvar)
                unc_vars = set()
                for unc in self[var]['data']:
                    if not hasattr(unc, 'derivatives'):
                        continue
                    unc_vars |= set(unc.derivatives.keys())
                if len(unc_vars):
                    f.variables[uvar].setncattr('has_unc', 1)
                for unc_var in unc_vars:
                    unc_var_ = repr(abs(unc_var._std_dev))
                    if unc_var_ not in list(f.variables.keys()):
                        f.createVariable(unc_var_, float)
                        f.variables[unc_var_][:] = unc_var._std_dev
                    from uncertainties.unumpy.core import array_derivative

                    var_unc_comp = '%s_unc_%s' % (var, unc_var_)
                    printd(var_unc_comp)
                    if var_unc_comp not in list(f.variables.keys()):
                        f.createVariable(var_unc_comp, self[var]['__dtype__'], self[var]['__dimensions__'])
                        f.variables[var_unc_comp][:] = array_derivative(self[var]['data'], unc_var)
                var_unc_tot = '%s_unc_tot' % var
                f.createVariable(var_unc_tot, self[var]['__dtype__'], self[var]['__dimensions__'])
                f.variables[var_unc_tot][:] = std_devs(self[var]['data'])
            tmp = self[var]['data']
            if isinstance(tmp, str):
                tmp = list(tmp)
                f.variables[uvar][:] = tmp
            elif self[var]['__dtype__'].name.lower()[0] in ['s', 'b']:
                if len(np.shape(tmp)) == 0:
                    tmp = [list(str(tmp))]
                else:
                    tmp = list(map(list, tmp))
                for k, item in enumerate(tmp):
                    tmp[k] = tmp[k] + ([''] * (self['__dimensions__'][self[var]['__dimensions__'][-1]] - len(item)))
                f.variables[uvar][:] = tmp
            else:
                try:
                    f.variables[uvar][:] = nominal_values(tmp)
                except Exception:
                    printe(var, self[var])
                    raise

            for attribute in self[var]:
                if not re.match(hide_ptrn, attribute) and attribute not in ['data', '_FillValue']:
                    f.variables[uvar].setncattr(attribute, self[var][attribute])
        f.close()

        # update the link so that next time around the files are identical and we can skip the saving
        self.link = self.filename


class OMFITncData(SortedDict):
    """
    Class which takes care of converting netCDF variables into SortedDict to be used in OMFIT
    OMFITncData object are intended to be contained in OMFITnc objects

    :param variable:  * if  None then returns
                      * if a netCDF4.Variable object then data is read from that variable
                      * if anything else, this is used as the data
                      * if a string and `filename` is set then this is the name of the variable to read from the file

    :param dimension: * Not used if variable is a netCDF4.Variable object or None
                      * If None, then the dimension of the variable is automatically set
                      * If not None sets the dimension of the variable
                      * Ignored if `filename` is set

    :param dtype: * Not used if variable is a netCDF4.Variable object or None
                  * If None, then the data type of the variable is automatically set
                  * If not None sets the data type of the variable
                  * Ignored if `filename` is set

    :param filename: * this is the filename from which variables will be read
                     * if None then no dynamic loading

    """

    def __init__(self, variable=None, dimension=None, varid=None, dtype=None, filename=None):
        SortedDict.__init__(self)
        self['__dimensions__'] = dimension
        self['__dtype__'] = dtype
        self['__varid__'] = varid
        self._filename = None
        self._attributes = {}
        if filename is not None and isinstance(variable, str):
            self._variable = variable
            self._filename = filename
            self.dynaLoad = True
        else:
            self.load(variable=variable, dimension=dimension, dtype=dtype)

    @dynaLoad
    def load(self, variable=None, dimension=None, dtype=None):
        try:
            f = None
            if self._filename is not None and isinstance(self._variable, str):
                f = netCDF4.Dataset(self._filename)
                variable = f.variables[self._variable]

            if variable is None:
                return

            elif isinstance(variable, netCDF4.Variable):
                variable.set_auto_maskandscale(False)
                try:
                    if isinstance(variable['__dtype__'], type) and issubclass(variable['__dtype__'], str):
                        self['data'] = variable.getValue()
                    else:
                        self['data'] = variable.getValue()[0]
                except Exception:
                    self['data'] = variable[:]

                for attribute in variable.ncattrs():
                    printd(b2s(attribute), topic='NetCDF')
                    self[b2s(attribute)] = variable.getncattr(attribute)

                # Take care of adding back in uncertainties
                if 'has_unc' in self and self['has_unc'] and f is not None:
                    unc_val = self['data']
                    var_str = self._variable
                    for var in list(f.variables.keys()):
                        if not var.startswith('%s_unc_' % var_str):
                            continue
                        unc_var_ = var.split('_')[-1]
                        if unc_var_ == 'tot':
                            continue
                        unc_var = ufloat_fromstr('0+/-%s' % unc_var_)
                        unc_val = unc_val + f.variables[var][:] * unc_var
                    self['data'] = unc_val

                self['__dimensions__'] = tuple(map(str, variable.dimensions))
                self['__dtype__'] = variable.dtype
                self['__varid__'] = variable._varid

                # convert strings
                if isinstance(self['__dtype__'], type) and issubclass(self['__dtype__'], str):
                    pass
                elif self['__dtype__'].name.lower()[0] in ['s', 'b']:
                    if self['__dtype__'].name.lower()[0] == 'b':
                        self['data'] = self['data'].astype(str)
                    stLen = self['data'].shape[-1]
                    tmp = np.reshape(self['data'], (-1, stLen)).tolist()
                    for k, string in enumerate(tmp):
                        tmp[k] = ''.join(string)
                    self['data'] = np.reshape(np.array(tmp), self['data'].shape[:-1])

            else:
                self['data'] = variable

                if isinstance(dimension, tuple):
                    self['__dimensions__'] = dimension
                else:
                    self['__dimensions__'] = None
                if dtype is not None:
                    self['__dtype__'] = dtype
                else:
                    self['__dtype__'] = None

        finally:
            if f is not None:
                f.close()

    def __tree_repr__(self):
        dynaStatus = self.dynaLoad
        self.dynaLoad = False
        tmp = None
        if 'long_name' in self:
            tmp = self['long_name']
        elif 'definition' in self:
            tmp = self['definition']
        elif 'description' in self:
            tmp = self['description']
        if tmp is not None:
            tmp = tmp.strip()
            if 'units' in self and len(self['units'].strip()):
                tmp += ' [' + self['units'].strip() + ']'
            if '__dimensions__' in self and self['__dimensions__'] is not None and len(self['__dimensions__']):
                tmp += ' (' + ','.join(self['__dimensions__']) + ')'
            values = tmp
        else:
            values = self.keys(filter=hide_ptrn)
        self.dynaLoad = dynaStatus
        return values, []


class OMFITncDataTmp(OMFITncData):
    """
    Same class as OMFITncData but this type of object
    will not be saved into the NetCDF file. This is useful
    if one wants to create "shadow" NetCDF variables into OMFIT
    without altering the original NetCDF file.
    """

    pass


############################################
if '__main__' == __name__:
    test_classes_main_header()

    tmp = OMFITnc(OMFITsrc + '/../samples/statefile_1.860000E+00.nc')
    tmp.load()

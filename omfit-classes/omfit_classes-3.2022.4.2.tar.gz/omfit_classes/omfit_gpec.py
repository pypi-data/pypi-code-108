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

from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.omfit_data import Dataset, DataArray, OMFITncDataset
from omfit_classes.utils_math import interp1e

from types import MethodType
from io import StringIO
import numpy as np
from scipy.io import FortranFile

__all__ = ['OMFITGPECbin', 'OMFITGPECascii', 'OMFITGPECnc', 'OMFITldpi']

########################################################### NetCDF files


def lock_items(f):
    """Decorator that should lock up the dictionary-like class after the method is called"""

    @functools.wraps(f)
    def lock(self, *args, **kwargs):
        """Calls the function then modified __setitem__ and __getitem__ to prevent editing keys/values."""
        # first call the function (like load)
        result = f(self, *args, **kwargs)
        # now that we have a good tree representation of the file, don't let anyone edit it
        def locked(self, *args, **kwargs):
            """This is over riden so GPEC outputs cannot be modified directly"""
            raise AssertionError("GPEC output cannot be modified in OMFIT. \n" + "Use to_dataset to get an in-memory copy of the data")

        self.__setitem__ = MethodType(locked, self)

        def jail_break(obj, key):
            """This should copy all the items when they are requested so they cannot be modified in place"""
            return copy.deepcopy(dict.__getitem__(obj, key))

        self.__getitem__ = MethodType(jail_break, self)

        return result

    return lock


class OMFITGPECnc(OMFITncDataset):
    """
    Child of OMFITncDataset, which is a hybrid xarray Dataset and OMFIT SortedDict object.
    This one updates the GPEC naming conventions when it is loaded, and locks the data
    by default so users don't change the code outputs.

    """

    def __init__(self, filename, lock=True, update_naming_conventions=True, export_kw={}, **kwargs):
        self._update_names = update_naming_conventions
        OMFITncDataset.__init__(self, filename, lock=lock, export_kw=export_kw, **kwargs)

    @dynaLoad
    def load(self):
        """
        Loads the netcdf file using the omfit_data importDataset function,
        then distributes those keys and attributes to this class.

        :return:
        """
        OMFITncDataset.load(self)

        # this overrides the lock
        lock = self.lock
        self.set_lock(False)
        if self._update_names:
            try:
                self = self._update_naming_conventions()
            except ValueError as err:
                printe(err)
            self._update_names = False  # stop it from re-updating
        self.set_lock(lock)

    def _update_naming_conventions(self, version=None):
        """

        Update the naming conventions in a dataset to the latest conventions.

        Use this to avoid lots of if statements in cross-checking versions.

        :param dataset:
        :param version: str. Override version attribute.
        :return:

        """
        # set to operate on
        newset = copy.deepcopy(self)

        # version number
        if version is None:
            version = self.attrs.get('version', None)
            if version is None:
                raise ValueError('Must specify version')
        if 'version' in version:
            version = version.split()[-1]  # just the major.minor.patch numbers
        else:
            version = version[1:].split('-')[0]  # newer git tag version label
        version = np.sum(np.array([1, 0.1, 0.001]) * list(map(np.float, version.split('.'))))  # float representation

        translator = OrderedDict()
        if version < 0.3:
            # profile output changes
            translator['xi_psi1'] = 'xigradpsi_dpsi'
            translator['xi_psi'] = 'xigradpsi'
            translator['xi_alpha'] = 'xigradalpha'
        if version < 0.5:
            # control output changes
            translator['b_xn'] = 'b_n_x_fun'
            translator['b_n'] = 'b_n_fun'
            translator['xi_xn'] = 'xi_n_x_fun'
            translator['xi_n'] = 'xi_n_fun'
            translator['dphi'] = 'delta_phi'
            translator['b_xnm'] = 'b_n_x'
            translator['b_nm'] = 'b_n'
            translator['xi_xnm'] = 'xi_n_x'
            translator['xi_nm'] = 'xi_n'
            translator['Phi_X'] = 'Phi_x'
            translator['Phi_EX'] = 'Phi_xe'
            translator['Phi_T'] = 'Phi'
            translator['Phi_ET'] = 'Phi_e'
            translator['X_EVT'] = 'X_eigenvalue'
            translator['X_EDT'] = 'X_eigenvector'
            translator['W_EVX'] = 'W_xe_eigenvalue'
            translator['R_EVX'] = 'R_xe_eigenvalue'
            translator['P_EVX'] = 'P_xe_eigenvalue'
            translator['C_EVX'] = 'C_xe_eigenvalue'
            translator['W_EDX'] = 'W_xe_eigenvector'
            translator['R_EDX'] = 'R_xe_eigenvector'
            translator['P_EDX'] = 'P_xe_eigenvector'
            translator['C_EDX'] = 'C_xe_eigenvector'
            translator['W_EVX_energyv'] = 'W_xe_energyv'
            translator['W_EVX_energys'] = 'W_xe_energys'
            translator['W_EVX_energyp'] = 'W_xe_energyp'
            translator['R_EVX_energyv'] = 'R_xe_energyv'
            translator['R_EVX_energys'] = 'R_xe_energys'
            translator['R_EVX_energyp'] = 'R_xe_energyp'
            translator['W_EVX_A'] = 'W_xe_amp'
            translator['R_EVX_RL'] = 'R_xe_RL'
            translator['O_XT'] = 'O_Xxi_n'
            translator['O_WX'] = 'O_WPhi_xe'
            translator['O_PX'] = 'O_PPhi_xe'
            translator['O_RX'] = 'O_RPhi_xe'
            # profile output changes
            translator['derxi_m_contrapsi'] = 'xigradpsi_dpsi'
            translator['xi_m_contrapsi'] = 'xigradpsi'
            translator['xi_m_contraalpha'] = 'xigradalpha'
            # cylindrical output changes
            translator['b_r_plas'] = 'b_r_plasma'
            translator['b_z_plas'] = 'b_z_plasma'
            translator['b_t_plas'] = 'b_t_plasma'
        if version < 1.4:
            # profile and control netcdf coordinate name changes
            translator['psi_n_rat'] = 'psi_n_rational'
            translator['q_rat'] = 'q_rational'
            translator['m_rat'] = 'm_rational'
            translator['dqdpsi_n_rat'] = 'dqdpsi_n_rational'
        # do this in an explicit loop because some names already exist and need to get replaced in order
        for okey, nkey in list(translator.items()):
            if okey in newset:
                newset = newset.rename({okey: nkey})

        return newset


########################################################### ASCII files

# better label recognition using genfromtxt
for c in '^|<>/':
    if c in np.lib._iotools.NameValidator.defaultdeletechars:
        np.lib._iotools.NameValidator.defaultdeletechars.remove(c)


def structured_array_to_dataset(fromtxt, dims=(), excludedims=(), attrs={}):
    """
    Takes structured array from np.genfromtxt, and creates Dataset
    with dependent/independent data going to dims/data_vars.

    :param fromtxt: structured array.
    :param dims: list. Use these as dimension variable keys.
    :param excludedims: list. Do not use these as dimension variable keys.
    :param attrs: dict. Dataset attributes.

    """
    dataset = Dataset()
    names = list(fromtxt.dtype.names)
    l = len(fromtxt)

    # Set independent/dependent variables (max 3D,min 3pt grid)
    potxnames = []
    for name in names:
        if name not in excludedims:
            potxnames.append(name)
        if len(potxnames) >= 3:
            break
    # by default, don't use psi and q as independent dims (but they are often listed next to each other)
    if np.any([k.startswith('psi') for k in potxnames]) and 'q' in potxnames:
        potxnames.remove('q')
    # catch r,z ("fun") descriptions of the control surface
    if set(potxnames) == set(['r', 'z', 'theta']):
        potxnames = ['theta', 'r', 'z']
    if set(potxnames) == set(['R(m)', 'Z(m)', 'theta(rad)']):  # wall_geom.out
        potxnames = ['theta(rad)']
    # catch crit.out, which has insufficient accuracy in psi so it looks repeated
    if len(potxnames) and potxnames[0] == 'is':
        potxnames = potxnames[:1]
    if not np.all([name in names for name in dims]):
        print('WARNING: Requested axes not available. Using default left column(s).')
    if dims and np.all([name in names for name in dims]):
        nd = len(dims)
        potxnames = list(dims)
    else:
        nd = 1
        npot = len(potxnames)
        if npot > 1 and len(set(fromtxt[potxnames[1]])) < int(l // 2):
            nd += 1
            if npot > 2 and len(set(fromtxt[potxnames[2]])) < int(l // 3):
                nd += 1
    xnames = potxnames[:nd]
    xcols = np.array([np.array(fromtxt[key]).ravel() for key in xnames])
    datashape = []
    for xkey, xcol in zip(xnames, xcols):
        xset = np.sort(list(set(xcol)))  # ordered set. Presumably the table column repeated values if nd>1
        datashape.append(len(xset))
        dataset[xkey] = DataArray(xset, coords={xkey: xset}, dims=(xkey,))
    if np.product(datashape) != l:  # had repeats in dimension variables! Probably psi to closely packed
        # fall back to a simple indexing scheme
        dataset = Dataset()
        xkey = 'row_index'
        xset = np.arange(l)
        dataset[xkey] = DataArray(xset, coords={xkey: xset}, dims=(xkey,))
        xnames = ['row_index']
        nd = 1
        datashape = [l]
        # raise ValueError(
        #     "The table rows are not fully described by the unique valued dimensions {:}".format(potxnames[:nd]))

    # set the data_vars, allowing for real and imaginary columns
    ynames = [name for name in names if name not in xnames]
    for name in ynames:
        if 'real' in name:
            newname = name.replace('real', '')
            newname = newname.lstrip('(').rstrip(')')
            if not newname:  # the columns just say "real    imag"
                newname = "var_0"
            y = np.reshape(fromtxt[name] + 1j * fromtxt[name.replace('real', 'imag')], datashape)
        elif not 'imag' in name:
            newname = name
            y = np.reshape(fromtxt[name], datashape)
        dataset[newname] = DataArray(y, coords=dataset.coords, dims=xnames)
    dataset.attrs.update(attrs)

    return dataset


def text_to_attrs(txt):
    """Parse text with variables defined using 'name = value' syntax."""
    preamble = txt.split()
    params = []
    names = []
    while preamble.count('='):  # parameter specifications
        idx = preamble.index('=')
        param = preamble[idx + 1]
        name = preamble[idx - 1]
        name.translate({ord(char): '' for char in r'()[]{}\/*-+^%.,:!@#&'})
        if name in names and idx > 1:
            name = ' '.join(preamble[idx - 2 : idx])
            name = name.translate({ord(char): '' for char in r'()[]{}\/*-+^%.,:!@#&'})
        elif name in names:
            for sfx in range(1, 100):
                if name + str(sfx) not in names:
                    name += str(sfx)
                    break
        try:
            params.append((name, float(param.rstrip('.,'))))  # if its a number
        except Exception:
            params.append((name, param))  # if its not a number
        names.append(name)
        preamble.remove(preamble[idx - 1])
        preamble.remove(str(param))
        preamble.remove('=')
    return dict(params)


def ascii_to_dataset(fname, squeeze=False, dims=(), excludedims=('l',), coords=(), maxnumber=999, verbose=False):
    """
    Get the data from any gpec output as a list of python
    class-type objects using np.genfromtxt.

    :param fname: str. Path of gpec output file.
    :param squeeze: bool. True uses the update method to form a single data object from multiple tables.
        str. Concatenate all tables along the specified dimension or attribute.
    :param dims: list. Use these as the independent data.
    :param excludedims: list. Do not use these as the independent data.
    :param maxnumber: int. Reads only first maxnumber of tables.
    :param verbose: bool. Print verbose status messages.

    :returns: list. Class objects for each block of data in the file.

    """
    collection = []
    dcollection = []
    pcollection = []

    with open(fname) as f:
        # Get preamble
        preamble = ''
        lastline = ''
        for lstart, line in enumerate(f):
            try:
                test = float(line.split()[0])
                break
            except Exception:
                preamble += lastline
                lastline = line
        f.seek(0)
        try:  # Simple file : single table
            # data = np.genfromtxt(f,skip_header=lstart-1,names=True,dtype=np.float64)
            raise ValueError  # genfromtxt read pfile (multiple 2-column tables) as one... '\r' bug
            pcollection.append(preamble)
            dcollection.append(data)
        # look through file manually
        except ValueError:
            f.seek(0)
            # clean up messy dcon output formats
            if 'dcon.out' in fname or 'stride.out' in fname:
                lines = f.read()
                lines = lines.replace('mu0 p', 'mu0p')
                lines = lines.replace(' abs ', ' abs')
                lines = lines.replace(' re ', ' real')
                lines = lines.replace(' im ', ' imag')
                lines = lines.replace('*', '')
                lines = lines.replace('q          q1', 'qs        qs1')
                lines = lines.replace('i     re', 'ipert re')
                lines = lines.replace(
                    '   isol  imax   plasma     vacuum     total\n', '   isol  imax   plasma     vacuum realtotal imagtotal\n'
                )
                lines = StringIO(lines).readlines()
            else:
                lines = f.readlines()
            top, bot = 0, 0
            count = 0
            length = len(lines)
            while bot < length and top < (length - 2) and count < maxnumber:
                preamble = ''
                lastline = ''
                for i, line in enumerate(lines[bot:]):
                    try:
                        # Find top defined as start of numbers
                        test = float(line.split()[0])
                        top = bot + i
                        # Throw out single lines of numbers
                        # if not lines[top+1].translate({ord(char): '' for char in ' \n\t\r'}):#=='\n':
                        #    raise ValueError
                        # Find bottom defined by end of numbers
                        for j, bline in enumerate(lines[top:]):
                            try:
                                test = float(bline.split()[0])
                            except Exception:
                                break  # end of numbers
                        # Throw out single lines of numbers
                        if j == 1:
                            # but include them as preamble (DCON one-liners)
                            vals = lines[top]
                            keys = lines[top - 1]
                            if not keys.translate({ord(char): '' for char in ' \n\t'}):  # empty line
                                keys = lines[top - 2]
                            if '=' not in keys and len(keys.split()) == len(vals.split()):
                                for k, v in zip(keys.split(), vals.split()):
                                    preamble += '{:} = {:}\n'.format(k, v)
                            raise ValueError
                        else:
                            bot = top + j + 1
                        break
                    except Exception:
                        preamble += lastline
                        lastline = line
                if line == lines[-1] and line == lastline:
                    break  # end of file without another table

                # include headers
                top -= 1
                if not lines[top].translate({ord(char): '' for char in ' \n\t'}):  # empty line
                    top -= 1
                skipfoot = length - bot
                f.seek(0)
                table = lines[top:bot]
                if '\n' in table:  # empty space
                    table.remove('\n')
                data = np.genfromtxt(StringIO(''.join(table)), names=True, deletechars='?', dtype=np.float64)
                pcollection.append(preamble)
                dcollection.append(data)
                count += 1
        # turn arrays into classes
        for i, (data, preamble) in enumerate(zip(dcollection, pcollection)):
            if verbose:
                printi("Casting table " + str(i + 1) + " into Dataset.")
            attrs = text_to_attrs(preamble)
            ds = structured_array_to_dataset(data, attrs=attrs, dims=dims, excludedims=excludedims)
            try:
                ds = structured_array_to_dataset(data, attrs=attrs, dims=dims, excludedims=excludedims)
            except ValueError as err:
                # sometimes diagnostics of splines used repeating ix values in the first column
                # this is confusing when sorting out the dims... try ignoring that column when looking for dims
                printe(str(err))
                baddim = str(err).split("'")[-2]
                excludedims = list(excludedims) + [baddim]
                ds = structured_array_to_dataset(data, attrs=attrs, dims=dims, excludedims=excludedims)
            ds = ds.set_coords(set(coords).intersection(set(ds.data_vars.keys())))

            collection.append(ds)

    # force all to a single object
    if squeeze:
        if isinstance(squeeze, bool):
            # choose some default squeeze dimensions
            if np.any(['isol' in ds.attrs for ds in collection]):
                squeeze = 'isol'  # common in DCON
            if np.any(['ia' in ds.attrs for ds in collection]):
                squeeze = 'ia'  # used in EQUIL 2d.out
            else:
                if np.any(['mode' in ds.attrs for ds in collection]):
                    squeeze = 'mode'  # common in GPEC
        if isinstance(squeeze, str):
            # This grouping catches cases where one dim of 2D data was split into separate tables,
            # but 1D data for that dim also exists
            index = 0
            lc = len(collection)
            dsq = Dataset()
            for i in range(lc):
                if index >= lc:
                    break
                series2d = []
                for j in range(index, lc):
                    if np.all(list(collection[j].keys()) == list(collection[index].keys())):
                        series2d.append(collection[j])
                        index = j
                index += 1
                # combine the series of similar blocks
                ds2d = combine_datasets(series2d, squeeze)
                # then safely combine that with the rest of the data
                dsq = combine_datasets((dsq, ds2d), squeeze)
        else:
            try:
                dsq = combine_datasets(collection)
            except Exception as err:
                printe("Unable to merge multiple tables found in file, returning only the last one")
                dsq = collection[-1]
        return dsq

    return collection


def combine_datasets(datasets, dim=''):
    """
    Combine multiple datasets, allowing for the concatenating dimension to have been
    written in the headers of multiple tables (essentially writing multi-dimensional data
    as a series of 1D tables) and thus appearing in the dataset attributes.

    :param datasets: list. Datasets to be combined into one.
    :param dim: str. Dimension along which to concatenate. Can be a common attribute.
    :return:

    """
    new = Dataset()
    for i, d in enumerate(datasets):
        # allow a new dimension specified in each tables preamble
        if dim in d.attrs:
            x = np.atleast_1d(d.attrs.pop(dim))
            d *= DataArray(np.ones_like(x), coords=[(dim, x)])
        # concat along an existing dimension if necessary
        if i == 0:
            new.update(d)
        elif dim in d.dims and dim in new.dims and not (np.all(d[dim] == new[dim]) and len(d[dim] == new[dim]) > 0):
            new = xarray.concat((new, d), dim, data_vars='minimal')
        else:
            new.update(d)
        new.attrs.update(d.attrs)
    return new


class OMFITGPECascii(OMFITncDataset, OMFITascii):
    """
    This class parses ascii tables in a very general way that catches most of the oddities
    in GPEC output file formatting (mostly inherited from DCON).

    The data is stored as a Dataset in memory but has no save method, so the original
    file is never modified.

    """

    def __init__(self, filename, lock=True, export_kw={}, **kwargs):
        OMFITascii.__init__(self, filename, **kwargs)
        OMFITncDataset.__init__(self, filename, lock=lock, export_kw=export_kw)

    @dynaLoad
    def load(self):
        """
        Load ascii tables into memory.
        """
        try:
            # try to squeeze along the isol dimension, which DCON likes to split into separate tables
            data = ascii_to_dataset(self.filename, squeeze=True)
            # try to put this into a OMFITncDataset type object-Dataset hybrid
            lock = self.lock
            self.set_lock(False)
            self.update(data)
            self.attrs = data.attrs
            self.set_lock(lock)
        except Exception as err:
            printe("WARNING: Could not parse " + self.filename.split('/')[-1])
            # printe(repr(err))
            raise err

        self.dynaLoad = False

    @dynaSave
    def save(self):
        """
        This method can detect if .filename was changed and if so, makes a copy from the original .filename
        (saved in the .link attribute) to the new .filename
        """
        OMFITobject.save(self)


########################################################### Binary Files


def _get_binary_mapping(gpec_home='$GPECHOME'):
    """Get a mapping of all the binary variables that the xdraw application knows"""
    import json

    # list all the files in the draw directory
    files = []
    for k in os.listdir(gpec_home + '/draw'):
        pth = os.path.abspath(gpec_home + '/draw/' + k)
        print(pth)
        if os.path.isfile(pth) and k.endswith('.in'):
            files.append(pth)
    bin_map = {}
    for pth in files:
        with open(pth, 'r') as f:
            lines = f.readlines()
        # find markers
        iname, idstart, idend, iistart, iiend = -1, -1, -1, -1, -1
        for i, l in enumerate(lines):
            if 'filename' in l:
                iname = i + 1
            if l.startswith('independent variable names'):
                iistart = i + 1
            if l.startswith('\n') and iistart > 0 and iiend < 0:
                iiend = i
            if l.startswith('dependent variable names') or l.startswith('variable names'):
                idstart = i + 1
            if l.startswith('\n') and idstart > 0 and idend < 0:
                idend = i
        # parse variable names
        name = lines[iname].split('.')[0]
        vars = ['_'.join(l.split()[1:]).lower() for l in lines[idstart:idend]]
        dims = ['_'.join(l.split()[1:]).lower() for l in lines[iistart:iiend]]
        type_code = lines[0].split()[-1]
        if type_code == 'G':  # 1D "graphs"
            dims = [vars.pop(0)]
        # store in a master map
        bin_map[name] = dict(vars=vars, dims=dims, type=type_code)

    print(json.dumps(bin_map, indent=4))
    return bin_map


bin_mapping = {
    "deltap": {"dims": ["r"], "type": "G", "vars": ["q", "psi", "psi1", "u1", "u2", "log10_ca1", "log10_ca2", "log10_|z|"]},
    "ahb": {
        "dims": ["theta"],
        "type": "G",
        "vars": [
            "re_bn",
            "re_bp",
            "re_bt",
            "im_bn",
            "im_bp",
            "im_bt",
            "theta_hamada",
            "theta_pest",
            "theta_equal_arc",
            "theta_boozer",
            "dtheta_hamada",
            "dtheta_pest",
            "dtheta_equal_arc",
            "dtheta_boozer",
        ],
    },
    "chord": {"dims": ["r"], "type": "G", "vars": ["q", "xi_psi", "b_psi", "xi_norm", "b_norm"]},
    "kwmats": {
        "dims": ["psifac"],
        "type": "G",
        "vars": [
            "real_ak",
            "imag_ak",
            "real_bk",
            "imag_bk",
            "real_ck",
            "imag_ck",
            "real_dk",
            "imag_dk",
            "real_ek",
            "imag_ek",
            "real_hk",
            "imag_hk",
        ],
    },
    "ktmats": {
        "dims": ["psifac"],
        "type": "G",
        "vars": [
            "real_ak",
            "imag_ak",
            "real_bk",
            "imag_bk",
            "real_ck",
            "imag_ck",
            "real_dk",
            "imag_dk",
            "real_ek",
            "imag_ek",
            "real_hk",
            "imag_hk",
        ],
    },
    "xbnormal": {
        "dims": ["psifac"],
        "type": "G",
        "vars": ["real_xi", "imag_xi", "real_b", "imag_b", "real_jac.b.delpsi", "imag_jac.b.delpsi"],
    },
    "metric": {
        "dims": ["psi"],
        "type": "G",
        "vars": [
            "log10_psi",
            "log10_1-psi",
            "log10_ffco1",
            "arg_ffco1",
            "log10_ffco2",
            "arg_ffco2",
            "log10_ffco3",
            "arg_ffco3",
            "log10_ffco4",
            "arg_ffco4",
            "log10_ffco5",
            "arg_ffco5",
            "log10_ffco6",
            "arg_ffco6",
        ],
    },
    "sum2": {"dims": ["q0"], "type": "G", "vars": ["inval", "psifac", "di", "deltap"]},
    "surface": {
        "dims": ["theta"],
        "type": "G",
        "vars": [
            "re_tn",
            "re_tp",
            "re_tt",
            "im_tn",
            "im_tp",
            "im_tt",
            "re_bn",
            "re_bp",
            "re_bt",
            "im_bn",
            "im_bp",
            "im_bt",
            "theta_hamada",
            "theta_pest",
            "theta_equal_arc",
            "theta_boozer",
            "dtheta_hamada",
            "dtheta_pest",
            "dtheta_equal_arc",
            "dtheta_boozer",
        ],
    },
    "metyx": {"dims": ["theta"], "type": "G", "vars": ["j11", "j12", "j13", "j21", "j22", "j23", "j33"]},
    "sol10": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "solutions": {"dims": ["psifac"], "type": "G", "vars": ["rho", "q", "real_xi", "imag_xi", "real_b", "imag_b"]},
    "crit": {"dims": ["psifac"], "type": "G", "vars": ["log_10_psifac", "log_10_(m_-_n_q)", "q", "crit"]},
    "sol+00": {"dims": ["psifac"], "type": "G", "vars": ["logpsi1", "logpsi2", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "ode": {"dims": ["t"], "type": "G", "vars": ["psi", "theta", "zeta", "p_psi", "p_theta", "p_zeta"]},
    "bal1": {"dims": ["theta"], "type": "G", "vars": ["dbdb0", "dbdb1", "dbdb2", "kapw0", "kapw1"]},
    "fixup": {"dims": ["psifac"], "type": "G", "vars": ["log10_psifac", "log10_uration"]},
    ";results/time193/0": {
        "dims": ["theta"],
        "type": "G",
        "vars": [
            "re_bn",
            "re_bp",
            "re_bt",
            "im_bn",
            "im_bp",
            "im_bt",
            "theta_hamada",
            "theta_pest",
            "theta_equal_arc",
            "theta_boozer",
            "dtheta_hamada",
            "dtheta_pest",
            "dtheta_equal_arc",
            "dtheta_boozer",
        ],
    },
    "rzphi": {
        "dims": ["psi"],
        "type": "G",
        "vars": ["log10_psi", "log10_1-psi", "log10_r2", "arg_r2", "log10_eta", "arg_eta", "log10_phi", "arg_phi"],
    },
    "xbtangent": {"dims": ["psifac"], "type": "G", "vars": ["real_xi", "imag_xi", "real_b", "imag_b"]},
    "sol11": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "sol12": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "avec": {"dims": ["psifac"], "type": "G", "vars": ["-phi", "chi", "1/v1^2"]},
    ";results/trial/1": {
        "dims": ["theta"],
        "type": "G",
        "vars": ["re_bnorm", "im_bnorm", "re_xinorm", "im_xinorm", "theta_hamada", "theta_pest", "theta_equal_arc", "theta_boozer"],
    },
    "results/time129v2fixb/0": {
        "dims": ["psifac"],
        "type": "G",
        "vars": ["rho", "f", "mu0_p", "q", "arcsinh_di", "arcsinh_dr", "arcsinh_h", "arcsinh_ca1"],
    },
    "dcon": {"dims": ["psifac"], "type": "G", "vars": ["rho", "f", "mu0_p", "q", "arcsinh_di", "arcsinh_dr", "arcsinh_h", "arcsinh_ca1"]},
    "rz": {"dims": ["theta"], "type": "G", "vars": ["r2", "eta"]},
    "contour": {"dims": ["time", "r", "z"], "type": "M", "vars": ["xi", "b"]},
    "frs": {"dims": ["q0"], "type": "G", "vars": ["rs", "deltap"]},
    "pmodb_2d": {
        "dims": ["time", "r", "z"],
        "type": "M",
        "vars": ["eulerian_re_mod_b", "eulerian_im_mod_b" "lagrangian_re_mod_b", "lagrangian_im_mod_b"],
    },
    "psi_in": {"dims": ["time", "r", "z"], "type": "M", "vars": ["psi"]},
    "prof": {"dims": ["psifac"], "type": "G", "vars": ["rho", "f", "mu0_p", "q"]},
    "fourfit": {
        "dims": ["psi"],
        "type": "G",
        "vars": ["amat_new", "bmat_new", "cmat_new", "dmat_new", "emat_new", "hmat_new", "fmat_new", "kmat_new", "gmat_new"],
    },
    "cyl": {"dims": ["beta0"], "type": "G", "vars": ["q0", "psis", "di", "deltap"]},
    "xbnormal_2d": {"dims": ["time", "r", "z"], "type": "M", "vars": ["re_xi_normal", "im_xi_normal"]},
    "sq_in": {"dims": ["psi"], "type": "G", "vars": ["f", "p", "q", "rho"]},
    "gsec": {"dims": ["time", "r", "z"], "type": "M", "vars": ["flux1", "flux2", "source", "total", "error", "errlog"]},
    "rz_in": {"dims": ["theta"], "type": "G", "vars": ["r", "z"]},
    "fmat": {
        "dims": ["psi"],
        "type": "G",
        "vars": [
            "log_10_psi",
            "log_10_1-psi",
            "log_10_fmat01",
            "arg_fmat01",
            "log_10_fmat02",
            "arg_fmat02",
            "log_10_fmat03",
            "arg_fmat03",
            "log_10_fmat04",
            "arg_fmat04",
            "log_10_fmat05",
            "arg_fmat05",
            "log_10_fmat06",
            "arg_fmat06",
            "log_10_fmat07",
            "arg_fmat07",
            "log_10_fmat08",
            "arg_fmat08",
            "log_10_fmat09",
            "arg_fmat09",
            "log_10_fmat10",
            "arg_fmat10",
            "log_10_fmat11",
            "arg_fmat11",
            "log_10_fmat12",
            "arg_fmat12",
            "log_10_fmat13",
            "arg_fmat13",
        ],
    },
    "pflux_im_2d": {"dims": ["time", "r", "z"], "type": "M", "vars": ["im_perturbed_flux"]},
    "gsei": {"dims": ["psi"], "type": "G", "vars": ["term1", "term2", "totali", "errori", "log10_errori"]},
    "vbnormal": {"dims": ["psifac"], "type": "G", "vars": ["real_jac.b.delpsi", "imag_jac.b.delpsi"]},
    "gmat": {
        "dims": ["psi"],
        "type": "G",
        "vars": [
            "log_10_psi",
            "log_10_1-psi",
            "log_10_gmat01",
            "arg_gmat01",
            "log_10_gmat02",
            "arg_gmat02",
            "log_10_gmat03",
            "arg_gmat03",
            "log_10_gmat04",
            "arg_gmat04",
            "log_10_gmat05",
            "arg_gmat05",
            "log_10_gmat06",
            "arg_gmat06",
            "log_10_gmat07",
            "arg_gmat07",
            "log_10_gmat08",
            "arg_gmat08",
            "log_10_gmat09",
            "arg_gmat09",
            "log_10_gmat10",
            "arg_gmat10",
            "log_10_gmat11",
            "arg_gmat11",
            "log_10_gmat12",
            "arg_gmat12",
            "log_10_gmat13",
            "arg_gmat13",
        ],
    },
    "vbnormal_spectrum": {"dims": ["time", "poloidal_harmonics", "psi"], "type": "M", "vars": ["jac.b.delpsi"]},
    "debug": {"dims": ["psi"], "type": "G", "vars": ["theta", "r", "z", "xi_psi", "b_psi", "xi_norm", "b_norm"]},
    "xbtangent_2d": {"dims": ["time", "r", "z"], "type": "M", "vars": ["re_xi_tangent", "im_xi_tangent"]},
    "bnormal_spectrum": {"dims": ["time", "poloidal_harmonics", "psi"], "type": "M", "vars": ["jac.b.delpsi"]},
    "flint": {"dims": ["eta"], "type": "G", "vars": ["y1", "y2", "r", "z", "err"]},
    "metxy": {"dims": ["psi"], "type": "G", "vars": ["j11", "j12", "j13", "j21", "j22", "j23", "j33"]},
    "bal2": {"dims": ["theta"], "type": "G", "vars": ["asinh_y1", "asinh_y2", "y2/dy1", "dy2/y1", "asinh_ca1", "asinh_ca2"]},
    "plen": {"dims": ["ipert"], "type": "G", "vars": ["psifac", "asinh_eval"]},
    "line": {"dims": ["r"], "type": "G", "vars": ["theta", "z", "xi_psi", "b_psi", "xi_rho", "b_rho", "jstep"]},
    ";results/betaN/3": {
        "dims": ["theta"],
        "type": "G",
        "vars": [
            "re_bn",
            "re_bp",
            "re_bt",
            "im_bn",
            "im_bp",
            "im_bt",
            "theta_hamada",
            "theta_pest",
            "theta_equal_arc",
            "theta_boozer",
            "dtheta_hamada",
            "dtheta_pest",
            "dtheta_equal_arc",
            "dtheta_boozer",
        ],
    },
    "lar": {"dims": ["r"], "type": "G", "vars": ["bp", "bt", "pp", "sigma", "q", "p", "f", "psi"]},
    "kmat": {
        "dims": ["psi"],
        "type": "G",
        "vars": [
            "log_10_psi",
            "log_10_1-psi",
            "log_10_kmat01",
            "arg_kmat01",
            "log_10_kmat02",
            "arg_kmat02",
            "log_10_kmat03",
            "arg_kmat03",
            "log_10_kmat04",
            "arg_kmat04",
            "log_10_kmat05",
            "arg_kmat05",
            "log_10_kmat06",
            "arg_kmat06",
            "log_10_kmat07",
            "arg_kmat07",
            "log_10_kmat08",
            "arg_kmat08",
            "log_10_kmat09",
            "arg_kmat09",
            "log_10_kmat10",
            "arg_kmat10",
            "log_10_kmat11",
            "arg_kmat11",
            "log_10_kmat12",
            "arg_kmat12",
            "log_10_kmat13",
            "arg_kmat13",
        ],
    },
    "lar2": {"dims": ["psi"], "type": "G", "vars": ["rho", "q", "g11", "g22", "g33", "f", "g", "k"]},
    "lar1": {"dims": ["psi"], "type": "G", "vars": ["rho", "q", "g11", "g22", "g33", "f", "g", "k"]},
    "pmodb": {"dims": ["psifac"], "type": "G", "vars": ["real_eulerian", "imag_eulerian", "real_lagrangian", "imag_lagrangian"]},
    "scan": {"dims": ["asinh_re_s"], "type": "G", "vars": ["asinh_im_s", "re_det", "im_det", "asinh_re_det", "asinh_im_det"]},
    "diffw": {"dims": ["m"], "type": "G", "vars": ["re_diffw", "im_diffw", "re_bctheta", "im_bctheta", "re_bczeta", "im_bczeta"]},
    "eval": {"dims": ["ipert"], "type": "G", "vars": ["psifac", "log_10_psifac", "log_10_(m_-_n_q)", "log_10_hu", "q", "eval"]},
    "sol07": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "det": {"dims": ["de"], "type": "G", "vars": ["do", "det", "deta", "error"]},
    "orbit": {
        "dims": ["tau"],
        "type": "G",
        "vars": ["r", "z", "phi", "error", "bmod", "rl", "rlfac", "dmufac", "psi", "rho", "vpar", "x", "y"],
    },
    "ipout_contra": {
        "dims": ["psifac"],
        "type": "G",
        "vars": [
            "rho",
            "q",
            "real_xipsi",
            "imag_xipsi",
            "real_xitheta",
            "imag_xitheta",
            "real_xizeta",
            "imag_xizeta",
            "real_bpsi",
            "imag_bpsi",
            "real_btheta",
            "imag_btheta",
            "real_bzeta",
            "imag_bzeta",
            "real_xis",
            "imag_xis",
            "real_dxipsi",
            "imag_dxipsi",
            "real_dbpsi",
            "imag_dbpsi",
            "real_delta",
            "imag_delta",
            "delta",
        ],
    },
    "2d": {"dims": ["theta"], "type": "G", "vars": ["r2", "deta", "eta", "dphi", "r", "z", "jac"]},
    "sol09": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "sol08": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "gse": {"dims": ["theta"], "type": "G", "vars": ["psi", "flux1", "flux2", "source", "total", "error", "log10_error"]},
    "sum": {
        "dims": ["outval"],
        "type": "G",
        "vars": [
            "inval",
            "psilow",
            "psihigh",
            "amean",
            "rmean",
            "aratio",
            "kappa",
            "delta1",
            "delta2",
            "li1",
            "li2",
            "li3",
            "ro",
            "zo",
            "psio",
            "betap1",
            "betap2",
            "betap3",
            "betat",
            "betan",
            "bt0",
            "q0",
            "qmin",
            "qmax",
            "qa",
            "crnt",
            "asinh_plasma1",
            "asinh_vacuum1",
            "asinh_total1",
        ],
    },
    "sol03": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "sol02": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "sol01": {"dims": ["psifac"], "type": "G", "vars": ["log10_psifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "pflux_re_2d": {"dims": ["time", "r", "z"], "type": "M", "vars": ["re_perturbed_flux"]},
    "root": {"dims": ["log10_|s|"], "type": "G", "vars": ["re_root", "im_root"]},
    "sol06": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "sol05": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
    "sol04": {"dims": ["psifac"], "type": "G", "vars": ["logpsifac", "log10_u1", "log10_u2", "log10_ca1", "log10_ca2"]},
}


class OMFITGPECbin(OMFITncDataset):
    r"""
    OMFIT class used to interface with DCON and GPEC binary files.

    :param filename: String. File path (file name must start with original output name)

    :param \**kw: All additional key word arguments passed to OMFITobject

    """

    def __init__(self, filename, lock=True, export_kw={}, **kwargs):
        OMFITncDataset.__init__(self, filename, lock=lock, export_kw=export_kw, **kwargs)

    @dynaLoad
    def load(self):
        """
        Parse GPEC binaries using the xdraw mapping for variable names
        and expected binary structures.

        """
        data_set = Dataset()
        name = self.filename.split('/')[-1].split('.')[0]

        # warn user if they just opened a big (750KB+) slow file
        if os.path.getsize(self.filename) * 1e-3 > 750:
            print('Loading {:}. This may take a second...'.format(name))

        # find out if we know this file's format/vars
        found_name = False
        for k, v in list(bin_mapping.items()):
            if k == name:
                found_name = True
                vars = bin_mapping[name]['vars']
                dims = bin_mapping[name]['dims']
                dtype = bin_mapping[name]['type']
                break

        # if it is a "graph" file, data is written in column format
        # and breaks signal some sort of new line (often used to plot "slices" of 2D data)
        if found_name and dtype == 'G':
            index = 0
            # read the data if we do recognize it
            with FortranFile(self.filename, 'r') as f:
                data = []
                for i in range(int(1e8)):
                    try:
                        tmp = f.read_reals(dtype='f4')
                    except Exception:
                        break
                    if len(tmp):  # defence against DCON's empty lines
                        data.append(tmp)
                    else:
                        index += 1
                data = np.vstack(data).T
            # this would be nice, but DCON sometimes puts weird breaks in the data :/
            # with open(self.filename, 'r') as f:
            #     data = np.fromfile(f, dtype='float32', count=-1)

            vars = bin_mapping[name]['vars']
            # are there a lot of repeated profiles?
            if np.mod(data.shape[1], index):
                index = 1  # probably broke up profiles into segments for some reason (coloring)
            x = data[0].reshape((-1, index), order='F')
            if index > 1 and np.all(x[:, 0] == x[:, -1]):
                data = data.reshape((data.shape[0], -1, index), order='F')
                dims = (bin_mapping[name]['dims'][0], 'index')
                coords = {dims[0]: x[:, 0], 'index': np.arange(index)}
            else:
                dims = (bin_mapping[name]['dims'][0],)
                coords = {dims[0]: data[0]}
            # load up the data into memory as a Dataset (temporary because we have no save method)
            for i, k in enumerate(vars):
                data_set[k] = DataArray(data[i + 1], coords=coords, dims=dims)

        # if it is a 'M' file, data from each variable is all dumped at once (i.e. row format)
        # header integers specify sizes, then coordinates are dumped together, then variables one at a time
        elif found_name and dtype == 'M':
            # read the data if we do recognize it
            with FortranFile(self.filename, 'r') as f:
                # read header integers
                itime = f.read_ints(dtype=np.int32)
                shape = f.read_ints(dtype=np.int32) + 1
                # read dims
                dim_data = f.read_reals(dtype='f4').reshape(shape[0], shape[1], 2, order='F')
                # read vars
                var_data = []
                for i in range(len(vars)):
                    var_data.append(f.read_reals(dtype='f4').reshape(*shape, order='F'))
                var_data = np.array(var_data)

            # slice the dims, ignoring time
            if np.all(np.all(dim_data[:, :, 0].T == dim_data[:, 0, 0], axis=0)) & np.all(
                np.all(dim_data[:, :, 1] == dim_data[0, :, 1], axis=0)
            ):
                coords = {dims[1]: dim_data[:, 0, 0], dims[2]: dim_data[0, :, 1]}
                dims = dims[1:][::-1]
            else:
                coords = {'dim_0': np.arange(dim_data.shape[0]), 'dim_1': np.arange(dim_data.shape[1])}
                for i, k in enumerate(dims[1::]):
                    data_set[k] = DataArray(dim_data[:, :, i - 1], coords=coords, dims=['dim_0', 'dim_1'])
                dims = ['dim_0', 'dim_1']
            # load up the data into memory as a Dataset (temporary because we have no save method)
            for i, k in enumerate(vars):
                if len(coords[dims[0]]) == var_data[i].shape[0] and len(coords[dims[1]]) == var_data[i].shape[1]:
                    data_set[k] = DataArray(var_data[i], coords=coords, dims=dims)  # definitely true with dim_0, dim_1
                else:
                    data_set[k] = DataArray(var_data[i].T, coords=coords, dims=dims)
        else:
            raise ValueError("Unknown parsing for {:}".format(name))
            # printe("WARNING: Unknown parsing for {:}".format(name))

        lock = self.lock
        self.set_lock(False)
        self.update(data_set)
        self.attrs = {}
        self.set_lock(lock)

        self.dynaLoad = False

        return

    @dynaSave
    def save(self):
        """
        This method can detect if .filename was changed and if so, makes a copy from the original .filename
        (saved in the .link attribute) to the new .filename
        """
        OMFITobject.save(self)


class OMFITldpi(OMFITncDataset):
    r"""
    OMFIT class used to interface with L. Don Pearlstein's inverse equilibrium code.

    :param filename: String. File path (file name must start with original output name)

    :param \**kw: All additional key word arguments passed to OMFITobject

    """

    def __init__(self, filename, lock=True, export_kw={}, **kwargs):
        OMFITncDataset.__init__(self, filename, lock=lock, export_kw=export_kw, **kwargs)

    @dynaLoad
    def load(self):
        """
        Parse ldp_i binaries using the DCON read_eq_ldp_i as a guide for variable names
        and expected binary structures.

        """
        data_set = Dataset()
        name = self.filename.split('/')[-1].split('.')[0]

        # warn user if they just opened a big (750KB+) slow file
        if os.path.getsize(self.filename) * 1e-3 > 750:
            print('Loading {:}. This may take a second...'.format(name))

        # header integers specify sizes, then variables are dumped one at a time
        vars = SortedDict()
        with FortranFile(self.filename, 'r') as binfile:
            # read header integers
            mxmy = binfile.read_ints(dtype=np.int32)
            # read 1d vars
            # Note that in the SPECTOR example, every other number in the vars is garbage
            vars['psi'] = binfile.read_reals(dtype='f8')
            vars['f'] = binfile.read_reals(dtype='f8')
            vars['p'] = binfile.read_reals(dtype='f8')
            vars['q'] = binfile.read_reals(dtype='f8')
            # read 2d vars
            r = binfile.read_reals(dtype='f8').reshape(mxmy[0], mxmy[1], order='C')
            z = binfile.read_reals(dtype='f8').reshape(mxmy[0], mxmy[1], order='C')

        # coordinates
        psio = vars['psi'][-1] - vars['psi'][0]
        psin = (vars['psi'] - vars['psi'][0]) / psio
        theta = np.linspace(-np.pi, np.pi, mxmy[1], endpoint=True)
        # helicity **What is the proper way to get this? From q? From psio? Both?**
        if psio < 0 or np.nanmean(vars['q']) < 0:
            helicity = -1  # is this true? What is the convention?
        else:
            helicity = 1
        # store 1d vars
        coords = {'psi_n': psin}
        dims = ['psi_n']
        for k, v in vars.items():
            data_set[k] = DataArray(v, coords=coords, dims=dims)
        # store 2d vars
        coords = {'psi_n': psin, 'theta': theta}
        dims = ['psi_n', 'theta']
        data_set['R'] = DataArray(r, coords=coords, dims=dims)
        data_set['Z'] = DataArray(z, coords=coords, dims=dims)

        # update the ncDataset in-memory representation of the file. Don't let users mess with it
        lock = self.lock
        self.set_lock(False)
        self.update(data_set)
        self.attrs = {'helicity': helicity}
        self.set_lock(lock)

        self.dynaLoad = False

        return

    @dynaSave
    def save(self):
        """
        This method can detect if .filename was changed and if so, makes a copy from the original .filename
        (saved in the .link attribute) to the new .filename
        """
        OMFITobject.save(self)

    def plot(self, only2D=False, qcontour=False, levels=10, **kwargs):
        """
        Quick plot of LDPI equilibrium.

        :param only2D: bool. Plot only the 2D contour of psi_n (or optionally q)
        :param qcontour: bool. If true, levels of q are contoured in 2D plot (default is psi_n)
        :param levels: int or np.ndarray. Number of (or explicit values of) levels to be contoured in 2D plot. None plots all levels in file
        :param kwargs: All other key word arguments are passed to the matplotlib plot function
        :return:
        """
        # default to all levels in the file
        if levels is None:
            levels = self['psi_n'].values
        # convert q levels into psi_n levels
        elif qcontour:
            # set some number of equally spaced levels
            if is_int(levels):
                levels = np.linspace(self['q'].min(), self['q'].max(), levels + 1, endpoint=True)[1:]  # skip psi_n=0
            levels = interp1e(self['q'], self['psi_n'])(levels)
        # set some number of equally spaced levels
        elif is_int(levels):
            levels = np.linspace(0, 1, levels + 1, endpoint=True)[1:]  # skip psi_n=0

        def plot_2d(ax):
            """
            Kind of like a custom contour using the fact that the r,z arrays trace out flux surfaces.
            Using plot makes the key word arguments consistent with 1D plots too, which is nice.
            :param ax: Axes.
            :return: list of lines
            """
            psi = self['psi_n'].sel(psi_n=levels, method='nearest')
            r = self['R'].sel(psi_n=psi).values
            z = self['Z'].sel(psi_n=psi).values
            x = np.vstack((r.T, np.nan * r[:, 0])).T.ravel()
            y = np.vstack((z.T, np.nan * z[:, 0])).T.ravel()

            l = ax.plot(x, y, **kwargs)
            ax.set_xlabel('R')
            ax.set_ylabel('Z')
            ax.set_aspect('equal')

            return l

        if only2D:
            ax = kwargs.pop('ax', None)
            if ax is None:
                # extra logic to handle OMFIT's auto-figure making when double-clicked in tree
                fig = pyplot.gcf()
                if len(fig.axes):
                    # normal situation in which existing figures should be respected and left alone
                    fig, ax = pyplot.subplots(subplot_kw={'aspect': 'equal'})
                else:
                    # OMFIT (or the pyplot.gcf needed to check OMFIT) made a empty figure for us
                    ax = fig.add_subplot(111, aspect='equal')
            plot_2d(ax)
        else:
            fig = kwargs.pop('figure', None)
            if fig is None:
                # extra logic to handle OMFIT's auto-figure making when double-clicked in tree
                fig = pyplot.gcf()
                if len(fig.axes):
                    # normal situation in which existing figures should be respected and left alone
                    fig = figure()
                else:
                    # OMFIT (or the pyplot.gcf needed to check OMFIT) made a empty figure for us
                    pass

            # 1D plots
            ax = fig.add_subplot(322)
            self['q'].plot(ax)
            pyplot.setp(ax.get_xticklabels(), visible=False)
            ax.set_xlabel('')
            ax.yaxis.set_major_locator(pyplot.MaxNLocator(nbins=4))
            ax = fig.add_subplot(324, sharex=ax)
            self['p'].plot(ax)
            pyplot.setp(ax.get_xticklabels(), visible=False)
            ax.set_xlabel('')
            ax.yaxis.set_major_locator(pyplot.MaxNLocator(nbins=4))
            ax = fig.add_subplot(326, sharex=ax)
            self['f'].plot(ax)
            ax.yaxis.set_major_locator(pyplot.MaxNLocator(nbins=4))

            ax = fig.add_subplot(131)
            ax.set_frame_on(False)
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')
            ax.locator_params(nbins=3)
            plot_2d(ax)

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

from omfit_classes.omfit_mds import OMFITmds
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.omfit_nc import OMFITncData
from omfit_classes.utils_base import printi
from omfit_classes.exceptions_omfit import OMFITexception
from omfit_classes.utils_math import interp1e

import omas
import numpy as np

__all__ = ['NoFitException', 'OMFITosborneProfile', 'OMFITpFile']

os.environ.setdefault('VPN_ACTIVE', '')


class NoFitException(OMFITexception):
    pass


class OMFITosborneProfile(OMFITmds):
    """
    Class accesses Osborne fits stored in MDS+, and provides convenient methods
    for accessing the data or fitting functions used in those fits, including
    handling the covariance of the fitting parameters

    :param server: The device (really MDS+ archive)

    :param treename: The tree where the Osborne-tool profiles are stored

    :param shot: The shot number

    :param time: The timeid of the profile

    :param runid: The runid of the profile

    Note that this class assumes that the profiles are stored as
    [`tree`]['PROFDB_PED']['P<time>_<runid>']
    """

    def __init__(self, server='DIII-D', treename='auto', shot=None, time=None, runid=None):
        if treename == 'auto':
            if is_device(server, 'DIII-D'):
                treename = 'PEDESTAL'
            elif is_device(server, ('NSTX', 'NSTX-U')):
                treename = 'PROFDB_PED'
        self.OMFITproperties = {}
        OMFITmds.__init__(self, server, treename, shot)
        self.OMFITproperties['treename'] = treename
        self.OMFITproperties['time'] = time
        self.OMFITproperties['runid'] = runid
        self.OMFITproperties['shot'] = shot

    @property
    def treename(self):
        return self.OMFITproperties['treename']

    @treename.setter
    def treename(self, value):
        self.OMFITproperties['treename'] = value
    @property
    def time(self):
        return self.OMFITproperties['time']

    @time.setter
    def time(self, value):
        self.OMFITproperties['time'] = value

    @time.deleter
    def time(self):
        self.OMFITproperties['time'] = None

    @property
    def runid(self):
        return self.OMFITproperties['runid']

    @runid.setter
    def runid(self, value):
        self.OMFITproperties['runid'] = value

    @runid.deleter
    def runid(self):
        self.OMFITproperties['runid'] = None

    @property
    def shot(self):
        return self.OMFITproperties['shot']

    @shot.setter
    def shot(self, value):
        self.OMFITproperties['shot'] = value

    @shot.deleter
    def shot(self):
        self.OMFITproperties['shot'] = None

    @dynaLoad
    def load(self):
        OMFITmds.load(self)
        profdb_ped = self
        if self.treename == 'PEDESTAL':
            profdb_ped = self['PROFDB_PED']
        if 'P%s_%s' % (self.time, self.runid.upper()) not in profdb_ped:
            raise RuntimeError('Time: %s, Runid: %s does not exist for shot %s' % (self.time, self.runid, self.shot))
        tmp = profdb_ped['P%s_%s' % (self.time, self.runid.upper())]
        self.clear()
        self.update(tmp)

    def __repr__(self):
        return self.__class__.__name__ + '(' + ','.join(map(repr, [self.server, self.treename, self.shot, self.time, self.runid])) + ')'

    def get_raw_data(self, x_var='rhob', quant='ne'):
        """
        Get the raw data

        :param x_var: The mapping of the data (rhob,rhov,psi,R)

        :param quant: The quantity for which to return the data of the fit

        :return: x,y tuple * x - mapped radius of data
                           * y - the data (an array of numbers with uncertainties)
        """
        from uncertainties.unumpy import uarray

        node = self['%sDAT%s' % (quant.upper(), x_var.upper())]
        return node.dim_of(0), uarray(node.data(), node.error())

    def plot_raw_data(self, x_var='rhob', quant='ne', **kw):
        r"""
        Plot the raw data

        :param x_var: The mapping of the data (rhob,rhov,psi,R)

        :param quant: The quantity for which to plot the data of the fit

        :param \**kw: Keyword dictionary passed to uerrorbar

        :return: The collection instance returned by uerrorbar
        """
        from omfit_classes.utils_plot import uerrorbar
        from matplotlib import rcParams

        if quant == 'omeg':
            x, y = self.get_raw_data(quant='vt1', x_var=x_var)
            xR, yR = self.get_raw_data(quant='vt1', x_var='R')
            y = y / xR
        else:
            x, y = self.get_raw_data(x_var=x_var, quant=quant)
        kw.setdefault('color', rcParams['axes.prop_cycle'].by_key()['color'][0])
        kw.setdefault('ms', 0.5)
        kw.setdefault('capsize', 0)
        kw.setdefault('marker', '.')
        return uerrorbar(x, y, **kw)

    def calc_spline_fit(self, x_var='rhob', quant='ne', knots=5):
        """
        Calculate a spline fit

        :param x_var: The mapping of the data (rhob,rhov,psi,R)

        :param quant: The quantity for which to calculate a spline fit

        :param knots: An integer (autoknotted) or a list of knot locations
        """
        x, y = self.get_raw_data(x_var=x_var, quant=quant)
        fit = 'spl'
        fit_node = '%s%s%s' % (quant.upper(), fit.upper(), x_var.upper())
        print(fit_node in self)
        if fit_node in self:
            node = self[fit_node]
            xfit = node.dim_of(0)
            if xfit is not None:
                print(max(xfit), x < max(xfit))
                ind = x < max(xfit)
                x = x[ind]
                y = y[ind]
            if 'SPLINE_T' in node and node['SPLINE_T'].data() is not None:
                print('Using {fit_node} knots'.format(fit_node=fit_node))
                knots = np.unique(node['SPLINE_T'].data())
                print(knots)
        return fitSpline(x, nominal_values(y), std_devs(y), knots=knots, fit_SOL=True)

    def get_fit(self, fit, x_var='rhob', quant='ne', corr=True, x_val=None):
        """
        Get the fit, including uncertainties taking into account covariance of parameters

        :param fit: Which type of fit to retrieve

        :param x_var: The mapping of the fit (rhob,rhov,psi,R)

        :param quant: The quantity that was fit

        :param corr: (bool) Use the covariance of the parameters

        :param x_val: If the fit can be evaluated, if ``x_val`` is not ``None``,
            evaluate the fit at these locations

        :return: x,y tuple * x - radius of fit as stored in MDS+
                           * y - the fit (an array of numbers with uncertainties)
        """
        node = self['%s%s%s' % (quant.upper(), fit.upper(), x_var.upper())]
        if node.data() is None:
            raise NoFitException('No fit for %s' % fit)

        def get_mdsplus_fit():
            if node.data().shape == node.error().shape:
                return node.dim_of(0), uarray(node.data(), node.error())
            else:
                return node.dim_of(0), uarray(node.data(), 0)

        import uncertainties
        import numpy as np
        from uncertainties.unumpy import uarray

        try:
            import data_fit_functions
        except Exception:
            warnings.warn('You must have Osborne tools installed to get the fit with covarianced errors.  \n' 'Using the stored errors')
            return get_mdsplus_fit()
        else:
            orig_np = np
            try:
                data_fit_functions.numpy = uncertainties.unumpy
                data_fit_functions.numpy.where = np.where
                try:
                    fit_fun = eval('data_fit_functions.%s' % (node['FITNAME'].data()[0]))
                except Exception:
                    warnings.warn("Can't handle fitname %s" % (node['FITNAME'].data()[0]))
                    return get_mdsplus_fit()
                if 'FIT_COEFCOV' not in node or not corr:
                    printi('Using Osborne tool profile fit parameters without correlated uncertainties for fit:%s' % fit)
                    params = uarray(node['FIT_COEF'].data(), node['FIT_COEFERR'].data())
                else:
                    params = uncertainties.correlated_values(node['FIT_COEF'].data(), node['FIT_COEFCOV'].data())
                try:
                    x = node.dim_of(0)
                    if x_val is not None:
                        x = x_val
                    if node['FITNAME'].data()[0] == 'tanh_multi' and x_var.upper() == 'RHOB':
                        return x, fit_fun(params, x, 0)
                    else:
                        return x, fit_fun(params, x)
                except Exception as _excp:
                    printe(_excp)
                    printe('Using MDS+ stored fit, without errorbars')
                    return get_mdsplus_fit()
            finally:
                data_fit_functions.numpy = orig_np

    def get_fit_deriv(self, nder, fit, **kw):
        r"""
        Apply deriv(x,y) `nder` times

        :param nder: Number of derivatives

        :param fit: Which type of fit to apply derivatives to

        :param \**kw: Keyword arguments passed to get_fit

        :return: x, d^{nder}y / d x^{nder} tuple * x - radius of fit as stored in MDS+
                                                 * d^n y / d x^n - The nder'th derivative of the fit
        """
        x, y = self.get_fit(fit, **kw)
        for i in range(nder):
            y = deriv(x, y)
        return x, y

    def plot_fit(self, fit, x_var='rhob', quant='ne', corr=True, nder=0, **kw):
        """
        Plot the fit for the given quant, with the given x-coordinate.

        :param fit: Which type of fit to plot

        :param x_var:  The mapping of the fit (rhob,rhov,psi,R)

        :param quant: The quantity that was fit

        :param corr: Plot with correlated uncertainty parameters

        :param nder: The number of derivatives to compute before plotting

        :return: The result of uband
        """
        x, y = self.get_fit_deriv(nder, fit, x_var=x_var, quant=quant, corr=corr)
        from omfit_classes.utils_plot import uband

        return uband(x, y, **kw)

    def plot_all_fits(self, x_var='rhob', quant='ne', corr=True, nder=0):
        """
        Plot all fits for the given quantity `quant` and mapping `x_var`

        :param x_var: The mapping of the fit (rhob,rhov,psi,R)

        :param quant: The quantity that was fit

        :param corr: Plot with correlated uncertainty parameters

        :param nder: Plot the nder'th derivative of the fit (if nder=0, plot data also)

        :return: None
        """
        if nder == 0:
            self.plot_raw_data(x_var=x_var, quant=quant)
        ki = 1
        for k in list(self.keys()):
            if not (k.startswith(quant.upper()) and k.endswith(x_var.upper())):
                continue
            fit_type = k[len(quant) : -len(x_var)]
            if fit_type == 'DAT':
                continue
            try:
                from matplotlib import rcParams

                self.plot_fit(
                    fit_type,
                    x_var=x_var,
                    quant=quant,
                    color=rcParams['axes.prop_cycle'].by_key()['color'][ki % len(rcParams['axes.prop_cycle'].by_key()['color'])],
                    corr=corr,
                    label=fit_type,
                    nder=nder,
                )
                ki += 1
            except (NoFitException, TypeError) as _excp:
                continue
        from pylab import draw

        draw()

    def __save_kw__(self):
        """
        :return: generate the kw dictionary used to save the attributes to be passed when reloading from OMFITsave.txt
        """
        return self.OMFITproperties


class OMFITpFile(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with Osborne pfiles

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, **kw):
        OMFITobject.__init__(self, filename, **kw)
        SortedDict.__init__(self)

        self.legacy = False

        self.descriptions = SortedDict()
        self.descriptions['ne'] = 'Electron density'
        self.descriptions['te'] = 'Electron temperature'
        self.descriptions['ni'] = 'Ion density'
        self.descriptions['ti'] = 'Ion temperature'
        self.descriptions['nb'] = 'Fast ion density'
        self.descriptions['pb'] = 'Fast ion pressure'
        self.descriptions['ptot'] = 'Total pressure'
        self.descriptions['omeg'] = 'Toroidal rotation: VTOR/R'
        self.descriptions['omegp'] = 'Poloidal rotation: Bt * VPOL / (RBp)'
        self.descriptions['omgvb'] = 'VxB rotation term in the ExB rotation frequency: OMEG + OMEGP'
        self.descriptions['omgpp'] = 'Diamagnetic term in the ExB rotation frequency: (P_Carbon)/dpsi / (6*n_Carbon)'
        self.descriptions['omgeb'] = 'ExB rotation frequency: OMGPP + OMGVB = Er/(RBp)'
        self.descriptions['er'] = 'Radial electric field from force balance: OMGEB * RBp'
        self.descriptions['ommvb'] = 'Main ion VXB term of Er/RBp, considered a flux function'
        self.descriptions['ommpp'] = 'Main ion pressure term of Er/RBp, considered a flux function'
        self.descriptions['omevb'] = 'Electron VXB term of Er/RBp, considered a flux function'
        self.descriptions['omepp'] = 'Electron pressure term of Er/RBp, considered a flux function'
        self.descriptions['kpol'] = 'KPOL=VPOL/Bp : V_vector = KPOL*B_vector + OMGEB * PHI_Vector'
        self.descriptions['N Z A'] = 'N Z A of ION SPECIES'
        self.descriptions['omghb'] = 'Hahm-Burrell form for the ExB velocity shearing rate: OMGHB = (RBp)**2/Bt * d (Er/RBp)/dpsi'
        self.descriptions['nz1'] = 'Density of the 1st impurity species'
        self.descriptions['vtor1'] = 'Toroidal velocity of the 1st impurity species'
        self.descriptions['vpol1'] = 'Poloidal velocity of the 1st impurity species'
        self.descriptions['nz2'] = 'Density of the 2nd impurity species'
        self.descriptions['vtor2'] = 'Toroidal velocity of the 2nd impurity species'
        self.descriptions['vpol2'] = 'Poloidal velocity of the 2nd impurity species'
        # There may be more impurity species, but let's stop here for now.

        self.units = SortedDict()
        self.units['ne'] = '10^20/m^3'
        self.units['te'] = 'KeV'
        self.units['ni'] = '10^20/m^3'
        self.units['ti'] = 'KeV'
        self.units['nb'] = '10^20/m^3'
        self.units['pb'] = 'KPa'
        self.units['ptot'] = 'KPa'
        self.units['omeg'] = 'kRad/s'
        self.units['omegp'] = 'kRad/s'
        self.units['omgvb'] = 'kRad/s'
        self.units['omgpp'] = 'kRad/s'
        self.units['omgeb'] = 'kRad/s'
        self.units['ommvb'] = ''
        self.units['ommpp'] = ''
        self.units['omevb'] = ''
        self.units['omepp'] = ''
        self.units['er'] = 'kV/m'
        self.units['kpol'] = 'km/s/T'
        self.units['N Z A'] = ''
        self.units['omghb'] = ''
        self.units['nz1'] = '10^20/m^3'
        self.units['vtor1'] = 'km/s'
        self.units['vpol1'] = 'km/s'
        self.units['nz2'] = '10^20/m^3'
        self.units['vtor2'] = 'km/s'
        self.units['vpol2'] = 'km/s'

        if os.stat(self.filename).st_size:
            self.dynaLoad = True
        else:
            for key in list(self.descriptions.keys()):
                if key in ('N Z A',):
                    continue
                self[key] = OMFITncData()
                self[key]['data'] = np.array([0])
                self[key]['description'] = self.descriptions[key]
                self[key]['psinorm'] = np.array([0])
                self[key]['units'] = self.units[key]
                self[key]['derivative'] = np.array([0])

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """

        self.clear()

        # read the file
        f = os.path.getsize(self.filename)
        if f == 0:
            return
        fn = self.filename
        with open(fn, 'r') as f:
            fl = f.read().strip().splitlines(True)

        ind = 0
        while True:
            try:
                line = fl[ind]
                cur = line.split()
                curData = fl[ind + 1].split()
            except IndexError:
                break

            num = int(re.sub(r'([0-9]*)\s.*', r'\1', line))
            xkey = re.sub(r'([0-9]*)\s(.*)\s(.*)\((.*)\)\s(.*)\n', r'\2', line)
            key = re.sub(r'([0-9]*)\s(.*)\s(.*)\((.*)\)\s(.*)\n', r'\3', line)
            units = re.sub(r'([0-9]*)\s(.*)\s(.*)\((.*)\)\s(.*)\n', r'\4', line)
            der = re.sub(r'([0-9]*)\s(.*)\s(.*)\((.*)\)\s(.*)\n', r'\5', line)

            quants = [xkey, key + '(' + units + ')', der]
            q = []
            for i in range(ind + 1, ind + 1 + num):
                q.append(list(map(float, fl[i].split())))
            q = list(zip(*q))
            if key in self:
                if np.sum(np.array(self[key]['data']) != np.array(q[1])):
                    raise ValueError('%s already defined, but trying to change its value' % quants[1])
            elif 'N Z A of ION SPECIES' in line:
                self['N Z A'] = OMFITncData()
                self['N Z A']['description'] = 'N Z A of ION SPECIES'
                self['N Z A']['N'] = np.array(q[0])
                self['N Z A']['Z'] = np.array(q[1])
                self['N Z A']['A'] = np.array(q[2])
            else:
                self[key] = OMFITncData()
                if key in self.descriptions:
                    self[key]['description'] = self.descriptions[key]
                else:
                    self[key]['description'] = key
                self[key]['units'] = units
                for qi, quant in enumerate(quants):
                    if qi == 1:
                        self[key]['data'] = np.array(q[qi])
                    elif quant == 'd%s/dpsiN' % key or quant == 'd%s/dpsi' % key:
                        self[key]['derivative'] = np.array(q[qi])
                    else:
                        self[key][quant] = np.array(q[qi])

            ind = ind + 1 + num

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """
        lines = []
        for key in self.keys(filter=hide_ptrn):
            if key == 'N Z A':
                if self.legacy:
                    break
                lines.append('%i N Z A of ION SPECIES\n' % (len(self[key]['A']),))
                for i in range(len(self[key]['A'])):
                    lines.append(" %f   %f   %f\n" % (self[key]['N'][i], self[key]['Z'][i], self[key]['A'][i]))
            else:
                if len(self[key]['data']) == 1:
                    continue
                lines.append("%i psinorm %s(%s) d%s/dpsiN\n" % (len(self[key]['data']), key, self[key]['units'], key))
                for i in range(len(self[key]['data'])):
                    lines.append(" %f   %f   %f\n" % (self[key]['psinorm'][i], self[key]['data'][i], self[key]['derivative'][i]))
        with open(self.filename, 'w') as f:
            f.writelines(lines)

    def plot(self):
        """
        Method used to plot all profiles, one in a different subplots

        :return: None
        """
        nplot = len(self)
        cplot = np.floor(np.sqrt(nplot) / 2.0) * 2
        rplot = np.ceil(nplot * 1.0 / cplot)
        pyplot.subplots_adjust(wspace=0.35, hspace=0.0)
        pyplot.ioff()
        try:
            for k, item in enumerate(self):
                r = np.floor(k * 1.0 / cplot)
                c = k - r * cplot

                if k == 0:
                    ax1 = pyplot.subplot(rplot, cplot, r * (cplot) + c + 1)
                    ax = ax1
                else:
                    ax = pyplot.subplot(rplot, cplot, r * (cplot) + c + 1, sharex=ax1)
                ax.ticklabel_format(style='sci', scilimits=(-3, 3))
                if 'psinorm' not in self[item]:
                    printi('Can\'t plot %s because no psinorm attribute' % item)
                    continue
                x = self[item]['psinorm']

                pyplot.plot(x, self[item]['data'], '.-')
                pyplot.text(0.5, 0.9, item, horizontalalignment='center', verticalalignment='top', size='medium', transform=ax.transAxes)

                if k < len(self) - cplot:
                    pyplot.setp(ax.get_xticklabels(), visible=False)
                else:
                    pyplot.xlabel('$\\psi$')

                pyplot.xlim(min(x), max(x))

        finally:
            pyplot.draw()
            pyplot.ion()

    def remap(self, points='ne', **kw):
        """
        Remap the disparate psinorm grids for each vaiable onto the same psinorm grid

        :param npoints: number of points to remap the originally 256 grid
            - If points is int: make an evenly spaced array.
            - If points is array: use this as the grid
            - If points is a string: use the 'psinorm' from that item in the pfile (by default `ne['psinorm']`)

        :param \**kw: addidional keywords are passed to scipy.interpolate.interp1d

        return: The entire object remapped to the same psinorm grid
        """

        mapped = copy.deepcopy(self)
        keys = mapped.keys()

        if isinstance(points, str):
            remap_psin = self[points]['psinorm']

        elif type(points) is int:  # Evenly spaced grid rebase
            remap_psin = np.linspace(0, 1, points)

        elif type(points) in [list, tuple, np.ndarray]:  # user provided grid rebase
            assert np.all(np.abs(points) <= 1), 'All values must be on the interval [0, 1]'
            assert np.all(np.diff(points) > 0), 'All values must be monotonically increasing'
            remap_psin = points

        mapped['psinorm'] = remap_psin  # save the psin grid
        # iterate through all keys
        for key in keys:
            if key in ('N Z A',):  # this is not mapped to psi so skip it
                continue
            f_key = interp1d(self[key]['psinorm'], self[key]['data'])
            f_key_derivative = interp1d(self[key]['psinorm'], self[key]['derivative'], **kw)
            mapped[key]['psinorm'] = remap_psin
            mapped[key]['data'] = f_key(remap_psin)
            mapped[key]['derivative'] = f_key_derivative(remap_psin)

        return mapped

    def to_omas(self, ods=None, time_index=0, gEQDSK=None):
        """
        translate OMFITpFile class to OMAS data structure

        :param ods: input ods to which data is added

        :param time_index: time index to which data is added

        :param gEQDSK: corresponding gEQDSK (if ods does not have equilibrium already

        :return: ods
        """
        # Lyons:  I've used my own rotation variable definitions here, until IMAS properly defines them
        #         Note that negative signs and sign_Ip are needed to make
        #           omega_perp, omega_dia, and omega_ExB have the same sign convention

        from omfit_classes.omfit_eqdsk import OMFITgeqdsk
        from omas import ODS, omas_environment
        from omfit_classes.utils_math import atomic_element

        if ods is None:
            ods = ODS()

        if gEQDSK is not None:
            gEQDSK.to_omas(ods=ods, time_index=time_index)
        else:
            filename = 'g' + os.path.split(self.filename)[1][1:]
            gEQDSK = OMFITgeqdsk(filename).from_omas(ods=ods, time_index=time_index)

        cocosio = 1  # pFile's have CCW phi and CW theta
        assert gEQDSK.cocos == cocosio, "gEQDSK must be in COCOS %d" % cocosio

        # get required quantities
        sign_Ip = np.sign(gEQDSK['CURRENT'])

        # get gEQDSK quantities
        psin_eq = np.linspace(0.0, 1.0, len(gEQDSK['PRES']))
        rhotn_eq = gEQDSK['RHOVN']
        R_eq = gEQDSK['fluxSurfaces']['midplane']['R']
        Bt_eq = gEQDSK['fluxSurfaces']['midplane']['Bt']
        Bp_eq = gEQDSK['fluxSurfaces']['midplane']['Bp']

        quants = [
            ('rotation_frequency_tor_sonic', 'omgeb', sign_Ip * 1e3),  # sign_Ip accounts for abs(Bp) in pFile definition
            ('pressure_perpendicular', 'ptot', 1e3 / 3.0),
            ('pressure_parallel', 'ptot', 1e3 / 3.0),
            ('electrons.density_thermal', 'ne', 1e20),
            ('electrons.temperature', 'te', 1e3),
            ('electrons.rotation.perpendicular', 'omevb', 1e3),
            ('electrons.rotation.diamagnetic', 'omepp', sign_Ip * 1e3),
        ]  # sign_Ip accounts for abs(dpsi) in pFile definition

        def get_ion(N, Z, A):
            label = list(atomic_element(Z=N, A=int(A)).values())[0]['symbol']
            k = -1
            ion = None
            prof1d = ods['core_profiles']['profiles_1d'][time_index]
            if 'ion' in prof1d:
                for k in prof1d['ion']:
                    if (
                        prof1d['ion'][k]['label'] == label
                        and int(prof1d['ion'][k]['element'][0]['a']) == int(A)
                        and prof1d['ion'][k]['element'][0]['z_n'] == Z
                    ):
                        # found the ion
                        ion = prof1d['ion'][k]
                        err = "OMAS only works for single ion states"
                        assert ion['multiple_states_flag'] == 0, err
            if ion is None:
                k += 1
                # need to add new ion
                ion = prof1d['ion'][k]
                ion['multiple_states_flag'] = 0
                ion['label'] = label
                ion['element'][0]['a'] = A
                ion['element'][0]['z_n'] = Z

            return k, ion

        if 'N Z A' in self:
            # Assume multiple ion species are defined
            mk, main_ion = get_ion(N=self['N Z A']['N'][-2], Z=self['N Z A']['Z'][-2], A=self['N Z A']['A'][-2])
            bk, beam_ion = get_ion(N=self['N Z A']['N'][-1], Z=self['N Z A']['Z'][-1], A=self['N Z A']['A'][-1])
        else:
            printw("'N Z A' missing from OMFITpFile; assuming deuterium for main and beam ions")
            mk, main_ion = get_ion(N=1, Z=1, A=2.0)
            bk, beam_ion = get_ion(N=1, Z=1, A=2.0)

        quants += [
            (f'ion.{mk}.density_thermal', 'ni', 1e20),
            (f'ion.{mk}.temperature', 'ti', 1e3),
            (f'ion.{mk}.rotation.perpendicular', 'ommvb', 1e3),
            (f'ion.{mk}.rotation.diamagnetic', 'ommpp', sign_Ip * 1e3),  # sign_Ip accounts for abs(dpsi) in pFile definition
            (f'ion.{bk}.density_fast', 'nb', 1e20),
            (f'ion.{bk}.pressure_fast_perpendicular', 'pb', 1e3 / 3.0),
            (f'ion.{bk}.pressure_fast_parallel', 'pb', 1e3 / 3.0),
        ]

        if 'N Z A' in self:
            for i in range(len(self['N Z A']['N']) - 2):
                ik, imp_ion = get_ion(N=self['N Z A']['N'][i], Z=self['N Z A']['Z'][i], A=self['N Z A']['A'][i])
                quants += [
                    (f'ion.{ik}.density_thermal', 'nz%d' % (i + 1), 1e20),
                    (f'ion.{ik}.temperature', 'ti', 1e3),
                ]  # Lyons: I think it's assumed all ions have same temperature

                if imp_ion['label'] == 'C':
                    # working with Carbon
                    quants += [
                        (f'ion.{ik}.rotation.perpendicular', 'omgvb', 1e3),
                        (f'ion.{ik}.rotation.diamagnetic', 'omgpp', sign_Ip * 1e3),  # sign_Ip accounts for abs(dpsi) in pFile definition
                        (f'ion.{ik}.rotation.parallel_stream_function', 'kpol', 1e3),
                    ]

        else:
            ik, imp_ion = get_ion(N=6, Z=6, A=12.0)
            if 'nz1' in self:
                printw("                                 carbon impurity")
                quants += [(f'ion.{ik}.density_thermal', 'nz1', 1e20)]
            else:
                printw("                                 carbon impurity with trace density")
                quants += [(f'ion.{ik}.density_thermal', 'ni', 1e-6)]
            quants += [
                (f'ion.{ik}.temperature', 'ti', 1e3),  # Lyons: I think it's assumed all ions have same temperature
                (f'ion.{ik}.rotation.perpendicular', 'omgvb', 1e3),
                (f'ion.{ik}.rotation.diamagnetic', 'omgpp', sign_Ip * 1e3),  # sign_Ip accounts for abs(dpsi) in pFile definition
                (f'ion.{ik}.rotation.parallel_stream_function', 'kpol', 1e3),
            ]

        for q_ods, q_p, fac in quants:
            if q_p in self:
                # pFiles don't enforce that every variable has the same psinorm grid
                rho_tor_norm = np.interp(self[q_p]['psinorm'], psin_eq, rhotn_eq)
                coordsio = {f'core_profiles.profiles_1d.{time_index}.grid.rho_tor_norm': rho_tor_norm}
                with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):
                    prof1d = ods['core_profiles']['profiles_1d'][time_index]
                    prof1d[q_ods] = fac * self[q_p]['data']
            else:
                printw("pFile does not contain " + q_p + ". Skipping")

        if 'N Z A' in self:
            for i in range(len(self['N Z A']['N']) - 2):
                ik, imp_ion = get_ion(N=self['N Z A']['N'][i], Z=self['N Z A']['Z'][i], A=self['N Z A']['A'][i])
                if imp_ion['label'] != 'C':
                    try:
                        # save rotations for non-carbon
                        psin = self[f'vpol{(i + 1)}']['psinorm']
                        rho_tor_norm = np.interp(psin, psin_eq, rhotn_eq)
                        coordsio = {f'core_profiles.profiles_1d.{time_index}.grid.rho_tor_norm': rho_tor_norm}

                        R = np.interp(psin, psin_eq, R_eq)
                        Bp = np.interp(psin, psin_eq, Bp_eq)
                        Bt = np.interp(psin, psin_eq, Bt_eq)

                        with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):
                            prof1d = ods['core_profiles']['profiles_1d'][time_index]

                            # parallel stream function from vpol and Bp
                            vpol = sign_Ip * self[f'vpol{(i + 1)}']['psinorm']['data']  # vpol in pFile has a sign_Ip
                            prof1d[f'ion.{ik}.velocity.poloidal'] = 1e3 * vpol
                            prof1d[f'ion.{ik}.rotation.parallel_stream_function'] = 1e3 * vpol / Bp

                            # perpendicular rotation from vtor and vpol
                            vtor = np.interp(psin, self[f'vtor{(i + 1)}']['psinorm'], self[f'vtor{(i + 1)}']['data'])
                            prof1d[f'ion.{ik}.velocity.toroidal'] = 1e3 * vtor
                            omeg = vtor / R
                            omegp = -vpol * Bt / (R * Bp)
                            prof1d[f'ion.{ik}.rotation.perpendicular'] = 1e3 * (omeg + omegp)

                            # diamagentic rotation from vtor, vpol, and omgeb
                            omgeb = sign_Ip * np.interp(
                                psin, self['omgeb']['psinorm'], self['omgeb']['data']
                            )  # sign_Ip accounts for abs(Bp) in pFile definition
                            prof1d[f'ion.{ik}.rotation.diamagnetic'] = 1e3 * (omgeb - omeg - omegp)

                    except KeyError:
                        printw(f'Some velocity info missing for pFile ion {(i + 1)}, so possible missing info for ODS ion {ik}')
                        continue

        return ods

    def from_omas(self, ods=None, time_index=0):
        """
        translate OMAS data structure to OMFITpFile

        :param ods: input ods to take data from

        :param time_index: time index to which data is added

        :return: ods
        """
        # Lyons:  I've used my own rotation variable definitions here, until IMAS properly defines them
        #         Note that negative signs and sign_Ip are needed to make
        #           omega_perp, omega_dia, and omega_ExB have the same sign convention

        from omfit_classes.omfit_eqdsk import OMFITgeqdsk
        from omas import ODS, omas_environment
        from omfit_classes.utils_math import atomic_element

        cocosio = 1  # pFile's have CCW phi and CW theta

        # get required quantities

        with omas_environment(ods, cocosio=cocosio):
            sign_Ip = np.sign(ods['equilibrium']['time_slice'][time_index]['global_quantities']['ip'])

        prof1d = ods['core_profiles']['profiles_1d'][time_index]

        # determine main ion by highest mean thermal density
        den_mk = 0.0
        ions = list(prof1d['ion'].keys())
        ck = None
        for k in ions:
            den_k = np.mean(prof1d['ion'][k]['density_thermal'])
            if den_k > den_mk:
                # define main ion
                den_mk = den_k
                mk = k
            if prof1d['ion'][k]['label'] == 'C':
                # define carbon ion (if found)
                ck = k

        # move main ion to end
        ions.remove(mk)
        ions += [mk]

        # move carbon ion to the beginning
        if ck is not None:
            ions.remove(ck)
            ions = [ck] + ions

        Nions = len(ions) + 1
        self['N Z A'] = OMFITncData()
        self['N Z A']['description'] = 'N Z A of ION SPECIES'
        self['N Z A']['N'] = np.zeros(Nions)
        self['N Z A']['Z'] = np.zeros(Nions)
        self['N Z A']['A'] = np.zeros(Nions)

        quants = [
            ('ne', 'electrons.density_thermal', 1e-20),
            ('te', 'electrons.temperature', 1e-3),
            ('ni', f'ion.{mk}.density_thermal', 1e-20),
            ('ti', f'ion.{mk}.temperature', 1e-3),
            ('nb', f'ion.{mk}.density_fast', 1e-20),
            ('pb', [f'ion.{mk}.pressure_fast_perpendicular', f'ion.{mk}.pressure_fast_parallel'], [2e-3, 1e-3]),
            ('ptot', ['pressure_perpendicular', 'pressure_parallel'], [2e-3, 1e-3]),
            ('omgeb', 'omega0', sign_Ip * 1e-3),  # sign_Ip accounts for abs(Bp) in pFile definition
            ('omevb', 'electrons.rotation.perpendicular', 1e-3),
            ('omepp', 'electrons.rotation.diamagnetic', sign_Ip * 1e-3),  # sign_Ip accounts for abs(dpsi) in pFile definition
            ('ommvb', f'ion.{mk}.rotation.perpendicular', 1e-3),
            ('ommpp', f'ion.{mk}.rotation.diamagnetic', sign_Ip * 1e-3),
        ]  # sign_Ip accounts for abs(dpsi) in pFile definition

        for i, k in enumerate(ions):
            # currently we don't store charge state information, so Z = N
            N = prof1d['ion'][k]['element'][0]['z_n']
            A = prof1d['ion'][k]['element'][0]['a']
            if k == mk:
                # main and beam ions
                self['N Z A']['N'][-1] = self['N Z A']['N'][-2] = N
                self['N Z A']['Z'][-1] = self['N Z A']['Z'][-2] = N
                self['N Z A']['A'][-1] = self['N Z A']['A'][-2] = A
            else:
                # impurity ions
                self['N Z A']['N'][i] = N
                self['N Z A']['Z'][i] = N
                self['N Z A']['A'][i] = A

                pk = i + 1  # iterate and use for pfile indexing
                if f'nz{pk}' not in self:
                    for key, desc, units in [
                        (f'nz{pk}', 'Density', '10^20/m^3'),
                        (f'vtor{pk}', 'Toroidal velocity', 'km/s'),
                        (f'vpol{pk}', 'Toroidal velocity', 'km/s'),
                    ]:
                        self[key] = OMFITncData()
                        self[key]['data'] = np.array([0])
                        self[key]['description'] = desc + f' of the #{pk} impurity species'
                        self[key]['psinorm'] = np.array([0])
                        self[key]['units'] = units
                        self[key]['derivative'] = np.array([0])

                quants += [(f'nz{pk}', f'ion.{k}.density_thermal', 1e-20)]

        # load gEQDSK from ODS
        # Need to identify correct time.
        gEQDSK = OMFITgeqdsk('g0.0').from_omas(ods, time_index=time_index)
        gtime = ods[f'equilibrium.time_slice.{time_index}.time']
        if gtime != prof1d['time']:
            printw("Warning: The time corresponding to the equilibrium and the profile is mismatched!")
            printw(f"    Please check your input ods!")
            printw(
                f"    For time_index = {time_index}, the equilibrium has time = {gtime}, and the core_profile has time = {prof1d['time']}."
            )

        # load data from ODS
        with omas_environment(ods, cocosio=cocosio):
            psi1D = interp1e(
                ods[f'equilibrium.time_slice.{time_index}.profiles_1d.rho_tor_norm'],
                ods[f'equilibrium.time_slice.{time_index}.profiles_1d.psi'],
            )(ods[f'core_profiles.profiles_1d.{time_index}.grid.rho_tor_norm'])
            coordsio = {f'equilibrium.time_slice.{time_index}.profiles_1d.psi': psi1D}

        with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):
            prof1d = ods['core_profiles']['profiles_1d'][time_index]
            # pFiles are on psinorm grid but core_profiles data on rho_tor_norm gird
            rhotn = ods['equilibrium']['time_slice'][time_index]['profiles_1d']['rho_tor_norm']
            psi = ods['equilibrium']['time_slice'][time_index]['profiles_1d']['psi']
            psib = np.interp(1.0, rhotn, psi)  # in case grid extends beyond rhotn = 1.
            psin = (psi - psi[0]) / (psib - psi[0])

            for q_p, q_ods, fac in quants:
                self[q_p]['psinorm'] = psin
                try:
                    if isinstance(q_ods, list):
                        self[q_p]['data'] = 0.0 * psin
                        for i, qo in enumerate(q_ods):
                            self[q_p]['data'] += fac[i] * nominal_values(prof1d[qo])
                    else:
                        self[q_p]['data'] = fac * nominal_values(prof1d[q_ods])
                except ValueError:
                    self[q_p]['data'] = 0.0 * psin

            # calc auxiliary quantities from gEQDSK['fluxSurfaces']
            psin_eq = np.linspace(0.0, 1.0, len(gEQDSK['PRES']))
            R = np.interp(psin, psin_eq, gEQDSK['fluxSurfaces']['midplane']['R'])
            Bt = np.interp(psin, psin_eq, gEQDSK['fluxSurfaces']['midplane']['Bt'])
            Bp = np.interp(psin, psin_eq, gEQDSK['fluxSurfaces']['midplane']['Bp'])

            self['er']['psinorm'] = psin
            self['er']['data'] = R * abs(Bp) * self['omgeb']['data']  # pFile Er same sign as omgeb

            zero_array = 0.0 * psin

            for ik, k in enumerate(ions):
                ik += 1
                if k != mk:
                    # these are all as they're defined in pFile
                    kpol = None
                    omegp = None
                    vpol = None
                    omgvb = None
                    omeg = None
                    vtor = None
                    omgpp = None
                    missing = []

                    if f'ion.{k}.rotation.parallel_stream_function' in prof1d:
                        kpol = 1e-3 * nominal_values(prof1d[f'ion.{k}.rotation.parallel_stream_function'])
                        omegp = -Bt * kpol / R
                        vpol = sign_Ip * kpol * Bp  # sign_Ip accounts for pFile definition

                    if f'ion.{k}.rotation_frequency_tor' in prof1d:
                        omeg = 1e-3 * nominal_values(prof1d[f'ion.{k}.rotation_frequency_tor'])

                    if f'ion.{k}.rotation.perpendicular' in prof1d:
                        omgvb = 1e-3 * nominal_values(prof1d[f'ion.{k}.rotation.perpendicular'])

                    if f'ion.{k}.rotation.diamagnetic' in prof1d:
                        # sign_Ip accounts for abs(dpsi) in pFile definition
                        omgpp = -1e-3 * sign_Ip * nominal_values(prof1d[f'ion.{k}.rotation.diamagnetic'])

                    omgeb = self['omgeb']['data']
                    if (omgvb is None) and (omeg is not None) and (omegp is not None):
                        omgvb = omeg + omegp

                    if (not np.any(omgeb)) and (omgpp is not None) and (omgvb is not None):
                        omgeb = omgpp + sign_Ip * omgvb

                    if omeg is None and omgvb is not None and omegp is not None:
                        omeg = omgvb - omegp

                    if omeg is not None:
                        vtor = R * omeg
                        if omgpp is None:
                            # sign_Ip accounts pFile definition
                            omgpp = omgeb - sign_Ip * omgvb

                    if vpol is None and f'ion.{k}.velocity.poloidal' in prof1d:
                        vpol = 1e-3 * nominal_values(prof1d[f'ion.{k}.velocity.poloidal'])

                    if vtor is None and f'ion.{k}.velocity.toroidal' in prof1d:
                        vtor = 1e-3 * nominal_values(prof1d[f'ion.{k}.velocity.toroidal'])

                    # Calculate fallback omevb and ommvb
                    omevb = self['omevb']['data']  # These are in params above and will be present, but may be all zero
                    omepp = self['omepp']['data']
                    ommvb = self['ommvb']['data']
                    ommpp = self['ommpp']['data']

                    if (not np.any(omevb)) and (omepp is not None) and np.any(omgeb):
                        omevb = sign_Ip * (omgeb - omepp)
                    if (not np.any(ommvb)) and (ommpp is not None) and np.any(omgeb):
                        ommvb = sign_Ip * (omgeb - ommpp)

                    params = [(f'vpol{ik}', vpol), (f'vtor{ik}', vtor)]
                    if ik == 1:
                        params += [
                            ('kpol', kpol),
                            ('omegp', omegp),
                            ('omgvb', omgvb),
                            ('omeg', omeg),
                            ('omgpp', omgpp),
                            ('omevb', omevb),
                            ('ommvb', ommvb),
                            ('omgeb', omgeb),
                        ]

                    for name, val in params:
                        self[name]['psinorm'] = psin
                        if val is not None:
                            self[name]['data'] = val
                        else:
                            self[name]['data'] = 0.0 * psin
                            missing += [name]

                    for name in missing:
                        printw(f"pFile.from_omas: {name} could not be defined")

        for key in list(self.keys()):
            if key != 'N Z A':
                if len(self[key]['data']) == 1:
                    del self[key]
                else:
                    self[key]['derivative'] = deriv(self[key]['psinorm'], self[key]['data'])

        # Hahm-Burrell shearing rate
        #        self['omghb'] = OMFITncData()
        #        self['omghb']['data'] = 1e-3*(R*Bp)**2*self['omgeb']['derivative']
        #        self['omghb']['data'] /= abs(gEQDSK['SIBRY']-gEQDSK['SIMAG'])*np.sqrt(Bt**2 + Bp**2)
        #        self['omghb']['description'] = self.descriptions['omghb']
        #        self['omghb']['psinorm'] = psin
        #        self['omghb']['units'] = self.units['omghb']
        #        self['omghb']['derivative'] = deriv(self['omghb']['psinorm'], self['omghb']['data'])
        #        printw('Hahm-Burrell shearing rate not written to pFile')

        return self


# OMAS extra_structures
# omega0 is kept for backward compatibility
_extra_structures = {
    'core_profiles': {
        "core_profiles.profiles_1d[:].omega0": {
            "coordinates": ["core_profiles.profiles_1d[:].grid.rho_tor_norm"],
            "data_type": "FLT_1D",
            "documentation": "ExB plasma rotation",
            "full_path": "core_profiles/profiles_1d(itime)/omega0(:)",
            "data_type": "FLT_1D",
            "units": "rad/s",
            "cocos_signal": "TOR",
        },
        "core_profiles.profiles_1d[:].electrons.rotation.perpendicular": {
            "coordinates": ["core_profiles.profiles_1d[:].grid.rho_tor_norm"],
            "data_type": "FLT_1D",
            "documentation": "electron perpendicular VxB rotation",
            "full_path": "core_profiles/profiles_1d(itime)/electrons/rotation/perpendicular(:)",
            "data_type": "FLT_1D",
            "units": "rad/s",
            "cocos_signal": "TOR",
        },
        "core_profiles.profiles_1d[:].electrons.rotation.diamagnetic": {
            "coordinates": ["core_profiles.profiles_1d[:].grid.rho_tor_norm"],
            "data_type": "FLT_1D",
            "documentation": "electron diamagnetic rotation",
            "full_path": "core_profiles/profiles_1d(itime)/electrons/rotation/diamagnetic(:)",
            "data_type": "FLT_1D",
            "units": "rad/s",
            "cocos_signal": "TOR",
        },
        "core_profiles.profiles_1d[:].ion[:].rotation.perpendicular": {
            "coordinates": ["core_profiles.profiles_1d[:].grid.rho_tor_norm"],
            "data_type": "FLT_1D",
            "documentation": "ion perpendicular VxB rotation",
            "full_path": "core_profiles/profiles_1d(itime)/ion(i1)/rotation/perpendicular(:)",
            "data_type": "FLT_1D",
            "units": "rad/s",
            "cocos_signal": "TOR",
        },
        "core_profiles.profiles_1d[:].ion[:].rotation.diamagnetic": {
            "coordinates": ["core_profiles.profiles_1d[:].grid.rho_tor_norm"],
            "data_type": "FLT_1D",
            "documentation": "ion diamagnetic rotation",
            "full_path": "core_profiles/profiles_1d(itime)/ion(i1)/rotation/diamagnetic(:)",
            "data_type": "FLT_1D",
            "units": "rad/s",
            "cocos_signal": "TOR",
        },
        "core_profiles.profiles_1d[:].ion[:].rotation.parallel_stream_function": {
            "coordinates": ["core_profiles.profiles_1d[:].grid.rho_tor_norm"],
            "data_type": "FLT_1D",
            "documentation": "ion parallel stream function",
            "full_path": "core_profiles/profiles_1d(itime)/ion(i1)/rotation/parallel_stream_function(:)",
            "data_type": "FLT_1D",
            "units": "rad/s"
            # no COCOS transformation
        },
    }
}
omas.omas_utils._structures = {}
omas.omas_utils._structures_dict = {}
if not hasattr(omas.omas_utils, '_extra_structures'):
    omas.omas_utils._extra_structures = {}
for _ids in _extra_structures:
    for _item in _extra_structures[_ids]:
        _extra_structures[_ids][_item]['lifecycle_status'] = 'omfit'
    omas.omas_utils._extra_structures.setdefault(_ids, {}).update(_extra_structures[_ids])

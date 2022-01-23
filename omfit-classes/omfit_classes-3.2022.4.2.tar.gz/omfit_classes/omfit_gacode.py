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

from omfit_classes.omfit_base import OMFITcollection
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.utils_math import integz
from omfit_classes.omfit_gapy import OMFITgacode, OMFITinputprofiles, OMFITinputgacode
from omfit_classes.omfit_json import SettingsName

# Explicit imports
import numpy as np
from scipy import interpolate

try:
    import pygacode.tgyro.data
    import pygacode.gyro.data_plot
    import pygacode.cgyro.data_plot
    import pygacode.neo.data
except ImportError:
    __all__ = []
else:
    __all__ = ['OMFITgacode', 'OMFITtgyro', 'OMFITgyro', 'OMFITcgyro', 'OMFITneo', 'copy_gacode_module_settings']

    def om_fig(func):
        """This is a decorator to pass a clean figure to the gacode plot routines"""

        def new_func(*args, **kw):
            if 'fig' not in kw or kw['fig'] is None:
                kw['fig'] = pyplot.figure()
            return func(*args, **kw)

        return new_func

    class OMFITtgyro(SortedDict, OMFITobject, pygacode.tgyro.data.tgyrodata):
        """
        Class used to interface with TGYRO results directory

        :param filename: directory where the TGYRO result files are stored.
            The data in this directory will be loaded upon creation of the object.
        """

        def __init__(self, filename=None, **kw):
            kw['file_type'] = 'dir'
            OMFITobject.__init__(self, filename, **kw)
            self.OMFITproperties.pop('file_type', 'dir')
            SortedDict.__init__(self, sorted=True)
            self.dynaLoad = True

        @dynaLoad
        def load(self):
            filename = self.filename
            pygacode.tgyro.data.tgyrodata.__init__(self, filename, verbose=False)

            # The tgyrodata class operates on self.data, this will be handled by __getattr__
            self.update(self.data)
            delattr(self, 'data')

            # Add (derived) quantities
            # minor radius
            self['a'] = self['rmin'][0][1] / self['r/a'][0][1]
            # Derivative on sparse TGYRO grid: a*d(w0)/dr (Note conversion of c_s, below, from m/s to cm/s)
            self['a/dw0dr'] = -self['a*gamma_p/cs'] * (100 * self['c_s']) / self['a'] / self['rmaj/a']
            # Rotation on sparse TGYRO grid: w0 (Note conversion of c_s, below, from m/s to cm/s)
            self['w0'] = self['M=wR/cs'] * (100 * self['c_s']) / (self['a'] * self['rmaj/a'])
            # Convergence
            if 'convergence' not in self:
                convergence_items = []
                for item in list(self.keys()):
                    if re.match('E([emp]flux_.*)', item):
                        convergence_items.append(item)
                # new TGYRO format with multiple ions particle evolution
                if len(convergence_items):
                    for k, item in enumerate(convergence_items):
                        if k == 0:
                            self['convergence'] = self[item].sum(axis=1)
                        else:
                            self['convergence'] += self[item].sum(axis=1)
                # old TGYRO format, with electron particle evolution
                else:
                    if 'residual' not in self:
                        self.get_residual()
                    if 'convergence' not in self:
                        self['convergence'] = self['residual'][1::2, :, :].sum(axis=0).sum(axis=1)
            # input.gacode is not used by TGYROData, so it may not be in the directory
            if os.path.exists(filename + os.sep + 'input.gacode'):
                tmp = OMFITinputgacode(filename + os.sep + 'input.gacode')
                tmp.load()
                self.dataProfiles = dict()
                self.dataProfiles.update(tmp)
            else:
                self.dataProfiles = None

            # if multiple input.gacode.XXX are found, read them in
            # the 0th profile is always input.gacode (if it is there, and it should!)
            # the last profiles is always input.gacode.new (if it is there)
            input_gacode_evo = self['profiles_evolution'] = OMFITcollection()
            if os.path.exists(self.filename + os.sep + 'input.gacode'):
                input_gacode_evo[0] = OMFITinputgacode(self.filename + os.sep + 'input.gacode')
            tmp = glob.glob(self.filename + os.sep + 'input.gacode.[0-9]*')
            tmp = sorted(tmp, key=lambda x: int(x.split('.')[-1]))
            for k, item in enumerate(tmp):
                input_gacode_evo[k + 1] = OMFITinputgacode(item)
            if os.path.exists(self.filename + os.sep + 'input.gacode.new'):
                input_gacode_evo[len(input_gacode_evo)] = OMFITinputgacode(self.filename + os.sep + 'input.gacode.new')

            # parsing of 'out.tgyro.ped' if it exists and is filled with something
            if (
                'betan' not in self
                and os.path.exists(self.filename + os.sep + 'out.tgyro.ped')
                and os.stat(self.filename + os.sep + 'out.tgyro.ped').st_size
            ):
                with open(self.filename + os.sep + 'out.tgyro.ped', 'r') as f:
                    tmp = f.readlines()
                data = np.array([list(map(float, x.split())) for x in tmp[2::3]])
                for k, name in enumerate(tmp[0].split()):
                    if name in ['r_top/a', 'betan', 'psi_top', 'p_top', 't_top', 'n_top']:
                        self[name] = data[:, k]

            # parsing out.tgyro.run
            if os.path.exists(self.filename + os.sep + 'out.tgyro.run'):
                with open(self.filename + os.sep + 'out.tgyro.run', 'r') as f:
                    self['run_log'] = f.read()

        def plot_profiles_evolution(self, quantity=None, x='rho', ax=None, colors=None):
            """
            plot evolution in input.gacode.XXX of the quantity

            :param quantity: quantity to be plotted (plots Te, Ti, ne, omega0 if `quantity is None`)

            :param x: x axis, typically `rho` or `rmin`

            :param ax: axis to plot in (only if `quantity is not None`)

            :param colors:
            """
            if 'profiles_evolution' not in self:
                printw('input.gacode.{0...} files not in TGYRO output directory')
                return

            what = [['Te', 'Ti_1'], [], ['ne'] + ['ni_%d' % k for k in range(1, 11)], ['omega0']]

            if not quantity:
                fig = figure()
            for k, items in enumerate(what):
                colors0 = colors
                if colors is None:
                    colors0 = list(default_colorblind_line_cycle)
                if not quantity:
                    ax = pyplot.subplot(2, 2, k + 1)
                elif ax is None:
                    ax = pyplot.gca()
                i = 0
                for k1, item in enumerate(items):
                    if quantity and item != quantity:
                        continue
                    itemName = item
                    if re.match('.*_[0-9]+$', item):
                        if int(item.split('_')[1]) in self['profiles_evolution'][0]['IONS']:
                            ion = self['profiles_evolution'][0]['IONS'][int(item.split('_')[1])]
                            itemName = item.split('_')[0][:-1] + ion[0] + ' ' + ion[3]
                        else:
                            continue
                    color = colors0[i]['color']
                    ax.plot(nan, nan, color=color, label=itemName)
                    ax.plot(nan, nan, color=color, ls='--', label=itemName + ' experiment')
                    for line in list(self['profiles_evolution'].keys()):
                        xx = self['profiles_evolution'][line][x]
                        yy = self['profiles_evolution'][line][item].copy()
                        ax.plot(xx, yy, color=color, alpha=(line + 1.0) / len(self['profiles_evolution']))
                    ax.plot(self['profiles_evolution'][0][x], self['profiles_evolution'][item][:, 0], color=color, ls='--')
                    i += 1
                try:
                    ax.legend(loc=0).draggable(True)
                except Exception:
                    pass
            if not quantity:
                pyplot.subplot(2, 2, 2)
                pyplot.semilogy(self['convergence'], color='k')

        @dynaLoad
        def __getattr__(self, attr):
            if attr == 'data':
                return self  # The TGYROdata class operates on self.data
            elif attr == 'n_iterations':
                return self.data['rho'].shape[0] - 1
            else:
                raise AttributeError('bad attribute `%s`' % attr)

        def get_residual(self):
            def get_gacode_residual():
                fn = 'out.tgyro.residual'
                with open(self.dir + '/' + fn, 'r') as f:
                    data = f.readlines()
                if len(data) == 0:
                    if self.n_iterations == 0:
                        print("WARNING: out.tgyro.residual is blank")
                        return 0
                    raise OSError("out.tgyro.residual is blank")

                # Data dimensions
                nr = self.n_r
                nb = self.n_iterations + 1
                nc = 1 + 2 * self.n_evolve

                numdata = np.zeros((nc, nb, nr - 1), dtype=float)
                cdata = np.zeros((nb), dtype=float)

                new_format = os.path.exists(self.dir + '/out.tgyro.profile_i1')
                nh = [1, 2][new_format]
                if not new_format:
                    nr = nr - 1
                self.data['convergence'] = []
                for ib in range(nb):
                    try:
                        if new_format:
                            tags = data[ib * (nr + nh)].split()  # Contains overall residual
                        cdata[ib] = float(data[ib * (nr + nh) + nh - 1].split(':')[1].split()[1])
                    except Exception:
                        raise ValueError("out.tgyro.residual shorter than expected")

                    for ir in range(nr - 1):
                        row = data[ib * (nr + nh) + ir + nh].split()
                        for ic in range(nc):
                            numdata[ic, ib, ir] = row[ic]

                self.data['convergence'] = cdata
                self.data['residual'] = numdata
                return self.data

            valid = False
            data = get_gacode_residual()
            if data is not 0:
                valid = True
            if not valid:
                # Data dimensions
                nr = self.n_r
                nb = self.n_iterations + 1
                # 9 = 1+2*n_evolve, where n_evolve=4 (ti,te,ne,er)
                nc = 1 + 2 * self.n_evolve
                numdata = np.zeros((nc, nb, nr - 1), dtype=float)
                self.data['residual'] = numdata * np.nan

        def sprofile(self, what, nf0=201, x='r/a', verbose=False):
            """
            This function returns smooth profiles on a uniform ['r/a', 'rho', 'rmin', 'rmaj/a'] grid

            :param what: what profile to return ['r/a', 'rho', 'rmin', 'rmaj/a', 'te', 'a/LTe', 'ne', 'a/Lne' , 'ti', 'a/LTi', 'ni', 'a/Lni', 'M=wR/cs']

            :param nf0: number of points

            :param x: return profiles equally spaced in 'r/a', 'rho', 'rmin', 'rmaj/a'

            :param verbose: plotting of the `what` quantity

            :return: `what` quantity (nf0 x niterations) at the `x` locations

            Note: all TGYRO quantities are naturally defined over 'r/a'

            **example**

            >> tmp=OMFITtgyro('...')
            >> x='rho'
            >> y='te'
            >> pyplot.plot(tmp[x].T,tmp[y].T,'or')
            >> X=tmp.sprofile(x, nf0=201, x=x, verbose=False)
            >> Y=tmp.sprofile(y, nf0=201, x=x, verbose=False)
            >> pyplot.plot(X,Y,'b',alpha=0.25)

            """
            n = self.n_iterations

            # rf0 contains the value of `x` uniformly spaced
            rf0 = np.linspace(self.data[x][0][0], self.data[x][0][-1], int(nf0 * self.data[x][0][-1]))
            if what == x:
                return rf0

            # rf0 contains the value of r/a uniformly spaced in 'x'
            if x != 'r/a':
                rf0 = interpolate.interp1d(self.data[x][0], self.data['r/a'][0])(rf0)

            if what in ['r/a', 'rho', 'rmin', 'rmaj/a']:
                return interpolate.interp1d(self.data['r/a'][0], self.data[what][0])(rf0)

            quantity = {'ne': 'a/Lne', 'te': 'a/Lte', 'w0': 'a/dw0dr'}
            quantityScaleLen = {'a/Lne': 'ne', 'a/Lte': 'te', 'w0': 'a/dw0dr'}
            for spec in range(1, 10):
                for quant in ['t', 'n']:
                    quantity['%si%d' % (quant, spec)] = 'a/L%si%d' % (quant, spec)
                    quantityScaleLen['a/L%si%d' % (quant, spec)] = '%si%d' % (quant, spec)

            pf0 = np.zeros((len(rf0), n))
            for l in range(n):

                if what == 'w0':
                    pf0[:, l] = interpolate.interp1d(
                        self.data['r/a'][0], integrate.cumtrapz(self.data[quantity[what]][l], self.data['r/a'][l], initial=0), kind=1
                    )(rf0)
                    pf0[:, l] = pf0[:, l] - pf0[-1, l] + self.data[what][l][-1]
                elif what in quantity:
                    pf0[:, l] = integz(
                        self.data['r/a'][l], self.data[quantity[what]][l], self.data['r/a'][l][-1], self.data[what][l][-1], rf0
                    )
                elif what in quantityScaleLen:
                    pf0[:, l] = interpolate.interp1d(self.data['r/a'][0], self.data[what][l])(rf0)
                else:
                    raise ValueError("Quantity '" + what + "' is not in %s" % repr(list(quantity.keys()) + list(quantity.values())))

            if verbose:
                figure()
                plotc(rf0, pf0)
                pyplot.ylabel(what)
                pyplot.xlabel(r'$' + x + '$')

            return pf0

        def jacobian(self, return_matrix=False):
            """
            :param return_matrix: return jacobian as dictionary or matrix

            :return: dictionary with the jacobians of the last iteration as calculated by TGYRO
            """
            data = {}
            with open(self.filename + os.sep + 'out.tgyro.jacobian', 'r') as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith('r/a'):
                    pass
                else:
                    data.setdefault(line.split()[0], []).append(float(line.split()[1]))
            for k in data:
                data[k] = np.array(data[k])

            if not return_matrix:
                return data

            else:
                neq = 0
                X = []
                Y = []
                for ky, y in enumerate(['Qe', 'Qi', 'Ge', 'Pi']):
                    for kx, x in enumerate(['zTe', 'zTi', 'zne', 'w0']):
                        if 'd%s/d%s' % (y, x) in data:
                            X.append(x)
                            Y.append(y)
                            neq += 1
                neq = int(np.sqrt(neq))
                X = unsorted_unique(X)
                Y = unsorted_unique(Y)

                d = np.zeros((neq, neq, len(self['rho'][0, :]) - 1))
                for rr in range(len(self['rho'][0, :]) - 1):
                    for ky, y in enumerate(Y):
                        for kx, x in enumerate(X):
                            d[ky, kx, rr] = data['d%s/d%s' % (y, x)][rr]
                    for ky, y in enumerate(Y):
                        n = abs(d[ky, ky, rr])
                        d[ky, :, rr] = d[ky, :, rr] / n
                        d[:, ky, rr] = d[:, ky, rr] / n
                        d[ky, ky, rr] = 1.0
                return d

        @dynaLoad
        def plot(self, **kw):
            """
            This function plots ne, ni, te, ti for every iteration run by TGYRO

            :return: None
            """
            pyplot.clf()
            pyplot.gcf().canvas.set_window_title('TGYRO results')

            # whatTgyroDict:
            # keys will be the titles of each subplot
            # ['name'][0] -> input.gacode variable name (output.dataProfiles)
            # ['name'][1] -> out.tgyro.*    variable name (output.sprofile and in output.keys())
            whatTgyroDict = SortedDict()
            whatTgyroDict['$n_e$'] = {'normalization': [1, 1e13], 'unit': '$10^{19}/m^3$', 'name': ['ne', 'ne']}
            whatTgyroDict['$n_{i1}$'] = {'normalization': [1, 1e13], 'unit': '$10^{19}/m^3$', 'name': ['ni_1', 'ni1']}
            whatTgyroDict['convergence'] = {}
            whatTgyroDict['$T_e$'] = {'normalization': [1, 1], 'unit': '$keV$', 'name': ['Te', 'te']}
            whatTgyroDict['$T_i$'] = {'normalization': [1, 1], 'unit': '$keV$', 'name': ['Ti_1', 'ti1']}
            whatTgyroDict[r'$\omega_0$'] = {'normalization': [1e3, 1e3], 'unit': '$krad/s$', 'name': ['omega0', 'w0']}

            for k, whatTgyro in enumerate(whatTgyroDict.keys()):
                pyplot.gcf().add_subplot(2, 3, k + 1)
                if whatTgyro == 'convergence':
                    pyplot.semilogy(self['convergence'], color='k')
                    pyplot.xlim([0, len(self['convergence']) - 1])
                    pyplot.title('Convergence')
                    continue
                if self.dataProfiles is not None:
                    pyplot.plot(
                        self.dataProfiles['rho'],
                        self.dataProfiles[whatTgyroDict[whatTgyro]['name'][0]] / whatTgyroDict[whatTgyro]['normalization'][0],
                        'k--',
                        linewidth=3,
                    )
                plotc(
                    self.sprofile('rho', nf0=201, x='rho'),
                    self.sprofile(whatTgyroDict[whatTgyro]['name'][1], nf0=201, x='rho') / whatTgyroDict[whatTgyro]['normalization'][1],
                )
                pyplot.plot(self['rho'].T, self[whatTgyroDict[whatTgyro]['name'][1]].T / whatTgyroDict[whatTgyro]['normalization'][1], '.r')
                if k in [3, 4, 5]:
                    pyplot.xlabel('$\\rho$')
                pyplot.title('%s [%s]' % (whatTgyro, whatTgyroDict[whatTgyro]['unit']))

        def plotFigure(self, *args, **kw):
            """
            This function plots ne, ni, te, ti for every iteration run by TGYRO

            :return: None
            """
            pyplot.figure(*args)
            return self.plot(**kw)

        def calcQ(self, it_index=-1):
            """
            Calculate and return the fusion energy gain factor, Q,
            assuming D+T->alpha+neutron is the main reaction

            :param it_index: Indicates for which iteration to calculate Q
            """
            # Factor of 5 in following is because total fusion power = 5*alpha power, correct for DT
            return (
                (self['p_i_fus'][it_index, -1] + self['p_e_fus'][it_index, -1])
                * 5
                / (self['p_i_aux'][it_index, -1] + self['p_e_aux'][it_index, -1])
            )

    class OMFITgyro(SortedDict, OMFITobject, pygacode.gyro.data_plot.gyrodata_plot):
        """
        Class used to interface with GYRO results directory

        This class extends the OMFITgyro class with the save/load methods of the OMFITpath class
        so that the save/load carries all the original files from the GYRO output

        :param filename: directory where the GYRO result files are stored.
            The data in this directory will be loaded upon creation of the object.
        :param extra_files: Any extra files that should be downloaded from the remote location
        :param test_mode: Don't raise an exception if out.gyro.t is not present (and abort loading at that point)
        """

        def __init__(self, filename=None, extra_files=[], test_mode=False, **kw):

            if isinstance(filename, (list, tuple)):
                kw['tunnel'] = filename[2]
                kw['server'] = filename[1]
                filename = filename[0]

            if ',' not in filename:
                # output in alphabetical order
                # This is copied from an ls for reg01 with three fields for phi, A|| and Aperp as well as nl01
                outputs = [
                    'bin.gyro.field_rms',
                    'bin.gyro.gbflux_i',
                    'bin.gyro.gbflux_n',
                    'bin.gyro.kxkyspec',
                    'bin.gyro.moment_u',
                    'bin.gyro.moment_zero',
                    'gyrotest_flag',
                    'halt',
                    'input.gyro',
                    'input.gyro.gen',
                    'out.gyro.balloon_a',
                    'out.gyro.balloon_aperp',
                    'out.gyro.balloon_epar',
                    'out.gyro.balloon_phi',
                    'out.gyro.efficiency',
                    'out.gyro.error',
                    'out.gyro.freq',
                    'out.gyro.geometry_arrays',
                    'out.gyro.localdump',
                    'out.gyro.memory',
                    'out.gyro.phase_space',
                    'out.gyro.prec',
                    'out.gyro.profile',
                    'out.gyro.radial_op',
                    'out.gyro.run',
                    'out.gyro.star',
                    'out.gyro.t',
                    'out.gyro.timing',
                    'out.gyro.units',
                    'out.gyro.version',
                    'fieldeigen.out',
                ]

                # input.gacode
                outputs += ['input.gacode']

                # Batch files
                outputs += ['batch.src', 'batch.out', 'batch.err']

                outputs += extra_files
                filename = ','.join([filename + os.sep + x for x in outputs])

            kw['file_type'] = 'dir'
            OMFITobject.__init__(self, filename, **kw)
            self.OMFITproperties.pop('file_type', 'dir')
            SortedDict.__init__(self, sorted=True)
            self.test_mode = test_mode
            self.dynaLoad = True

        @dynaLoad
        def load(self):
            filename = self.filename
            if os.path.exists(filename + '/input.gyro.gen'):
                self['input.gyro.gen'] = OMFITgacode(filename + '/input.gyro.gen')
            if os.path.exists(filename + '/out.gyro.run'):
                self['out.gyro.run'] = OMFITascii(filename + '/out.gyro.run')
            if os.path.exists(filename + '/out.gyro.version'):
                self['out.gyro.version'] = OMFITascii(filename + '/out.gyro.version')
            if os.path.exists(filename + '/out.gyro.efficiency'):
                self['out.gyro.efficiency'] = OMFITascii(filename + '/out.gyro.efficiency')
            if os.path.exists(filename + '/batch.src'):
                self['batch.src'] = OMFITascii(filename + '/batch.src')
            if os.path.exists(filename + '/batch.out'):
                self['batch.out'] = OMFITascii(filename + '/batch.out')
            if os.path.exists(filename + '/batch.err'):
                self['batch.err'] = OMFITascii(filename + '/batch.err')
            if not os.path.exists(filename + '/out.gyro.t') and self.test_mode:
                self.dynaLoad = False
                printw('No out.gyro.t file: aborting the load')
                return
            pygacode.gyro.data.GYROData.__init__(self, filename)

            # create keys from self attributes
            # add input.gacode as object to gyro class here if needed

            # common variables
            self['originalFilename'] = self.originalFilename
            self['profile'] = self.profile
            self['geometry'] = self.geometry
            self['n_r'] = self.profile['n_x']
            self['n_bnd'] = self.profile['n_explicit_damp']
            n_n = self.profile['n_n']
            tor_n = self.profile['n0'] + self.profile['d_n'] * np.linspace(0, n_n - 1, n_n)
            self['tor_n'] = tor_n.astype(int)
            self['kyrhos'] = self.profile['kt_rho']
            self['n_n'] = n_n
            self['n_theta_plot'] = self.profile['n_theta_plot']
            self['r'] = self.profile['r']
            self['t'] = self.t['(c_s/a)t']
            self['n_time'] = self.t['n_time']

            # units
            self['units'] = dict()
            self['units']['m_ref'] = self.units[0]  # kg
            self['units']['b_unit'] = self.units[1]  # T
            self['units']['a'] = self.units[2]  # m
            self['units']['csD/a'] = self.units[3]  # 1/s
            self['units']['csD'] = self.units[4]  # m/s
            self['units']['Te'] = self.units[5]  # keV
            self['units']['ne'] = self.units[6]  # 10^19/m^3
            self['units']['rho_sD'] = self.units[7]  # m
            self['units']['chi_gBD'] = self.units[8]  # m^2/s
            self['units']['Gamma_gBD'] = self.units[9]  # 0.6244e22/m^2/s = MW/keV/m^2
            self['units']['Q_gBD'] = self.units[10]  # MW/m^2
            self['units']['Pi_gBD'] = self.units[11]  # Nm/m^2
            self['units']['S_gBD'] = self.units[12]  # MW/m^3

            # tags
            self['tagfield'] = self.tagfield
            self['tagfieldtext'] = self.tagfieldtext[0 : self.profile['n_field']]
            self['tagmom'] = self.tagmom
            self['tagspec'] = self.tagspec

            # create a Boolean flag indicating whether run is linear or nonlinear
            if self.profile['nonlinear_flag'] == 0:
                self['nonlinear_run'] = False
            else:
                self['nonlinear_run'] = True

            if os.path.exists(self.filename + '/fieldeigen.out'):
                self['eigensolver'] = True
            else:
                self['eigensolver'] = False

            # fluctuations
            self['flucs'] = dict()

            # load other results based on whether run is nonlinear or linear (either initial value or eigen solver)
            if self['nonlinear_run']:
                # load n=0 and n>0 potential
                self['field_rms'] = dict()
                if hasattr(self, 'field_rms'):
                    tmp = xarray.DataArray(
                        self.field_rms / np.average(self['profile']['rho_s']),
                        coords={'potential': ['n=0', 'n>0'], 't': self['t']},
                        dims=['potential', 't'],
                        attrs={'comment': 'NL zonal and n>0 potential'},
                    )
                    self['field_rms']['n=0'] = tmp.isel(potential=0)
                    self['field_rms']['n>0'] = tmp.isel(potential=1)
                # load fluxes vs. ky and time
                self['flux_t'] = dict()
                self['flux_ky'] = dict()
                self['flux_r'] = dict()
                self.read_gbflux_n()
                if hasattr(self, 'gbflux_n'):
                    tmp = xarray.DataArray(
                        self.gbflux_n,
                        coords={
                            'species': self['tagspec'],
                            'field': self['tagfieldtext'],
                            'moment': ['n', 'e', 'v', 's'],
                            'ky': self['kyrhos'],
                            't': self['t'],
                        },
                        dims=['species', 'field', 'moment', 'ky', 't'],
                        attrs={'comment': 'NL gyroBohm-normalized fluxes vs (ky,t)'},
                    )
                    self['flux_ky']['particle'] = tmp.isel(moment=0)
                    self['flux_ky']['energy'] = tmp.isel(moment=1)
                    self['flux_ky']['momentum'] = tmp.isel(moment=2)
                    self['flux_t']['particle'] = self['flux_ky']['particle'].sum(dim='ky')
                    self['flux_t']['energy'] = self['flux_ky']['energy'].sum(dim='ky')
                    self['flux_t']['momentum'] = self['flux_ky']['momentum'].sum(dim='ky')
                self.read_gbflux_i()
                if hasattr(self, 'gbflux_i'):
                    tmp = xarray.DataArray(
                        self.gbflux_i,
                        coords={
                            'species': self['tagspec'],
                            'field': self['tagfieldtext'],
                            'moment': ['n', 'e', 'v', 's'],
                            'r': self['r'],
                            't': self['t'],
                        },
                        dims=['species', 'field', 'moment', 'r', 't'],
                        attrs={'comment': 'NL gyroBohm-normalized fluxes vs (r,t)'},
                    )
                    self['flux_r']['particle'] = tmp.isel(moment=0)
                    self['flux_r']['energy'] = tmp.isel(moment=1)
                    self['flux_r']['momentum'] = tmp.isel(moment=2)
            else:
                # load frequency
                self['freq'] = dict()
                if hasattr(self, 'freq'):
                    self['freq']['omega'] = xarray.DataArray(
                        self.freq['(a/c_s)w'], coords={'ky': self['kyrhos'], 't': self['t']}, dims=['ky', 't']
                    )
                    self['freq']['gamma'] = xarray.DataArray(
                        self.freq['(a/c_s)gamma'], coords={'ky': self['kyrhos'], 't': self['t']}, dims=['ky', 't']
                    )
                    self['freq']['omega_err'] = xarray.DataArray(
                        self.freq['err(a/c_s)w'], coords={'ky': self['kyrhos'], 't': self['t']}, dims=['ky', 't']
                    )
                    self['freq']['gamma_err'] = xarray.DataArray(
                        self.freq['err(a/c_s)gamma'], coords={'ky': self['kyrhos'], 't': self['t']}, dims=['ky', 't']
                    )

                # eigenvalue solver
                if self['eigensolver']:
                    data = np.loadtxt(self.filename + '/fieldeigen.out')
                    self['t'] = np.arange(data.shape[0])
                    self['n_time'] = data.shape[0]

                    self['freq']['gamma'] = xarray.DataArray(
                        np.atleast_2d(data[:, 0]),
                        coords={'ky': self['kyrhos'], 't': self['t']},
                        dims=['ky', 't'],
                        attrs={'comment': 'Eigenvalue growth rate'},
                    )

                    self['freq']['omega'] = xarray.DataArray(
                        np.atleast_2d(data[:, 1]),
                        coords={'ky': self['kyrhos'], 't': self['t']},
                        dims=['ky', 't'],
                        attrs={'comment': 'Eigenvalue frequency'},
                    )

                    self['freq']['eigensolver_err'] = xarray.DataArray(
                        np.atleast_2d(data[:, 3]),
                        coords={'ky': self['kyrhos'], 't': self['t']},
                        dims=['ky', 't'],
                        attrs={'comment': 'Eigensolver error'},
                    )
                    del self['freq']['gamma_err']
                    del self['freq']['omega_err']

                # load ballooning modes
                if self['n_n'] == 1:
                    try:
                        self.read_balloon()
                        n_p = self.profile['n_x'] / self.profile['box_multiplier']
                        n_ang = self.profile['n_theta_plot'] * n_p
                        x_ball = -(1.0 + n_p) + 2.0 * n_p * np.arange(n_ang) / float(n_ang)  # theta_balloon/pi
                        self['balloon'] = {'theta_b_over_pi': x_ball}
                    except Exception:
                        self.balloon = dict()
                        print('no ballooning mode files')

                    if self['eigensolver']:
                        balloon_field = np.zeros((int(n_ang), self['n_time']), dtype=complex)
                        if 'balloon_phi' in self.balloon:
                            balloon_field[:, -1] = self.balloon['balloon_phi'][:, 0, -1]
                            self['balloon']['balloon_phi'] = xarray.DataArray(
                                balloon_field,
                                coords={'theta_b_over_pi': self['balloon']['theta_b_over_pi'], 't': self['t']},
                                dims=['theta_b_over_pi', 't'],
                            )
                        if 'balloon_a' in self.balloon:
                            balloon_field[:, -1] = self.balloon['balloon_a'][:, 0, -1]
                            self['balloon']['balloon_apar'] = xarray.DataArray(
                                balloon_field,
                                coords={'theta_b_over_pi': self['balloon']['theta_b_over_pi'], 't': self['t']},
                                dims=['theta_b_over_pi', 't'],
                            )
                        if 'balloon_aperp' in self.balloon:
                            balloon_field[:, -1] = self.balloon['balloon_aperp'][:, 0, -1]
                            self['balloon']['balloon_bpar'] = xarray.DataArray(
                                balloon_field,
                                coords={'theta_b_over_pi': self['balloon']['theta_b_over_pi'], 't': self['t']},
                                dims=['theta_b_over_pi', 't'],
                            )
                        if 'balloon_epar' in self.balloon:
                            balloon_field[:, -1] = self.balloon['balloon_epar'][:, 0, -1]
                            self['balloon']['balloon_epar'] = xarray.DataArray(
                                balloon_field,
                                coords={'theta_b_over_pi': self['balloon']['theta_b_over_pi'], 't': self['t']},
                                dims=['theta_b_over_pi', 't'],
                            )
                    else:
                        if 'balloon_phi' in self.balloon:
                            self['balloon']['balloon_phi'] = xarray.DataArray(
                                self.balloon['balloon_phi'][:, 0, :],
                                coords={'theta_b_over_pi': self['balloon']['theta_b_over_pi'], 't': self['t']},
                                dims=['theta_b_over_pi', 't'],
                            )
                        if 'balloon_a' in self.balloon:
                            self['balloon']['balloon_apar'] = xarray.DataArray(
                                self.balloon['balloon_a'][:, 0, :],
                                coords={'theta_b_over_pi': self['balloon']['theta_b_over_pi'], 't': self['t']},
                                dims=['theta_b_over_pi', 't'],
                            )
                        if 'balloon_aperp' in self.balloon:
                            self['balloon']['balloon_bpar'] = xarray.DataArray(
                                self.balloon['balloon_aperp'][:, 0, :],
                                coords={'theta_b_over_pi': self['balloon']['theta_b_over_pi'], 't': self['t']},
                                dims=['theta_b_over_pi', 't'],
                            )
                        if 'balloon_epar' in self.balloon:
                            self['balloon']['balloon_epar'] = xarray.DataArray(
                                self.balloon['balloon_epar'][:, 0, :],
                                coords={'theta_b_over_pi': self['balloon']['theta_b_over_pi'], 't': self['t']},
                                dims=['theta_b_over_pi', 't'],
                            )
                # load quasilinear flux weights
                self['qlflux_ky'] = dict()
                self.read_gbflux_i()
                if hasattr(self, 'gbflux'):
                    gbflux = np.zeros((len(self['tagspec']), len(self['tagfieldtext']), 4, self['n_time']))
                    gbflux[:, :, :, -1] = self.gbflux[:, :, :, -1]
                    if self['eigensolver']:
                        tmp = xarray.DataArray(
                            gbflux,
                            coords={
                                'species': self['tagspec'],
                                'field': self['tagfieldtext'],
                                'moment': ['n', 'e', 'v', 's'],
                                't': self['t'],
                            },
                            dims=['species', 'field', 'moment', 't'],
                            attrs={'comment': 'QL gyroBohm-normalized fluxes vs (t)'},
                        )
                    else:
                        tmp = xarray.DataArray(
                            self.gbflux,
                            coords={
                                'species': self['tagspec'],
                                'field': self['tagfieldtext'],
                                'moment': ['n', 'e', 'v', 's'],
                                't': self['t'],
                            },
                            dims=['species', 'field', 'moment', 't'],
                            attrs={'comment': 'QL gyroBohm-normalized fluxes vs (t)'},
                        )

                    self['qlflux_ky']['particle'] = tmp.isel(moment=0)
                    self['qlflux_ky']['energy'] = tmp.isel(moment=1)
                    self['qlflux_ky']['momentum'] = tmp.isel(moment=2)
                    self['qlflux_ky']['exchange'] = tmp.isel(moment=3)

    for item in dir(pygacode.gyro.data_plot.gyrodata_plot):
        func = getattr(pygacode.gyro.data_plot.gyrodata_plot, item)
        if item.startswith('plot') and 'fig' in inspect.getfullargspec(func).args:
            wrappedfunc = om_fig(func)
            setattr(OMFITgyro, item, wrappedfunc)

    class OMFITcgyro(SortedDict, OMFITobject, pygacode.cgyro.data_plot.cgyrodata_plot):
        """
        Class used to interface with CGYRO results directory

        :param filename: directory where the CGYRO result files are stored.
            The data in this directory will be loaded upon creation of the object.
        :param extra_files: Any extra files that should be downloaded from the remote location
        :param test_mode: Don't raise an exception if out.gyro.t is not present (and abort loading at that point)
        """

        def __init__(self, filename=None, extra_files=[], test_mode=False, **kw):

            if isinstance(filename, (list, tuple)):
                kw['tunnel'] = filename[2]
                kw['server'] = filename[1]
                filename = filename[0]
            if not is_localhost(kw.get('server', 'localhost')):
                outputs = [
                    'input.cgyro',
                    'input.cgyro.gen',
                    'out.cgyro.aparb',
                    'out.cgyro.bparb',
                    'out.cgyro.egrid',
                    'out.cgyro.equilibrium',
                    'out.cgyro.freq',
                    'out.cgyro.geo',
                    'out.cgyro.grids',
                    'out.cgyro.hosts',
                    'out.cgyro.info',
                    'out.cgyro.ky_flux',
                    'out.cgyro.lky_flux_e',
                    'out.cgyro.lky_flux_n',
                    'out.cgyro.lky_flux_v',
                    'out.cgyro.memory',
                    'out.cgyro.mpi',
                    'out.cgyro.phib',
                    'out.cgyro.prec',
                    'out.cgyro.res_ver',
                    'out.cgyro.tag',
                    'out.cgyro.time',
                    'out.cgyro.timing',
                    'out.cgyro.version',
                ]

                # binary files
                outputs += [
                    'bin.cgyro.aparb',
                    'bin.cgyro.bparb',
                    'bin.cgyro.freq',
                    'bin.cgyro.geo',
                    'bin.cgyro.kxky_apar',
                    'bin.cgyro.kxky_bpar',
                    'bin.cgyro.kxky_e',
                    'bin.cgyro.kxky_flux_e',
                    'bin.cgyro.kxky_n',
                    'bin.cgyro.kxky_phi',
                    'bin.cgyro.ky_flux',
                    'bin.cgyro.ky_cflux',
                    'bin.cgyro.ky_flux_e',
                    'bin.cgyro.ky_flux_n',
                    'bin.cgyro.ky_flux_v',
                    'bin.cgyro.phib',
                ]

                # input.gacode
                outputs += ['input.gacode']

                # batch files
                outputs += ['batch.src', 'batch.out', 'batch.err']

                outputs += extra_files
                filename = ','.join([filename + os.sep + x for x in outputs])
            kw['file_type'] = 'dir'
            OMFITobject.__init__(self, filename, **kw)
            self.OMFITproperties.pop('file_type', 'dir')
            SortedDict.__init__(self, sorted=True)
            self.test_mode = test_mode
            self.dynaLoad = True

        @dynaLoad
        def load(self):
            filename = self.filename
            if os.path.exists(filename + '/input.cgyro.gen'):
                self['input.cgyro.gen'] = OMFITgacode(filename + '/input.cgyro.gen')
            if os.path.exists(filename + '/out.cgyro.info'):
                self['out.cgyro.info'] = OMFITascii(filename + '/out.cgyro.info')
            if os.path.exists(filename + '/out.cgyro.mpi'):
                self['out.cgyro.mpi'] = OMFITascii(filename + '/out.cgyro.mpi')
            if os.path.exists(filename + '/out.cgyro.version'):
                self['out.cgyro.version'] = OMFITascii(filename + '/out.cgyro.version')
            if os.path.exists(filename + '/batch.src'):
                self['batch.src'] = OMFITascii(filename + '/batch.src')
            if os.path.exists(filename + '/batch.out'):
                self['batch.out'] = OMFITascii(filename + '/batch.out')
            if os.path.exists(filename + '/batch.err'):
                self['batch.err'] = OMFITascii(filename + '/batch.err')
            if not os.path.exists(filename + '/out.cgyro.time') and self.test_mode:
                self.dynaLoad = False
                printw('No out.cgyro.time file: aborting the load')
                return
            pygacode.cgyro.data.cgyrodata.__init__(self, filename + '/')

            # common variables
            self['originalFilename'] = self.originalFilename
            self['n_r'] = self.n_radial
            self['n_n'] = self.n_n
            self['n_species'] = self.n_species
            self['n_field'] = self.n_field
            self['n_theta'] = self.n_theta
            self['n_energy'] = self.n_energy
            self['n_xi'] = self.n_xi
            self['m_box'] = self.m_box
            self['length'] = self.length
            self['n_global'] = self.n_global
            self['theta_plot'] = self.theta_plot

            self['kyrhos'] = self.ky
            self['kxrhos'] = self.kx
            self['t'] = self.t
            self['n_time'] = self.n_time
            self['field_tags'] = ['Phi', 'Apar', 'Bpar'][0 : self.n_field]
            self['species_tags'] = list(map(str, np.arange(self.n_species) + 1))

            # units- need to test if out.cgyro.equilibrium loaded
            # most equilibrium parameters in self['input.cgyro.gen']
            # what to do about gyroBohm units
            self['units'] = dict()
            if hasattr(self, 'b_unit'):
                self['units']['b_unit'] = self.b_unit  # T
                self['units']['a'] = self.a_meters  # m
                self['units']['vth_norm'] = self.vth_norm  # m/s
                self['units']['Te_norm'] = self.temp_norm  # keV
                self['units']['ne_norm'] = self.dens_norm  # 10^19/m^3
                self['units']['mass_norm'] = self.mass_norm  # 10^-27 kg^-1?
                self['units']['rho_star'] = self.rho_star_norm
                self['units']['gamma_gb_norm'] = self.gamma_gb_norm  # 10^19 m^-2 s^-1
                self['units']['q_gb_norm'] = self.q_gb_norm  # MW / m^2
                self['units']['pi_gb_norm'] = self.pi_gb_norm  # N / m
                self['units']['Z'] = self.z
                self['units']['mass'] = self.mass  # relative to species 1
                self['units']['dens'] = self.dens
                self['units']['temp'] = self.temp
                self['units']['dlnndr'] = self.dlnndr
                self['units']['dlntdr'] = self.dlntdr
                self['units']['nu'] = self.nu

            # create a Boolean flag indicating whether run is linear or nonlinear
            if self['input.cgyro.gen']['NONLINEAR_FLAG'] == 0:
                self['nonlinear_run'] = False
            else:
                self['nonlinear_run'] = True

            # fluctuations
            self['flucs'] = dict()

            # CGYRO always saves frequencies, even for NL runs
            self['freq'] = dict()
            if hasattr(self, 'freq'):
                # gamma and omega are arrays of size [n_n, n_time]
                tmp = xarray.DataArray(
                    self.freq, coords={'type': ['omega', 'gamma'], 'ky': self['kyrhos'], 't': self['t']}, dims=['type', 'ky', 't']
                )
                self['freq']['omega'] = tmp.isel(type=0)
                self['freq']['gamma'] = tmp.isel(type=1)

            # load other results based on whether run is linear or nonlinear
            self.getflux()
            if self['nonlinear_run']:
                self['flux_t'] = dict()
                self['flux_ky'] = dict()
                if hasattr(self, 'ky_flux'):
                    tmp = xarray.DataArray(
                        self.ky_flux,
                        coords={
                            'species': self['species_tags'],
                            'moment': ['n', 'e', 'v'],
                            'field': self['field_tags'],
                            'ky': self['kyrhos'],
                            't': self['t'],
                        },
                        dims=['species', 'moment', 'field', 'ky', 't'],
                        attrs={'comment': 'NL gyroBohm-normalized fluxes'},
                    )
                    self['flux_ky']['particle'] = tmp.isel(moment=0)
                    self['flux_ky']['energy'] = tmp.isel(moment=1)
                    self['flux_ky']['momentum'] = tmp.isel(moment=2)
                    self['flux_t']['particle'] = self['flux_ky']['particle'].sum(dim='ky')
                    self['flux_t']['energy'] = self['flux_ky']['energy'].sum(dim='ky')
                    self['flux_t']['momentum'] = self['flux_ky']['momentum'].sum(dim='ky')
            else:
                # load ballooning modes. IFF n_radial == 1, ZF test, otherwise standard finite-ky
                if self.n_radial == 1:
                    ball_x = self.theta / np.pi
                    label_x = 'theta_over_pi'
                else:
                    ball_x = self.thetab / np.pi
                    label_x = 'theta_b_over_pi'
                self['balloon'] = {label_x: ball_x}
                if hasattr(self, 'phib'):
                    tmp = self.phib[0, :, :] + 1j * self.phib[1, :, :]
                    self['balloon']['balloon_phi'] = xarray.DataArray(
                        tmp, coords={label_x: self['balloon'][label_x], 't': self['t']}, dims=[label_x, 't']
                    )
                if hasattr(self, 'aparb'):
                    tmp = self.aparb[0, :, :] + 1j * self.aparb[1, :, :]
                    self['balloon']['balloon_apar'] = xarray.DataArray(
                        tmp, coords={label_x: self['balloon'][label_x], 't': self['t']}, dims=[label_x, 't']
                    )
                if hasattr(self, 'bparb'):
                    tmp = self.bparb[0, :, :] + 1j * self.bparb[1, :, :]
                    self['balloon']['balloon_bpar'] = xarray.DataArray(
                        tmp, coords={label_x: self['balloon'][label_x], 't': self['t']}, dims=[label_x, 't']
                    )

                # load quasilinear flux weights
                self['qlflux_ky'] = dict()
                if hasattr(self, 'ky_flux'):
                    tmp = xarray.DataArray(
                        self.ky_flux,
                        coords={
                            'species': self['species_tags'],
                            'moment': np.arange(3),
                            'field': self['field_tags'],
                            'ky': self['kyrhos'],
                            't': self['t'],
                        },
                        dims=['species', 'moment', 'field', 'ky', 't'],
                        attrs={'comment': 'quasilinear weights'},
                    )
                    # to be compatible with GYRO convention remove the dim=ky for the single ky
                    tmp = tmp.sum(dim='ky')
                    self['qlflux_ky']['particle'] = tmp.isel(moment=0)
                    self['qlflux_ky']['energy'] = tmp.isel(moment=1)
                    self['qlflux_ky']['momentum'] = tmp.isel(moment=2)
                    if len(tmp['moment']) == 4:
                        self['qlflux_ky']['exchange'] = tmp.isel(moment=3)

    for item in dir(pygacode.cgyro.data_plot.cgyrodata_plot):
        func = getattr(pygacode.cgyro.data_plot.cgyrodata_plot, item)
        if item.startswith('plot') and 'fig' in inspect.getfullargspec(func).args:
            wrappedfunc = om_fig(func)
            setattr(OMFITcgyro, item, wrappedfunc)

    class OMFITneo(SortedDict, OMFITobject, pygacode.neo.data.NEOData):
        """
        Class used to interface with NEO results directory

        :param filename: directory where the TGYRO result files are stored.
            The data in this directory will be loaded upon creation of the object.
        """

        def __init__(self, filename, **kw):
            kw['file_type'] = 'dir'
            OMFITobject.__init__(self, filename, **kw)
            self.OMFITproperties.pop('file_type', 'dir')
            SortedDict.__init__(self, sorted=True)
            self.dynaLoad = True

        @dynaLoad
        def load(self):
            pygacode.neo.data.NEOData.__init__(self, self.filename)

            self['neo_results'] = SortedDict()
            for k in [
                'equil',
                'expnorm',
                'grid',
                'phi',
                'rotation',
                'theory',
                'theory_nclass',
                'transport',
                'transport_gv',
                'transport_exp',
            ]:
                for key, v in list(getattr(self, k, {}).items()):
                    if key in self['neo_results'] and np.all(np.atleast_1d(self['neo_results'][key] != v)):
                        print('%s already added to neo_results' % key)
                    self['neo_results'][key] = v

            self['neo_files'] = SortedDict()
            for k in list(self.keys()):
                prefixes = ('out.neo', 'input', 'out.expro', 'OMFIT_run_')
                if k.startswith(prefixes):
                    self['neo_files'][k] = self[k]
                    del self[k]

    def copy_gacode_module_settings(root):
        """
        Utility function to sync all GACODE modules to use the same working environment

        :param root: GACODE module to use as template (if None only sets module['SETTINGS']['SETUP']['branch'])
        """
        from omfit_classes.omfit_base import OMFITexpression

        default_GACODE_branch = OMFITexpression(
            '''
version = 'tglf_sat2'
server = root['SETTINGS']['REMOTE_SETUP']['serverPicker']
if is_server(server, ['iris', 'saturn']):
    if version == 'pre_pygacode':
        return_variable = '/dev'
    elif version=='post_pygacode':
        return_variable = '/pygacode'
    else:
        return_variable = '/tglf_sat2'
elif is_server(server, 'portal'):
    if version == 'pre_pygacode':
        return_variable = '/unstable'
    elif version == 'post_pygacde':
        return_variable = '/pygacode'
    else:
        return_variable = '/tglf_sat2'
elif is_server(server, 'cori'):
    if version == 'pre_pygacode':
        raise ValueError(f'GACODE installation on {server} has not yet been updated to pre_gacode')
    else:
        return_variable = ''
else:
    if version == 'pre_pygacode':
        return_variable = ''
    else:
        raise ValueError(f'GACODE installation on {server} has not yet been updated to post_gacode')

    '''.strip()
        )

        for module in ['TGYRO_GACODE', 'TGLF_GACODE', 'GYRO_GACODE', 'PROFILES_GEN_GACODE', 'NEO_GACODE']:
            if module not in OMFIT:
                OMFIT.loadModule(module, "OMFIT['%s']" % module, withSubmodules=False, quiet=True)
            OMFIT[module]['SETTINGS']['SETUP']['branch'] = copy.deepcopy(default_GACODE_branch)
            if root is None:
                continue
            print('Copying executable and branch settings from %s to %s' % (root.ID[:-7], module[:-7]))
            OMFIT[module]['SETTINGS']['SETUP']['branch'] = copy.deepcopy(root['SETTINGS']['SETUP']['branch'])
            for item in root['SETTINGS']['REMOTE_SETUP']:
                if not isinstance(root['SETTINGS']['REMOTE_SETUP'][item], dict):
                    continue
                if item not in OMFIT[module]['SETTINGS']['REMOTE_SETUP']:
                    OMFIT[module]['SETTINGS']['REMOTE_SETUP'][item] = SettingsName()
                    for k in root['SETTINGS']['REMOTE_SETUP'][item]:
                        if k in OMFIT[module]['SETTINGS']['REMOTE_SETUP']['iris']:
                            OMFIT[module]['SETTINGS']['REMOTE_SETUP'][item][k] = copy.deepcopy(root['SETTINGS']['REMOTE_SETUP'][item][k])
                else:
                    OMFIT[module]['SETTINGS']['REMOTE_SETUP'][item]['executable'] = copy.deepcopy(
                        root['SETTINGS']['REMOTE_SETUP'][item]['executable']
                    )
            OMFIT[module]['SETTINGS']['REMOTE_SETUP']['saturn']['executable'] = OMFIT[module]['SETTINGS']['REMOTE_SETUP']['iris'][
                'executable'
            ]


############################################
if '__main__' == __name__:
    test_classes_main_header()
    sample_files = glob.glob(OMFITsrc + '/../samples/input*')
    eligble_samples = [fn for fn in sample_files if not (fn.endswith('jbs') or '_omfit' in fn)]
    fn = eligble_samples[0]  # Pick the first one
    f0 = OMFITgacode(fn)
    f0.load()

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

import numpy as np
from omfit_classes.omfit_path import OMFITpath
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.sortedDict import OMFITdataset
from omfit_classes.omfit_dir import OMFITdir
from omfit_classes.omfit_gacode import OMFITgacode
from omfit_classes.omfit_asciitable import OMFITasciitable

__all__ = [
    'OMFITtglfEPinput',
    'OMFITalphaInput',
    'OMFITtglf_eig_spectrum',
    'OMFITtglf_wavefunction',
    'OMFITtglf_flux_spectrum',
    'OMFITtglf_nete_crossphase_spectrum',
    'OMFITtglf_potential_spectrum',
    'OMFITtglf_fluct_spectrum',
    'OMFITtglf_intensity_spectrum',
    'OMFITtglf',
    'OMFITtglf_nsts_crossphase_spectrum',
    'sum_ky_spectrum',
]


class OMFITtglfEPinput(OMFITascii, SortedDict):
    '''
    Class used to read/write TGLFEP input files
    '''

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.read()

        widths = []
        for line in lines.split('\n'):
            if not len(line.strip()):
                continue
            try:
                if len(widths):
                    self['WIDTHS'] = widths
                value, key = line.split()
            except ValueError:  # not enough values to unpack
                widths.append(eval(line))
            else:
                if value == '.false.':
                    value = False
                elif value == '.true.':
                    value = True
                else:
                    value = eval(value)
                self[key] = value

    @dynaSave
    def save(self):
        txt = []
        for key, value in self.items():
            if key == 'WIDTHS':
                continue
            if value is False:
                value = '.false.'
            elif value is True:
                value = '.true.'
            txt.append(f'{value} {key}')
            if key == 'WIDTH_IN_FLAG' and 'WIDTHS' in self:
                txt.append('\n'.join(map(str, self['WIDTHS'])))
        with open(self.filename, 'w') as f:
            f.write('\n'.join(txt))


class OMFITalphaInput(OMFITascii, SortedDict):
    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.read().strip().split('\n')
        comment = lines[0]
        data = np.array(list(map(eval, lines[1:])))
        self['comment'] = comment
        self['data'] = data


def get_ky_spectrum(filename):
    with open(filename, 'r') as f:
        content = f.readlines()
    content = ''.join(content[2:]).split()
    ky = np.array(content, dtype=float)
    return ky


class OMFITtglf_eig_spectrum(OMFITdataset, OMFITascii):
    def __init__(self, filename, ky_file, nmodes, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.nmodes = self.OMFITproperties['nmodes'] = nmodes

    @dynaLoad
    def load(self):
        nmodes = self.nmodes
        with open(self.filename, 'r') as f:
            content = f.readlines()
        content = ''.join(content[2:]).split()
        ky = get_ky_spectrum(self.ky_file)
        gamma = []
        freq = []
        for k in range(self.nmodes):
            gamma.append(np.array(content[2 * k :: nmodes * 2], dtype=float))
            freq.append(np.array(content[2 * k + 1 :: nmodes * 2], dtype=float))
        gamma = np.array(gamma)
        freq = np.array(freq)
        gamma = DataArray(gamma, dims=('mode_num', 'ky'), coords={'ky': ky, 'mode_num': np.arange(nmodes) + 1})
        freq = DataArray(freq, dims=('mode_num', 'ky'), coords={'ky': ky, 'mode_num': np.arange(nmodes) + 1})
        self.update({'gamma': gamma, 'freq': freq})

    def plot(self, axs=None):
        '''
        Plot the eigenvalue spectrum as growth rate and frequency

        :param axs: A length 2 sequence of matplotlib axes (growth rate, frequency)
        '''
        if axs is None:
            fig, axs = pyplot.subplots(2, 1, num=pyplot.gcf().number, squeeze=True, sharex=True)
        else:
            fig = axs[0].get_figure()
        for k in range(self.nmodes):
            axs[0].plot(self['ky'], self['gamma(%d)' % (k + 1)], label='Growth rate $\\gamma_{%d}$' % (k + 1))
            axs[1].plot(self['ky'], self['freq(%d)' % (k + 1)], label='Frequency $\\omega_{%d}$' % (k + 1))
        axs[0].set_ylabel('Growth rate $\\gamma$')
        with warnings.catch_warnings():
            # We don't care if matplotlib has an underflow while drawing
            warnings.filterwarnings('ignore', category=RuntimeWarning, message='underflow*')
            axs[0].set_yscale('symlog', linthreshy=0.01)
            axs[1].set_yscale('symlog', linthreshy=0.01)
            axs[1].set_ylabel('Frequency $\\omega$')
            axs[1].axhline(0, color='gray', ls='--')
            axs[1].set_xlabel('$k_\\perp \\rho$')
            axs[0].set_xscale('log')
            fig.canvas.draw()

    @dynaLoad
    def __getitem__(self, key):

        if key in self:
            return OMFITdataset.__getitem__(self, key)

        if key.startswith('gamma') and '(' in key:
            ind = int(key.split('(')[1].split(')')[0])
            return self['gamma'].sel(mode_num=ind).values

        if key.startswith('freq') and '(' in key:
            ind = int(key.split('(')[1].split(')')[0])
            return self['freq'].sel(mode_num=ind).values

        raise KeyError(key)


class OMFITtglf_wavefunction(OMFITascii, SortedDict):
    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        nmodes, nfields, npoints = list(map(int, lines[0].split()))
        self.nmodes = nmodes
        self.nfields = nfields
        keys = lines[1].split()
        self.headers = keys[1:]
        content = ''.join(lines[2:]).split()
        self['theta'] = np.array(content[0 :: nmodes * nfields * 2 + 1], dtype=float)
        for ik, k in enumerate(keys[1:]):
            for n in range(nmodes):
                self['%s(%d)' % (k, n + 1)] = np.array(content[2 * n * nfields + 1 + ik :: nmodes * nfields * 2 + 1], dtype=float)

    def plot(self):
        def pi_mult_formatter(x, pos):
            if x == 0:
                return '0'
            if x == np.pi:
                return r'$\pi$'
            if x == -np.pi:
                return r'$-\pi$'
            return r'$%d\pi$' % (int(round(x / np.pi, 0)))

        fig, axs = pyplot.subplots(self.nfields, self.nmodes, num=pyplot.gcf().number, sharex=True, sharey='row', squeeze=False)
        for n in range(self.nmodes):
            for ki, k in enumerate(self.headers):
                axs[int(ki // 2)][n].plot(self['theta'], self['%s(%d)' % (k, n + 1)], ls=['-', '--'][ki % 2])
                if n == 0:
                    axs[int(ki // 2)][n].set_ylabel(k.split('(')[1].split(')')[0])
                if ki == len(self.headers) - 1:
                    axs[int(ki // 2)][n].set_xlabel(r'$\theta$')
                    axs[int(ki // 2)][n].xaxis.set_major_locator(MultipleLocator(np.pi))
                    axs[int(ki // 2)][n].xaxis.set_major_formatter(FuncFormatter(pi_mult_formatter))
        fig.canvas.draw()


class OMFITtglf_flux_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the out.tglf.sum_flux_spectrum file and provide a convenient means for
    plotting it.

    :param filename: Path to the out.tglf.sum_flux_spectrum file

    :param n_species: Number of species

    :param n_fields: Number of fields
    '''

    def __init__(self, filename, ky_file, n_species, n_fields, spec_labels, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.n_species = self.OMFITproperties['n_species'] = n_species
        self.n_fields = self.OMFITproperties['n_fields'] = n_fields
        self.spec_labels = self.OMFITproperties['spec_labels'] = spec_labels

    @dynaLoad
    def load(self):
        ns = self.n_species
        nf = self.n_fields
        with open(self.filename) as f:
            content = f.read()
        tmpdict = SortedDict()
        ky = get_ky_spectrum(self.ky_file)
        tmpdict['ky'] = np.array(ky, dtype=float)
        for s in range(ns):
            for f in range(nf):
                ind1 = content.find('species =')
                ind2 = content.find('species =', ind1 + 10)
                data = content[ind1:ind2]
                first_two = data.splitlines()[:2]
                spec = int(first_two[0].split()[2])
                field = int(first_two[0].split()[5])
                spec_label = self.spec_labels[s]
                labels = [k.strip().replace('flux', '').strip() for k in first_two[1].split(',')]
                keys = [k + '_field_%d_spec_%s' % (field, spec_label) for k in labels]
                labels = labels[:]
                data = ''.join(data.splitlines()[2:]).split()
                for ki, k in enumerate(keys):
                    tmpdict[k] = np.array(data[ki :: len(keys)], dtype=float)
                content = content[content.find('species =', 10) :]
        ky = tmpdict['ky']
        tmparray = {}
        for label in labels:
            tmparray['_'.join(label.split())] = DataArray(
                np.zeros((ns, nf, len(ky))),
                dims=('species', 'field', 'ky'),
                coords={'species': self.spec_labels, 'field': ['phi', 'B_perp', 'B_parallel'][: self.n_fields], 'ky': ky},
            )
        for k, v in list(tmpdict.items()):
            if k == 'ky':
                continue
            quant, field = k.split('_field_', 2)
            quant = '_'.join(quant.split())
            field, spec_label = field.split('_spec_')
            spec_ind = self.spec_labels.index(spec_label)
            field_ind = int(field) - 1
            tmparray[quant][spec_ind, field_ind, :] = v
        self.update(tmparray)
        self._initialized = False
        self.labels = labels
        self._initialized = True

    @dynaLoad
    def plot(self, fn=None):
        '''
        Plot the flux spectra

        :param fn: A FigureNotebook instance
        '''
        ns = self.n_species
        nf = self.n_fields
        if fn is None:
            from omfit_plot import FigureNotebook

            tabbed = FigureNotebook(nfig=0, name='TGLF Flux Spectra')
        else:
            tabbed = fn
        for k in self.labels:
            fig = tabbed.add_figure(label=k)
            fig.suptitle(k)
            for s in range(ns):
                for f in range(nf):
                    if s == 0 and f == 0:
                        ax0 = ax = axr = fig.add_subplot(ns, nf, s * nf + f + 1)
                    elif f == 0:
                        ax = axr = fig.add_subplot(ns, nf, s * nf + f + 1, sharex=ax0)
                    else:
                        ax = fig.add_subplot(ns, nf, s * nf + f + 1, sharex=ax0, sharey=axr)
                    if f == 0:
                        ax.set_ylabel('Species: %s' % (self.spec_labels[s]))
                    if s == 0:
                        ax.set_title([r'$\phi$', r'$B_{\perp}$', r'$B_{\parallel}$'][f])
                    ax.plot(self['ky'], self[k + '_field_%d_spec_%s' % (f + 1, self.spec_labels[s])])
                    ax.set_xscale('log')
                    ax.axis('tight')
            autofmt_sharexy(fig=fig)
            fig.canvas.draw()

    @dynaLoad
    def __getitem__(self, key):
        if key in self:
            return OMFITdataset.__getitem__(self, key)
        try:
            quant, field = key.split('_field_', 2)
            quant = '_'.join(quant.split())
            field, spec_label = field.split('_spec_')
            spec_ind = self.spec_labels.index(spec_label)
            field_ind = int(field) - 1
            return self[quant].isel(field=field_ind, species=spec_ind)
        except Exception as _excp:
            print(_excp)
            raise KeyError(k)


class OMFITtglf_nete_crossphase_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the out.tglf.nete_crossphase_spectrum file and provide a convenient means for
    plotting it.

    :param filename: Path to the out.tglf.nete_crossphase_spectrum file

    :param nmodes: Number of modes computed by TGLF and used in the
    '''

    def __init__(self, filename, ky_file, nmodes, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.nmodes = self.OMFITproperties['nmodes'] = nmodes
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file

    @dynaLoad
    def load(self):
        nmodes = self.nmodes
        with open(self.filename, 'r') as f:
            content = f.readlines()
        content = ''.join(content[2:]).split()
        ky = get_ky_spectrum(self.ky_file)
        tmparray = []
        for k in range(self.nmodes):
            tmparray.append(np.array(content[k::nmodes], dtype=float))
        self.update({'nete': DataArray(np.array(tmparray), dims=('mode_num', 'ky'), coords={'mode_num': np.arange(nmodes) + 1, 'ky': ky})})

    def plot(self, ax=None):
        '''
        Plot the nete crossphase spectrum

        :param ax: A matplotlib axes instance
        '''
        if ax is None:
            fig, ax = pyplot.subplots(1, 1, squeeze=True)
        ky = self['ky']
        nmodes = self.nmodes
        for k in range(nmodes):
            ax.plot(ky, self['nete_crossphase_spectrum(%d)' % (k + 1)] / np.pi, label='Mode %d' % (k + 1))
        ax.legend(loc='best')
        ax.set_xscale('log')
        ax.set_xlabel(r'$k_y$')
        ax.set_ylabel(r'$\delta n_e$ $\delta T_e$ crossphase')
        ax.set_title(r'$\Theta_{\delta n_e\delta T_e}$')
        ax.axis('tight')
        ax.set_yticks(np.linspace(-np.pi / 2.0, np.pi / 2.0, 5), [r'$-\pi/2$', r'$\pi/4$', '0', r'$\pi/4$', r'$\pi/2$'])
        fmt = pyplot.ScalarFormatter()
        fmt.set_scientific(False)
        ax.xaxis.set_major_formatter(fmt)

    @dynaLoad
    def __getitem__(self, key):
        if key in self:
            return OMFITdataset.__getitem__(self, key)
        if 'nete_crossphase_spectrum(' in key:
            ind = int(key.split('(')[1].split(')')[0])
            return self['nete'].sel(mode_num=ind)
        raise KeyError(key)


class OMFITtglf_nsts_crossphase_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the out.tglf.nsts_crossphase_spectrum file and provide a convenient means for
    plotting it.

    :param filename: Path to the out.tglf.nsts_crossphase_spectrum file

    :param nmodes: Number of modes computed by TGLF and used in the
    '''

    def __init__(self, filename, ky_file, nmodes, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.nmodes = self.OMFITproperties['nmodes'] = nmodes

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            content = f.readlines()  # Remove the main header
        header = content.pop(0)
        nspec = int(header.strip().split()[-2])
        nmodes = self.nmodes
        for ci, c in enumerate(content):
            if ci == 0:
                continue
            if c.strip().startswith('species'):
                nk = ci - 2  # Two header lines
                break
        nsts = np.zeros((nspec, nmodes, nk), dtype=float)
        for si in range(nspec):
            block = ' '.join(content[(2 + nk) * si + 2 : (2 + nk) * (si + 1)]).split()
            if si == 0:
                ky = get_ky_spectrum(self.ky_file)
            for mi in range(nmodes):
                nsts[si, mi, :] = np.array(block[mi::nmodes], dtype=float)
        self.update(
            {
                'nsts': DataArray(
                    np.array(nsts),
                    dims=('spec', 'mode_num', 'ky'),
                    coords={'spec': np.arange(nspec) + 1, 'mode_num': np.arange(nmodes) + 1, 'ky': ky},
                )
            }
        )

    def plot(self, axs=None):
        '''
        Plot the nsts crossphase spectrum

        :param axs: A sequence of matplotlib axes instances of length len(self['spec'])
        '''
        ky = self['ky']
        nmodes = self.nmodes
        nspec = len(self['spec'])
        if axs is None or len(np.atleast1d(axs)) != nspec:
            fig, axs = pyplot.subplots(nspec, 1, squeeze=True, sharex=True)
        fmt = pyplot.ScalarFormatter()
        fmt.set_scientific(False)
        for si, spec in enumerate(self['spec']):
            ax = axs[si]
            ax.set_ylabel(r'$\delta n_s$ $\delta T_s$ crossphase')
            ax.xaxis.set_major_formatter(fmt)
            ax.set_yticks(np.linspace(-np.pi / 2.0, np.pi / 2.0, 5), [r'$-\pi/2$', r'$\pi/4$', '0', r'$\pi/4$', r'$\pi/2$'])
            for mi in range(nmodes):
                ax.plot(ky, self['nsts'].isel(spec=si, mode_num=mi) / np.pi, label='Mode %d' % (mi + 1))
        ax.legend(loc='best')
        ax.set_xscale('log')
        ax.set_xlabel(r'$k_y$')
        axs[0].set_title(r'$\Theta_{\delta n_s\delta T_s}$')
        ax.axis('tight')


class OMFITtglf_potential_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the potential fluctuation spectrum in out.tglf.potential_spectrum and
    provide a convenient means for plotting it.

    :param filename: Path to the out.tglf.potential_spectrum file
    '''

    def __init__(self, filename, ky_file, nmodes, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.nmodes = self.OMFITproperties['nmodes'] = nmodes

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        nmodes = self.nmodes
        ky = get_ky_spectrum(self.ky_file)
        description = lines[0]
        columns = [x.strip() for x in lines[1].split(',')]
        nc = len(columns)
        content = ''.join(lines[6:]).split()
        tmpdict = {}
        tmpdict['ky'] = np.array(ky, dtype=float)
        for ik, k in enumerate(columns):
            tmp = []
            for nm in range(nmodes):
                tmp.append(np.array(content[ik + nm * nc :: nmodes * nc], dtype=float))
            tmpdict[k] = tmp
        for k, v in list(tmpdict.items()):
            if k == 'ky':
                continue
            self[k] = xarray.DataArray(v, dims=('mode_num', 'ky'), coords={'ky': tmpdict['ky'], 'mode_num': np.arange(nmodes) + 1})

    @dynaLoad
    def plot(self, fn=None):
        '''
        Plot the fields

        :param fn: A FigureNotebook instance
        '''
        from omfit_plot import FigureNotebook

        if fn is None:
            fn = FigureNotebook('Field spectra')
        nmodes = self.nmodes
        fmt = pyplot.ScalarFormatter()
        fmt.set_scientific(False)
        for k in self.data_vars:
            for nm in range(nmodes):
                if not np.any(self[k] != 0):
                    continue
                fig, ax = fn.subplots(label=k + ', mode = ' + str(nm + 1), squeeze=True)
                ax.plot(self['ky'], self[k][nm])
                ax.set_xscale('log')
                ax.axis('tight')
                ax.xaxis.set_major_formatter(fmt)
                ax.set_xlabel('$k_y$')


class OMFITtglf_fluct_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the {density,temperature} fluctuation spectrum in
    out.tglf.{density,temperature}_spectrum  and provide a convenient means for
    plotting it.

    :param filename: Path to the out.tglf.{density,temperature}_spectrum file

    :param ns: Number of species

    :param label: Type of fluctuations ('density' or 'temperature')
    '''

    pretty_names = {'density': r'\delta n ', 'temperature': r'\delta T '}

    def __init__(self, filename, ky_file, ns, label, spec_labels, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.ns = self.OMFITproperties['ns'] = ns
        self.label = self.OMFITproperties['label'] = label
        self.spec_labels = self.OMFITproperties['spec_labels'] = spec_labels

    @dynaLoad
    def load(self):
        ns = self.ns
        with open(self.filename, 'r') as f:
            content = f.readlines()
        content = ''.join(content[2:]).split()
        ky = get_ky_spectrum(self.ky_file)
        tmplist = []
        for s in range(ns):
            tmplist.append(np.array(content[s::ns], dtype=float))
        self[self.label] = xarray.DataArray(np.array(tmplist), dims=('species', 'ky'), coords={'species': self.spec_labels, 'ky': ky})

    @dynaLoad
    def plot(self, axs=None):
        '''
        Plot the fluctuation spectrum

        :param axs: A list of matplotlib axes of length self.ns
        '''
        from matplotlib import pyplot
        from matplotlib.ticker import ScalarFormatter

        if axs is None:
            fig, axs = pyplot.subplots(self.ns, 1, sharex=True, sharey=True)
        else:
            if len(axs) != self.ns:
                raise ValueError('Must pass length %s list of axes' % self.ns)
            fig = axs[0].get_figure()
        ns = self.ns
        lab_base = self.pretty_names[self.label]
        for s in range(ns):
            ax = axs[s]
            ax.plot(self['ky'], self[self.label + '_spec_%d' % (s + 1)], label=r'$%s_{%s}$' % (lab_base, self.spec_labels[s]))
            ax.legend()
            ax.set_xscale('log')
            ax.axis('tight')
            fmt = pyplot.ScalarFormatter()
            fmt.set_scientific(False)
            ax.xaxis.set_major_formatter(fmt)
        ax.set_xlabel(r'$k_y$')
        try:
            autofmt_sharexy(fig=fig)
        except NameError:
            pass

    def __getitem__(self, key):
        if key in self:
            return OMFITdataset.__getitem__(self, key)
        if key.startswith(self.label + '_spec_'):
            spec_ind = int(key.split('_')[-1]) - 1
            return self[self.label].isel(species=spec_ind)
        raise KeyError(key)


class OMFITtglf_intensity_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the intensity fluctuation spectrum in
    out.tglf.{density,temperature}_spectrum  and provide a convenient means for
    plotting it.

    :param filename: Path to the out.tglf.{density,temperature}_spectrum file

    :param ns: Number of species

    :param label: Type of fluctuations ('density' or 'temperature')
    '''

    def __init__(self, filename, ky_file, nmodes, ns, spec_labels, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.nmodes = self.OMFITproperties['nmodes'] = nmodes
        self.ns = self.OMFITproperties['ns'] = ns
        self.spec_labels = self.OMFITproperties['spec_labels'] = spec_labels

    @dynaLoad
    def load(self):
        ns = self.ns
        nmodes = self.nmodes
        ky = get_ky_spectrum(self.ky_file)
        nky = len(ky)
        with open(self.filename, 'r') as f:
            dens, temp, vpara, enpara = np.loadtxt(f, skiprows=4, unpack=True)

        density = dens.reshape(ns, nky, nmodes)
        self['density'] = xarray.DataArray(
            density, dims=('ns', 'ky', 'nmodes'), coords={'ns': np.arange(ns) + 1, 'ky': ky, 'nmodes': np.arange(nmodes) + 1}
        )

        temperature = temp.reshape(ns, nky, nmodes)
        self['temperature'] = xarray.DataArray(
            temperature, dims=('ns', 'ky', 'nmodes'), coords={'ns': np.arange(ns) + 1, 'ky': ky, 'nmodes': np.arange(nmodes) + 1}
        )

        parallel_vel = vpara.reshape(ns, nky, nmodes)
        self['parallel_velocity'] = xarray.DataArray(
            parallel_vel, dims=('ns', 'ky', 'nmodes'), coords={'ns': np.arange(ns) + 1, 'ky': ky, 'nmodes': np.arange(nmodes) + 1}
        )

        parallel_energy = enpara.reshape(ns, nky, nmodes)
        self['parallel_energy'] = xarray.DataArray(
            parallel_energy, dims=('ns', 'ky', 'nmodes'), coords={'ns': np.arange(ns) + 1, 'ky': ky, 'nmodes': np.arange(nmodes) + 1}
        )


class OMFITtglf(OMFITdir):
    '''
    The purpose of this class is to be able to store all results from a given
    TGLF run in its native format, but parsing the important parts into the tree

    :param filename: Path to TGLF run
    '''

    def __init__(self, filename, **kw):
        printd('Calling OMFITtglf init', topic='OMFITtglf')
        OMFITdir.__init__(self, filename, **kw)
        printd('print self.keys():', list(self.keys()), topic='OMFITtglf')

        # remove 'OMFIT_run_command.sh'
        if 'OMFIT_run_command.sh' in self:
            del self['OMFIT_run_command.sh']

        # convert OMFITpath to OMFITascii
        for item in list(self.keys()):
            if isinstance(self[item], OMFITpath):
                self[item].__class__ = OMFITascii

        # rename input.tglf.gen to input.tglf
        if 'input.tglf.gen' in self:
            input_tglf = self['input.tglf'] = OMFITgacode(self['input.tglf.gen'].filename, noCopyToCWD=True)
            del self['input.tglf.gen']

        ns = self['input.tglf']['NS']
        from omfit_classes.utils_math import element_symbol

        self.spec_labels = [element_symbol(self['input.tglf']['ZS_%d' % x]).lower() for x in range(1, ns + 1)]

        # Note: as part of the parsing process, some entries under SELF are deleted.
        #      however we are not deleting the files these entries referred to,
        #      and because OMFITtglf inherits from OMFITdir these files will be carried
        #      through even if they are not visible in the OMFIT tree
        if np.any([str(k).startswith('out') for k in self]):
            self._parse_version()
            self._parse_prec()
            if not input_tglf['USE_TRANSPORT_MODEL']:  # linear run
                self['wavefunction'] = OMFITtglf_wavefunction(self['out.tglf.wavefunction'].filename, noCopyToCWD=True)
                del self['out.tglf.wavefunction']
            else:
                if 'out.tglf.eigenvalue_spectrum' in self:
                    self['eigenvalue_spectrum'] = OMFITtglf_eig_spectrum(
                        self['out.tglf.eigenvalue_spectrum'].filename,
                        self['out.tglf.ky_spectrum'].filename,
                        nmodes=input_tglf['NMODES'],
                        noCopyToCWD=True,
                    )
                    del self['out.tglf.eigenvalue_spectrum']
                try:
                    self._parse_potential_spectrum()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_flucs_spectra()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_flux_spectrum()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_nete_crossphase_spectrum()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_nsts_crossphase_spectrum()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_gbflux()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_run()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_intensity_spectrum()
                except Exception as _excp:
                    printe(_excp)

    def plot(self):
        for k in self:
            if hasattr(self[k], 'plot'):
                self[k].plot()

    def __delitem__(self, key):
        '''
        Deleting an item only deletes it from the tree, not from the underlying
        directory (which ``OMFITdir`` would do)
        '''
        super(OMFITdir, self).__delitem__(key)

    def _parse_flucs_spectra(self):
        '''
        Parse the fluctuation spectra in out.tglf.{density,temperature}_spectrum
        '''
        ns = self['input.tglf']['NS']
        result = SortedDict()
        for field in ['density', 'temperature']:
            if '%s_spectrum' % field in self:
                continue
            fn = 'out.tglf.%s_spectrum' % field
            if fn not in self:
                printe('No %s file to parse' % fn)
                continue
            self['%s_spectrum' % field] = OMFITtglf_fluct_spectrum(
                self[fn].filename, self['out.tglf.ky_spectrum'].filename, ns, field, self.spec_labels, noCopyToCWD=True
            )
            del self[fn]

    def _parse_potential_spectrum(self):
        '''
        Parse the potential fluctuation spectrum in out.tglf.potential_spectrum
        '''
        nm = self['input.tglf']['NMODES']
        if 'potential_spectrum' in self:
            return
        for fn in ['out.tglf.potential_spectrum', 'out.tglf.field_spectrum']:
            if fn not in self and fn == 'out.tglf.potential_spectrum':
                continue
            elif fn not in self and fn == 'out.tglf.field_spectrum':
                printe('No %s file to parse' % fn)
                return
        self['potential_spectrum'] = OMFITtglf_potential_spectrum(
            self[fn].filename, self['out.tglf.ky_spectrum'].filename, nmodes=nm, noCopyToCWD=True
        )
        del self[fn]

    def _parse_version(self):
        '''
        Parse the version information in out.tglf.version
        '''
        with open(self['out.tglf.version'].filename, 'r') as f:
            content = f.readlines()
        self['GACODE_VERSION'], self['GACODE_PLATFORM'], self['TIMESTAMP'] = [x.strip() for x in content[:3]]
        del self['out.tglf.version']

    def _parse_prec(self):
        '''
        Parse the out.tglf.prec file (a single number)
        '''
        self['regression_prec'] = None
        if 'out.tglf.prec' in self:
            with open(self['out.tglf.prec'].filename, 'r') as f:
                content = f.read()
            self['regression_prec'] = float(content.strip())
            del self['out.tglf.prec']

    def _parse_flux_spectrum(self):
        '''
        Parse the flux spectrum from out.tglf.sum_flux_spectrum
        '''
        ns = self['input.tglf']['NS']
        nf = 1 + self['input.tglf']['USE_BPAR'] + self['input.tglf']['USE_BPER']
        spec_labels = []
        spec_labels_counter = {}
        for item in range(1, ns + 1):
            A = self['input.tglf']['ZS_%d' % item]
            Z = self['input.tglf']['MASS_%d' % item] * 2
            try:
                element = str(element_symbol(A, Z).lower())
            except ValueError:
                element = 'lump'
            spec_labels_counter.setdefault(element, []).append(element)
            if len(spec_labels_counter[element]) == 1:
                spec_labels.append(element)
            else:
                spec_labels.append(element + '%d' % len(spec_labels_counter[element]))
        self['sum_flux_spectrum'] = OMFITtglf_flux_spectrum(
            self['out.tglf.sum_flux_spectrum'].filename, self['out.tglf.ky_spectrum'].filename, ns, nf, spec_labels, noCopyToCWD=True
        )
        del self['out.tglf.sum_flux_spectrum']

    def _parse_nete_crossphase_spectrum(self):
        '''
        Parse the cross phase spectrum from out.tglf.nete_crossphase_spectrum
        '''
        input_tglf = self['input.tglf']
        self['nete_crossphase_spectrum'] = OMFITtglf_nete_crossphase_spectrum(
            self['out.tglf.nete_crossphase_spectrum'].filename,
            self['out.tglf.ky_spectrum'].filename,
            nmodes=input_tglf['NMODES'],
            noCopyToCWD=True,
        )
        del self['out.tglf.nete_crossphase_spectrum']

    def _parse_nsts_crossphase_spectrum(self):
        '''
        Parse the cross phase spectrum from out.tglf.nsts_crossphase_spectrum
        '''
        input_tglf = self['input.tglf']
        self['nsts_crossphase_spectrum'] = OMFITtglf_nsts_crossphase_spectrum(
            self['out.tglf.nsts_crossphase_spectrum'].filename,
            self['out.tglf.ky_spectrum'].filename,
            nmodes=input_tglf['NMODES'],
            noCopyToCWD=True,
        )
        del self['out.tglf.nsts_crossphase_spectrum']

    def _parse_gbflux(self):
        '''
        Parse the flux from the out.tglf.gbflux file
        '''
        try:
            with open(self['out.tglf.gbflux'].filename) as f:
                content = f.read()
            tmp = list(map(float, content.split()))
            if 'std.tglf.gbflux' in self:
                with open(self['std.tglf.gbflux'].filename) as f:
                    content = f.read()
                tmp = uarray(tmp, list(map(float, content.split())))
            tmp = tolist(np.reshape(tmp, (4, -1)))
            species = ['elec'] + ['ion' + str(k) for k in range(1, len(tmp[0]))]
            tmp.insert(0, species)
            printd('Right before out.tglf.run creation', topic='OMFITtglf')
            result = SortedDict()
            result['header'] = ''
            result['columns'] = ['.', 'Gam/Gam_GB', 'Q/Q_GB', 'Pi/Pi_GB', 'S/S_GB']
            result['data'] = torecarray(tmp, result['columns'])
            if 'out.tglf.gbflux' in self:
                del self['out.tglf.gbflux']
            if 'std.tglf.gbflux' in self:
                del self['std.tglf.gbflux']
        except ValueError:
            result = OMFITasciitable(self.filename + '/out.tglf.gbflux', noCopyToCWD=True)
        self['gbflux'] = result

    def _parse_run(self):
        '''
        Parse the flux from the out.tglf.run file
        data should be same as gbflux file, but also includes local MHD stability
        '''
        with open(self['out.tglf.run'].filename) as f:
            lines = f.readlines()
        results = SortedDict()
        lines = [line[:-2] for line in lines]  # Remove '\n' from end of lines
        lines = [line.split() for line in lines]
        for line in lines:
            if 'D(R)' in line:
                for i, item in enumerate(line):
                    try:
                        results[line[i - 2]] = float(item)
                    except Exception:
                        pass
            elif 'Gam' in line[0]:
                results['.'] = line

            elif 'elec' in line[0] or 'ion' in line[0]:
                line_name = line[0]
                line_split = [float(l) for l in line[1:]]
                results[line_name] = line_split

        self['run'] = results
        del self['out.tglf.run']

    def _parse_intensity_spectrum(self):
        input_tglf = self['input.tglf']
        self['intensity_spectrum'] = OMFITtglf_intensity_spectrum(
            self.filename + '/out.tglf.intensity_spectrum',
            self['out.tglf.ky_spectrum'].filename,
            input_tglf['NMODES'],
            input_tglf['NS'],
            self.spec_labels,
        )
        del self['out.tglf.intensity_spectrum']

    def saturation_rule(self, saturation_rule_name):
        ky_spect = np.asarray(self['eigenvalue_spectrum']['ky'])
        gammas = np.asarray(self['eigenvalue_spectrum']['gamma']).T
        potential = self['potential_spectrum']['potential'].T.values

        with open(self['out.tglf.QL_flux_spectrum'].filename, 'r') as f:
            lines = f.readlines()
        nky, nm, ns, nfield, ntype = list(map(int, lines[3].split()))

        # QL weights
        with open(self['out.tglf.QL_flux_spectrum'].filename, 'r') as f:
            QL_data = np.loadtxt(f, skiprows=4, unpack=True).reshape(nky, nm, ns, nfield, ntype)
        particle_QL = QL_data[:, :, :, :, 0]
        energy_QL = QL_data[:, :, :, :, 1]
        toroidal_stress_QL = QL_data[:, :, :, :, 2]
        parallel_stress_QL = QL_data[:, :, :, :, 3]
        exchange_QL = QL_data[:, :, :, :, 4]

        with open(self['out.tglf.spectral_shift'].filename, 'r') as f:
            kx0_e = np.loadtxt(f, skiprows=5, unpack=True)

        with open(self['out.tglf.scalar_saturation_parameters'].filename, 'r') as f:
            ave_p0, B_unit, R_unit, q_unit, SAT_geo0_out, kx_geo0_out = np.loadtxt(f, skiprows=5, unpack=True)

        R_unit = np.ones((21, 2)) * R_unit

        return sum_ky_spectrum(
            sat_rule_in=saturation_rule_name,
            ky_spect=ky_spect,
            gp=gammas,
            ave_p0=ave_p0,
            R_unit=R_unit,
            kx0_e=kx0_e,
            potential=potential,
            particle_QL=particle_QL,
            energy_QL=energy_QL,
            toroidal_stress_QL=toroidal_stress_QL,
            parallel_stress_QL=parallel_stress_QL,
            exchange_QL=exchange_QL,
            etg_fact=1.25,
            c0=32.48,
            c1=0.534,
            exp1=1.547,
            cx_cy=0.56,
            alpha_x=1.15,
            **self['input.tglf'],
        )


def intensity_desat(ky_spect, gradP, q, taus_2):
    '''
    Dummy Experimental SATuration rule

    :param ky_spect: poloidal wave number [nk]

    :param gradP: P_PRIME_LOC (pressure gradient - see tglf inputs: https://gacode.io/tglf/tglf_list.html)

    :param q: absolute value of safety factor (i.e. Q_LOC)

    :param taus_2: ratio of T_main_ion/ T_e
    '''
    intensity_desat = (0.0082 / abs(gradP) + 0.1 * log10(ky_spect)) / (ky_spect ** ((3.81 * q) / (q + taus_2)))
    intensity_desat = np.c_[intensity_desat, intensity_desat]
    return intensity_desat


def intensity_sat0(
    ky_spect,
    gp,
    ave_p0,
    R_unit,
    kx0_e,
    etg_fact,
    c0,
    c1,
    exp1,
    cx_cy,
    alpha_x,
    B_unit=1.0,
    as_1=1.0,
    zs_1=-1.0,
    taus_1=1.0,
    mass_2=1.0,
    alpha_quench=0,
):
    '''
    SAT0 template for modifying the TGLF SAT0 intensity function from [Staebler et al., Nuclear Fusion, 2013], still needs to be normalized (see below)

    nk --> number of elements in ky spectrum
    nm --> number of modes
    ns --> number of species
    nf --> number of fields (1: electrostatic, 2: electromagnetic parallel, 3:electromagnetic perpendicular)

    :param ky_spect: poloidal wave number [nk]

    :param gp: growth rates [nk, nm]

    :param ave_p0: scalar average pressure

    :param R_unit: scalar normalized major radius

    :param kx0_e: spectral shift of the radial wavenumber due to VEXB_SHEAR [nk]

    :param etg_fact: scalar TGLF calibration coefficient [1.25]

    :param c0: scalar TGLF calibration coefficient [32.48]

    :param c1: scalar TGLF calibration coefficient [0.534]

    :param exp1: scalar TGLF calibration coefficient [1.547]

    :param cx_cy: scalar TGLF calibration coefficient [0.56] (from Eq.13)

    :param alpha_x: scalar TGLF calibration coefficient [1.15] (from Eq.13)

    :param B_unit: scalar normalized magnetic field (set to 1.0)

    :param as_1: scalar ratio of electron density to itself (must be 1.0)

    :param zs_1: scalar ratio of electron charge to the first ion charge (very likely to be -1.0)

    :param taus_1: scalar ratio of electron temperature to itself (must be 1.0)

    :param mass_2: scalar ratio of first ion mass to itself (must be 1.0)

    :param alpha_quench: scalar if alpha_quench==0 and any element in spectral shift array is greater than zero (versus equal zero), apply spectral shift routine

    :return: intensity function [nk, nm]
    '''

    if as_1 != 1.0 or taus_1 != 1.0 or mass_2 != 1.0:
        raise ValueError('as_1, taus_1, mass_2 must be equal to 1.0')
    kp = np.c_[ky_spect, ky_spect]  # add column makes two column array for dependence on two modes
    # kx0_e = np.c_[kx0_e, kx0_e]
    ks = kp * np.sqrt(taus_1 * mass_2)
    pols = (ave_p0 / np.abs(as_1 * zs_1 * zs_1)) ** 2
    R_unit[R_unit == 0] = np.amax(R_unit)  # when EV solver does not converge, R_unit is 0.0, but should be nonzero and the same for all  ky
    wd0 = ks * np.sqrt(taus_1 / mass_2) / R_unit
    gnet = gp / wd0
    cond = (alpha_quench == 0) * (np.abs(kx0_e) > 0)
    notcond = (alpha_quench != 0) + (np.abs(kx0_e) == 0)
    # Calculate intensity_given using scalar TGLF calibration coefficients
    cnorm = c0 * pols
    cnorm = cnorm / ((ks ** etg_fact) * (ks > 1) + 1 * (ks <= 1))
    intensity_out = cnorm * (wd0 ** 2) * (gnet ** exp1 + c1 * gnet) / (kp ** 4)
    intensity_out = intensity_out / (((1 + cx_cy * kx0_e ** 2) ** 2) * cond + 1 * notcond)
    intensity_out = intensity_out / (((1 + (alpha_x * kx0_e) ** 4) ** 2) * cond + 1 * notcond)
    intensity_out = intensity_out / B_unit ** 2
    intensity_out = np.nan_to_num(intensity_out)
    intensity_out[
        intensity_out == 0
    ] = 10e10  # when EV solver did not converge, intensity and potential are zero; change zeros to large number before division
    return intensity_out  # Careful: This still needs to be normalized; next operation is intensity_out = intensity_out * potential(TGLF SAT0 output) / intensity_out(default SAT0 params)
    # See example with default parameters below and regression test 'omfit/regression/test_tglf_satpy.py'


def intensity_sat1(
    ky_spect,
    gp,
    kx0_e,
    taus_2,
    expsub=2.0,
    alpha_zf_in=1.0,
    kx_geo0_out=1.0,
    SAT_geo_out=1.0,
    bz1=0.0,
    bz2=0.0,
    zs_1=-1.0,
    zs_2=1.0,
    taus_1=1.0,
    mass_1=0.000272313,
    mass_2=1.0,
):
    '''
    TGLF SAT1 from [Staebler et al., 2016, PoP], takes both GYRO and TGLF outputs as inputs

    :param ky_spect: poloidal wavenumber [nk]

    :param gp: growth rates [nk, nm]

    :param kx0_e: spectral shift of the radial wavenumber due to VEXB_SHEAR [nk]

    :param expsub: scalar exponent in gammaeff calculation [2.0]

    :param alpha_zf_in: scalar switch for the zonal flow coupling coefficient [1.0]

    :param kx_geo_out: scalar switch for geometry [1.0]

    :param SAT_geo_out: scalar switch for geoemtry [1.0]

    :param bz1: scalar correction to zonal flow mixing term [0.0]

    :param bz2: scalar correction to zonal flow mixing term [0.0]

    :param zs_1: scalar ratio of electron charge to the first ion charge (very likely to be -1.0)

    :param zs_2: scalar ratio fo the first ion charge with itself [1.0]

    :param taus_1: scalar ratio of electron temperature to itself [1.0]

    :param taus_2: scalar ratio of first ion temperature to electron temperature

    :param mass_1: scalar ratio of electron to first ion [0.000272313]

    :param mass_2: scalar ratio of first ion mass to itself [1.0]

    '''

    nmodes_in = len(gp[0, :])
    nky = len(ky_spect)
    gammas1 = gp[:, 0]  # SAT1 uses the growth rates of the most unstable modes

    etg_streamer = 1.05
    kyetg = etg_streamer * abs(zs_2) / np.sqrt(taus_2 * mass_2)

    czf = abs(alpha_zf_in)
    small = 1.0e-10
    cz1 = 0.48 * czf
    cz2 = 1.0 * czf
    ax = 1.15
    ay = 0.56

    gamma_net = gammas1 / (1.0 + (ax * kx_geo0_out * kx0_e) ** 4)

    cky = 3.0
    sqcky = np.sqrt(cky)
    cnorm = 14.29

    kycut = 0.8 * abs(zs_2) / np.sqrt(taus_2 * mass_2)  # ITG/ETG-scale separation (for TEM scales see [Creely et al., PPCF, 2019])
    kyhigh = 0.15 / np.sqrt(taus_1 * mass_1)

    gammamax1 = gamma_net[0]
    kymax1 = ky_spect[0]
    testmax1 = gammamax1 / kymax1
    testmax2 = 0
    jmax1 = 0
    jmax2 = 0

    j1 = 0
    j2 = 0

    for j in range(1, nky):
        ky0 = ky_spect[j]
        if ky0 < kycut:
            j1 = j1 + 1
        if ky0 < kyhigh:
            j2 = j2 + 1
        test = gamma_net[j] / ky0
        if ky0 < kycut:
            if test > testmax1:
                testmax1 = test
                jmax1 = j
        if ky0 > kycut:
            if test > testmax2:
                testmax2 = test
                jmax2 = j
    # handle exceptions
    if j1 == nky - 1:
        j1 = nky - 2
    if jmax2 == 0:
        jmax2 = j2

    gammamax2 = gamma_net[jmax2]
    kymax2 = ky_spect[jmax2]
    gammamax1 = gamma_net[jmax1]
    kymax1 = ky_spect[jmax1]

    # Routine for better determination of gamma/ky peak
    if jmax1 > 0 and jmax1 < j1:
        f0 = gamma_net[jmax1 - 1] / ky_spect[jmax1 - 1]
        f1 = gamma_net[jmax1] / ky_spect[jmax1]
        f2 = gamma_net[jmax1 + 1] / ky_spect[jmax1 + 1]
        dky = ky_spect[jmax1 + 1] - ky_spect[jmax1 - 1]
        x0 = (ky_spect[jmax1] - ky_spect[jmax1 - 1]) / dky
        a = f0
        x02 = x0 * x0
        b = (f1 - f0 * (1 - x02) - f2 * x02) / (x0 - x02)
        c = f2 - f0 - b
        xmax = -b / (2.0 * c)
        if xmax > 1.0:
            kymax1 = ky_spect[jmax1 + 1]
            gammamax1 = f2 * kymax1
        elif xmax < 0.0:
            kymax1 = ky_spect[jmax1 - 1]
            gammamax1 = f0 * kymax1
        else:
            kymax1 = ky_spect[jmax1 - 1] + dky * xmax
            gammamax1 = (a + b * xmax + c * xmax * xmax) * kymax1

    vzf1 = gammamax1 / kymax1
    vzf2 = gammamax2 / kymax2
    dvzf = max(vzf2 - vzf1, 0.0)
    dgamma = dvzf * kymax1
    vzf3 = max(vzf1 - bz1 * dvzf, 0.0)
    vzf4 = max(vzf1 - bz2 * dvzf, 0.0)

    # include zonal flow effects on growth rate model:
    gamma_mix1 = np.zeros(nky)
    gamma = np.zeros(nky)

    for j in range(0, nky):
        gamma0 = gamma_net[j]
        if ky_spect[j] < kymax1:
            gamma[j] = max(gamma0 - cz1 * (kymax1 - ky_spect[j]) * vzf1, 0.0)
        else:
            gamma[j] = cz2 * gammamax1 + max(gamma0 - cz2 * vzf1 * ky_spect[j], 0.0)
        gamma_mix1[j] = gamma[j]

    # Mix over ky>kymax with integration weight
    mixnorm1 = np.zeros(nky)
    for j in range(jmax1 + 2, nky):
        gamma_ave = 0.0
        mixnorm1 = ky_spect[j] * (
            np.arctan(sqcky * (ky_spect[nky - 1] / ky_spect[j] - 1.0)) - np.arctan(sqcky * (ky_spect[jmax1 + 1] / ky_spect[j] - 1.0))
        )
        for i in range(jmax1 + 1, nky - 1):
            ky_1 = ky_spect[i]
            ky_2 = ky_spect[i + 1]
            mix1 = ky_spect[j] * (np.arctan(sqcky * (ky_2 / ky_spect[j] - 1.0)) - np.arctan(sqcky * (ky_1 / ky_spect[j] - 1.0)))
            delta = (gamma[i + 1] - gamma[i]) / (ky_2 - ky_1)
            mix2 = ky_spect[j] * mix1 + (ky_spect[j] * ky_spect[j] / (2.0 * sqcky)) * (
                np.log(cky * (ky_2 - ky_spect[j]) ** 2 + ky_spect[j] ** 2) - np.log(cky * (ky_1 - ky_spect[j]) ** 2 + ky_spect[j] ** 2)
            )
            gamma_ave = gamma_ave + (gamma[i] - ky_1 * delta) * mix1 + delta * mix2
        gamma_mix1[j] = gamma_ave / mixnorm1

    # intensity
    nmodes_in = 2
    field_spectrum_out = np.zeros((21, 2))
    for j in range(0, nky):
        gamma0 = gp[j, 0]
        ky0 = ky_spect[j]
        kx = kx0_e[j]
        for i in range(0, nmodes_in):
            gammaeff = 0.0
            if gamma0 > small:
                gammaeff = gamma_mix1[j] * (gp[j, i] / gamma0) ** expsub
            if ky0 > kyetg:
                gammaeff = gammaeff * np.sqrt(ky0 / kyetg)
            field_spectrum_out[j, i] = SAT_geo_out * (cnorm * gammaeff * gammaeff / ky0 ** 4) / (1.0 + ay * (kx_geo0_out * kx) ** 2) ** 2
    phinorm = field_spectrum_out
    return phinorm  # is the intensity


def flux_integrals(
    NM,
    NS,
    NF,
    i,
    ky,
    dky0,
    dky1,
    particle,
    energy,
    toroidal_stress,
    parallel_stress,
    exchange,
    particle_flux_out,
    energy_flux_out,
    stress_tor_out,
    stress_par_out,
    exchange_out,
    q_low_out,
    taus_1=1.0,
    mass_2=1.0,
):
    '''
    Compute the flux integrals
    '''
    for nm in range(NM):
        for ns in range(NS):
            for j in range(NF):
                particle_flux_out[nm][ns][j] += dky0 * (0 if i == 0 else particle[i - 1][nm][ns][j]) + dky1 * particle[i][nm][ns][j]
                energy_flux_out[nm][ns][j] += dky0 * (0 if i == 0 else energy[i - 1][nm][ns][j]) + dky1 * energy[i][nm][ns][j]
                stress_tor_out[nm][ns][j] += (
                    dky0 * (0 if i == 0 else toroidal_stress[i - 1][nm][ns][j]) + dky1 * toroidal_stress[i][nm][ns][j]
                )
                stress_par_out[nm][ns][j] += (
                    dky0 * (0 if i == 0 else parallel_stress[i - 1][nm][ns][j]) + dky1 * parallel_stress[i][nm][ns][j]
                )
                exchange_out[nm][ns][j] += dky0 * (0 if i == 0 else exchange[i - 1][nm][ns][j]) + dky1 * exchange[i][nm][ns][j]
            if ky * taus_1 * mass_2 <= 1:
                q_low_out[nm][ns] = energy_flux_out[nm][ns][0] + energy_flux_out[nm][ns][1]
    return particle_flux_out, energy_flux_out, stress_tor_out, stress_par_out, exchange_out, q_low_out


def sum_ky_spectrum(
    sat_rule_in,
    ky_spect,
    gp,
    ave_p0,
    R_unit,
    kx0_e,
    potential,
    particle_QL,
    energy_QL,
    toroidal_stress_QL,
    parallel_stress_QL,
    exchange_QL,
    etg_fact=1.25,
    c0=32.48,
    c1=0.534,
    exp1=1.547,
    cx_cy=0.56,
    alpha_x=1.15,
    **kw,
):
    '''
    Perform the sum over ky spectrum
    The inputs to this function should be already weighted by the intensity function

    nk --> number of elements in ky spectrum
    nm --> number of modes
    ns --> number of species
    nf --> number of fields (1: electrostatic, 2: electromagnetic parallel, 3:electromagnetic perpendicular)

    :param sat_rule_in:

    :param ky_spect: k_y spectrum [nk]

    :param gp: growth rates [nk, nm]

    :param ave_p0: scalar average pressure

    :param R_unit: scalar normalized major radius

    :param kx0_e: spectral shift of the radial wavenumber due to VEXB_SHEAR [nk]

    :param potential: input potential fluctuation spectrum  [nk, nm]

    :param particle_QL: input particle fluctuation spectrum [nk, nm, ns, nf]

    :param energy_QL: input energy fluctuation spectrum [nk, nm, ns, nf]

    :param toroidal_stress_QL: input toroidal_stress fluctuation spectrum [nk, nm, ns, nf]

    :param parallel_stress_QL: input parallel_stress fluctuation spectrum [nk, nm, ns, nf]

    :param exchange_QL: input exchange fluctuation spectrum [nk, nm, ns, nf]

    :param etg_fact: scalar TGLF SAT0 calibration coefficient [1.25]

    :param c0: scalar TGLF SAT0 calibration coefficient [32.48]

    :param c1: scalar TGLF SAT0 calibration coefficient [0.534]

    :param exp1: scalar TGLF SAT0 calibration coefficient [1.547]

    :param cx_cy: scalar TGLF SAT0 calibration coefficient [0.56] (from TGLF 2008 POP Eq.13)

    :param alpha_x: scalar TGLF SAT0 calibration coefficient [1.15] (from TGLF 2008 POP Eq.13)

    :param \**kw: any additional argument should follow the naming convention of the TGLF_inputs
            for SAT1 the TAUS_2 argument is needed

    :return: dictionary with summations over ky spectrum:
            * particle_flux_integral: [nm, ns, nf]
            * energy_flux_integral: [nm, ns, nf]
            * toroidal_stresses_integral: [nm, ns, nf]
            * parallel_stresses_integral: [nm, ns, nf]
            * exchange_flux_integral: [nm, ns, nf]
    '''
    phi_bar_sum_out = 0
    NM = len(energy_QL[0, :, 0, 0])  # get the number of modes
    NS = len(energy_QL[0, 0, :, 0])  # get the number of species
    NF = len(energy_QL[0, 0, 0, :])  # get the number of fields
    particle_flux_out = np.zeros((NM, NS, NF))
    energy_flux_out = np.zeros((NM, NS, NF))
    stress_tor_out = np.zeros((NM, NS, NF))
    stress_par_out = np.zeros((NM, NS, NF))
    exchange_out = np.zeros((NM, NS, NF))
    q_low_out = np.zeros((NM, NS))

    # Multiply QL weights with desired intensity
    if sat_rule_in in [0.0, 0, 'SAT0']:
        intensity_factor = (
            intensity_sat0(ky_spect, gp, ave_p0, R_unit, kx0_e, etg_fact, c0, c1, exp1, cx_cy, alpha_x)
            * potential
            / intensity_sat0(ky_spect, gp, ave_p0, R_unit, kx0_e, 1.25, 32.48, 0.534, 1.547, 0.56, 1.15)
        )
    elif sat_rule_in in [1.0, 1, 'SAT1']:
        intensity_factor = intensity_sat1(ky_spect, gp, kx0_e, kw['TAUS_2'])
    elif sat_rule_in in [-1.0, -1, 'DESAT']:
        intensity_factor = (
            intensity_desat(ky_spect, kw['P_PRIME_LOC'], kw['Q_LOC'], kw['TAUS_2'])
            * potential
            / intensity_sat0(ky_spect, gp, ave_p0, R_unit, kx0_e, 1.25, 32.48, 0.534, 1.547, 0.56, 1.15)
        )
    else:
        raise ValueError("sat_rule_in must be [0.0, 0, 'SAT0'] or [1.0, 1, 'SAT1']")

    shapes = [item.shape for item in [particle_QL, energy_QL, toroidal_stress_QL, parallel_stress_QL, exchange_QL] if item is not None][0]

    particle = np.zeros(shapes)
    energy = np.zeros(shapes)
    toroidal_stress = np.zeros(shapes)
    parallel_stress = np.zeros(shapes)
    exchange = np.zeros(shapes)

    for i in range(NS):  # iterate over the species
        for j in range(NF):  # iterate over the fields
            if particle_QL is not None:
                particle[:, :, i, j] = particle_QL[:, :, i, j] * intensity_factor
            if energy_QL is not None:
                energy[:, :, i, j] = energy_QL[:, :, i, j] * intensity_factor
            if toroidal_stress_QL is not None:
                toroidal_stress[:, :, i, j] = toroidal_stress_QL[:, :, i, j] * intensity_factor
            if parallel_stress_QL is not None:
                parallel_stress[:, :, i, j] = parallel_stress_QL[:, :, i, j] * intensity_factor
            if exchange_QL is not None:
                exchange[:, :, i, j] = exchange_QL[:, :, i, j] * intensity_factor

    dky0 = 0
    ky0 = 0
    for i in range(len(ky_spect)):
        ky = ky_spect[i]
        ky1 = ky
        if i == 0:
            dky1 = ky1
        else:
            dky = np.log(ky1 / ky0) / (ky1 - ky0)
            dky1 = ky1 * (1.0 - ky0 * dky)
            dky0 = ky0 * (ky1 * dky - 1.0)

        particle_flux_out, energy_flux_out, stress_tor_out, stress_par_out, exchange_out, q_low_out = flux_integrals(
            NM,
            NS,
            NF,
            i,
            ky,
            dky0,
            dky1,
            particle,
            energy,
            toroidal_stress,
            parallel_stress,
            exchange,
            particle_flux_out,
            energy_flux_out,
            stress_tor_out,
            stress_par_out,
            exchange_out,
            q_low_out,
        )
        ky0 = ky1
        results = {
            "particle_flux_integral": particle_flux_out,
            "energy_flux_integral": energy_flux_out,
            "toroidal_stresses_integral": stress_tor_out,
            "parallel_stresses_integral": stress_par_out,
            "exchange_flux_integral": exchange_out,
        }
    return results

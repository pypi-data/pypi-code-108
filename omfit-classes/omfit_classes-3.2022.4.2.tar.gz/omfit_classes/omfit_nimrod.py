try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

import struct
import numpy as np

__all__ = ['OMFITnimrod']


class OMFITnimrod(SortedDict, OMFITobject):
    r"""
    OMFIT class used to interface with NIMROD output files
    Note: does not support writing

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, **kw):
        OMFITobject.__init__(self, filename, **kw)
        SortedDict.__init__(self, caseInsensitive=True)
        self.dynaLoad = True

    contour_labels = [
        'B0_r [T]',  # 1
        'B0_z [T]',  # 2
        'B0_{\\phi} [T]',  # 3
        'J0_r [A/m^2]',  # 4
        'J0_z [A/m^2]',  # 5
        'J0_{\\phi} [A/m^2]',  # 6
        'V0_r [m/s]',  # 7
        'V0_z [m/s]',  # 8
        'V0_{\\phi} [m/s]',  # 9
        'P_0 [Pa]',  # 10
        'P_{0e} [Pa]',  # 11
        'n0 [m^{-3}]',  # 12
        'diff shape',  # 13
        'B_r [T]',  # 14
        'B_z [T]',  # 15
        'B_{\\phi} [T]',  # 16
        'Im B_r [T]',  # 17
        'Im B_z [T]',  # 18
        'Im B_{\\phi} [T]',  # 19
        'J_r [A/m^2]',  # 20
        'J_z [A/m^2]',  # 21
        'J_{\\phi} [A/m^2]',  # 22
        'Im J_r [A/m^2]',  # 23
        'Im J_z [A/m^2]',  # 24
        'Im J_{\\phi} [A/m^2]',  # 25
        'V_r [m/s]',  # 26
        'V_z [m/s]',  # 27
        'V_{\\phi} [m/s]',  # 28
        'Im V_r [m/s]',  # 29
        'Im V_z [m/s]',  # 30
        'Im V_{\\phi} [m/s]',  # 31
        'P [Pa]',  # 32
        'Im P [Pa]',  # 33
        'P_e [Pa]',  # 34
        'Im P_e [Pa]',  # 35
        'n [m^{-3}]',  # 36
        'Im n [m^{-3}]',  # 37
        'conc',  # 38
        'Im conc',  # 39
        'T_e [eV]',  # 40
        'Im T_e [eV]',  # 41
        'T_i [eV]',  # 42
        'Im T_i [eV]',  # 43
        'P_{dilu} [W/m^3]',  # 44
        'Im P_{dilu} [W/m^3]',  # 45
        'P_{brem} [W/m^3]',  # 46
        'Im P_{brem} [W/m^3]',  # 47
        'P_{rec} [W/m^3]',  # 48
        'Im P_{rec} [W/m^3]',  # 49
        'P_{line} [W/m^3]',  # 50
        'Im P_{line} [W/m^3]',  # 51
        'P_{ion} [W/m^3]',  # 52
        'Im P_{ion} [W/m^3]',  # 53
        'n_imp [m^{-3}]',  # 54
        'Im n_imp [m^{-3}]',  # 55
        'n_{ele} [m^{-3}]',  # 56
        'Im n_{ele} [m^{-3}]',  # 57
        'n_{neut} [m^{-3}]',  # 58
        'Im n_{neut} [m^{-3}]',  # 59
        'n_{imp neut} [m^{-3}]',  # 60
    ]
    for iz in range(1, 19):
        contour_labels.append('n_{imp +' + str(iz) + '} [m^{-3}]')
    discharge_labels = [
        'istep',
        'time',
        'divB',
        'totE',  # total energy
        'totIE',  # total internal energy
        'totIEe',  # total internal electron energy
        'totIEi',  # total internal ion energy
        'lnE',  # ln(total energy)
        'lnIE',  # ln(internal energy)
        'grate',  # growth rate
        'Itot',  # current
        'Ipert',  # perturbed current
        'Vloop',  # perturbed loop voltage
        'totflux',  # total flux
        'n0flux',  # n=0 flux
        'bigF',  # F
        'Theta',  # Theta
        'magCFL',  # Eq. Mag-ac CFL
        'NLCFL',  # Nonlinear CFL
        'flowCFL',
    ]  # Flow CFL]

    polflux_labels = ['R', 'Z', 'polflux', 'R*Bphi']

    flsurf_labels = ['t', 'ix', 'polm', 'sqrt(polm)', 'polp', 'sqrt(polp)', 'q_surf', 'par_surf']

    SPIhist_labels = ['thstp', 'thtm', 'ip', 'Rp', 'Zp', 'Pp', 'radius', 'aden', 'taden', 'eden', 'eT', 'ablt', 'tablt', 'asim', 'tsim']

    energy_labels = ['step', 'time', 'imode', 'k', 'E_mag', 'E_kin', 'prad']

    kpraden_labels = [
        'istep',
        'time',
        'qlosd',
        'qloso',
        'qlosb',
        'qlosr',
        'qlosl',
        'qlosi',
        'Nz',
        'Ne',
        'Nz+zi',
        'qlost',
        'elosd',
        'eloso',
        'elosb',
        'elosr',
        'elosl',
        'elosi',
        'elost',
    ]

    kpradnz_labels = ['istep', 'time', 'Nz+2', 'Nz+3', 'Nz+4', 'Nz+5', 'Nz+6', 'Nz+7', 'Nz+8', 'Nz+9', 'Nz+10']

    xy_slice_labels = [
        'ix/mx',  # 0
        'iy/my',  # 1
        'R',  # 2
        'Z',  # 3
        'B0R',  # 4
        'B0Z',  # 5
        'B0Phi',  # 6
        'J0R',  # 7
        'J0Z',  # 8
        'J0Phi',  # 9
        'V0R',  # 10
        'V0Z',  # 11
        'V0Phi',  # 12
        'P0',  # 13
        'PE0',  # 14
        'n0',  # 15
        'diff shape',  # 16
        'BR',  # 17
        'BZ',  # 18
        'BP',  # 19
        'Im BR',  # 20
        'Im BZ',  # 21
        'Im BP',  # 22
        'JR',  # 23
        'JZ',  # 24
        'JP',  # 25
        'Im JR',  # 26
        'Im JZ',  # 27
        'Im JP',  # 28
        'VR',  # 29
        'VZ',  # 30
        'VP',  # 31
        'Im VR',  # 32
        'Im VZ',  # 33
        'Im VP',  # 34
        'P',  # 35
        'Im P',  # 36
        'PE',  # 37
        'Im PE',  # 38
        'n',  # 39
        'Im n',  # 40
        'conc',  # 41
        'Im conc',  # 42
        'Te',  # 43
        'Im Te',  # 44
        'Ti',  # 45
        'Im Ti',
    ]  # 46

    xt_slice_labels = [
        'ix/mx',  # 0
        'istep',  # 1
        't',  # 2
        'R',  # 3
        'Z',  # 4
        'B0R',  # 5
        'B0Z',  # 6
        'B0Phi',  # 7
        'J0R',  # 8
        'J0Z',  # 9
        'J0Phi',  # 10
        'V0R',  # 11
        'V0Z',  # 12
        'V0Phi',  # 13
        'P0',  # 14
        'PE0',  # 15
        'n0',  # 16
        'diff shape',  # 17
        'BR',  # 18
        'BZ',  # 19
        'BP',  # 20
        'Im BR',  # 21
        'Im BZ',  # 22
        'Im BP',  # 23
        'JR',  # 24
        'JZ',  # 25
        'JP',  # 26
        'Im JR',  # 27
        'Im JZ',  # 28
        'Im JP',  # 29
        'VR',  # 30
        'VZ',  # 31
        'VP',  # 32
        'Im VR',  # 33
        'Im VZ',  # 34
        'Im VP',  # 35
        'P',  # 36
        'Im P',  # 37
        'PE',  # 38
        'Im PE',  # 39
        'n',  # 40
        'Im n',  # 41
        'conc',  # 42
        'Im conc',  # 43
        'Te',  # 44
        'Im Te',  # 45
        'Ti',  # 46
        'Im Ti',
    ]  # 47

    xt_slice_kprad_labels = [
        'nimp',  # 48
        'Im nimp',  # 49
        'ne',  # 50
        'Im ne',  # 51
        'qlosd',  # 52
        'Im qlosd',  # 53
        'qloso',  # 54
        'Im qloso',  # 55
        'qlosb',  # 56
        'Im qlosb',  # 57
        'qlosr',  # 58
        'Im qlosr',  # 59
        'qlosl',  # 60
        'Im qlosl',  # 61
        'qlosi',  # 62
        'Im qlosi',  # 63
        'ndn',  # 64
        'Im ndn',
    ]  # 65

    nimhist_labels = [
        'istep',  # 0
        't',  # 1
        'imode',  # 2
        'k',  # 3
        'Br',  # 4
        'Bz',  # 5
        'Bphi',  # 6
        'Im Br',  # 7
        'Im Bz',  # 8
        'Im Bphi',  # 9
        'Jr',  # 10
        'Jz',  # 11
        'Jphi',  # 12
        'Im Jr',  # 13
        'Im Jz',  # 14
        'Im Jphi',  # 15
        'Vr',  # 16
        'Vz',  # 17
        'Vphi',  # 18
        'Im Vr',  # 19
        'Im Vz',  # 20
        'Im Vphi',  # 21
        'P',  # 22
        'Im P',  # 23
        'Pe',  # 24
        'Im Pe',  # 25
        'n',  # 26
        'Im n',  # 27
        'conc',  # 28
        'Im conc',  # 29
        'Te',  # 30
        'Im Te',  # 31
        'Ti',  # 32
        'Im Ti',
    ]  # 33

    def _read_raw(self):
        with open(self.filename, 'rb') as f:
            raw_data = f.read()
        nreals = len(raw_data) // 4
        return np.array(struct.unpack(">" + str(nreals) + 'f', raw_data))

    def _read_table(self, l=4):
        with open(self.filename, 'rb') as f:
            d1 = []
            d2 = []
            data = 0
            while data is not None:
                data = self._read_record(f, l)
                if data is not None:
                    if len(data):
                        d2.append(data)
                    else:
                        d1.append(np.array(d2))
                        d2 = []
        if not len(d1):
            return np.array(d2)
        return np.array(d1)

    # Seperate read_table for discharge to fix bug with reading restarts
    def _read_table_dis(self, l=4):
        with open(self.filename, 'rb') as f:
            d1 = []
            data = 0
            while data is not None:
                data = self._read_record(f, l)
                if data is not None and len(data):
                    d1.append(data)

        return np.array(d1)

    def _read_record(self, f, l=4):
        d = f.read(4)
        if not len(d):
            return None
        n = struct.unpack(">1i", d)[0]
        data = np.array(struct.unpack(">" + str(n // l) + 'f', f.read(n)))
        n2 = struct.unpack(">1i", f.read(4))[0]
        if n != n2:
            raise IOError('Error reading record')
        return data

    def _merge_blocks(self, qnt):
        blx = int(self['blx'])
        bly = int(self['bly'])
        nxbl = int(self['nxbl'])
        nybl = int(self['nybl'])

        if len(qnt.shape) == 3:
            tmp = np.zeros(((blx - 1) * nxbl + 1, (bly - 1) * nybl + 1), dtype=qnt.dtype)
        elif len(qnt.shape) == 4:
            tmp = np.zeros(((blx - 1) * nxbl + 1, (bly - 1) * nybl + 1, qnt.shape[2]), dtype=qnt.dtype)

        for ibl in range(nxbl):
            for jbl in range(nybl):
                if len(qnt.shape) == 3:
                    tmp[ibl * (blx - 1) : ibl * (blx - 1) + blx, jbl * (bly - 1) : jbl * (bly - 1) + bly] = qnt[:, :, nybl * ibl + jbl]
                elif len(qnt.shape) == 4:
                    tmp[ibl * (blx - 1) : ibl * (blx - 1) + blx, jbl * (bly - 1) : jbl * (bly - 1) + bly, :] = qnt[
                        :, :, :, nybl * ibl + jbl
                    ]

        return tmp

    def _read_contour(self):
        """
        Parse contour.bin files
        """
        with open(self.filename, 'rb') as f:
            raw_data = f.read()
        bldat = struct.unpack(">" + str(10) + 'i', raw_data[: 4 * 10])
        nbl = self['nbl'] = int(bldat[1])
        nvar = self['nvar'] = int(bldat[3])
        blx = self['blx'] = int(bldat[6] + 1)
        bly = self['bly'] = int(bldat[7] + 1)
        blp = self['blp'] = self['blx'] * self['bly']

        cdata = self._read_raw()

        nslice = self['nslice'] = int((len(cdata) - (11 + nbl * blp * 2 + 6 * (nbl - 1))) / (nbl * (blp + 2) * nvar))
        print('Parsing data: ' + str(nslice) + ' slices')

        r = np.zeros((blx, bly, nbl))
        z = np.zeros((blx, bly, nbl))
        for ibl in range(nbl):
            c = 10 + ibl * (2 * blp + 6) + 2 * blp
            b = 10 + ibl * (2 * blp + 6) + blp
            a = 10 + ibl * (2 * blp + 6)
            r[:, :, ibl] = np.reshape(cdata[a:b], (bly, blx)).T
            z[:, :, ibl] = np.reshape(cdata[b:c], (bly, blx)).T

        nybl = 1
        for ir in range(1, nbl):
            if r[0, 0, 0] != r[0, 0, ir]:
                nybl = ir
                break
        nxbl = nbl // nybl
        self['nxbl'] = nxbl
        self['nybl'] = nybl

        self['z'] = self._merge_blocks(z)
        self['r'] = self._merge_blocks(r)

        cdat2 = cdata[10 + 2 * blp * nbl + 6 * (nbl - 1) :]

        varr = np.zeros((blx, bly, nslice, nbl, nvar))
        for sl in range(nslice):
            for iv in range(nvar):
                for ibl in range(nbl):
                    a = 2 + iv * (blp + 2) + ibl * (blp + 2) * nvar
                    b = 2 + iv * (blp + 2) + ibl * (blp + 2) * nvar + blp
                    varr[:, :, sl, ibl, iv] = np.reshape(cdat2[a:b], (bly, blx)).T
            if sl < nslice:
                cdat2 = cdat2[nbl * nvar * (blp + 2) :]

        printi('Restructuring blocks')
        for k, label in enumerate(self.contour_labels):
            if label[:3] == 'Im ':
                continue
            if k < varr.shape[-1]:
                if 'Im ' + label in self.contour_labels:
                    kI = self.contour_labels.index('Im ' + label)
                    self[label] = self._merge_blocks(varr[:, :, :, :, k] + 1j * varr[:, :, :, :, kI])
                elif ('{imp' in label) and (k + (nvar - 59) // 2 < nvar):
                    kI = k + (nvar - 59) // 2
                    self[label] = self._merge_blocks(varr[:, :, :, :, k] + 1j * varr[:, :, :, :, kI])
                elif k < 59:
                    self[label] = self._merge_blocks(varr[:, :, :, :, k])

    def _plot_contour(self, slice=0, phase=0, nlevels=21):
        """
        Default plot for contour.bin files

        :param slice: slice to plot

        :param phase: plot real part of complex quantities multiplied by exp(1j*phase)

        :param nlevels: number of levels in the contours
        """
        plts = np.array([31, 35, 41, 13, 14, 15, 19, 20, 21, 25, 26, 27])
        ioff()
        try:
            for k, label in enumerate(np.array(self.contour_labels)[plts]):
                if k == 0:
                    ax = pyplot.subplot(3, 4, k + 1)
                else:
                    pyplot.subplot(3, 4, k + 1, sharex=ax, sharey=ax)
                if 'complex' in self[label].dtype.name and phase != 0:
                    contour(self['r'], self['z'], np.real(self[label][:, :, slice] * np.exp(1j * phase)), nlevels)
                else:
                    contour(self['r'], self['z'], self[label][:, :, slice], nlevels)
                pyplot.title('$' + re.sub(r'\(', '\\,(', label) + '$')
                pyplot.gca().set_aspect('equal')
                pyplot.plot(self['r'][-1, :], self['z'][-1, :], 'k')
            autofmt_sharexy()
            pyplot.subplots_adjust(wspace=0.0, hspace=0.2)
            pyplot.suptitle('Slice ' + str(slice))
        finally:
            ion()
            show()

    def _read_polflux(self):
        """
        Parse polflux.bin files
        """
        with open(self.filename, 'rb') as f:
            raw_data = f.read()
        bldat = struct.unpack(">" + str(8) + 'i', raw_data[: 4 * 8])

        mx = self['mx'] = bldat[6] + 1
        my = self['my'] = bldat[7] + 1

        cdata = self._read_table()

        R = self['R'] = np.reshape(cdata[2][: mx * my], (my, mx))
        Z = self['Z'] = np.reshape(cdata[2][mx * my :], (my, mx))
        self['polflux'] = np.ndarray([my, mx, (len(cdata) - 3) // 2])
        self['R*Bphi'] = np.ndarray([my, mx, (len(cdata) - 3) // 2])
        nd = 3
        while nd + 1 < len(cdata):
            polflux = self['polflux'][:, :, (nd - 3) // 2] = np.reshape(cdata[nd][:], (my, mx))
            nd = nd + 1
            RBphi = self['R*Bphi'][:, :, (nd - 4) // 2] = np.reshape(cdata[nd][:], (my, mx))
            nd = nd + 1

    def _plot_polflux(self):
        """
        Default plot for polflux.bin files

        """
        ioff()
        try:
            ax = pyplot.subplot(1, 2, 1)
            contourf(self['R'], self['Z'], self['polflux'])
            pyplot.title('polflux')
            pyplot.subplot(1, 2, 2, sharey=ax)
            contourf(self['R'], self['Z'], self['R*Bphi'])
            pyplot.title('R*Bphi')
            autofmt_sharexy()
            pyplot.subplots_adjust(wspace=0.0, hspace=0.2)
        finally:
            ion()
            show()

    def _read_flsurf(self):
        """
        Parse flsurf.bin files
        """

        cdata = self._read_table()

        for k, label in enumerate(self.flsurf_labels):
            self[label] = cdata[0, :, k]

    def _plot_flsurf(self):
        """
        Default plot for flsurf.bin files

        """
        ioff()
        try:
            pyplot.plot(self['polp'], self['q_surf'], label='q_surf')
            pyplot.plot(self['polp'], self['par_surf'], label='par_surf')
            pyplot.title('q and j|| vs poloidal flux')
            legend()
        finally:
            ion()
            show()

    def _read_discharge(self):
        """
        Parse discharge.bin files
        """
        alld = self._read_table_dis()

        discharge_labels = self.discharge_labels[: alld.shape[-1]]
        for kit, it in enumerate(discharge_labels):
            if it not in ['dummy', 'lnE', 'lnIE']:
                try:
                    self[it] = np.squeeze(alld)[:, kit]
                except IndexError as _excp:
                    raise
                    printe(repr(_excp))

    def _plot_discharge(self):
        """
        Default plot for discharge.bin files
        """
        kit = 0
        for it in self:
            if it not in ['istep', 'time']:
                kit += 1
                if kit == 1:
                    ax = pyplot.subplot(4, 4, kit)
                else:
                    pyplot.subplot(4, 4, kit, sharex=ax)
                pyplot.plot(self['time'] * 1e3, self[it])
                title_inside(it, 0.5, 0.7)
                pyplot.xlabel('time [ms]')
        autofmt_sharex()
        pyplot.suptitle('Discharge summary')

    def _read_kpraden(self):
        """
        Parse kpraden.bin files
        """
        alld = self._read_table()
        kpraden_labels = self.kpraden_labels[: alld.shape[-1]]
        for kit, it in enumerate(kpraden_labels):
            if it not in ['istep']:
                self[it] = np.squeeze(alld)[:, kit]

    def _plot_kpraden(self):
        """
        Default plot for kpraden.bin files
        """
        kit = 0
        for it in self:
            if it not in ['istep', 'time']:
                kit += 1
                if kit == 1:
                    ax = pyplot.subplot(6, 3, kit)
                else:
                    pyplot.subplot(6, 3, kit, sharex=ax)
                pyplot.plot(self['time'] * 1e3, self[it])
                title_inside(it, 0.5, 0.7)
                pyplot.xlabel('time [ms]')
        autofmt_sharex()
        pyplot.suptitle('kprad radiation')

    def _read_kpradnz(self):
        """
        Parse kpradnz.bin files
        """
        alld = self._read_table()
        kpradnz_labels = self.kpradnz_labels[: alld.shape[-1]]
        for kit, it in enumerate(kpradnz_labels):
            if it not in ['istep']:
                self[it] = np.squeeze(alld)[:, kit]

    def _plot_kpradnz(self):
        """
        Default plot for kpradnz.bin files
        """
        kit = 0
        for it in self:
            if it not in ['istep', 'time']:
                kit += 1
                if kit == 1:
                    ax = pyplot.subplot(3, 3, kit)
                else:
                    pyplot.subplot(3, 3, kit, sharex=ax)
                pyplot.plot(self['time'] * 1e3, self[it])
                title_inside(it, 0.5, 0.7)
                pyplot.xlabel('time [ms]')
        autofmt_sharex()
        pyplot.suptitle('kprad impurities')

    def _read_energy(self):
        """
        Parse energy.bin files
        """
        alld = self._read_table()
        energy_labels = self.energy_labels[: alld.shape[-1]]
        for kit, it in enumerate(energy_labels):
            if it in ['k', 'imode']:
                continue

            elif it in ['time', 'step', 'prad']:
                self[it] = alld[:, 0, kit]

            else:
                self['modes_k'] = []
                for k in range(alld.shape[1]):
                    kmode = alld[0, k, energy_labels.index('k')]
                    imode = int(alld[0, k, energy_labels.index('imode')])
                    self.setdefault(imode - 1, SortedDict())
                    self[imode - 1][it] = alld[:, imode - 1, kit]
                    self[imode - 1]['keff'] = kmode
                    self['modes_k'].append(kmode)
                # self['modes_k']=np.array(self['modes_k']).astype(int)

    def _plot_energy(self):
        """
        Default plot for energy.bin files
        """
        colors = cm.rainbow(np.linspace(0, 1, len(self['modes_k'])))

        ax1 = pyplot.subplot(2, 1, 1)
        pyplot.ylabel('$E_{\\rm mag}$')
        ax2 = pyplot.subplot(2, 1, 2, sharex=ax1)
        pyplot.ylabel('$E_{\\rm kin}$')

        autofmt_sharex()

        for k in range(len(self['modes_k'])):
            ax1.semilogy(self['time'] * 1e3, self[k]['E_mag'], label=str(self['modes_k'][k]), color=colors[k])

        for k in range(len(self['modes_k'])):
            ax2.semilogy(self['time'] * 1e3, self[k]['E_kin'], label=str(self['modes_k'][k]), color=colors[k])
        ax2.legend(loc=0).draggable(True)

        pyplot.xlim([0, max(self['time'] * 1e3)])
        pyplot.xlabel('time [ms]')

    def _plot_prad(self):
        """
        Prad plot for energy.bin files
        """
        pyplot.semilogy(self['time'] * 1e3, self['prad'], 'k')
        pyplot.ylabel('$P_{\\rm rad}$')
        pyplot.xlim([0, max(self['time'] * 1e3)])
        pyplot.xlabel('time [ms]')

    def _read_grid(self):
        """
        Parse grid.bin files
        """
        alld = self._read_table()
        self['r'] = []
        self['z'] = []
        for k in range(len(alld)):
            self['r'].append(alld[k][:, 0])
            self['z'].append(alld[k][:, 1])

    def _plot_grid(self):
        """
        Default plot for grid.bin files
        """
        pyplot.gca().set_aspect('equal')
        colors = color_cycle(len(self['r']))
        for k in range(len(colors)):
            pyplot.plot(self['r'][k], self['z'][k], color=colors[k])
        pyplot.xlabel('R [m]')
        pyplot.ylabel('Z [m]')

    def _read_xy_slice(self):
        """
        Parse xy_slice.bin files
        """
        alld = self._read_table()
        nmodes = int((np.size(alld, 2) - 17) // 30)

        for j in range(0, 17):
            self[self.xy_slice_labels[j]] = alld[:, :, j]

        slice = (17, 23, 29, 35, 37, 39, 41, 43, 45, 47)
        for k in range(len(slice) - 1):
            # print(slice[k],slice[k+1],slice[k]-slice[0],slice[k+1]-slice[k])
            for j in range(slice[k], slice[k + 1]):
                label = self.xy_slice_labels[j]
                if label[:3] == 'Im ':
                    continue
                for n in range(nmodes):
                    self.setdefault(n, SortedDict())
                    if 'Im ' + label in self.xy_slice_labels:
                        jI = self.xy_slice_labels.index('Im ' + label)
                        self[n][label] = (
                            alld[:, :, j + (slice[k] - slice[0]) * (nmodes - 1) + n * (slice[k + 1] - slice[k])]
                            + 1j * alld[:, :, jI + (slice[k] - slice[0]) * (nmodes - 1) + n * (slice[k + 1] - slice[k])]
                        )
                    else:
                        self[n][label] = alld[:, :, j + (slice[k] - slice[0]) * (nmodes - 1) + n * (slice[k + 1] - slice[k])]

    def _plot_xy_slice(self, nlevels=21):
        """
        Default plot for xy_slice.bin files
        """
        for k, label in enumerate(self.xy_slice_labels[4:16]):
            pyplot.subplot(3, 4, k + 1)
            pyplot.gca().set_aspect('equal')
            try:
                contour(self['ix/mx'][:, :].T, self['iy/my'][:, :].T, self[label][:, :].T, nlevels)
            except Exception:
                pass
            if k in [8, 9, 10, 11]:
                pyplot.xlabel('ix/mx')
            if k in [0, 4, 8]:
                pyplot.ylabel('iy/my')
            pyplot.title(label)

        autofmt_sharexy()
        pyplot.subplots_adjust(wspace=0.0, hspace=0.2)

    def _read_xt_slice(self):
        """
        Parse xt_slice.bin files
        """
        alld = self._read_table()
        nslice = np.size(alld, 0)

        for n in range(0, nslice):
            self.setdefault(n, SortedDict())
            for j in range(0, 48):
                label = self.xt_slice_labels[j]
                if label[:3] == 'Im ':
                    continue
                if 'Im ' + label in self.xt_slice_labels:
                    jI = self.xt_slice_labels.index('Im ' + label)
                    self[n][label] = alld[n, :, j] + 1j * alld[n, :, jI]
                else:
                    self[n][label] = alld[n, :, j]

            if np.size(alld, 2) >= 59:
                for j in range(48, 66):
                    label = self.xt_slice_kprad_labels[j - 48]
                    if label[:3] == 'Im ':
                        continue
                    if 'Im ' + label in self.xt_slice_kprad_labels:
                        jI = self.xt_slice_kprad_labels.index('Im ' + label)
                        self[n][label] = alld[n, :, j] + 1j * alld[n, :, jI]
                    else:
                        self[n][label] = alld[n, :, j]
            if np.size(alld, 2) >= 61:
                zimp = int((np.size(alld, 2) - 66) / 2)
                for j in range(66, 66 + zimp):
                    label = 'nz+' + str(j - 66)
                    self[n][label] = alld[n, :, j] + 1j * alld[n, :, j + zimp]

    def _plot_xt_slice(self, nlevels=21):
        """
        Default plot for xt_slice.bin files
        """
        colors = color_cycle(len(self))
        for k, label in enumerate(self.xt_slice_labels[i] for i in [18, 20, 24, 26, 30, 32, 36, 40, 44]):
            tlabel = label
            pyplot.subplot(3, 3, k + 1)

            for n in self:
                try:
                    pyplot.plot(self[n]['ix/mx'][:], self[n][label][:], color=colors[n])
                    if k in [0, 2, 4]:
                        pyplot.plot(self[n]['ix/mx'][:], self[n][label[0] + 'Z'][:], linestyle='--', color=colors[n])
                        tlabel = label + ',' + label[0] + 'Z'
                    if k in [6]:
                        pyplot.plot(self[n]['ix/mx'][:], self[n][label[0] + 'E'][:], linestyle='--', color=colors[n])
                        tlabel = label + ',' + label[0] + 'E'
                    if k in [8]:
                        pyplot.plot(self[n]['ix/mx'][:], self[n][label[0] + 'e'][:], linestyle='--', color=colors[n])
                        tlabel = label + ',' + label[0] + 'i'
                except Exception:
                    pass
            pyplot.xlabel('ix/mx')
            pyplot.title(tlabel)
            if k == 1:
                pyplot.gca().legend(self)

        autofmt_sharex()
        pyplot.subplots_adjust(wspace=0.3, hspace=0.2)

    def _read_nimhist(self):
        """
        Parse nimhist.bin files
        """
        alld = self._read_table()
        nmodes = np.size(alld, 1)

        for n in range(0, nmodes):
            self.setdefault(n, SortedDict())
            for j in range(0, 34):
                label = self.nimhist_labels[j]
                if label[:3] == 'Im ':
                    continue
                if 'Im ' + label in self.nimhist_labels:
                    jdrhoI = self.nimhist_labels.index('Im ' + label)
                    self[n][label] = alld[:, n, j] + 1j * alld[:, n, jdrhoI]
                else:
                    self[n][label] = alld[:, n, j]

    def _read_SPIhist(self):
        """
        Parse SPIhist.bin files
        """
        alld = self._read_table()
        SPIhist_labels = self.SPIhist_labels[: alld.shape[-1]]
        for kit, it in enumerate(SPIhist_labels):
            self[it] = alld[:, :, kit]

    def _plot_nimhist(self, nlevels=21):
        """
        Default plot for nimhist.bin files
        """
        colors = cm.rainbow(np.linspace(0, 1, len(self)))
        for k, label in enumerate(self.nimhist_labels[i] for i in [4, 6, 10, 12, 16, 18, 22, 26, 30]):
            tlabel = label
            pyplot.subplot(3, 3, k + 1)

            for n in self:
                try:
                    pyplot.plot(self[n]['t'][:], self[n][label][:], color=colors[n])
                    if k in [0, 2, 4]:
                        pyplot.plot(self[n]['t'][:], self[n][label[0] + 'Z'][:], linestyle='--', color=colors[n])
                        tlabel = label + ',' + label[0] + 'Z'
                    if k in [6]:
                        pyplot.plot(self[n]['t'][:], self[n][label[0] + 'E'][:], linestyle='--', color=colors[n])
                        tlabel = label + ',' + label[0] + 'E'
                    if k in [8]:
                        pyplot.plot(self[n]['t'][:], self[n][label[0] + 'i'][:], linestyle='--', color=colors[n])
                        tlabel = label + ',' + label[0] + 'i'
                except Exception:
                    pass
            pyplot.xlabel('t')
            pyplot.title(tlabel)
            if k == 1:
                pyplot.gca().legend(self).draggable()

        autofmt_sharex()
        pyplot.subplots_adjust(wspace=0.3, hspace=0.2)

    def _read_nimfl(self):
        """
        Parse nimfl.bin files
        """
        alld = self._read_table()
        for k in range(0, len(alld) - 1):
            self[k] = SortedDict()
            self[k]['r'] = alld[k][:, 0]
            self[k]['z'] = alld[k][:, 1]

    def _plot_nimfl(self):
        """
        Default plot for nimfl.bin files
        """
        colors = color_cycle(len(self), cmap_name='hsv')
        limits = {'rmin': 0, 'rmax': 0, 'zmin': 0, 'zmax': 0}
        for k in list(self.keys()):
            pyplot.plot(self[k]['r'], self[k]['z'], '.', color=colors[k])
            limits['zmin'] = min(limits['zmin'], min(self[k]['z']))
            limits['zmax'] = max(limits['zmax'], max(self[k]['z']))
        pyplot.gca().set_aspect('equal')
        pyplot.ylim([limits['zmin'], limits['zmax']])

    @dynaLoad
    def load(self):
        if 'energy' in os.path.split(self.filename)[1]:
            self._read_energy()
        elif 'discharge' in os.path.split(self.filename)[1]:
            self._read_discharge()
        elif 'kpraden' in os.path.split(self.filename)[1]:
            self._read_kpraden()
        elif 'kpradnz' in os.path.split(self.filename)[1]:
            self._read_kpradnz()
        elif 'flsurf' in os.path.split(self.filename)[1]:
            self._read_flsurf()
        elif 'polflux' in os.path.split(self.filename)[1]:
            self._read_polflux()
        elif 'contour' in os.path.split(self.filename)[1]:
            self._read_contour()
        elif 'conrz' in os.path.split(self.filename)[1]:
            self._read_contour()
        elif 'grid' in os.path.split(self.filename)[1]:
            self._read_grid()
        elif 'xy_slice' in os.path.split(self.filename)[1]:
            self._read_xy_slice()
        elif 'xyrz' in os.path.split(self.filename)[1]:
            self._read_xy_slice()
        elif 'xyrz' in os.path.split(self.filename)[1]:
            self._read_xy_slice()
        elif 'xt_slice' in os.path.split(self.filename)[1]:
            self._read_xt_slice()
        elif 'nimfl' in os.path.split(self.filename)[1]:
            self._read_nimfl()
        elif 'nimhist' in os.path.split(self.filename)[1]:
            self._read_nimhist()
        elif 'SPIhist' in os.path.split(self.filename)[1]:
            self._read_SPIhist()
        else:
            self['data'] = self._read_table()

    def plot(self, slice=0, phase=0, nlevels=21):
        """
        Default plot of energy.bin, discharge.bin, contour.bin and grid.bin files

        :param slice: (contour.bin) slice to plot

        :param phase: (contour.bin) plot real part of complex quantities multiplied by np.exp(1j*phase)

        :param nlevels: (contour.bin) number of levels in the contours
        """
        if 'energy' in os.path.split(self.filename)[1]:
            self._plot_energy()
        elif 'discharge' in os.path.split(self.filename)[1]:
            self._plot_discharge()
        elif 'kpraden' in os.path.split(self.filename)[1]:
            self._plot_kpraden()
        elif 'kpradnz' in os.path.split(self.filename)[1]:
            self._plot_kpradnz()
        elif 'flsurf' in os.path.split(self.filename)[1]:
            self._plot_flsurf()
        elif 'polflux' in os.path.split(self.filename)[1]:
            self._plot_polflux()
        elif 'contour' in os.path.split(self.filename)[1]:
            self._plot_contour(slice=slice, phase=phase, nlevels=nlevels)
        elif 'conrz' in os.path.split(self.filename)[1]:
            self._plot_contour(slice=slice, phase=phase, nlevels=nlevels)
        elif 'grid' in os.path.split(self.filename)[1]:
            self._plot_grid()
        elif 'xy_slice' in os.path.split(self.filename)[1]:
            self._plot_xy_slice(nlevels=nlevels)
        elif 'xyrz' in os.path.split(self.filename)[1]:
            self._plot_xy_slice(nlevels=nlevels)
        elif 'xt_slice' in os.path.split(self.filename)[1]:
            self._plot_xt_slice(nlevels=nlevels)
        elif 'nimfl' in os.path.split(self.filename)[1]:
            self._plot_nimfl()
        elif 'nimhist' in os.path.split(self.filename)[1]:
            self._plot_nimhist()


############################################
if '__main__' == __name__:
    os.chdir(OMFITtmpDir)

    foo = OMFITnimrod(os.path.dirname(__file__) + '/../../samples/nimrod_discharge.bin')
    foo.load()
    print(foo)

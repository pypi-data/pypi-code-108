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

from omfit_classes.omfit_ascii import *

__all__ = ['OMFITrabbitEq', 'OMFITrabbitBeamout', 'OMFITrabbitTimetraces', 'OMFITrabbitBeamin']


class OMFITrabbitEq(SortedDict, OMFITascii):
    """Equilibirium files for RABBIT"""

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)

        if os.stat(self.filename).st_size:
            self.dynaLoad = True
        else:
            self['NW'] = 0
            self['NH'] = 0
            self['PSIRZ'] = np.zeros((1, 1))
            self['NPSI1D'] = 0
            self['QPSI'] = np.zeros((1, 1))
            self['FPOL'] = np.zeros((1, 1))
            self['SIBRY'] = 0
            self['SIMAG'] = 0
            self['SIGNIP'] = 0
            self['RMAXIS'] = 0
            self['ZMAXIS'] = 0
            self['AuxQuantities'] = SortedDict(
                {
                    'R': np.zeros((1, 1)),
                    'Z': np.zeros((1, 1)),
                    'PSIRZ': np.zeros((1, 1)),
                    'RHORZ': np.zeros((1, 1)),
                    'PSI': np.zeros((1, 1)),
                    'VOL': np.zeros((1, 1)),
                    'AREA': np.zeros((1, 1)),
                    'RHO': np.zeros((1, 1)),
                }
            )

    @dynaLoad
    def load(self):
        content = []
        with open(self.filename, 'r') as f:
            line = f.read()
            content += line.split()
        content = [float(i) for i in content]

        self['NW'] = NW = int(content[0])
        self['NH'] = NH = int(content[1])

        AuxQuantities = SortedDict()
        AuxQuantities['R'] = np.array(content[2 : NW + 2])
        AuxQuantities['Z'] = np.array(content[NW + 2 : NW + 2 + NH])

        istr = NW + 2 + NH
        self['PSIRZ'] = np.zeros((NW, NH))
        for i in range(NH):
            self['PSIRZ'][i, :] = content[istr + (i * NW) : istr + ((i + 1) * NW)]
        AuxQuantities['PSIRZ'] = self['PSIRZ']

        istr = istr + ((i + 1) * NW)
        AuxQuantities['RHORZ'] = np.zeros((NW, NH))
        for i in range(NH):
            AuxQuantities['RHORZ'][i, :] = content[istr + (i * NW) : istr + ((i + 1) * NW)]

        self['NPSI1D'] = NPsi1d = int(content[istr + ((i + 1) * NW)])

        istr = istr + ((i + 1) * NW) + 1
        AuxQuantities['PSI'] = np.array(content[istr + 0 * NPsi1d : istr + 1 * NPsi1d])
        AuxQuantities['VOL'] = np.array(content[istr + 1 * NPsi1d : istr + 2 * NPsi1d])
        AuxQuantities['AREA'] = np.array(content[istr + 2 * NPsi1d : istr + 3 * NPsi1d])
        AuxQuantities['RHO'] = np.array(content[istr + 3 * NPsi1d : istr + 4 * NPsi1d])
        self['QPSI'] = np.array(content[istr + 4 * NPsi1d : istr + 5 * NPsi1d])
        self['FPOL'] = np.array(content[istr + 5 * NPsi1d : istr + 6 * NPsi1d])

        istr = istr + 6 * NPsi1d
        self['SIBRY'] = content[istr]
        self['SIMAG'] = content[istr + 1]
        self['SIGNIP'] = content[istr + 2]
        self['RMAXIS'] = content[istr + 3]
        self['ZMAXIS'] = content[istr + 4]

        self['AuxQuantities'] = AuxQuantities

    @dynaLoad
    def plot(self):
        # plot contours
        contour(self['AuxQuantities']['R'], self['AuxQuantities']['Z'], self['AuxQuantities']['PSIRZ'], 50)

        # plot separatrix
        contour(
            self['AuxQuantities']['R'],
            self['AuxQuantities']['Z'],
            self['AuxQuantities']['PSIRZ'],
            levels=[self['SIBRY']],
            linewidths=2,
            cmap=mpl.cm.gray,
        )

        # plot maxis
        scatter(self['RMAXIS'], self['ZMAXIS'], 50, marker='+')

        pyplot.gca().set_aspect('equal')
        pyplot.xlabel('R')
        pyplot.ylabel('Z')

        cornernote(time='')

    @dynaSave
    def save(self):
        def print6(f, d):  # print to file in rows of 6
            i0 = 0
            for i in range(int(len(d) // 6)):
                f.write(('{:13.6f}' * 6 + '\n').format(*d[i0 : i0 + 6]))
                i0 += 6
            for i in range(i0, len(d)):
                f.write('{:13.6f}'.format(d[i]))
            f.write('\n')

        with open(self.filename, 'w') as f:
            f.write('          {}\n'.format(self['NW']))
            f.write('          {}\n'.format(self['NH']))

            print6(f, self['AuxQuantities']['R'])
            print6(f, self['AuxQuantities']['Z'])

            for d in self['AuxQuantities']['PSIRZ']:
                print6(f, d)
            for d in self['AuxQuantities']['RHORZ']:
                print6(f, d)

            f.write('          {}\n'.format(self['NPSI1D']))

            print6(f, self['AuxQuantities']['PSI'])
            print6(f, self['AuxQuantities']['VOL'])
            print6(f, self['AuxQuantities']['AREA'])
            print6(f, self['AuxQuantities']['RHO'])
            print6(f, self['QPSI'])
            print6(f, self['FPOL'])

            f.write(
                '{:12.6f}{:12.6f}{:12.6f}{:12.6f}{:12.6f}\n'.format(
                    self['SIBRY'], self['SIMAG'], self['SIGNIP'], self['RMAXIS'], self['ZMAXIS']
                )
            )

    def from_geqdsk(self, gEQDSK):

        gEQDSK = gEQDSK.cocosify(5, True, True)  ###### CONVERT gEQDSK file to COCOS 5
        signIp = -1 + 2 * (gEQDSK['CURRENT'] > 0)

        self['NH'] = len(gEQDSK['AuxQuantities']['Z'])
        self['NW'] = len(gEQDSK['AuxQuantities']['R'])
        self['NPSI1D'] = len(gEQDSK['AuxQuantities']['PSI'])
        self['SIGNIP'] = signIp
        self['SIBRY'] = gEQDSK['SIBRY']
        self['SIMAG'] = gEQDSK['SIMAG']
        self['RMAXIS'] = gEQDSK['rmaxis']
        self['ZMAXIS'] = gEQDSK['zmaxis']

        self['FPOL'] = gEQDSK['FPOL']
        self['QPSI'] = abs(gEQDSK['QPSI'])  ###### RABBIT assumes positive q?
        self['PSIRZ'] = gEQDSK['PSIRZ']

        self['AuxQuantities'] = SortedDict()
        self['AuxQuantities']['R'] = gEQDSK['AuxQuantities']['R']
        self['AuxQuantities']['Z'] = gEQDSK['AuxQuantities']['Z']
        self['AuxQuantities']['PSI'] = gEQDSK['AuxQuantities']['PSI']
        self['AuxQuantities']['PSIRZ'] = gEQDSK['AuxQuantities']['PSIRZ']
        self['AuxQuantities']['VOL'] = gEQDSK['fluxSurfaces']['geo']['vol']
        self['AuxQuantities']['AREA'] = gEQDSK['fluxSurfaces']['geo']['vol'] * 0.0

        # use rho_tor inside lcfs, rho_pol outside... (to be improved later?)
        self['AuxQuantities']['RHO'] = RHO = gEQDSK['AuxQuantities']['RHO']
        self['AuxQuantities']['RHORZ'] = RHORZ = gEQDSK['AuxQuantities']['RHORZ']
        RHOp = gEQDSK['AuxQuantities']['RHOp']
        RHOpRZ = gEQDSK['AuxQuantities']['RHOpRZ']
        self['AuxQuantities']['RHO'][np.where(RHO > 1)] = RHOp[np.where(RHO > 1)]
        self['AuxQuantities']['RHORZ'][np.where(RHORZ > 1)] = RHOpRZ[np.where(RHORZ > 1)]

        return self

    def save_from_gFile(self, filename, gEQDSK):  # Save a gEQDSK file as an self file
        def print6(f, d):  # print to file in rows of 6
            i0 = 0
            for i in range(int(len(d) // 6)):
                f.write(('{:13.6f}' * 6 + '\n').format(*d[i0 : i0 + 6]))
                i0 += 6
            for i in range(i0, len(d)):
                f.write('{:13.6f}'.format(d[i]))
            f.write('\n')

        data = {
            'NW': gEQDSK['NW'],
            'NH': gEQDSK['NH'],
            'PSIRZ': gEQDSK['PSIRZ'],
            'NPsi1d': len(gEQDSK['QPSI']),
            'QPSI': gEQDSK['QPSI'],
            'FPOL': gEQDSK['FPOL'],
            'SIBRY': gEQDSK['SIBRY'],
            'SIMAG': gEQDSK['SIMAG'],
            'signIp': np.sign(gEQDSK['CURRENT']),
            'RMAXIS': gEQDSK['RMAXIS'],
            'ZMAXIS': gEQDSK['ZMAXIS'],
            'AuxQuantities': SortedDict(
                {
                    'R': gEQDSK['AuxQuantities']['R'],
                    'Z': gEQDSK['AuxQuantities']['Z'],
                    'PSIRZ': gEQDSK['AuxQuantities']['PSIRZ'],
                    'rhotor': gEQDSK['AuxQuantities']['RHORZ'],
                    'PSI': gEQDSK['AuxQuantities']['PSI'],
                    'vol': np.zeros(len(gEQDSK['QPSI'])),
                    'PSI_NORM': gEQDSK['AuxQuantities']['PSI_NORM'],
                }
            ),
        }

        with open(filename, 'w') as f:
            f.write('          {}\n'.format(data['NW']))
            f.write('          {}\n'.format(data['NH']))

            print6(f, data['AuxQuantities']['R'])
            print6(f, data['AuxQuantities']['Z'])

            for d in data['AuxQuantities']['PSIRZ']:
                print6(f, d)
            for d in data['AuxQuantities']['rhotor']:
                print6(f, d)

            f.write('          {}\n'.format(data['NPsi1d']))

            print6(f, np.zeros(data['NPsi1d']))
            print6(f, data['AuxQuantities']['PSI'])
            print6(f, data['AuxQuantities']['vol'])
            print6(f, data['AuxQuantities']['PSI_NORM'])
            print6(f, data['QPSI'])
            print6(f, data['FPOL'])

            f.write(
                '{:12.6f}{:12.6f}{:12.6f}{:12.6f}{:12.6f}\n'.format(
                    data['SIBRY'], data['SIMAG'], data['signIp'], data['RMAXIS'], data['ZMAXIS']
                )
            )


class OMFITrabbitBeamout(SortedDict, OMFITascii):
    """Beam output files from RABBIT"""

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        import struct

        struct_fmt = 'f'
        struct_len = struct.calcsize(struct_fmt)
        struct_unpack = struct.Struct(struct_fmt).unpack_from

        names = [
            'ntime',
            'nrho',
            'nv',
            'nleg',
            'rabbit_version',
            'time',
            'rho',
            'bdens',
            'press',
            'powe',
            'powi',
            'jfi',
            'jnbcd',
            'bdep',
            'bdep_k1',
            'dV',
            'pheatI',
            'pheatE',
            'pheat',
            'pshine',
            'prot',
            'ploss',
            'pcx',
            'dArea',
            'torqdepo',
            'torqjxb',
            'torqe',
            'torqi',
            'wfi_par',
            'wfi_perp',
        ]

        data_names = {}
        data_names['time'] = 'Time'
        data_names['rho'] = 'rho'
        data_names['bdens'] = 'Fast-ion Density'
        data_names['press'] = 'Fast-ion Pressure'
        data_names['powe'] = 'Power Density Profile to Electrons'
        data_names['powi'] = 'Power Density Profile to Ions'
        data_names['jfi'] = 'Fast-ion Current Density'
        data_names['jnbcd'] = 'Driven Current Density'
        data_names['bdep'] = 'Particle Source Density (per Energy Component)'
        data_names['bdep_k1'] = r'Particle Source Average Pitch $\langle v_\parallel/v\rangle$ (per Energy Component)'
        data_names['dV'] = 'Volume of Radial Cell'
        data_names['pheatI'] = 'Ion Heating Power'
        data_names['pheatE'] = 'Electron Heating Power'
        data_names['pheat'] = 'Heating Power'
        data_names['pshine'] = 'Shine-thru Power'
        data_names['prot'] = 'Power to Rotation'
        data_names['ploss'] = 'Beam Power Losses in SOL'
        data_names['pcx'] = 'Charge Exchange Loss'
        data_names['dArea'] = 'Poloidal Cross-Sectional Area of Radial Cell'
        data_names['torqdepo'] = 'Deposited Torque Density'
        data_names['torqjxb'] = 'JxB Torque Density'
        data_names['torqe'] = 'Collisional Torque Density to Electrons'
        data_names['torqi'] = 'Collisional Torque Density to Ions'
        data_names['wfi_par'] = 'Stored Fast-Ion Energy Density (parallel)'
        data_names['wfi_perp'] = 'Stored Fast-Ion Energy Density (perpendicular)'

        units = {}
        units['time'] = r'(s)'
        units['rho'] = r'(-)'
        units['bdens'] = r'(# m$^{-3}$)'
        units['press'] = r'(Pa)'
        units['powe'] = r'(W / m$^3$)'
        units['powi'] = r'(W / m$^3$)'
        units['jfi'] = r'(A / m$^2$)'
        units['jnbcd'] = r'(A / m$^2$)'
        units['bdep'] = r'(# m$^{-3}$ s$^{-1}$)'
        units['bdep_k1'] = r'(-)'
        units['dV'] = r'(m$^3$)'
        units['pheatI'] = r'(W)'
        units['pheatE'] = r'(W)'
        units['pheat'] = r'(W)'
        units['pshine'] = r'(W)'
        units['prot'] = r'(W)'
        units['ploss'] = r'(W)'
        units['pcx'] = r'(W)'
        units['dArea'] = r'(m$^2$)'
        units['torqdepo'] = r'(Nm / m$^3$)'
        units['torqjxb'] = r'(Nm / m$^3$)'
        units['torqe'] = r'(Nm / m$^3$)'
        units['torqi'] = r'(Nm / m$^3$)'
        units['wfi_par'] = r'(J / m$^3$)'
        units['wfi_perp'] = r'(J / m$^3$)'

        for name in names:
            self[name] = SortedDict()
            try:
                self[name]['name'] = data_names[name]
                self[name]['unit'] = units[name]
            except KeyError:
                pass

        with open(self.filename, mode='rb') as f:
            while True:
                f.seek(0, 2)
                file_size = f.tell()
                f.seek(0)  # get file size

                self['ntime'] = ntime = int(struct_unpack(f.read(struct_len))[0])
                self['nrho'] = nrho = int(struct_unpack(f.read(struct_len))[0])
                self['nv'] = nv = int(struct_unpack(f.read(struct_len))[0])

                self['time']['data'] = np.zeros((ntime,))
                for i in range(ntime):
                    self['time']['data'][i] = struct_unpack(f.read(struct_len))[0]

                self['rho']['data'] = np.zeros((nrho,))
                for i in range(nrho):
                    self['rho']['data'][i] = struct_unpack(f.read(struct_len))[0]

                bdens = np.zeros((nrho * ntime,))
                for i in range(bdens.size):
                    bdens[i] = struct_unpack(f.read(struct_len))[0]
                self['bdens']['data'] = np.reshape(bdens, (ntime, nrho))

                press = np.zeros((nrho * ntime,))
                for i in range(press.size):
                    press[i] = struct_unpack(f.read(struct_len))[0]
                self['press']['data'] = np.reshape(press, (ntime, nrho))

                powe = np.zeros((nrho * ntime,))
                for i in range(powe.size):
                    powe[i] = struct_unpack(f.read(struct_len))[0]
                self['powe']['data'] = np.reshape(powe, (ntime, nrho))

                powi = np.zeros((nrho * ntime,))
                for i in range(powi.size):
                    powi[i] = struct_unpack(f.read(struct_len))[0]
                self['powi']['data'] = np.reshape(powi, (ntime, nrho))

                jfi = np.zeros((nrho * ntime,))
                for i in range(jfi.size):
                    jfi[i] = struct_unpack(f.read(struct_len))[0]
                self['jfi']['data'] = np.reshape(jfi, (ntime, nrho))

                jnbcd = np.zeros((nrho * ntime,))
                for i in range(jnbcd.size):
                    jnbcd[i] = struct_unpack(f.read(struct_len))[0]
                self['jnbcd']['data'] = np.reshape(jnbcd, (ntime, nrho))

                ## test to see if next line exists ##
                next_line = f.read(struct_len)
                if not next_line:
                    break

                dV = np.zeros((nrho * ntime,))
                dV[0] = struct_unpack(next_line)[0]
                for i in range(dV.size - 1):
                    dV[i + 1] = struct_unpack(f.read(struct_len))[0]
                self['dV']['data'] = np.reshape(dV, (ntime, nrho))

                bdep = np.zeros((nrho * nv * ntime,))
                for i in range(bdep.size):
                    bdep[i] = struct_unpack(f.read(struct_len))[0]
                self['bdep']['data'] = np.reshape(bdep, (ntime, nv, nrho))

                bdep_k1 = np.zeros((nrho * nv * ntime,))
                for i in range(bdep_k1.size):
                    bdep_k1[i] = struct_unpack(f.read(struct_len))[0]
                self['bdep_k1']['data'] = np.reshape(bdep_k1, (ntime, nv, nrho))

                ## test to see if next line exists ##
                next_line = f.read(struct_len)
                if not next_line:
                    break

                self['pheatI']['data'] = np.zeros((ntime,))
                self['pheatI']['data'][0] = struct_unpack(next_line)[0]
                for i in range(ntime - 1):
                    self['pheatI']['data'][i + 1] = struct_unpack(f.read(struct_len))[0]

                self['pheatE']['data'] = np.zeros((ntime,))
                for i in range(ntime):
                    self['pheatE']['data'][i] = struct_unpack(f.read(struct_len))[0]

                self['pheat']['data'] = np.zeros((ntime,))
                for i in range(ntime):
                    self['pheat']['data'][i] = struct_unpack(f.read(struct_len))[0]

                self['pshine']['data'] = np.zeros((ntime,))
                for i in range(ntime):
                    self['pshine']['data'][i] = struct_unpack(f.read(struct_len))[0]

                ## test to see if next line exists ##
                next_line = f.read(struct_len)
                if not next_line:
                    break

                self['prot']['data'] = np.zeros((ntime,))
                self['prot']['data'][0] = struct_unpack(next_line)[0]
                for i in range(ntime - 1):
                    self['prot']['data'][i + 1] = struct_unpack(f.read(struct_len))[0]

                self['ploss']['data'] = np.zeros((ntime,))
                for i in range(ntime):
                    self['ploss']['data'][i] = struct_unpack(f.read(struct_len))[0]

                ## test to see if next line exists ##
                next_line = f.read(struct_len)
                if not next_line:
                    break

                self['pcx']['data'] = np.zeros((ntime,))
                self['pcx']['data'][0] = struct_unpack(next_line)[0]
                for i in range(ntime - 1):
                    self['pcx']['data'][i + 1] = struct_unpack(f.read(struct_len))[0]

                ## test to see if torque calculations have been preformed ##
                if file_size - f.tell() > nrho * ntime * struct_len:
                    rabbit_version_strlen = struct.unpack('i', f.read(struct_len))[0]
                    if int(rabbit_version_strlen) > 0:
                        self['rabbit_version'] = str(struct.unpack('s' * rabbit_version_strlen, f.read(rabbit_version_strlen))[0])

                        dArea = np.zeros((nrho * ntime,))
                        for i in range(dV.size):
                            dArea[i] = struct_unpack(f.read(struct_len))[0]
                        self['dArea']['data'] = np.reshape(dArea, (ntime, nrho))

                        torqdepo = np.zeros((nrho * nv * ntime,))
                        for i in range(torqdepo.size):
                            torqdepo[i] = struct_unpack(f.read(struct_len))[0]
                        self['torqdepo']['data'] = np.reshape(torqdepo, (ntime, nv, nrho))

                        torqjxb = np.zeros((nrho * nv * ntime,))
                        for i in range(torqjxb.size):
                            torqjxb[i] = struct_unpack(f.read(struct_len))[0]
                        self['torqjxb']['data'] = np.reshape(torqjxb, (ntime, nv, nrho))

                        torqe = np.zeros((nrho * ntime,))
                        for i in range(torqe.size):
                            torqe[i] = struct_unpack(f.read(struct_len))[0]
                        self['torqe']['data'] = np.reshape(torqe, (ntime, nrho))

                        torqi = np.zeros((nrho * ntime,))
                        for i in range(torqi.size):
                            torqi[i] = struct_unpack(f.read(struct_len))[0]
                        self['torqi']['data'] = np.reshape(torqi, (ntime, nrho))
                    else:
                        self['rabbit_version'] = 'undef'

                ## test to see if next line exists ##
                next_line = f.read(struct_len)
                if not next_line:
                    break

                self['nleg'] = int(struct.unpack('i', next_line)[0])

                ## test to see if wfi calculations have been preformed ##
                if file_size - f.tell() >= nrho * ntime * struct_len:
                    wfi_par = np.zeros((nrho * ntime,))
                    for i in range(wfi_par.size):
                        wfi_par[i] = struct_unpack(f.read(struct_len))[0]
                    self['wfi_par']['data'] = np.reshape(wfi_par, (ntime, nrho))

                    self['wfi_perp']['data'] = 1.5 * self['press']['data'] - self['wfi_par']['data']

                ## test to see if there are any remaining lines ##
                if f.tell() < file_size:
                    printw('Warning: {} bytes remain in file!'.format(file_size - f.tell()))

                ## eof ##
                break

        ## get rid of anything that is empty
        for key in list(self.keys()):
            if not self[key]:
                del self[key]
            elif isinstance(self[key], dict) and 'data' not in self[key].keys():
                del self[key]

    @dynaLoad
    def plot(self):
        # plot current density
        pyplot.subplot(221)

        contourf(self['time']['data'], self['rho']['data'], self['jfi']['data'].T, 100)
        cbar = colorbar()
        cbar.set_label(self['jfi']['unit'])
        pyplot.xlabel('time (s)')
        pyplot.ylabel('rho')
        pyplot.title(self['jfi']['name'])

        # plot pressure
        pyplot.subplot(222)

        contourf(self['time']['data'], self['rho']['data'], self['press']['data'].T, 100)
        cbar = colorbar()
        cbar.set_label(self['press']['unit'])
        pyplot.xlabel('time (s)')
        pyplot.ylabel('rho')
        pyplot.title(self['press']['name'])

        # plot density
        pyplot.subplot(223)

        contourf(self['time']['data'], self['rho']['data'], self['bdens']['data'].T, 100)
        cbar = colorbar()
        cbar.set_label(self['bdens']['unit'])
        pyplot.xlabel('time (s)')
        pyplot.ylabel('rho')
        pyplot.title(self['bdens']['name'])

        # plot rotation power
        pyplot.subplot(224)

        pyplot.plot(self['time']['data'], self['prot']['data'])
        pyplot.xlabel('time (s)')
        pyplot.ylabel(self['prot']['unit'])
        pyplot.title(self['prot']['name'])

        cornernote(time='')

        tight_layout()


class OMFITrabbitTimetraces(SortedDict, OMFITascii):
    """Timetraces input file for RABBIT"""

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)

        self.names = SortedDict()
        self.names['time'] = 'Time'
        self.names['rho'] = r'\rho'
        self.names['te'] = r'T$_e$'
        self.names['ti'] = r'T$_i$'
        self.names['dene'] = r'n$_e$'
        self.names['vtor'] = r'v$_{tor}$'
        self.names['zeff'] = r'Z$_{eff}$'
        self.names['pnbi'] = r'P$_{NBI}$'

        self.units = SortedDict()
        self.units['time'] = 's'
        self.units['rho'] = '-'
        self.units['te'] = 'keV'
        self.units['ti'] = 'keV'
        self.units['dene'] = r'1/cm$^3$'
        self.units['vtor'] = 'rad/s, sign wrt. tor. angle phi'
        self.units['zeff'] = '-'
        self.units['pnbi'] = 'W'

        if os.stat(self.filename).st_size:
            self.dynaLoad = True
        else:
            self['n_time'] = 0
            self['n_rho'] = 0
            for key in self.names.keys():
                if key == 'time':
                    self[key] = DataArray(np.array([0]), dims=('time'), coords={'time': np.array([0])})
                elif key == 'rho':
                    self[key] = DataArray(np.array([0]), dims=('rho'), coords={'rho': np.array([0])})
                else:
                    self[key] = DataArray(
                        np.array([[0], [0]]), dims=('rho', 'time'), coords={'rho': np.array([0, 0]), 'time': np.array([0])}
                    )
                self[key].name = self.names[key]
                self[key].__setitem__('units', self.units[key])

    @dynaLoad
    def load(self):
        with open(self.filename, mode='r') as f:
            content = f.readlines()
        flatten = lambda l: [item for sublist in l for item in sublist]
        content = flatten([x.split() for x in content])

        self['n_time'] = n_time = int(content[0])
        self['n_rho'] = n_rho = int(content[1])

        i1 = 3
        i2 = 3 + n_time
        time = np.array([float(x) for x in content[i1:i2]])
        self['time'] = DataArray(time, dims=('time'), coords={'time': time})

        i1 = i2
        i2 += n_rho
        rho = np.array([float(x) for x in content[i1:i2]])
        self['rho'] = DataArray(rho, dims=('rho'), coords={'rho': rho})

        i1 = i2
        i2 += n_time * n_rho
        self['te'] = DataArray(
            np.array([float(x) for x in content[i1:i2]]).reshape((n_rho, n_time)), dims=('rho', 'time'), coords={'rho': rho, 'time': time}
        )

        i1 = i2
        i2 += n_time * n_rho
        self['ti'] = DataArray(
            np.array([float(x) for x in content[i1:i2]]).reshape((n_rho, n_time)), dims=('rho', 'time'), coords={'rho': rho, 'time': time}
        )

        i1 = i2
        i2 += n_time * n_rho
        self['dene'] = DataArray(
            np.array([float(x) for x in content[i1:i2]]).reshape((n_rho, n_time)), dims=('rho', 'time'), coords={'rho': rho, 'time': time}
        )

        i1 = i2
        i2 += n_time * n_rho
        self['vtor'] = DataArray(
            np.array([float(x) for x in content[i1:i2]]).reshape((n_rho, n_time)), dims=('rho', 'time'), coords={'rho': rho, 'time': time}
        )

        i1 = i2
        i2 += n_time * n_rho
        self['zeff'] = DataArray(
            np.array([float(x) for x in content[i1:i2]]).reshape((n_rho, n_time)), dims=('rho', 'time'), coords={'rho': rho, 'time': time}
        )

        i1 = i2
        self['pnbi'] = DataArray(
            np.array([float(x) for x in content[i1:]]).reshape((-1, n_time)), dims=('beams', 'time'), coords={'time': time}
        )

        for key in self.names.keys():
            self[key].name = self.names[key]
            self[key].__setitem__('units', self.units[key])

    @dynaSave
    def save(self):
        def cropdata_f(data, nw):
            text = ''
            if len(data) < nw:
                text += ''.join(['       {:8.7f}'.format(data[j])[:16] for j in range(len(data))]) + '\n'
            else:
                for i in range(int(len(data) // nw)):
                    text += ''.join(['       {:8.7f}'.format(data[j + (i * nw)])[:16] for j in range(nw)]) + '\n'
                if ((nw - 1) + (i * nw)) < len(data):  # crop the remainder
                    text += ''.join(['       {:8.7f}'.format(item)[:16] for item in data[(nw - 1) + (i * nw) + 1 :]]) + '\n'
            return text

        def cropdata_e(data, nw):
            text = ''
            if len(data) < nw:
                text += ''.join(['   {:.7e}'.format(data[j])[:16] for j in range(len(data))]) + '\n'
            else:
                for i in range(int(len(data) // nw)):
                    text += ''.join(['   {:.7e}'.format(data[j + (i * nw)])[:16] for j in range(nw)]) + '\n'
                if ((nw - 1) + (i * nw)) < len(data):  # crop the remainder
                    text += ''.join(['   {:.7e}'.format(item)[:16] for item in data[(nw - 1) + (i * nw) + 1 :]]) + '\n'
            return text

        nw = 5
        tttext = ''
        tttext += '         ' + str(self['n_time']) + '\n'
        tttext += '         ' + str(self['n_rho']) + '\n'
        tttext += 'rho_tor' + '\n'
        tttext += cropdata_f(self['time'].data, nw)
        tttext += cropdata_f(self['rho'].data, nw)
        for row in self['te'].data:
            tttext += cropdata_f(row, nw)
        for row in self['ti'].data:
            tttext += cropdata_f(row, nw)
        for row in self['dene'].data:
            tttext += cropdata_e(row, nw)
        for row in self['vtor'].data:
            tttext += cropdata_f(row, nw)
        for row in self['zeff'].data:
            tttext += cropdata_f(row, nw)
        for row in self['pnbi'].data:
            tttext += cropdata_f(row, nw)

        with open(self.filename, 'w') as f:
            f.writelines(tttext)


class OMFITrabbitBeamin(SortedDict, OMFITascii):
    """Beam input file for RABBIT"""

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)

        self.names = SortedDict()
        self.names['start_pos'] = 'Starting positions of each beam'
        self.names['unit_vecs'] = 'Beam unit vectors'
        self.names['bwp_coeff'] = 'Beam width polynomial coefficients'
        self.names['E_inj'] = 'Injection energy'
        self.names['part_frac'] = 'Particle fraction of full/half/third energy'
        self.names['a_beam'] = 'A beam'

        self.units = SortedDict()
        self.units['start_pos'] = 'm'
        self.units['unit_vecs'] = '-'
        self.units['bwp_coeff'] = '-'
        self.units['E_inj'] = 'eV'
        self.units['part_frac'] = '-'
        self.units['a_beam'] = '-'

        if os.stat(self.filename).st_size:
            self.dynaLoad = True
        else:
            self['num_beams'] = 8  # THIS IS DIII-D HARD-CODED
            self['nv'] = 3  # THIS IS DIII-D HARD-CODED
            for key in self.names.keys():
                self[key] = {}
                self[key]['data'] = [0]
                self[key]['name'] = self.names[key]
                self[key]['unit'] = self.units[key]

    @dynaLoad
    def load(self):
        with open(self.filename, mode='r') as f:
            content = f.readlines()
        content = [x.strip() for x in content]

        self['num_beams'] = nb = int(content[1])
        self['nv'] = nv = int(content[3])

        i1 = 5
        i2 = i1 + nb
        self['start_pos'] = {}
        self['start_pos']['data'] = []
        for i in range(i1, i2):
            self['start_pos']['data'].append([float(x) for x in content[i].split()])

        i1 = i2 + 1
        i2 = i1 + nb
        self['unit_vecs'] = {}
        self['unit_vecs']['data'] = []
        for i in range(i1, i2):
            self['unit_vecs']['data'].append([float(x) for x in content[i].split()])

        i1 = i2 + 1
        i2 = i1 + nb
        self['bwp_coeff'] = {}
        self['bwp_coeff']['data'] = []
        for i in range(i1, i2):
            self['bwp_coeff']['data'].append([float(x) for x in content[i].split()])

        i1 = i2 + 1
        i2 = i1 + 1 + (nb - 1) // len(content[i1].split())
        self['E_inj'] = {}
        self['E_inj']['data'] = []
        for i in range(i1, i2):
            self['E_inj']['data'] += [float(x) for x in content[i].split()]

        i1 = i2 + 1
        i2 = i1 + nb
        self['part_frac'] = {}
        self['part_frac']['data'] = []
        for i in range(i1, i2):
            self['part_frac']['data'].append([float(x) for x in content[i].split()])

        i1 = i2 + 1
        i2 = i1 + 1 + (nb - 1) // len(content[i1].split())
        self['a_beam'] = {}
        self['a_beam']['data'] = []
        for i in range(i1, i2):
            self['a_beam']['data'] += [float(x) for x in content[i].split()]

        for key in self.names.keys():
            self[key]['name'] = self.names[key]
            self[key]['unit'] = self.units[key]

    @dynaSave
    def save(self):
        def print5(d):  # print to file in rows of 5
            i0 = 0
            text = []
            for i in range(int(len(d) // 5)):
                text.append(('{:16.3f}' * 5).format(*d[i0 : i0 + 5]))
                i0 += 5
            endtext = ''
            for i in range(i0, len(d)):
                endtext += '{:16.3f}'.format(d[i])
            text.append(endtext)
            return text

        ftext = []
        ftext.append('# no. of sources:')
        ftext.append('           {}'.format(self['num_beams']))
        ftext.append('# nv:')
        ftext.append('           {}'.format(self['nv']))
        ftext.append('# start pos: [m]')
        for x in self['start_pos']['data']:
            ftext.append('{:16.7f}{:16.7f}{:16.7f}'.format(x[0], x[1], x[2]))
        ftext.append('# beam unit vector:')
        for x in self['unit_vecs']['data']:
            ftext.append('{:16.8f}{:16.8f}{:16.8f}'.format(x[0], x[1], x[2]))
        ftext.append('# beam-width-polynomial coefficients:')
        for x in self['bwp_coeff']['data']:
            ftext.append('{:16.8f}{:16.8f}{:16.8f}'.format(x[0], x[1], x[2]))
        ftext.append('# Injection energy [eV]:')
        ftext += print5(self['E_inj']['data'])
        ftext.append('# Particle fraction of full/half/third energy:')
        for x in self['part_frac']['data']:
            ftext.append('{:16.8f}{:16.8f}{:16.8f}'.format(x[0], x[1], x[2]))
        ftext.append('# A beam [u]')
        ftext += print5(self['a_beam']['data'])
        ftext = '\n'.join(ftext) + '\n'

        with open(self.filename, 'w') as f:
            f.write(ftext)

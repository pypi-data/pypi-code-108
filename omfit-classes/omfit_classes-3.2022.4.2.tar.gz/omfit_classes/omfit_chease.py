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
from omfit_classes.utils_math import cicle_fourier_smooth

import numpy as np
import scipy.interpolate as interpolate

__all__ = ['OMFITchease', 'OMFITcheaseLog']


class OMFITchease(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with CHEASE EXPEQ files

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True

        self.rhotypes = {0: 'RHO_PSI', 1: 'RHO_TOR'}
        self.names = {
            1: ['PSI', 'PPRIME', 'FFPRIM'],
            2: ['PSI', 'PPRIME', 'JTOR'],
            3: ['PSI', 'PPRIME', 'JPAR'],
            41: ['RHO', 'PPRIME', 'FFPRIM'],
            42: ['RHO', 'PPRIME', 'JTOR'],
            43: ['RHO', 'PPRIME', 'JPAR'],
            44: ['RHO', 'PPRIME', 'IPAR'],
            45: ['RHO', 'PPRIME', 'Q'],
            81: ['RHO', 'PRES', 'FFPRIM'],
            82: ['RHO', 'PRES', 'JTOR'],
            83: ['RHO', 'PRES', 'JPAR'],
            84: ['RHO', 'PRES', 'IPAR'],
            85: ['RHO', 'PRES', 'Q'],
        }

    @dynaLoad
    def load(self):

        if self.filename is None or not os.stat(self.filename).st_size:
            return

        with open(self.filename, 'r') as f:
            lines = f.read().split('\n')

        tmp = lines[3].split()
        if len(tmp) == 1:
            self.version = 'standard'
            n1 = int(lines[3])
            n2 = 1
            n3 = 2
        elif len(tmp) == 3:
            self.version = 'mars'
            (
                n1,
                n2,
                n3,
            ) = list(map(int, tmp))
        else:
            raise OMFITexception('%s is not a valid OMFITchease file' % self.filename)

        self['EPS'] = float(lines[0])
        self['Z_AXIS'] = float(lines[1])
        self['P_SEP'] = float(lines[2])

        boundaries = []
        for b in range(n2):
            tmp = []
            for k, line in enumerate(lines[4 + n1 * b : 4 + n1 * (b + 1)]):
                tmp.append(list(map(float, line.split())))
            tmp = np.array(tmp)
            boundaries.append(tmp)

        bounds = ['PLASMA'] + ['LIMITER_%d' % k for k in range(len(boundaries) - 1)]
        self['BOUNDARY'] = {}
        for k, bound in enumerate(bounds):
            self['BOUNDARY'][bound] = {}
            self['BOUNDARY'][bound]['R'] = boundaries[k][:, 0]
            self['BOUNDARY'][bound]['Z'] = boundaries[k][:, 1]
            if n3 > 2:
                self['BOUNDARY'][bound]['x'] = boundaries[k][:, 2]

        offset = 4 + n1 * n2
        if self.version == 'standard':
            tmp = lines[offset].split()
            l = int(tmp[0])
            if len(tmp) > 1:
                self.nppfun = int(tmp[1])
            else:
                self.nppfun = 4
            tmp = lines[offset + 1].split()
            self.nsttp = int(tmp[0])
            self.nrhotype = int(tmp[1])
            self['MODE'] = self.nppfun * 10 + self.nsttp
        elif self.version == 'mars':
            l = int(lines[offset])
            self['MODE'] = int(lines[offset + 1])

        for k, name in enumerate(self.names[self['MODE']]):
            if (name == 'RHO') and (self.version == 'standard'):
                name = self.rhotypes[self.nrhotype]
            self[name] = np.array(list(map(float, lines[offset + 2 + l * k : offset + 2 + l * (k + 1)])))
        offset = offset + 2 + l * (k + 1) + 1

        self['NOTES'] = []
        for line in lines[offset:]:
            if line.strip():
                self['NOTES'].append(line.rstrip('\n'))
        self['NOTES'] = '\n'.join(self['NOTES'])

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """

        with open(self.filename, 'w') as f:
            f.write(str(self['EPS']) + '\n')
            f.write(str(self['Z_AXIS']) + '\n')
            f.write(str(self['P_SEP']) + '\n')
            n1 = len(self['BOUNDARY']['PLASMA']['R'])
            if self.version == 'standard':
                n2 = 1
                n3 = 2
                f.write(str(n1) + '\n')
            elif self.version == 'mars':
                n2 = len(self['BOUNDARY'])
                n3 = len(self['BOUNDARY']['PLASMA'])
                tmp = np.hstack((n1, n2, n3))
                f.write(' '.join(map(str, tmp)) + '\n')
            bounds = ['PLASMA'] + ['LIMITER_%d' % k for k in range(n2 - 1)]
            for bound in bounds:
                tmp = np.vstack([self['BOUNDARY'][bound]['R'], self['BOUNDARY'][bound]['Z']]).T
                shape = list(tmp.shape)
                for k in range(tmp.shape[0]):
                    f.write(' '.join(['%5.9e' % x for x in tmp[k, :]]) + '\n')
            # Write length of profiles
            l = len(self[self.names[self['MODE']][-1]])
            if self.version == 'standard':
                tmp = np.hstack((l, self.nppfun))
                f.write(' '.join(map(str, tmp)) + '\n')
                tmp = np.hstack((self.nsttp, self.nrhotype))
                f.write(' '.join(map(str, tmp)) + '\n')
            elif self.version == 'mars':
                f.write(str(l) + '\n')
                # Write number corresponding to profile combitation
                f.write(str(self['MODE']) + '\n')
            for name in self.names[self['MODE']]:
                if (name == 'RHO') and (self.version == 'standard'):
                    name = self.rhotypes[self.nrhotype]
                tmp = self[name]
                shape = list(tmp.shape)
                for k in range(shape[0]):
                    f.write(str('%5.9e' % tmp[k]) + '\n')
            if len(self['NOTES'].strip()):
                f.write(self['NOTES'].rstrip('\n') + '\n')

    @staticmethod
    def splineRZ(R, Z, Nnew):
        """
        Auxilliary function to spline single boundary from EXPEQ

        :param R: array 1 (R coordinate)

        :param Z: array 2 (Z coordinate)

        :param Nnew: new number of points

        :return: smoothed R,Z

        """
        npoints = len(R)
        degree = 3
        t = np.linspace(-np.pi, np.pi, npoints)
        ipl_t = np.linspace(-np.pi, np.pi, Nnew)
        R_i = interpolate.UnivariateSpline(t, R, k=degree, s=1.0e-5)(ipl_t)
        Z_i = interpolate.UnivariateSpline(t, Z, k=degree, s=1.0e-5)(ipl_t)
        return R_i, Z_i

    def EQsmooth(self, keep_M_harmonics, inPlace=True, equalAngle=False, doPlot=False):
        """
        smooth plasma boundary by zeroing out high harmonics

        :param keep_M_harmonics: how many harmonics to keep

        :param inPlace: operate in place (update this file or not)

        :param equalAngle: use equal angle interpolation, and if so, how many points to use

        :param doPlot: plot plasma boundary before and after

        :return: smoothed R and Z coordinates
        """

        R = self['BOUNDARY']['PLASMA']['R']
        Z = self['BOUNDARY']['PLASMA']['Z']

        RS, ZS = cicle_fourier_smooth(R, Z, keep_M_harmonics, equalAngle=equalAngle, doPlot=doPlot)

        if inPlace:
            self['BOUNDARY']['PLASMA']['R'] = RS
            self['BOUNDARY']['PLASMA']['Z'] = ZS

        return RS, ZS

    def addLimiter(self, R, Z):
        """
        Insertion of a wall defined by coordinates (R,Z)

        :R = radial coordinate

        :Z = vertical coordinate

        Note: both must be normalized, and ndarray type
        """
        if len(self['BOUNDARY']) == 0:
            raise ("Error. No PLASMA found")
        else:
            d = len(self['BOUNDARY']) - 1
            self['BOUNDARY']['LIMITER_' + str(d)] = {}
            self['BOUNDARY']['LIMITER_' + str(d)]['R'] = R
            self['BOUNDARY']['LIMITER_' + str(d)]['Z'] = Z

    def modifyBoundary(self):
        """
        Interactively modify plasma boundary
        """
        R = self['BOUNDARY']['PLASMA']['R']
        Z = self['BOUNDARY']['PLASMA']['Z']
        tmp = fluxGeo(R, Z)

        bs = BoundaryShape(
            a=tmp['a'],
            eps=tmp['eps'],
            kapu=tmp['kapu'],
            kapl=tmp['kapl'],
            delu=tmp['delu'],
            dell=tmp['dell'],
            zetaou=tmp['zetaou'],
            zetaiu=tmp['zetaiu'],
            zetail=tmp['zetail'],
            zetaol=tmp['zetaol'],
            zoffset=tmp['zoffset'],
            rbbbs=R,
            zbbbs=Z,
            upnull=False,
            lonull=True,
        )

        self['BOUNDARY']['PLASMA']['R'] = bs['r']
        self['BOUNDARY']['PLASMA']['Z'] = bs['z']

        bs.plot()

    def from_gEQDSK(self, gEQDSK=None, conformal_wall=False, mode=None, rhotype=0, version=None, cocos=2):
        """
        Modify CHEASE EXPEQ file with data loaded from gEQDSK

        :param gEQDSK: input gEQDKS file from which to copy the plasma boundary

        :param conformal_wall: floating number that multiplies plasma boundary (should be >1)

        :param mode: select profile to use from gEQDSK

        :param rhotype: 0 for poloidal flux. 1 for toroidal flux. Only with version=='standard'

        :param version: either 'standard' or 'mars'

        """

        if version is None:
            if hasattr(self, 'version'):
                version = self.version
            else:
                version = 'standard'
        if mode is None:
            if 'MODE' in self:
                mode = self['MODE']
            else:
                mode = {'standard': 41, 'mars': 1}[version]

        gEQDSK = gEQDSK.cocosify(cocos, True, True, False)

        R0 = gEQDSK['RCENTR']
        B0 = gEQDSK['BCENTR']

        # normalizations from section 5.4.6 of CHEASE manual

        if version not in ['standard', 'mars']:
            OMFITexception('Cannot create OMFITchease in version %s' % version)
        else:
            self.version = version

        self['EPS'] = gEQDSK['fluxSurfaces']['geo']['eps'][-1]
        self['Z_AXIS'] = gEQDSK['ZMAXIS'] / R0
        self['P_SEP'] = gEQDSK['PRES'][-1] / (B0 ** 2 / constants.mu_0)

        self['BOUNDARY'] = {}
        self['BOUNDARY']['PLASMA'] = {}
        self['BOUNDARY']['PLASMA']['R'] = gEQDSK['RBBBS'] / R0
        self['BOUNDARY']['PLASMA']['Z'] = gEQDSK['ZBBBS'] / R0

        if version == 'mars':
            # conformal wall
            if 'LIMITER_0' not in self['BOUNDARY']:
                self['BOUNDARY']['LIMITER_0'] = {}
            if conformal_wall:
                self['BOUNDARY']['LIMITER_0']['R'] = (self['BOUNDARY']['PLASMA']['R'] - 1) * conformal_wall + 1
                self['BOUNDARY']['LIMITER_0']['Z'] = (self['BOUNDARY']['PLASMA']['Z'] - self['Z_AXIS']) * conformal_wall + self['Z_AXIS']
            # original wall
            else:
                self['BOUNDARY']['LIMITER_0']['R'] = gEQDSK['RLIM'] / R0
                self['BOUNDARY']['LIMITER_0']['Z'] = gEQDSK['ZLIM'] / R0

        # Deleting all possible profiles to avoid conflicts
        profiles = ['PSI', 'RHO_PSI', 'RHO_TOR']  # coordinates
        profiles += ['PPRIME', 'PRES']  # pressure
        profiles += ['FFPRIM', 'JTOR', 'JPAR', 'IPAR', 'Q']  # current
        for prof in profiles:
            self.safe_del(prof)

        if version == 'standard':

            # coordinate
            if rhotype == 0:
                self['RHO_PSI'] = gEQDSK['AuxQuantities']['RHOp']
            elif rhotype == 1:
                self['RHO_TOR'] = gEQDSK['AuxQuantities']['RHO']
            self.nrhotype = rhotype

            # pressure
            if mode in [1, 2] or int(mode / 10) == 4:
                self['PPRIME'] = gEQDSK['PPRIME'] / np.abs(B0 / (constants.mu_0 * R0 ** 2))
            elif int(mode / 10) == 8:
                self['PRES'] = gEQDSK['PRES'] / (B0 ** 2) * constants.mu_0
            else:
                raise OMFITexception('Cannot define pressure for MODE %d' % mode)

            # current/q
            if mod(mode, 10) == 1:
                self['FFPRIM'] = gEQDSK['FFPRIM'] / np.abs(B0)
            elif mod(mode, 10) == 2:
                self['JTOR'] = (
                    gEQDSK['fluxSurfaces']['avg']['Jt/R'] / gEQDSK['fluxSurfaces']['avg']['1/R'] / np.abs(B0 / (R0 * constants.mu_0))
                )
            elif mod(mode, 10) == 3:
                raise OMFITexception('%s cannot be loaded from gEQDSK yet' % self.names[mode][2])
            elif mod(mode, 10) == 4:
                raise OMFITexception('%s cannot be loaded from gEQDSK yet' % self.names[mode][2])
            elif mod(mode, 10) == 5:
                self['Q'] = gEQDSK['QPSI']
            else:
                raise OMFITexception('Cannot define current or q for MODE %d' % mode)

        elif version == 'mars':
            self['PSI'] = gEQDSK['AuxQuantities']['RHOp']
            self['PPRIME'] = gEQDSK['PPRIME'] / np.abs(B0 / (constants.mu_0 * R0 ** 2))
            if mode == 1:
                self['FFPRIM'] = gEQDSK['FFPRIM'] / np.abs(B0)
            elif mode == 2:
                self['JTOR'] = (
                    gEQDSK['fluxSurfaces']['avg']['Jt/R'] / gEQDSK['fluxSurfaces']['avg']['1/R'] / np.abs(B0 / (R0 * constants.mu_0))
                )
            elif mode == 3:
                raise OMFITexception('%s cannot be loaded from gEQDSK yet' % self.names[mode][2])
            else:
                raise OMFITexception('MODE %s unknown or not supported' % mode)

        self['MODE'] = mode
        self['NOTES'] = ''
        self.version = version
        return self

    def plot(self, bounds=None, **kw):
        """

        :param bounds:
        :param kw:
        :return:
        """
        from matplotlib import pyplot

        if bounds is None:
            bounds = self['BOUNDARY']

        kw0 = copy.copy(kw)
        if 'lw' in kw:
            kw0['lw'] = kw0['lw'] + 1
        elif 'linewidth' in kw:
            kw0['linewidth'] = kw0['linewidth'] + 1
        else:
            kw0['lw'] = 2
        kw0['color'] = 'k'

        if self.version == 'standard':
            X = self[self.rhotypes[self.nrhotype]]
            Xlabel = '$\\rho$'
        elif self.version == 'mars':
            X = self['PSI']
            Xlabel = '$\\sqrt{\\psi}$'

        ax = pyplot.subplot(2, 2, 2)
        quantity = self.names[self['MODE']][1]
        ax.plot(X, self[quantity], **kw)
        ax.set_title(quantity)
        color = ax.lines[-1].get_color()
        kw['color'] = color

        ax = pyplot.subplot(2, 2, 4)
        quantity = self.names[self['MODE']][2]
        ax.plot(X, self[quantity], **kw)
        ax.set_title(quantity)
        ax.set_xlabel(Xlabel)

        ax = pyplot.subplot(1, 2, 1)
        for bound in self['BOUNDARY']:
            if bound == 'PLASMA':
                ax.plot(self['BOUNDARY'][bound]['R'], self['BOUNDARY'][bound]['Z'], **kw)
            else:
                ax.plot(self['BOUNDARY'][bound]['R'], self['BOUNDARY'][bound]['Z'], **kw0)
        ax.set_aspect('equal')
        ax.set_frame_on(False)


class OMFITcheaseLog(SortedDict, OMFITascii):
    r"""
    OMFIT class used to parse the CHEASE log FILES for the following parameters:
    betaN, NW, CURRT, Q_EDGE, Q_ZERO, R0EXP, B0EXP, Q_MIN, S_Q_MIN, Q_95

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """
        Load CHEASE log file data
        """
        # Array with string pattern, variable name and position of the number to store
        mystring = [
            ('CSV=', 'NW', -1),
            ('GEXP', 'BetaN', -1),
            ('TOTAL CURRENT -->', 'CURRT', 0),
            ('Q_EDGE', 'Q_EDGE', 0),
            ('Q_ZERO', 'Q_ZERO', 0),
            ('R0 [M]', 'R0EXP', 0),
            ('B0 [T]', 'B0EXP', 0),
            ('MINIMUM Q VALUE', 'Q_MIN', -1),
            ('S VALUE OF QMIN', 'S_Q_MIN', -1),
            ('Q AT 95%', 'Q_95', -1),
            ('RESIDU', 'RESIDUAL', 2),
        ]

        with open(self.filename, 'r') as f:
            for line in f.readlines():
                for word, name, pos in mystring:
                    str_found = line.find(word)
                    if (word == 'CSV=') and (name not in self):
                        self[name] = []
                    if str_found != -1:
                        if word == 'CSV=':
                            try:
                                self[name].append(ast.literal_eval(line.split()[pos]))
                            except SyntaxError:
                                tmp = re.findall(r'(\w+=)(\d+)', line.split()[pos])[0]
                                self[name].append(ast.literal_eval(tmp[-1]))
                        elif (word != 'RESIDU') or ('EPSLON' in line.split()):
                            self[name] = ast.literal_eval(line.split()[pos])
        return self

    def read_VacuumMesh(self, npsi):
        """
        Read vacuum mesh from CHEASE log file
        :param npsi: number of radial intervals (=NPSI from input namelist)
        """
        self['VACUUM MESH'] = {}
        NW = []
        rw = []
        mystring = 'VACUUM MESH CSV ='
        with open(self.filename, 'r') as f:
            data = f.readlines()
            for line_no, line in enumerate(data):
                if line.find(mystring) != -1:
                    break
            for ii in range(npsi + 1):
                NW.append(int(data[line_no + ii + 1].split()[0]))
                rw.append(float(data[line_no + ii + 1].split()[1]))
        self['VACUUM MESH']['NW'] = np.asarray(NW)
        self['VACUUM MESH']['rw'] = np.asarray(rw)
        return self


############################################
if '__main__' == __name__:
    test_classes_main_header()

    tmp1 = OMFITchease(OMFITsrc + '/../samples/EXPEQ.OUT')

    tmp1.plot()
    tmp1.EQsmooth(10)
    tmp1.plot(bounds=['PLASMA'])

    from matplotlib import pyplot

    pyplot.show()

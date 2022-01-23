# file processed by 2to3
from __future__ import print_function, absolute_import
from builtins import map, filter, range

try:
    # framework is running
    from .startup_choice import *
except (ValueError, SystemError):  # catch error in Python2.x
    # class is imported by itself
    from startup_choice import *
except ImportError as _excp:  # catch error in Python3.x
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
from omfit_classes.fluxSurface import fluxSurfaces, miller_derived
from omfit_classes.utils_math import deriv, calcz, integz, interp1e, atomic_element
from omfit_classes.utils_fusion import alpha_heating, fusion_power
from omfit_classes import namelist

# Explicit imports
from omfit_classes.gapy import Gapy

import numpy as np
import omas
from scipy.interpolate import interp1d
from scipy import integrate, constants

__all__ = ['OMFITgacode', 'OMFITinputprofiles', 'OMFITinputgacode']

# OMAS source mapper used
# i_vol, d_dvol indicate if volume integrated or density source
# IMAS identifier.index: see core_sources.source[:].identifier at https://gafusion.github.io/omas/schema/schema_core%20sources.html
# NOTE: the first identifier.index is what is used when generating ODSs
# NOTE: here a identifier.index==-1 means `catch all` when reading from ODSs
# NOTE: pow_ie, q_ie has an extra factor of 2 in normalization to avoid double counting ion and electron source
omas_source_mapper = {
    # ============================================================
    # volume integrated source densities
    # ============================================================
    'pow_e_fus': ['i_vol', [6], [(+1, 'electrons.energy', 1e6)]],
    'pow_i_fus': ['i_vol', [6], [(+1, 'total_ion_energy', 1e6)]],
    'pow_e_brem': ['i_vol', [8], [(-1, 'electrons.energy', 1e6)]],
    'pow_e_sync': ['i_vol', [9], [(-1, 'electrons.energy', 1e6)]],
    'pow_e_line': ['i_vol', [10], [(-1, 'electrons.energy', 1e6)]],
    'pow_ei': ['i_vol', [11], [(-1, 'electrons.energy', 2e6), (+1, 'total_ion_energy', 2e6)]],
    'pow_e_aux': ['i_vol', [100, -1], [(+1, 'electrons.energy', 1e6)]],
    'pow_i_aux': ['i_vol', [100, -1], [(+1, 'total_ion_energy', 1e6)]],
    'flow_wall': ['i_vol', [108, -1], [(+1, 'electrons.particles', 0.624e22)]],
    'flow_beam': ['i_vol', [2], [(+1, 'electrons.particles', 0.624e22)]],
    'flow_mom': ['i_vol', [2, -1], [(+1, 'momentum_tor', 1.0)]],
    # ============================================================
    # source densities
    # ============================================================
    'qohme': ['d_dvol', [7], [(+1, 'electrons.energy', 1e6)]],
    'qbeame': ['d_dvol', [2], [(+1, 'electrons.energy', 1e6)]],
    'qbeami': ['d_dvol', [2], [(+1, 'total_ion_energy', 1e6)]],
    'qrfe': ['d_dvol', [3, -1], [(+1, 'electrons.energy', 1e6)]],
    'qrfi': ['d_dvol', [5, -1], [(+1, 'total_ion_energy', 1e6)]],
    'qfuse': ['d_dvol', [6], [(+1, 'electrons.energy', 1e6)]],
    'qfusi': ['d_dvol', [6], [(+1, 'total_ion_energy', 1e6)]],
    'qbrem': ['d_dvol', [8], [(-1, 'electrons.energy', 1e6)]],
    'qsync': ['d_dvol', [9], [(-1, 'electrons.energy', 1e6)]],
    'qline': ['d_dvol', [10], [(-1, 'electrons.energy', 1e6)]],
    'qei': ['d_dvol', [11], [(-1, 'electrons.energy', 2e6), (+1, 'total_ion_energy', 2e6)]],
    'qione': ['d_dvol', [602], [(+1, 'electrons.energy', 1e6)]],
    'qioni': ['d_dvol', [602], [(+1, 'total_ion_energy', 1e6)]],
    'qcxi': ['d_dvol', [305], [(+1, 'total_ion_energy', 1e6)]],
    'qpar_wall': ['d_dvol', [108, -1], [(+1, 'electrons.particles', 0.624e22)]],
    'qpar_beam': ['d_dvol', [2], [(+1, 'electrons.particles', 0.624e22)]],
    'qmom': ['d_dvol', [2, -1], [(+1, 'momentum_tor', 1.0)]],
}

sources_internal_list = [6, 8, 9, 10, 11]

map_d_i = {
    'electrons.energy': 'electrons.power_inside',
    'total_ion_energy': 'total_ion_power_inside',
    'electrons.particles': 'electrons.particles_inside',
    'momentum_tor': 'torque_tor_inside',
}


class OMFITgacode(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with GAcode input.XXX files
    This class supports .gen, .extra, .geo, .profiles file

    .plot() method is available for .profiles files

    :param GACODEtype: force 'profiles' parsing input.profiles format or use `None` for autodetection based on file name

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename=None, GACODEtype=None, **kw):
        kw['GACODEtype'] = GACODEtype
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kw)
        # parse .gen files
        if re.match(r'input\.profiles\.gen.*$', os.path.split(self.filename)[1]) or re.match(r'.*\.gen$', os.path.split(self.filename)[1]):
            pass

        # parse input.profiles.extra files
        elif (
            self.GACODEtype == 'extra'
            or re.match(r'input\.profiles\.extra.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.extra$', os.path.split(self.filename)[1])
        ):
            self.GACODEtype = 'extra'
            self.__class__ = OMFITinputprofiles
            OMFITinputprofiles.init_profiles_names(self)

        # parse input.profiles.geo files
        elif (
            self.GACODEtype == 'geo'
            or re.match(r'input\.profiles\.geo.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.geo', os.path.split(self.filename)[1])
        ):
            self.GACODEtype = 'geo'
            self.__class__ = OMFITinputprofiles
            OMFITinputprofiles.init_profiles_names(self)

        # parse input.profiles files
        elif (
            self.GACODEtype == 'profiles'
            or re.match(r'input\.profiles.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.profiles$', os.path.split(self.filename)[1])
        ):
            self.GACODEtype = 'profiles'
            self.__class__ = OMFITinputprofiles
            OMFITinputprofiles.init_profiles_names(self)

        # parse input.gacode files
        elif (
            self.GACODEtype == 'gacode'
            or re.match(r'input\.gacode.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.gacode$', os.path.split(self.filename)[1])
        ):
            self.__class__ = OMFITinputgacode
            self.GACODEtype = 'gacode'
        self.dynaLoad = True

    @property
    def GACODEtype(self):
        return self.OMFITproperties.get('GACODEtype', None)

    @GACODEtype.setter
    def GACODEtype(self, value):
        self.OMFITproperties['GACODEtype'] = value

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """
        self.clear()

        if self.filename is None or not os.stat(self.filename).st_size:
            return

        with open(self.filename, 'r') as f:
            lines = f.read()
        if len(lines):
            lines = lines.split('\n')
            lines = [line.strip() for line in lines]
            for h, line in enumerate(lines):
                if not len(line):
                    continue
                if line[0] != '#':
                    break
                self['__header_' + format(h, '04d') + '__'] = line

        # parse input.profiles.gen files (allowing for DIR directives of tgyro)
        if re.match(r'input\.profiles\.gen.*$', os.path.split(self.filename)[1]) or re.match(r'.*\.gen$', os.path.split(self.filename)[1]):
            ndir = 0
            for line in lines:
                if not len(line):
                    continue
                if ' ' not in line:
                    ndir = int(line)
                    self['DIR'] = SortedDict()
                    continue
                else:
                    item = line.split()[0]
                    key = line.split()[-1]
                if ndir > 0:
                    if len(line.strip().split()) == 2:
                        self['DIR'][item] = int(key)
                    else:
                        self['DIR'][item] = [int(line.split()[1]), line.split()[2]] + line.split()[3:]
                        if 'X=' not in self['DIR'][item][1]:
                            # uniform distribution of points
                            self['DIR'][item][1] = float(self['DIR'][item][1])
                            if self['DIR'][item][1] == -1:
                                self['DIR'][item][1] = -1
                else:
                    self[key] = namelist.interpreter(item)

        # parse input.profiles.extra files
        elif (
            self.GACODEtype == 'extra'
            or re.match(r'input\.profiles\.extra.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.extra$', os.path.split(self.filename)[1])
        ):
            self.GACODEtype = 'extra'
            self.__class__ = OMFITinputprofiles
            OMFITinputprofiles.init_profiles_names(self)
            OMFITinputprofiles.load(self)

        # parse input.profiles.geo files
        elif (
            self.GACODEtype == 'geo'
            or re.match(r'input\.profiles\.geo.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.geo', os.path.split(self.filename)[1])
        ):
            self.GACODEtype = 'geo'
            self.__class__ = OMFITinputprofiles
            OMFITinputprofiles.init_profiles_names(self)
            OMFITinputprofiles.load(self)

        # parse input.profiles files
        elif (
            self.GACODEtype == 'profiles'
            or re.match(r'input\.profiles.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.profiles$', os.path.split(self.filename)[1])
        ):
            self.GACODEtype = 'profiles'
            self.__class__ = OMFITinputprofiles
            OMFITinputprofiles.init_profiles_names(self)
            OMFITinputprofiles.load(self)

        # parse XXX files
        else:
            # allow parsing of DIR directives as used in TGYRO
            with open(self.filename, 'r') as f:
                DIR = SortedDict()
                while True:
                    line = f.readline()
                    if re.match('DIR .* [0-9]*', line):
                        dp = line.strip().split()
                        if len(dp) == 3:
                            DIR[dp[1]] = int(dp[2])
                        else:
                            DIR[dp[1]] = [int(dp[2])] + dp[3:]
                            DIR[dp[1]] = float(DIR[dp[1]][2])
                    else:
                        break

            tmp = lines
            if len(DIR):
                tmp = lines[len(DIR) :]
                self['DIR'] = DIR

            # normal parsing
            for h, line in enumerate(tmp):
                if not len(line) or '#' in line[0]:
                    self['__header_' + format(h, '04d') + '__'] = line
                else:
                    self[line.split('=')[0].strip()] = namelist.interpreter(line.split('=')[1])

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """
        if (
            self.GACODEtype == 'extra'
            or re.match(r'input\.profiles\.extra.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.extra$', os.path.split(self.filename)[1])
        ):
            self.GACODEtype = 'extra'
            self.__class__ = OMFITinputprofiles
            OMFITinputprofiles.init_profiles_names(self)
            return OMFITinputprofiles.save(self)

        # parse input.profiles.geo files
        elif (
            self.GACODEtype == 'geo'
            or re.match(r'input\.profiles\.geo.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.geo', os.path.split(self.filename)[1])
        ):
            self.GACODEtype = 'geo'
            self.__class__ = OMFITinputprofiles
            OMFITinputprofiles.init_profiles_names(self)
            return OMFITinputprofiles.save(self)

        # parse input.profiles files
        elif (
            self.GACODEtype == 'profiles'
            or re.match(r'input\.profiles.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.profiles$', os.path.split(self.filename)[1])
        ):
            self.GACODEtype = 'profiles'
            self.__class__ = OMFITinputprofiles
            OMFITinputprofiles.init_profiles_names(self)
            return OMFITinputprofiles.save(self)

        # parse input.profiles files
        elif (
            self.GACODEtype == 'gacode'
            or re.match(r'input\.gacode.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.gacode$', os.path.split(self.filename)[1])
        ):
            self.GACODEtype = 'gacode'
            self.__class__ = OMFITinputgacode
            return OMFITinputgacode.save(self)

        # save XXX files
        else:

            header_ptrn = re.compile(r'^__header_.*__$')
            header = []
            for item in list(self.keys()):
                if re.match(header_ptrn, item):
                    header.append(self[item])
            if len(header):
                header.append('')

            with open(self.filename, 'w') as f:
                # save XXX.gen files (allowing for DIR directives of tgyro)
                if re.match(r'input\.profiles\.gen.*$', os.path.split(self.filename)[1]) or re.match(
                    r'.*\.gen$', os.path.split(self.filename)[1]
                ):
                    for key in [k for k in list(self.keys()) if k != 'DIR']:
                        f.write(namelist.encoder(self[key]) + '  ' + str(key) + '\n')
                    # write DIR directives at the end of the file as necessary for tgyro
                    if 'DIR' in self:
                        f.write(str(len(self['DIR'])) + '\n')
                        for key in list(self['DIR'].keys()):
                            f.write(str(key) + '  ' + ' '.join(map(str, tolist(self['DIR'][key]))) + '\n')
                # save XXX files
                else:
                    # write DIR directives at the top of the file as necessary for tgyro
                    if 'DIR' in list(self.keys()):
                        for dir in self['DIR']:
                            if len(tolist(self['DIR'][dir])) > 1 and self['DIR'][dir][1] != -1:
                                try:
                                    self['DIR'][dir][1] = 'X=%f' % float(self['DIR'][dir][1])
                                except ValueError:
                                    pass
                            f.write('DIR ' + dir + ' ' + ' '.join(map(str, tolist(self['DIR'][dir])[:2])) + '\n')

                    # write header
                    for ii, item in enumerate(self.keys()):
                        if not isinstance(self[item], np.ndarray) and not isinstance(self[item], dict):
                            if not re.match(hide_ptrn, item):
                                f.write(item + '=' + namelist.encoder(self[item]) + '\n')
                            else:
                                if self[item] or not ii == len(self) - 1:
                                    f.write(self[item] + '\n')

    @dynaLoad
    def __getattr__(self, attr):
        # backward compatibility with older nomenclature of methods
        # that used `input_profile_` prefix for methods that were
        # meant to work only for `input.profiles` files.
        attr0 = attr
        if 'input_profiles_' in attr:
            attr = re.sub('input_profiles_', '', attr)
            if hasattr(self, attr):
                printw(self.__class__.__name__ + '.%s() is deprecated. Use .%s() instead' % (attr0, attr))
                return getattr(self, attr)
        raise AttributeError('bad attribute `%s`' % attr0)


class _gacode_profiles(object):
    """
    GACODE profiles maniputlation methods
    to be shared between OMFITinputprofiles and OMFITinputgacode classes
    """

    def init_profiles_names(self):
        self.profNames = {}
        self.extraNames = {}

        self.profNames[0] = [
            ['rho', 'rmin', 'rmaj', 'q', 'kappa'],
            ['delta', 'Te', 'ne', 'z_eff', 'omega0'],
            ['flow_mom', 'pow_e', 'pow_i', 'pow_ei', 'zeta'],
            ['flow_beam', 'flow_wall', 'zmag', 'ptot', 'polflux'],
            ['ni_1', 'ni_2', 'ni_3', 'ni_4', 'ni_5'],
            ['Ti_1', 'Ti_2', 'Ti_3', 'Ti_4', 'Ti_5'],
            ['vtor_1', 'vtor_2', 'vtor_3', 'vtor_4', 'vtor_5'],
            ['vpol_1', 'vpol_2', 'vpol_3', 'vpol_4', 'vpol_5'],
            ['pow_e_aux', 'pow_i_aux', 'pow_e_fus', 'pow_i_fus', 'pow_e_sync'],
            ['pow_e_brem', 'pow_e_line', 'NULL', 'NULL', 'NULL'],
        ]

        self.extraNames[0] = [
            'bunit',
            's',
            'drmaj',
            'dzmag',
            'sdelta',
            'skappa',
            'szeta',
            'dlnnedr',
            'dlntedr',
            'dlnnidr_1',
            'dlnnidr_2',
            'dlnnidr_3',
            'dlnnidr_4',
            'dlnnidr_5',
            'dlntidr_1',
            'dlntidr_2',
            'dlntidr_3',
            'dlntidr_4',
            'dlntidr_5',
            'dlnptotdr',
            'drdrho',
            'w0p',
            'vol',
            'volp',
            'cs',
            'rhos',
            'ni_new',
            'dlnnidr_new',
            'grad_r0',
            'ave_grad_r',
            'bp0',
            'bt0',
            'gamma_e',
            'gamma_p',
            'mach',
        ]

        self.profNames[1] = [
            ['rho', 'rmin', 'polflux', 'q', 'omega0'],
            ['rmaj', 'zmag', 'kappa', 'delta', 'zeta'],
            ['ne', 'Te', 'ptot', 'z_eff', 'NULL'],
            ['ni_1', 'ni_2', 'ni_3', 'ni_4', 'ni_5'],
            ['ni_6', 'ni_7', 'ni_8', 'ni_9', 'ni_10'],
            ['Ti_1', 'Ti_2', 'Ti_3', 'Ti_4', 'Ti_5'],
            ['Ti_6', 'Ti_7', 'Ti_8', 'Ti_9', 'Ti_10'],
            ['vtor_1', 'vtor_2', 'vtor_3', 'vtor_4', 'vtor_5'],
            ['vtor_6', 'vtor_7', 'vtor_8', 'vtor_9', 'vtor_10'],
            ['vpol_1', 'vpol_2', 'vpol_3', 'vpol_4', 'vpol_5'],
            ['vpol_6', 'vpol_7', 'vpol_8', 'vpol_9', 'vpol_10'],
            ['flow_beam', 'flow_wall', 'flow_mom', 'NULL', 'NULL'],
            ['pow_e', 'pow_i', 'pow_ei', 'pow_e_aux', 'pow_i_aux'],
            ['pow_e_fus', 'pow_i_fus', 'pow_e_sync', 'pow_e_brem', 'pow_e_line'],
        ]

        self.extraNames[1] = [
            'bunit',
            's',
            'drmaj',
            'dzmag',
            'sdelta',
            'skappa',
            'szeta',
            'dlnnedr',
            'dlntedr',
            'dlnnidr_1',
            'dlnnidr_2',
            'dlnnidr_3',
            'dlnnidr_4',
            'dlnnidr_5',
            'dlnnidr_6',
            'dlnnidr_7',
            'dlnnidr_8',
            'dlnnidr_9',
            'dlnnidr_10',
            'dlntidr_1',
            'dlntidr_2',
            'dlntidr_3',
            'dlntidr_4',
            'dlntidr_5',
            'dlntidr_6',
            'dlntidr_7',
            'dlntidr_8',
            'dlntidr_9',
            'dlntidr_10',
            'dlnptotdr',
            'drdrho',
            'w0p',
            'vol',
            'volp',
            'cs',
            'rhos',
            'ni_new',
            'dlnnidr_new',
            'grad_r0',
            'ave_grad_r',
            'bp0',
            'bt0',
            'gamma_e',
            'gamma_p',
            'mach',
        ]

        self.profNames[2] = [
            ['rho', 'rmin', 'polflux', 'q', 'omega0'],
            ['rmaj', 'zmag', 'kappa', 'delta', 'zeta'],
            ['ne', 'Te', 'ptot', 'z_eff', 'NULL'],
            ['ni_1', 'ni_2', 'ni_3', 'ni_4', 'ni_5'],
            ['ni_6', 'ni_7', 'ni_8', 'ni_9', 'ni_10'],
            ['Ti_1', 'Ti_2', 'Ti_3', 'Ti_4', 'Ti_5'],
            ['Ti_6', 'Ti_7', 'Ti_8', 'Ti_9', 'Ti_10'],
            ['vtor_1', 'vtor_2', 'vtor_3', 'vtor_4', 'vtor_5'],
            ['vtor_6', 'vtor_7', 'vtor_8', 'vtor_9', 'vtor_10'],
            ['vpol_1', 'vpol_2', 'vpol_3', 'vpol_4', 'vpol_5'],
            ['vpol_6', 'vpol_7', 'vpol_8', 'vpol_9', 'vpol_10'],
            ['flow_beam', 'flow_wall', 'flow_mom', 'sbcx', 'sbeame'],
            ['pow_e', 'pow_i', 'pow_ei', 'pow_e_aux', 'pow_i_aux'],
            ['pow_e_fus', 'pow_i_fus', 'pow_e_sync', 'pow_e_brem', 'pow_e_line'],
        ]

        self.extraNames[2] = self.extraNames[1]

        self.profNames[3] = [
            ['rho', 'rmin', 'polflux', 'q', 'omega0'],
            ['rmaj', 'zmag', 'kappa', 'delta', 'zeta'],
            ['ne', 'Te', 'ptot', 'z_eff', 'NULL'],
            ['ni_1', 'ni_2', 'ni_3', 'ni_4', 'ni_5'],
            ['ni_6', 'ni_7', 'ni_8', 'ni_9', 'ni_10'],
            ['Ti_1', 'Ti_2', 'Ti_3', 'Ti_4', 'Ti_5'],
            ['Ti_6', 'Ti_7', 'Ti_8', 'Ti_9', 'Ti_10'],
            ['vtor_1', 'vtor_2', 'vtor_3', 'vtor_4', 'vtor_5'],
            ['vtor_6', 'vtor_7', 'vtor_8', 'vtor_9', 'vtor_10'],
            ['vpol_1', 'vpol_2', 'vpol_3', 'vpol_4', 'vpol_5'],
            ['vpol_6', 'vpol_7', 'vpol_8', 'vpol_9', 'vpol_10'],
            ['flow_beam', 'flow_wall', 'flow_mom', 'NULL', 'NULL'],
            ['pow_e', 'pow_i', 'pow_ei', 'pow_e_aux', 'pow_i_aux'],
            ['pow_e_fus', 'pow_i_fus', 'pow_e_sync', 'pow_e_brem', 'pow_e_line'],
            ['sbeame', 'sbcx', 'sscxl', 'NULL', 'NULL'],
        ]

        self.extraNames[3] = [
            'bunit',
            's',
            'drmaj',
            'dzmag',
            'sdelta',
            'skappa',
            'szeta',
            'dlnnedr',
            'dlntedr',
            'dlnnidr_1',
            'dlnnidr_2',
            'dlnnidr_3',
            'dlnnidr_4',
            'dlnnidr_5',
            'dlnnidr_6',
            'dlnnidr_7',
            'dlnnidr_8',
            'dlnnidr_9',
            'dlnnidr_10',
            'dlntidr_1',
            'dlntidr_2',
            'dlntidr_3',
            'dlntidr_4',
            'dlntidr_5',
            'dlntidr_6',
            'dlntidr_7',
            'dlntidr_8',
            'dlntidr_9',
            'dlntidr_10',
            'dlnptotdr',
            'drdrho',
            'w0p',
            'vol',
            'volp',
            'cs',
            'rhos',
            'ni_new',
            'dlnnidr_new',
            'grad_r0',
            'ave_grad_r',
            'bp0',
            'bt0',
            'gamma_e',
            'gamma_p',
            'mach',
            'ip',
            'sdlnnedr',
            'sdlntedr',
            'sdlnnidr_1',
            'sdlnnidr_2',
            'sdlnnidr_3',
            'sdlnnidr_4',
            'sdlnnidr_5',
            'sdlnnidr_6',
            'sdlnnidr_7',
            'sdlnnidr_8',
            'sdlnnidr_9',
            'sdlnnidr_10',
            'sdlntidr_1',
            'sdlntidr_2',
            'sdlntidr_3',
            'sdlntidr_4',
            'sdlntidr_5',
            'sdlntidr_6',
            'sdlntidr_7',
            'sdlntidr_8',
            'sdlntidr_9',
            'sdlntidr_10',
            'nuee',
        ]

        self.latest_version = self.version = 3

        # fmt: off
        self.profNamesPretty = \
             {'NULL'       : (''                          ,''             ,'[null]'),
              'rho'        : ('{\\hat \\rho}'             ,''             ,'rho(-)'),
              'rmin'       : ('a'                         ,'m'            ,'rmin(m)'),
              'rmaj'       : ('R_0'                       ,'m'            ,'rmaj(m)'),
              'q'          : ('q'                         ,''             ,'q(-)'),
              'kappa'      : ('\\kappa'                   ,''             ,'kappa(-)'),
              'delta'      : ('\\delta'                   ,''             ,'delta(-)'),
              'Te'         : ('T_e'                       ,'keV'          ,'Te(keV)'),
              'ne'         : ('n_e'                       ,'10^{19}/m^3'  ,'ne(10^19/m^3)'),
              'z_eff'      : ('Z_\\mathrm{eff}'           ,''             ,'zeff(-)'),
              'omega0'     : ('\\omega_0'                 ,'rad/s'        ,'omega0(rad/s)'),
              'flow_mom'   : ('S_\\mathrm{\\omega}'       ,'Nm'           ,'flow_mom(Nm)'),
              'sbcx'       : ('sbcx'                      ,'1/m^3/s'      ,'sbcx(/m^3/s)'),
              'sbeame'     : ('sbeame'                    ,'1/m^3/s'      ,'sbeame(/m^3/s)'),
              'sscxl'      : ('sscxl'                     ,'1/m^3/s'      ,'sscxl(/m^3/s)'),
              'pow_e'      : ('P_e'                       ,'MW'           ,'pow_e(MW)'),
              'pow_i'      : ('P_i'                       ,'MW'           ,'pow_i(MW)'),
              'pow_ei'     : ('P_{ei}'                    ,'MW'           ,'pow_ei(MW)'),
              'zeta'       : ('\\zeta'                    ,''             ,'zeta(-)'),
              'flow_beam'  : ('S_\\mathrm{n,beam}'        ,'kW/eV'        ,'flow_beam(kW/eV)'),
              'flow_wall'  : ('S_\\mathrm{n,wall}'        ,'kW/eV'        ,'flow_wall(kW/eV)'),
              'zmag'       : ('Z_0'                       ,'m'            ,'zmag(m)'),
              'ptot'       : ('p_\\mathrm{total}'         ,'Pa'           ,'ptot(Pa)'),
              'polflux'    : ('\\psi'                     ,'Wb/rad'       ,'polflux(Wb/rad)'),
              'pow_e_aux'  : ('P_{e,\\rm aux}'            ,'MW'           ,'pow_e_aux(MW)'),
              'pow_i_aux'  : ('P_{i,\\rm aux}'            ,'MW'           ,'pow_i_aux(MW)'),
              'pow_e_fus'  : ('P_{e,\\rm fus}'            ,'MW'           ,'pow_e_fus(MW)'),
              'pow_i_fus'  : ('P_{i,\\rm fus}'            ,'MW'           ,'pow_i_fus(MW)'),
              'pow_e_sync' : ('P_{e,\\rm sync}'           ,'MW'           ,'pow_e_sync(MW)'),
              'pow_e_brem' : ('P_{e,\\rm brem}'           ,'MW'           ,'pow_e_brem(MW)'),
              'pow_e_line' : ('P_{e,\\rm line}'           ,'MW'           ,'pow_e_line(MW)'),
              # extra (needs units)
              'bunit'      : ('B_\\mathrm{unit}'          ,'T'            ,''),
              's'          : ('s'                         ,''             ,''),
              'drmaj'      : ('dR_0/dr'                   ,''             ,''),
              'dzmag'      : ('dZ_0/dr'                   ,''             ,''),
              'sdelta'     : ('s_\\delta'                 ,''             ,''),
              'skappa'     : ('s_\\kappa'                 ,''             ,''),
              'szeta'      : ('s_\\zeta'                  ,''             ,''),
              'dlnnedr'    : ('-dln(n_e)/dr'              ,'1/m'          ,''),
              'dlntedr'    : ('-dln(T_e)/dr'              ,'1/m'          ,''),
              'dlnptotdr'  : ('-dln(p_\\mathrm{tot})/dr'  ,'1/m'          ,''),
              'drdrho'     : ('dr/d\\rho'                 ,''             ,''),
              'w0p'        : ('d(\\omega_0)/dr'           ,'rad/s/m'        ,''),
              'vol'        : ('V'                         ,'m^3'          ,''),
              'volp'       : ('dV/dr'                     ,'m^2'          ,''),
              'cs'         : ('c_\\mathrm{s}'             ,'m/s'          ,''),
              'rhos'       : ('\\rho_\\mathrm{s,unit}'     ,'m'            ,''),
              'ni_new'     : ('n_i'                       ,'10^{19}/m^3'  ,''),  # [Corrected for quasin.]
              'dlnnidr_new': ('-dln(n_i)/dr'              ,'1/m'          ,''),  # [Corrected for quasin.]
              'grad_r0'    : ('|\\nabla_r|_{\\theta=0}'   ,''             ,''),
              'ave_grad_r' : ('<|\\nabla_r|>'             ,''             ,''),
              'bp0'        : ('B_p|_{\\theta=0}'          ,'T'            ,''),
              'bt0'        : ('B_t|_{\\theta=0}'          ,'T'            ,''),
              'gamma_e'    : ('r/q d(\\omega_0)/dr'       ,'rad/s'          ,''),
              'gamma_p'    : ('R_0 d(\\omega_0)/dr'       ,'rad/s'          ,''),
              'mach'       : ('R_0 \\omega_0/c_s'         ,''             ,''),
              #jbs
              'expro_rho'  : ('\\rho'                     ,''             ,''),
              'jbs_err'    : ('j_\\mathrm{bs,err}'        ,'MA/m^2'       ,''),
              'jbs_neo'    : ('j_\\mathrm{bs,neo}'        ,'MA/m^2'       ,''),
              'jbs_sauter' : ('j_\\mathrm{bs,sauter}'     ,'MA/m^2'       ,''),
              'jbs_nclass' : ('j_\\mathrm{bs,nclass}'     ,'MA/m^2'       ,''),
              'jbs_koh'    : ('j_\\mathrm{bs,koh}'        ,'MA/m^2'       ,''),
              #expro
              'fpol'       : ('F'                         ,'T*m'          ,''),
              'jbs'        : ('j_\\mathrm{bs}'            ,'MA/m^2'       ,''),
              'jbstor'     : ('j_\\mathrm{bs,tor}'        ,'MA/m^2'       ,''),
              'jnb'        : ('j_\\mathrm{nb}'            ,'MA/m^2'       ,''),
              'johm'       : ('j_\\mathrm{oh}'            ,'MA/m^2'       ,''),
              'jrf'        : ('j_\\mathrm{rf}'            ,'MA/m^2'       ,''),
              'nuee'       : ('\\nu_{ee}'                 ,'1/s'          ,''),
              'qbeame'     : ('Q_{e,nb}'                  ,'W/m^3'        ,''),
              'qbeami'     : ('Q_{i,nb}'                  ,'W/m^3'        ,''),
              'qbrem'      : ('Q_{brem}'                  ,'W/m^3'        ,''),
              'qcxi'       : ('Q_{cxi}'                   ,'W/m^3'        ,''),
              'qei'        : ('Q_{ei}'                    ,'W/m^3'        ,''),
              'qfuse'      : ('Q_{e,fus}'                 ,'W/m^3'        ,''),
              'qfusi'      : ('Q_{i,fus}'                 ,'W/m^3'        ,''),
              'qione'      : ('Q_{ione}'                  ,'W/m^3'        ,''),
              'qioni'      : ('Q_{ioni}'                  ,'W/m^3'        ,''),
              'qline'      : ('Q_{line}'                  ,'W/m^3'        ,''),
              'qmom'       : ('Q_{mom}'                   ,'W/m^3'        ,''),
              'qohme'      : ('Q_{e,oh}'                  ,'W/m^3'        ,''),
              'qpar_beam'  : ('Q_{beam,par}'              ,'W/m^3'        ,''),
              'qpar_wall'  : ('Q_{wall,par}'              ,'W/m^3'        ,''),
              'qrfe'       : ('Q_{e,rf}'                  ,'W/m^3'        ,''),
              'qrfi'       : ('Q_{i,rf}'                  ,'W/m^3'        ,''),
              'qsync'      : ('Q_{sync}'                  ,'W/m^3'        ,''),
              'sigmapar'   : ('\\sigma_{\\parallel}'      ,'S'            ,''),
              'surf'       : ('A'                         ,'m^2'          ,''),
        }

        for _k in range(0, 11):
            self.profNamesPretty['ni_%d'%_k]              = ('n_{i,%d}'%_k          ,'10^{19}/m^3' ,'ni_%d(10^19/m^3)'%_k)
            self.profNamesPretty['Ti_%d'%_k]              = ('T_{i,%d}'%_k          ,'keV'         ,'Ti_%d(keV)'%_k)
            self.profNamesPretty['vtor_%d'%_k]            = ('v_{\\varphi,%d}'%_k   ,'m/s'         ,'vtor_%d(m/s)'%_k)
            self.profNamesPretty['vpol_%d'%_k]            = ('v_{\\theta,%d}'%_k    ,'m/s'         ,'vpol_%d(m/s)'%_k)
            self.profNamesPretty['dlntidr_%d'%_k]         = ('-dln(T_{i,%d})/dr'%_k ,'1/m'         ,'')
            self.profNamesPretty['dlnnidr_%d'%_k]         = ('-dln(n_{i,%d})/dr'%_k ,'1/m'         ,'')
            for g in ['cos','scos','sin','ssin']:
                self.profNamesPretty['shape_%s%d'%(g,_k)] = ('%s%d'%(g,_k)           ,''           ,'')

        # fmt: on

    def plot(self, what=None, only2D=False, axs={}, pretty_names=True, **kw):
        r"""
        Plot all profiles entries as function of rho

        :param what: list of quantities to plot. All quantities are plotted if set to None.

        :param only2D: plot 2D flux surfaces based on miller geometry coefficients

        :param axs: dictionary with axes for each of the quantities to be plotted

        :param pretty_names: use pretty names for subplots

        :param \**kw: extra arguments passed to plot functions

        :return: dictionary with all the plot axes that have been used
        """
        inputaxs = axs
        axs = {}

        if self.GACODEtype == 'geo':
            return self.plot_geo(**kw)

        import matplotlib
        from matplotlib import pyplot

        if only2D:
            ax = kw.pop('ax', None)
            if ax is None:
                ax = pyplot.gca()
            r, z = self.rz_geometry()
            ax.plot(r[:, 0], z[:, 0], **kw)
            kw['color'] = ax.lines[-1].get_color()
            ax.plot(r[:, 1:], z[:, 1:], **kw)
            ax.set_aspect('equal')
            return ax

        if what is None:
            what = sorted(
                [
                    item
                    for item in list(self.keys())
                    if isinstance(self[item], np.ndarray) and item != 'rho' and not np.all(self[item] == 0.0)
                ],
                key=lambda x: x.lower(),
            )
        else:
            what = tolist(what, None)
        nplot = len(what)
        cplot = max([np.floor(np.sqrt(nplot)), 1.0])
        rplot = np.ceil(nplot / cplot)
        pyplot.gcf().subplots_adjust(wspace=0.35, hspace=0.0)
        interactive = matplotlib.is_interactive()
        try:
            if interactive:
                pyplot.ioff()
            for k, item in enumerate(what):
                if len(inputaxs):
                    if item in inputaxs:
                        ax = inputaxs[item]
                    else:
                        continue
                else:
                    if k == 0:
                        ax1 = ax = pyplot.subplot(rplot, cplot, k + 1)
                    else:
                        ax = pyplot.subplot(rplot, cplot, k + 1, sharex=ax1)
                axs[item] = ax
                r = np.floor(k * 1.0 / cplot)
                c = k - r * cplot
                ax.ticklabel_format(style='sci', scilimits=(-3, 3))
                if 'rho' in self:
                    x = self['rho']
                    ax.set_xlabel('$\\rho$')
                elif 'drdrho' in self:
                    x = integrate.cumtrapz(1.0 / self['drdrho'], initial=0)
                    x = x / max(x)
                    ax.set_xlabel('$\\rho$')
                else:
                    x = np.arange(len(self[item]))
                    ax.set_xlabel('Array element')

                ax.plot(x, self[item], **kw)
                if 0 == self[item].min() == self[item].max():
                    ax.set_yticks([0])

                text = item
                if pretty_names:
                    text = '$' + self.profNamesPretty[item][0] + '~[' + self.profNamesPretty[item][1] + ']$'
                ax.text(0.5, 0.9, text, horizontalalignment='center', verticalalignment='top', size='medium', transform=ax.transAxes)

                if k >= len(what) - cplot:
                    pyplot.setp(ax.get_xticklabels(), visible=True)
            pyplot.xlim(min(x), max(x))
        finally:
            if interactive:
                pyplot.ion()
                pyplot.draw()

        return axs

    def plot_geo(self, **kw):
        """
        Plot equilibrum based on fourier representation
        """
        import matplotlib
        from matplotlib import pyplot

        kw.pop('only2D', None)

        ax = kw.pop('ax', None)
        if ax is None:
            ax = pyplot.gca()
        r, z = self.rz_geometry()
        ax.plot(r[:, 0], z[:, 0], **kw)
        kw['color'] = ax.lines[-1].get_color()
        ax.plot(r[:, 1:], z[:, 1:], **kw)
        ax.set_aspect('equal')
        ax.set_xlabel('R')
        ax.set_ylabel('Z')
        return ax

    def calc_ptot(self, in_place=False):
        """
        Calculates ptot from species densities and temperatures

        :param in_place: update z_eff array

        :return: calculated ptot array
        """
        ptot = []
        for item in ['e'] + ['i_%d' % i for i in range(1, 11)]:
            if 'n' + item in self and 'T' + item in self:
                ptot.append(self['n' + item] * self['T' + item] * 1e3 * constants.e * 1e19)
        ptot = np.sum(ptot, 0)
        if in_place:
            self['ptot'] = ptot
        return ptot

    def calc_zeff(self, use_ne=True, in_place=False):
        """
        Calculates z_eff from species densities and charges
        Two ways of calculating z_eff are identical when plasma is quasineutral but different otherwise

            * z_eff=np.sum(ni*Zi**2)/ne

            * z_eff=np.sum(ni*Zi**2)/np.sum(ni*Zi)

        :param use_ne: use z_eff=np.sum(ni*Zi**2)/ne

        :param in_place: update z_eff array

        :return: z_eff array
        """
        num = []
        den = []
        for k in self['IONS']:
            num.append(self['ni_%d' % k] * self['IONS'][k][1] ** 2)
            den.append(self['ni_%d' % k] * self['IONS'][k][1])
        if use_ne:
            z_eff = np.sum(num, 0) / self['ne']
        else:
            z_eff = np.sum(num, 0) / np.sum(den, 0)
        if in_place:
            self['z_eff'] = z_eff
        return z_eff

    def calc_pow_aux(self, in_place=False):
        """
        Calculates electron and ion auxiliary sources as the difference between total sources and the other known individual components

        :param in_place: Update pow_e_aux and pow_i_aux arrays

        :return: pow_e_aux, pow_i_aux arrays
        """
        pow_e_aux = self['pow_e'] - (-self['pow_ei'] + self['pow_e_fus'] - self['pow_e_sync'] - self['pow_e_brem'] - self['pow_e_line'])
        pow_i_aux = self['pow_i'] - (self['pow_ei'] + self['pow_i_fus'])
        if in_place:
            self['pow_e_aux'] = pow_e_aux
            self['pow_i_aux'] = pow_i_aux
        return pow_e_aux, pow_i_aux

    def calc_pow(self, in_place=False):
        """
        Calculates electron and ion sources as the difference between total sources and the other known individual components

        :param in_place: Update pow_e_aux and pow_i_aux arrays

        :return: pow_e_aux, pow_i_aux arrays
        """
        pow_e = self['pow_e_aux'] - self['pow_ei'] + self['pow_e_fus'] - self['pow_e_sync'] - self['pow_e_brem'] - self['pow_e_line']
        pow_i = self['pow_i_aux'] + self['pow_ei'] + self['pow_i_fus']
        if in_place:
            self['pow_e'] = pow_e
            self['pow_i'] = pow_i
        return pow_e, pow_i

    def checks(self):
        """
        runs a series of consistency checks on gacode profiles file
        """
        problems = []
        for item in ['pow_e_line', 'pow_e_sync', 'pow_e_brem']:
            if (self[item] < 0).any():
                problems.append(item + ' is negative (should always be positive)')
        for item in self:
            if isinstance(self[item], np.ndarray) and np.any(np.isnan(self[item])):
                problems.append(item + ' has NaNs')
        if np.any(np.abs(self['zeta']) > np.sqrt(2) / 2.0):
            problems.append('abs(zeta) is not between 0 and 0.7')
        if len(problems):
            printw('Possible problems found with gacode profiles file:')
            printw('\n'.join(map(lambda x: ' * ' + x, problems)))
        self['N_ION'] = len(self['IONS'])

    def ion_names(self, fast_last=False):
        """
        returns the ion names in gacode profiles file with the format `['D','C','D[fast]']` for example

        :param fast_last: return fast ions last

        :return: list with strings with ion names
        """
        ion_names = [self['IONS'][k][0] for k in self['IONS']]
        numd_ion_names = []
        for k in list(self['IONS'].keys()):
            ion = self['IONS'][k][0]
            if self['IONS'][k][3] == 'fast':
                ion += '[fast]'
            count = 1
            for x in numd_ion_names:
                if ion in x:
                    count += 1
            if count > 1:
                ion += '#' + str(count)
            numd_ion_names.append(ion)

        # additional sorting thermal/fast if requested
        if fast_last:
            fast_last = []
            for k in numd_ion_names:
                if '[fast]' not in k:
                    fast_last.append(k)
            for k in numd_ion_names:
                if '[fast]' in k:
                    fast_last.append(k)
            return fast_last
        else:
            return numd_ion_names

    def reorder_ions(self, reordered_ions, verbose=True):
        """
        Reorder ions in gacode profiles file by sorting their ['ni', 'Ti', 'vtor', 'vpol'] entries
            NOTE: This method operates in place

        :param reordered_ions: list of ion names or numbers (as per .ion_names() method)
            If reordered_ions is None, then nothing is done.

        :param verbose: print when ions are reordered

        :return: self (modified)
        """
        if reordered_ions is None:
            return self

        numd_ion_names = self.ion_names()

        # convert integers to ion names
        reordered_ion_names = copy.deepcopy(reordered_ions)
        for k, item in enumerate(reordered_ions):
            if isinstance(reordered_ions[k], int):
                reordered_ion_names[k] = numd_ion_names[item - 1]

        # check that ions are only reordered
        if len(self['IONS']) != len(reordered_ion_names):
            raise OMFITexception('You can only reorder the ions. Valid ions name are: %s' % numd_ion_names)
        if set(numd_ion_names) != set(reordered_ion_names):
            raise OMFITexception('Valid ions name for reordering are: %s' % numd_ion_names)

        if tuple(reordered_ion_names) != tuple(numd_ion_names):

            # update 'ni', 'Ti', 'vtor', 'vpol' quantities
            new = {}
            ion_quants = ['ni', 'Ti', 'vtor', 'vpol']
            for i, ion in enumerate(reordered_ion_names):
                for k in ion_quants:
                    new[k + '_%d' % (i + 1)] = self[k + '_%d' % (numd_ion_names.index(ion) + 1)]
            self.update(new)

            # update IONS dictionary
            new = {}
            for i, ion in enumerate(reordered_ion_names):
                new[i + 1] = self['IONS'][numd_ion_names.index(ion) + 1]
            self['IONS'].update(new)

            if verbose:
                printi('Reodered gacode profiles ions to: %s' % reordered_ion_names)

        return self

    def add_ion(
        self,
        ion_num,
        ion,
        Z,
        A,
        ni=None,
        concentration=0,
        thermal=True,
        aoLn=None,
        isl_mul=None,
        isl_add=None,
        aoLn_from=None,
        z_eff=None,
        remove_density_from_ion=1,
        temperature_and_velocities_from_ion=1,
        verbose=True,
    ):
        """
        Add ion to a gacode profiles file. When an ion is added, its 'ni', 'Ti', 'vtor', 'vpol' quantities are set.
        The ion density profile of the added ion can be set in different ways:

        1. as user defined density profile
        2. as user defined normalized inverse scale lenght + concentration
        3. copy density profile from other ion and modify it by isl_mul and isl_add
        4. target Zeff

        NOTE: this method operates in place

        :param ion_num: insert new ion as this number

        :param ion: ion name

        :param Z: ion charge

        :param A: ion mass

        :param ni: ion density profile

        :param concentration: ion concentration nX/ne

        :param thermal: thermal or fast ion

        :param aoLn: (optional) normalized inverse scale length of the ion density profile
            Necessary for impurity transport studies when you need a finite gradient for computing D, V.
            If set, then the profile has the average concentration set at the boundary rho=1

        :param isl_mul: (optional) multiply the inverse scale length of the ion density profile as specified by aoLn_from

        :param isl_add: (optional) add to the inverse scale length of the ion density profile as specified by aoLn_from

        :param aoLn_from: (optional) specify a species to take the density profile from as starting point for the added profile (as a string or as an index)

        :param z_eff: (optional) add ion to reach a certain z_eff

        :param remove_density_from_ion: ion name or number from which to steal density (numbering before adding the new ion)

        :param temperature_and_velocities_from_ion: ion name or number from which the temperature and velocities are copied from (numbering before adding the new ion)

        :return: self (modified)
        """

        numd_ion_names = self.ion_names()
        if isinstance(remove_density_from_ion, int):
            remove_density_from_ion = numd_ion_names[remove_density_from_ion - 1]
        remove_density_from_ion_num = numd_ion_names.index(remove_density_from_ion) + 1

        if isinstance(temperature_and_velocities_from_ion, int):
            temperature_and_velocities_from_ion = numd_ion_names[temperature_and_velocities_from_ion - 1]
        temperature_and_velocities_from_ion_num = numd_ion_names.index(temperature_and_velocities_from_ion) + 1

        if verbose:
            if isl_mul is not None and isl_add is not None and aoLn_from is not None:
                if isinstance(aoLn_from, int):
                    aoLn_from = numd_ion_names[aoLn_from - 1]
                printi('Adding ion based on %s' % aoLn_from)
            else:
                printi('Adding ion %s' % ion)
            printi('Copying ion temperature from ni_%d %s' % (temperature_and_velocities_from_ion_num, temperature_and_velocities_from_ion))
            printi('Removing ion charge density from ni_%d %s' % (remove_density_from_ion_num, remove_density_from_ion))

        # ion density directly provided by the user
        if ni is not None:
            pass

        # calculate ion density to match given Z_eff
        elif z_eff is not None:
            z_eff_start = self.calc_zeff()
            ni = self['ne'] * (z_eff - z_eff_start) / float(Z) ** 2
            if np.any(ni < 0):
                raise ValueError('requested z_eff leads to negative ion density')

        # ion density as concentration of electron density
        elif aoLn is None and aoLn_from is None:
            ni = self['ne'] * concentration

        # generate ion density profile by
        else:
            # modifying the inverse scale length of an existing profile of species aoLn by adding/multiplying
            if isl_add is not None and isl_mul is not None and aoLn_from is not None:
                if isinstance(aoLn_from, int):
                    aoLn_from = numd_ion_names[aoLn_from - 1]
                aoLn_from_num = numd_ion_names.index(aoLn_from) + 1
                rmin = self['rmin']
                n = self['ni_%d' % aoLn_from_num]

                # Calculate the inverse scale length and then modify it by multiplying or adding a factor,
                isl = calcz(rmin, n) * isl_mul + isl_add

                # Integrate the inverse scale length profile to generate a new density profile
                # NOTE: start integration from the core outward
                ni = concentration * integz(rmin, isl, rmin[0], n[0], rmin)

            # user given inverse scale length aoLn
            else:
                rmin = self['rmin']
                isl = np.zeros_like(rmin) + aoLn * rmin[-1]
                isl[0] = 0.0
                ni = integz(rmin, isl, rmin[0], 1, rmin)
                ni -= ni[-1] - 1.0
                ni *= np.mean(self['ne']) * concentration

        Z_del = self['IONS'][remove_density_from_ion_num][1]
        self['ni_%d' % remove_density_from_ion_num] -= (Z / float(Z_del)) * ni

        # Check for negative density values
        if np.min(self['ni_%d' % remove_density_from_ion_num]) < 0:
            printw(
                'WARNING: species addition resulted in negative density values for %s! Negative values were set to zero.'
                % 'ni_%d'
                % remove_density_from_ion_num
            )
            self['ni_%d' % remove_density_from_ion_num][self['ni_%d' % remove_density_from_ion_num] < 0] = 0.0

        # new ion
        tmp = {}
        tmp['ni_%d' % ion_num] = ni
        tmp['Ti_%d' % ion_num] = self['Ti_%d' % temperature_and_velocities_from_ion_num]
        tmp['vtor_%d' % ion_num] = self['vtor_%d' % temperature_and_velocities_from_ion_num]
        tmp['vpol_%d' % ion_num] = self['vpol_%d' % temperature_and_velocities_from_ion_num]

        # Add the ion to the IONS list by reverse shifting every ion with number>=ion_num up one
        # Also must shift other ion properties in gacode profiles file
        for i in list(reversed(list(range(ion_num, len(self['IONS']) + 1)))):
            self['IONS'][i + 1] = self['IONS'].pop(i)
            self['ni_%d' % (i + 1)] = self['ni_%d' % i]
            self['Ti_%d' % (i + 1)] = self['Ti_%d' % i]
            self['vtor_%d' % (i + 1)] = self['vtor_%d' % i]
            self['vpol_%d' % (i + 1)] = self['vpol_%d' % i]

        # Update ion data
        self.update(tmp)
        self['IONS'][ion_num] = [ion, int(Z), float(A), ['fast', 'therm'][thermal]]
        self['IONS'].sort()
        self['N_ION'] = len(self['IONS'])

        # make z_eff self consistent
        self['z_eff'] = self.calc_zeff()
        # There are occurances where the stafile (i.e. ONETWO example) can mess this one
        self['z_eff'][self['z_eff'] < 1] = 1.0

        # update ptot
        self['ptot'] = self.calc_ptot()

        return self

    def del_ion(self, ion, add_density_to_ion=1, verbose=True):
        """
        Remove ion from a gacode profiles file. When an ion is removed, its 'ni', 'Ti', 'vtor', 'vpol' quantities are set to zero.
            NOTE: this method operates in place

        :param ion: ion name or number as per .ion_names()

        :param add_density_to_ion: ion name or number to which to add the density of the ion that is being removed

        :param verbose: print when ion is removed

        :return: self (modified)
        """
        numd_ion_names = self.ion_names()
        if isinstance(ion, int):
            ion = numd_ion_names[ion - 1]
        if isinstance(add_density_to_ion, int):
            add_density_to_ion = numd_ion_names[add_density_to_ion - 1]

        ion_num = numd_ion_names.index(ion) + 1
        add_density_to_ion_num = numd_ion_names.index(add_density_to_ion) + 1

        if ion_num == add_density_to_ion_num:
            add_density_to_ion_num += 1

        # The ion's charge and density
        if verbose:
            printi('Removing ion %s' % ion)
            printi('Adding ion charge density to ni_{} {}'.format(add_density_to_ion_num, numd_ion_names[add_density_to_ion_num - 1]))
        Z_del = self['IONS'][ion_num][1]
        Z_add = self['IONS'][add_density_to_ion_num][1]
        ni_del = self['ni_%d' % ion_num]
        self['ni_%d' % add_density_to_ion_num] += (Z_del * ni_del) / float(Z_add)

        # Change the number of all following ions (i.e. if we remove ion 2 of 3, rename 3->2)
        for i in range(ion_num, len(self['IONS'])):
            self['IONS'][i] = self['IONS'][i + 1]
            self['ni_%d' % i] = self['ni_%d' % (i + 1)].copy()
            self['Ti_%d' % i] = self['Ti_%d' % (i + 1)].copy()
            self['vtor_%d' % i] = self['vtor_%d' % (i + 1)].copy()
            self['vpol_%d' % i] = self['vpol_%d' % (i + 1)].copy()
            if 'dlnnidr_%d' % (i + 1) in self:
                self['dlnnidr_%d' % i] = self['dlnnidr_%d' % (i + 1)].copy()
            if 'dlntidr_%d' % (i + 1) in self:
                self['dlntidr_%d' % i] = self['dlntidr_%d' % (i + 1)].copy()

        # Remove all evidence of the discarded ion
        ion_num = len(self['IONS'])
        del self['ni_{}'.format(ion_num)]
        del self['Ti_{}'.format(ion_num)]
        del self['vtor_{}'.format(ion_num)]
        del self['vpol_{}'.format(ion_num)]
        if 'dlnnidr_{}'.format(ion_num) in self:
            del self['dlnnidr_{}'.format(ion_num)]
        if 'dlntidr_{}'.format(ion_num) in self:
            del self['dlntidr_{}'.format(ion_num)]
        del self['IONS'][ion_num]
        self['N_ION'] = len(self['IONS'])

        # make z_eff self consistent
        self['z_eff'] = self.calc_zeff()
        # There are occurances where the stafile (i.e. ONETWO example) can can mess this one
        self['z_eff'][self['z_eff'] < 1] = 1.0

        # update ptot
        self['ptot'] = self.calc_ptot()

        return self

    def merge_DT(self, raise_no_DT=True, verbose=True):
        """
        merge thermal deuterium (D) and tritium (T) species into a single (DT) species with Z=1 and A=2.5

        :param raise_no_DT: raise exception if D and T species are not found

        :param verbose: print to stdout
        """
        names = self.ion_names()
        if 'T' in names and 'D' in names:
            if names.index('D') > names.index('T'):
                H1 = 'D'
                H2 = 'T'
            else:
                H2 = 'D'
                H1 = 'T'
            self.del_ion(H1, H2)
            self['IONS'][names.index(H2) + 1] = ['DT', 1, 2.5, 'therm']
        elif 'D' not in names and raise_no_DT:
            raise OMFITexception('gacode profiles does not have D species')
        elif 'T' not in names and raise_no_DT:
            raise OMFITexception('gacode profiles does not have T species')
        self.enforce_quasineutrality(verbose=verbose)

    def remove_fast(self, only_He=False, raise_no_fast=True, verbose=True):
        """
        delete all fast ions

        :param only_He: keep helium ash or not

        :param raise_no_fast: raise exception if there are no fast ions

        :param verbose: print to stdout
        """
        names = self.ion_names(fast_last=True)
        self.reorder_ions(names)
        no_fast = True
        for item in names[::-1]:
            if '[fast]' in item and (not only_He or item.startswith('He')):
                no_fast = False
                self.del_ion(item, names[0], verbose=verbose)
        if no_fast and raise_no_fast:
            raise OMFITexception('gacode profiles does not have fast ion species')
        self.enforce_quasineutrality(verbose=verbose)

    def remove_impurities(self, keep_He=True, raise_no_imp=True, verbose=True):
        """
        remove all impurity species, that is thermal ions with Z>1 (or Z>2 if keep_He is True)

        :param keep_He: keep Helium ions

        :param raise_no_imp: raise exception if there are no impurity species

        :param verbose: print to stdout
        """
        if keep_He:
            keep_He = 2
        else:
            keep_He = 1
        names = self.ion_names()
        no_imp = True
        for item in names[::-1]:
            if self['IONS'][names.index(item) + 1][-1] == 'therm' and self['IONS'][names.index(item) + 1][1] > keep_He:
                no_imp = False
                self.del_ion(item, names[0], verbose=verbose)
        if no_imp and raise_no_imp:
            raise OMFITexception('gacode profiles does not have impurity species')
        self.enforce_quasineutrality(verbose=verbose)

    def lump_impurities(self, impurity_symbol, z_eff=None, keep_He=True, verbose=True):
        """
        lump all impurity species into a single one

        :param impurity_symbol: impurity symbol

        :param z_eff: target Zeff

        :param keep_He: keep He impurities untouched

        :param verbose: print to stdout
        """

        if z_eff is None:
            self.enforce_quasineutrality(verbose=verbose)
            z_eff = self['z_eff']

        # remove all impurities
        self.remove_impurities(keep_He=keep_He, raise_no_imp=False)

        # add the requested impurity species to match a given Zeff
        imp = list(atomic_element(symbol=impurity_symbol).values())[0]
        self.add_ion(len(self.ion_names()) + 1, impurity_symbol, imp['Z'], imp['A'], z_eff=z_eff)
        self.enforce_quasineutrality(verbose=verbose)
        names = self.ion_names(fast_last=True)
        self.reorder_ions(names)

    def remove_dummy_ions(self):
        """
        Remove trailing ion species in gacode profiles that have no density or temperature
        NOTE: N_ION and IONS are set and trimmed accordingly
        """
        for k in reversed(list(range(1, 11))):
            if np.sum(self['ni_%d' % k] * self['Ti_%d' % k]) == 0:
                if self['N_ION'] > k:
                    self['N_ION'] = k
            else:
                break
        self['N_ION'] = k
        for k in range(self['N_ION'] + 1, 11):
            if k in self['IONS']:
                del self['IONS'][k]

    def enforce_quasineutrality(self, ion=1, balanced_DT=True, verbose=True):
        """
        Modify ion density and electron densities to make the plasma quasineutral.
            NOTE: this method operates in place
            NOTE: this method will also update Zeff and ptot

        :param ion: ion name or number as per .ion_names()

        :param balanced_DT: if ion is `D` or `T` in a DT plasma, then make plasma quasineutral by equally splitting differences on D and T ions

        :param verbose: print to stdout

        :return: self (modified)
        """
        # identify ion
        numd_ion_names = self.ion_names()
        if isinstance(ion, int):
            ion = numd_ion_names[ion - 1]
        ion_num = numd_ion_names.index(ion) + 1

        # get weighted ion densities
        ne = self['ne']
        zarr = []
        sum_nizi = ne * 0
        nizi = {}
        for i, k in enumerate(list(self['IONS'].keys()), 1):
            Z = self['IONS'][k][1]
            nizi['ni_%d' % i] = self['ni_%d' % i] * Z
            sum_nizi += nizi['ni_%d' % i]

        # warning message
        ratio = max((abs(ne - sum_nizi) / ne)[:-1]) * 100
        if ratio > 0.1 and verbose:
            printw('Starting profiles violated quasineutrality by %3.3f%% of electron density' % ratio)

        # update main ions density to ensure quasineutrality
        # handle balanced DT
        if ion in ['D', 'T'] and 'D' in numd_ion_names and 'T' in numd_ion_names and balanced_DT:
            d_ind = numd_ion_names.index('D') + 1
            t_ind = numd_ion_names.index('T') + 1
            Z = 1.0
            assert float(self['IONS'][d_ind][1]) == float(self['IONS'][t_ind][1]) == Z
            old = np.min([self['ni_%d' % d_ind], self['ni_%d' % t_ind]], 0)

            delta = ne - sum_nizi

            delta_ni = delta.copy() / float(Z)
            condition = np.min(np.vstack((self['ni_%d' % d_ind], self['ni_%d' % d_ind])), 0) + delta_ni / 2.0
            delta_ni[condition < 0] = 0.0

            delta_ne = -delta.copy()
            delta_ne[condition > 0] = 0.0

            self['ni_%d' % d_ind] += delta_ni / 2.0
            self['ni_%d' % t_ind] += delta_ni / 2.0
            ratio = max(abs(delta_ni / 2.0 / old)[:-1]) * 100
            if np.any(condition > 0) and ratio > 0.1 and verbose:
                printi('Modified D-T densities by a maximum of %3.3f%% each to enforce quasineutrality' % ratio)

        # handle single ion
        else:
            Z = float(self['IONS'][ion_num][1])
            ind_key = 'ni_%d' % ion_num

            delta = ne - sum_nizi

            delta_ni = delta.copy() / float(Z)
            condition = self[ind_key] + delta_ni
            delta_ni[condition < 0] = 0.0

            delta_ne = -delta.copy()
            delta_ne[condition > 0] = 0.0

            self[ind_key] += delta_ni

            ratio = max(abs(delta_ni / (self[ind_key] - delta_ni))[:-1]) * 100
            if np.any(condition > 0) and ratio > 0.1 and verbose:
                printi('Modified %s density by a maximum of %3.3f%% to enforce quasineutrality' % (ion, ratio))

        # making the plasma quasineutral may require modifying the electron density to avoid negative ion densities
        self['ne'] += delta_ne
        ratio = max(abs(delta_ne / (self['ne'] - delta_ne))[:-1]) * 100
        if np.any(condition < 0) and ratio > 0.1 and verbose:
            printw('Modified electron density by a maximum of %3.3f%% to enforce quasineutrality' % ratio)

        # update zeff
        self['z_eff'] = self.calc_zeff()

        # update total pressure
        self['ptot'] = self.calc_ptot()

        return self

    def volume(self):
        """
        return volume of each flux surface
        """
        if 'vol' in self:
            return self['vol']
        return miller_derived(self['rmin'], self['rmaj'], self['kappa'], self['delta'], self['zeta'], self['zmag'], self['q'])['volume']

    def volume_integral(self, quantity):
        """
        Integrate a quantity over the plasma volume

        :param quantity: if string, it integrates quantity in gacode profiles, else one must pass an array on the same grid of profiles in gacode profiles file

        :return: array of integrated quantity from axis to edge
        """
        if isinstance(quantity, str) and quantity in self:
            quantity = self[quantity]
        return integrate.cumtrapz(np.gradient(self.volume()) * quantity, initial=0)

    def monotonic(self, pivot=0, fast_ions=False, minimum_z=0.01):
        """
        Force densities and temperatures are monotonically decreasing from core to edge
        NOTE: might want to call self.enforce_quasineutrality() afterwards

        :param pivot: rho value (between 0 and 1) where the profiles will match the original ones

        :param fast_ions: apply monotonic transformation also to fast-ions

        :param minimum_z: minimum inverse scale-length value
        """
        for item in self:
            if item[0] in ['n', 'T'] and np.sum(self[item]) != 0:
                if item[1] == 'i' and self['IONS'][int(item.split('_')[1])][3] == 'fast' and not fast_ions:
                    continue
                z = calcz(self['rho'], self[item])
                z[z < minimum_z] = minimum_z
                self[item] = integz(self['rho'], z, pivot, interp1d(self['rho'], self[item])(pivot), self['rho'])

    def shot_time(self):
        """
        :return: tuple shot and time as written in the gacode profiles header (None if they cannot be found)
        """
        shot = None
        for p in [0, 1]:
            for k, v in list(self.items()):
                if not k.startswith('__header'):
                    continue
                if 'SHOT NUMBER' in v:
                    shot = int(v.split(':')[-1])
                elif shot is not None and str(shot) in v:
                    try:
                        time = int(re.sub('([0-9]+).*', r'\1', v.split(str(shot))[1].strip('.').strip()))
                    except Exception:
                        continue
                    return shot, time
        return shot, None

    def rz_geometry(self, poloidal_resolution=101):
        """
        Return R,Z coordinates for all flux surfaces from either fourier, ham, or miller geometry representation

        :param poloidal_resolution: integer with number of equispaced points in toroidal angle, or array of toroidal angles

        :return: 2D arrays with (R, Z) flux surface coordinates
        """
        if 'ar' in self:
            r, z = self.rz_fourier_geometry(poloidal_resolution=poloidal_resolution)
        elif 'shape_cos0' in self:
            r, z = self.rz_ham_geometry(poloidal_resolution=poloidal_resolution)
        else:
            r, z = self.rz_miller_geometry(poloidal_resolution=poloidal_resolution)
        return r, z

    def rz_miller_geometry(self, poloidal_resolution=101):
        """
        return R,Z coordinates for all flux surfaces from miller geometry coefficients in gacode profiles file
        based on gacode/gapy/src/gapy_geo.f90

        :param poloidal_resolution: integer with number of equispaced points in toroidal angle, or array of toroidal angles

        :return: 2D arrays with (R, Z) flux surface coordinates
        """
        if isinstance(poloidal_resolution, int):
            t0 = np.linspace(0, 2 * np.pi, poloidal_resolution)
        else:
            t0 = poloidal_resolution

        x = np.arcsin(self['delta'])

        # R
        a = t0[:, np.newaxis] + x[np.newaxis, :] * np.sin(t0[:, np.newaxis])
        r0 = self['rmaj'][np.newaxis, :] + self['rmin'][np.newaxis, :] * np.cos(a)

        # Z
        a = t0[:, np.newaxis] + self['zeta'][np.newaxis, :] * np.sin(2 * t0[:, np.newaxis])
        z0 = self['zmag'][np.newaxis, :] + self['kappa'][np.newaxis, :] * self['rmin'][np.newaxis, :] * np.sin(a)

        return r0, z0

    def rz_fourier_geometry(self, poloidal_resolution=101):
        """
        return R,Z coordinates for all flux surfaces from fourier geometry representation in gacode profiles file

        :param poloidal_resolution: integer with number of equispaced points in toroidal angle, or array of toroidal angles

        :return: 2D arrays with (R, Z) flux surface coordinates
        """
        ar = copy.deepcopy(self['ar'])
        ar[:, 0] = ar[:, 0] / 2.0
        br = self['br']
        az = copy.deepcopy(self['az'])
        az[:, 0] = az[:, 0] / 2.0
        bz = self['bz']

        if isinstance(poloidal_resolution, int):
            x = np.linspace(0, 1, poloidal_resolution)
        else:
            x = poloidal_resolution

        XN = x[:, np.newaxis] * np.arange(ar.shape[1])
        r = np.zeros((len(x), ar.shape[0]))
        z = np.zeros((len(x), az.shape[0]))
        for l in range(ar.shape[0]):
            r[:, l] = np.sum(ar[l, :] * np.cos(2 * np.pi * XN) + br[l, :] * np.sin(2 * np.pi * XN), 1)
            z[:, l] = np.sum(az[l, :] * np.cos(2 * np.pi * XN) + bz[l, :] * np.sin(2 * np.pi * XN), 1)

        return r, z

    def rz_ham_geometry(self, poloidal_resolution=101):
        """
        return R,Z coordinates for all flux surfaces from ham geometry representation in gacode profiles file

        :param poloidal_resolution: integer with number of equispaced points in toroidal angle, or array of toroidal angles

        :return: 2D arrays with (R, Z) flux surface coordinates
        """
        rmaj = self['rmaj']
        zmaj = self['zmag']
        r = self['rmin']
        k = self['kappa']
        s1 = np.arcsin(self['delta'])
        s2 = -self['zeta']
        s3 = self['shape_sin3']
        c0 = self['shape_cos0']
        c1 = self['shape_cos1']
        c2 = self['shape_cos2']
        c3 = self['shape_cos3']

        if isinstance(poloidal_resolution, int):
            t = np.linspace(0, 2 * np.pi, poloidal_resolution)
        else:
            t = poloidal_resolution

        x = rmaj[np.newaxis, :] + r[np.newaxis, :] * np.cos(
            t[:, np.newaxis]
            + c0[np.newaxis, :]
            + s1[np.newaxis, :] * np.sin(t[:, np.newaxis])
            + c1[np.newaxis, :] * np.cos(t[:, np.newaxis])
            + s2[np.newaxis, :] * np.sin(2 * t[:, np.newaxis])
            + c2[np.newaxis, :] * np.cos(2 * t[:, np.newaxis])
            + s3[np.newaxis, :] * np.sin(3 * t[:, np.newaxis])
            + c3[np.newaxis, :] * np.cos(3 * t[:, np.newaxis])
        )
        y = zmaj[np.newaxis, :] + k[np.newaxis, :] * r[np.newaxis, :] * np.sin(t[:, np.newaxis])
        return x, y

    def from_omas(self, ods, time_index=0, clear=True):
        """
        Translate OMAS data structure to gacode profiles file

        :param time_index: time index to extract data from

        :param clear: clear gacode profiles content prior populating it

        :return: self
        """

        from omas import ODS, omas_environment

        cocosio = 2  # GACODE uses COCOS 2

        rho = ods['core_profiles.profiles_1d.%d.grid.rho_tor_norm' % time_index]
        rho = rho[rho <= 1]
        coordsio = {'core_profiles.profiles_1d.%d.grid.rho_tor_norm' % time_index: rho}

        if (
            'equilibrium.time_slice.%d.profiles_1d.psi' % time_index in ods
            and 'equilibrium.time_slice.%d.profiles_1d.rho_tor_norm' % time_index in ods
        ):
            with omas_environment(ods, cocosio=cocosio):
                psi1D = interp1e(
                    ods['equilibrium.time_slice.%d.profiles_1d.rho_tor_norm' % time_index],
                    ods['equilibrium.time_slice.%d.profiles_1d.psi' % time_index],
                )(rho)
                coordsio['equilibrium.time_slice.%d.profiles_1d.psi' % time_index] = psi1D

        with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):

            prof1d = ods['core_profiles.profiles_1d'][time_index]
            eq = ods['equilibrium.time_slice'][time_index]
            eq1d = ods['equilibrium.time_slice'][time_index]['profiles_1d']

            if clear:
                self.clear()
            else:
                # only clear headers
                for item in list(self.keys()):
                    if re.match(comment_ptrn, item):
                        del self[item]

            # This is a fresh file, so turn off dynaLoad
            self.dynaLoad = False
            self['__header_0000__'] = '# gacode profiles - Generated by OMFIT via OMAS on ' + now()
            self['__header_0001__'] = '#'
            self['__header_0002__'] = '#                 IONS :  Name       Z    Mass'
            self['__header_0003__'] = '#'
            self['IONS'] = SortedDict()
            self['N_ION'] = 0
            self['N_EXP'] = 0
            if 'core_profiles.vacuum_toroidal_field.b0' in ods:
                self['BT_EXP'] = ods['core_profiles.vacuum_toroidal_field.b0'][time_index]
            elif 'equilibrium.vacuum_toroidal_field.b0' in ods:
                self['BT_EXP'] = ods['equilibrium.vacuum_toroidal_field.b0'][time_index]
            if 'global_quantities.ip' in eq:
                self['IP_EXP'] = eq['global_quantities.ip'] / 1e6
            if 'core_profiles.vacuum_toroidal_field.r0' in ods:
                self['RVBV'] = ods['core_profiles.vacuum_toroidal_field.r0'] * ods['core_profiles.vacuum_toroidal_field.b0'][time_index]
            elif 'equilibrium.vacuum_toroidal_field.r0' in ods:
                self['RVBV'] = ods['equilibrium.vacuum_toroidal_field.r0'] * ods['equilibrium.vacuum_toroidal_field.b0'][time_index]
            self['ARHO_EXP'] = 0
            self['rho'] = prof1d['grid.rho_tor_norm']
            self['N_EXP'] = len(self['rho'])

            # zero out arrays
            for item in np.array(self.profNames[self.latest_version]).flatten():
                if item not in ['NULL', 'rho']:
                    self[item] = self['rho'] * 0.0

            # polflux is in Wb/rad, so actually psi_ref in COCOS 2
            # should be zero on-axis
            self['polflux'] = eq1d['psi'] - eq1d['psi'][0]

            try:
                if 'centroid' not in eq1d:
                    raise LookupError('OMAS centroid not available')
                self['rmin'] = 0.5 * (eq1d['centroid.r_max'] - eq1d['centroid.r_min'])
                self['rmin'][0] = 0.0
                self['rmaj'] = 0.5 * (eq1d['centroid.r_max'] + eq1d['centroid.r_min'])
                self['kappa'] = eq1d['elongation']
                self['delta'] = 0.5 * (eq1d['triangularity_lower'] + eq1d['triangularity_upper'])
                if np.all(
                    [
                        k in eq1d
                        for k in ['squareness_upper_outer', 'squareness_upper_inner', 'squareness_lower_outer', 'squareness_lower_inner']
                    ]
                ):
                    self['zeta'] = 0.25 * (
                        eq1d['squareness_upper_outer']
                        + eq1d['squareness_upper_inner']
                        + eq1d['squareness_lower_outer']
                        + eq1d['squareness_lower_inner']
                    )
                else:
                    self['zeta'] = self['kappa'] * 0.0
                self['zmag'] = eq1d['centroid.z']
                self['q'] = eq1d['q']
            except (LookupError, TypeError):
                # if the geometric quantities are missing, then we have no choice but to trace the flux surfaces
                psin = eq1d['psi']
                psin = (psin - min(psin)) / (max(psin) - min(psin))
                tmp = fluxSurfaces(
                    Rin=eq['profiles_2d'][0]['r'][:, 0],
                    Zin=eq['profiles_2d'][0]['z'][0, :],
                    PSIin=eq['profiles_2d'][0]['psi'].T,
                    Btin=eq['profiles_2d'][0]['b_field_tor'].T,
                    Rcenter=eq['global_quantities.magnetic_axis.r'],
                    F=eq1d['f'],
                    P=eq1d['pressure'],
                    levels=psin,
                    cocosin=cocosio,
                    quiet=True,
                )

                tmp.dynaLoad = False
                if 'global_quantities.psi_boundary' in eq:
                    tmp.forceFindSeparatrix = False
                    tmp._findAxis()
                    tmp.flx = eq['global_quantities.psi_boundary']
                # tmp.PSIaxis = eq['global_quantities.psi_axis']
                tmp.load()

                self['rmin'] = tmp['geo']['a']
                self['rmaj'] = tmp['geo']['R']
                self['kappa'] = tmp['geo']['kap']
                self['delta'] = tmp['geo']['delta']
                self['zeta'] = tmp['geo']['zeta']
                self['zmag'] = tmp['geo']['Z']
                self['q'] = tmp['avg']['q']

            self['ARHO_EXP'] = np.sqrt(self['kappa'][-1]) * self['rmin'][-1]
            self['ne'] = prof1d['electrons.density_thermal'] / 1e19
            self['Te'] = prof1d['electrons.temperature'] / 1e3

            derived = miller_derived(self['rmin'], self['rmaj'], self['kappa'], self['delta'], self['zeta'], self['zmag'], self['q'])
            R = self['rmaj'] + self['rmin']
            Bp = derived['bp0']
            Bt = derived['bt0']

            i = 0
            self['ptot'] = prof1d['electrons.density_thermal'] * prof1d['electrons.temperature'] * constants.e
            for therm_fast, density in [('therm', 'density_thermal'), ('fast', 'density_fast')]:
                for k in range(len(prof1d['ion'])):
                    if len(prof1d['ion']) and density in prof1d['ion'][k] and np.sum(np.abs(prof1d['ion'][k][density])) > 0:
                        i += 1
                        A = prof1d['ion'][k]['element'][0]['a']
                        Z_N = Z = prof1d['ion'][k]['element'][0]['z_n']
                        if 'z_ion' in prof1d['ion'][k]:
                            Z = prof1d['ion'][k]['z_ion']
                        if 'label' in prof1d['ion'][k]:
                            label = prof1d['ion'][k]['label'].strip().split()[0]
                        else:
                            try:
                                label = list(atomic_element(A=A, Z=Z_N).values())[0]['symbol']
                            except ValueError:
                                label = 'LUMPED'
                        self['IONS'][i] = self['ni_%d' % i] = [label, Z, A, therm_fast]
                        self['ni_%d' % i] = prof1d['ion'][k][density] / 1e19
                        if therm_fast == 'therm':
                            self['Ti_%d' % i] = prof1d['ion'][k]['temperature'] / 1e3
                            self['ptot'] += prof1d['ion'][k]['density_thermal'] * prof1d['ion'][k]['temperature'] * constants.e

                            if 'ion.%d.rotation.parallel_stream_function' % k in prof1d:
                                kpol = prof1d['ion.%d.rotation.parallel_stream_function' % k]
                                omegp = -Bt * kpol / R
                                self['vpol_%d' % i] = kpol * Bp

                                if 'ion.%d.rotation.perpendicular' % k in prof1d:
                                    omgvb = prof1d['ion.%d.rotation.perpendicular' % k]
                                elif ('rotation_frequency_tor_sonic' in prof1d) and ('ion.%d.rotation.diamagnetic' % k in prof1d):
                                    omgvb = prof1d['rotation_frequency_tor_sonic'] - prof1d['ion.%d.rotation.diamagnetic' % k]
                                else:
                                    self['vtor_%d' % i] = 0.0 * R
                                    continue

                                self['vtor_%d' % i] = R * (omgvb - omegp)
                            else:
                                self['vpol_%d' % i] = 0.0 * R

                        else:
                            self['Ti_%d' % i] = (
                                (
                                    (2 * prof1d['ion'][k]['pressure_fast_perpendicular'] + prof1d['ion'][k]['pressure_fast_parallel'])
                                    / prof1d['ion'][k]['density_fast']
                                )
                                / constants.e
                                / 1e3
                            )
                            self['ptot'] += 2 * prof1d['ion'][k]['pressure_fast_perpendicular'] + prof1d['ion'][k]['pressure_fast_parallel']
                            # Set finite temperature when density ~0  for TGYRO splines
                            navg = np.mean(prof1d['ion'][k]['density_fast'])
                            self['Ti_%d' % i][np.where(prof1d['ion'][k]['density_fast'] < 1e-6 * navg)] = np.mean(self['Ti_%d' % i])

            self['N_ION'] = i

            self['z_eff'] = prof1d['zeff']

            if 'rotation_frequency_tor_sonic' in prof1d:
                self['omega0'] = prof1d['rotation_frequency_tor_sonic']
            elif 'omega0' in prof1d:
                self['omega0'] = prof1d['omega0']
            else:
                self['omega0'] = prof1d['zeff'] * 0.0

        # =============
        # Core Sources
        # =============
        if 'core_sources' not in ods:
            printw('`core_sources` data not found in supplied ODS. Skip populating gacode profiles sources!')

        else:

            def d_dvol(y):
                return deriv(src['grid.volume'], y)

            def i_vol(y):
                return integrate.cumtrapz(y, src['grid.volume'], initial=0)

            source = ods['core_sources.source']
            for ks in range(len(source)):
                identifier = source[ks]['identifier.name']
                id_index = source[ks].get('identifier.index', None)

                # decide how to map data in OMAS to input.gacode
                # two passes: first try a matching index, second use the catch-all [-1]
                candidates = []
                for t in range(2):
                    for item in omas_source_mapper:
                        type, possible_id_index, details = omas_source_mapper[item]
                        if id_index is not None and ((t == 0 and id_index in possible_id_index) or (t > 0 and -1 in possible_id_index)):
                            if isinstance(self, OMFITinputprofiles) and type == 'i_vol':
                                candidates.append(item)
                            elif isinstance(self, OMFITinputgacode) and type == 'd_dvol':
                                candidates.append(item)
                if not len(candidates):
                    printe('Unrecognized source: %s of IMAS type index %d' % (identifier, id_index))
                    continue
                src = source[ks]['profiles_1d'][time_index]

                coordsio2 = copy.deepcopy(coordsio)
                coordsio2['core_sources.source.%d.profiles_1d.%d.grid.rho_tor_norm' % (ks, time_index)] = rho
                with omas_environment(ods, cocosio=cocosio, coordsio=coordsio2):
                    # NOTE: input.profiles sources are volume integrated
                    # NOTE: input.gacode sources are the not (though the derived integrated value is also available)
                    if 'volume' in src['grid']:
                        vol = src['grid.volume']
                    else:
                        try:
                            vol = interp1d(
                                ods['equilibrium']['time_slice'][time_index]['profiles_1d']['rho_tor_norm'],
                                ods['equilibrium']['time_slice'][time_index]['profiles_1d']['volume'],
                            )(rho)
                        except Exception:
                            vol = None

                    accounted = []
                    for candidate in candidates:
                        type, possible_id_index, details = omas_source_mapper[candidate]
                        for sign, location, norm in details:
                            ilocation = map_d_i[location]
                            # check if source density is available
                            if location not in accounted and location in src and np.sum(np.abs(src[location])) > 0:
                                if candidate not in self:
                                    self[candidate] = self['rho'] * 0.0
                                if isinstance(self, OMFITinputgacode):
                                    self[candidate] += sign * src[location] / norm
                                    print('%d) %s %s= %s[%s]/%g' % (ks, candidate, ['-', '+'][int(sign > 0)], identifier, location, norm))
                                elif isinstance(self, OMFITinputprofiles):
                                    self[candidate] += sign * i_vol(src[location]) / norm
                                    print(
                                        '%d) %s %s= i_vol(%s[%s])/%g'
                                        % (ks, candidate, ['-', '+'][int(sign > 0)], identifier, location, norm)
                                    )
                                accounted.append(location)
                            # alternatively get it from integrated source
                            elif location not in accounted and ilocation in src and np.sum(np.abs(src[ilocation])) > 0:
                                if candidate not in self:
                                    self[candidate] = self['rho'] * 0.0
                                if isinstance(self, OMFITinputgacode):
                                    self[candidate] += sign * d_dvol(src[ilocation]) / norm
                                    print(
                                        '%d) %s %s= d_dvol(%s[%s])/%g'
                                        % (ks, candidate, ['-', '+'][int(sign > 0)], identifier, ilocation, norm)
                                    )
                                elif isinstance(self, OMFITinputprofiles):
                                    self[candidate] += sign * src[ilocation] / norm
                                    print('%d) %s %s= %s[%s]/%g' % (ks, candidate, ['-', '+'][int(sign > 0)], identifier, ilocation, norm))
                                accounted.append(location)

        # set the GACODEtype
        self.GACODEtype = 'profiles'

        # update all derived quantities
        self.consistent_derived()

        # run checks
        self.checks()

        return self

    def to_omas(self, ods=None, time_index=0, update=['core_profiles', 'equilibrium', 'core_sources']):
        """
        Translate gacode profiles file to OMAS data structure

        :param ods: input ods to which data is added

        :param time_index: time index to which data is added

        :update: list of IDS to update from gacode profiles

        :return: ODS
        """
        from omas import ODS, omas_environment

        if ods is None:
            ods = ODS()

        cocosio = 2  # GACODE is COCOS 2

        # setup coordsio for automatic interpolation
        coordsio = {
            'core_profiles.profiles_1d.%d.grid.rho_tor_norm' % time_index: self['rho'],
            'equilibrium.time_slice.%d.profiles_1d.psi' % time_index: self['polflux'],
        }
        if 'equilibrium.time_slice.%d.profiles_1d.psi' % time_index in ods:
            with omas_environment(ods, cocosio=cocosio):
                ods['equilibrium.time_slice.%d.profiles_1d.psi' % time_index] = (
                    ods['equilibrium.time_slice.%d.profiles_1d.psi' % time_index]
                    - ods['equilibrium.time_slice.%d.profiles_1d.psi' % time_index][0]
                    + coordsio['equilibrium.time_slice.%d.profiles_1d.psi' % time_index][0]
                )
        for i, s in enumerate(omas_source_mapper):
            coordsio['core_sources.source.%d.profiles_1d.%d.grid.rho_tor_norm' % (i, time_index)] = self['rho']

        # generate ODS
        with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):
            eq = ods['equilibrium.time_slice'][time_index]

            # =============
            # Equilibrium
            # =============
            if 'equilibrium' in update:
                eq['global_quantities.magnetic_axis.b_field_tor'] = self['BT_EXP']
                if 'IP_EXP' in self:
                    eq['global_quantities.ip'] = self['IP_EXP'] * 1e6

                ods.set_time_array('core_profiles.vacuum_toroidal_field.b0', time_index, self['BT_EXP'])
                ods.set_time_array('equilibrium.vacuum_toroidal_field.b0', time_index, self['BT_EXP'])
                if 'RVBV' in self:
                    ods['core_profiles.vacuum_toroidal_field.r0'] = self['RVBV'] / self['BT_EXP']
                    ods['equilibrium.vacuum_toroidal_field.r0'] = ods['core_profiles.vacuum_toroidal_field.r0']

                r, z = self.rz_geometry()
                eq['boundary.outline.r'] = r[:, -1]
                eq['boundary.outline.z'] = z[:, -1]

                eq['profiles_1d.rho_tor_norm'] = self['rho']

                eq['profiles_1d.psi'] = self['polflux']

                eq['profiles_1d.elongation'] = self['kappa']

                eq['profiles_1d.triangularity_upper'] = self['delta']
                eq['profiles_1d.triangularity_lower'] = self['delta']
                eq['profiles_1d.squareness_upper_outer'] = self['zeta']
                eq['profiles_1d.squareness_upper_inner'] = self['zeta']
                eq['profiles_1d.squareness_lower_outer'] = self['zeta']
                eq['profiles_1d.squareness_lower_inner'] = self['zeta']

                eq['profiles_1d.centroid.r_max'] = self['rmaj'] + self['rmin']
                eq['profiles_1d.centroid.r_min'] = self['rmaj'] - self['rmin']
                eq['profiles_1d.centroid.z'] = self['zmag']

                eq['profiles_1d.q'] = self['q']

            # geometry info
            derived = miller_derived(self['rmin'], self['rmaj'], self['kappa'], self['delta'], self['zeta'], self['zmag'], self['q'])
            R = self['rmaj'] + self['rmin']
            Bp = derived['bp0'] + np.finfo(float).eps  # prevent division by zero
            Bt = derived['bt0']

            # =============
            # Core Profiles
            # =============
            if 'core_profiles' in update:
                prof1d = ods['core_profiles.profiles_1d'][time_index]

                prof1d['grid.rho_tor_norm'] = self['rho']
                prof1d['electrons.density_thermal'] = self['ne'] * 1e19
                prof1d['electrons.temperature'] = self['Te'] * 1e3

                if 'ion' in prof1d:
                    prof1d['ion'].clear()
                ions = {}
                for i, ion in enumerate(self['IONS'].values()):
                    i += 1
                    ion_name, Z_ion, A, therm_fast = ion
                    if ion_name not in ions:
                        ions[ion_name] = len(ions)
                    k = ions[ion_name]
                    if ion_name.lower() in ['lumped']:
                        ion_details = {'symbol': ion_name, 'Z_ion': Z_ion, 'Z': Z_ion, 'A': A}
                    else:
                        ion_details = list(atomic_element(symbol=ion_name, Z_ion=Z_ion).values())[0]
                    prof1d['ion'][k]['label'] = ion_details['symbol']
                    prof1d['ion'][k]['z_ion'] = ion_details['Z_ion']
                    prof1d['ion'][k]['multiple_states_flag'] = 0
                    prof1d['ion'][k]['element'][0]['atoms_n'] = 1
                    prof1d['ion'][k]['element'][0]['z_n'] = ion_details['Z']
                    prof1d['ion'][k]['element'][0]['a'] = ion_details['A']
                    if therm_fast == 'therm':
                        density = 'density_thermal'
                    else:
                        density = 'density_fast'
                    prof1d['ion'][k][density] = self['ni_%d' % i] * 1e19

                    if therm_fast == 'therm':
                        prof1d['ion'][k]['temperature'] = self['Ti_%d' % i] * 1e3

                        # only send rotations to OMAS if non-zero
                        if np.any(self['vpol_%d' % i] != 0.0) or np.any(self['vtor_%d' % i] != 0.0):
                            kpol = self['vpol_%d' % i] / Bp
                            omeg = self['vtor_%d' % i] / R
                            omegp = -kpol * Bt / R

                            prof1d['ion'][k]['rotation.parallel_stream_function'] = kpol
                            prof1d['ion'][k]['rotation.perpendicular'] = omeg + omegp
                            prof1d['ion'][k]['rotation.diamagnetic'] = self['omega0'] - omeg - omegp

                    else:
                        prof1d['ion'][k]['pressure_fast_perpendicular'] = (
                            self['Ti_%d' % i] / 3.0 * prof1d['ion'][k]['density_fast'] * constants.e * 1e3
                        )
                        prof1d['ion'][k]['pressure_fast_parallel'] = (
                            self['Ti_%d' % i] / 3.0 * prof1d['ion'][k]['density_fast'] * constants.e * 1e3
                        )

                prof1d['zeff'] = self['z_eff']
                prof1d['rotation_frequency_tor_sonic'] = self['omega0']

            # =============
            # Core Sources
            # =============
            if 'core_sources' in update or 'core_sources-internal' in update or 'core_sources-aux' in update:
                source = ods['core_sources.source']
                if 'core_sources' in update:
                    source.clear()
                if 'core_sources-internal' in update:
                    for s in range(len(source) - 1, -1, -1):
                        if source[s]['identifier.index'] in sources_internal_list:
                            del source[s]
                if 'core_sources-aux' in update:
                    for s in range(len(source) - 1, -1, -1):
                        if source[s]['identifier.index'] not in sources_internal_list:
                            del source[s]

                volume = derived['volume']

                def d_dvol(y):
                    return deriv(source[s]['profiles_1d'][time_index]['grid.volume'], y)

                def i_vol(y):
                    return integrate.cumtrapz(y, source[s]['profiles_1d'][time_index]['grid.volume'], initial=0)

                for identifier in omas_source_mapper:

                    type, possible_id_index, details = omas_source_mapper[identifier]
                    id_index = possible_id_index[0]

                    if 'core_sources' not in update and not ('core_sources-internal' in update and 'core_sources-aux' in update):
                        if 'core_sources-aux' in update and id_index in sources_internal_list:
                            continue

                        if 'core_sources-internal' in update and id_index not in sources_internal_list:
                            continue

                    if type == 'd_dvol' and isinstance(self, OMFITinputprofiles):
                        continue
                    elif type == 'i_vol' and isinstance(self, OMFITinputgacode):
                        continue

                    s = len(source)
                    source[s]['profiles_1d'][time_index]['grid.volume'] = volume
                    source[s]['identifier.name'] = identifier
                    source[s]['identifier.index'] = id_index
                    src = source[s]['profiles_1d'][time_index]

                    for sign, location, norm in details:
                        ilocation = map_d_i[location]
                        # split collisional_equipartition between ions and electrons
                        if id_index == 11:
                            norm = norm / 2.0

                        # we write both source densities as well as integrated values
                        if location not in src:
                            src[location] = volume * 0.0
                        if ilocation not in src:
                            src[ilocation] = volume * 0.0
                        if type == 'd_dvol':
                            src[location] += sign * self[identifier] * norm
                            src[ilocation] += sign * i_vol(self[identifier]) * norm
                        elif type == 'i_vol':
                            src[location] += sign * d_dvol(self[identifier]) * norm
                            src[ilocation] += sign * self[identifier] * norm

            # =============
            # Summary
            # =============
            if 'ptransp' in self:
                if 'power_loss' not in ods['summary.global_quantities']:
                    ods['summary.global_quantities.power_loss.value'] = [self['ptransp'] * 1e6]
                else:
                    ods['summary.global_quantities.power_loss.value'][time_index] = self['ptransp'] * 1e6

            if 'vol' in self:
                norm = 1e19 * 1e3 * constants.e
                total_pressure = self['ne'] * self['Te'] * norm
                ion_names = self.ion_names()

                for idx, ion in enumerate(ion_names):
                    idx += 1
                    if 'fast' in ion.lower():
                        continue
                    else:
                        total_pressure += self[f'ni_{idx}'] * self[f'Ti_{idx}'] * norm

                if 'energy_thermal' not in ods['summary.global_quantities']:
                    ods['summary.global_quantities.energy_thermal.value'] = [3 / 2 * np.trapz(total_pressure, x=self['vol'])]
                else:
                    ods['summary.global_quantities.energy_thermal.value'][time_index] = 3 / 2 * np.trapz(total_pressure, x=self['vol'])

        return ods

    def __save_kw__(self):
        """
        :return: kw dictionary used to save the attributes to be passed when reloading from OMFITsave.txt
        """
        tmp = self.OMFITproperties.copy()
        if 'GACODEtype' in self.OMFITproperties and self.OMFITproperties['GACODEtype'] is None:
            tmp.pop('GACODEtype')
        return tmp

    def __popup_menu__(self):
        menu = []
        if self.GACODEtype in ['profiles', 'geo']:
            menu.append(['Plot flux surfaces', lambda: self.plot(only2D=True)])
        if self.GACODEtype == 'profiles':
            menu.append(['Consistency checks', self.checks])
        return menu

    def calcQ(self):
        """
        Calculate and return the fusion energy gain factor, Q,
        assuming D+T->alpha+neutron is the main reaction
        """
        # Factor of 5 in following is because total fusion power = 5*alpha power, correct for DT
        return (self['pow_i_fus'][-1] + self['pow_e_fus'][-1]) * 5 / (self['pow_i_aux'][-1] + self['pow_e_aux'][-1])

    def calc_powei_fusion(self, in_place=False):
        """
        calculate pow_e_fus and pow_i_fus given profiles

        :param in_place: update qfusi, qfusi, pow_e_fus and pow_i_fus

        :return: tuple with pow_e_fus, pow_i_fus, qfuse, qfusi
        """
        ion_names = self.ion_names()
        if 'DT' in ion_names:
            k = ion_names.index('DT') + 1
            Ti = self['Ti_%d' % k] * 1e3
            nD = self['ni_%d' % k] * 1e19 / 2.0
            nT = self['ni_%d' % k] * 1e19 / 2.0

        elif 'D' in ion_names and 'T' in ion_names:
            k = ion_names.index('D') + 1
            Ti = self['Ti_%d' % k] * 1e3
            nD = self['ni_%d' % k] * 1e19
            k = ion_names.index('T') + 1
            nT = self['ni_%d' % k] * 1e19
            Ti += self['Ti_%d' % k] * 1e3
            Ti /= 2.0

        else:
            k = 1
            Ti = self['Ti_%d' % k] * 1e3
            nD = self['ni_%d' % k] * 1e19 / 2.0
            nT = self['ni_%d' % k] * 1e19 / 2.0

        # fusion power
        qfus = fusion_power(nD, nT, Ti)
        pfus = self.volume_integral(qfus)

        # calculate alpha heating partion betweek electrons and ions
        ni = []
        zi = []
        mi = []
        for k, name in enumerate(self.ion_names()):
            if self['IONS'][k + 1][-1] == 'therm':
                ni.append(self['ni_%d' % (k + 1)])
                zi.append(self['IONS'][k + 1][1])
                mi.append(self['IONS'][k + 1][2])
        ne = self['ne']
        Te = self['Te']
        frac_ai = alpha_heating(np.array(ni), zi, mi, ne, Te * 1e3)

        pow_e_fus = pfus * (1 - frac_ai) / 1e6
        pow_i_fus = pfus * frac_ai / 1e6
        qfuse = qfus * (1 - frac_ai) / 1e6
        qfusi = qfus * frac_ai / 1e6

        if in_place:
            self['pow_e'] = self['pow_e'] - self['pow_e_fus'] + pow_e_fus
            self['pow_e_fus'] = pow_e_fus
            self['pow_i'] = self['pow_i'] - self['pow_i_fus'] + pow_i_fus
            self['pow_i_fus'] = pow_i_fus
            self['qfuse'] = qfuse
            self['qfusi'] = qfusi

        return pow_e_fus, pow_i_fus, qfuse, qfusi

    def to_gen(self, input_profiles_version=-1):
        '''
        Generate input.XXX.gen file

        :param input_profiles_version: version of the input.profiles format to use (-1 uses latest)
        '''
        tmp = _gacode_profiles()
        tmp.init_profiles_names()

        if input_profiles_version == -1:
            input_profiles_version = self.latest_version

        txt = [
            f'''
{self.get('SHOT', 0)}  SHOT
{len(self['IONS'])}  N_ION
{self['N_EXP']}  N_EXP
{self.get('BT_EXP', 0.0)}  BT_EXP
{self.get('IP_EXP', 0.0)}  IP_EXP
{self.get('RVBV', 0.0)}  RVBV
{self['ARHO_EXP']} ARHO_EXP
    '''.strip()
        ]
        for row in tmp.profNames[input_profiles_version]:
            for k in row:
                if k == 'NULL' or k not in self:
                    txt.append('\n'.join(map(lambda x: '%10.10e' % x, self['rho'] * 0.0)))
                else:
                    txt.append('\n'.join(map(lambda x: '%10.10e' % x, self[k])))

        tmp = OMFITascii(os.path.split(self.filename)[1] + '.gen')
        tmp.write('\n'.join(txt))
        return tmp


class OMFITinputprofiles(OMFITgacode, _gacode_profiles):
    def __init__(self, filename=None, GACODEtype=None, **kw):
        OMFITgacode.__init__(self, filename, GACODEtype=GACODEtype, **kw)
        self.init_profiles_names()

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """
        self.clear()

        if self.filename is None or not os.stat(self.filename).st_size:
            return

        with open(self.filename, 'r') as f:
            lines = f.read()
        if len(lines):
            lines = lines.split('\n')
            lines = [line.strip() for line in lines]
            for h, line in enumerate(lines):
                if not len(line):
                    continue
                if line[0] != '#':
                    break
                self['__header_' + format(h, '04d') + '__'] = line

        # parse input.profiles.extra files
        if (
            self.GACODEtype == 'extra'
            or re.match(r'input\.profiles\.extra.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.extra$', os.path.split(self.filename)[1])
        ):
            self.__class__ = OMFITinputprofiles
            self.GACODEtype = 'extra'
            for line in lines:
                if re.match('# Each vector has length', line):
                    length = int(re.findall('# Each vector has length (.*)', line)[0])

            data = np.genfromtxt(self.filename, comments='#', invalid_raise=True)
            data = np.reshape(data, (-1, length))

            # always create all of the entries
            for var in self.extraNames[self.latest_version]:
                self[var] = np.zeros(length)

            # identify version (from latest to oldest)
            self.version = self.latest_version
            for k in list(self.extraNames.keys())[::-1]:
                if len(self.extraNames[k]) == data.shape[0]:
                    self.version = k
            extraNames = self.extraNames[self.version]

            for k, entry in enumerate(extraNames[: data.shape[0]]):
                self[entry] = data[k]

        # parse input.profiles.geo files
        elif (
            self.GACODEtype == 'geo'
            or re.match(r'input\.profiles\.geo.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.geo', os.path.split(self.filename)[1])
        ):
            self.__class__ = OMFITinputprofiles
            self.GACODEtype = 'geo'
            data = np.genfromtxt(self.filename, comments='#', invalid_raise=True)
            length = data[0]
            data = np.reshape(data[1:], (-1, int(length) + 1, 4))
            for k, entry in enumerate(['ar', 'br', 'az', 'bz']):
                self[entry] = data[:, :, k]

        # parse input.profiles files
        elif (
            self.GACODEtype == 'profiles'
            or re.match(r'input\.profiles.*$', os.path.split(self.filename)[1])
            or re.match(r'.*\.profiles$', os.path.split(self.filename)[1])
        ):
            self.__class__ = OMFITinputprofiles
            self.GACODEtype = 'profiles'

            def parse_ion_line(x):
                try:
                    return [x[0], int(x[1]), float(x[2]), x[3].strip('[]')]
                except Exception:
                    return [x[0], int(x[1]), float(x[2]), 'thermal?']

            header_ptrn = re.compile(r'^__header_.*__$')
            ions = self['IONS'] = SortedDict()
            startIons = False
            kk = 0
            for k in list(self.keys()):
                if re.match(header_ptrn, k):
                    if startIons:
                        if len(self[k]) > 1:
                            kk += 1
                            ions[kk] = parse_ion_line([x for x in self[k].split() if x][1:5])
                            del self[k]
                        else:
                            break

                    elif re.match(r'\W*\bIONS\b\W*:\W*Name\W+Z\W+Mass\b', self[k]):
                        startIons = True
                        self[k] = '>>>IONS<<<'

                    elif 'IONS : ' in self[k]:
                        ion_names = self[k].split(':')[1].split()
                        ions_list = []
                        for ion in map(lambda x: str(x).upper(), ion_names):
                            kk += 1
                            if ion not in ions_list:
                                therm_fast = 'therm'
                            else:
                                therm_fast = 'fast'
                            if ion == 'H':
                                ions[kk] = [ion, '1', '1', therm_fast]
                            elif ion == 'D':
                                ions[kk] = [ion, '1', '2', therm_fast]
                            elif ion == 'T':
                                ions[kk] = [ion, '1', '3', therm_fast]
                            elif ion == 'HE':
                                ions[kk] = [ion, '2', '4', therm_fast]
                            elif ion == 'LI':
                                ions[kk] = [ion, '3', '6', therm_fast]
                            elif ion == 'C':
                                ions[kk] = [ion, '6', '12', therm_fast]
                            else:
                                raise ValueError('%s is not yet programmed up' % ion)
                            ions[kk] = parse_ion_line(ions[kk])
                            ions_list.append(ion)
                            self[k] = '>>>IONS<<<'
                        break

            # this substitution is done for backwards compatibility towards old scripts
            for k in list(self.keys()):
                if re.match(header_ptrn, k) and self[k] == '>>>IONS<<<':
                    self[k] = '#                 IONS : ' + ' '.join([ions[i][0].lower() for i in list(ions.keys())])
                    break

            # parse header entries
            row = 0
            for line in lines:
                row = row + 1
                if re.match(r'#\s*rho.*rmin.*[(polflux)|(rmaj)].*q.*[(omega0)|(kappa)].*', line):
                    break
                if not len(line) or '#' in line[0]:
                    continue
                line = line.split('#')[0]  # remove any inline comment
                self[line.split('=')[0]] = namelist.interpreter(line.split('=')[1])

            # load raw data
            d = StringIO(str('\n'.join(lines[row:])))
            data = np.loadtxt(d)

            # always create all of the entries
            for k1, line in enumerate(self.profNames[self.latest_version]):
                for k2, var in enumerate(line):
                    self[var] = np.zeros(self['N_EXP'])

            # identify version
            self.version = self.latest_version
            if 'Ti_10' not in ''.join(lines):
                self.version = 0
            elif 'sbcx' not in ''.join(lines):
                self.version = 1
            vars_input_profiles = self.profNames[self.version]

            # load
            for k1, line in enumerate(vars_input_profiles):
                if self['N_EXP'] * (k1 + 1) > data.shape[0]:
                    break
                for k2, var in enumerate(line):
                    self[var] = data[self['N_EXP'] * k1 : self['N_EXP'] * (k1 + 1), k2]
            if 'NULL' in self:
                del self['NULL']

            # run consistency checks
            self.checks()

        else:
            raise ValueError('OMFITinputprofiles class cannot load this file type: %s' % self.filename)

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """
        header_ptrn = re.compile(r'^__header_.*__$')
        header = []
        for item in list(self.keys()):
            if re.match(header_ptrn, item):
                header.append(self[item])
        if len(header):
            header.append('')

        with open(self.filename, 'w') as f:

            # save input.profiles.extra files
            if (
                self.GACODEtype == 'extra'
                or np.all([k in self for k in self.extraNames])
                or re.match(r'input\.profiles\.extra.*$', os.path.split(self.filename)[1])
                or re.match(r'.*\.extra$', os.path.split(self.filename)[1])
            ):
                f.write('\n'.join(header))
                for entry in self.extraNames[self.latest_version]:
                    np.savetxt(f, self[entry], fmt=' % .7E')

            # save input.profiles.geo files
            elif (
                self.GACODEtype == 'geo'
                or re.match(r'input\.profiles\.geo.*$', os.path.split(self.filename)[1])
                or re.match(r'.*\.geo', os.path.split(self.filename)[1])
            ):
                if header[-1] == '':
                    header.pop()
                header.append('%13d\n' % (self['az'].shape[1] - 1))
                f.write('\n'.join(header))
                for i in range(len(self['ar'].flat)):
                    for k in ['ar', 'br', 'az', 'bz']:
                        f.write('% .13E\n' % self[k].flat[i])

            # save input.profiles files
            elif (
                self.GACODEtype == 'profiles'
                or np.all([k in self.profNames for k in list(self.keys())])
                or re.match(r'input\.profiles.*$', os.path.split(self.filename)[1])
                or re.match(r'.*\.profiles$', os.path.split(self.filename)[1])
            ):
                # if there are no comments, we are generating an input.profiles file from scratch
                if not len(header):
                    self.insert(0, '__header_0000__', '#                 IONS : ')
                # write header (handling ions)
                ions_found = False
                for ii, item in enumerate(self.keys()):
                    if re.match(header_ptrn, item) and 'IONS : ' in self[item]:
                        ions_found = True
                        f.write('#                 IONS :  Name       Z    Mass\n')
                        for k in self['IONS']:
                            f.write(
                                '#                         %s %d     %g [%s]\n'
                                % (self['IONS'][k][0].ljust(10), self['IONS'][k][1], self['IONS'][k][2], self['IONS'][k][3])
                            )
                    elif not isinstance(self[item], np.ndarray) and not isinstance(self[item], dict):
                        if not re.match(hide_ptrn, item):
                            f.write(item + '=' + str(self[item]) + '\n')
                        else:
                            if self[item] or not ii == len(self) - 1:
                                f.write(self[item] + '\n')
                if not ions_found:
                    raise RuntimeError('No header line in input.profile contains IONS comment! Cannot save.')

                # write
                for block in self.profNames[self.latest_version]:
                    f.write('#\n')
                    tmp = []
                    for item in block:
                        item = self.profNamesPretty[item][2]
                        tmp.append(item + ' ' * (16 - len(item)))
                    f.write('#' + ''.join(tmp)[:-1] + '\n')
                    for k in range(self['rho'].size):
                        tmp = []
                        for item in block:
                            if item != 'NULL':
                                data = self[item][k]
                            else:
                                data = 0.0
                            tmp.append(format(data, ' < 16.7E'))
                        f.write(''.join(tmp).rstrip() + '\n')
            else:
                raise ValueError('OMFITinputprofiles class cannot save this file type: %s' % self.filename)

    def sort(self):
        keys = sorted(list(self.keys()), key=lambda x: x.lower())
        for item in ['torfluxa', 'current', 'rcentr', 'bcentr', 'TIME', 'SHOT', 'N_EXP', 'IONS']:
            if item in keys:
                keys.pop(keys.index(item))
                keys = [item] + keys
        tmp = {}
        tmp.update(self)
        self.clear()
        for item in keys:
            self[item] = tmp[item]

    def consistent_derived(self):
        """
        Enforce consistency the same way input.gacode format would

        :return: self
        """
        self.calc_ptot(in_place=True)
        self.calc_pow(in_place=True)
        return self

    def inputgacode(self):
        """
        return a OMFITinputgacode object from the data contained in this object

        :return: OMFITinputgacode
        """
        ods = self.to_omas()
        return OMFITinputgacode('input.gacode').from_omas(ods)


class OMFITinputgacode(SortedDict, OMFITascii, Gapy, _gacode_profiles):
    def __init__(self, filename=None, input_profiles_compatibility_mode=True, **kw):
        if not os.path.basename(filename).startswith('input.gacode'):
            raise TypeError('Filename must start with input.gacode to be parsed by this class')
        SortedDict.__init__(self)
        if not input_profiles_compatibility_mode:
            kw['input_profiles_compatibility_mode'] = input_profiles_compatibility_mode
        OMFITascii.__init__(self, filename, **kw)
        self.init_profiles_names()
        self.GACODEtype = 'gacode'
        self.dynaLoad = True

    @property
    def input_profiles_compatibility_mode(self):
        return self.OMFITproperties.get('input_profiles_compatibility_mode', True)

    @input_profiles_compatibility_mode.setter
    def input_profiles_compatibility_mode(self, value):
        self.OMFITproperties['input_profiles_compatibility_mode'] = value

    @dynaLoad
    def load(self):
        if not os.stat(self.filename).st_size:
            return self
        content = self.read()
        if not all([k in content for k in ['nion', 'name', 'type', 'masse', 'mass', 'ze', 'z']]):
            raise OMFITexception('This does not appear to be an input.gacode file')
        # This is especially possible if input.gacode was formed from an input.profiles that was missing some information
        if 'rho' in content and 'polflux' in content and ('current' not in content or 'bcentr' not in content):
            raise OMFITexception('Cowardly refusing to attempt to use gapy to load input.gacode without bcentr and current info')
        self.clear()

        if self.filename is None or not os.stat(self.filename).st_size:
            return

        Gapy.load(self)

    @dynaLoad
    def sort(self):
        Gapy.sort(self)

    @dynaSave
    def save(self):
        Gapy.save(self)

    def __getitem__(self, key):
        # Mimic old input.profiles arrays full of zeros
        if key not in self and any(key.startswith(k) for k in ['ni_', 'Ti_', 'vtor_', 'vpol_']):
            return SortedDict.__getitem__(self, 'ne') * 0.0
        # print a warning and return 0 if these quantities are requested
        if key not in self and key in ['sbcx', 'sbeame']:
            return SortedDict.__getitem__(self, 'ne') * 0.0
        # return the requested quantity
        return SortedDict.__getitem__(self, key)

    def inputprofiles(self, via_omas=False):
        """
        return a OMFITinputprofiles object from the data contained in this object

        :param via_omas: make the transformation via OMAS

        :return: OMFITinputprofiles
        """
        if via_omas:
            ods = self.to_omas()
            return OMFITinputprofiles('input.profiles').from_omas(ods)
        else:
            tmp = OMFITinputprofiles('input.profiles')
            tmp.load()  # to remove dynaLoad
            for block in [['IONS', 'N_EXP', 'N_ION', 'BT_EXP', 'IP_EXP', 'ARHO_EXP', 'RVBV']] + tmp.profNames[tmp.latest_version]:
                for item in block:
                    if item in ['NULL']:
                        continue
                    elif item not in self:
                        tmp[item] = self['rho'] * 0.0
                    else:
                        tmp[item] = self[item]
        return tmp

    def inputtglf(self, irhos=None, inputtglf_objects=True):
        """
        Evaluate TGLF input parameters at given radii

        :param irho: indices of desired input.tglf files. If None, return for all radii.

        :param inputtglf_objects: if true create OMFITinputglf objects else use simple dictionaries

        :return: dictionary of input.tglf objects for each grid point in this object
        """
        e = 4.8032e-10
        k = 1.6022e-12
        me = 9.1094e-28
        mi = self['IONS'][1][2] * 1.6726e-24
        c = 2.9979e10
        m_to_cm = 1e2
        T_to_Gauss = 1e4

        a = self['rmin'][-1] * m_to_cm
        rmin = self['rmin'] * m_to_cm
        one = np.ones(len(rmin))
        one_int = np.ones(len(rmin), dtype=int)
        q = self['q']
        Te = self['Te'] * 1e3
        ne = self['ne'] * 1e13

        bunit = T_to_Gauss * self['bunit']
        input_tglf = {}

        signb = np.sign(self['BT_EXP'])
        signq = np.sign(self['q'])
        input_tglf['SIGN_BT'] = -signb * one_int
        input_tglf['SIGN_IT'] = -signb * signq * one_int

        input_tglf['NS'] = (self['N_ION'] + 1) * one_int
        input_tglf['MASS_1'] = me / mi * one
        input_tglf['TAUS_1'] = 1.0 * one
        input_tglf['AS_1'] = 1.0 * one
        input_tglf['ZS_1'] = -1 * one
        input_tglf['RLNS_1'] = a / m_to_cm * self['dlnnedr']
        input_tglf['RLTS_1'] = a / m_to_cm * self['dlntedr']

        c_s = np.sqrt(k * Te / mi)
        input_tglf['VPAR_1'] = -input_tglf['SIGN_IT'] * (a / c_s) * self['mach']
        input_tglf['VPAR_SHEAR_1'] = -input_tglf['SIGN_IT'] * (a / c_s) * self['gamma_p']

        AS_ions = 0.0
        for i in range(2, self['N_ION'] + 2):
            input_tglf['MASS_' + str(i)] = self['IONS'][i - 1][2] // self['IONS'][1][2] * one
            input_tglf['ZS_' + str(i)] = self['IONS'][i - 1][1] * one
            input_tglf['TAUS_' + str(i)] = self['Ti_' + str(i - 1)] / self['Te']
            input_tglf['AS_' + str(i)] = self['ni_' + str(i - 1)] / self['ne']
            input_tglf['VPAR_' + str(i)] = -input_tglf['SIGN_IT'] * (a / c_s) * self['mach']
            input_tglf['VPAR_SHEAR_' + str(i)] = -input_tglf['SIGN_IT'] * (a / c_s) * self['gamma_p']
            input_tglf['RLNS_' + str(i)] = a / m_to_cm * self['dlnnidr_' + str(i - 1)]
            input_tglf['RLTS_' + str(i)] = a / m_to_cm * self['dlntidr_' + str(i - 1)]
            AS_ions += input_tglf['AS_' + str(i)]

        input_tglf['BETAE'] = 8.0 * np.pi * ne * k * Te / bunit ** 2
        loglam = 24.0 - np.log(np.sqrt(ne) / (Te))
        input_tglf['XNUE'] = a / c_s * np.sqrt(self['IONS'][1][2]) * e ** 4 * np.pi * ne * loglam / (np.sqrt(me) * (k * Te) ** 1.5)
        input_tglf['ZEFF'] = zeff = self['z_eff']
        rho_s = c_s / (e * np.abs(bunit) / (mi * c))
        input_tglf['DEBYE'] = 7.43e2 * np.sqrt(Te / (ne)) / rho_s

        input_tglf['VEXB_SHEAR'] = -input_tglf['SIGN_IT'] * self['w0p'] * (a / c_s)

        input_tglf['RMIN_LOC'] = self['rmin'] * m_to_cm / a
        input_tglf['RMAJ_LOC'] = self['rmaj'] * m_to_cm / a
        input_tglf['ZMAJ_LOC'] = self['zmag'] * m_to_cm / a
        input_tglf['DRMINDX_LOC'] = 1.0 * one
        input_tglf['DRMAJDX_LOC'] = self['drmaj']
        input_tglf['DZMAJDX_LOC'] = self['dzmag']

        input_tglf['Q_LOC'] = np.abs(q)
        input_tglf['KAPPA_LOC'] = self['kappa']
        input_tglf['S_KAPPA_LOC'] = self['skappa']
        input_tglf['DELTA_LOC'] = self['delta']
        input_tglf['S_DELTA_LOC'] = self['sdelta']
        input_tglf['ZETA_LOC'] = self['zeta']
        input_tglf['S_ZETA_LOC'] = self['szeta']

        press = self['ptot']
        Pa_to_dyn = 10.0
        dpdr = np.gradient(press * Pa_to_dyn, rmin)
        dqdr = np.gradient(q, rmin)
        input_tglf['P_PRIME_LOC'] = np.zeros(rmin.shape)  # avoid division by zero
        input_tglf['P_PRIME_LOC'][1:] = -q[1:] / (rmin[1:] / a) ** 2 * rmin[1:] / bunit[1:] ** 2 * dpdr[1:]
        input_tglf['P_PRIME_LOC'][0] = input_tglf['P_PRIME_LOC'][1]
        s = rmin / q * dqdr
        input_tglf['Q_PRIME_LOC'] = np.zeros(rmin.shape)  # avoid division by zero
        input_tglf['Q_PRIME_LOC'][1:] = q[1:] ** 2 * a ** 2 / rmin[1:] ** 2 * s[1:]
        input_tglf['Q_PRIME_LOC'][0] = input_tglf['Q_PRIME_LOC'][1]
        q_gb = ne * k * Te * c_s * (rho_s / a) ** 2 * 1.0e-7

        if irhos is None:
            irhos = np.arange(len(self['rho']))
        irhos = np.atleast_1d(irhos)

        all_tglfs = SortedDict()
        for irho in irhos:
            rho = self['rho'][irho]
            if inputtglf_objects:
                all_tglfs[rho] = OMFITgacode(GACODEtype='tglf', filename='input.tglf')
            else:
                all_tglfs[rho] = dict()
            for item in input_tglf:
                all_tglfs[rho][item] = input_tglf[item][irho]

        return all_tglfs


# OMAS extra_structures
# omega0 is kept for backward compatibility
_extra_structures = {
    'core_profiles': {
        "core_profiles.profiles_1d[:].omega0": {
            "coordinates": ["core_profiles.profiles_1d[:].grid.rho_tor_norm"],
            "data_type": "FLT_1D",
            "documentation": "Plasma rotation",
            "full_path": "core_profiles/profiles_1d(itime)/omega0(:)",
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

############################################
if '__main__' == __name__:
    test_classes_main_header()

    import warnings

    warnings.simplefilter("error")

    if False:
        print('=' * 20)
        from pygacode.test import test_install

        print('=' * 20)

    # make a copy of the sample input.gacode in the current working directory
    OMFITascii(OMFITsrc + '/../samples/input.gacode').deploy('input.gacode')

    # check from_omas and to_omas
    tmp = OMFITinputgacode('input.gacode')
    ods = tmp.to_omas()
    tmp0 = OMFITinputgacode('input.gacode0')
    tmp0.from_omas(ods)

    if False:
        # plot
        from matplotlib import pyplot

        axs = tmp.plot(pretty_names=False)
        tmp0.plot(color='r', axs=axs, pretty_names=False)
        pyplot.show()

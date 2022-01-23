__all__ = ['Gapy']

import sys
import numpy as np
import re
import os
from collections import OrderedDict
import copy
import tempfile
import warnings

try:
    from pygacode import expro
    from gacode_ext import expro_compute_derived

except ImportError as _excp:
    gapy_error = _excp

    class Gapy:
        def load(self):
            raise gapy_error

    warnings.warn('No `gacode` support: ' + repr(_excp))
else:

    class IONS(OrderedDict):
        def sort(self, *args, **kw):
            tmp = copy.copy(self)
            self.clear()
            for k in sorted(tmp, *args, **kw):
                self[k] = tmp[k]
            return self

    def gapystr_get(s):
        tmp = s.T.flatten()
        if sys.version_info[0] > 2:
            return ''.join(list(map(lambda x: str(x, 'utf-8'), tmp))).split()
        else:
            return ''.join(list(map(lambda x: str(x), tmp))).split()

    def gapystr_set(s, n=10):
        return [item.ljust(n) for item in s + [''] * 20][:20]

    def sort_key(x):
        if re.match('[a-zA-Z]+_[0-9]+', x):
            x = x.split('_')
            x = '%s_%02d' % (x[0], int(x[1]))
        return x.lower()

    class Gapy(dict):
        def __init__(self, filename, input_profiles_compatibility_mode=True):
            self.filename = filename
            self.input_profiles_compatibility_mode = input_profiles_compatibility_mode
            self.load()

        def load(self):
            """
            Load data in memory from file

            :return: self
            """
            if self.filename is None or not os.stat(self.filename).st_size:
                return
            expro.expro_read(self.filename)
            self.load_from_expro()
            self.consistent_derived()
            return self

        def expro_clear(self):
            """
            Clear (sets to zero) all data in expro

            :return: self
            """
            for item in gapystr_get(expro.expro_list):
                tmp = getattr(expro, 'expro_' + item)
                setattr(expro, 'expro_' + item, np.zeros(tmp.shape).astype(tmp.dtype))
            return self

        def expro_init_via_file(self, nexp, nion):
            """
            Initialize expro arrays to be n_ion X n_exp elements long

            :param n_exp: number of radial array elements

            :param n_ion: number of ions

            :return: self
            """
            zero_float = ' 0.0000000E+00'
            empty = '''#  *original : null
# *statefile : null
#     *gfile : null
#   *cerfile : null
#      *vgen : null
#     *tgyro : null
#
# nexp
{nexp}
# nion
{nion}
# name
{ion_names}
# type
{ion_types}
# masse
{zero_float}
# mass
{zero_array}
# ze
{zero_array}
# z
{zero_array}
# torfluxa | Wb/radian
 1.0
'''.format(
                nexp=nexp,
                nion=nion,
                zero_array=zero_float * nion,
                zero_float=zero_float,
                ion_names=' D' * nion,
                ion_types=' [therm]' * nion,
            )
            filename = tempfile._get_default_tempdir() + '/input.gacode_empty_%d' % nexp
            with open(filename, 'w') as f:
                f.write(empty)
            expro.expro_read(filename)
            return self

        def expro_init(self, n_exp, n_ion):
            """
            Initialize expro arrays to be n_ion X n_exp elements long

            :param n_exp: number of radial array elements

            :param n_ion: number of ions

            :return: self
            """
            if expro.expro_mass is not None:
                expro.expro_init(0)
            expro.expro_n_exp = n_exp
            expro.expro_n_ion = 10
            expro.expro_init(1)
            expro.expro_list_set()
            return self

        def load_from_expro(self):
            """
            Load data from exrpo to memory

            :return: self
            """
            lst = gapystr_get(expro.expro_list)

            # Define Gapy class members corresponding to list[]
            for item in lst:
                self[item] = getattr(expro, 'expro_' + item).copy()

            # Species name and type
            self['name'] = gapystr_get(expro.expro_name)
            self['type'] = gapystr_get(expro.expro_type)

            # refactor output to be compatible with input.profiles format
            if self.input_profiles_compatibility_mode:
                # capitalize some entries
                for item in ['n_exp', 'shot', 'time', 'n_ion']:
                    tmp = np.atleast_1d(self[item])[0]
                    del self[item]
                    self[item.upper()] = tmp
                # input.profiles Te and Ti are capitalized
                self['Te'] = self['te']
                del self['te']
                self['Ti'] = self['ti']
                del self['ti']
                self['omega0'] = self['w0']
                del self['w0']
                self['BT_EXP'] = self['bcentr']
                self['RVBV'] = self['rcentr'] * self['bcentr']
                del self['rcentr']
                del self['bcentr']
                self['IP_EXP'] = self['current']
                del self['current']
                if self['BT_EXP'] != 0.0:
                    self['ARHO_EXP'] = np.sqrt(np.abs(self['torfluxa'] * 2 / self['BT_EXP']))
                else:
                    self['ARHO_EXP'] = 1.0
                del self['torfluxa']
                for item in ['qpar_wall', 'qpar_beam', 'flow_wall', 'flow_beam']:
                    self[item] = self[item] / 0.624e22
                # input.profiles entries are split per ion species
                for item in list(self.keys()):
                    if isinstance(self[item], np.ndarray) and len(self[item].shape) > 1:
                        for k in range(self['N_ION']):
                            if k < self[item].shape[0]:
                                self[item + '_%d' % (k + 1)] = self[item][k]
                            else:
                                self[item + '_%d' % (k + 1)] = self['rho'] * 0.0
                        del self[item]
                # input.profiles ions infos are collected under the IONS structure
                self['IONS'] = IONS()
                for k in range(self['N_ION']):
                    self['IONS'][k + 1] = [self['name'][k], self['z'][k], self['mass'][k], self['type'][k].strip('[]')]
                del self['name']
                del self['type']
                del self['z']
                del self['mass']
                # use floats and ints rather than 0D numpy arrays
                for item in self:
                    if isinstance(self[item], np.ndarray) and not len(self[item].shape):
                        self[item] = self[item].item()
            self.sort()
            return self

        def save_to_expro(self):
            """
            Write data in memory to exrpo

            :return: self
            """
            if not self.input_profiles_compatibility_mode:
                self.expro_init(np.atleast_1d(self['n_exp'])[0], np.atleast_1d(self['n_ion'])[0])
                for item in sorted(list(self.keys()), key=sort_key):
                    expro_item = item
                    expro_value = self[item]
                    if expro_item in gapystr_get(expro.expro_list):
                        setattr(expro, 'expro_' + expro_item, expro_value)
            else:
                self.expro_init(len(self['rho']), len(self['IONS']))
                # write single arrays and collate items
                collated = {}
                for item in sorted(list(self.keys()), key=sort_key):
                    if item == 'IONS':
                        continue
                    expro_item = item
                    expro_value = self[item]
                    if item in ['N_EXP', 'SHOT', 'TIME', 'Te']:
                        expro_item = item.lower()
                    if item == 'omega0':
                        expro_item = 'w0'
                    if item == 'BT_EXP':
                        expro_item = 'bcentr'
                    if item == 'IP_EXP':
                        expro_item = 'current'
                    if item == 'RVBV' and 'BT_EXP' in self:
                        expro_value = self['RVBV'] / self['BT_EXP']
                        expro_item = 'rcentr'
                    if item == 'ARHO_EXP':
                        expro_item = 'torfluxa'
                        expro_value = 0.5 * self['BT_EXP'] * self['ARHO_EXP'] ** 2
                    if item in ['qpar_wall', 'qpar_beam', 'flow_wall', 'flow_beam']:
                        expro_value = expro_value * 0.624e22
                    if re.match('[a-zA-Z]+_[0-9]+', item):
                        expro_item = item.split('_')
                        collated.setdefault(expro_item[0].lower(), []).append(self[item])
                        continue
                    elif expro_item in ['name', 'type']:
                        getattr(expro, 'expro_' + expro_item)[:] = gapystr_set(expro_value)
                        continue
                    if expro_item in gapystr_get(expro.expro_list):
                        setattr(expro, 'expro_' + expro_item, expro_value)
                    elif '__header_' not in item and item not in ['N_ION', 'sbeame', 'sbcx']:
                        print('UNSET: ' + item)
                # manage collated items
                for expro_item in collated:
                    if expro_item in gapystr_get(expro.expro_list):
                        tmp = np.array(copy.deepcopy(collated[expro_item]))[: len(self['IONS']), :]
                        setattr(expro, 'expro_' + expro_item, tmp)
                # manage IONS
                for item_n, expro_item in enumerate(['name', 'z', 'mass', 'type']):
                    expro_value = [
                        '[%s]' % self['IONS'][k][item_n] if expro_item == 'type' else self['IONS'][k][item_n] for k in self['IONS']
                    ]
                    if expro_item in ['name', 'type']:
                        getattr(expro, 'expro_' + expro_item)[:] = gapystr_set(expro_value)
                        continue
                    setattr(expro, 'expro_' + expro_item, expro_value)
                setattr(expro, 'expro_n_ion', len(self['IONS']))
            return self

        def save(self):
            """
            Save data from memory to file

            :return: self
            """
            self.save_to_expro()
            # write input.gacode file
            expro.expro_write(self.filename)
            return self

        def consistent_derived(self):
            """
            Update derived quantities and make them self-consitent with fundamental input.gacode quantities

            :return: self
            """
            self.save_to_expro()
            expro_compute_derived()
            self.load_from_expro()
            return self

        def sort(self):
            """
            Sort alphabetically independent of capitalization and consistent with subscript numbering

            :return: self
            """
            keys = sorted(list(self.keys()), key=sort_key)
            # place some elements at the top of the input.profiles
            for item in ['torfluxa', 'current', 'rcentr', 'bcentr', 'TIME', 'SHOT', 'N_EXP', 'IONS']:
                if item in keys:
                    keys.pop(keys.index(item))
                    keys = [item] + keys
            # recreate dictionary with the correct sorting
            tmp = {}
            tmp.update(self)
            self.clear()
            for item in keys:
                self[item] = tmp[item]


# --------------------------
if '__main__' in __name__:
    import pygacode

    for compatibility_mode in [False, True]:
        for times in range(2):
            tmp = Gapy(os.environ['GACODE_ROOT'] + '/tgyro/tools/input/treg01/input.gacode', compatibility_mode)
            print(tmp.keys())
            tmp.save()

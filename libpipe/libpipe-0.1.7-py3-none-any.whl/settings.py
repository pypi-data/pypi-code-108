# Handle setting
#
# Author: F. Mertens

import os
import shutil
from collections import OrderedDict

import toml

from . import attrmap, futils


class BaseSettings(attrmap.AttrMap):

    DEFAULT_SETTINGS = None

    def __init__(self, file, d):
        attrmap.AttrMap.__init__(self, d)
        self.set_file(file)

    def _build(self, obj):
        if isinstance(obj, attrmap.Mapping):
            obj = self.__class__(self.get_file(), obj)

        return obj

    def set_file(self, file):
        self._setattr('_file', os.path.abspath(file) if file else file)

    def get_file(self):
        return self._file

    def get_path(self, key):
        path = self.get(key)
        if path:
            path = os.path.expanduser(path)
            if not os.path.isabs(path):
                if self.get_file():
                    path = os.path.join(os.path.dirname(self.get_file()), path)
                else:
                    path = os.path.abspath(path)
        return path

    def validate_keys(self, max_depth=2):
        sd = self.get_defaults()
        invalid_keys = set(self.all_keys()) - set(sd.all_keys())
        if invalid_keys and min([len(k.split('.')) for k in invalid_keys]) <= max_depth:
            print(f'Warning: invalid keys: {",".join(invalid_keys)}')
            return False
        return True

    @classmethod
    def load(cls, file, check_args=True):
        s = cls(file, toml.load(file, _dict=OrderedDict))
        if check_args:
            s.validate_keys()

        return s

    @classmethod
    def load_with_defaults(cls, file, with_type_keyword=False, check_args=True):
        c_file = cls.load(file, check_args=check_args)
        c_default = cls.get_defaults()

        if 'default_settings' in c_file and c_file.default_settings:
            c_default += cls.load(c_file.get_path('default_settings'), check_args=check_args)

        if not with_type_keyword:
            s = c_default + c_file
        else:
            for k, v in c_file.items():
                if isinstance(v, dict):
                    if 'type' in v.keys():
                        t = v['type']
                    else:
                        t = k
                    if t not in c_default.keys():
                        print(f'Warning: no default for section {k} of type {t}')
                        continue
                    t_default = c_default[t]
                    c_file[k] = attrmap.AttrMap(t_default) + attrmap.AttrMap(v)
            s = c_file

        s.set_file(file)
        return s

    @classmethod
    def get_defaults(cls):
        return cls.load(cls.DEFAULT_SETTINGS, check_args=False)

    def get_root_settings_file(self):
        s = self
        while s.default_settings:
            s = self.load(s.get_path('default_settings'), check_args=False)
        return s.get_file()

    @classmethod
    def load_from_string(cls, s, check_args=True):
        if isinstance(s, (list, tuple)):
            s = '\n'.join(s)
        d = toml.loads(s)

        s = cls(None, d)
        if check_args:
            s.validate_keys()

        return s

    def save(self, file=None, strip_parents_keys=False):
        if not file:
            file = self.get_file()
        if not file:
            print('Error: No target filename to save settings.')
        else:
            m = self._mapping.copy()
            if strip_parents_keys and os.path.isfile(self.get_path('default_settings')):
                s_parent = self.__class__.load(self.default_settings)
                m = m - s_parent
            with open(file, mode='w') as f:
                toml.dump(dict(m), f)

    def duplicate(self, out_file, copy_parset_files=False, strip_parents_keys=False, **config_modifiers):
        s_out = self.copy()
        s_out.set_file(out_file)
        s_out['default_settings'] = ''

        cur_dir = os.path.dirname(self.get_file()) if self.get_file() else os.getcwd()
        new_dir = os.path.dirname(s_out.get_file()) if s_out.get_file() else os.getcwd()

        if new_dir and not os.path.exists(new_dir):
            os.makedirs(new_dir)

        if cur_dir != new_dir:
            if not os.path.isabs(s_out.data_dir):
                s_out['data_dir'] = os.path.join(cur_dir, s_out.data_dir)
            for p, k, v in s_out.all_items():
                if isinstance(v, str) and v.endswith('.parset') and not os.path.isabs(v):
                    if copy_parset_files:
                        futils.mkdir(os.path.join(new_dir, os.path.dirname(v)))
                        shutil.copyfile(os.path.join(cur_dir, v), os.path.join(new_dir, v))
                    elif not os.path.isabs(v):
                        p[k.split('.')[-1]] = os.path.join(cur_dir, v)

        if config_modifiers:
            s_out = s_out + config_modifiers

        s_out.save(strip_parents_keys=strip_parents_keys)

        return s_out

    def validate(self, module):
        try:
            assert module in self

            def val_fct(v, k, m=module):
                assert v, f'{m}.{k}={getattr(self, m)[k]} is invalid'
            getattr(self, f'validate_{module}')(val_fct)

        except AssertionError as error:
            print(f'Error: {error}')
            return False
        except ValueError as error:
            print(f'Error: {error}')
            return False

        return True

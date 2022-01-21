import argparse
from copy import deepcopy
import json, jsonpickle

class simpcfg():

    __slots__ = ('cfg', 'dflt', 'tb', 'trace_lvl', 'other_values', 'usage',\
                    'track_rqrmnts', 'rqrmnts', 'warn_dflt', 'track_usage')

    def __init__(self, **kargs):

        # Parameters
        self.cfg = {}                # Stores user provided configuration
        self.dflt = {}               # Stores default values used
        self.warn_dflt = kargs.get('warn_dflt', False)

        # Requirements
        self.track_rqrmnts = kargs.get('track_rqrmnts', False)
        if self.track_rqrmnts:
            self.rqrmnts = {}
        else:
            self.rqrmnts = None

        # Track Usage
        self.track_usage = kargs.get('track_usage', False)
        if self.track_usage:
            self.usage = {}
        else:
            self.usage = {}

        # ToolBox (saves classes)
        self.tb = None

        # trace_lvl is the
        self.trace_lvl = kargs.get('trace_lvl', 0)

        # Other Values (Saves values)
        self.other_values = None

    # Access Fxns
    def get(self, key, **kargs):

        # Add requirements
        if self.track_rqrmnts:
            self.rqrments[key] = self.rqrmnts.get(key, [])
            self.rqrments[key].append(kargs)

        # Tracks number of calls
        if self.track_usage:
            self.usage[key] = self.usage.get(key, 0) + 1

        # Try to get the value or fall back on the default value (if provided)
        try:
            try:
                item = self.cfg.__getitem__(key)
            except KeyError:
                item = self.dflt.__getitem__(key)
        except KeyError:
            if 'dflt' in kargs:
                if not kargs.get('verify_dflt', True):
                    return self.get_default(key, kargs.get('dflt'))
                item = self.get_default(key, kargs.get('dflt'))
            else:
                raise KeyError(f'{key} not submitted as a parameter value')

        # If None is always okay, don't bother with rest of requirements
        if kargs.get('None_always_okay', False) and item is None:
            return None

        # Check other requirements
        if 'options' in kargs:
            self.check_options(key, item, kargs.get('options'))

        if 'dtype' in kargs:
            self.check_dtype(key, item, kargs.get('dtype'))

        if 'min' in kargs:
            self.check_min(key, item, kargs.get('min'), \
                    min_inclusive=kargs.get('min_inclusive', True))

        if 'max' in kargs:
            self.check_max(key, item, kargs.get('max'), \
                    max_inclusive=kargs.get('max_inclusive', True))

        if 'callable' in kargs:
            self.check_callable(key, item, kargs.get('callable'))

        return item
    def __getitem__(self, key):
        return self.get(key)
    def __setitem__(self, key,item):
        self.cfg.__setitem__(key, item)
    def remove_param(self, key):
        if key in self.cfg:
            del self.cfg[key]
        if key in self.dflt:
            del self.dflt[key]
    def __delitem__(self, key):
        self.remove_param(key)

    ''' Access other dictionaries '''
    # Allows access to default
    def set_dflt(self, key, default_val):
        self.dflt[key] = default_val
    def get_dflt(self, key):
        try:
            return self.dflt[key]
        except KeyError:
            raise KeyError(f'{key} does not have a default value set')
    def del_dflt(self, key):
        try:
            del self.dflt[key]
        except KeyError:
            return
    # Allows access to values
    def save_value(self, key, val):
        self.other_vals[key] = val
    def get_value(self, key):
        try:
            return self.other_vals[key]
        except KeyError:
            raise KeyError(f'No value saved for {key}')
    def del_value(self, key):
        try:
            del self.other_vals[key]
        except KeyError:
            return
    # Allows access to toolbox
    def add_to_toolbox(self, key, val):
        self.tb[key] = val
    def get_from_toolbox(self, key):
        try:
            return self.tb[key]
        except KeyError:
            raise KeyError(f'{key} is not in the toolbox')
    def create_instance(key, *args, **kargs):
        return self.get_from_toolbox(key)(*args, **kargs)
    def del_from_toolbox(self, key):
        try:
            del self.tb[key]
        except KeyError:
            return
    ''' Import / Export data '''
    # Exports all data saved in config
    def export_data(self):
        values = {'user_input':self.cfg, \
                  'dflt_vals':self.dflt, \
                  'other_vals':self.other_vals,\
                  'cfg_params':self.get_cfg_params()}
        if self.track_rqrmnts:
            values['rqrmnts'] = self.rqrmnts
        if self.track_usage:
            values['usage'] = self.usage
        return values
    def get_cfg_params(self):
        return {'warn_dflt':self.warn_dflt, 'track_rqrmnts':self.track_rqrmnts,\
                'track_usage':self.track_usage, 'trace_lvl':self.trace_lvl}
    def set_cfg_params(self, *args, **kargs):
        if len(args) == 1 and len(kargs) == 0:
            if isinstance(args[0], dict):
                self.warn_dflt = args[0].get('warn_dflt', self.warn_dflt)
                self.track_rqrmnts = args[0].get('track_rqrmnts', \
                                                        self.track_rqrmnts)
                self.track_usage = args[0].get('track_usage', self.track_usage)
                self.trace_lvl = args[0].get('trace_lvl', self.trace_lvl)
            else:
                raise TypeError('Must provide a dictionary or kargs, '+\
                                        f'not {type(args[0])}')
        elif len(args) == 0 and len(kargs) > 0:
            self.warn_dflt = kargs.get('warn_dflt', self.warn_dflt)
            self.track_rqrmnts = kargs.get('track_rqrmnts', self.track_rqrmnts)
            self.track_usage = kargs.get('track_usage', self.track_usage)
            self.trace_lvl = kargs.get('trace_lvl', self.trace_lvl)
        elif len(args) > 1:
            raise ValueError('Cannot pass multiple dictionaries at once')
        elif len(args) > 0 and len(kargs) > 0:
            raise ValueError('Either provide dictionary of params or kargs,'+\
                                    ' not both')
        elif len(args) == 0 and len(kargs) == 0:
            raise ValueError('Need to provide a dictionary or kargs')
        else:
            raise Error('Must provide either singular dictionary as '+\
                            'positional argument or kargs')
    # Loads parameters from dictionary
    def load_dict(self, param_dict):
        self.cfg = param_dict.get('user_input', {})
        self.dflt = param_dict.get('dflt', {})
    def to_dict(self):
        return {'user_input':deepcopy(self.cfg), 'dflt':deepcopy(self.dflt)}
    def set_params(self, *args, **kargs):
        if len(args) == 1 and len(kargs) == 0:
            if isinstance(args[0], dict):
                self.cfg.update(args[0])
            else:
                raise TypeError('Must provide a dictionary or kargs, '+\
                                        f'not {type(args[0])}')
        elif len(args) == 0 and len(kargs) > 0:
            self.cfg.update(kargs)
        elif len(args) > 1:
            raise ValueError('Cannot pass multiple dictionaries at once')
        elif len(args) > 0 and len(kargs) > 0:
            raise ValueError('Either provide dictionary of params or kargs,'+\
                                    ' not both')
        elif len(args) == 0 and len(kargs) == 0:
            raise ValueError('Need to provide a dictionary or kargs')
        else:
            raise Error('Must provide either singular dictionary as '+\
                            'positional argument or kargs')
    def __str__(self):
        return self.to_dict().__str__()
    def __repr__(self):
        return self.export_data().__str__()
    # Allows to save as json or as pickle
    def load_jsonfile(self, file_path, use_jsonpickle=True):
        with open(file_path, 'r') as F:
            if use_jsonpickle:
                self.load_dict(jsonpickle.load(F))
            else:
                self.load_dict(json.load(F))
    def save_jsonfile(self, file_path, use_jsonpickle=True):
        with open(file_path, 'w') as F:
            if use_jsonpickle:
                jsonpickle.dump(F, self.to_dict())
    def load_picklefile(self, file_path):
        with open(file_path, 'rb') as F:
            self.load_dict(pickle.load(F))
    def save_picklefile(self, file_path):
        with open(file_path, 'wb') as F:
            pickle.dump(F, self.to_dict())

    ''' Verification Fxns '''

    # Returns default value
    #   Whatever the first default value is for this will determine what value
    #   will be called in future calls regardless if the default is different
    #   when called again
    def get_default(self, key, default_val):
        if self.warn_dflt:
            print(f'Warning: {key} was not submitted,'+\
                                    f' defaulted to {default_val}')
        if key in self.dflt:
            return self.dflt[key]
        else:
            self.dflt[key] = default_val
            return default_val

    # Raises error if not a correct option
    def check_options(self, key, item, options):
        if not isinstance(options, (tuple, list, set)):
            options = tuple(options)
        if item not in options:
            raise ValueError(f'Received {item} for {key} but expected one of'+\
                    f'the following options:\n{options}')
        return

    # Raises error if not an appropriate dtype
    def check_dtype(self, key, item, dtype):
        if not isinstance(key, dtype):
            if isinstance(dtype, (list, tuple, set)):
                raise TypeError(f'Received type {type(item)} for {key} but ' + \
                        f'expected one of the following types:\n{dtype}')
            else:
                raise TypeError(f'Received type {type(item)} for {key} but ' + \
                        f'expected {dtype}')

    # Raises an error if below min
    def check_min(self, item, min, min_inclusive=True):
        if min_inclusive and item < min:
            raise ValueError(f'Received {item} for {key} below the inclusive '+\
                    f'min ({min})')
        elif not min_inclusive and item <= min:
            raise ValueError(f'Received {item} for {key} below the '+\
                    f'non-inclusive min ({min})')

    # Raises an error if greater than max
    def check_max(self, item, max, max_inclusive=True):
        if max_inclusive and item > max:
            raise ValueError(f'Received {item} for {key} above the inclusive '+\
                    f'max ({max})')
        elif not max_inclusive and item <= max:
            raise ValueError(f'Received {item} for {key} below the '+\
                    f'non-inclusive max ({max})')

    # Raises an error if doesn't match whether it should be callable
    def check_callable(self, key, item, should_be_callable):
        if not (callable(item) == should_be_callable):
            if should_be_callable:
                raise ValueError(f'Received {item} for {key},'+\
                        ' but it is not callable')
            raise ValueError(f'Received {item} for {key}, but it is '+\
                    'callable when it shouldn\'t be')

    ''' Other '''
    def __contains__(self, key):
        return self.cfg.__contains__(key) or self.dflt.__contains__(key)
    def __hash__(self):
        return self.to_set().__hash__()
    def __eq__(self, other):
        if isinstance(other, dict):
            return (self.to_frozen_set() != frozenset([(key,temp.get(key)) for \
                                                        key in other.keys()]))
        elif isinstance(other, simpcfg):
            return (self.to_frozen_set() == other.to_frozen_set())
        elif isinstance(other, (tuple, list, set)):
            return (self.to_frozen_set() != frozenset(other))
        else:
            return False
    def to_tuple(self):
        temp = self.__combine_cfg_and_dflt__()
        return tuple([(key,temp.get(key)) for key in self.keys(sorted=True)])
    def to_set(self):
        temp = self.__combine_cfg_and_dflt__()
        return set([(key,temp.get(key)) for key in self.keys(sorted=True)])
    def to_frozen_set(self):
        temp = self.__combine_cfg_and_dflt__()
        return frozenset([(key,temp.get(key)) for key in self.keys(sorted=True)])

    def __iter__(self):
        return self.__combine_cfg_and_dflt__().__iter__()
    def __len__(self):
        return self.__combine_cfg_and_dflt__().__len__()
    def __combine_cfg_and_dflt__(self):
        temp = {**self.dflt}.update(self.cfg)
        return temp

    def items(self):
        return self.__combine_cfg_and_dflt__().items()

    def keys(self, sorted=False):
        if sorted:
            return sorted(self.__combine_cfg_and_dflt__().keys())
        return self.__combine_cfg_and_dflt__().keys()

"""
Module for storing option defaults and handling levels of
control
"""
from __future__ import print_function
import logging
from exoedge import logger

LOG = logger.getLogger(__name__)


class TypeConverter(object):
    def __init__(self, _type):
        self._type = _type

    def convert(self, value):
        if value is None:
            return None
        else:
            return getattr(self, '_like_' + self._type.__name__)(value)

    def _like_str(self, v):
        if isinstance(v, str):
            return v
        else:
            return str(v)

    def _like_list(self, v):
        if isinstance(v, list):
            return v
        elif isinstance(v, str):
            return v.split(',')
        else:
            return [v]

    def _like_bool(self, v):
        if isinstance(v, bool):
            return v
        elif isinstance(v, str) and v in ['False', 'false', 'f', 'F', '0']:
            return False
        else:
            return bool(v)

    def _like_int(self, v):
        if isinstance(v, int):
            return v
        else:
            try:
                return int(v)
            except ValueError:
                return int()

    def _like_dict(self, v):
        if isinstance(v, dict):
            return v
        elif isinstance(v, str):
            try:
                return {_v.split(':')[0]:_v.split(':')[1] for _v in v.split(',')}
            except IndexError:
                return dict()


class OptionsHandler(object):
    def __init__(self,
                 precedence,
                 option_type_map,
                 option_name_map,
                 **kwargs):
        """
        Each value in kwargs is expected to be a dictionary.
        """
        self.precedence = [x for x in precedence if x in kwargs]
        self.option_type_map = option_type_map
        self.option_name_map = {k:v for k, v in option_name_map.items() if k in kwargs}
        self.opt_vals = kwargs

        self.values = self.honor_precedence()

    def _stack_params(self):
        param_stack = {}

        for _option, _type in self.option_type_map.items():
            option_stack = {}
            TC = TypeConverter(_type)

            for _option_source, _fn in self.option_name_map.items():
                _v = TC.convert(_fn(self.opt_vals.get(_option_source, None), _option))
                option_stack.update({_option_source: _v})

            param_stack.update({_option: option_stack})

        return param_stack

    def honor_precedence(self):
        param_stack = self._stack_params()
        _values = {}

        for option, stack in param_stack.items():
            _v = ([stack[_src] for _src in self.precedence if stack[_src] is not None] or [None])[0]
            _values.update({option: _v})

        return _values

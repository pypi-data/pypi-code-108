from typing import Optional, Union, Dict, List
import os
import re
import copy
import glob
import itertools

import numpy as np

from quickstats.components.numerics import pretty_float, str_encode_value, str_decode_value


signature_regex = {
    'F': r"\d+[.]?\d*",
    'P': r"n?\d+p?\d*",
    'S': r"\w+"
}

signature_parser = {
    'F': pretty_float,
    'P': str_decode_value,
    'S': str
}

signature_regex = {
    'F': r"\d+[.]?\d*",
    'P': r"n?\d+p?\d*",
    'S': r"\w+"
}

signature_parser = {
    'F': pretty_float,
    'P': str_decode_value,
    'S': str
}

class ParamParser:
    
    DEFAULT_FORMAT_STR = r"\w+"
    
    @property
    def format_str(self):
        return self._format_str
    @format_str.setter
    def format_str(self, val):
        if val is None:
            self._format_str = self.DEFAULT_FORMAT_STR
        else:
            self._format_str = val
        self.fname_regex   = self.get_fname_regex(self._format_str)
        self.attribute_parser = self.get_attribute_parser(self._format_str)

    def __init__(self, format_str:str=None, internal_param_str:str=None):
        self.format_str   = format_str
        self.internal_param_str = internal_param_str
    
    @staticmethod
    def get_signature_map(format_str:str):
        attribute_groups = re.findall(r"<(\w+)\[(\w)\]>", format_str)
        signature_map = {}
        for group in attribute_groups:
            attribute, signature = group[0], group[1]
            signature_map[attribute] = signature
        return signature_map
    
    @staticmethod
    def get_fname_regex(format_str:str, ext:str=".root"):
        expr = format_str
        signature_map = ParamParser.get_signature_map(format_str)
        for attribute, signature in signature_map.items():
            attribute_expr = signature_regex.get(signature.upper(), None)
            if expr is None:
                raise ValueError(f"unknown signature `{signature}`")
            group_expr = f"(?P<{attribute}>{attribute_expr})"
            expr = expr.replace(f"<{attribute}[{signature}]>", group_expr)
        expr += (ext.replace('.', r'\.') + "$")
        regex = re.compile(expr)
        return regex
   
    @staticmethod
    def sort_param_points(param_points:List, attributes:List):
        key = lambda d: tuple(d['parameters'][attrib] for attrib in attributes)
        return sorted(param_points, key=key)
    
    @staticmethod
    def get_attribute_parser(format_str:str):
        attribute_parser = {}
        signature_map = ParamParser.get_signature_map(format_str)
        for attribute, signature in signature_map.items():
            parser = signature_parser.get(signature, None)
            if parser is None:
                raise ValueError(f"unknown signature `{signature}`")
            attribute_parser[attribute] = parser
        return attribute_parser

    @staticmethod
    def parse_param_str(param_str:Optional[str]=None):
        if param_str is None:
            return {}
        param_values = {}
        param_expr_list = [s.strip() for s in param_str.split(',')]
        param_expr_list = [s for s in param_expr_list if s]
        for expr in param_expr_list:
            tokens = expr.split('=')
            if len(tokens) != 2:
                raise ValueError('invalid expression for parameterisation')
            param_name = tokens[0]
            values_expr = tokens[1]
            tokens = values_expr.split('_')
            # fixed value
            if len(tokens) == 1:
                values = [float(tokens[0])]
            # scan across range
            elif len(tokens) == 3:
                poi_min = float(tokens[0])
                poi_max = float(tokens[1])
                poi_step = float(tokens[2])
                values = np.arange(poi_min, poi_max + poi_step, poi_step)
            else:
                raise ValueError('invalid expression for parameterisation')
            param_values[param_name] = values
        param_names = list(param_values.keys())
        combinations = [param_values[param_name] for param_name in param_names]
        combinations = itertools.product(*combinations)
        param_points = []
        for combination in combinations:
            param_point = {k:v for k,v in zip(param_names, combination)}
            param_points.append(param_point)
        return param_points
    
    @staticmethod
    def val_encode_parameters(parameters:Dict):
        return ",".join([f"{param}={round(value, 8)}" for param, value in parameters.items()])
    
    @staticmethod
    def str_encode_parameters(parameters:Dict):
        encoded_str_list = []
        for param, value in parameters.items():
            if isinstance(value, float):
                value = str_encode_value(round(value, 8))
            encoded_str = f"{param}_{value}"
            encoded_str_list.append(encoded_str)
        return "_".join(encoded_str_list)

    def get_external_param_points(self, dirname:str=""):
        fnames = glob.glob(os.path.join(dirname, '*'))
        param_points = []
        for fname in fnames:
            basename = os.path.basename(fname)
            match = self.fname_regex.match(basename)
            if not match:
                continue
            point = {'filename': fname, 'parameters':{}}
            point['basename'] = basename.split('.')[0]
            for key, value in match.groupdict().items():
                parser = self.attribute_parser[key]
                point['parameters'][key] = parser(value)
            param_points.append(point)
        attributes = list(self.attribute_parser)
        param_points = self.sort_param_points(param_points, attributes)
        return param_points
    
    def get_internal_param_points(self):
        return self.parse_param_str(self.internal_param_str)
    
    def get_param_points(self, dirname:str=""):
        external_param_points = self.get_external_param_points(dirname)     
        internal_param_points = self.get_internal_param_points()
        if len(internal_param_points) == 0:
            internal_param_points = [{}]
        param_points = []
        for ext_point in external_param_points:
            fname = ext_point['filename']
            basename = ext_point['basename']
            ext_params = ext_point['parameters']
            for int_params in internal_param_points:
                param_point = {}
                param_point['filename'] = fname
                param_point['basename'] = basename
                param_point['external_parameters'] = {**ext_params}
                param_point['internal_parameters'] = {**int_params}
                param_points.append(param_point)
        return param_points
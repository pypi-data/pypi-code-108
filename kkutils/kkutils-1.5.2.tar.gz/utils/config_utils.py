#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: zhangkai@cmcm.com
Last modified: 2018-01-05 14:09:42
'''
import argparse
import json
import logging
import re
from configparser import ConfigParser
from pathlib import Path

from .base_utils import Dict, yaml


class Config(Dict):

    def __init__(self, *configs):
        for config in configs:
            self.update(self._load_cfg(config))

        parser = argparse.ArgumentParser(allow_abbrev=False)
        parser.add_argument('--config', type=str, default=None)
        options, _ = parser.parse_known_args()
        if options.config:
            self.update(self._load_cfg(options.config))

        parser = argparse.ArgumentParser()
        for key, value in self.items():
            self._add_args(parser, key, value)

        options, params = parser.parse_known_args()
        parsed_params = self._guess(params)
        if parsed_params:
            options.__dict__.update(parsed_params)
            logging.getLogger().info(f'{params} is parsed as: {parsed_params}')

        for key, value in options.__dict__.items():
            self._update(self, key, value)

    @staticmethod
    def _load_ini(config):
        conf = ConfigParser()
        conf.read(config)
        cfg = Dict()
        for section in conf.sections():
            cfg[section] = Dict()
            for key, value in conf.items(section):
                cfg[section][key] = Config._convert(value)
        return cfg

    @staticmethod
    def _load_cfg(config):
        cfg = Dict()
        if isinstance(config, dict):
            cfg.update(Dict(config))
        elif Path(config).exists():
            if config.endswith('.ini'):
                cfg.update(Dict(Config._load_ini(config)))
            elif config.endswith('.json'):
                cfg.update(Dict(json.load(open(config))))
            elif config.endswith('.yaml') or config.endswith('.yml'):
                cfg.update(Dict(yaml.load(open(config), Loader=yaml.FullLoader)))

        if cfg.extends:
            base = Dict()
            root = Path(config).parent
            if isinstance(cfg.extends, list):
                for x in cfg.extends:
                    base.update(Config._load_cfg(str(root / x)))
            elif isinstance(cfg.extends, str):
                base.update(Config._load_cfg(str(root / cfg.extends)))
            base.update(cfg)
            cfg = base

        return cfg

    @staticmethod
    def _convert(value):
        if re.match(r'^-?[\d]+$', value):
            return int(value)
        elif re.match(r'^-?\d+(\.?\d+)?$', value):
            return float(value)
        elif re.match(r'^true|false$', value.lower()):
            return value.lower() == 'true'
        else:
            return value

    @staticmethod
    def _update(opt, key, value):
        if key.find('.') >= 0:
            arr = key.split('.', 1)
            opt.setdefault(arr[0], Dict())
            Config._update(opt[arr[0]], arr[1], value)
        else:
            if isinstance(value, list):
                opt[key] = list(filter(lambda x: x != '', value))
            elif value == '':
                opt[key] = None
            else:
                opt[key] = value

    @staticmethod
    def _guess(params):
        options = {}
        for i, param in enumerate(params):
            if param.startswith('--') and param.find('=') >= 0:
                arr = param[2:].split('=')
                options[arr[0]] = Config._convert(arr[1])
            elif param.startswith('--no-'):
                options[param[5:]] = False
            elif param.startswith('--'):
                options[param[2:]] = True
            else:
                values = [Config._convert(param)]
                for j in range(1, i + 1):
                    key = params[i - j]
                    if not key.startswith('--'):
                        values.insert(0, Config._convert(key))
                    else:
                        key = key[2:]
                        options[key] = values[0] if len(values) == 1 else values
                        break
        return options

    @staticmethod
    def _str2bool(value):
        if isinstance(value, bool):
            return value
        elif value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        else:
            raise argparse.ArgumentTypeError('Boolean value expected')

    @staticmethod
    def _get_type(value):
        if isinstance(value, list):
            if len(value) > 0:
                return Config._get_type(value[0])
            else:
                return str
        elif isinstance(value, bool):
            return Config._str2bool
        elif value is None:
            return str
        else:
            return type(value)

    @staticmethod
    def _add_args(parser, key, value):
        if isinstance(key, str):
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(k, str):
                        Config._add_args(parser, f'{key}.{k}', v)
            elif isinstance(value, list):
                parser.add_argument(f'--{key}', type=Config._get_type(value), nargs='+', default=value)
            # elif isinstance(value, bool):
            #     parser.add_argument(f'--{key}', dest=key, action='store_true', default=value)
            #     parser.add_argument(f'--no-{key}', dest=key, action='store_false', default=(not value))
            else:
                parser.add_argument(f'--{key}', type=Config._get_type(value), default=value)

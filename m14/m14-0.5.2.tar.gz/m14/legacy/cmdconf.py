#!/usr/bin/env python3
# coding: utf-8

import importlib
import json
import os

import json5
from volkanic.cmdline import remember_cwd
from volkanic.utils import query_attr


class CommandNotFound(KeyError):
    pass


# deprecated
class CommandConf(object):
    def __init__(self, commands):
        self.commands = dict(commands)
        self.commands.setdefault('_global', {})

    @classmethod
    def _from_file(cls, name, loader, default_dir=None):
        path = cls._locate(name, default_dir)
        return cls(loader(open(path)))

    @classmethod
    def from_yaml(cls, name, default_dir=None):
        import yaml
        ext = os.path.splitext(name)[1].lower()
        if ext not in ['.yml', '.yaml']:
            name += '.yml'
        return cls._from_file(name, yaml.safe_load, default_dir)

    @classmethod
    def from_json(cls, name, default_dir=None):
        return cls._from_file(name, json.load, default_dir)

    @classmethod
    def from_json5(cls, name, default_dir=None):
        return cls._from_file(name, json5.load, default_dir)

    @staticmethod
    def _locate(path, default_dir):
        paths = [path]
        if default_dir is not None:
            paths.append(os.path.join(default_dir, path))
        for path in paths:
            if os.path.isfile(path):
                return path
        raise FileNotFoundError(path)

    @staticmethod
    def _execute(params):
        # only 'module' is a must-have
        prefix = params.get('prefix', '')
        module = prefix + params['module']
        call = params.get('call', 'run')
        args = params.get('args', [])
        kwargs = params.get('kwargs', {})
        if not isinstance(args, (list, tuple)):
            args = [args]
        m = importlib.import_module(module)
        query_attr(m, *call.split('.'))(*args, **kwargs)

    def __call__(self, cmd):
        if cmd not in self.commands:
            raise CommandNotFound(str(cmd))
        params = dict(self.commands['_global'])
        params.update(self.commands[cmd])
        with remember_cwd():
            os.chdir(params.get('cd', '.'))
            self._execute(params)

    @classmethod
    def run(cls, prog=None, args=None, default_dir=None, **kwargs):
        from argparse import ArgumentParser
        kwargs.setdefault('description', 'volkanic command-conf runner')
        parser = ArgumentParser(prog=prog, **kwargs)
        parser.add_argument('name', help='a YAML file')
        parser.add_argument(
            'key', nargs='?', default='default',
            help='a top-level key in the YAML file',
        )
        ns = parser.parse_args(args=args)
        cconf = cls.from_yaml(ns.name, default_dir)
        cconf(ns.key)

import json
import os
import re
from typing import List
from ruamel.yaml import YAML

from x_scaffold.context import ScaffoldContext
from x_scaffold.runtime import ScaffoldRuntime
from ..steps import ScaffoldStep
from ..plugin import ScaffoldPluginContext
from ..rendering import render_options, render_text


def init(context: ScaffoldPluginContext):
    context.add_step("config_write", ConfigStep())
    context.add_step("config_read", ConfigReadStep())


def get_formatter(path, options):
    default_formatter = YamlConfigFormatter()

    formatters: List[ConfigFormatter] = [
        YamlConfigFormatter(),
        JsonConfigFormatter(),
        default_formatter
    ]

    for formatter in formatters:
        if formatter.is_formatter(path, options):
            return formatter

    return default_formatter


class ConfigStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        options = render_options(step, context)

        # target_base = os.path.realpath(context.get('__target', '.'))
        # path: str = os.path.join(target_base, options.get('path'))
        path: str = context.resolve_target_path(options.get('path'))
        configuration = options.get('configuration')

        formatter = get_formatter(path, options)
        formatter.configure(path, configuration)


class ConfigReadStep(ScaffoldStep):
    def run(self, context: ScaffoldContext, step: dict, runtime: ScaffoldRuntime):
        options = render_options(step, context)
        # target_base = os.path.realpath(context.get('__target', '.'))
        # path: str = os.path.join(target_base, options.get('path'))
        path: str = context.resolve_target_path(options.get('path'))

        formatter = get_formatter(path, options)
        return formatter.read(path)


class ConfigFormatter:
    def read(self, path):
        pass

    def write(self, path, config):
        pass

    def configure(self, path, config):
        pass

    def is_formatter(self, path, options):
        pass


def merge(source, destination: dict):
    dest = destination
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = dest.setdefault(key, {})
            merge(value, node)
        else:
            dest[key] = value

    return dest


class YamlConfigFormatter(ConfigFormatter):
    def __init__(self) -> None:
        self.yaml = YAML()
        super().__init__()

    def read(self, path):
        yaml = self.yaml
        with open(path, 'r') as fhd:
            yaml_dict = yaml.load(fhd)
        return yaml_dict
    
    def write(self, path, config):
        yaml = self.yaml
        with open(path, 'w') as fhd:
            yaml.dump(config, fhd)

    def configure(self, path, config):
        yaml_dict = self.read(path)

        new_config = merge(config, yaml_dict)

        self.write(path, new_config)
    
    def is_formatter(self, path, options):
        format = options.get('format')
        if format == 'yaml' or re.match(r'.*\.y(a)?ml', path):
            return True


class JsonConfigFormatter(ConfigFormatter):
    def __init__(self) -> None:
        super().__init__()

    def read(self, path):
        with open(path, 'r') as fhd:
            yaml_dict = json.load(fhd)
        return yaml_dict
    
    def write(self, path, config):
        with open(path, 'w') as fhd:
            json.dump(config, fhd, indent=4)

    def configure(self, path, config):
        yaml_dict = self.read(path)

        new_config = merge(config, yaml_dict)

        self.write(path, new_config)
    
    def is_formatter(self, path, options):
        format = options.get('format')
        if format == 'json' or re.match(r'.*\.json', path):
            return True

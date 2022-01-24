#!/usr/bin/env python
# coding: utf-8

import argparse
import io
import os
import pathlib

import yaml
import logging
import getpass
import json
import sys
import re
import tempfile
import importlib
from collections import defaultdict
from fnmatch import fnmatch

from .context import ScaffoldContext
from .runtime import ScaffoldRuntime
from .plugins import load_plugins
from .rendering import render_text
from .steps import ScaffoldStep
from .plugin import ScaffoldPluginContext

_log = logging.getLogger(__name__)


def complete(text, state):
    if str(text).startswith('~/'):
        home = os.path.expanduser('~/')
        p = os.path.join(home, text[2:])
    else:
        p = text
        home = None

    items = pathlib.Path(os.getcwd()).glob(p + '*')
    if items is not None and home is not None:
        items = ['~/' + x[len(home):] for x in items]
    return (items + [None])[state]


def set_readline():
    try:
        import readline
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(complete)
    except:
        pass


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


color = AttributeDict({
    'PURPLE': '\033[35m',
    'CYAN':  '\033[36m',
    'BLUE':  '\033[34m',
    'GREEN':  '\033[32m',
    'YELLOW':  '\033[33m',
    'RED':  '\033[31m',
    'BOLD':  '\033[1m',
    'UNDERLINE':  '\033[4m',
    'ITALIC':  '\033[3m',
    'END':  '\033[0m',
})


def dict_to_str(d, fmt='%s=%s\n'):
    s = ''
    for x in d:
        s += fmt % (x, d[x])
    return s


def str2bool(v):
    if v is None:
        return False
    return v.lower() in ("yes", "true", "t", "1", "y")


known_types = {
    'int': int,
    'bool': str2bool,
    'str': str,
    'float': float
}


def term_color(text, *text_colors):
    return ''.join(text_colors) + text + color.END




# def render_file(path, context):
#     """Used to render a Jinja template."""

#     template_dir, template_name = os.path.split(path)
#     return render(template_name, context, template_dir)


def is_enabled(options):
    if 'enabled' in options:
        return options['enabled']
    if 'disabled' in options:
        return not options['disabled']
    if 'enabledif' in options:
        enabledif = options['enabledif']
        value = enabledif['value']
        if 'equals' in enabledif:
            return value == enabledif['equals']
        elif 'notequals' in enabledif:
            return value != enabledif['notequals']
    return True


def read_input(s):
    return input(s)


# class Prompt:

#     def __init__(self, d):
#         self._dict = d
#         self._value = None

#     def get(self):
#         if self._value is None:
#             self._value = self._get_value(self._dict)
#         return self._value

#     def _get_value(self, prompt):
#         default = prompt.get('default', None)
#         if isinstance(default, str):
#             default = default.format(env=os.environ)

#         if not is_enabled(prompt):
#             return default

#         required = prompt.get('required', False)
#         while True:
#             s = term_color('%s: ' % prompt['description'].format(
#                 default=default, env=os.environ), color.BOLD)
#             # if 'description' in prompt:
#             #     desc = term_color('%s' % prompt['description'], color.ITALIC)
#             #     sys.stdout.write('%s\n' % desc)

#             if 'choices' in prompt:
#                 s = term_color('%s: ' % prompt['description'].format(
#                     default=default), color.BOLD)
#                 sys.stdout.write('%s\n\n' % s)

#                 choices = prompt['choices']
#                 while True:
#                     opts = []
#                     max_len = 0
#                     for c in choices:
#                         keywords = ', '.join(c['keywords'])
#                         if len(keywords) > max_len:
#                             max_len = len(keywords)
#                         opts.append({'kw': keywords, 't': c['text']})

#                     for opt in opts:
#                         s = '%s' % c['text']
#                         opt['kw'] = opt['kw'].ljust(max_len)
#                         sys.stdout.write('[{kw}] {t}\n'.format(**opt))

#                     d = read_input(term_color('\nchoice: ', color.BOLD))

#                     for c in choices:
#                         if d in c['keywords']:
#                             v = c.get('value', d)
#                             if isinstance(v, dict):
#                                 v = defaultdict(
#                                     lambda: '', c.get('default', {}), **v)
#                             return v

#                     sys.stdout.write('\n%s please select a keyword on the left\n\n' %
#                                      term_color('[invalid choice] ', color.RED))
#             else:
#                 if prompt.get('secure', False):
#                     d = getpass.getpass(prompt=s)
#                 else:
#                     d = read_input(s)

#             if d == '' or d is None:
#                 if not required:
#                     return default
#                 else:
#                     sys.stdout.write(term_color('[required] ', color.RED))
#             else:
#                 if 'validate' in prompt:
#                     matches = re.match(prompt['validate'], d)
#                     if matches is None:
#                         sys.stdout.write(term_color(
#                             '[invalid, %s] ' % prompt['validate'], color.RED))
#                         continue
#                 if 'load' in prompt:
#                     if prompt['load'] == 'yaml':
#                         with open(d, 'r') as fhd:
#                             return yaml.load(fhd, Loader=yaml.FullLoader)
#                 return convert(d, prompt.get('type', 'str'))


# class ScaffoldLoader(yaml.Loader):

#     def __init__(self, stream):
#         if stream is not None:
#             if isinstance(stream, io.FileIO):
#                 self._root = os.path.split(stream.name)[0]
#             elif isinstance(stream, dict):
#                 d = stream
#                 stream = d['fhd']
#                 self._root = os.path.splitext(stream.name)[0]
#                 self._context = d['context']

#         super(ScaffoldLoader, self).__init__(stream)

#     def module(self, node):
#         item = self.construct_mapping(node, 9999)

#         if not is_enabled(item):
#             return None

#         fn = load_module(item)
#         if 'args' in item:
#             return fn(**item['args'])
#         else:
#             return fn()

    

#     def prompt(self, node):
#         item = self.construct_mapping(node, 9999)

#         return Prompt(item).get()

#     def prompt2(self, node):
#         item = self.construct_mapping(node, 9999)

#         return Prompt(item)


# ScaffoldLoader.add_constructor('!prompt2', ScaffoldLoader.prompt2)
# ScaffoldLoader.add_constructor('!prompt', ScaffoldLoader.prompt)
# ScaffoldLoader.add_constructor('!module', ScaffoldLoader.module)


def convert(v, type):
    if type in known_types:
        return known_types[type](v)
    return str(v)


def read_parameter(prompt, context, runtime: ScaffoldRuntime):
    default = prompt.get('default', None)
    if isinstance(default, str):
        default = default.format(env=os.environ)

    if not is_enabled(prompt):
        return default

    name = prompt.get('name', 'parameter')
    required = prompt.get('required', False)
    description = prompt.get('description', name)

    if 'if' in prompt:
        enabled = render_text(prompt['if'], context)
        if enabled.lower() != 'true':
            return default
    
    while True:
        # s = term_color('%s: ' % description.format(
        #     default=default, env=os.environ), color.BOLD)
        # if 'description' in prompt:
        #     desc = term_color('%s' % prompt['description'], color.ITALIC)
        #     sys.stdout.write('%s\n' % desc)

        # if 'choices' in prompt:
        #     s = term_color('%s: ' % description.format(
        #         default=default), color.BOLD)
        #     sys.stdout.write('%s\n\n' % s)

        #     choices = prompt['choices']
        #     while True:
        #         opts = []
        #         max_len = 0
        #         for c in choices:
        #             keywords = ', '.join(c['keywords'])
        #             if len(keywords) > max_len:
        #                 max_len = len(keywords)
        #             opts.append({'kw': keywords, 't': c['text']})

        #         for opt in opts:
        #             s = '%s' % c['text']
        #             opt['kw'] = opt['kw'].ljust(max_len)
        #             sys.stdout.write('[{kw}] {t}\n'.format(**opt))

        #         d = None #read_input(term_color('\nchoice: ', color.BOLD))


        #         for c in choices:
        #             if d in c['keywords']:
        #                 v = c.get('value', d)
        #                 if isinstance(v, dict):
        #                     v = defaultdict(
        #                         lambda: '', c.get('default', {}), **v)
        #                 return v

        #         sys.stdout.write('\n%s please select a keyword on the left\n\n' %
        #                             term_color('[invalid choice] ', color.RED))
        # else:
        d = runtime.ask(prompt)

        if d == '' or d is None:
            if not required:
                return default
            else:
                sys.stdout.write(term_color('[required] ', color.RED))
        else:
            if 'validate' in prompt:
                matches = re.match(prompt['validate'], d)
                if matches is None:
                    sys.stdout.write(term_color(
                        '[invalid, %s] ' % prompt['validate'], color.RED))
                    continue
            if 'load' in prompt:
                if prompt['load'] == 'yaml':
                    with open(d, 'r') as fhd:
                        return yaml.load(fhd, Loader=yaml.FullLoader)
            return convert(d, prompt.get('type', 'str'))


def config_cli(args):
    options = {}
    scaffold_file = os.path.expanduser('~/.xscaffold')
    if os.path.exists(scaffold_file):
        with open(scaffold_file, 'r') as fhd:
            options = yaml.load(fhd, Loader=yaml.FullLoader)

    if args.action == 'save':
        options['url'] = args.url

        with open(scaffold_file, 'w') as fhd:
            yaml.dump(options, fhd, default_flow_style=False)
    elif args.action == 'view':
        sys.stdout.write('url: %s' % options.get('url', 'not defined'))


# def log(s, context={}):
#     sys.stdout.write(
#         render_text(s, context)
#     )


# def load_module(m):
#     mod = importlib.import_module('modules.%s' % m['name'])
#     if hasattr(mod, 'init'):
#         getattr(mod, 'init')(sys.modules[__name__])

#     return getattr(mod, m.get('function', 'execute'))


# def execute_modules(context, pkg_dir, modules):
#     for m in modules:
#         execute_fn = load_module(m)
#         execute_fn(context, pkg_dir, m)


def rm_rf(d):
    for path in (os.path.join(d, f) for f in os.listdir(d)):
        if os.path.isdir(path):
            rm_rf(path)
        else:
            os.unlink(path)
    os.rmdir(d)


def locate_scaffold_file(path, name):
    paths = [
        os.path.join(path, f'.{name}.yml'),
        os.path.join(path, f'.{name}.yaml'),
        os.path.join(path, f'.{name}.json'),
        os.path.join(path, f'{name}.yml'),
        os.path.join(path, f'{name}.yaml'),
        os.path.join(path, f'{name}.json')
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def process_parameters(parameters, context: ScaffoldContext, runtime: ScaffoldRuntime):
    for parameter in parameters:
        parameter_name = parameter['name']
        if parameter_name in context:
            context[parameter_name] = context[parameter_name]
        else:
            context[parameter_name] = read_parameter(parameter, context, runtime)


def run(context: ScaffoldContext, options, runtime: ScaffoldRuntime):
    execute_scaffold(context, options, runtime)

    runtime.print_todos(context)
    runtime.print_notes(context)

    return context


def execute_scaffold(context: ScaffoldContext, options, runtime: ScaffoldRuntime):
    tempdir = options.get('temp', tempfile.gettempdir())
    package = options['package']

    name = options.get('name', 'xscaffold')

    if os.path.exists(package):
        runtime.log(
            '[info] using local package \'%s\'...' % package + '\n')
        pkg_dir = package
    else:
        pkg_dir = fetch_git(runtime, tempdir, package)

    sys.path.append(pkg_dir)
    scaffold_file = locate_scaffold_file(pkg_dir, name)
    _log.debug('scaffold file: %s', scaffold_file)

    if scaffold_file is not None:
        with open(scaffold_file, 'r') as fhd:
            config = yaml.load(fhd, Loader=yaml.FullLoader)
    else:
        config = {
            'steps': options.get('steps', [{ 'fetch': {} }])
        }

    plugin_context = ScaffoldPluginContext(
        config.get('plugins', {})
    )
    plugins: list = load_plugins()
    for plugin in plugins:
        plugin.init(plugin_context)

    context.update(config.get('context', {}))

    process_parameters(config.get('parameters', []), context, runtime)

    context['__package'] = {
        'path': pkg_dir,
        'options': options
    }

    steps_context = context['steps'] = {}
    steps: list = config.get('steps', [])

    execute_steps(context, runtime, plugin_context, steps_context, steps)

    return context

def execute_steps(context, runtime, plugin_context, steps_context, steps):
    step: dict
    for step in steps:
        if 'if' in step:
            enabled = render_text(step['if'], context)
            if enabled == False:
                continue
        step_id = step.get('id', 'last')
        if 'group' in step:
            group_steps = step['group']
            execute_steps(context, runtime, plugin_context, steps_context, group_steps)
        elif 'foreach' in step:
            foreach_steps = step['foreach']
            items = render_text(foreach_steps.get('items', []), context)
            for item in items:
                steps_context[step_id] = item
                execute_steps(context, runtime, plugin_context, steps_context, foreach_steps.get('steps', []))
        else:
            plugin_step_name = None
            for step_name in step:
                if step_name in plugin_context.steps:
                    plugin_step_name = step_name
                    break
            if plugin_step_name:
                plugin_step = plugin_context.steps[plugin_step_name]
                result = plugin_step.run(context, step[plugin_step_name], runtime)

                if 'id' in step:
                    step_id = step['id']
                    steps_context[step_id] = result


def fetch_git(runtime, tempdir, package):
    package_parts = package.split('@')
    if len(package_parts) == 1:
        package_name = package_parts[0]
        package_version = 'main'
    else:
        package_name = package_parts[0]
        package_version = package_parts[1]
    package_name_parts = package_name.split('/')
    if len(package_name_parts) <= 2:
        package_name_parts = ['github.com'] + package_name_parts
        package_name = '/'.join(package_name_parts)
    pkg_dir = os.path.join(tempdir, f'{package_name}@{package_version}')

    rc = 9999
    if os.path.exists(pkg_dir):
        runtime.log('{YELLOW}[git] updating %s package...{END}\n' % package)
        rc = os.system(
                """(cd {pkg_dir} && git pull >/dev/null 2>&1)""".format(pkg_dir=pkg_dir))
        if rc != 0:
            runtime.log('{RED}[error]{YELLOW} package %s is having issues, repairing...{END}\n' % package)
            rm_rf(pkg_dir)

    if rc != 0:
        runtime.log('[git] pulling %s package...' % package + '\n')
        rc = os.system(f"""
        git clone https://{package_name} {pkg_dir} >/dev/null 2>&1
        """)
    if rc != 0:
        raise Exception(
                'Failed to pull scaffold package %s' % package)

    rc = os.system(f"""(cd {pkg_dir} && git checkout -f {package_version} >/dev/null 2>&1)""")
    if rc != 0:
        raise Exception('Failed to load version %s' % package_version)
    return pkg_dir

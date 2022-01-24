#!/usr/bin/env python
# coding: utf-8

import logging
import os
import pathlib
import re
import sys
import tempfile

import yaml

from .context import ScaffoldContext
from .plugin import ScaffoldPluginContext
from .plugins import load_plugins
from .rendering import render_options, render_text
from .runtime import ScaffoldRuntime


_log = logging.getLogger(__name__)


# def complete(text, state):
#     if str(text).startswith('~/'):
#         home = os.path.expanduser('~/')
#         p = os.path.join(home, text[2:])
#     else:
#         p = text
#         home = None

#     items = pathlib.Path(os.getcwd()).glob(p + '*')
#     if items is not None and home is not None:
#         items = ['~/' + x[len(home):] for x in items]
#     return (items + [None])[state]


# def set_readline():
#     try:
#         import readline
#         readline.set_completer_delims(' \t\n;')
#         readline.parse_and_bind("tab: complete")
#         readline.set_completer(complete)
#     except:
#         pass


# class AttributeDict(dict):
#     __getattr__ = dict.__getitem__
#     __setattr__ = dict.__setitem__


# color = AttributeDict({
#     'PURPLE': '\033[35m',
#     'CYAN':  '\033[36m',
#     'BLUE':  '\033[34m',
#     'GREEN':  '\033[32m',
#     'YELLOW':  '\033[33m',
#     'RED':  '\033[31m',
#     'BOLD':  '\033[1m',
#     'UNDERLINE':  '\033[4m',
#     'ITALIC':  '\033[3m',
#     'END':  '\033[0m',
# })


# def dict_to_str(d, fmt='%s=%s\n'):
#     s = ''
#     for x in d:
#         s += fmt % (x, d[x])
#     return s


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


# def term_color(text, *text_colors):
#     return ''.join(text_colors) + text + color.END




# def render_file(path, context):
#     """Used to render a Jinja template."""

#     template_dir, template_name = os.path.split(path)
#     return render(template_name, context, template_dir)


# def is_enabled(options):
#     if 'enabled' in options:
#         return options['enabled']
#     if 'disabled' in options:
#         return not options['disabled']
#     if 'enabledif' in options:
#         enabledif = options['enabledif']
#         value = enabledif['value']
#         if 'equals' in enabledif:
#             return value == enabledif['equals']
#         elif 'notequals' in enabledif:
#             return value != enabledif['notequals']
#     return True


# def read_input(s):
#     return input(s)


def convert(v, type):
    if type in known_types:
        return known_types[type](v)
    return str(v)


def read_parameter(prompt, context, runtime: ScaffoldRuntime):
    default = prompt.get('default', '')
    # if isinstance(default, str):
    #     default = default.format(env=os.environ)

    #name = prompt.get('name', 'parameter')
    required = prompt.get('required', False)

    if 'if' in prompt:
        enabled = prompt['if']
        if not enabled:
            return default
    
    while True:
        d = runtime.ask(prompt)

        if d == '' or d is None:
            if not required:
                return default
            else:
                runtime.write('{RED}[required]{END} ')
        else:
            if 'validate' in prompt:
                matches = re.match(prompt['validate'], d)
                if matches is None:
                    runtime.write('{RED}[invalid, %s]{END} ' % prompt['validate'])
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


def rm_rf(d):
    for path in (os.path.join(d, f) for f in os.listdir(d)):
        if os.path.isdir(path):
            rm_rf(path)
        else:
            os.unlink(path)
    os.rmdir(d)


def locate_scaffold_file(path, name):
    base_paths = [
        path,
        os.path.join(path, '.xscaffold')
    ]

    extensions = [
        '.yaml',
        '.yml',
        '.json'
    ]

    names = [
        f'.{name}',
        f'{name}',
        f'{name}/xscaffold',
        f'{name}/.xscaffold'
    ]
    for base_path in base_paths:
        for ext in extensions:
            for n in names:
                full_path = os.path.join(base_path, n + ext)
                if os.path.exists(full_path):
                    return full_path
    return None


def process_parameters(parameters, context: ScaffoldContext, runtime: ScaffoldRuntime):
    for parameter in parameters:
        parameter_options = render_options(parameter, context)
        parameter_name = parameter_options['name']
        if parameter_name in context:
            context[parameter_name] = context[parameter_name]
        else:
            context[parameter_name] = read_parameter(parameter_options, context, runtime)


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
    
    scaffold_file = locate_scaffold_file(pkg_dir, name)
    pkg_dir = os.path.dirname(scaffold_file)
    sys.path.append(pkg_dir)
    _log.info('scaffold file: %s', scaffold_file)

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

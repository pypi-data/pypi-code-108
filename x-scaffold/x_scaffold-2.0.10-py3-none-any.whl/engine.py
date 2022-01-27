#!/usr/bin/env python
# coding: utf-8

import collections
import logging
import os
import re
import sys
import tempfile

from ruamel.yaml import YAML

from x_scaffold.steps import ScaffoldStepExecution

from .context import ScaffoldContext
from .plugin import ScaffoldPluginContext
from .plugins import load_plugins
from .rendering import render_options, render_text, render_value
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
                runtime.write('{RED}[required]{END} ', format=True)
        else:
            if 'validate' in prompt:
                matches = re.match(prompt['validate'], d)
                if matches is None:
                    runtime.write('{RED}[invalid, %s]{END} ' % prompt['validate'], format=True)
                    continue
            return convert(d, prompt.get('type', 'str'))


def config_cli(args):
    options = {}
    scaffold_file = os.path.expanduser('~/.xscaffold')

    yaml = YAML()
    if os.path.exists(scaffold_file):
        with open(scaffold_file, 'r') as fhd:
            options = yaml.load(fhd)

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
        os.path.join(path, '.xscaffold'),
        os.path.join(path, 'xscaffold')
    ]

    extensions = [
        '.yaml',
        '.yml',
        '.json',
        ''
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
            context[parameter_name] = convert(context[parameter_name], parameter.get('type', 'str'))
        else:
            context[parameter_name] = read_parameter(parameter_options, context, runtime)


def run(context: ScaffoldContext, options, runtime: ScaffoldRuntime):
    execute_scaffold(context, options, runtime)

    runtime.print_todos(context)
    runtime.print_notes(context)

    return context


def execute_scaffold(context: ScaffoldContext, options, runtime: ScaffoldRuntime):
    packages_dir = os.path.realpath(os.path.expanduser('~/.xscaffold/packages'))
    tempdir = options.get('temp', packages_dir)
    package = options['package']

    yaml = YAML()

    name = options.get('name', 'xscaffold')

    if '__package' in context:
        package_path = context.resolve_package_path(package)
    else:
        package_path = package
    if os.path.exists(package_path):
        _log.debug('using local package \'%s\'', package_path)
        pkg_dir = package_path
    else:
        pkg_dir = fetch_git(runtime, tempdir, package)
    
    scaffold_file = locate_scaffold_file(pkg_dir, name)
    _log.debug('scaffold file: %s', scaffold_file)

    if scaffold_file:
        pkg_dir = os.path.dirname(scaffold_file)
    sys.path.append(pkg_dir)
    

    if scaffold_file is not None:
        with open(scaffold_file, 'r') as fhd:
            config = yaml.load(fhd)
    else:
        config = {
            'steps': options.get('steps', [{ 'action': 'fetch' }])
        }

    context.todos.extend(config.get('todos', []))
    context.notes.extend(config.get('notes', []))

    plugin_context = ScaffoldPluginContext(
        config.get('plugins', {})
    )

    step_execution = ScaffoldStepExecution(plugin_context)

    plugins: list = load_plugins()
    for plugin in plugins:
        plugin.init(plugin_context)

    process_parameters(config.get('parameters', []), context, runtime)

    context_options = render_options(config.get('context', {}), context)
    context.update(context_options)

    context['__package'] = {
        'path': pkg_dir,
        'options': options
    }

    steps_context = context['steps'] = {}
    steps: list = config.get('steps', [])

    step_execution.execute(context, runtime, steps_context, steps)

    return context

# def execute_steps(context: ScaffoldContext, runtime, step_execution: ScaffoldStepExecution, steps_context, steps):
#     step: dict
#     for step in steps:
#         if 'if' in step:
#             enabled = render_value(step['if'], context)
#             if enabled == False:
#                 continue
#         if 'group' in step:
#             group_steps = step['group']
#             execute_steps(context, runtime, step_execution, steps_context, group_steps)
#         elif 'foreach' in step:
#             foreach_steps = step['foreach']
#             items = render_value(foreach_steps.get('items', []), context)
#             step_id = step.get('id', 'foreach')
#             for item in items:
#                 context.set_step(step_id, item)
#                 execute_steps(context, runtime, step_execution, steps_context, foreach_steps.get('steps', []))
#         else:
#             executor = None
#             executor_step_name = None
#             is_plugin = False
#             for step_name in step:
#                 executor, is_plugin = step_execution.get_executor(step_name, context)
#                 if executor is not None:
#                     executor_step_name = step_name
#                     break
#             if executor:
#                 step_options = step[executor_step_name]

#                 step_id = step.get('id', executor_step_name)
                
#                 _log.debug(f'[{step_id}] running')
#                 if is_plugin:
#                     if isinstance(executor_step_name, collections.Mapping):
#                         step_options['__id'] = step_id
#                     result = executor(context, step_options, runtime)
#                 else:
#                     executor(**step_options)
#                 context.set_step(step_id, result)

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
    _log.debug('using package dir: %s', pkg_dir)

    rc = 9999
    if os.path.exists(pkg_dir):
        _log.debug('[git] updating %s package', package)
        rc = os.system(
                """(cd {pkg_dir} && git pull >/dev/null 2>&1)""".format(pkg_dir=pkg_dir))
        if rc != 0:
            _log.error('package %s is having issues, repairing', package)
            rm_rf(pkg_dir)

    if rc != 0:
        _log.debug('[git] pulling %s package', package)
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

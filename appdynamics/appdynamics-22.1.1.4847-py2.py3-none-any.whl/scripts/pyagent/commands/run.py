# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

import errno
import os
import shlex

from appdynamics.scripts.pyagent.commands import proxy
from appdynamics.scripts.pyagent import CommandInvocationError, CommandExecutionError

USAGE = "run <options> -- <command> [args...]"

ABOUT = """Run a program with the agent enabled.

Use this command to instrument a Python application. If <command> is not the
path to an executable, the command is looked for in your PATH. The command may
be a Python interpreter or a supported server that embeds Python (like uwsgi
and gunicorn).

For example, if you normally run your application using gunicorn:

    gunicorn -w 4 -b unix:acme.sock acme.app:app

You can run the same application instrumented by AppDynamics with:

    pyagent run -c acme.cfg -- gunicorn -w 4 -b unix:acme.sock acme.app:app

The -c (--config-file) option specifies an agent configuration file. A simple
minimal configuration file looks like:

    [agent]
    app = Acme Book Store
    tier = django-web
    node = django-web-01

    [controller]
    host = my-controller.example.com

The agent requires the app, tier, and node names and controller host to be
set. If any of these values is not set, your application will be run without
instrumentation (the agent will be disabled).

Values for common configuration options may also be passed on the command line
to {pyagent}; see the list of options below. If a configuration option is
specified both on the command line and in the configuration file, the value
from the command line takes precedence over the configuration file.
"""

OPTIONS = {
    'cli': 'run in CLI mode',
    'use-manual-proxy': 'disable auto-start of proxy (manual start)',
    'no-watchdog': 'disable the watchdog when auto-starting proxy',

    'config-file': {
        'short': 'c',
        'help': 'the config file to use',
        'value': True,
        'value_help': '<file>',
    },

    'app': {
        'short': 'a',
        'help': 'the name of the app',
        'value': True,
        'value_help': '<app>',
    },
    'tier': {
        'short': 't',
        'help': 'the name of the tier',
        'value': True,
        'value_help': '<tier>',
    },
    'node': {
        'short': 'n',
        'help': 'the name of the node',
        'value': True,
        'value_help': '<node>',
    },

    'controller': {
        'short': 'h',
        'help': 'the host (and optionally port) of the controller',
        'value': True,
        'value_help': '<host>[:<port>]',
    },
    'ssl': {
        'help': 'pass to use SSL with the controller',
    },
    'no-ssl': {
        'help': 'pass to disable SSL with the controller (the default)',
    },

    # Internal / undocumented options

    'run-proxy-script': {
        'help': False,     # "Path to runProxy script"
        'value': True,
    },

    'proxy-args': {
        'help': False,  # "Command line arguments to pass to runProxy"
        'value': True,
    },
}


def command(options, args):
    import appdynamics.autoinject
    pythonpath = [os.path.dirname(appdynamics.autoinject.__file__), '.']

    if not args:
        raise CommandInvocationError('missing command: run <options> -- <command> [args...]')

    environ = os.environ

    if 'PYTHONPATH' in environ:
        pythonpath.append(environ['PYTHONPATH'])

    environ['PYTHONPATH'] = ':'.join(pythonpath)

    if 'config-file' in options:
        environ['APPD_CONFIG_FILE'] = options['config-file']
    if 'app' in options:
        environ['APPDYNAMICS_AGENT_APPLICATION_NAME'] = options['app']
    if 'tier' in options:
        environ['APPDYNAMICS_AGENT_TIER_NAME'] = options['tier']
    if 'node' in options:
        environ['APPDYNAMICS_AGENT_NODE_NAME'] = options['node']
    if 'nodereuse' in options:
        environ['APPDYNAMICS_AGENT_REUSE_NODE_NAME'] = options['nodereuse']
    if 'nodereuseprefix' in options:
        environ['APPDYNAMICS_AGENT_REUSE_NODE_NAME_PREFIX'] = options['nodereuseprefix']

    if 'ssl' in options:
        environ['APPDYNAMICS_CONTROLLER_SSL_ENABLED'] = 'on'
    elif 'no-ssl' in options:
        environ['APPDYNAMICS_CONTROLLER_SSL_ENABLED'] = 'off'

    if 'controller' in options:
        value = options['controller']

        if ':' in value:
            host, port = value.split(':', 1)
            environ['APPDYNAMICS_CONTROLLER_HOST_NAME'] = host
            environ['APPDYNAMICS_CONTROLLER_PORT'] = port
        else:
            environ['APPDYNAMICS_CONTROLLER_HOST_NAME'] = value

    if 'use-manual-proxy' not in options:
        proxy_args = []

        if 'no-watchdog' in options:
            proxy_args.append('--no-watchdog')

        if 'run-proxy-script' in options:
            proxy_args.append('--run-proxy-script')
            proxy_args.append(options['run-proxy-script'])

        if 'proxy-args' in options:
            proxy_args.extend(shlex.split(options['proxy-args']))

        proxy.start(proxy_args)

    try:
        os.execvpe(args[0], args, environ)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            raise CommandExecutionError('%s: no such file or directory' % args[0])
        elif exc.errno == errno.EPERM:
            raise CommandExecutionError('%s: permission denied' % args[0])
        raise

# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

import os
from pkg_resources import resource_filename
from appdynamics.scripts.pyagent import CommandExecutionError, CommandInvocationError, parse_options


USAGE = "config <param> [options]"

ABOUT = """Show configuration of AppDynamics Python agent

WSGI CONFIGURATION
    If you have a raw WSGI application or an application that uses a
    WSGI-based framework not currently supported by the Python agent, you can
    configure the agent to intercept at the WSGI layer by wrapping your
    WSGI callable.

        {pyagent} config wsgi [--no-check] --t <type> <wsgi-file> [callable]

    The <wsgi-file> argument is the full path to your WSGI file. The command
    normally checks to ensure that this file exists before outputting the
    configuration. To skip this check, pass the --no-check option. The
    optional [callable] argument is the name of the WSGI callable defined in
    your WSGI file. You MUST pass the name of the callable if your callable
    is NOT named 'application' or 'app'.

    The --type (-t) argument controls the output configuration and is
    required. Its value may be one of:

        file                output a new WSGI file that loads and wraps yours
        wrap                print a modified version of the given WSGI file
        mod_wsgi            Apache + mod_wsgi configuration directives
        gunicorn            Gunicorn command line option
        uwsgi               uWSGI command line options
        uwsgi.conf          uWSGI configuration file options

    The 'wrap' type displays a modified version of your WSGI file that
    injects the agent. This does NOT modify the WSGI file; it just displays
    the modified file for you to use.


    EXAMPLES
        {pyagent} config wsgi -t mod_wsgi /var/www/myapp/main.wsgi
        {pyagent} config wsgi -t gunicorn /var/www/myapp/main.wsgi MyApp

OTHER CONFIGURATION"""


def command(options, args):
    CONFIG_DISPLAY = {
        'wsgi': config_wsgi,
    }

    try:
        config = args[0]
        args = args[1:]
        CONFIG_DISPLAY[config](args)
    except IndexError:
        raise CommandInvocationError('missing required config parameter name')
    except KeyError:
        raise CommandInvocationError('unknown config parameter name: %s' % config)


WSGI_OPTIONS = {
    'type': {
        'short': 't',
        'value': True,
        'required': True,
    },
    'no-check': 'do not check if the WSGI file exists',
}

WSGI_TYPES = ['file', 'wrap', 'mod_wsgi', 'gunicorn', 'uwsgi', 'uwsgi.conf']

WSGI_FILE_TEMPLATE = """\
from appdynamics.agent.frameworks.wsgi import make_app as _make_app
{our_callable} = _make_app('{wsgi_file}', {their_callable})
"""

MOD_WSGI_DIRECTIVES = """\
Use the following directives in your Apache mod_wsgi configuration:

SetEnv APPDYNAMICS_WSGI_SCRIPT {their_wsgi_file}
SetEnv APPDYNAMICS_WSGI_CALLABLE_OBJECT {callable}
WSGIScriptAlias YOUR_URL_ROOT_HERE {our_wsgi_file}
WSGICallableObject application
"""

UWSGI_DIRECTIVES = """\
module=appdynamics.agent.frameworks.wsgi
callable=application
env=APPDYNAMICS_WSGI_SCRIPT={wsgi_file}{callable}
"""


def config_wsgi(args):
    options, args = parse_options(WSGI_OPTIONS, args)
    wsgi_type = options['type']
    check_for_existence = 'no-check' not in options

    if not args:
        raise CommandInvocationError('missing required argument <wsgi-file>')
    if wsgi_type not in WSGI_TYPES:
        raise CommandInvocationError('unrecognized type %s' % wsgi_type)

    wsgi_file = args[0]
    wsgi_callable = args[1] if len(args) > 1 else None

    if check_for_existence and not os.path.exists(wsgi_file):
        raise CommandExecutionError('%s: file not found (fix path or use --no-check)' % wsgi_file)

    if wsgi_type == 'file':
        print(WSGI_FILE_TEMPLATE.format(
            our_callable=wsgi_callable or 'application',
            their_callable=repr(wsgi_callable),
            wsgi_file=wsgi_file))
    elif wsgi_type == 'wrap':
        if wsgi_callable is None:
            raise CommandInvocationError('must specify wsgi callable name for --type wrap')

        with open(wsgi_file, 'r') as fp:
            print('import appdynamics.agent.frameworks.wsgi')
            print(fp.read())
            print('{callable} = appdynamics.agent.frameworks.wsgi.wsgi_middleware({callable})'.format(
                callable=wsgi_callable))
    elif wsgi_type == 'mod_wsgi':
        print(MOD_WSGI_DIRECTIVES.format(
            our_wsgi_file=resource_filename('appdynamics.scripts', 'appdynamics.wsgi'),
            their_wsgi_file=wsgi_file,
            callable=wsgi_callable or ''))
    elif wsgi_type == 'gunicorn':
        print('gunicorn -e "APPDYNAMICS_WSGI_SCRIPT={wsgi_file}" {callable} '
              'appdynamics.agent.frameworks.wsgi:application'.format(
                  wsgi_file=wsgi_file,
                  callable='-e "APPDYNAMICS_WSGI_CALLABLE_OBJECT=%s"' % wsgi_callable if wsgi_callable else ''))
    elif wsgi_type == 'uwsgi':
        print('pyagent run -w {their_wsgi_file} {callable} - uwsgi --wsgi-file {our_wsgi_file}'.format(
            our_wsgi_file=resource_filename('appdynamics.scripts', 'appdynamics.wsgi'),
            their_wsgi_file=wsgi_file,
            callable='-c %s' % wsgi_callable if wsgi_callable else ''))
    elif wsgi_type == 'uwsgi.conf':
        callable_env = " APPDYNAMICS_WSGI_CALLABLE_OBJECT={callable}".format(
            callable=wsgi_callable) if wsgi_callable else ''
        print(UWSGI_DIRECTIVES.format(wsgi_file=wsgi_file, callable=callable_env))

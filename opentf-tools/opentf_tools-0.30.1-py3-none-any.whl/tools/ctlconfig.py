# Copyright 2022 Henix, henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""opentf-ctl config module"""

import os
import sys

from importlib.metadata import version

import yaml

from opentf.tools.ctlcommons import _is_command, _get_value, _error


########################################################################

# pylint: disable=broad-except

CONFIG = {}
HEADERS = {}


########################################################################
# Help messages

CONFIG_HELP = '''Modify opentfconfig files using subcommands like "opentf-ctl config use-context my-context"

 The following rules are used to find the configuration file to use:

 1.  If the --opentfconfig flag is set, then that file is loaded.
 2.  If $OPENTF_CONFIG environment variable is set, then it is used as a file path and that file is loaded.
 3.  Otherwise, ${HOME}/.opentf/config is used.

Available Commands:
  generate             Generate a configuration file from user inputs
  use-context          Set the current-context in an opentfconfig file
  set-context          Set a context entry in opentfconfig
  set-orchestrator     Set an orchestrator entry in opentfconfig
  set-credentials      Set a user entry in opentfconfig
  delete-context       Delete a context entry from the opentfconfig
  delete-orchestrator  Delete an orchestrator entry from the opentfconfig
  delete-credentials   Delete a user entry from the opentfconfig
  view                 Display current configuration

Usage:
  opentf-ctl config <command> [options]

Use "opentf-ctl config <command> --help" for more information about a given command.
Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

CONFIG_GENERATE_HELP = '''Generate a configuration file from user inputs and streams it in stdout

Options:
  --name='': Nickname that will be used for context and orchestrator registration (default: default)
  --orchestrator-server='': Address of the opentf orchestrator
  --orchestrator-receptionist-port='': Port of the receptionist service (integer)  (default: 7774)
  --orchestrator-observer-port='': Port of the observer service (integer) (default: 7775)
  --orchestrator-eventbus-port='': Port of the eventbus service (integer) (default: 38368)
  --orchestrator-killswitch-port='': Port of the killswitch service (integer) (default: 7776)
  --orchestrator-agentchannel-port='': Port of the agentchannel service (integer) (default: 24368)
  --insecure-skip-tls-verify=false|true: Skip TLS verification (default: false)
  --token=": User's token to sign communications with orchestrator

Usage:
  opentf-ctl config generate [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

CONFIG_USE_CONTEXT_HELP = '''Select the current context to use

Usage:
  opentf-ctl config use-context {context}

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

CONFIG_SET_CONTEXT_HELP = '''Sets a context entry in opentfconfig

 Specifying a name that already exists will merge new fields on top of existing values for those fields.

Examples:
  # Set the user field on the foo context entry without touching other values
  opentf-ctl config set-context foo --user=admin

Options:
      --current=false: Modify the current context

Usage:
  opentf-ctl config set-context [NAME | --current] [--orchestrator=orchestrator_nickname] [--user=user_nickname] [--namespace=namespace] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

CONFIG_SET_ORCHESTRATOR_HELP = '''Sets an orchestrator entry in opentfconfig

 Specifying a name that already exists will merge new fields on top of existing values.

Examples:
  # Set only the server field of the e2e orchestrator entry without touching other values.
  opentf-ctl config set-orchestrator e2e --server=https://1.2.3.4

Options:
  --agentchannel-port='': Port of the agentchannel service (integer)
  --eventbus-port='': Port of the eventbus service (integer)
  --insecure-skip-tls-verify=false|true: Skip TLS verification
  --killswitch-port='': Port of the killswitch service (integer)
  --observer-port='': Port of the observer service (integer)
  --receptionist-port='': Port of the receptionist service (integer)
  --server='': Address of the opentf orchestrator

Usage:
  opentf-ctl config set-orchestrator NAME [--insecure-skip-tls-verify=true] [--server=server] [--eventbus-port=port] [--agentchannel-port=port] [--observer-port=port] [--receptionist-port=port] [--killswitch-port=port] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

CONFIG_SET_CREDENTIALS_HELP = '''Sets a user entry in opentfconfig

 Specifying a name that already exists will merge new fields on top of existing values.

  Bearer token flags:
    --token=bearer_token

Examples:
  # Set token auth for the "admin" entry
  opentf-ctl config config set-credentials cluster-admin --token=token

Options:
      --token='': Bearer token

Usage:
  kubectl config set-credentials NAME [--token=bearer_token] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

CONFIG_DELETE_CONTEXT_HELP = '''Delete the specified context from the opentfconfig

Examples:
  # Delete the context for the demo orchestrator
  opentf-ctl config delete-context demo

Usage:
  opentf-ctl config delete-context NAME [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

CONFIG_DELETE_ORCHESTRATOR_HELP = '''Delete the specified orchestrator from the opentfconfig

Usage:
  opentf-ctl config delete-orchestrator NAME [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

CONFIG_DELETE_CREDENTIALS_HELP = '''Delete the specified user from the opentfconfig

Examples:
  # Delete the admin user
  opentf-ctl config delete-credentials admin

Usage:
  opentf-ctl config delete-credentials NAME [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

CONFIG_VIEW_HELP = '''Display current configuration

The displayed configuration will be in order of priority the one pointed by
  - the --opentfconfig= argument value
  - the environment variable OPENTF_CONFIG
  - the current user configuration located at ~/.opentf/config

Usage:
  opentf-ctl config view [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''


########################################################################


def read_configuration():
    """Read configuration file.

    Configuration file is by default ~/.opentf/config, but this can be
    overridden by specifying the OPENTF_CONFIG environment variable or
    by using the `--opentfconfig=' command line parameter.

    Configuration file is a kubeconfig-like file, in YAML:

    ```yaml
    apiVersion: opentestfactory.org/v1alpha1
    kind: CtlConfig
    current-context: default
    contexts:
    - context:
        orchestrator: default
        user: default
      name: default
    orchestrators:
    - name: default
      orchestrator:
        insecure-skip-tls-verify: true
        server: http://localhost
        ports:
          receptionist: 7774
          observer: 7775
          killswitch: 7776
          eventbus: 38368
    users:
    - name: default
      user:
        token: ey...
    ```

    Optional command-line options:

    --token=''
    --user=''
    --orchestrator=''
    --context=''
    --insecure-skip-tls-verify=false|true
    --opentfconfig=''
    """

    def _get(kind, name):
        for item in config[f'{kind}s']:
            if item['name'] == name:
                return item[kind]
        return None

    def _safe_get(kind, name):
        what = _get(kind, name)
        if what is None:
            _error('%s %s is not available in configuration.', kind.title(), repr(name))
            _error('(Using the %s configuration file.)', repr(_))
            sys.exit(2)
        return what

    def _safe_value(option):
        what = _get_value(option)
        if what == '':
            _error('The %s option specifies an empty value.', option)
            sys.exit(2)
        return what

    _, config = _read_opentfconfig()

    context_name = _safe_value('--context=') or config.get('current-context')
    if not context_name:
        _error(
            'Empty or undefined current context.  Please specify a current context in your configuration file or use the --context= command line option.'
        )
        sys.exit(2)
    context = _safe_get('context', context_name)

    orchestrator_name = _safe_value('--orchestrator=') or context.get('orchestrator')
    if not orchestrator_name:
        _error(
            'No orchestrator defined in the context.  Please specify an orchestrator in your configuration file or use the --orchestrator= command line option.'
        )
        sys.exit(2)
    orchestrator = _safe_get('orchestrator', orchestrator_name)

    user_name = _safe_value('--user=') or context.get('user')
    if not user_name:
        _error(
            'No user defined in the context.  Please specify a user in your configuration file or use the --user= command line option.'
        )
        sys.exit(2)
    user = _safe_get('user', user_name)

    try:
        CONFIG['token'] = (
            os.environ.get('OPENTF_TOKEN') or _get_value('--token=') or user['token']
        )
        CONFIG['orchestrator'] = orchestrator
        CONFIG['orchestrator']['insecure-skip-tls-verify'] = CONFIG['orchestrator'].get(
            'insecure-skip-tls-verify', False
        ) or (_get_value('--insecure-skip-tls-verify=') == 'true')
        HEADERS['Authorization'] = 'Bearer ' + CONFIG['token']
    except Exception as err:
        _error('Could not read configuration: %s.', err)
        sys.exit(2)


########################################################################
# Helpers


def _get_port(service, default):
    port = (
        _get_value(f'--orchestrator-{service}-port=')
        or input(f'Please specify the {service} port ({default}): ').strip()
        or default
    )
    try:
        return int(port)
    except ValueError as err:
        _error('Not a valid port value: %s', err)
        sys.exit(2)


########################################################################
# Commands

## config commands
def config_cmd():
    """Interact with opentf-config.

    Possible sub commands are
        generate             Generate configuration file from user inputs
        set-context          Set a context entry in the opentf-config
        set-orchestrator     Set an orchestrator entry in the opentf-config
        set-credentials      Set a user entry in the opentf-config
        delete-context       Unset a context entry in the opentf-config
        delete-orchestrator  Unset an orchestrator entry in the opentf-config
        delete-credentials   Unset a user entry in the opentf-config
        view                 Display current opentf-config
    """
    if _is_command('config generate', sys.argv):
        generate_config()
    elif _is_command('config use-context _', sys.argv):
        use_context(sys.argv[3])
    elif _is_command('config set-context _', sys.argv):
        set_context(sys.argv[3])
    elif _is_command('config set-orchestrator _', sys.argv):
        set_orchestrator(sys.argv[3])
    elif _is_command('config set-credentials _', sys.argv):
        set_credentials(sys.argv[3])
    elif _is_command('config delete-context _', sys.argv):
        delete_context(sys.argv[3])
    elif _is_command('config delete-orchestrator _', sys.argv):
        delete_orchestrator(sys.argv[3])
    elif _is_command('config delete-credentials _', sys.argv):
        delete_credentials(sys.argv[3])
    elif _is_command('config view', sys.argv):
        view_config()
    else:
        _error(
            'Unknown subcommand.  Use "opentf-ctl config --help" to list known subcommands.'
        )
        sys.exit(1)


def _write_opentfconfig(conf_filename, config):
    with open(conf_filename, 'w', encoding='utf-8') as conffile:
        yaml.safe_dump(config, conffile)


def _read_opentfconfig():
    conf_filename = (
        _get_value('--opentfconfig=')
        or os.environ.get('OPENTF_CONFIG')
        or os.path.expanduser('~/.opentf/config')
    )
    try:
        with open(conf_filename, 'r', encoding='utf-8') as conffile:
            config = yaml.safe_load(conffile)
    except Exception as err:
        _error('Could not read configuration file %s: %s.', conf_filename, err)
        _error(
            'You may generate a configuration file using the "opentf-ctl config generate" subcommand.  Use "opentf-ctl config generate --help" for usage.'
        )
        sys.exit(2)
    return conf_filename, config


def _ensure_name_exists(name, label, config, src):
    names = [item['name'] for item in config[f'{label}s']]
    if name not in names:
        _error(
            '%s %s does not exist in configuration file %s.',
            label.title(),
            repr(name),
            repr(src),
        )
        _error('Available %ss: %s.', label, ','.join(names))
        sys.exit(2)


# Contexts


def use_context(context):
    """Change current context."""
    conf_filename, config = _read_opentfconfig()
    try:
        _ensure_name_exists(context, 'context', config, conf_filename)
        config['current-context'] = context
        _write_opentfconfig(conf_filename, config)
    except Exception as err:
        _error('Could not modify configuration file %s: %s.', conf_filename, err)
        sys.exit(2)


def set_context(context):
    """Create or update context."""
    conf_filename, config = _read_opentfconfig()
    try:
        if context == '--current':
            if 'current-context' not in config:
                _error(
                    'No current context defined in configuration file %s.',
                    conf_filename,
                )
                _error(
                    'You can use the "opentf-ctl config use-context" subcommand to define a default context.'
                )
                sys.exit(2)
            context = config.get('current-context')
        contexts = {item['name']: item for item in config['contexts']}
        if context not in contexts:
            entry = {'context': {}, 'name': context}
            contexts[context] = entry
            config['contexts'].append(entry)
            msg = f'Context "{context}" created in {conf_filename}.'
        else:
            msg = f'Context "{context}" modified in {conf_filename}.'
        if orchestrator := _get_value('--orchestrator='):
            _ensure_name_exists(orchestrator, 'orchestrator', config, conf_filename)
            contexts[context]['context']['orchestrator'] = orchestrator
        if user := _get_value('--user='):
            _ensure_name_exists(user, 'user', config, conf_filename)
            contexts[context]['context']['user'] = user
        if namespace := _get_value('--namespace='):
            contexts[context]['context']['namespace'] = namespace
        _write_opentfconfig(conf_filename, config)
        print(msg)
    except Exception as err:
        _error('Could not modify configuration file %s: %s.', conf_filename, err)
        sys.exit(2)


def delete_context(context):
    """Delete context."""
    conf_filename, config = _read_opentfconfig()
    try:
        _ensure_name_exists(context, 'context', config, conf_filename)
        config['contexts'] = [
            item for item in config['contexts'] if item['name'] != context
        ]
        _write_opentfconfig(conf_filename, config)
        print(f'Deleted context "{context}" from {conf_filename}.')
    except Exception as err:
        _error('Could not modify configuration file %s: %s.', conf_filename, err)
        sys.exit(2)


# Credentials


def set_credentials(user):
    """Create or update user entry."""
    conf_filename, config = _read_opentfconfig()
    try:
        users = {item['name']: item for item in config['users']}
        if user not in users:
            entry = {'user': {}, 'name': user}
            users[user] = entry
            config['users'].append(entry)
        if token := _get_value('--token='):
            users[user]['user']['token'] = token
        _write_opentfconfig(conf_filename, config)
        print(f'User "{user}" set in {conf_filename}.')
    except Exception as err:
        _error('Could not modify configuration file %s: %s.', conf_filename, err)
        sys.exit(2)


def delete_credentials(user):
    """Delete user."""
    conf_filename, config = _read_opentfconfig()
    try:
        _ensure_name_exists(user, 'user', config, conf_filename)
        config['users'] = [item for item in config['users'] if item['name'] != user]
        _write_opentfconfig(conf_filename, config)
        print(f'Deleted user "{user}" from {conf_filename}.')
    except Exception as err:
        _error('Could not modify configuration file %s: %s.', conf_filename, err)
        sys.exit(2)


# Orchestrators


def set_orchestrator(orchestrator):
    """Create or update orchestrator."""
    conf_filename, config = _read_opentfconfig()
    try:
        orchestrators = {item['name']: item for item in config['orchestrators']}
        if orchestrator not in orchestrators:
            entry = {'orchestrator': {}, 'name': orchestrator}
            orchestrators[orchestrator] = entry
            config['orchestrators'].append(entry)
            msg = f'Orchestrator "{orchestrator}" created in {conf_filename}.'
        else:
            msg = f'Orchestrator "{orchestrator}" modified in {conf_filename}.'
        if verify := _get_value('--insecure-skip-tls-verify='):
            orchestrators[orchestrator]['orchestrator']['insecure-skip-tls-verify'] = (
                verify.lower() == 'true'
            )
        if server := _get_value('--server='):
            orchestrators[orchestrator]['orchestrator']['server'] = server

        ports = {}
        for svc in [
            'receptionist',
            'observer',
            'killswitch',
            'eventbus',
            'agentchannel',
        ]:
            if port := _get_value(f'--{svc}-port='):
                try:
                    port = int(port)
                except ValueError:
                    _error('%s port must be an integer: %s.', svc.title(), repr(port))
                    sys.exit(2)
                ports[svc] = port
        if ports:
            orchestrators[orchestrator]['orchestrator'].setdefault('ports', {})
            for svc, port in ports.items():
                orchestrators[orchestrator]['orchestrator']['ports'][svc] = int(port)

        _write_opentfconfig(conf_filename, config)
        print(msg)
    except Exception as err:
        _error('Could not modify configuration file %s: %s.', conf_filename, err)
        sys.exit(2)


def delete_orchestrator(orchestrator):
    """Delete orchestrator."""
    conf_filename, config = _read_opentfconfig()
    try:
        _ensure_name_exists(orchestrator, 'orchestrator', config, conf_filename)
        config['orchestrators'] = [
            item for item in config['orchestrators'] if item['name'] != orchestrator
        ]
        _write_opentfconfig(conf_filename, config)
        print(f'Deleted orchestrator "{orchestrator}" from {conf_filename}.')
    except Exception as err:
        _error('Could not modify configuration file %s: %s.', conf_filename, err)
        sys.exit(2)


def view_config():
    """Display currently used configuration file in stdout.

    The configuration is found using, in priority

    - the `--opentfconfig=` argument value
    - the `OPENTF_CONFIG` environment variable
    - the current user configuration located at `~/.opentf/config`

    # Raised exception

    Exits violently with error code 2 if no configuration file is found
    """
    _, config = _read_opentfconfig()
    for user in config['users']:
        if user.get('user', {}).get('token'):
            user['user']['token'] = 'REDACTED'
    print(yaml.dump(config))


def generate_config():
    """
    Generate a config file from user input

    Configuration file is a kubeconfig-like file, in YAML:

    ```yaml
    apiVersion: opentestfactory.org/v1alpha1
    kind: CtlConfig
    current-context: default
    contexts:
    - context:
        orchestrator: default
        user: default
      name: default
    orchestrators:
    - name: default
      orchestrator:
        insecure-skip-tls-verify: true
        server: http://localhost
        ports:
          receptionist: 7774
          observer: 7775
          killswitch: 7776
          eventbus: 38368
    users:
    - name: default
      user:
        token: ey...
    ```

    Optional command-line options:

    --name="
    --orchestrator-server=''
    --orchestrator-receptionist-port=''
    --orchestrator-observer-port=''
    --orchestrator-eventbus-port=''
    --orchestrator-killswitch-port=''
    --orchestrator-agentchannel-port=''
    --insecure-skip-tls-verify=false|true
    --token="
    """

    generated_conf = {'apiVersion': 'opentestfactory.org/v1alpha1', 'kind': 'CtlConfig'}

    name = (
        _get_value('--name=')
        or (input('Please specify a nickname for the orchestrator (default): ').strip())
        or 'default'
    )

    server = _get_value('--orchestrator-server=')
    while not server:
        server = input('Please specify the orchestrator server: ').strip()

    receptionist_port = _get_port('receptionist', 7774)
    eventbus_port = _get_port('eventbus', 38368)
    observer_port = _get_port('observer', 7775)
    killswitch_port = _get_port('killswitch', 7776)
    agentchannel_port = _get_port('agentchannel', 24368)

    skip_tls_verify = (
        _get_value('--insecure-skip-tls-verify=')
        or (input('Skip TLS verification (false): ').strip())
        or False
    )
    try:
        skip_tls_verify = bool(skip_tls_verify)
    except ValueError as err:
        _error('Not a valid insecure-skip-tls-verify flag: %s.', err)
        sys.exit(2)

    token = _get_value('--token=')
    while not token:
        token = input('Please specify the token: ').strip()

    contexts = [{'name': name, 'context': {'orchestrator': name, 'user': name}}]

    generated_conf['contexts'] = contexts
    generated_conf['current-context'] = name

    orchestrators = [
        {
            'name': name,
            'orchestrator': {
                'insecure-skip-tls-verify': skip_tls_verify,
                'server': server,
                'ports': {
                    'receptionist': receptionist_port,
                    'observer': observer_port,
                    'eventbus': eventbus_port,
                    'killswitch': killswitch_port,
                    'agentchannel': agentchannel_port,
                },
            },
        }
    ]

    generated_conf['orchestrators'] = orchestrators

    users = [{'name': name, 'user': {'token': token}}]

    generated_conf['users'] = users

    print('#')
    print('# Generated opentfconfig')
    print('# (generated by opentf-ctl version %s)' % version('opentf-tools'))
    print('#')

    print(yaml.dump(generated_conf))


def print_config_help(args):
    """Display config help."""
    if _is_command('config generate', args):
        print(CONFIG_GENERATE_HELP)
    elif _is_command('config use-context', args):
        print(CONFIG_USE_CONTEXT_HELP)
    elif _is_command('config set-context', args):
        print(CONFIG_SET_CONTEXT_HELP)
    elif _is_command('config set-orchestrator', args):
        print(CONFIG_SET_ORCHESTRATOR_HELP)
    elif _is_command('config set-credentials', args):
        print(CONFIG_SET_CREDENTIALS_HELP)
    elif _is_command('config delete-context', args):
        print(CONFIG_DELETE_CONTEXT_HELP)
    elif _is_command('config delete-orchestrator', args):
        print(CONFIG_DELETE_ORCHESTRATOR_HELP)
    elif _is_command('config delete-credentials', args):
        print(CONFIG_DELETE_CREDENTIALS_HELP)
    elif _is_command('config view', args):
        print(CONFIG_VIEW_HELP)
    elif _is_command('config', args):
        print(CONFIG_HELP)
    else:
        _error('Unknown config command.  Use --help to list known commands.')
        sys.exit(1)

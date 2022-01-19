"""
    lager.config

    Config file management routines
"""
import os
import configparser
import click

DEFAULT_CONFIG_FILE_NAME = '.lager'
LAGER_CONFIG_FILE_NAME = os.getenv('LAGER_CONFIG_FILE_NAME', DEFAULT_CONFIG_FILE_NAME)

DEVENV_SECTION_NAME = 'DEVENV'


def get_global_config_file_path():
    if 'LAGER_CONFIG_FILE_DIR' in os.environ:
        return make_config_path(os.getenv('LAGER_CONFIG_FILE_DIR'))
    return make_config_path(os.path.expanduser('~'))

def make_config_path(directory, config_file_name=None):
    """
        Make a full path to a lager config file
    """
    if config_file_name is None:
        config_file_name = LAGER_CONFIG_FILE_NAME

    return os.path.join(directory, config_file_name)

def find_devenv_config_path():
    """
        Find a local .lager config, if it exists
    """
    configs = _find_config_files()
    if not configs:
        return None
    return configs[0]

def _find_config_files():
    """
        Search up from current directory for all .lager files
    """
    cwd = os.getcwd()
    cfgs = []
    global_config_file_path = get_global_config_file_path()
    while True:
        config_path = make_config_path(cwd)
        if os.path.exists(config_path) and config_path != global_config_file_path:
            cfgs.append(config_path)
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent

    return cfgs


def read_config_file(path=None):
    """
        Read our config file into `config` object
    """
    if path is None:
        path = get_global_config_file_path()
    config = configparser.SafeConfigParser()
    try:
        with open(path) as f:
            config.read_file(f)
    except FileNotFoundError:
        pass

    if 'LAGER' not in config:
        config.add_section('LAGER')
    return config

def write_config_file(config, path=None):
    """
        Write out `config` into our config file
    """
    if path is None:
        path = get_global_config_file_path()
    with open(path, 'w') as f:
        config.write(f)

def add_devenv_command(section, command_name, command, warn):
    """
        Add a named command to devenv
    """
    key = f'cmd.{command_name}'
    if key in section and warn:
        click.echo(f'Command `{command_name}` already exists, overwriting. ', nl=False, err=True)
        click.echo(f'Previous value: {section[key]}', err=True)
    section[key] = command

def remove_devenv_command(section, command_name):
    """
        Delete a named command
    """
    key = f'cmd.{command_name}'
    if key not in section:
        click.secho(f'Command `{command_name}` does not exist.', fg='red', err=True)
        click.get_current_context().exit(1)
    del section[key]

def all_commands(section):
    """
        Get a map of command name -> command for all commands in the section
    """
    return {
        k.split('.', 1)[1]: section[k] for k in section.keys() if k.startswith('cmd.')
    }

def get_devenv_config():
    """
        Return a path and config file for devenv
    """
    config_path = find_devenv_config_path()
    if config_path is None:
        click.echo(f'Could not find {LAGER_CONFIG_FILE_NAME} in {os.getcwd()} or any parent directories', err=True)
        click.get_current_context().exit(1)
    config = read_config_file(config_path)
    return config_path, config

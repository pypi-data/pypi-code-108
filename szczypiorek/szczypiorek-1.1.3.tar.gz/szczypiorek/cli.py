
from glob import glob
import os
import re
import importlib
import json

import click

from .utils import load_yaml, dump_yaml
from .git import assert_is_git_ignored
from .exceptions import BaseException, normalize
from . import crypto
from .constants import (
    ENVIRONMENT_FILE_ENV_NAME,
    ENVIRONMENT_DEFAULT,
)


def cast(value: str):
    if value.lower() in ['true', 'false']:
        return value == 'true'

    elif re.search(r'^\d+$', value):
        return int(value)

    elif re.search(r'^\d+\.\d+$', value):
        return float(value)

    return value


@click.group()
def cli():
    """Expose multiple commands allowing one to work with szczypiorek."""
    pass


@click.command()
@click.argument('env_path')
def print_env(env_path):
    """Print currently loaded env variables into stdout."""

    def hide_sensitive(name, value):
        if (name.endswith('password') or
                name.endswith('key') or
                name.endswith('secret')):
            return 10 * '*'

        return value

    env_path_parts = env_path.split('.')
    env_path = '.'.join(env_path_parts[:-1])
    env_variable = env_path_parts[-1]
    env = getattr(importlib.import_module(env_path), env_variable)
    for k, v in env.env.items():
        v = hide_sensitive(k, v)

        try:
            if isinstance(json.loads(v), dict):
                v = json.loads(v)
                for kk, vv in v.items():
                    v[kk] = hide_sensitive(kk, vv)

                v = json.dumps(v, indent=4)

        except (json.decoder.JSONDecodeError, TypeError):
            pass

        click.echo(f'{k}: {v}')


@click.command()
@click.argument('path')
@click.option('--key_filepath', '-k')
def encrypt(path, key_filepath=None):
    """Encrypt all yml files in a given path."""

    if os.path.isdir(path):
        filepaths = sorted(
            glob(os.path.join(path, '*.yml')) +
            glob(os.path.join(path, '*.yaml')))

    else:
        filepaths = [path]

    for filepath in filepaths:
        _encrypt_single(filepath, key_filepath=key_filepath)


@click.command()
@click.argument('path')
@click.option('--key_filepath', '-k')
def decrypt(path, key_filepath=None):
    if os.path.isdir(path):
        filepaths = glob(os.path.join(path, '*.szczyp'))

    else:
        filepaths = [path]

    for filepath in filepaths:
        _decrypt_single(filepath, key_filepath=key_filepath)


@click.command()
@click.option(
    '--replacement',
    '-r',
    multiple=True,
    help='One can specify many of those')
@click.option(
    '--path',
    '-p',
    help='Optional path to the specific .szczyp file')
@click.option(
    '--key_filepath',
    '-k',
    help='Optional path to the specific encryption key')
def replace(replacement, path=None, key_filepath=None):
    """
    Replace values in the stored encoded yaml.

    One should pass the replacement patterns as in the example below:

    szczypiorek replace -r a.b.c:123 -r a.g:67

    Which would lead to the following replacements:
    - under key `c` inside `b` inside `c` value 123 would be set
    - under key `g` inside `c` value 76 would be set

    """
    if not replacement:
        return

    for r in replacement:
        if not re.search(r'^[\w\d\.\_]+\:.+$', r):
            raise click.ClickException(normalize(f'''
                The replacement `{r}` does not follow required syntax.
            '''))

    szczyp_filepath = path
    if not szczyp_filepath:
        szczyp_filepath = os.environ.get(
            ENVIRONMENT_FILE_ENV_NAME,
            ENVIRONMENT_DEFAULT)

    # -- decrypt
    try:
        yml_filepath, content = _decrypt_single(
            szczyp_filepath, key_filepath=key_filepath)

    except FileNotFoundError:
        raise click.ClickException(normalize(f'''
            It seems that the file `{szczyp_filepath}` does not exist.
        '''))

    # -- replacements
    content = load_yaml(content)
    for c in content:
        for r in replacement:
            try:
                k, v = r.split(':')
                keys = k.split('.')
                current = c
                for key in keys[:-1]:
                    current = current[key]

                current[keys[-1]] = cast(v)

            except KeyError:
                raise click.ClickException(normalize(f'''
                    It seems that the path `{k}` does not exist. Check if it's
                    correct.
                '''))

    with open(yml_filepath, 'w') as f:
        f.write(dump_yaml(content))

    # -- encrypt
    _encrypt_single(yml_filepath, key_filepath=key_filepath, with_checks=False)
    os.remove(yml_filepath)


def _encrypt_single(filepath, key_filepath=None, with_checks=True):
    with open(filepath, 'r') as f:
        szczyp_filepath = re.sub(
            r'(\.yml|\.yaml)', '.szczyp', filepath)

        click.secho(f'[ENCRYPTING] {filepath}', color='green')

        try:
            if with_checks:
                assert_is_git_ignored(filepath)

            content = f.read()
            # -- used here only to validate
            load_yaml(content)
            content = crypto.encrypt(content, key_filepath)

        except BaseException as e:
            raise click.ClickException(e.args[0])

        # -- WRITE at the end when it's certain that all went well
        with open(szczyp_filepath, 'w') as g:
            g.write(content)


def _decrypt_single(filepath, key_filepath=None):

    with open(filepath, 'r') as f:
        yml_filepath = filepath.replace('.szczyp', '.yml')
        click.secho(f'[DECRYPTING] {filepath}', color='green')

        try:
            content = crypto.decrypt(f.read(), key_filepath)

        except BaseException as e:
            raise click.ClickException(e.args[0])

        # -- WRITE at the end when it's certain that all went well
        with open(yml_filepath, 'w') as g:
            g.write(content)

        return yml_filepath, content


cli.add_command(encrypt)
cli.add_command(decrypt)
cli.add_command(print_env)
cli.add_command(replace)

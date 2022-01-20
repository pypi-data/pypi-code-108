
import os

import click

from .fields import BaseField
from .crypto import decrypt
from .utils import load_yaml, flatten, substitute
from .constants import (
    ENVIRONMENT_ENV_NAME,
    ENVIRONMENT_FILE_ENV_NAME,
    ENVIRONMENT_DEFAULT,
)


class Env:

    def __init__(self, **env):
        for k, v in env.items():
            setattr(self, k, v)

        self.env = env


class EnvParser:

    _envs_gpg_cache = {}

    document_idx = 0

    @property
    def fields(self):
        fields = {}
        for name in dir(self):
            if name != 'fields':
                attr = getattr(self, name)
                if isinstance(attr, BaseField):
                    fields[name] = attr

        return fields

    def parse(self):

        env_key, env_from_gpg = self.get_env_from_gpg()

        click.secho(f'[PARSING] {env_key}', color='green')
        env_variables = {}
        for field_name, field in self.fields.items():
            if field.required:
                raw_value = env_from_gpg[field_name]

            else:
                raw_value = env_from_gpg.get(field_name, field.default)

            env_variables[field_name] = (
                field.to_python(field_name, raw_value))

            if field.as_env:
                if isinstance(field.as_env, str):
                    env_name = field.as_env

                else:
                    env_name = field_name.upper()

                os.environ[env_name] = env_variables[field_name]

            if field.as_file:
                if isinstance(field.as_file, str):
                    file_name = field.as_file

                else:
                    file_name = field_name

                with open(file_name, 'w') as f:
                    f.write(env_variables[field_name])

        return Env(**env_variables)

    def get_env_from_gpg(self):

        env_from_gpg = os.environ.get(ENVIRONMENT_ENV_NAME)
        env_key = (
            f'{self.__class__.__module__}.'
            f'{self.__class__.__name__}'
            f'(environ.{ENVIRONMENT_ENV_NAME})')

        if not env_from_gpg:
            env_path = os.environ.get(
                ENVIRONMENT_FILE_ENV_NAME,
                ENVIRONMENT_DEFAULT)
            env_key = (
                f'{self.__class__.__module__}.'
                f'{self.__class__.__name__}'
                f'({env_path})')

            env_from_gpg = EnvParser._envs_gpg_cache.get(env_path)
            if not env_from_gpg:
                click.secho(f'[LOADING] {env_path}', color='green')
                with open(env_path, 'r') as f:
                    env_from_gpg = f.read()

                EnvParser._envs_gpg_cache[env_path] = env_from_gpg

        env_from_gpg = decrypt(env_from_gpg)
        env_from_gpg = load_yaml(env_from_gpg)

        if isinstance(env_from_gpg, list):
            env_from_gpg = env_from_gpg[self.document_idx]

        env_from_gpg = flatten(env_from_gpg)
        env_from_gpg = substitute(env_from_gpg)

        return env_key, env_from_gpg

from __future__ import annotations
from base64 import b64decode, b64encode
from io import StringIO
import json
import os
from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML

from anylearn.cli.errors import ConfigurationKeyError, NameConflictError
from anylearn.interfaces import (
    Algorithm,
    Dataset,
    Project,
    ResourceVisibility,
)


class AnylearnCliConfig:

    remote: dict = {
        'host': None,
        'username': None,
        'password': None,
    }
    project: Optional[Project] = None
    algorithms: dict[str, Algorithm] = {}
    datasets: dict[str, Dataset] = {}
    path: dict[str, dict[str, str]] = {
        'algorithm': {},
        'dataset': {},
    }
    images: dict[str, str] = {}

    def gets(self, config_key: str):
        funcs, keys = self.__parse_config_key(config_key=config_key)
        try:
            return funcs['get'](keys=keys)
        except Exception as e:
            if not str(e):
                raise ConfigurationKeyError(f"Unknown configuration key {config_key}")
            raise

    def sets(self, config_key: str, value):
        funcs, keys = self.__parse_config_key(config_key=config_key)
        try:
            funcs['set'](keys=keys, value=value)
        except Exception as e:
            if not str(e):
                raise ConfigurationKeyError(f"Unknown configuration key {config_key}")
            raise

    def __parse_config_key(self, config_key: str):
        parts = config_key.split('.')
        if not parts:
            raise ConfigurationKeyError("Configuration key required.")
        meta_key = parts[0]
        mapping = {
            'project': {
                'get': self.__get_in_project,
                'set': self.__set_in_project,
            },
            'algorithms': {
                'get': self.__get_in_algorithms,
                'set': self.__set_in_algorithms,
            },
            'datasets': {
                'get': self.__get_in_datasets,
                'set': self.__set_in_datasets,
            },
            'path': {
                'get': self.__get_in_path,
                'set': self.__set_in_path,
            },
            'images': {
                'get': self.__get_in_images,
                'set': self.__set_in_images,
            }
        }
        if meta_key not in mapping.keys():
            raise ConfigurationKeyError(f"Unknown configuration key {config_key}")
        del(parts[0])
        return mapping[meta_key], parts

    def __get_in_project(self, keys: list):
        if not keys or len(keys) != 1:
            raise ConfigurationKeyError
        return getattr(self.project, keys[0])

    def __set_in_project(self, keys: list, value):
        if not keys or len(keys) != 1:
            raise ConfigurationKeyError
        setattr(self.project, keys[0], value)

    def __get_in_algorithms(self, keys: list):
        if not keys or len(keys) != 2:
            raise ConfigurationKeyError
        return getattr(self.algorithms[keys[0]], keys[1])

    def __set_in_algorithms(self, keys: list, value):
        if not keys or len(keys) != 2:
            raise ConfigurationKeyError
        if keys[1] == 'name':
            if value in self.algorithms:
                raise NameConflictError(
                    f"Failed to rename algorithm {keys[0]} to {value}: "
                    f"algorithm {value} already added in current project."
                )
            self.algorithms[keys[0]].name = value
            self.algorithms[value] = self.algorithms[keys[0]]
            self.path['algorithm'][value] = self.path['algorithm'][keys[0]]
            del(self.algorithms[keys[0]])
            del(self.path['algorithm'][keys[0]])
        else:
            setattr(self.algorithms[keys[0]], keys[1], value)

    def __get_in_datasets(self, keys: list):
        if not keys or len(keys) != 2:
            raise ConfigurationKeyError
        return getattr(self.datasets[keys[0]], keys[1])

    def __set_in_datasets(self, keys: list, value):
        if not keys or len(keys) != 2:
            raise ConfigurationKeyError
        if keys[1] == 'name':
            if value in self.datasets:
                raise NameConflictError(
                    f"Failed to rename dataset {keys[0]} to {value}: "
                    f"dataset {value} already added in current project."
                )
            self.datasets[keys[0]].name = value
            self.datasets[value] = self.datasets[keys[0]]
            self.path['dataset'][value] = self.path['dataset'][keys[0]]
            del(self.datasets[keys[0]])
            del(self.path['dataset'][keys[0]])
        else:
            setattr(self.datasets[keys[0]], keys[1], value)

    def __get_in_path(self, keys: list):
        if not keys or len(keys) != 2 or not keys[0] in self.path:
            raise ConfigurationKeyError
        return self.path[keys[0]][keys[1]]

    def __set_in_path(self, keys: list, value: str):
        if not keys or len(keys) != 2 or not keys[0] in self.path:
            raise ConfigurationKeyError
        self.path[keys[0]][keys[1]] = value

    def __get_in_images(self, keys: list):
        if not keys or len(keys) != 1 or not keys[0] in self.images:
            raise ConfigurationKeyError
        return self.images[keys[0]]

    def __set_in_images(self, keys: list, value: str):
        if not keys or len(keys) != 1 or not keys[0] in self.images:
            raise ConfigurationKeyError
        self.images[keys[0]] = value

    def __str__(self) -> str:
        yaml = YAML()
        with StringIO() as stream:
            yaml.dump(AnylearnCliConfig.serialize(config=self), stream)
            s = stream.getvalue()
        return s

    @staticmethod
    def serialize(config: AnylearnCliConfig) -> dict:
        config_dict = {}
        config_dict['auth'] = AnylearnCliConfig.remote2auth(config.remote)
        config_dict['project'] = {} if not config.project else {
            'id': config.project.id,
            'name': config.project.name,
            'description': config.project.description,
        }
        config_dict['algorithms'] = {
            algo_name: {
                'id': algo.id,
                'name': algo.name,
                'description': algo.description,
                'visibility': algo.visibility,
                'train_params': algo.train_params,
                'evaluate_params': algo.evaluate_params,
                'follows_anylearn_norm': algo.follows_anylearn_norm,
                'entrypoint_training': algo.entrypoint_training,
                'entrypoint_evaluation': algo.entrypoint_evaluation,
                'output_training': algo.output_training,
                'output_evaluation': algo.output_evaluation,
            }
            for algo_name, algo in config.algorithms.items()
        }
        config_dict['datasets'] = {
            dset_name: {
                'id': dset.id,
                'name': dset.name,
                'description': dset.description,
                'visibility': dset.visibility,
            }
            for dset_name, dset in config.datasets.items()
        }
        config_dict['path'] = config.path
        config_dict['images'] = config.images
        return config_dict

    @staticmethod
    def deserialize(config_dict: dict) -> AnylearnCliConfig:
        proj_dict = config_dict.get('project', {})
        algorithms = config_dict.get('algorithms', {})
        datasets = config_dict.get('datasets', {})
        path = config_dict.get('path', {
            'algorithm': {},
            'dataset': {},
        })
        images = config_dict.get('images', {})
        config = AnylearnCliConfig()
        config.remote = AnylearnCliConfig.auth2remote(config_dict['auth'])
        config.project = Project(
            id=proj_dict.get('id', None),
            name=proj_dict.get('name', None),
            description=proj_dict.get('description', None),
        )
        config.algorithms = {
            algo_name: Algorithm(
                id=algo_dict.get('id', None),
                name=algo_dict.get('name', None),
                description=algo_dict.get('description', None),
                visibility=algo_dict.get('visibility',
                                         ResourceVisibility.PRIVATE),
                train_params=json.dumps(algo_dict.get('train_params', [])),
                evaluate_params=json.dumps(algo_dict.get('evaluate_params', [])),
                follows_anylearn_norm=algo_dict.get('follows_anylearn_norm', True),
                entrypoint_training=algo_dict.get('entrypoint_training', None),
                entrypoint_evaluation=algo_dict.get('entrypoint_evaluation', None),
                output_training=algo_dict.get('output_training', None),
                output_evaluation=algo_dict.get('output_evaluation', None),
            )
            for algo_name, algo_dict in algorithms.items()
        }
        config.datasets = {
            dset_name: Dataset(
                id=dset_dict.get('id', None),
                name=dset_dict.get('name', None),
                description=dset_dict.get('description', None),
                visibility=dset_dict.get('visibility',
                                            ResourceVisibility.PRIVATE),
            )
            for dset_name, dset_dict in datasets.items()
        }
        config.path = path
        config.images = images
        return config

    @staticmethod
    def auth2remote(auth_str: str):
        if not auth_str:
            return {
                'host': None,
                'username': None,
                'password': None,
            }
        s = b64decode(auth_str.encode('utf8')).decode('utf8')
        cred, host = s.split('@')
        username, p = cred.split(':')
        password = b64decode(p.encode('utf8')).decode('utf8')
        return {
            'host': host,
            'username': username,
            'password': password,
        }

    @staticmethod
    def remote2auth(remote: dict):
        if not all([
            'host' in remote and remote['host'],
            'username' in remote and remote['username'],
            'password' in remote and remote['password'],
        ]):
            return ''
        p = b64encode(remote['password'].encode('utf8')).decode('utf8')
        s = f"{remote['username']}:{p}@{remote['host']}"
        return b64encode(s.encode('utf8')).decode('utf8')

    @staticmethod
    def get_config_path() -> Path:
        cwd = Path(os.getcwd())
        config_path = cwd / 'AnylearnProject.yaml'
        return config_path

    @staticmethod
    def load():
        config_path = AnylearnCliConfig.get_config_path()
        if not config_path.exists():
            return AnylearnCliConfig()
        yaml = YAML()
        return AnylearnCliConfig.deserialize(config_dict=yaml.load(config_path))

    @staticmethod
    def update(config: AnylearnCliConfig):
        config_path = AnylearnCliConfig.get_config_path()
        config_path.touch(exist_ok=True)
        yaml = YAML()
        yaml.dump(AnylearnCliConfig.serialize(config=config), config_path)

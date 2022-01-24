import glob
import logging
import os
import pathlib
import random
import string
import sys
from abc import ABC
from distutils.dir_util import copy_tree
from distutils.file_util import copy_file
from shutil import copyfile
from typing import Any, List, Dict, Union

import numpy as np
import yaml

from baseten_scaffolding.constants import SERVING_DIR, CUSTOM, SKLEARN, PYTORCH, KERAS, HUGGINGFACE_TRANSFORMER
from baseten_scaffolding.model_inference import parse_requirements_file

logger = logging.getLogger(__name__)


def _validate(request):
    if ("instances" in request and not isinstance(request["instances"], (list, np.ndarray))) or \
            ("inputs" in request and not isinstance(request["inputs"], (list, np.ndarray))):
        raise Exception(
            reason="Expected \"instances\" or \"inputs\" to be a list"
        )
    return request


def prediction_flow(model, body):
    request = model.preprocess(body)
    request = _validate(request)
    response = model.predict(request)
    response = model.postprocess(response)
    return response



def _server_directory_name(model_framework: str):
    return f'{model_framework}_server'


def _server_cpu_dockerfile(model_framework: str):
    return f'{model_framework}-server.Dockerfile'


def _server_gpu_dockerfile(model_framework: str):
    return f'{model_framework}-server-gpu.Dockerfile'


def _has_gpu_dockerfile(model_framework: str):
    return os.path.exists(
        pathlib.Path(SERVING_DIR, 'docker', _server_gpu_dockerfile(model_framework)))


def _server_dockerfile(model_framework: str):
    if _has_gpu_dockerfile(model_framework):
        return _server_gpu_dockerfile(model_framework)
    return _server_cpu_dockerfile(model_framework)


def _serialize_files(files, directory):
    for _file in files:
        file_name = pathlib.PurePath(_file).name
        new_path = pathlib.PurePath(directory, file_name)
        copyfile(_file, new_path)


def _serialize_dirs(dirs: List[pathlib.Path], directory: pathlib.Path):
    for _dir in dirs:
        copy_tree(str(_dir.name), str(pathlib.Path(directory, _dir)))


MODEL_FOLDER = 'model'
DATA_FOLDER = 'data'
SRC_FOLDER = 'src'
COMMON_FOLDER = 'common'
DOCS_FOLDER = 'docs'
CONFIG_FILE = 'config.yaml'
REQUIREMENTS_FILE = 'requirements.txt'


def _files_and_dirs(glob_file_list: List[str]):
    files = []
    dirs = []
    for item in glob_file_list:
        if pathlib.Path(item).is_dir():
            dirs += [pathlib.Path(item)]
        else:
            files += glob.glob(item)
    return files, dirs


def _load_kf_model_for_model_framework(model_framework, model_dir, build_args):
    from common.lib_support import ensure_kfserving_installed
    ensure_kfserving_installed()

    if model_framework == SKLEARN:
        from server.inference_model import SKLearnModel
        kf_model = SKLearnModel(model_dir=model_dir)
    elif model_framework == PYTORCH:
        from server.inference_model import PyTorchModel
        kf_model = PyTorchModel(
            name='model',
            model_class_name=build_args['MODEL_CLASS'],
            model_class_file=build_args['MODEL_CLASS_DEFINITION_FILE'],
            model_dir=model_dir
        )
    elif model_framework == KERAS:
        from server.inference_model import KerasModel
        kf_model = KerasModel(model_dir=model_dir)
    elif model_framework == CUSTOM:
        from server.inference_model import CustomBasetenModel
        kf_model = CustomBasetenModel(
            name='model',
            model_class_name=build_args['MODEL_CLASS'],
            model_class_file=build_args['MODEL_CLASS_DEFINITION_FILE'],
            model_dir=model_dir
        )
    elif model_framework == HUGGINGFACE_TRANSFORMER:
        from server.inference_model import TransformerModel
        kf_model = TransformerModel(
            name='model',
            task=build_args['hf_task'],
            has_named_args=build_args.get('has_named_args', False),
            has_hybrid_args=build_args.get('has_hybrid_args', False),
        )
    kf_model.load()
    return kf_model


class AbstractModelScaffoldDefinition(ABC):
    """
    Abstract definition of a Scaffold Object in memory. Provides the high level interface and describes the pieces
    required for using a scaffold
    """
    model_framework = None

    @property
    def dockerfile_path(self):
        return str(pathlib.Path(self.scaffold_dir, self.dockerfile))

    @property
    def scaffold_model_dir(self):
        return str(pathlib.Path(self.scaffold_src_dir, MODEL_FOLDER))

    @property
    def scaffold_src_dir(self):
        return str(pathlib.Path(self.scaffold_dir, SRC_FOLDER))

    @property
    def dockerfile(self):
        return _server_dockerfile(self.model_framework)

    @property
    def model_framework_requirements(self) -> Dict:
        raise NotImplementedError()

    @property
    def build_args(self) -> Dict:
        raise NotImplementedError()

    @property
    def docker_build_arg_string(self) -> str:
        if not self.build_args:
            return ''
        return ' '.join(f'--build-arg {key}={val}' for key, val in self.build_args.items())

    @property
    def docker_build_string(self) -> str:
        return f'docker build {self.docker_build_arg_string} -f {self.dockerfile_path} {self.scaffold_dir}'

    def config(self):
        return {
            'model_framework': self.model_framework,
            'model_type': self.model_type,
            'dockerfile': self.dockerfile,
            'build_args': self.build_args
        }

    def server_predict(self, request: Dict):
        if not self.kf_model:
            self._load_scaffold_model()
        return prediction_flow(self.kf_model, request)

    def predict(self, instances: Union[list, np.array]):
        return self.server_predict({'instances': instances})

    def _load_scaffold_model(self):
        self.kf_model = _load_kf_model_for_model_framework(
            self.model_framework,
            self.scaffold_model_dir,
            self.build_args
        )


class ReadModelScaffoldDefinition(AbstractModelScaffoldDefinition):
    """
    A class for representing an existing scaffold directory.

    It will load the existing scaffold directory correctly provided that the `config.yaml` is existing
    """

    def __init__(
            self,
            scaffold_directory: str
    ):
        if pathlib.Path(scaffold_directory, CONFIG_FILE).exists():
            with open(pathlib.Path(scaffold_directory, CONFIG_FILE), 'r') as config_file:
                self._config = yaml.safe_load(config_file)
        else:
            self._config = {}

        self.scaffold_dir = scaffold_directory
        self._build_args = self._load_build_args()
        self._dockerfile = self._load_dockerfile()
        self.requirements_file = self._load_requirements_file()
        self.model_type = self._load_model_type()
        self.model_framework = self._config.get('model_framework', None)
        self.kf_model = None
        sys.path.append(str(self.scaffold_src_dir))

    def _load_build_args(self):
        return self._config.get('build_args', {})

    def _load_dockerfile(self):
        return self._config.get('dockerfile', '')

    def _load_requirements_file(self):
        return pathlib.Path(self.scaffold_dir, REQUIREMENTS_FILE)

    def _load_model_type(self):
        return self._config.get('model_type', CUSTOM)

    @property
    def model_framework_requirements(self) -> Dict:
        return parse_requirements_file(self.requirements_file)

    @property
    def build_args(self) -> Dict:
        return self._build_args

    @property
    def dockerfile(self):
        return self._dockerfile


class WrittenModelScaffoldDefinition(AbstractModelScaffoldDefinition):
    """
    A base class for representing a scaffold in memory that will be written.

    All inheriting classes will have to implement the required functionality for `_build_scaffold_directory` to execute,
    mainly `model_framework_requirements` and `serialize_model_to_directory`
    """
    def __init__(
            self,
            model: Any,
            model_type: str = CUSTOM,
            model_files: List[str] = None,
            data_files: List[str] = None,
            path_to_scaffold: str = None,
            requirements_file: str = None,
    ):
        self.model = model
        if model_files is None:
            model_files = []
        if data_files is None:
            data_files = []
        self.model_files = model_files
        self.data_files = data_files
        self.model_type = model_type
        self.requirements_file = requirements_file
        self.scaffold_dir = self._build_scaffold_directory(path_to_scaffold)
        self._write_config()
        self.kf_model = None
        sys.path.append(str(self.scaffold_src_dir))

    @property
    def model_framework_requirements(self) -> Dict:
        raise NotImplementedError()

    @property
    def build_args(self) -> Dict:
        raise NotImplementedError()

    def _write_config(self):
        with open(pathlib.Path(self.scaffold_dir, CONFIG_FILE), 'w') as config_file:
            yaml.dump(self.config(), config_file)

    def _build_scaffold_directory(self, path_to_scaffold: str = None):
        if path_to_scaffold is None:
            rand_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            target_directory_path = pathlib.Path(
                pathlib.Path.home(),
                '.baseten',
                f'{self.model_framework}-{rand_suffix}'

            )
            target_directory_path.mkdir(parents=True)
            target_directory = str(target_directory_path)
        else:
            pathlib.Path(path_to_scaffold).mkdir(parents=True)
            target_directory = path_to_scaffold

        scaffold_model_dir = pathlib.Path(target_directory, SRC_FOLDER, MODEL_FOLDER)
        data_model_dir = pathlib.Path(target_directory, SRC_FOLDER, DATA_FOLDER)

        # folder for the model serialization
        pathlib.Path(target_directory, SRC_FOLDER).mkdir()
        scaffold_model_dir.mkdir()

        # ensure the model dir has an __init__.py
        open(pathlib.Path(scaffold_model_dir, '__init__.py'), 'a').close()
        model_files, model_dirs = _files_and_dirs(self.model_files)
        _serialize_files(model_files, scaffold_model_dir)
        _serialize_dirs(model_dirs, scaffold_model_dir)

        # folder for any other files the user would like to bundle
        data_model_dir.mkdir()
        data_files, data_dirs = _files_and_dirs(self.data_files)
        _serialize_files(data_files, data_model_dir)
        _serialize_dirs(data_dirs, data_model_dir)

        # a copy of the server template
        copy_tree(
            pathlib.Path(SERVING_DIR, _server_directory_name(self.model_framework)),
            str(pathlib.Path(target_directory, SRC_FOLDER))
        )

        # common python files
        copy_tree(
            pathlib.Path(SERVING_DIR, COMMON_FOLDER),
            str(pathlib.Path(target_directory, SRC_FOLDER, COMMON_FOLDER)))

        # a copy of the server dockerfile
        copy_file(
            pathlib.Path(SERVING_DIR, 'docker', _server_cpu_dockerfile(self.model_framework)),
            str(pathlib.Path(target_directory, _server_cpu_dockerfile(self.model_framework)))
        )

        # a copy of the server dockerfile with gpu support if it exists
        if _has_gpu_dockerfile(self.model_framework):
            copy_file(
                pathlib.Path(SERVING_DIR, 'docker', _server_gpu_dockerfile(self.model_framework)),
                str(pathlib.Path(target_directory, _server_gpu_dockerfile(self.model_framework)))
            )

        # a copy of the documentation
        copy_tree(
            pathlib.Path(SERVING_DIR, DOCS_FOLDER),
            str(pathlib.Path(target_directory))
        )
        # child-class specific serialization method
        self._update_requirements_txt(target_directory)
        # child-class specific serialization method
        self.serialize_model_to_directory(scaffold_model_dir)

        logger.info(f'Created a Baseten Scaffold Directory at {target_directory}')
        return target_directory

    def _update_requirements_txt(self, scaffold_dir):
        """
        Updates a requirements.txt file at model_dir with requirements from
        the model deployment request.

        Args:
            model_dir: The directory of the requirements file to update
            name_to_requirement: A dictionary of module name to requirements.txt entries
        """

        this_req_txt = pathlib.PurePath(scaffold_dir, REQUIREMENTS_FILE)
        pathlib.Path(this_req_txt).touch()
        if self.model_framework_requirements:
            with open(this_req_txt, 'a') as f:
                f.write('\n'.join(self.model_framework_requirements.values()))

    def serialize_model_to_directory(self, model_directory):
        raise NotImplementedError()

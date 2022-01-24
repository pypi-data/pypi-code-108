import os
import pathlib
from typing import Any

import pkg_resources
from dataclasses import dataclass
from packaging import version
from pkg_resources.extern.packaging.requirements import InvalidRequirement

from baseten_scaffolding.constants import PYTORCH, SKLEARN, TENSORFLOW, HUGGINGFACE_TRANSFORMER
from baseten_scaffolding.errors import FrameworkNotSupportedError

# list from https://scikit-learn.org/stable/developers/advanced_installation.html
SKLEARN_REQ_MODULE_NAME = {
    'numpy',
    'scipy',
    'joblib',
    'scikit-learn',
    'threadpoolctl',
}

# list from https://www.tensorflow.org/install/pip
# if problematic, lets look to https://www.tensorflow.org/install/source
TENSORFLOW_REQ_MODULE_NAME = {
    'tensorflow',
}


# list from https://pytorch.org/get-started/locally/
PYTORCH_REQ_MODULE_NAME = {
    'torch',
    'torchvision',
    'torchaudio',
}

HUGGINGFACE_TRANSFORMER_MODULE_NAME = {
    'transformers'
}


def pip_freeze():
    """
    This spawns a subprocess to do a pip freeze programmatically. pip is generally not supported as an API or threadsafe

    Returns: The result of a `pip freeze`

    """
    import pip
    pip_version = pip.__version__
    if version.parse(pip_version) < version.parse('20.1'):
        stream = os.popen('pip freeze -qq')
    else:
        stream = os.popen('pip list --format=freeze')
    this_env_requirements = [line.strip() for line in stream.readlines()]
    return this_env_requirements


def _get_entries_for_packages(list_of_requirements, desired_requirements):
    name_to_req_str = {}
    for req_name in desired_requirements:
        for full_req_str in list_of_requirements:
            if req_name == full_req_str.split('==')[0]:
                name_to_req_str[req_name] = full_req_str
    return name_to_req_str


def infer_sklearn_packages():
    return _get_entries_for_packages(pip_freeze(), SKLEARN_REQ_MODULE_NAME)


def infer_tensorflow_packages():
    return _get_entries_for_packages(pip_freeze(), TENSORFLOW_REQ_MODULE_NAME)


def infer_keras_packages():
    return _get_entries_for_packages(pip_freeze(), TENSORFLOW_REQ_MODULE_NAME)


def infer_pytorch_packages():
    return _get_entries_for_packages(pip_freeze(), PYTORCH_REQ_MODULE_NAME)


def infer_huggingface_packages():
    return _get_entries_for_packages(pip_freeze(), HUGGINGFACE_TRANSFORMER_MODULE_NAME)


def infer_model_framework(model_class: str):
    model_framework, _, _ = model_class.__module__.partition('.')
    if model_framework == 'transformers':
        return HUGGINGFACE_TRANSFORMER
    if model_framework not in {SKLEARN, TENSORFLOW}:
        try:
            import torch
            if issubclass(model_class, torch.nn.Module):
                model_framework = PYTORCH
            else:
                raise FrameworkNotSupportedError(f'Models must be one of {HUGGINGFACE_TRANSFORMER}, {SKLEARN}, {TENSORFLOW}, or {PYTORCH}.')
        except ModuleNotFoundError:
            raise FrameworkNotSupportedError(f'Models must be one of {HUGGINGFACE_TRANSFORMER}, {SKLEARN}, {TENSORFLOW}, or {PYTORCH}.')

    return model_framework


@dataclass
class ModelBuildStageOne:
    # the Python Class of the model
    model_type: str
    # the framework that the model is built in
    model_framework: str


def _model_class(model: Any):
    return model.__class__


def infer_model_information(model: Any) -> ModelBuildStageOne:
    model_class = _model_class(model)
    model_framework = infer_model_framework(model_class)
    model_type = model_class.__name__
    return ModelBuildStageOne(
        model_type,
        model_framework,
    )


def parse_requirements_file(requirements_file: str) -> dict:
    name_to_req_str = {}
    with pathlib.Path(requirements_file).open() as reqs_file:
        for raw_req in reqs_file.readlines():
            try:
                req = pkg_resources.Requirement.parse(raw_req)
                if req.specifier:
                    name_to_req_str[req.name] = str(req)
                else:
                    name_to_req_str[str(req)] = str(req)
            except InvalidRequirement:
                # there might be pip requirements that do not conform
                raw_req = str(raw_req).strip()
                name_to_req_str[f'custom_{raw_req}'] = raw_req
            except ValueError:
                # can't parse empty lines
                pass

    return name_to_req_str

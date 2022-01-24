import ast
import copy
import glob
import json
import logging
import pathlib
import re
import tarfile
import tempfile
import zipfile
from functools import reduce
from shutil import copyfile
from typing import IO, Any, Callable, Dict, List, Optional, Tuple

from baseten_scaffolding.definitions.base import \
    AbstractModelScaffoldDefinition
from baseten_scaffolding.model_inference import (infer_pytorch_packages,
                                                 infer_sklearn_packages,
                                                 infer_tensorflow_packages)
from baseten_scaffolding.scaffold.build import scaffold, scaffold_custom
from colorama import Fore, Style

import baseten
from baseten.baseten_deployed_model import BasetenDeployedModel
from baseten.common import api
from baseten.common.core import (MODEL_FILENAME, FrameworkNotSupportedError,
                                 ModelClassImplementationError,
                                 ModelFilesMissingError, ModelInputShapeError,
                                 ModelNotSupportedError, Semver,
                                 raises_api_error)
from baseten.common.settings import (API_URL_BASE, CUSTOM, KERAS, PYTORCH,
                                     SKLEARN, TENSORFLOW)
from baseten.common.util import parse_requirements_file, zipdir

logger = logging.getLogger(__name__)


@raises_api_error
def deploy_model(serialized_model: IO[Any],
                 model_framework: str,
                 model_name: str = None,
                 model_type: str = None,
                 input_shape: List[int] = None,
                 feature_names: List[str] = None,
                 feature_summary: dict = None,
                 class_labels: List[str] = None,
                 version_bump: Semver = Semver.MINOR.value,
                 model_framework_req: List[str] = None,
                 model_files_dict: Dict = None) -> BasetenDeployedModel:
    """Create a model version based on the serialized_model. If baseten wasn't initialized with a model_id, then
    create a model first and then create the model version.

    Args:
        serialized_model (file): A file-like object that is the serialized representation of the model object.
        model_framework (str): The framework used to create the model.
        model_name (str, optional): The name of the model to be created, if necessary.
        model_type (str, optional): The type of the model to be created.
        input_shape (List[int], optional): The shape of the model's input; e.g: [10] for a model with 10 features;
            [28, 28] for a model with 2 input dimensions of size 28 each.
        feature_names (list, optional): The list of feature names.
        feature_summary (dict, optional): A dict of summary stats with feature names as keys.
        class_labels (List[str], optional): The list of target class labels, if applicable.
        version_bump (str, optional): The version bump for this deployment, one of 'MAJOR', 'MINOR', 'PATCH'.
        model_framework_req (List[str], optional): The model_framework specific requirements
    Returns:
        BasetenDeployedModel

    Raises:
        ApiError: If there was an error communicating with the server.
        ValueError: If no model was provided.
        FrameworkNotSupportedError: If provided model's framework is not supported.
    """
    if not serialized_model:
        raise ValueError('A model was not provided!')
    if not input_shape:
        input_shape = []
    if not feature_summary:
        feature_summary = {}
    if not class_labels:
        class_labels = []
    if not model_framework_req:
        model_framework_req = {}

    logger.info('👽 👋 Making contact with BaseTen 👋 👽')

    file_ext = _model_ext_from_framework(model_framework)
    model_key = api.upload_model(serialized_model, file_ext, MODEL_FILENAME)
    model_info = _exists_model(model_name, baseten.working_model_id, api.models)
    if not model_info:
        logger.debug('No model found with provided name/id.')
        logger.debug(f'Creating new model named {Fore.BLUE}{model_name}{Style.RESET_ALL}')
        model_and_version_json = api.create_model(model_name,
                                                  model_key,
                                                  model_framework,
                                                  model_type,
                                                  input_shape,
                                                  feature_names,
                                                  feature_summary,
                                                  class_labels,
                                                  model_framework_req,
                                                  version_bump,
                                                  model_files_dict)
        logger.debug(f'Created model:\n{json.dumps(model_and_version_json, indent=4)}')
        logger.info(f'Successfully created new model named {Fore.BLUE}{model_name}{Style.RESET_ALL}.')

        model_id = model_and_version_json['id']
        model_version_id = model_and_version_json['version_id']
        # Set the newly created model to be the working model for future commands
        baseten.working_model_id = model_id
    else:
        model_id, model_name = model_info
        logger.info(f"Model '{model_name}' found. Creating a new version.")
        model_version_json = api.create_model_version(model_id,
                                                      model_key,
                                                      model_framework,
                                                      model_type,
                                                      input_shape,
                                                      feature_names,
                                                      feature_summary,
                                                      class_labels,
                                                      model_framework_req,
                                                      version_bump,
                                                      model_files_dict)

        model_version_id = model_version_json['id']
        logger.info(
            f'Successfully created version {Fore.BLUE}{model_version_id}{Style.RESET_ALL} for {model_name}.')

    logger.debug(f'{Fore.BLUE}Deploying model version.')
    model_version_web_url = f'{API_URL_BASE}/models/{model_id}/versions/{model_version_id}'
    logger.info('🏁 Deploying model 🏁')
    visit_message = f'|  Visit {Fore.BLUE}{model_version_web_url}{Style.RESET_ALL} for deployment status  |'
    visit_message_len = len(visit_message) - len(Fore.BLUE) - len(Style.RESET_ALL)
    logger.info(''.join(['-' for _ in range(visit_message_len)]))
    logger.info(visit_message)
    logger.info(''.join(['-' for _ in range(visit_message_len)]))

    return BasetenDeployedModel(model_version_id=model_version_id, model_name=model_name)


def _exists_model(model_name: Optional[str],
                  model_id: Optional[str],
                  models_provider: Callable) -> Optional[Tuple[str, str]]:
    """Checks if an effective model exists for the purpose of deploy or one needs to be created.

    If model name is supplied and a model with that name exists then it's picked up. Otherwise
    working model id in the session is tried.

    Returns id of model if model exists, or None
    """
    models = models_provider()['models']
    model_id_by_name = {model['name']: model['id'] for model in models}
    model_name_by_id = {model['id']: model['name'] for model in models}

    if model_name:
        if model_name in model_id_by_name:
            return model_id_by_name[model_name], model_name
        else:
            return None

    # No model_name supplied, try to work with working model id
    if model_id:
        if model_id in model_name_by_id:
            return model_id, model_name_by_id[model_id]
        else:
            logger.warning('Working model id not found in deployed models')
            return None

    # No model name or working model
    return None


@raises_api_error
def deploy_custom_model(
    model_name: str,
    model_class: str,
    model_files: List[str],
    requirements_file: str = None,
    version_bump: Semver = Semver.MINOR.value,
    model_type: str = None,
) -> BasetenDeployedModel:
    """Deploy a custom model.

    Deploy a model class (`model_class`) which implements the functions `load` and `predict`. `load()` is
    called on the model to initialize it, so is the place to load from a serialized format, download necessary
    files, etc. The `predict` method is passed the raw json inputs to the model, and must return json
    serializable data. Any additional pre or post processing can be run before returning the response.

    Model files should be all contained within the current working directory, and will be packaged relative
    to the current working directory.

    See docs.baseten.co for further documentation and examples.

    Args:
        model_name (str): The name of the model to be created.
        model_class (str): The name of the model class which implements `load` and `predict` methods,
            defined in one of `model_files`.
        model_files (List[str]): A list of files to include with the model deployment, including serialized
            models, python files, data, embeddings, etc. Files will match based on pathname patterns, eg *.py
            will match all python files in the current working directory.

            Must include file defining the model class.
        requirements_file (str, optional): A requirements.txt file specifying requirements to be installed
            alongside the model.
        version_bump (Semver, optional): The version bump for this deployment, one of 'MAJOR', 'MINOR', 'PATCH'.
            Defaults to Semver.MINOR.value.

    Returns:
        BasetenDeployedModel
    """
    all_model_files = list(set([_file for f in model_files for _file in glob.glob(f)]))
    serialized_model, class_def_file = _serialize_custom_model(model_class, all_model_files)
    model_files_dict = {'class_def_file': class_def_file, 'model_class': model_class}
    if requirements_file:
        model_framework_req = parse_requirements_file(requirements_file)
    else:
        model_framework_req = {}
    if not model_type:
        model_type = CUSTOM

    deployed_model = deploy_model(serialized_model,
                                  CUSTOM,
                                  model_name,
                                  model_type,
                                  version_bump=version_bump,
                                  model_framework_req=model_framework_req,
                                  model_files_dict=model_files_dict)
    serialized_model.close()
    return deployed_model


def _legacy_model_framework(model_framework: str):
    # tf.Keras does not always resolve to tensorflow, in newer versions of TF (>2.3.4) it will show as keras
    # in the legacy world we still want this to be tensorflow
    if model_framework == KERAS:
        return TENSORFLOW
    return model_framework


@raises_api_error
def deploy_model_object(
    model: Any,
    model_name: str = None,
    model_files: List[str] = None,
    feature_names: List[str] = None,
    class_labels: List[str] = None,
    version_bump: Semver = Semver.MINOR.value,
) -> BasetenDeployedModel:
    """Create a model version based on the model. If baseten wasn't initialized with a model_id, then
    create a model first and then create the model version.

    Args:
        model (an in-memory model object): A model object to be deployed (e.g. a RandomForestClassifier object)
        model_name (str, optional): The name of the model to be created, if necessary.
        model_files (List[str], optional): Additional files required for model definition, e.g class
            definitions for pytorch models.
        feature_names (List[str], optional): The list of feature names. If not provided,
            a list of feature names that match the model's input dimensions will be automatically generated.
            If the model's input has multiple dimensions, feature_names should be a flattened list of names.
        class_labels (List[str], optional): The list of target class labels, if applicable.
        version_bump (str, optional): The version bump for this deployment, one of 'MAJOR', 'MINOR', 'PATCH'.
    Returns:
        BasetenDeployedModel

    Raises:
        FrameworkNotSupportedError: If the model framework used is not supported.
        ModelInputShapeError: feature_names does not match the model's signature.
        ModelFilesMissingError: model is missing required supporting files for deployment.
        ApiError: If there was an error communicating with the server.
    """
    if hasattr(model, 'baseten'):
        model = copy.deepcopy(model)
        del model.baseten
    logger.info('🤖 Extracting model metadata 🤖')
    model_class = model.__class__
    model_framework, _, _ = model_class.__module__.partition('.')
    model_framework = _legacy_model_framework(model_framework)

    if model_framework not in {SKLEARN, TENSORFLOW}:
        try:
            import torch
            if issubclass(model_class, torch.nn.Module):
                model_framework = PYTORCH
            else:
                raise FrameworkNotSupportedError(f'Models must be one of {SKLEARN}, {TENSORFLOW}, or {PYTORCH}.')
        except ModuleNotFoundError:
            raise FrameworkNotSupportedError(f'Models must be one of {SKLEARN}, {TENSORFLOW}, or {PYTORCH}.')

    model_type = model_class.__name__
    input_shape = _model_input_shape(model, model_framework)
    logger.info(f'Preparing {Fore.BLUE}{model_framework} - {model_type}{Style.RESET_ALL} model.')

    if feature_names:
        input_features_count = reduce(lambda x, y: x * y, input_shape)
        if len(feature_names) != input_features_count:
            raise ModelInputShapeError(f'The model has {input_features_count} features but feature_names provided '
                                       f'{len(feature_names)}')

    if version_bump not in [item.value for item in Semver]:
        raise ValueError(f'{version_bump} is not a valid semantic version bump. '
                         f'Must be one of MAJOR, MINOR, and PATCH')
    logger.info(f'Serializing {Fore.BLUE}{model_name}{Style.RESET_ALL}.')
    if model_framework == SKLEARN:
        serialized_model = _serialize_sklearn_model(model)
        model_framework_req = infer_sklearn_packages()
        deployed_model = deploy_model(serialized_model,
                                      model_framework,
                                      model_name,
                                      model_type,
                                      input_shape,
                                      feature_names=feature_names,
                                      class_labels=class_labels,
                                      version_bump=version_bump,
                                      model_framework_req=model_framework_req)
        serialized_model.close()
    elif model_framework == TENSORFLOW:
        serialized_model = _serialize_tf_model(model)
        model_framework_req = infer_tensorflow_packages()
        deployed_model = deploy_model(serialized_model,
                                      model_framework,
                                      model_name,
                                      model_type,
                                      input_shape,
                                      feature_names=feature_names,
                                      class_labels=class_labels,
                                      version_bump=version_bump,
                                      model_framework_req=model_framework_req)
        serialized_model.close()
    elif model_framework == PYTORCH:
        serialized_model, model_files_dict = _serialize_pytorch_model(model, model_files)
        model_framework_req = infer_pytorch_packages()
        deployed_model = deploy_model(serialized_model,
                                      model_framework,
                                      model_name,
                                      model_type,
                                      input_shape,
                                      feature_names=feature_names,
                                      class_labels=class_labels,
                                      version_bump=version_bump,
                                      model_framework_req=model_framework_req,
                                      model_files_dict=model_files_dict)
        serialized_model.close()

    return deployed_model


def build_baseten_scaffold(
    model: Any,
    model_name: str = None,
    model_files: List[str] = None,
    data_files: List[str] = None,
    target_directory: str = None,
    requirements_file: str = None,
):
    """Create a scaffold directory with the given model. A scaffold directory is a build context designed to be built
    as a container locally or uploaded into a baseten serving environment.

    Args:
        model (an in-memory model object): A model object to be deployed (e.g. a keras, sklearn, or pytorch model
            object)
        model_name (str, optional): The name of the model to be created, if necessary.
        model_files (List[str], optional): Additional files required for model definition, e.g class
            definitions for pytorch models or other python code. Can be a glob that resolves to files for the root
            directory or a directory path. Files and directories here will be on the Python path
        data_files (List[str], optional): Additional files required for model operation. Can be a glob that resolves to
            files for the root directory or a directory path.
        target_directory (str, optional): The local directory target for the scaffold. Otherwise a temporary directory
            will be generated
        requirements_file (str, optional): A file of packages in a PIP requirements format to be installed in the
            container environment.
    Returns:
        AbstractModelScaffoldDefinition
    """
    if not model_name:
        import coolname
        model_name = coolname.generate_slug(2)
    local_name = model_name.replace(' ', '_')

    b10_scaffold = scaffold(
        model=model,
        model_files=model_files,
        data_files=data_files,
        target_directory=target_directory,
        requirements_file=requirements_file,
    )
    logger.info(f'To build this model server locally execute '
                f'`{b10_scaffold.docker_build_string} -t {local_name.lower()}`')
    logger.info(f'To run this model server locally execute `docker run --rm -p 8080:8080 {local_name.lower()}`')
    logger.info(f'To use the Python shell locally execute `docker run --rm -it {local_name.lower()} python3`')
    return b10_scaffold


def build_baseten_custom_scaffold(
    model_name: str,
    model_files: List[str] = None,
    data_files: List[str] = None,
    target_directory: str = None,
    requirements_file: str = None,
    model_class: str = None,
):
    """
    Create a scaffold directory for a custom model. A scaffold directory is a build context designed to be built as a
    container locally or uploaded into a baseten serving environment.

        Args:
            model_name (str, optional): The name of the model to be created, if necessary.
            model_files (List[str], optional): Additional files required for model definition, e.g class
                definitions for pytorch models or other python code. Can be a glob that resolves to files for the root
                directory or a directory path. Files and directories here will be on the Python path
            data_files (List[str], optional): Additional files required for model operation. Can be a glob that resolves
                to files for the root directory or a directory path.
            target_directory (str, optional): The local directory target for the scaffold. Otherwise a temporary
                directory will be generated
            requirements_file (str, optional): A file of packages in a PIP requirements format to be installed in the
                container environment.
            model_class (str, optional): The python class name for a model object that exists as a code within
                `model_files`
        Returns:
            AbstractModelScaffoldDefinition
    """
    if not model_name:
        import coolname
        model_name = coolname.generate_slug(2)
    local_name = model_name.replace(' ', '_')

    b10_scaffold = scaffold_custom(
        model_files=model_files,
        data_files=data_files,
        target_directory=target_directory,
        requirements_file=requirements_file,
        model_class=model_class
    )
    logger.info(f'To build this model server locally execute '
                f'`{b10_scaffold.docker_build_string} -t {local_name.lower()}`')
    logger.info(f'To run this model server locally execute `docker run --rm -p 8080:8080 {local_name.lower()}`')
    logger.info(f'To use the Python shell locally execute `docker run --rm -it {local_name.lower()} python3`')
    logger.info('Be sure to read the `README.md` for guidance on construction of a working custom scaffold')
    return b10_scaffold


@raises_api_error
def deploy_baseten_scaffold(
    b10_scaffold: AbstractModelScaffoldDefinition,
    model_name: str = None,
    version_bump: Semver = Semver.MINOR.value,
):
    """
    Given an existing baseten scaffold object, deploy it onto the baseten infastructure.

    Args:
        b10_scaffold: A scaffold object representing a local baseten_scaffold directory
        model_name (str, optional): The name of the model to be created, if necessary.
        version_bump (str, optional): The version bump for this deployment, one of 'MAJOR', 'MINOR', 'PATCH'.

    Returns:
        BasetenDeployedModel
    """
    logger.info(f'Serializing {Fore.BLUE}{model_name}{Style.RESET_ALL} scaffold.')
    temp_file = tempfile.NamedTemporaryFile(suffix='.tgz')
    with tarfile.open(temp_file.name, 'w:gz') as tar:
        tar.add(b10_scaffold.scaffold_dir, arcname='.')
    temp_file.file.seek(0)

    model_info = _exists_model(model_name, baseten.working_model_id, api.models)

    logger.info('Making contact with BaseTen 👋 👽')
    s3_key = api.upload_model(temp_file, 'tgz', MODEL_FILENAME)
    if not model_info:
        model_version_json = api.create_model_from_scaffold(
            model_name,
            s3_key,
            b10_scaffold.model_framework,
            b10_scaffold.model_type,
            b10_scaffold.model_framework_requirements,
            b10_scaffold.dockerfile,
            b10_scaffold.build_args,
            version_bump
        )
        logger.info(f'Created model:\n{json.dumps(model_version_json, indent=4)}')
        logger.info(f'Successfully registered model {Fore.BLUE}{model_name}{Style.RESET_ALL}.')

        model_id = model_version_json['id']
        model_version_id = model_version_json['version_id']
        # Set the newly created model model_version_json be the working model for future commands
        baseten.working_model_id = model_id
    else:
        model_id, model_name = model_info
        logger.info(f"Model '{model_name}' found. Creating a new version.")

        model_version_json = api.create_model_version_from_scaffold(model_id,
                                                                    s3_key,
                                                                    b10_scaffold.model_framework,
                                                                    b10_scaffold.model_type,
                                                                    b10_scaffold.model_framework_requirements,
                                                                    b10_scaffold.dockerfile,
                                                                    b10_scaffold.build_args,
                                                                    version_bump)

        model_version_id = model_version_json['id']
        logger.info(
            f'Successfully created version {Fore.BLUE}{model_version_id}{Style.RESET_ALL} for {model_name}.')

    logger.info(f'{Fore.BLUE}Deploying model version.')
    model_version_web_url = f'{API_URL_BASE}/models/{model_id}/versions/{model_version_id}'
    logger.info('🏁 The model is being built and deployed right now 🏁')
    visit_message = f'|  Visit {Fore.BLUE}{model_version_web_url}{Style.RESET_ALL} for deployment status  |'
    visit_message_len = len(visit_message) - len(Fore.BLUE) - len(Style.RESET_ALL)
    logger.info(''.join(['-' for _ in range(visit_message_len)]))
    logger.info(visit_message)
    logger.info(''.join(['-' for _ in range(visit_message_len)]))
    return BasetenDeployedModel(model_version_id=model_version_id, model_name=model_name)


def build_and_deploy_baseten_scaffold(
    model: Any,
    model_name: str = None,
    model_files: List[str] = None,
    data_files: List[str] = None,
    target_directory: str = None,
    requirements_file: str = None,
    version_bump: Semver = Semver.MINOR.value,
):
    """Create a scaffold directory with the given model and upload it to the basten serving environment. A scaffold
    directory is a build context designed to be built as a container locally or uploaded into a baseten serving
    environment.

    Args:
        model (an in-memory model object): A model object to be deployed (e.g. a keras, sklearn, or pytorch model
            object)
        model_name (str, optional): The name of the model to be created, if necessary.
        model_files (List[str], optional): Additional files required for model definition, e.g class
            definitions for pytorch models or other python code. Can be a glob that resolves to files for the root
            directory or a directory path. Files and directories here will be on the Python path
        data_files (List[str], optional): Additional files required for model operation. Can be a glob that resolves to
            files for the root directory or a directory path.
        target_directory (str, optional): The local directory target for the scaffold. Otherwise a temporary directory
            will be generated
        requirements_file (str, optional): A file of packages in a PIP requirements format to be installed in the
            container environment.
        version_bump (str, optional): The version bump for this deployment, one of 'MAJOR', 'MINOR', 'PATCH'.
    Returns:
        BasetenDeployedModel
    """

    b10_scaffold = build_baseten_scaffold(
        model, model_name, model_files, data_files, target_directory, requirements_file
    )
    return deploy_baseten_scaffold(
        b10_scaffold,
        model_name,
        version_bump
    )


def build_and_deploy_baseten_custom_scaffold(
    model_name: str = None,
    model_files: List[str] = None,
    data_files: List[str] = None,
    target_directory: str = None,
    requirements_file: str = None,
    model_class: str = None,
    version_bump: Semver = Semver.MINOR.value,
):
    """
    Create a scaffold directory for a custom model and upload it into the baseten serving environment.

        Args:
            model_name (str, optional): The name of the model to be created, if necessary.
            model_files (List[str], optional): Additional files required for model definition, e.g class
                definitions for pytorch models or other python code. Can be a glob that resolves to files for the root
                directory or a directory path. Files and directories here will be on the Python path
            data_files (List[str], optional): Additional files required for model operation. Can be a glob that resolves
                to files for the root directory or a directory path.
            target_directory (str, optional): The local directory target for the scaffold. Otherwise a temporary
                directory will be generated
            requirements_file (str, optional): A file of packages in a PIP requirements format to be installed in the
                container environment.
            model_class (str, optional): The python class name for a model object that exists as a code within
                `model_files`
            version_bump (str, optional): The version bump for this deployment, one of 'MAJOR', 'MINOR', 'PATCH'.
    Returns:
        BasetenDeployedModel
    """

    b10_scaffold = build_baseten_custom_scaffold(
        model_name, model_files, data_files, target_directory, requirements_file, model_class
    )
    return deploy_baseten_scaffold(
        b10_scaffold,
        model_name,
        version_bump
    )


def _serialize_sklearn_model(model: Any) -> tempfile.SpooledTemporaryFile:
    """Serializes a model based on the scikit-learn framework.

    Args:
        model (Any): The model object.

    Returns:
        tempfile.SpooledTemporaryFile: A temporary file wrapper.
    """
    import joblib
    model_joblib = tempfile.TemporaryFile()
    joblib.dump(model, model_joblib, compress=True)
    model_joblib.seek(0)
    return model_joblib


def _serialize_tf_model(model: Any) -> tempfile.NamedTemporaryFile:
    """Serializes a Tensorflow model as a zipped SavedModel.

    Args:
        model (Any): The model object.

    Returns:
        tempfile.NamedTemporaryFile: A temporary zipfile.ZipFile wrapper.
    """
    temp_model_dir = tempfile.TemporaryDirectory()
    temp_file = tempfile.NamedTemporaryFile(suffix='.zip')
    model.save(temp_model_dir.name)
    zip_file = zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED)
    zipdir(temp_model_dir.name, zip_file)
    zip_file.close()
    temp_model_dir.cleanup()
    temp_file.file.seek(0)
    return temp_file


def _serialize_pytorch_model(model: Any, model_files: List[str] = None) -> Tuple[tempfile.NamedTemporaryFile, Dict]:
    """Serializes a PyTorch model as a zipped .pt file.

    Args:
        model (Any): The model object.

    Returns:
        tempfile.NamedTemporaryFile: A temporary zipfile.ZipFile wrapper.
    """
    model_class = model.__class__
    class_name = model_class.__name__
    if not model_files:
        raise ModelFilesMissingError(f'The file defining the PyTorch model class `{class_name}` is missing.')
    temp_model_dir = tempfile.TemporaryDirectory()
    temp_file = tempfile.NamedTemporaryFile(suffix='.zip')
    import torch
    torch.save(model.state_dict(), f'{temp_model_dir.name}/model.pt')
    has_supplied_model_class_definion = False
    model_files_dict = {'files': {}, 'model_class': class_name}
    for filepath in model_files:
        with open(filepath, 'r') as _file:
            file_contents = _file.read()
            model_files_dict['files'][filepath] = file_contents
            parsed_contents = ast.parse(file_contents)
            is_model_class_definion_file = (
                True if [
                    stmt for stmt in parsed_contents.body
                    if type(stmt) == ast.ClassDef
                    and stmt.name == class_name
                ] else False)
            if is_model_class_definion_file:
                model_files_dict['class_def_file'] = filepath
            has_supplied_model_class_definion = has_supplied_model_class_definion or is_model_class_definion_file
    if not has_supplied_model_class_definion:
        raise ModelFilesMissingError(f'The file defining the PyTorch model class `{class_name}` is missing.')

    zip_file = zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED)
    zipdir(temp_model_dir.name, zip_file)
    zip_file.close()
    temp_model_dir.cleanup()
    temp_file.file.seek(0)
    return temp_file, model_files_dict


def _serialize_custom_model(class_name: str, model_files: List[str]) -> Tuple[tempfile.NamedTemporaryFile, str]:
    """Serializes a list of model files as a zip file.

    Args:
        class_name (str): The class_name for the model.
        model_files List[str]): A list of files to be packaged as the model deployment.

    Returns:
        tempfile.NamedTemporaryFile: A temporary zipfile.ZipFile wrapper.

    Raises:
        ModelFilesMissingError: If a file defining the model class is not supplied.
        ModelClassImplementationError: If the model class does not implement the required `load` and
            `predict` methods.

    Returns:
        (tempfile.NamedTemporaryFile, str): A tuple with a temporary zipfile.ZipFile wrapper and the filepath
            of the file defining the model class.
    """
    if not model_files:
        raise ModelFilesMissingError(f'The file defining the model class `{class_name}` is missing.')
    has_supplied_model_class_definion = False
    python_files = [f for f in model_files if f.endswith('.py')]
    class_def_file = None
    for filepath in python_files:
        with open(filepath, 'r') as _file:
            file_contents = _file.read()
            parsed_contents = ast.parse(file_contents)
            model_class_definion_file = [
                stmt for stmt in parsed_contents.body
                if type(stmt) == ast.ClassDef
                and stmt.name == class_name
            ]
            if model_class_definion_file:
                cls_function_names = [stmt.name for stmt in model_class_definion_file[0].body]
                if 'load' not in cls_function_names or 'predict' not in cls_function_names:
                    raise ModelClassImplementationError(f'The model class in {filepath} does not \
                        implement the required `load` and `predict` methods.')
                class_def_file = filepath
                has_supplied_model_class_definion = True
                break
    if not has_supplied_model_class_definion:
        raise ModelFilesMissingError(f'The file defining the model class `{class_name}` is missing.')
    temp_model_dir = tempfile.TemporaryDirectory()
    temp_file = tempfile.NamedTemporaryFile(suffix='.zip')
    for _f in model_files:
        file_name = pathlib.PurePath(_f).name
        path = pathlib.PurePath(temp_model_dir.name, file_name)
        copyfile(_f, path)
    zip_file = zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED)
    zipdir(temp_model_dir.name, zip_file)
    zip_file.close()
    temp_model_dir.cleanup()
    temp_file.file.seek(0)
    return temp_file, class_def_file


def _model_ext_from_framework(model_framework: str) -> str:
    if model_framework == SKLEARN:
        return 'joblib'
    elif model_framework == TENSORFLOW:
        return 'zip'
    elif model_framework == PYTORCH:
        return 'zip'
    elif model_framework == CUSTOM:
        return 'zip'
    else:
        raise FrameworkNotSupportedError(f'Models derived from {model_framework} are not currently supported.')


def _model_input_shape(model, framework: str) -> List[int]:
    """Returns the shape of the model's input as an array; e.g: [10] for a model with 10 features; [28, 28] for a
    model with 2 input dimensions of size 28 each.
    """
    if framework == SKLEARN:
        n_features = _hack_n_features_from_sklearn_model(model)
        if n_features is None:
            return []
        return [n_features]
    elif framework == TENSORFLOW:
        input_shape = model.input_shape
        if isinstance(input_shape, list):
            raise ModelNotSupportedError("Baseten currently supports only single input models.")
        return list(input_shape[1:])  # The first dimension is None (batch size)
    elif framework == PYTORCH:
        return []
    else:
        raise FrameworkNotSupportedError(f'Models derived from {framework} are not currently supported.')


def _hack_n_features_from_sklearn_model(model) -> int:
    """Determines the size of the input for the given model.

    Due to inconsistent representation of feature inputs in sklearn, various methods/props
    are required to extract the input dimension based on the model type. It's a hack.

    Args:
        model: A sklearn model object.

    Returns:
        int: The number of features used to train the model.
    """
    if 'sklearn.neighbors' in str(model.__class__):
        return model._tree.data.shape[-1]
    if 'sklearn.naive_bayes.GaussianNB' in str(model.__class__):
        return model.theta_.shape[-1]
    if model.__module__ == 'sklearn.naive_bayes':
        return model.feature_log_prob_.shape[-1]
    if model.__module__ == 'sklearn.discriminant_analysis':
        return model.means_.shape[-1]
    if 'sklearn.gaussian_process' in model.__module__:
        return model.base_estimator_.X_train_.shape[-1]
    try:
        model.predict([[1]])
        n_features = 1
    except ValueError as e:
        # For many models (not the ones above), the correct input feature length is raised in the exception
        numbers = re.findall(r' (\d+)', str(e))
        n_features = [int(x) for x in numbers if x != '1'][-1]
    except Exception as e:
        logger.debug(f'Unable to determine input_shape because of: {e}, but not stopping 🤞')
        # we can't determine the input shape, but we don't want to stop the user from uploading
        n_features = None
    return n_features

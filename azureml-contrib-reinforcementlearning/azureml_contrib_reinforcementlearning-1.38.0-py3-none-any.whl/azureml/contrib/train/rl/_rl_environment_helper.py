# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import path
from azureml.exceptions import TrainingException
import copy
from azureml.core.runconfig import EnvironmentDefinition
import azureml._vendor.ruamel.yaml as ruamelyaml


def _setup_environment(framework, use_gpu, conda_dependencies, base_env=None,
                       environment_variables=None):
    if not base_env:
        env = EnvironmentDefinition()
        is_custom_env = False
    else:
        env = copy.deepcopy(base_env)
        is_custom_env = True

    if is_custom_env:
        if conda_dependencies:
            env.python.conda_dependencies._merge_dependencies(conda_dependencies)
        else:
            env.python.user_managed_dependencies = True
    elif conda_dependencies:
        _load_env_defaults(env, use_gpu, framework)
        env.python.conda_dependencies._merge_dependencies(conda_dependencies)
    else:
        _load_framework_image(env, use_gpu, framework)

    if environment_variables:
        env.environment_variables = environment_variables

    return env


def _load_env_defaults(target_env, use_gpu, framework):
    _SCENARIO_FILE_NOT_FOUND_ERROR = 'Scenario file for {name}:{version} not found.'

    if use_gpu:
        image_type = "gpu"
    else:
        image_type = "cpu"
    scenario_filename = '{}-{}.yml'.format(repr(framework),
                                           image_type)
    scenario_path = path.join(path.dirname(__file__), "scenarios", scenario_filename)

    if not path.isfile(scenario_path):
        raise TrainingException((_SCENARIO_FILE_NOT_FOUND_ERROR).
                                format(name=framework._name, version=framework._version))
    conda_dependencies, base_image, base_dockerfile = \
        _load_scenario_file(scenario_path)

    target_env.docker.base_image = base_image
    target_env.docker.base_dockerfile = base_dockerfile
    target_env.python.conda_dependencies = conda_dependencies


def _load_scenario_file(path):
    from azureml.core.conda_dependencies import CondaDependencies
    with open(path, "r") as input:
        scenario = ruamelyaml.round_trip_load(input)
        base_image = scenario.get('baseImage', None)
        dockerfile = scenario.get('dockerFile', None)
        dependencies = scenario.get('inlineCondaDependencies', None)

        conda_dependencies = CondaDependencies(_underlying_structure=dependencies)

        # Base image and dockerfile are mutually exclusive.
        # Make sure scenario file isn't specifying both.
        if base_image is not None and dockerfile is not None:
            raise TrainingException("Incorrect scenario file specification for {}. Scenario file can specify either "
                                    "base image or docker image".format(path))

        base_image = base_image
        base_dockerfile = dockerfile
        return conda_dependencies, base_image, base_dockerfile


def _load_framework_image(target_env, use_gpu, framework):

    if use_gpu:
        image_type = "gpu"
    else:
        image_type = "cpu"
    base_image = "viennaprivate.azurecr.io/{0}:{1}-{2}".format(framework.name.lower(),
                                                               framework.version, image_type)
    target_env.docker.base_image = base_image
    target_env.python.user_managed_dependencies = True

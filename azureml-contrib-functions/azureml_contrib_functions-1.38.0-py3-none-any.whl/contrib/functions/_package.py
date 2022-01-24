# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating Azure Machine Learning service Webservice Packages for advanced use cases."""

import uuid

from azureml.core.model import Model, ModelPackage
from azureml._model_management._util import convert_parts_to_environment, submit_mms_operation
from azureml.exceptions import WebserviceException

SERVICE_BUS_QUEUE_TRIGGER = "service_bus_queue"
BLOB_TRIGGER = "blob"
HTTP_TRIGGER = "http"


def package(workspace, models, inference_config, generate_dockerfile=False, functions_enabled=False, trigger=None,
            **kwargs):
    """Create a model package in the form of a Docker image or Dockerfile build context.

    This function creates a model package for use in Azure Functions with the specified ``trigger`` type.
    The other functions in this package, create model packages for specific trigger types. For more information,
    see `Azure Functions triggers and
    bindings <https://docs.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings>`_.

    :param workspace: The workspace in which to create the package.
    :type workspace: azureml.core.Workspace
    :param models: A list of Model objects to include in the package. Can be an empty list.
    :type models: list[azureml.core.Model]
    :param inference_config: An InferenceConfig object to configure the operation of the models.
        This must include an Environment object.
    :type inference_config: azureml.core.model.InferenceConfig
    :param generate_dockerfile: Whether to create a Dockerfile that can be run locally
        instead of building an image.
    :type generate_dockerfile: bool
    :param functions_enabled: Whether Azure Functions should be enabled in the packaged container.
    :type functions_enabled: bool
    :param trigger: An optional trigger for the function. The values can be "blob", "http", or "service_bus_queue".
    :type trigger: str
    :param kwargs: Any of the arguments for a specific package function defined in this module. For example,
        for the ``package_http`` method, the argument passed is ``auth_level``.
    :return: A ModelPackage object.
    :rtype: azureml.core.model.ModelPackage
    :raises azureml.exceptions.WebserviceException: Invalid trigger specified.
    """
    if not functions_enabled:
        return __package_call(workspace, models, inference_config, generate_dockerfile, {})
    try:
        return __package_call(workspace, models, inference_config, generate_dockerfile,
                              payload_functions[trigger](**kwargs))
    except KeyError as ex:
        raise WebserviceException(
            "Invalid trigger {}, valid options are [{}]".format(str(ex), ','.join(payload_functions.keys())))
    except TypeError as ex:
        raise WebserviceException("Invalid option {} for trigger {}".format(str(ex), trigger))


def __package_call(workspace, models, inference_config, generate_dockerfile, options):
    model_ids = Model._resolve_to_model_ids(workspace, models, 'package.{}'.format(uuid.uuid4()))

    inference_config, _ = convert_parts_to_environment('package', inference_config)

    if not inference_config.environment:
        raise WebserviceException('Error, model packaging requires an InferenceConfig containing an Environment '
                                  'object.')

    options = {k: v for k, v in options.items() if v is not None}

    package_request = {
        'imageRequest': inference_config._build_environment_image_request(workspace, model_ids),
        'packageType': 'DockerBuildContext' if generate_dockerfile else 'DockerImage',
        'deployedApiOptions': options
    }

    operation_id = submit_mms_operation(workspace, 'POST', '/packages', package_request)

    return ModelPackage(workspace, operation_id, inference_config.environment)


def package_http(workspace, models, inference_config, generate_dockerfile=False, auth_level=None):
    """Create an Azure Functions model package as a Docker image or Dockerfile build context with an HTTP trigger.

    :param workspace: The workspace in which to create the package.
    :type workspace: azureml.core.Workspace
    :param models: A list of Model objects to include in the package. Can be an empty list.
    :type models: list[azureml.core.Model]
    :param inference_config: An InferenceConfig object to configure the operation of the models.
        This must include an Environment object.
    :type inference_config: azureml.core.model.InferenceConfig
    :param generate_dockerfile: Whether to create a Dockerfile that can be run locally
        instead of building an image.
    :type generate_dockerfile: bool
    :param auth_level: Auth level for the generated HTTP function.
    :type auth_level: str
    :return: A ModelPackage object.
    :rtype: azureml.core.model.ModelPackage
    """
    return package(workspace, models, inference_config, generate_dockerfile, functions_enabled=True,
                   trigger=HTTP_TRIGGER, auth_level=auth_level)


def _http(auth_level=None):
    return {"flavor": "functionsApp", "trigger": "Http", "authLevel": auth_level}


def package_blob(workspace, models, inference_config, generate_dockerfile=False, input_path=None, output_path=None):
    """Create an Azure Functions model package as a Docker image or Dockerfile build context with a blob trigger.

    :param workspace: The workspace in which to create the package.
    :type workspace: azureml.core.Workspace
    :param models: A list of Model objects to include in the package. Can be an empty list.
    :type models: list[azureml.core.Model]
    :param inference_config: An InferenceConfig object to configure the operation of the models.
        This must include an Environment object.
    :type inference_config: azureml.core.model.InferenceConfig
    :param generate_dockerfile: Whether to create a Dockerfile that can be run locally
        instead of building an image.
    :type generate_dockerfile: bool
    :param input_path: Input path for the blob trigger option.
    :type input_path: str
    :param output_path: Output path for the blob trigger option.
    :type output_path: str
    :return: A ModelPackage object.
    :rtype: azureml.core.model.ModelPackage
    """
    return package(workspace, models, inference_config, generate_dockerfile, functions_enabled=True,
                   trigger=BLOB_TRIGGER, input_path=input_path, output_path=output_path)


def _blob(input_path=None, output_path=None):
    return {"flavor": "functionsApp", "trigger": "Blob", "inPath": input_path, "outPath": output_path}


def package_service_bus_queue(workspace, models, inference_config, generate_dockerfile=False, input_queue_name=None,
                              output_queue_name=None):
    """Create an Azure Functions model package as a Docker image or Dockerfile with a service bus queue trigger.

    :param workspace: The workspace in which to create the package.
    :type workspace: azureml.core.Workspace
    :param models: A list of Model objects to include in the package. Can be an empty list.
    :type models: list[azureml.core.Model]
    :param inference_config: An InferenceConfig object to configure the operation of the models.
        This must include an Environment object.
    :type inference_config: azureml.core.model.InferenceConfig
    :param generate_dockerfile: Whether to create a Dockerfile that can be run locally
        instead of building an image.
    :type generate_dockerfile: bool
    :param input_queue_name: Input queue name for the queue trigger option.
    :type input_queue_name: str
    :param output_queue_name: Output queue name for the queue trigger option.
    :type output_queue_name: str
    :return: A ModelPackage object.
    :rtype: azureml.core.model.ModelPackage
    """
    return package(workspace, models, inference_config, generate_dockerfile, functions_enabled=True,
                   trigger=SERVICE_BUS_QUEUE_TRIGGER, input_queue_name=input_queue_name,
                   output_queue_name=output_queue_name)


def _service_bus_queue(input_queue_name=None, output_queue_name=None):
    return {"flavor": "functionsApp", "trigger": "ServiceBusQueue", "inQueueName": input_queue_name,
            "outQueueName": output_queue_name}


payload_functions = {BLOB_TRIGGER: _blob, SERVICE_BUS_QUEUE_TRIGGER: _service_bus_queue, HTTP_TRIGGER: _http}

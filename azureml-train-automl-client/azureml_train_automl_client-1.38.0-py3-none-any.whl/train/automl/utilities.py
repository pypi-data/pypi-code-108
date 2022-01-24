# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods used in automated ML in Azure Machine Learning."""
from typing import Any, Dict, List, Optional
import logging
import requests
from azureml.automl.core.shared import utilities as common_utilities, logging_utilities
from .constants import ComputeTargets

logger = logging.getLogger(__name__)


def get_primary_metrics(task):
    """
    Get the primary metrics supported for a given task.

    :param task: The string "classification" or "regression".
    :return: A list of the primary metrics supported for the task.
    """
    return common_utilities.get_primary_metrics(task)


def _get_package_version():
    """
    Get the package version string.

    :return: The version string.
    """
    from . import __version__
    return __version__


def _is_gpu() -> bool:
    is_gpu = False
    try:
        import torch
        is_gpu = torch.cuda.is_available()
    except ImportError:
        pass
    return is_gpu


def _is_azurevm() -> bool:
    """
    Use the Azure Instance Metadata Service to find out if this code is running on Azure VM.

    :return: bool
    """
    is_azure_vm = False
    headers = {'Metadata': 'true'}
    url = "http://169.254.169.254/metadata/instance?api-version=2017-04-02"
    timeout = 5

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == requests.codes.ok:
            is_azure_vm = True

    except requests.exceptions.ConnectionError:
        # Do nothing, by default return false
        pass

    except Exception:
        # log the error
        logger.info('failed in metadata instance call')
    return is_azure_vm


class _InternalComputeTypes:
    """Class to represent all Compute types."""

    _AZURE_NOTEBOOK_VM_IDENTIFICATION_FILE_PATH = "/mnt/azmnt/.nbvm"
    _AZURE_SERVICE_ENV_VAR_KEY = "AZURE_SERVICE"
    _AZURE_BATCHAI_CLUSTER_TYPE_ENV_VAR_KEY = "AZ_BATCHAI_VM_OFFER"

    AML_COMPUTE = "AmlCompute"
    ARCADIA = "Microsoft.ProjectArcadia"
    AIBUILDER = "Microsoft.AIBuilder"
    AZUREML_COMPUTE = "amlcompute"
    COMPUTE_INSTANCE = "computeinstance"
    DSI = "aml-workstation"
    COSMOS = "Microsoft.SparkOnCosmos"
    DATABRICKS = "Microsoft.AzureDataBricks"
    HDINSIGHTS = "Microsoft.HDI"
    LOCAL = "local"
    NOTEBOOK_VM = "Microsoft.AzureNotebookVM"
    REMOTE = "remote"

    _AZURE_SERVICE_TO_COMPUTE_TYPE = {
        ARCADIA: ARCADIA,
        COSMOS: COSMOS,
        DATABRICKS: DATABRICKS,
        HDINSIGHTS: HDINSIGHTS,
        AIBUILDER: AIBUILDER
    }

    """
    Defining only needed cluster types
    """
    _AZURE_BATCHAI_TO_CLUSTER_TYPE = {
        AZUREML_COMPUTE: AML_COMPUTE,
        DSI: COMPUTE_INSTANCE
    }

    @classmethod
    def get(cls) -> List[str]:
        return [
            _InternalComputeTypes.ARCADIA,
            _InternalComputeTypes.AIBUILDER,
            _InternalComputeTypes.AML_COMPUTE,
            _InternalComputeTypes.COMPUTE_INSTANCE,
            _InternalComputeTypes.COSMOS,
            _InternalComputeTypes.DATABRICKS,
            _InternalComputeTypes.HDINSIGHTS,
            _InternalComputeTypes.LOCAL,
            _InternalComputeTypes.NOTEBOOK_VM,
            _InternalComputeTypes.REMOTE,
        ]

    @classmethod
    def identify_compute_type(cls, compute_target: str,
                              azure_service: Optional[str] = None) -> Optional[str]:
        """
        Identify compute target and return appropriate key from _Compute_Type.

        For notebook VMs we need to check existence of a specific file.
        For Project Arcadia, HD Insights, Spark on Cosmos, Azure data bricks, AIBuilder, we need to use
        AZURE_SERVICE environment variable which is set to specific values.
        For AMLCompute and ContainerInstance, check AZ_BATCHAI_CLUSTER_TYPE environment variable.
        These values are stored in _InternalComputeTypes.
        """
        import os
        if (compute_target == ComputeTargets.LOCAL or compute_target is None):

            if os.path.isfile(_InternalComputeTypes._AZURE_NOTEBOOK_VM_IDENTIFICATION_FILE_PATH):
                return _InternalComputeTypes.NOTEBOOK_VM

            cluster_type = os.environ.get(_InternalComputeTypes._AZURE_BATCHAI_CLUSTER_TYPE_ENV_VAR_KEY)

            if ((cluster_type is not None) and (cluster_type.lower()
                                                in _InternalComputeTypes._AZURE_BATCHAI_TO_CLUSTER_TYPE)):
                return _InternalComputeTypes._AZURE_BATCHAI_TO_CLUSTER_TYPE.get(cluster_type.lower())
            azure_service = azure_service or os.environ.get(_InternalComputeTypes._AZURE_SERVICE_ENV_VAR_KEY)
            if azure_service is not None:
                return _InternalComputeTypes._AZURE_SERVICE_TO_COMPUTE_TYPE.get(azure_service, None)

            if _is_azurevm():
                return _InternalComputeTypes.REMOTE

            if (compute_target == ComputeTargets.LOCAL):
                return _InternalComputeTypes.LOCAL

        compute_type = None
        if compute_target == ComputeTargets.AMLCOMPUTE:
            compute_type = _InternalComputeTypes.AML_COMPUTE
        else:
            compute_type = _InternalComputeTypes.REMOTE

        return compute_type

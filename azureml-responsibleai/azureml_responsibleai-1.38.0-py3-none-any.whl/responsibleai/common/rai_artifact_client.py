# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Helper class to upload artifact files and download artifact files for RAI tools."""
from typing import Any, Dict, Optional
import io
import json

from azureml.core.run import Run
from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml._restclient.constants import RUN_ORIGIN
from azureml._logging import ChainedIdentity
import azureml._restclient.artifacts_client
from azureml.responsibleai.common._constants import IOConstants
from azureml.responsibleai.common._constants import LoggingConstants as LogCons
from azureml.responsibleai.common._loggerfactory import _LoggerFactory, track


_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


@experimental
class RAIArtifactClient(ChainedIdentity):
    """Helper class for uploading and downloading RAI Artifacts.

    :param run: A Run object to which the objects should be uploaded
    :type run: azureml.core.Run
    """

    @track(_get_logger, custom_dimensions={'app_name': 'RAIArtifactClient'}, activity_type=LogCons.PUBLIC_API)
    def __init__(
        self,
        run: Run,
        datastore_name: Optional[str] = None,
        **kwargs
    ):
        """Construct instance of the class.

        :param run: A Run object to which the objects should be uploaded
        :type run: azureml.core.Run
        :param datastore_name: Name of the datastore to use for uploading artifacts.
        :type datastore_name: str
        """
        super(RAIArtifactClient, self).__init__(**kwargs)
        self._logger.debug("Initializing RAIArtifactClient")
        self.run = run
        self.datastore_name = datastore_name

    @track(_get_logger, custom_dimensions={'app_name': 'RAIArtifactClient'}, activity_type=LogCons.PUBLIC_API)
    def generate_storage_path(
        self,
        artifact_area_path: str,
        upload_id: str,
        artifact_type: str
    ) -> str:
        """Create a path in storage for a particular artifact.

        The result will be something like:
        {artifact_area_path}/{upload_id}/{artifact_type}.json

        :param artifact_area_path: The top level name for rai artifact for example 'causal', 'counterfactual',
            'explanations', 'fairness' and so on.
        :type artifact_area_path: str
        :param upload_id: The upload id
        :type upload_id: str
        :param artifact_type: The type of the artifact being created
        :type artifact_type: str
        :returns: string for the Artifact prefix
        :rtype: str
        """
        return f'{artifact_area_path}/{upload_id}/{artifact_type}.json'

    @track(_get_logger, custom_dimensions={'app_name': 'RAIArtifactClient'}, activity_type=LogCons.PUBLIC_API)
    def upload_single_object(
        self,
        target: Any,
        artifact_area_path: str,
        upload_id: str,
        artifact_type: str
    ) -> Dict[str, str]:
        """Upload a single Python object as JSON.

        Returns a single dictionary, with a single entry of 'prefix'
        (recall that Artifacts are allowed to be entire directories,
        even though ours will be a single file)

        :param target: The object to be uploaded. This should be json serializable.
        :type target: Any
        :param artifact_area_path: The top level name for rai artifact for example 'causal', 'counterfactual',
            'explanations', 'fairness' and so on.
        :type artifact_area_path: str
        :param upload_id: The id of the current upload
        :type upload_id: str
        :param artifact_type: The type of the artifact being created
        :type artifact_type: str
        :returns: Single dictionary with a single entry of 'prefix' and storage path.
        :rtype: Dict[str,str]
        """
        storage_path = self.generate_storage_path(artifact_area_path, upload_id, artifact_type)
        self._logger.info("Uploading to {0}".format(storage_path))

        json_string = json.dumps(target)
        stream = io.BytesIO(json_string.encode(IOConstants.UTF8))

        self.run.upload_file(storage_path, stream, datastore_name=self.datastore_name)

        return {IOConstants.ARTIFACT_PREFIX: storage_path}

    @track(_get_logger, custom_dimensions={'app_name': 'RAIArtifactClient'}, activity_type=LogCons.PUBLIC_API)
    def download_single_object(
        self,
        artifact_area_path: str,
        upload_id: str,
        artifact_type: str
    ) -> Any:
        """Download a single Python object from the given prefix.

        This assumes that the 'prefix' is a file and not a directory.
        The file itself should be in JSON format.

        :param artifact_area_path: The top level name for rai artifact for example 'causal', 'counterfactual',
            'explanations', 'fairness' and so on.
        :type artifact_area_path: str
        :param upload_id: The upload id
        :type upload_id: str
        :param artifact_type: The type of the artifact being created
        :type artifact_type: str
        :returns: The object after conversion from JSON
        :rtype: Any
        """
        storage_path = self.generate_storage_path(artifact_area_path, upload_id, artifact_type)
        self._logger.info("Downloading from {0}".format(storage_path))
        core_client = azureml._restclient.artifacts_client.ArtifactsClient(
            self.run.experiment.workspace.service_context)

        artifact_string = core_client.download_artifact_contents_to_string(
            RUN_ORIGIN, self.run._container, storage_path)

        return json.loads(artifact_string)

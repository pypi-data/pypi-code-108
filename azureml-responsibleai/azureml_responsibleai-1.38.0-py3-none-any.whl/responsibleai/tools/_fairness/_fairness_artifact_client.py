# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import io
import json
import uuid

from azureml._logging import ChainedIdentity
import azureml._restclient.artifacts_client
from azureml._restclient.constants import RUN_ORIGIN
from azureml.responsibleai.common._constants import IOConstants

from ._constants import (
    FairnessAssetTypes,
    FairnessDashboardArtifactTypes
)


class FairnessArtifactClient(ChainedIdentity):
    """Helper class for uploading and downloading Fairness Artifacts.

    :param run: A Run object to which the objects should be uploaded
    :type run: azureml.core.Run
    """

    def __init__(self, run, **kwargs):
        """Construct instance of the class.

        :param run: A Run object to which the objects should be uploaded
        :type run: azureml.core.Run
        """
        super(FairnessArtifactClient, self).__init__(**kwargs)
        self._logger.debug("Initializing FairnessArtifactClient")
        self.run = run

    def generate_storage_path(self, upload_id, artifact_type):
        """Create a path in storage for a particular artifact.

        The result will be something like:
        azureml.fairness/dashboard.metrics/{upload_id}/{artifact_type}/{uuid}.json

        :param upload_id: The upload id
        :type upload_id: str
        :param artifact_type: The type of the artifact being created
        :type artifact_type: str
        :returns: string for the Artifact prefix
        :rtype: str
        """
        assert artifact_type in FairnessDashboardArtifactTypes.VALID_ARTIFACT_TYPES

        filename = str(uuid.uuid4())
        fmt = "{0}/{1}/{2}/{3}/{4}.json"
        result = fmt.format(FairnessAssetTypes.FAIRNESS_ASSET,
                            FairnessAssetTypes.DASHBOARD_METRICS,
                            upload_id,
                            artifact_type,
                            filename)
        return result

    def upload_single_object(self, datastore_name, target, upload_id, artifact_type):
        """Upload a single Python object as JSON.

        Returns a list of a single dictionary, with a single
        entry of 'prefix' (recall that Artifacts are allowed
        to be entire directories, even though ours will be
        a single file)

        :param datastore_name: The datastore for the upload
        :type datastore_name: str
        :param target: The object to be uploaded
        :type target: object
        :param upload_id: The id of the current fairness upload
        :type upload_id: str
        :param artifact_type: The type of the artifact being created
        :type artifact_type: str
        :returns: Single entry list of dictionary with a single entry, 'prefix'
        :rtype: list(dict[str,str])
        """
        storage_path = self.generate_storage_path(upload_id, artifact_type)
        self._logger.info("Uploading to {0}".format(storage_path))

        json_string = json.dumps(target)
        stream = io.BytesIO(json_string.encode(IOConstants.UTF8))

        self.run.upload_file(storage_path,
                             stream,
                             datastore_name=datastore_name)

        return [{IOConstants.ARTIFACT_PREFIX: storage_path}]

    def download_single_object(self, prefix):
        """Download a single Python object from the given prefix

        This assumes that the 'prefix' is a file and not a directory.
        The file itself should be in JSON format.

        :param prefix: The storage prefix of the object to download
        :type prefix: str
        :returns: The object after conversion from JSON
        :rtype: object
        """
        self._logger.info("Downloading from {0}".format(prefix))
        core_client = azureml._restclient.artifacts_client.ArtifactsClient(
            self.run.experiment.workspace.service_context)

        artifact_string = core_client.download_artifact_contents_to_string(
            RUN_ORIGIN,
            self.run._container,
            prefix)

        return json.loads(artifact_string)

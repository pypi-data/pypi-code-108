# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Access run artifacts extension client."""

from azureml._restclient.artifacts_client import ArtifactsClient
from .artifact_repository_client import ArtifactRepositoryClient


class LocalArtifactRepositoryClient(ArtifactRepositoryClient):
    """Local Artifact Repository client class."""

    def __init__(self, service_context, origin, container, path):
        super(LocalArtifactRepositoryClient, self).__init__(path)
        self._artifacts_client = ArtifactsClient(service_context)
        self._origin = origin
        self._container = container

    def download_artifact(self, path, output_file_path):
        """
        Download a single artifact from artifact service.

        :param path: the filepath within the container of the artifact to be downloaded
        :type path: str
        :param output_file_path: filepath in which to store the downloaded artifact locally
        :rtype: None
        """
        return self._artifacts_client.download_artifact(
            self._origin,
            self._container,
            path,
            output_file_path)

    def upload_artifact(self, artifact, dest_path):
        """Upload local file or stream to a new artifact."""
        return self._artifacts_client.upload_artifact(
            artifact,
            self._origin,
            self._container,
            dest_path)

    def upload_files(self, paths, names=None):
        """
        Upload files to artifact service.

        :rtype: list[BatchArtifactContentInformationDto]
        """
        return self._artifacts_client.upload_files(
            paths, self._origin, self._container, names=names)

    def upload_dir(
            self, dir_path, path_to_name_fn=None, skip_first_level=False):
        """
        Upload all files in path.

        :rtype: list[BatchArtifactContentInformationDto]
        """
        return self._artifacts_client.upload_dir(
            dir_path,
            self._origin,
            self._container,
            path_to_nae_fn=path_to_name_fn,
            skip_first_level=skip_first_level)

    def get_file_paths(self):
        return self._artifacts_client.get_file_paths(
            self._origin, self._container)

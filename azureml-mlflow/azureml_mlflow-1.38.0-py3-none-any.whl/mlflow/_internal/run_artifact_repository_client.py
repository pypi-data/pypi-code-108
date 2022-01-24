# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Access run artifacts extension client."""

import os

from io import IOBase

from azureml._async import TaskQueue
from azureml._file_utils import upload_blob_from_stream
from azureml.exceptions import UserErrorException, AzureMLException

from azureml._restclient.models.artifact_path_dto import ArtifactPathDto
from azureml._restclient.models.batch_artifact_create_command import BatchArtifactCreateCommand

from azureml._restclient.run_artifacts_client import RunArtifactsClient, SUPPORTED_NUM_EMPTY_ARTIFACTS
from .artifact_repository_client import ArtifactRepositoryClient


class RunArtifactRepositoryClient(ArtifactRepositoryClient):
    """Run Artifact Repository client class."""

    def __init__(self, service_context, experiment_name, run_id, path):
        super(RunArtifactRepositoryClient, self).__init__(path)
        self._run_artifacts_client = RunArtifactsClient(service_context, experiment_name)
        self._run_id = run_id

    def download_artifact(self, path, output_file_path):
        """
        Download a single artifact from artifact service.

        :param path: the filepath within the container of the artifact to be downloaded
        :type path: str
        :param output_file_path: filepath in which to store the downloaded artifact locally
        :rtype: None
        """
        filename = os.path.basename(path)  # save outputs/filename.txt as filename.txt
        if os.path.isdir(output_file_path):
            self._logger.debug("output_file_path for download_artifact is a directory.")
            output_file_path = os.path.join(output_file_path, filename)
        else:
            self._logger.debug("output_file_path for download_artifact is not a directory.")
        self._run_artifacts_client.download_artifact(self._run_id, path, output_file_path)

    def _create_empty_artifacts(self, paths):
        """Create empty artifacts."""
        if self._run_id is None:
            raise UserErrorException("run_id cannot be null when creating empty artifacts")

        if isinstance(paths, str):
            paths = [paths]
        artifacts = [ArtifactPathDto(path) for path in paths]
        batch_create_command = BatchArtifactCreateCommand(artifacts)
        res = self._run_artifacts_client._execute_with_experiment_arguments(
            self._run_artifacts_client._client.run_artifact.batch_create_empty_artifacts,
            self._run_id,
            batch_create_command)

        if res.errors:
            error_messages = []
            for artifact_name in res.errors:
                error = res.errors[artifact_name].error
                error_messages.append("{}: {}".format(error.code,
                                                      error.message))
            raise AzureMLException("\n".join(error_messages))

        return res

    def _upload_stream_to_existing_artifact(
            self, stream, artifact, content_information, content_type=None):
        """Upload a stream to existring artifact."""
        artifact = artifact
        artifact_uri = content_information.content_uri
        res = upload_blob_from_stream(
            stream,
            artifact_uri,
            content_type=content_type,
            session=self._run_artifacts_client.session)
        return res

    def _upload_artifact_from_stream(
            self, stream, name, content_type=None):
        """Upload a stream to a new artifact."""
        if self._run_id is None:
            raise UserErrorException("Cannot upload artifact when run_id is None")
        # Construct body
        res = self._create_empty_artifacts(name)
        artifact = res.artifacts[name]
        content_information = res.artifact_content_information[name]
        self._upload_stream_to_existing_artifact(
            stream, artifact, content_information,
            content_type=content_type)
        return res

    def _upload_artifact_from_path(self, path, *args, **kwargs):
        """Upload a local file to a new artifact."""
        path = os.path.normpath(path)
        path = os.path.abspath(path)
        with open(path, "rb") as stream:
            return self._upload_artifact_from_stream(stream, *args, **kwargs)

    def upload_artifact(self, artifact, *args, **kwargs):
        """Upload local file or stream to a new artifact."""
        self._logger.debug("Called upload_artifact")
        if isinstance(artifact, str):
            self._logger.debug("Uploading path artifact")
            return self._upload_artifact_from_path(artifact, *args, **kwargs)
        elif isinstance(artifact, IOBase):
            self._logger.debug("Uploading io artifact")
            return self._upload_artifact_from_stream(artifact, *args, **kwargs)
        else:
            raise UserErrorException("UnsupportedType: type {} is invalid, "
                                     "supported input types: file path or file".format(type(artifact)))

    def upload_files(self, paths, names=None):
        """
        Upload files to artifact service.

        :rtype: list[BatchArtifactContentInformationDto]
        """
        if self._run_id is None:
            raise UserErrorException("run_id cannot be null when uploading artifact")

        names = names if names is not None else paths
        path_to_name = {}
        paths_and_names = []
        # Check for duplicates, this removes possible interdependencies
        # during parallel uploads
        for path, name in zip(names, paths):
            if path not in path_to_name:
                paths_and_names.append((path, name))
                path_to_name[path] = name
            else:
                self._logger.warning("Found repeat file {} with name {} in upload_files.\n"
                                     "Uploading file {} to the original name "
                                     "{}.".format(path, name, path, path_to_name[path]))

        batch_size = SUPPORTED_NUM_EMPTY_ARTIFACTS

        results = []
        for i in range(0, len(names), batch_size):
            with TaskQueue(
                    worker_pool=self._run_artifacts_client._pool,
                    _ident="upload_files") as task_queue:
                batch_names = names[i:i + batch_size]
                batch_paths = paths[i:i + batch_size]

                content_information = self._create_empty_artifacts(batch_names)

                def perform_upload(path, artifact, artifact_content_info):
                    with open(path, "rb") as stream:
                        return self._upload_stream_to_existing_artifact(stream, artifact, artifact_content_info)

                for path, name in zip(batch_paths, batch_names):
                    artifact = content_information.artifacts[name]
                    artifact_content_info = content_information.artifact_content_information[name]
                    task = task_queue.add(perform_upload, path, artifact, artifact_content_info)
                    results.append(task)

        return map(lambda task: task.wait(), results)

    def upload_dir(
            self, dir_path, path_to_name_fn=None, skip_first_level=False):
        """
        Upload all files in path.

        :rtype: list[BatchArtifactContentInformationDto]
        """
        if self._run_id is None:
            raise UserErrorException("Cannot upload when run_id is None")
        paths_to_upload = []
        names = []
        for pathl, _subdirs, files in os.walk(dir_path):
            for _file in files:
                fpath = os.path.join(pathl, _file)
                paths_to_upload.append(fpath)
                if path_to_name_fn is not None:
                    name = path_to_name_fn(fpath)
                elif skip_first_level:
                    subDir = pathl.split("/", 1)[1]
                    name = os.path.join(subDir, _file)
                else:
                    name = fpath
                names.append(name)
        self._logger.debug("Uploading {}".format(names))
        result = self.upload_files(paths_to_upload, names)
        return result

    def get_file_paths(self):
        return self._run_artifacts_client.get_file_paths(self._run_id)

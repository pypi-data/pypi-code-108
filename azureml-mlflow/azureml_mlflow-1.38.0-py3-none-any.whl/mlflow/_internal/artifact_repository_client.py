# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._logging import ChainedIdentity


class ArtifactRepositoryClient(ChainedIdentity):
    def __init__(self, path, **kwargs):
        super(ArtifactRepositoryClient, self).__init__(**kwargs)
        self.path = path

    def upload_artifact(self, local_file, dest_path):
        raise NotImplementedError()

    def upload_dir(self, local_dir, dest_path, skip_first_level=True):
        raise NotImplementedError()

    def upload_files(self, files, file_names):
        raise NotImplementedError()

    def get_file_paths(self):
        raise NotImplementedError()

    def download_artifact(self, remote_file_path, local_path):
        raise NotImplementedError()

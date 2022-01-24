# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of Wikipedia Data."""

from .base_blob_info import BaseBlobInfo


class WikipediaBlobInfo(BaseBlobInfo):
    """Blob info of Wikipedia Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'wikipedia'
        self.blob_account_name = 'wikipediadatastore'
        self.blob_container_name = "preprocessed"
        self.blob_relative_path = "latest/bert_data/"
        self.blob_sas_token = (
            "?st=2019-09-17T10%3A07%3A38Z&se=2232-01-01T10%3A07%3A00Z&sp=rl&sv=2018-03-28&sr=c"
            # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Offline sas token")]
            r"&sig=TJvGl5JcIbCjpGasLNSTAnmpeNScTt8k3CFkfGA5zJo%3D")

    def get_url(self) -> str:
        """Get the web url of Dataset."""
        self._update_blob_info()
        return 'https://%s.blob.core.windows.net/%s/latest/bert_data/**/*' % (
            self.blob_account_name,
            self.blob_container_name)

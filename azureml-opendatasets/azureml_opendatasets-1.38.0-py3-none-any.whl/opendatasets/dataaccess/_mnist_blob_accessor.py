# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List

from ._blob_accessor import BlobAccessor


class MNISTFileBlobAccessor(BlobAccessor):
    """File accessor for MNIST."""

    def __init__(self, registry_info, mandatory_columns=None):
        super().__init__(registry_info, mandatory_columns=mandatory_columns)
        self._partition_pattern = None

    def get_urls(self, **kwrags) -> List[str]:
        """
        Get the blob url based on args and partition pattern to reduce look up cost
        :return: List of blob urls
        :rtype: List[str]
        """
        if "dataset_filter" in kwrags:
            dataset_filter = kwrags["dataset_filter"]
            file_prefix = ""
            if dataset_filter == 'train':
                file_prefix = "train-"
            elif dataset_filter == 'test':
                file_prefix = "t10k-"
            glob_pattern = file_prefix + "*.gz"
            return 'https://%s.blob.core.windows.net/%s/%s' % (
                self._blob_account_name,
                self._blob_container_name,
                glob_pattern)
        raise Exception("Please specify dataset_filter.")

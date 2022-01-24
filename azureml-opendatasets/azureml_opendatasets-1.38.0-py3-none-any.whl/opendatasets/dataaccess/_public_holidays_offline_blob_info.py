# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of Public holiday Data."""

from .base_blob_info import BaseBlobInfo


class PublicHolidaysOfflineBlobInfo(BaseBlobInfo):
    """Blob info of Public Holiday Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'public_holiday_offline'
        self.blob_account_name = None
        self.blob_container_name = None
        self.blob_relative_path = None
        self.blob_sas_token = None

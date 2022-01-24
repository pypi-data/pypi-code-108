# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to control how the limit pandas data loads when parquet files are large.

With this module's functionality, you can specify how to limit how pandas data loads when parquet files
are too large to load.
"""

from datetime import datetime

from azureml._vendor.azure_storage.blob import BlockBlobService

from .._utils.time_utils import day_range, month_range


class PandasDataLoadLimitNone:
    """Defines no pandas data load limit."""

    def __init__(self):
        """Initialize _match_paths."""
        self._match_paths = None

    def _contains_match_paths(self, path):
        if self._match_paths is None:
            return True

        for match_path in self._match_paths:
            if path.find(match_path) >= 0:
                return True
        return False

    def get_target_blob_paths(
            self,
            blob_service: BlockBlobService,
            blob_container_name: str,
            blob_relative_path: str):
        """
        Get target blob paths based on its own filters.

        :param blob_service: block blob service.
        :type blob_service: azure.storage.blob.blockblobservice.BlockBlobService
        :param blob_container_name: blob container name
        :type blob_container_name: str
        :param blob_relative_path: blob relative path
        :type blob_relative_path: str

        :return: a list of target blob paths within filter range.
        :rtype: list
        """
        print('Looking for parquet files...')
        if blob_relative_path is not None and not blob_relative_path.endswith('/'):
            blob_relative_path = blob_relative_path + '/'
        blobs = blob_service.list_blobs(
            blob_container_name, blob_relative_path)
        target_paths = []
        for blob in blobs:
            if blob.name.endswith('.parquet') and self._contains_match_paths(blob.name):
                target_paths.append(blob.name)
        return target_paths


class PandasDataLoadLimitToDay(PandasDataLoadLimitNone):
    """Defines a pandas data load limit to the last day.

    You can use PandasDataLoadLimitToDay to control how many parquets of days will be loaded.
    """

    def __init__(
            self,
            start_date,
            end_date,
            path_pattern='/year=%d/month=%d/day=%d/',
            limit=-1):
        """Initialize pandas data load limit to the last day.

        :param start_date: The start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: The end date you'd like to query inclusively.
        :type end_date: datetime
        :param path_pattern: A blob path pattern.
        :type path_pattern: str
        :param limit: The limit of the max number of paths that can be returned.
        :type limit: int
        """
        self.start_date = start_date
        self.end_date = end_date if end_date is not None else datetime.today()
        self.path_pattern = path_pattern
        self.limit = limit
        super(PandasDataLoadLimitToDay, self).__init__()

    def get_target_blob_paths(
            self,
            blob_service: BlockBlobService,
            blob_container_name: str,
            blob_relative_path: str):
        """
        Get target blob paths based on its own filters.

        :param blob_service: The block blob service.
        :type blob_service: azure.storage.blob.blockblobservice.BlockBlobService
        :param blob_container_name: The blob container name.
        :type blob_container_name: str
        :param blob_relative_path: The blob relative path.
        :type blob_relative_path: str

        :return: A list of target blob paths within filter range.
        :rtype: builtin.list
        """
        self._match_paths = []
        for current_day in day_range(self.start_date, self.end_date):
            self._match_paths.append(self.path_pattern % (
                current_day.year, current_day.month, current_day.day))

        if self.limit == 0:
            print('limit is 0! Returning no blob paths.')
            return []

        if self.limit > 0 and len(self._match_paths) > self.limit:
            print(
                'Due to size, we only allow getting %s-day data into pandas dataframe!' % (self.limit))
            starting_index = -self.limit
            self._match_paths = self._match_paths[starting_index:]

        print('Target paths: %s' % (self._match_paths))
        return super(PandasDataLoadLimitToDay, self).get_target_blob_paths(
            blob_service=blob_service,
            blob_container_name=blob_container_name,
            blob_relative_path=blob_relative_path)


class PandasDataLoadLimitToMonth(PandasDataLoadLimitNone):
    """Defines a pandas data load limit to the last month.

    You can use PandasDataLoadLimitToMonth to control how many parquets of months will be loaded.
    """

    def __init__(
            self,
            start_date,
            end_date,
            path_pattern='/year=%d/month=%d/',
            limit=-1):
        """Initialize pandas data load limit to the last month.

        :param start_date: The start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: The end date you'd like to query inclusively.
        :type end_date: datetime
        :param path_pattern: A blob path pattern.
        :type path_pattern: str
        :param limit: The limit of the max number of paths that can be returned.
        :type limit: int
        """
        self.start_date = start_date
        self.end_date = end_date if end_date is not None else datetime.today()
        self.path_pattern = path_pattern
        self.limit = limit
        super(PandasDataLoadLimitToMonth, self).__init__()

    def get_target_blob_paths(
            self,
            blob_service: BlockBlobService,
            blob_container_name: str,
            blob_relative_path: str):
        """
        Get target blob paths based on its own filters.

        :param blob_service: The block blob service.
        :type blob_service: azure.storage.blob.blockblobservice.BlockBlobService
        :param blob_container_name: The blob container name.
        :type blob_container_name: str
        :param blob_relative_path: The blob relative path.
        :type blob_relative_path: str

        :return: A list of target blob paths within filter range.
        :rtype: list
        """
        self._match_paths = []
        for current_month in month_range(self.start_date, self.end_date):
            self._match_paths.append(self.path_pattern % (
                current_month.year, current_month.month))

        if self.limit == 0:
            print('limit is 0! Returning no blob paths.')
            return []

        if self.limit > 0 and len(self._match_paths) > self.limit:
            print(
                'Due to size, we only allow getting %s-day data into pandas dataframe!' % (self.limit))
            starting_index = -self.limit
            self._match_paths = self._match_paths[starting_index:]

        print('Target paths: %s' % (self._match_paths))
        return super(PandasDataLoadLimitToMonth, self).get_target_blob_paths(
            blob_service=blob_service,
            blob_container_name=blob_container_name,
            blob_relative_path=blob_relative_path)

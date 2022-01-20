from ..__base_structures import BaseManagement

import datetime
from pytz import timezone
import re


class FeatureStore(BaseManagement):
    def __init__(self, mlops_bs):
        self.__core = mlops_bs.core['FS']

    def __iter__(self):
        return self

    def __next__(self):
        name = ''
        return name

    def _local_filesystem_user_interfaces(self):
        pass

    def _remote_filesystem_user_interfaces(self):
        pass

    def _local_search(self):
        pass

    def _remote_search(self):
        pass

    def loading_connection(self, specification, usage='train'):
        __FS_Loader__ = None
        specification['__loading_path_in_FS__'] = self.__core.path
        specification['__loading_name_in_FS__'] = __FS_Loader__
        specification['__loading_process_regulation__'].append(
            ('FS', 0),
        )
        return specification

    def storing_connection(self, specification, usage='train'):
        specification['__saving_path_in_FS__'] = self.__core.path
        specification['__saving_name_in_FS__'] = next(self)
        return specification


class FeatureStoreManager(BaseManagement):
    def __init__(self, mlops_bs):
        self.__core = mlops_bs.core['FS']

    def __iter__(self):
        return self

    def __next__(self):
        name = ''
        return name

    def _local_filesystem_user_interfaces(self):
        pass

    def _remote_filesystem_user_interfaces(self):
        pass

    def _local_search(self):
        pass

    def _remote_search(self):
        pass

    def loading_connection(self, specification, usage='train'):
        __FS_Loader__ = None
        specification['__loading_path_in_FS__'] = self.__core.path
        specification['__loading_name_in_FS__'] = __FS_Loader__
        specification['__loading_process_regulation__'].append(
            ('FS', 0),
        )
        return specification

    def storing_connection(self, specification, usage='train'):
        specification['__saving_path_in_FS__'] = self.__core.path
        specification['__saving_name_in_FS__'] = next(self)
        return specification



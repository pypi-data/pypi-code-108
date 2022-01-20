from ailever.investment import __fmlops_bs__ as fmlops_bs
from ..__base_structures import BaseManagement

import datetime
from pytz import timezone
import re



class BacktestingRepository(BaseManagement):
    def __init__(self):
        self.__core = fmlops_bs.core['BR'] 

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

    # Define Loading Proces Interchange Regulation
    def loading_connection(self, specification, usage='train'):
        specification['loading_path'] = self.__core.path
        specification['loading_name'] = None
        specification['loading_process_regulation'] = [('BR', 1)]
        return specification

    # Define Storing Process Interchange Regulation
    def storing_connection(self, specification, usage='train'):
        specification['saving_path'] = self.__core.path
        specification['saving_name'] = None
        specification['storing_process_regulation'] = [('BR', 1)]
        return specification




class BacktestingRepositoryManager(BaseManagement):
    def __init__(self):
        self.__core = fmlops_bs.core['BR'] 

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

    # Define Loading Proces Interchange Regulation
    def loading_connection(self, specification, usage='train'):
        specification['loading_path'] = self.__core.path
        specification['loading_name'] = None
        specification['loading_process_regulation'] = [('BR', 1)]
        return specification

    # Define Storing Process Interchange Regulation
    def storing_connection(self, specification, usage='train'):
        specification['saving_path'] = self.__core.path
        specification['saving_name'] = None
        specification['storing_process_regulation'] = [('BR', 1)]
        return specification


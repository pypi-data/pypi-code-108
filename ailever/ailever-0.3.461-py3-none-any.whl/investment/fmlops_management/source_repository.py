from ailever.investment import __fmlops_bs__ as fmlops_bs
from ..__base_structures import BaseManagement

import datetime
from pytz import timezone
import re


class SourceRepository(BaseManagement):
    def __init__(self):
        self.__core = fmlops_bs.core['SR']

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
        specification['loading_path'] = self.__core.path
        specification['loading_name'] = None
        return specification

    def storing_connection(self, specification, usage='train'):
        specification['saving_path'] = self.__core.path
        specification['saving_name'] = None
        return specification



class SourceRepositoryManager(BaseManagement):
    def __init__(self):
        self.__core = fmlops_bs.core['SR']
        self.architecture = 'lstm'
        self.ticker = 'are'
        self.training_data_period_start = '20200101'
        self.training_data_period_end = '20210801'
        self.packet_size = 365
        self.prediction_range = 100
        self.version = 0
        self.rep = 'ailever'
        self.message = 'TargetingMarketCaptial'

    def __iter__(self):
        return self

    def __next__(self):
        self.version += 1

        architecture = self.architecture
        ticker = self.ticker
        training_data_period_start = self.training_data_period_start
        training_data_period_end = self.training_data_period_end
        packet_size = self.packet_size
        prediction_range = self.prediction_range
        version = self.version
        rep = self.rep
        message = self.message

        name = f'{architecture}_{ticker}_{training_data_period_start}_{training_data_period_end}_{packet_size}_{prediction_range}_v{version}_{rep}_{message}'
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
        __SR_Loader__ = None
        specification['__loading_path_from_SR__'] = self.__core.path
        specification['__loading_name_from_SR__'] = __SR_Loader__
        specification['__loading_process_regulation__'].append(
            ('SR', 0),
        )
        return specification

    def storing_connection(self, specification, usage='train'):
        specification['__storing_path_in_SR__'] = self.__core.path
        specification['__storing_name_in_SR__'] = next(self)
        return specification


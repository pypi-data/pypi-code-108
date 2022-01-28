from ailever.investment import __fmlops_bs__ as fmlops_bs
from ..__base_structures import BaseManagement

import datetime
from pytz import timezone
import re


class ModelPredictionResult(BaseManagement):
    def __init__(self):
        self.__core = fmlops_bs.core['MPR']

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



class ModelPredictionResultManager(BaseManagement):
    def __init__(self):
        self.__core = fmlops_bs.core['MPR']

    def __iter__(self):
        return self

    def __next__(self):
        name = self.__token['ticker']
        return name

    def _local_filesystem_user_interfaces(self):
        self.prediction_grpahs = self.__core.listfiles(format='png')
        self.prediction_tables = self.__core.listfiles(format='csv')

    def _remote_filesystem_user_interfaces(self):
        pass

    def _local_search(self):
        pass

    def _remote_search(self):
        pass

    def remove(self, name:str, framework:str=None):
        self.__core.remove(name=name)

    def clearall(self, framework:str=None):
        self._local_filesystem_user_interfaces(framework=framework)
        for graph in self.prediction_graphs:
            self.__core.remove(name=graph)
        for table in self.prediction_tables:
            self.__core.remove(name=table)

    def copyall(self, framework:str=None):
        self._local_filesystem_user_interfaces(framework=framework)
        for graph in self.prediction_graphs:
            self.__core.copy(name=graph)
        for table in self.prediction_tables:
            self.__core.copy(name=table)

    def listfiles(self, framework:str=None):
        return self.__core.listfiles(format=None)

    def listdir(self, framework:str=None):
        return self.__core.listdir(format=None)

    def loading_connection(self, specification, usage='train'):
        self.__token = specification
        specification['__loading_path_from_MPR__'] = self.__core.path
        specification['__loading_name_from_MPR__'] = None
        return specification

    def storing_connection(self, specification, usage='train'):
        self.__token = specification
        specification['__storing_path_in_MPR__'] = self.__core.path
        specification['__storing_name_in_MPR__'] = next(self)
        specification['__storing_process_regulation__'].append(
            ('MPR', 1),
        )
        return specification


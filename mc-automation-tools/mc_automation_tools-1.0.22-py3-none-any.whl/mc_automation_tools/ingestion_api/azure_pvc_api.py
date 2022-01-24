"""This module will wrap access for azure's pv that raster ingestion based on - not for production testing"""
from mc_automation_tools.configuration import config
from mc_automation_tools import common
from mc_automation_tools import base_requests


class PVCHandler:
    """This is wrapper interface for pvc automation service"""
    __createTestDir = 'createTestDir'
    __updateShape = 'updateShape'
    __changeMaxZoom = 'changeMaxZoom'
    __validatePath = 'validatePath'
    __deleteTestDir = 'deleteTestDir'
    __createWatchDir = 'createWatchDir'
    __updateWatchShape = 'updateWatchShape'
    __changeWatchMaxZoom = 'changeWatchMaxZoom'
    __validateWatchPath = 'validateWatchPath'
    __deleteFromFolder = 'deleteFromFolder'
    __createMockFile = 'createMockFile'

    def __init__(self, endpoint_url, watch=True):
        self.__end_point_url = endpoint_url
        self.__watch = watch

    @property
    def get_class_params(self):
        params = {
            'createTestDir': self.__createTestDir,
            'watch': self.__watch,
            'updateShape': self.__updateShape,
            'changeMaxZoom': self.__changeMaxZoom,
            'validatePath': self.__validatePath,
            'deleteTestDir': self.__deleteTestDir,
            'createWatchDir': self.__createWatchDir,
            'updateWatchShape': self.__updateWatchShape,
            'changeWatchMaxZoom': self.__changeWatchMaxZoom,
            'validateWatchPath': self.__validateWatchPath,
            'deleteFromFolder': self.__deleteFromFolder,
            'createMockFile': self.__createMockFile

        }
        return params

    def create_new_ingestion_dir(self):
        """
        This method will send http get request to pvc server and create new directory of ingested source data
        :return: new directory on pv
        """
        api = self.__createWatchDir if self.__watch else self.__createTestDir
        url = common.combine_url(self.__end_point_url, api)
        resp = base_requests.send_get_request(url)
        return resp

    def change_max_zoom_tfw(self, required_zoom=4):
        """
        This function will send get request and update tfw files to resolution that fit to required zoom level
        :param required_zoom: integer represent zoom level according mapping on config file zoom -> resolution
        """
        params = {'max_zoom': config.zoom_level_dict[required_zoom]}
        api = self.__changeWatchMaxZoom if self.__watch else self.__changeMaxZoom
        url = common.combine_url(self.__end_point_url, api)
        resp = base_requests.send_get_request(url, params)
        return resp

    def make_unique_shapedata(self):
        """
        This method will send http get request to pvc server and change shape metadata to unique running
        :return: new product name and id based on running time string generation
        """
        api = self.__updateWatchShape if self.__watch else self.__updateShape
        url = common.combine_url(self.__end_point_url, api)
        resp = base_requests.send_get_request(url)
        return resp

    def validate_ingestion_directory(self):
        """
        This method validate on pvc directory if directory include all needed files for new discrete
        :param watch: if watch true -> will go to watch configured directory on pvc
        :return: (True , data json if) or (False, str->error reason)
        """
        api = self.__validateWatchPath if self.__watch else self.__validatePath
        url = common.combine_url(self.__end_point_url, api)
        resp = base_requests.send_get_request(url)
        return resp

    def delete_ingestion_directory(self, folder_name):
        """
        This function will delete ingestion test dir
        """
        param = {'folder': folder_name}
        url = common.combine_url(self.__end_point_url, self.__deleteTestDir)
        resp = base_requests.send_get_request(url, param)
        return resp

    def delete_file_from_folder(self, folder_name, file_name):
        """
        This function will delete ingestion test dir
        """
        param = {'folder': folder_name, 'file': file_name}
        url = common.combine_url(self.__end_point_url, self.__deleteFromFolder, )
        resp = base_requests.send_get_request(url, param)
        return resp

    def create_mock_file(self, folder_name, file_name):
        """
        This function will create file in folder
        """
        param = {'folder': folder_name, 'file': file_name}
        url = common.combine_url(self.__end_point_url, self.__createMockFile, )
        resp = base_requests.send_get_request(url, param)
        return resp

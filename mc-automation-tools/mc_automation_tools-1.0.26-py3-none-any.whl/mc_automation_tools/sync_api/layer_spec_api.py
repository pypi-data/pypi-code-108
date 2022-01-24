"""
This module will wrap and provide api's functionality of layer spec api of sync services
"""

import json
import time
import logging
from mc_automation_tools.configuration import config
from mc_automation_tools import base_requests, common

_log = logging.getLogger('mc_automation_tools.sync_api.layer_spec_api')


class LayerSpec:
    __tilesCount = 'tilesCount'

    def __init__(self, end_point_url):
        self.__end_point_url = end_point_url

    @property
    def get_class_params(self):
        params = {
            'tilesCount': self.__tilesCount
        }
        return params

    # ==============================================layer spec api's====================================================
    def get_tiles_count(self, layer_id, target):
        """
        This method will query and return tile count by layer id
        :param layer_id: str -> resourceId [product id] + layer version [product version] -> "productId-productVersion"
        :param target: str -> target of destination of synchronization
        :return: dict -> {status_code, {"tilesCount": int}}
        """
        url = common.combine_url(self.__end_point_url, self.__tilesCount, layer_id, target)
        resp = base_requests.send_get_request(url)
        status_code, content_dict = common.response_parser(resp)
        if status_code != config.ResponseCode.Ok.value:
            raise Exception(
                f'[find_jobs_by_criteria]:failed retrieve tile counts for layer: {layer_id}-target: {target},\n'
                f' return with error:[{status_code}],error msg:[{content_dict}]')
        return status_code, content_dict

    def updates_tile_count(self, layer_id, target, update_value):
        """
        This method based on PUT rest request to update or insert new tile count record for provided layer-target
        example of body:
            {
              "tilesBatchCount": 0
            }
        :param layer_id: str -> resourceId [product id] + layer version [product version] -> "productId-productVersion"
        :param target: str -> target of destination of synchronization
        :param update_value: str -> target of destination of synchronization
        :return: dict -> {"message": "string"}
        """
        url = common.combine_url(self.__end_point_url, self.__tilesCount, layer_id, target)
        if isinstance(update_value, dict):
            body = json.dumps(update_value)
        elif isinstance(update_value, str):
            body = {"tilesBatchCount": update_value}
        elif not isinstance(update_value, str):
            raise ValueError(f'params is not on valid params -> json|dict|str')

        resp = base_requests.send_put_request(url, body)
        status_code, content_dict = common.response_parser(resp)
        if status_code != config.ResponseCode.ChangeOk.value:
            raise Exception(
                f'[updates_tile_count]:failed update tile count, return with error:[{status_code}]:error msg:[{content_dict}]')
        return status_code, content_dict

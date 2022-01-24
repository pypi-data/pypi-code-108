"""
This module provide data validation utils testing data on pycsw [catalog] data
"""
import xmltodict
import logging

from mc_automation_tools import base_requests
from mc_automation_tools.configuration import config
from discrete_kit.validator.json_compare_pycsw import *

_log = logging.getLogger('mc_automation_tools.validators.pycsw_validator')


class PycswHandler:
    """
    This class provide multiple pycsw handlers utilities for mc automation
    can provide param dict for pycsw raster records ->
        ** example:
                {
                    'service': PYCSW_SERVICE, ["CSW"]
                    'version': PYCSW_VERSION, ["2.0.2"]
                    'request': PYCSW_REQUEST_GET_RECORDS, ["GetRecords"]
                    'typenames': PYCSW_TYPE_NAMES, ["mc:MCRasterRecord"]
                    'ElementSetName': PYCSW_ElEMENT_SET_NAME, ["full"]
                    'outputFormat': PYCSW_OUTPUT_FORMAT, ["application/xml"]
                    'resultType': PYCSW_RESULT_TYPE, ["results"]
                    'outputSchema': PYCSW_OUTPUT_SCHEMA [None]
                }
    """

    def __init__(self, pycsw_endpoint_url, get_raster_record_params=None):
        self.__pycsw_endpoint_url = pycsw_endpoint_url
        self.__get_raster_record_params = get_raster_record_params
        if not self.__get_raster_record_params:
            _log.warning("get_raster_record_params not provided for query raster records it may crash on those "
                         "functionalities")

    def set_get_params(self, params):
        """
        This will replace param for query on pycsw
        """
        if params:
            self.__get_raster_record_params = params
        else:
            raise ValueError('Should provide params')

    def validate_pycsw(self, source_json_metadata, product_id=None, product_version=None):
        """
        compare original metadata (represented as dict) with catalog data (pycsw)
        :param source_json_metadata: original meta data dictionary -> {'metadata': {<json data>}}
        :param product_id: layer id
        :param product_version: layer version
        :return: dict of result validation
        """
        res_dict = {'validation': True, 'reason': ""}
        get_records_params = self.__get_raster_record_params
        if not get_records_params:
            raise ValueError('Parameters of <get_raster_record_params> are empty - should provide on instance creation')

        pycsw_records = self.get_record_by_id(product_id,
                                              product_version,
                                              params=get_records_params)

        if not pycsw_records:
            return {"results": {'validation': False, 'reason': f'Records of [{product_id}] not found'}, "pycsw_record": None, "links":None}

        # todo -> mabye delete this section \ refactor to more generic
        links = {}
        for record in pycsw_records:
            links[record['mc:productType']] = {
                record['mc:links'][0]['@scheme']: record['mc:links'][0]['#text'],
                record['mc:links'][1]['@scheme']: record['mc:links'][1]['#text'],
                record['mc:links'][2]['@scheme']: record['mc:links'][2]['#text']
            }

            # source_json_metadata_dic = {'metadata': source_json_metadata}
        # todo -> validate outher data is valid and provided as dict
        source_json_metadata_dic = source_json_metadata
        validation_flag, err_dict = validate_pycsw_with_shape_json(pycsw_records, source_json_metadata_dic, sync_flag=True)

        res_dict['validation'] = validation_flag
        res_dict['reason'] = err_dict
        return {'results': res_dict, 'pycsw_record': pycsw_records, 'links': links}

    def get_record_by_id(self, product_id, product_version, params):
        """
           This method find record by semi unique ID -> product_name & product_id
           :param product_version: discrete version
           :param product_id: discrete id
           :param params: request parameters for GetRecords API request with json result ->
            ** example:
                {
                    'service': PYCSW_SERVICE, ["CSW"]
                    'version': PYCSW_VERSION, ["2.0.2"]
                    'request': PYCSW_REQUEST_GET_RECORDS, ["GetRecords"]
                    'typenames': PYCSW_TYPE_NAMES, ["mc:MCRasterRecord"]
                    'ElementSetName': PYCSW_ElEMENT_SET_NAME, ["full"]
                    'outputFormat': PYCSW_OUTPUT_FORMAT, ["application/xml"]
                    'resultType': PYCSW_RESULT_TYPE, ["results"]
                    'outputSchema': PYCSW_OUTPUT_SCHEMA [None]
                }
           :return: list of records [orthophoto and orthophotoHistory]
       """
        res = self.get_raster_records(params)
        records_list = [record for record in res if
                        (record['mc:productId'] == product_id and record['mc:productVersion'] == product_version)]
        return records_list

    def get_raster_records(self, params):
        """
        This function will return all records of raster's data
        :param params: request parameters for GetRecords API request with json result ->
            ** example:
                {
                    'service': PYCSW_SERVICE, ["CSW"]
                    'version': PYCSW_VERSION, ["2.0.2"]
                    'request': PYCSW_REQUEST_GET_RECORDS, ["GetRecords"]
                    'typenames': PYCSW_TYPE_NAMES, ["mc:MCRasterRecord"]
                    'ElementSetName': PYCSW_ElEMENT_SET_NAME, ["full"]
                    'outputFormat': PYCSW_OUTPUT_FORMAT, ["application/xml"]
                    'resultType': PYCSW_RESULT_TYPE, ["results"]
                    'outputSchema': PYCSW_OUTPUT_SCHEMA [None]
                }
        :return: Dict -> list of records - json format
        """
        records_list = []
        next_record = -1
        host = self.__pycsw_endpoint_url
        try:
            while next_record:
                resp = base_requests.send_get_request(host, params)
                s_code = resp.status_code
                if s_code != config.ResponseCode.Ok.value:
                    raise Exception(
                        f'Failed on request GetRecords with error:[{str(resp.text)}] and status code: [{str(s_code)}]')

                records = xmltodict.parse(resp.content)
                cuurent_records = records['csw:GetRecordsResponse']['csw:SearchResults']['mc:MCRasterRecord']
                params['startPosition'] = records['csw:GetRecordsResponse']['csw:SearchResults']['@nextRecord']
                next_record = int(records['csw:GetRecordsResponse']['csw:SearchResults']['@nextRecord'])
                records_list = records_list + cuurent_records

        except Exception as e:
            raise Exception(f'Failed on request records on pycsw host:[{host}] with error:{str(e)}')
        del params['startPosition']
        return records_list

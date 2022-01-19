# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.3898
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from lusid.api_client import ApiClient
from lusid.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)
from lusid.models.compliance_run import ComplianceRun
from lusid.models.lusid_problem_details import LusidProblemDetails
from lusid.models.lusid_validation_problem_details import LusidValidationProblemDetails
from lusid.models.paged_resource_list_of_compliance_rule_result import PagedResourceListOfComplianceRuleResult
from lusid.models.paged_resource_list_of_compliance_run import PagedResourceListOfComplianceRun


class ComplianceApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def get_compliance_run(self, run_id, **kwargs):  # noqa: E501
        """[EXPERIMENTAL] GetComplianceRun: Get the details of a single compliance run.  # noqa: E501

        Use this endpoint to fetch the detail associated with a specific compliance run, including a breakdown  of the passing state of each rule, portfolio combination.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_compliance_run(run_id, async_req=True)
        >>> result = thread.get()

        :param run_id: The unique identifier of the compliance run requested. (required)
        :type run_id: str
        :param page: The pagination token to use to continue listing compliance rule results from a previous call to list compliance rule result.              This value is returned from the previous call. If a pagination token is provided the sortBy, filter, and asAt fields              must not have changed since the original request. Also, if set, a start value cannot be provided.
        :type page: str
        :param limit: When paginating, limit the number of returned results to this many.
        :type limit: int
        :param filter: Expression to filter the result set. Read more about filtering results from LUSID here https://support.lusid.com/filtering-results-from-lusid.
        :type filter: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: PagedResourceListOfComplianceRuleResult
        """
        kwargs['_return_http_data_only'] = True
        return self.get_compliance_run_with_http_info(run_id, **kwargs)  # noqa: E501

    def get_compliance_run_with_http_info(self, run_id, **kwargs):  # noqa: E501
        """[EXPERIMENTAL] GetComplianceRun: Get the details of a single compliance run.  # noqa: E501

        Use this endpoint to fetch the detail associated with a specific compliance run, including a breakdown  of the passing state of each rule, portfolio combination.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_compliance_run_with_http_info(run_id, async_req=True)
        >>> result = thread.get()

        :param run_id: The unique identifier of the compliance run requested. (required)
        :type run_id: str
        :param page: The pagination token to use to continue listing compliance rule results from a previous call to list compliance rule result.              This value is returned from the previous call. If a pagination token is provided the sortBy, filter, and asAt fields              must not have changed since the original request. Also, if set, a start value cannot be provided.
        :type page: str
        :param limit: When paginating, limit the number of returned results to this many.
        :type limit: int
        :param filter: Expression to filter the result set. Read more about filtering results from LUSID here https://support.lusid.com/filtering-results-from-lusid.
        :type filter: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _return_http_data_only: response data without head status code
                                       and headers
        :type _return_http_data_only: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :return: Returns the result object, the HTTP status code, and the headers.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: (PagedResourceListOfComplianceRuleResult, int, HTTPHeaderDict)
        """

        local_var_params = locals()

        all_params = [
            'run_id',
            'page',
            'limit',
            'filter'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_compliance_run" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'run_id' is set
        if self.api_client.client_side_validation and ('run_id' not in local_var_params or  # noqa: E501
                                                        local_var_params['run_id'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `run_id` when calling `get_compliance_run`")  # noqa: E501

        if self.api_client.client_side_validation and ('run_id' in local_var_params and  # noqa: E501
                                                        len(local_var_params['run_id']) > 64):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `run_id` when calling `get_compliance_run`, length must be less than or equal to `64`")  # noqa: E501
        if self.api_client.client_side_validation and ('run_id' in local_var_params and  # noqa: E501
                                                        len(local_var_params['run_id']) < 1):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `run_id` when calling `get_compliance_run`, length must be greater than or equal to `1`")  # noqa: E501
        if self.api_client.client_side_validation and 'run_id' in local_var_params and not re.search(r'^[a-zA-Z0-9\-_]+$', local_var_params['run_id']):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `run_id` when calling `get_compliance_run`, must conform to the pattern `/^[a-zA-Z0-9\-_]+$/`")  # noqa: E501
        if self.api_client.client_side_validation and ('page' in local_var_params and  # noqa: E501
                                                        len(local_var_params['page']) > 500):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `page` when calling `get_compliance_run`, length must be less than or equal to `500`")  # noqa: E501
        if self.api_client.client_side_validation and ('page' in local_var_params and  # noqa: E501
                                                        len(local_var_params['page']) < 1):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `page` when calling `get_compliance_run`, length must be greater than or equal to `1`")  # noqa: E501
        if self.api_client.client_side_validation and 'page' in local_var_params and not re.search(r'^[a-zA-Z0-9\+\/]*={0,3}$', local_var_params['page']):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `page` when calling `get_compliance_run`, must conform to the pattern `/^[a-zA-Z0-9\+\/]*={0,3}$/`")  # noqa: E501
        if self.api_client.client_side_validation and 'limit' in local_var_params and local_var_params['limit'] > 5000:  # noqa: E501
            raise ApiValueError("Invalid value for parameter `limit` when calling `get_compliance_run`, must be a value less than or equal to `5000`")  # noqa: E501
        if self.api_client.client_side_validation and 'limit' in local_var_params and local_var_params['limit'] < 1:  # noqa: E501
            raise ApiValueError("Invalid value for parameter `limit` when calling `get_compliance_run`, must be a value greater than or equal to `1`")  # noqa: E501
        if self.api_client.client_side_validation and ('filter' in local_var_params and  # noqa: E501
                                                        len(local_var_params['filter']) > 16384):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `filter` when calling `get_compliance_run`, length must be less than or equal to `16384`")  # noqa: E501
        if self.api_client.client_side_validation and ('filter' in local_var_params and  # noqa: E501
                                                        len(local_var_params['filter']) < 0):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `filter` when calling `get_compliance_run`, length must be greater than or equal to `0`")  # noqa: E501
        if self.api_client.client_side_validation and 'filter' in local_var_params and not re.search(r'^[\s\S]*$', local_var_params['filter']):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `filter` when calling `get_compliance_run`, must conform to the pattern `/^[\s\S]*$/`")  # noqa: E501
        collection_formats = {}

        path_params = {}
        if 'run_id' in local_var_params:
            path_params['runId'] = local_var_params['run_id']  # noqa: E501

        query_params = []
        if 'page' in local_var_params and local_var_params['page'] is not None:  # noqa: E501
            query_params.append(('page', local_var_params['page']))  # noqa: E501
        if 'limit' in local_var_params and local_var_params['limit'] is not None:  # noqa: E501
            query_params.append(('limit', local_var_params['limit']))  # noqa: E501
        if 'filter' in local_var_params and local_var_params['filter'] is not None:  # noqa: E501
            query_params.append(('filter', local_var_params['filter']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['text/plain', 'application/json', 'text/json'])  # noqa: E501

        header_params['Accept-Encoding'] = "gzip, deflate, br"


        # set the LUSID header
        header_params['X-LUSID-SDK-Language'] = 'Python'
        header_params['X-LUSID-SDK-Version'] = '0.11.3898'

        # Authentication setting
        auth_settings = ['oauth2']  # noqa: E501
        
        response_types_map = {
            200: "PagedResourceListOfComplianceRuleResult",
            400: "LusidValidationProblemDetails",
        }

        return self.api_client.call_api(
            '/api/compliance/{runId}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_types_map=response_types_map,
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats,
            _request_auth=local_var_params.get('_request_auth'))

    def list_compliance_runs(self, **kwargs):  # noqa: E501
        """[EXPERIMENTAL] ListComplianceRuns: List historical compliance runs.  # noqa: E501

        Use this endpoint to fetch a list of all historical compliance runs.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.list_compliance_runs(async_req=True)
        >>> result = thread.get()

        :param page: The pagination token to use to continue listing compliance runs from a previous call to list compliance runs.              This value is returned from the previous call. If a pagination token is provided the sortBy, filter, and asAt fields              must not have changed since the original request. Also, if set, a start value cannot be provided.
        :type page: str
        :param limit: When paginating, limit the number of returned results to this many.
        :type limit: int
        :param filter: Expression to filter the result set. Read more about filtering results from LUSID here https://support.lusid.com/filtering-results-from-lusid.
        :type filter: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: PagedResourceListOfComplianceRun
        """
        kwargs['_return_http_data_only'] = True
        return self.list_compliance_runs_with_http_info(**kwargs)  # noqa: E501

    def list_compliance_runs_with_http_info(self, **kwargs):  # noqa: E501
        """[EXPERIMENTAL] ListComplianceRuns: List historical compliance runs.  # noqa: E501

        Use this endpoint to fetch a list of all historical compliance runs.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.list_compliance_runs_with_http_info(async_req=True)
        >>> result = thread.get()

        :param page: The pagination token to use to continue listing compliance runs from a previous call to list compliance runs.              This value is returned from the previous call. If a pagination token is provided the sortBy, filter, and asAt fields              must not have changed since the original request. Also, if set, a start value cannot be provided.
        :type page: str
        :param limit: When paginating, limit the number of returned results to this many.
        :type limit: int
        :param filter: Expression to filter the result set. Read more about filtering results from LUSID here https://support.lusid.com/filtering-results-from-lusid.
        :type filter: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _return_http_data_only: response data without head status code
                                       and headers
        :type _return_http_data_only: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :return: Returns the result object, the HTTP status code, and the headers.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: (PagedResourceListOfComplianceRun, int, HTTPHeaderDict)
        """

        local_var_params = locals()

        all_params = [
            'page',
            'limit',
            'filter'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method list_compliance_runs" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']

        if self.api_client.client_side_validation and ('page' in local_var_params and  # noqa: E501
                                                        len(local_var_params['page']) > 500):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `page` when calling `list_compliance_runs`, length must be less than or equal to `500`")  # noqa: E501
        if self.api_client.client_side_validation and ('page' in local_var_params and  # noqa: E501
                                                        len(local_var_params['page']) < 1):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `page` when calling `list_compliance_runs`, length must be greater than or equal to `1`")  # noqa: E501
        if self.api_client.client_side_validation and 'page' in local_var_params and not re.search(r'^[a-zA-Z0-9\+\/]*={0,3}$', local_var_params['page']):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `page` when calling `list_compliance_runs`, must conform to the pattern `/^[a-zA-Z0-9\+\/]*={0,3}$/`")  # noqa: E501
        if self.api_client.client_side_validation and 'limit' in local_var_params and local_var_params['limit'] > 5000:  # noqa: E501
            raise ApiValueError("Invalid value for parameter `limit` when calling `list_compliance_runs`, must be a value less than or equal to `5000`")  # noqa: E501
        if self.api_client.client_side_validation and 'limit' in local_var_params and local_var_params['limit'] < 1:  # noqa: E501
            raise ApiValueError("Invalid value for parameter `limit` when calling `list_compliance_runs`, must be a value greater than or equal to `1`")  # noqa: E501
        if self.api_client.client_side_validation and ('filter' in local_var_params and  # noqa: E501
                                                        len(local_var_params['filter']) > 16384):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `filter` when calling `list_compliance_runs`, length must be less than or equal to `16384`")  # noqa: E501
        if self.api_client.client_side_validation and ('filter' in local_var_params and  # noqa: E501
                                                        len(local_var_params['filter']) < 0):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `filter` when calling `list_compliance_runs`, length must be greater than or equal to `0`")  # noqa: E501
        if self.api_client.client_side_validation and 'filter' in local_var_params and not re.search(r'^[\s\S]*$', local_var_params['filter']):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `filter` when calling `list_compliance_runs`, must conform to the pattern `/^[\s\S]*$/`")  # noqa: E501
        collection_formats = {}

        path_params = {}

        query_params = []
        if 'page' in local_var_params and local_var_params['page'] is not None:  # noqa: E501
            query_params.append(('page', local_var_params['page']))  # noqa: E501
        if 'limit' in local_var_params and local_var_params['limit'] is not None:  # noqa: E501
            query_params.append(('limit', local_var_params['limit']))  # noqa: E501
        if 'filter' in local_var_params and local_var_params['filter'] is not None:  # noqa: E501
            query_params.append(('filter', local_var_params['filter']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['text/plain', 'application/json', 'text/json'])  # noqa: E501

        header_params['Accept-Encoding'] = "gzip, deflate, br"


        # set the LUSID header
        header_params['X-LUSID-SDK-Language'] = 'Python'
        header_params['X-LUSID-SDK-Version'] = '0.11.3898'

        # Authentication setting
        auth_settings = ['oauth2']  # noqa: E501
        
        response_types_map = {
            200: "PagedResourceListOfComplianceRun",
            400: "LusidValidationProblemDetails",
        }

        return self.api_client.call_api(
            '/api/compliance', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_types_map=response_types_map,
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats,
            _request_auth=local_var_params.get('_request_auth'))

    def run_compliance_check(self, file_name, **kwargs):  # noqa: E501
        """[EXPERIMENTAL] RunComplianceCheck: Kick off the compliance check process  # noqa: E501

        Use this endpoint to fetch the start a compliance run, based on a pre-set mapping file.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.run_compliance_check(file_name, async_req=True)
        >>> result = thread.get()

        :param file_name: The name of compliance mappings file to use. Has to exist in drive ComplianceRules folder (required)
        :type file_name: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: ComplianceRun
        """
        kwargs['_return_http_data_only'] = True
        return self.run_compliance_check_with_http_info(file_name, **kwargs)  # noqa: E501

    def run_compliance_check_with_http_info(self, file_name, **kwargs):  # noqa: E501
        """[EXPERIMENTAL] RunComplianceCheck: Kick off the compliance check process  # noqa: E501

        Use this endpoint to fetch the start a compliance run, based on a pre-set mapping file.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.run_compliance_check_with_http_info(file_name, async_req=True)
        >>> result = thread.get()

        :param file_name: The name of compliance mappings file to use. Has to exist in drive ComplianceRules folder (required)
        :type file_name: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _return_http_data_only: response data without head status code
                                       and headers
        :type _return_http_data_only: bool, optional
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :type _preload_content: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :return: Returns the result object, the HTTP status code, and the headers.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: (ComplianceRun, int, HTTPHeaderDict)
        """

        local_var_params = locals()

        all_params = [
            'file_name'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method run_compliance_check" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'file_name' is set
        if self.api_client.client_side_validation and ('file_name' not in local_var_params or  # noqa: E501
                                                        local_var_params['file_name'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `file_name` when calling `run_compliance_check`")  # noqa: E501

        if self.api_client.client_side_validation and ('file_name' in local_var_params and  # noqa: E501
                                                        len(local_var_params['file_name']) > 50):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `file_name` when calling `run_compliance_check`, length must be less than or equal to `50`")  # noqa: E501
        if self.api_client.client_side_validation and ('file_name' in local_var_params and  # noqa: E501
                                                        len(local_var_params['file_name']) < 1):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `file_name` when calling `run_compliance_check`, length must be greater than or equal to `1`")  # noqa: E501
        if self.api_client.client_side_validation and 'file_name' in local_var_params and not re.search(r'^[A-Za-z0-9_\-\.]+[A-Za-z0-9_\-\. ]*$', local_var_params['file_name']):  # noqa: E501
            raise ApiValueError("Invalid value for parameter `file_name` when calling `run_compliance_check`, must conform to the pattern `/^[A-Za-z0-9_\-\.]+[A-Za-z0-9_\-\. ]*$/`")  # noqa: E501
        collection_formats = {}

        path_params = {}

        query_params = []
        if 'file_name' in local_var_params and local_var_params['file_name'] is not None:  # noqa: E501
            query_params.append(('fileName', local_var_params['file_name']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['text/plain', 'application/json', 'text/json'])  # noqa: E501

        header_params['Accept-Encoding'] = "gzip, deflate, br"


        # set the LUSID header
        header_params['X-LUSID-SDK-Language'] = 'Python'
        header_params['X-LUSID-SDK-Version'] = '0.11.3898'

        # Authentication setting
        auth_settings = ['oauth2']  # noqa: E501
        
        response_types_map = {
            200: "ComplianceRun",
            400: "LusidValidationProblemDetails",
        }

        return self.api_client.call_api(
            '/api/compliance/run', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_types_map=response_types_map,
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats,
            _request_auth=local_var_params.get('_request_auth'))

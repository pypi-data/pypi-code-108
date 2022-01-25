import requests
import base64
import datetime
import traceback
import json

############################# Maximo REST API Class ############################
class MAXIMO_REST():
    """
        Maximo API class allows the user to communicate with Maximo REST API using python

        Prerequisites:
        -------------
            - Python > 3.7
            - Maximo access
    """


    _error_msgs = ['An existing connection was forcibly closed by the remote host',
                   'Remote end closed connection without response']

    def __init__(self, base_url, username=None, password=None, api_key=None,
                 authentication_type='LDAP BASIC',
                 max_attempts=1, timeout=None, mif=False,
                 verbose=False, verify=True):
        """

            :param maximo_url: (``string``) - Maximo URL
            :param username: (``string`` - optional) - Default value None
            :param password: (``string`` - optional) - Default value None
            :param api_key: (``string`` - optional) - Default value None
            :param authentication_type: (``string`` - optional) - The only value supported LDAP BASIC (default value LDAP BASIC)
            :param max_attempts: (``int`` - optional) - Maximum number of attempts if disconnected (default value 1)
            :param timeout: (``int`` - optional) - Timeout threshold in seconds (default value None)
            :param mif: (``bool`` - optional) - True if maximo_mif to be used, False if maximo to be used in the URL (default value False)
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False)
            :param verify: (``bool`` - optional) - By pass SSL verification if True (default value True)

            :returns: None
        """

        assert authentication_type in ['LDAP BASIC'], 'Incorrect authentication type'

        if username == None:
            raise Exception('Username is empty, please provide a valid username')

        if password == None:
            raise Exception('Password is empty, please provide a valid password')

        self.base_url = base_url
        self.authentication_type = authentication_type
        self.username = username
        self.password = password
        self.api_key = api_key
        self.max_attempts = max_attempts
        self.timeout = timeout   # TODO: To be added to the REST calls
        if mif:
            self.url_suffix = '_mif'
        else:
            self.url_suffix = ''

        self.verbose = verbose
        self.verify = verify
        self.api_key = self.generate_base64(self.username + ':' + self.password)
        self.session = None
        self.authenticate()

    ######################################################################################
    def generate_base64(self, value):
        """
            Generate base64 string

            :param value: (``string``) - String value to be converted to base64.

            :returns: (``String``) - base64 string.
        """

        return str(base64.b64encode(bytes(value, 'utf-8')), "utf-8")

    ######################################################################################
    def validate_and_return_response(self, response, message, raw=False, content=False):
        """
            Validate response by comparing it against the acceptable status codes. Returns response and status code.

            :param response: (``requests.response``) - The response from the query.
            :param message: (``string`` - optional) - Desired custom error message.
            :param raw: (``bool`` - optional) - Defines whether to return response raw format or json (default value False).
            :param content: (``bool`` - optional) - Defines whether to return response content or json (default value False).

            :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code.
        """

        if response.status_code in [200, 201, 304]:
            if raw:
                return response.raw, response.status_code
            elif content:
                return response.content, response.status_code
            else:
                return response.json(), response.status_code
        else:
            errormsg = str(message) + ' ' + str(response.status_code) + ': ' + str(response.text) + str(response.reason)
            # return errormsg, response.status_code
            raise Exception(errormsg)

    ######################################################################################
    def authenticate(self, verbose=False):
        """
            Authenticate with Maximo using the defined authentication type used in the class constructor

            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :returns: None
        """

        if self.verbose or verbose:
            print('Authenticating with Maximo...')

        if self.authentication_type == 'LDAP BASIC':
            url = self.base_url + '/maximo' + self.url_suffix + '/j_security_check?j_username=' + \
                  self.username + '&j_password=' + self.password

            self.session = requests.Session()
            self.session.get(url)
        else:
            raise Exception(self.authentication_type + ' authentication type not supported')

    ######################################################################################
    def add_param_to_url(self, url, param, value):
        result = url

        if param == None:
            param = value
        else:
            param = param + '=' + str(value)

        if value != None:
            if '?' in result:
                result += '&' + param
            else:
                result += '?' + param

        return result

    ######################################################################################
    def mxapi_get_request(self, url):
        """
            Execute get request.

            :param url: (``string``) - URL to be executed in the get request.

            :return: (``requests.response``)
        """

        if self.authentication_type == 'LDAP BASIC':
            return self.session.get(url,
                                    headers={'Authorization': 'Basic' + self.api_key},
                                    verify=self.verify)
        else:
            raise Exception(self.authentication_type + ' authentication type not supported')

    ######################################################################################
    def mxapi_post_request(self, url, body=None, headers=None):
        """
            Execute get request.

            :param url: (``string``) - URL to be executed in the post request.
            :param body: (``dict`` - optional) - Body to be included in the POST request (default value None).
            :param headers: (``dict`` - optional) - Additional headers to be added in the POST request (default value None).

            :return: (``requests.response``)
        """

        if self.authentication_type == 'LDAP BASIC':
            used_headers = {'Authorization': 'Basic' + self.api_key}

            if headers != None:
                used_headers.update(headers)

            if body != None:
                return self.session.post(url,
                                         headers=used_headers,
                                         data=body,
                                         verify=self.verify)
            else:
                return self.session.post(url,
                                         headers=used_headers,
                                         verify=self.verify)
        else:
            raise Exception(self.authentication_type + ' authentication type not supported')

    ################################## OSLC functions ####################################
    ######################################################################################
    def oslc_get_table(self, tableName, pageSize=None,
                       select=None, where=None, orderBy=None,
                       pageNum=1, stablePaging=False, gbcols=None,
                       verbose=False, current_attempt=1):
        """
            Get data from a specific table in Maximo using OSLC Integration.

            :param tableName: (``string``) - Maximo table name to extract data
            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default Maximo page size will be used (1000).
            :param select: (``string`` - optional) - Maximo table fields to be included in the select query (default value None).
            :param where: (``string`` - optional) - Where condition to filter data (default value None). See https://www.ibm.com/docs/en/mam/7.6.0?topic=orq-query-where-clause-parameter
            :param orderBy: (``string`` - optional) - Field(s) to order data (default value None). + sign indicated ascending and - sign indicates descending
            :param pageNum: (``int`` - optional) - Page number in the response (default value 1). Recommended to leave default.
            :param stablePaging: (``bool`` - optional) - Use Maximo stable paging option (default value False). Recommended to leave default.
            :param gbcols: (``string`` - optional) - Group by columns condition to aggregate data (default value None). See https://www.imwuc.org/HigherLogic/System/DownloadDocumentFile.ashx?DocumentFileKey=f29fb7ba-5917-f2a9-e599-9161e5d14582
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).
            :param current_attempt: (``int`` - **don't use**) - This argument is intended for internal method use only.

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Getting ' + str(tableName) + ' table...')

        # Adding /oslc/ part to the baseURI
        url = self.base_url + '/maximo' + self.url_suffix + '/oslc/os/' + tableName

        # Check page size
        if pageSize != None:
            if '?' in url:
                url += '&oslc.pageSize=' + str(pageSize)
            else:
                url += '?oslc.pageSize=' + str(pageSize)

        # Add select query
        if select != None:
            if '?' in url:
                url += '&oslc.select=' + str(select)
            else:
                url += '?oslc.select=' + str(select)

        # Add where query
        if where != None:
            if '?' in url:
                url += '&oslc.where=' + str(where)
            else:
                url += '?oslc.where=' + str(where)

        # Add order by query
        if orderBy != None:
            if '?' in url:
                url += '&oslc.orderBy=' + str(orderBy)
            else:
                url += '?oslc.orderBy=' + str(orderBy)

        # Add gbcols query
        if gbcols != None:
            if '?' in url:
                url += '&gbcols=' + str(gbcols)
            else:
                url += '?gbcols=' + str(gbcols)

        # Check stable paging
        if stablePaging:
            if '?' in url:
                url += '&stablepaging=true'
            else:
                url += '?stablepaging=true'

        # Check pageNum
        if pageNum > 1:
            if '?' in url:
                url += '&pageno=' + str(pageNum)
            else:
                url += '?pageno=' + str(pageNum)

        # Execute request
        has_more_records = True
        result = {'members': []}
        try:
            while has_more_records:
                response = self.mxapi_get_request(url)
                resp_result, resp_code = self.validate_and_return_response(response,
                                                                           'Get ' + tableName + ' table error')
                if gbcols == None:
                    result['members'].extend(resp_result['rdfs:member'])

                    if 'oslc:nextPage' in resp_result['oslc:responseInfo']:
                        prev_pageNum = pageNum
                        pageNum += 1
                        if '&pageno=' in url:
                            url = url.replace('&pageno=' + str(prev_pageNum), '&pageno=' + str(pageNum))
                        else:
                            url += '&pageno=' + str(pageNum)
                    else:
                        has_more_records = False
                else:
                    result['members'] = resp_result
                    has_more_records = False

            return result, resp_code
        except Exception as e:
            for error_msg in MAXIMO_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if current_attempt <= self.max_attempts:
                        self.authenticate()
                        return self.oslc_get_table(tableName, pageSize=pageSize,
                                                   current_attempt=current_attempt,
                                                   verbose=verbose, select=select,
                                                   where=where, orderBy=orderBy,
                                                   pageNum=pageNum,
                                                   stablePaging=stablePaging, gbcols=gbcols)

            errorMsg = traceback.format_exc()
            raise Exception('Error getting data from table: ' + str(tableName) + '\n' + errorMsg)

    ######################################################################################
    def oslc_create_new_record(self, tableName, parameters, verbose=False):
        """
            Create a new record in a specific table in Maximo.

            :param tableName: (``string``) - Maximo table name
            :param parameters: (``dict``) - Field names (dict keys) and values (dict values) to be inserted
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Inserting new record in ' + str(tableName) + '...')

        # Adding /oslc/ part to the baseURI
        url = self.base_url + '/maximo' + self.url_suffix + '/oslc/os/' + tableName

        try:
            headers = {'Properties': '*'}
            response = self.mxapi_post_request(url, body=parameters, headers=headers)
            resp_result, resp_code = self.validate_and_return_response(response,
                                                                       'Insert new record ' + tableName + ' table error',
                                                                       raw=True)
            return resp_result, resp_code
        except Exception as e:
            errorMsg = traceback.format_exc()
            raise Exception('Error inserting data in table: ' + str(tableName) + '\n' + errorMsg)

    ######################################################################################
    def oslc_update_record(self, tableName, restID, parameters, verbose=False):
        """
            Update specific record in a table in Maximo

            :param tableName: (``string``) - Maximo table name
            :param restID: (``int``) - REST ID for the record to be updated
            :param parameters: (``dict``) - Field names (dict keys) and values (dict values) to be updated
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Updating ' + str(tableName) + ' ' + str(restID) + '...')

        # Adding /oslc/ part to the baseURI
        url = self.base_url + '/maximo' + self.url_suffix + '/oslc/os/' + tableName + '/' + str(restID)

        try:
            headers = {'x-method-override': 'PATCH',
                       'patchtype': 'MERGE',
                       'Properties': '*'}
            response = self.mxapi_post_request(url, body=parameters, headers=headers)
            resp_result, resp_code = self.validate_and_return_response(response,
                                                                       'Update record ' + tableName + ' table error',
                                                                       raw=True)
            return resp_result, resp_code
        except Exception as e:
            errorMsg = traceback.format_exc()
            raise Exception('Error updating data in table: ' + str(tableName) + '\n' + errorMsg)

    ################################# REST functions #####################################
    ######################################################################################
    def mbo_get_table(self, tableName, includecols=None, excludecols=None,
                      orderbyasc=None, orderbydesc=None,
                      where=None, maxItems=None,
                      format='json', compact=1, verbose=False, current_attempt=1):
        """
        Get data from a specific table in Maximo using REST API.
        https://maximo.bia.gov/help/index.jsp?topic=/com.ibm.mif.doc/gp_intfrmwk/rest_api/r_rest_post_method.html

        :param tableName: (``string``) - Maximo table name
        :param includecols: (``string`` - optional) - Comma-separated list of MBO attributes. Includes the listed attributes from the resource response (default value None).
        :param excludecols: (``string`` - optional) - Comma-separated list of MBO attributes. Excludes the listed attributes from the resource response (default value None).
        :param orderbyasc: (``string`` - optional) - Comma-separated list of MBO attributes. Specifies the attributes that are used for the order by clause in ascending order (default value None).
        :param orderbydesc: (``string`` - optional) - Comma-separated list of MBO attributes. Specifies the attributes that are used for the order by clause in descending order (default value None).
        :param where: (``string`` - optional) - Where condition to filter data (default value None).
        :param maxItems: (``int`` - optional) - Specifies the maximum number of business objects that are serialized in the resource collection (default value None).
        :param format: (``string`` - optional) - Specifies the representation of the resource response (default value json). Could be either json or xml.
        :param compact: (``int`` - optional) - If true, JSON data is represented in a compact representation (default value 1).
        :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).
        :param current_attempt: (``int`` - **don't use**) - This argument is intended for internal method use only.

        :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Getting ' + str(tableName) + ' table...')

        # Adding /maxrest/ part to the baseURI
        url = self.base_url + '/maxrest' + self.url_suffix + '/rest/mbo/' + tableName

        # Adding URL parameters
        url = self.add_param_to_url(url, '_format', format)
        url = self.add_param_to_url(url, '_compact', compact)
        url = self.add_param_to_url(url, '_includecols', includecols)
        url = self.add_param_to_url(url, '_excludecols', excludecols)
        url = self.add_param_to_url(url, None, where)
        url = self.add_param_to_url(url, '_orderbyasc', orderbyasc)
        url = self.add_param_to_url(url, '_orderbydesc', orderbydesc)
        url = self.add_param_to_url(url, '_maxItems', maxItems)

        # Adding total records counts to the URL in the rsTotal attribute
        url = self.add_param_to_url(url, '_tc', 1)

        # Execute request
        totalRows = 1
        countRow = 0
        result = {'members': []}
        try:
            while countRow < totalRows:
                urlProc = self.add_param_to_url(url, '_rsStart', countRow)
                response = self.mxapi_get_request(urlProc)
                resp_result, resp_code = self.validate_and_return_response(response,
                                                                           'Get ' + tableName + ' table error')
                mboset = resp_result[tableName.upper() + 'MboSet']
                totalRows = mboset['rsTotal']
                countRow += mboset['rsCount']
                result['members'].extend(mboset[tableName.upper()])
            return result, resp_code
        except Exception as e:
            for error_msg in MAXIMO_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if current_attempt <= self.max_attempts:
                        self.authenticate()
                        return self.mbo_get_table(tableName, includecols=includecols, excludecols=excludecols,
                                                  orderbyasc=orderbyasc, orderbydesc=orderbydesc,
                                                  where=where, maxItems=maxItems,
                                                  format=format, compact=compact,
                                                  verbose=verbose, current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Error getting data from table: ' + str(tableName) + '\n' + errorMsg)

    ######################################################################################
    def mbo_create_new_record(self, tableName, parameters, verbose=False):
        """
            Create a new record in a specific table in Maximo.

            :param tableName: (``string``) - Maximo table name
            :param parameters: (``dict``) - Field names (dict keys) and values (dict values) to be inserted
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Inserting new record in ' + str(tableName) + '...')

        # Adding /maxrest/ part to the baseURI
        url = self.base_url + '/maxrest' + self.url_suffix + '/rest/mbo/' + tableName

        try:
            response = self.mxapi_post_request(url, body=parameters)
            resp_result, resp_code = self.validate_and_return_response(response,
                                                                       'Insert new record ' + tableName + ' table error',
                                                                       raw=True)
            return resp_result, resp_code
        except Exception as e:
            errorMsg = traceback.format_exc()
            raise Exception('Error inserting data in table: ' + str(tableName) + '\n' + errorMsg)

    ######################################################################################
    def mbo_update_record(self, tableName, tableID, parameters, verbose=False):
        """
            Update specific record in a table in Maximo.

            :param tableName: (``string``) - Maximo table name
            :param tableID: (``int``) - Primary key record ID to update
            :param parameters: (``dict``) - Field names (dict keys) and values (dict values) to be updated
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Updating ' + str(tableName) + ' ' + str(tableID) + '...')

        # Adding /maxrest/ part to the baseURI
        url = self.base_url + '/maxrest' + self.url_suffix + '/rest/mbo/' + tableName + '/' + str(tableID)

        try:
            response = self.mxapi_post_request(url, body=parameters)
            resp_result, resp_code = self.validate_and_return_response(response,
                                                                       'Update record ' + tableName + ' table error',
                                                                       raw=True)
            return resp_result, resp_code
        except Exception as e:
            errorMsg = traceback.format_exc()
            raise Exception('Error updating data in table: ' + str(tableName) + '\n' + errorMsg)

    ######################################################################################
    def mbo_exec_method(self, tableName, tableID, method, method_parameters=None, verbose=False):
        """
            Execute a method on a specific MBO in Maximo.

            :param tableName: (``string``) - Maximo table name
            :param tableID: (``int``) - Primary key record ID to update
            :param method: (``string``) - Name of the method to be executed
            :param method_parameters: (``dict``) - Method parameters
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Executing method ' + str(method) + ' on table ' + str(tableName) + ' on record ' + str(tableID) + '...')

        # Adding /maxrest/ part to the baseURI
        url = self.base_url + '/maxrest' + self.url_suffix + '/rest/mbo/' + tableName + '/' + str(tableID)

        # Add method parameters
        if method_parameters != None:
            for key in method_parameters.keys():
                if '?' in url:
                    url += '&~' + key + '=' + str(method_parameters[key])
                else:
                    url += '?~' + key + '=' + str(method_parameters[key])

        try:
            headers = {'x-http-method-override': method}
            response = self.mxapi_post_request(url, headers=headers)
            resp_result, resp_code = self.validate_and_return_response(response,
                                                                       'Executing method ' + method + ' error',
                                                                       raw=True)
            return resp_result, resp_code
        except Exception as e:
            errorMsg = traceback.format_exc()
            raise Exception('Error: ' + str(method) + '\n' + errorMsg)

    ################################# Table functions #####################################
    #######################################################################################
    def get_mx_wos(self, select_fields='*', where=None, orderBy=None, gbcols=None, oslc=True, pageSize=100):
        """
            Execute query and get WOs.

            :param select_fields: (``string`` - optional) - Fields included in the query (defaul value *)
            :param where: (``string`` - optional) - Where condition to be included in the query (defaul value None)
            :param orderBy: (``string`` - optional) - Field(s) to order data (default value None). + sign indicated ascending and - sign indicates descending
            :param gbcols: (``string`` - optional) - Group by columns condition to aggregate data (default value None). See https://www.imwuc.org/HigherLogic/System/DownloadDocumentFile.ashx?DocumentFileKey=f29fb7ba-5917-f2a9-e599-9161e5d14582
            :param oslc: (``bool`` - optional) - Defines whether to use oslc protocol or not (default value True)
            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default Maximo page size will be used (1000).

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        if gbcols == None:
            return self.oslc_get_table('mxwo', select=select_fields, where=where, orderBy=orderBy, pageSize=pageSize)
        else:
            return self.oslc_get_table('mxwo', gbcols=gbcols)

    ######################################################################################
    def get_mx_srs(self, select_fields='*', where=None, orderBy=None, gbcols=None, oslc=True, pageSize=100):
        """
            Execute query and get Service Requests.

            :param select_fields: (``string`` - optional) - Fields included in the query (defaul value *)
            :param where: (``string`` - optional) - Where condition to be included in the query (defaul value None)
            :param orderBy: (``string`` - optional) - Field(s) to order data (default value None). + sign indicated ascending and - sign indicates descending
            :param gbcols: (``string`` - optional) - Group by columns condition to aggregate data (default value None). See https://www.imwuc.org/HigherLogic/System/DownloadDocumentFile.ashx?DocumentFileKey=f29fb7ba-5917-f2a9-e599-9161e5d14582
            :param oslc: (``bool`` - optional) - Defines whether to use oslc protocol or not (default value True)
            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default Maximo page size will be used (1000).

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        if gbcols == None:
            return self.oslc_get_table('mxsr', select=select_fields, where=where, orderBy=orderBy, pageSize=pageSize)
        else:
            return self.oslc_get_table('mxsr', gbcols=gbcols)

######################################################################################
################################### Start Script #####################################
if __name__ == '__main__':
    maximoURL = ''
    username = ''
    password = ''

    mx_obj = MAXIMO_REST(maximoURL, username, password)
    print(mx_obj.getTable('mxasset', select='*'))
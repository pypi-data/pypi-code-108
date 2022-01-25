import requests
import base64
import datetime
import traceback
import json

############################# NEXUS REST API V2 Functions ############################
class NEXUSIC_REST():
    """
    NEXUS IC REST API class allows the user to communicate with Wood NEXUS IC REST API using python.

    Prerequisites:
    -------------
        - Python > 3.7
        - NEXUS IC > V6.6
        - IC-Web > V6.6

    NEXUS IC Documentation:
    ----------------------
        The NEXUS IC REST API documentation can be found in the below link:
        https://docs.nexusic.com/6.6/ic-web.rest.v2.html

        A specific NEXUS IC version can be specified in the above link by changing **6.6** to the desired NEXUS IC version*
    """

    _error_msgs = ['An existing connection was forcibly closed by the remote host',
                   'Remote end closed connection without response']

    def __init__(self, icweb_uri, authentication_type='APIKEY',
                 username=None, password=None, api_key=None,
                 max_attempts=1, timeout=None, verbose=False, verify=True):
        """

            :param icweb_uri: (``string``) - IC-Web URL.
            :param authentication_type: (``string`` - optional) - This can be one of the following values  (default value APIKEY).

                .. code-block:: python

                        ['APIKEY', 'BASIC']

            :param username: (``string`` - optional) - Default value None.
            :param password: (``string`` - optional) - Default value None.
            :param api_key: (``string`` - optional) - Default value None.
            :param max_attempts: (``int`` - optional) - Maximum number of attempts if disconnected (default value 1).
            :param timeout: (``int`` - optional) - Timeout threshold in seconds (default value None).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).
            :param verify: (``bool`` - optional) - By pass SSL verification if True (default value True).

            :returns: None
        """

        self.icweb_uri = icweb_uri
        self.authentication_type = authentication_type

        self.api_key = api_key
        self.username = username
        self.password = password

        self.max_attempts = max_attempts
        self.timeout = timeout   # TODO: To be added to the REST calls
        self.verbose = verbose
        self.verify = verify

        assert authentication_type in ['APIKEY', 'BASIC'], 'Incorrect authentication type'

        if authentication_type == 'APIKEY':
            if self.api_key != None:
                self.key_64 = self.generate_base64(api_key)
            else:
                raise Exception('API Key is not valid, please provide a valid API Key')
        elif authentication_type == 'BASIC':
            if self.username != None or self.password != None:
                self.key_64 = self.generate_base64(self.username + ':' + self.password)
            else:
                raise Exception('Username and/or password are not valid, please provide a valid username/password')
        else:
            raise Exception('Authentication type was not specified')

        self.hash = self.generate_hash()

        # Get current NEXUS version
        version, version_status_code = self.getVersion()
        self.version = version['version'].split('.')
        self.schema = version['schema'].split('.')

    ################################ Core REST API Calls #################################
    ######################################################################################
    def generate_base64(self, value):
        """
            Generate base64 string

            :param value: (``string``) - String value to be converted to base64.

            :returns: (``String``) - base64 string.
        """
        return str(base64.b64encode(bytes(value, 'utf-8')), "utf-8")

    ######################################################################################
    def generate_hash(self, verbose=False):
        """
            Generate hash key to be used in the REST calls

            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``string``) - Hash key
        """

        result, result_code = self.authenticate(verbose=verbose)

        if result_code == 200:
            return result.get('hash')
        else:
            errorMsg = traceback.format_exc()
            raise Exception(result + '\n' + errorMsg)

    ######################################################################################
    def addParamToURI(self, uri, param, value):
        if '?' in uri:
            newUri = uri + '&' + param + '=' + value
        else:
            newUri = uri + '?' + param + '=' + value

        return newUri

    ######################################################################################
    def validate_and_return_response(self, response, message, raw=False):
        """
            Validate response by comparing it against the acceptable status codes. Returns response and status code.

            :param response: (``requests.response``) - The response from the query.
            :param message: (``string`` - optional) - Desired custom error message.
            :param raw: (``bool`` - optional) - Defines whether to return response raw format or json (default value False).

            :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code.
        """

        if response.status_code in [200]:
            if raw:
                return response.raw, response.status_code
            else:
                return response.json(), response.status_code
        else:
            return str(message) + str(response.status_code) + ': ' + str(response.text), \
                   response.status_code

    ######################################################################################
    def authenticate(self, verbose=False):
        """
            Authenticate with NEXUS IC using the defined authentication type used in the class constructor.
            For more details see https://docs.nexusic.com/6.6/ic-web.rest.security.login.html#ic-web-rest-security-login

            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Authenticating with NEXUS IC...')

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        uri = baseURI + '/security/login'
        res = requests.get(uri, headers={'Authorization': self.authentication_type + ' ' + self.key_64},
                           verify=self.verify)

        return self.validate_and_return_response(res, 'Authentication error ')

    ######################################################################################
    def getVersion(self, current_attempt=1, verbose=False):
        if self.verbose or verbose:
            print('Getting NEXUS IC version...')

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        uri = baseURI + '/version' + '?hash=' + self.hash

        try:
            res = requests.get(uri, verify=self.verify)
            result, result_code = self.validate_and_return_response(res, 'Get version error ')
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.getVersion(current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    def getTable(self, tableDBName, xFilter=None, pageSize=None,
                 current_attempt=1, verbose=False):
        """
            Execute GET REST call to get data from specific table

            :param tableDBName: (``string``) - Table name as specified in the database (not the NEXUS IC display table name).
            :param xFilter: ( ``dict`` in ``JSON`` fomrat - optional) - Used to filter data from the required table (default value None).
            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default NEXUS IC page size will be used (100).
            :param current_attempt: (``int`` - **don't use**) - This arugment is intended for internal method use only.
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Getting ' + str(tableDBName) + '...')

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        uri = baseURI + '/bo/' + tableDBName + '/'

        # Adding pageSize
        if pageSize == None:
            pageSize = 100

        uri = self.addParamToURI(uri, 'pageSize', str(pageSize))

        # Adding startRow
        startRow = 0
        uri = self.addParamToURI(uri, 'startRow', str(startRow))

        # Adding hash value
        uri = self.addParamToURI(uri, 'hash', self.hash)

        try:
            if xFilter != None:
                res = requests.get(uri, headers={'X-NEXUS-Filter': xFilter}, verify=self.verify)
            else:
                res = requests.get(uri, verify=self.verify)

            result, result_code = self.validate_and_return_response(res, 'Get ' + tableDBName + ' table error ')

            # Get next page
            uri = uri.replace('startRow=' + str(startRow), 'startRow=' + str(pageSize))
            startRow = pageSize
            while len(result['rows']) < result['totalRows']:
                if xFilter != None:
                    res = requests.get(uri, headers={'X-NEXUS-Filter': xFilter}, verify=self.verify)
                else:
                    res = requests.get(uri, verify=self.verify)

                result2, result_code2 = self.validate_and_return_response(res, 'Get ' + tableDBName + ' table error ')
                result['rows'].extend(result2['rows'])

                prevStartRow = startRow
                startRow += pageSize
                uri = uri.replace('startRow=' + str(prevStartRow), 'startRow=' + str(startRow))

            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.getTable(tableDBName, xFilter=xFilter, pageSize=pageSize,
                                        current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    def deleteRecord(self, tableDBName, keyValue, current_attempt=1, verbose=False):
        if self.verbose or verbose:
            print('Deleting from ' + str(tableDBName) + '...')

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        uri = baseURI + '/bo/' + tableDBName + '/' + str(keyValue) + '/' + '?hash=' + self.hash

        try:
            res = requests.delete(uri, verify=self.verify)
            result, result_code = self.validate_and_return_response(res, 'Delete ' + tableDBName + ' table error ')
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.deleteRecord(tableDBName, keyValue, current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    def getMultimedia(self, rd_id, current_attempt=1, verbose=False):
        if self.verbose or verbose:
            print('Getting multimedia: ' + str(rd_id) + '...')

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        xFilter = str(rd_id) + '/File_Data'
        uri = baseURI + '/bo/' + 'Repository_Data' + '/' + xFilter + '/' + '?hash=' + self.hash

        try:
            res = requests.get(uri, stream=True, verify=self.verify)
            result, result_code = self.validate_and_return_response(res, 'Get multimeida error ', raw=True)
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.getMultimedia(rd_id, current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    # V6.6 or later
    def getDashboard(self, dashboard_Name, current_attempt=1, verbose=False):
        # Check if minor version is 6
        if not(int(self.version[1]) >= 6):
            return 'This function is not supported in the current NEXUS IC version', 404

        if self.verbose or verbose:
            print('Generating NEXUS IC dashboard...')

        # Get RT_ID
        xFilter = '{"where": [{"field": "Name", "value": "' + dashboard_Name + '"}]}'
        report_json, report_status = self.getTable('Report_Template', xFilter=xFilter)

        if report_status == 404:
            return str(report_status) + ': ' + str(report_json), report_status
        else:
            rt_id = report_json['rows'][0]['RT_ID']

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        uri = baseURI + '/dashboard/' + str(rt_id) + '/' + '?hash=' + self.hash

        try:
            res = requests.get(uri, verify=self.verify)
            result, result_code = self.validate_and_return_response(res, 'Get ' + dashboard_Name + ' error ')
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.getDashboard(dashboard_Name, current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    def generateReport(self, report_name, recipient, format='XLSX', current_attempt=1,
                       verbose=False):
        if self.verbose or verbose:
            print('Generating NEXUS IC report...')

        # Get RT_ID
        xFilter = '{"where": [{"field": "Name", "value": "' + report_name + '"}]}'
        report_json, report_status = self.getTable('Report_Template', xFilter=xFilter)

        if report_status == 404:
            return str(report_status) + ': ' + str(report_json), report_status
        else:
            rt_id = report_json['rows'][0]['RT_ID']

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        # Generate report
        uri = baseURI + '/web/generateReport'
        uri += '?key=' + str(rt_id) + '&format=' + format + '&recipient=' + recipient + '&hash=' + self.hash

        try:
            res = requests.post(uri, verify=self.verify)
            result, result_code = self.validate_and_return_response(res, 'Generate ' + report_name + ' report error ')
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.generateReport(report_name, recipient, format=format,
                                              current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)
    
    ######################################################################################
    # V6.7 or later
    def generateReport_v2(self, report_name=None, report_id=None, format='XLSX', parameters=None, current_attempt=1,
                       verbose=False):
        """
            Generate a report from Report_Template table using RT_ID.

            :param report_name: (``string`` - optional) - Name of report as it appears in NEXUS (default value None). 
            :param report_id: (``string`` - optional) - RT_ID value for the report (default value None). When default is used the RT_ID will be determined from report_name.
            :param format: (``string`` - optional) - Format of document to be generated (default value XLSX). 
            :param parameters: (``tuple`` - optional) - Report parameters in a json-formatted dict (default value None).
            :param current_attempt: (``int`` **don't use**) - This arugment is intended for internal method use only.
            :param verbose: (``bool`` - optional) - Show more details in command line output (default value False).

            :return: (``tuple`` - dict, int) - server job information (json, raw or error string) and response status code.
        """
        # Check if minor version is 7
        if not (int(self.version[1]) >= 7):
            return 'This function is not supported in the current NEXUS IC version', 404

        if self.verbose or verbose:
            print('Generating NEXUS IC report...')

        rt_id = report_id
        
        # Get RT_ID
        if not rt_id:
            rt_id = self.get_rt_id(report_name)
            if self.verbose or verbose:
                print('Determined Report ID = {}'.format(str(rt_id)))

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        # Set up the POST request body
        uri = baseURI + '/report/' +'?hash=' + self.hash
        json_dict = json.dumps({'reportTemplate': rt_id,
                                'outputType': format,
                                'parameters': parameters
                                })
        try:
            res = requests.post(uri, data=json_dict)
            result, result_code = self.validate_and_return_response(res, 'Generate ' + (report_name if report_name else "") + str((report_id if report_id else "")) + ' report error ')
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.generateReport_v2(report_name, report_id, format=format,
                                              current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    def jobStatus(self, job_id, current_attempt=1,
                       verbose=False):
        """
            Get the Job Status of a job via its job ID.

            :param job_id: (``int``) - Unique job ID provided in server response. 
            :param current_attempt: (``int`` **don't use**) - This arugment is intended for internal method use only.
            :param verbose: (``bool`` - optional) - Show more details in command line output (default value False).

            :return: (``tuple`` - dict, int) - Job Status information (json, raw or error string) and response status code.
        """
        # Check if minor version is 7
        if not (int(self.version[1]) >= 7):
            return 'This function is not supported in the current NEXUS IC version', 404
        
        if self.verbose or verbose:
            print('Getting NEXUS IC job status...')

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'
        uri = baseURI + '/jobStatus' + '?hash=' + self.hash + '&id=' + str(job_id)

        try:
            res = requests.get(uri)
            result, result_code = self.validate_and_return_response(res, 'Get Job Status of Job ' + str(job_id) + ' error ')
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.jobStatus(job_id, current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    def jobContent(self, job_id, current_attempt=1,
                       verbose=False):
        """
            Get the Job Content of a job via its job ID.

            :param job_id: (``int``) - Unique job ID provided in server response. 
            :param current_attempt: (``int`` **don't use**) - This arugment is intended for internal method use only.
            :param verbose: (``bool`` - optional) - Show more details in command line output (default value False).

            :return: (``tuple`` - dict, int) - Job Content information (json, raw or error string) and response status code.
        """
        # Check if minor version is 7
        if not (int(self.version[1]) >= 7): 
            return 'This function is not supported in the current NEXUS IC version', 404

        if self.verbose or verbose:
            print('Getting NEXUS IC job content...')

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'
        uri = baseURI + '/jobContent' + '?hash=' + self.hash + '&id=' + str(job_id)

        try:
            res = requests.get(uri, stream=True)
            result, result_code = self.validate_and_return_response(res, 'Get Job Content of Job ' + str(job_id) + ' error ', raw=True)
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.jobContent(job_id, current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    def execFunction(self, functionName, parameters=None, current_attempt=1,
                     verbose=False):
        if self.verbose or verbose:
            print('Executing ' + str(functionName) + '...')

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        uri = baseURI + '/function/' + functionName
        uri += '/' + '?hash=' + self.hash

        try:
            res = requests.post(uri, json=parameters, verify=self.verify)
            result, result_code = self.validate_and_return_response(res, 'Execute function ' + functionName + ' error ')
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.execFunction(functionName, parameters=parameters,
                                            current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    def execUpdate(self, tableDBName, tableID, body, current_attempt=1, verbose=False):
        if self.verbose or verbose:
            print('Updating ' + str(tableDBName) + '...')

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        uri = baseURI + '/bo/' + tableDBName + '/' + tableID
        uri += '?hash=' + self.hash

        try:
            res = requests.post(uri, json=body, verify=self.verify)
            result, result_code = self.validate_and_return_response(res, 'Updating ' + tableDBName + ' error ')
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.execUpdate(tableDBName, tableID, body,
                                          current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    def createNewRecord(self, tableDBName, body, key_value=0, current_attempt=1, verbose=False):
        if self.verbose or verbose:
            print('Creating new record in ' + str(tableDBName) + '...')

        # Adding /data/icweb.dll part to the baseURI
        baseURI = self.icweb_uri + '/data/icweb.dll'

        uri = baseURI + '/bo/' + tableDBName + '/' + str(key_value)
        uri += '?hash=' + self.hash

        try:
            res = requests.put(uri, json=body, verify=self.verify)
            result, result_code = self.validate_and_return_response(res, 'Creating new record in ' + tableDBName + ' error ')
            return result, result_code
        except Exception as e:
            for error_msg in NEXUSIC_REST._error_msgs:
                if error_msg in str(e):
                    current_attempt += 1
                    if (current_attempt <= self.max_attempts) and not (self.key_64 == None):
                        self.hash = self.generate_hash()
                        return self.createNewRecord(tableDBName, body, key_value=key_value,
                                                    current_attempt=current_attempt)

            errorMsg = traceback.format_exc()
            raise Exception('Number of attempts: ' + str(current_attempt) + '\n' + errorMsg)

    ######################################################################################
    def importRepository(self, filename, binary_data, verbose=False):
        """
        This call import external documentation in the database to be used with other modules within NEXUS IC

        :param filename: (``string``) - Name of the file to be imported
        :param binary_data: (``byte``) - The actual file as a byte variable
        :param verbose: (``bool`` - optional) - Print internal messages if True (default value False)

        :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code
        """

        if self.verbose or verbose:
            print('Importing repository...')

        postblob_uri = self.icweb_uri + '/data/icweb.dll/postBlob' +'?hash=' + self.hash

        try:
            # Execute post blob
            res = requests.post(postblob_uri, data=binary_data, verify=self.verify)
            result, result_code = self.validate_and_return_response(res, 'Importing repository error ')

            # Post blob result code check
            if result_code == 403:
                raise Exception('Not authorized')
            elif result_code == 404.13:
                raise Exception('File exceeds maximum IIS size')
            elif result_code == 404:
                raise Exception('Business object was not found')

            # Create new record in Repository table
            body = {'UNC': filename, 'File_Data': result['guid']}
            result, result_code = self.createNewRecord('Repository', body=body)
            return result, result_code
        except Exception as e:
            raise Exception(traceback.format_exc())

    ############################ Specific REST API Calls #################################
    ######################################################################################
    def getAssetLocationByName(self, assetName, assetView,
                         pageSize=None, verbose=False):
        x_filter = {"operator": "and",
                    "where": [{"field": "Comp_View.Name", "value": assetView},
                              {"field": "Component.Name", "value": assetName}]
                    }

        x_filter = json.dumps(x_filter)

        result, result_code = self.getTable('View_Node', xFilter=x_filter, pageSize=pageSize, verbose=verbose)

        return result, result_code

    ######################################################################################
    def getAssetLocationByID(self, assetID, assetView,
                         pageSize=None, verbose=False):
        x_filter = {"operator": "and",
                    "where": [{"field": "Comp_View.Name", "value": assetView},
                              {"field": "Component.Component_ID", "value": assetID}]
                    }

        x_filter = json.dumps(x_filter)

        result, result_code = self.getTable('View_Node', xFilter=x_filter, pageSize=pageSize, verbose=verbose)

        return result, result_code

    ######################################################################################
    def getAssetChildren(self, assetLocation, assetView=None, searchType='MAX LEVEL', assetTypes=None,
                         maxLevel=-1, atLevel=-1, pageSize=None, verbose=False):
        assert searchType in ['MAX LEVEL', 'AT LEVEL'], 'Incorrect search type'

        x_filter = {"operator": "and",
                    "where": [{"field": "View_Node.VN_ID", "method": "ch", "value": assetLocation}]
                    }

        # Apply asset view filter
        if assetView != None:
            x_filter['where'].append({"field": "Comp_View.Name", "value": assetView})

        # Apply asset type filters
        if assetTypes != None:
            # Get asset type IDs
            assetTypeIDs = self.getAssetTypesID(assetTypes, pageSize=pageSize, verbose=verbose)

            # Asset children filter
            x_filter['where'].append({"field": "CT_ID", "method": "in", "items": assetTypeIDs})

        # Apply level filter
        if searchType == 'MAX LEVEL' and maxLevel != -1:
            x_filter['where'].append({"field": "Level", "method": "le", "value": maxLevel})
        elif searchType == 'AT LEVEL' and atLevel != -1:
            x_filter['where'].append({"field": "Level", "value": atLevel})

        x_filter = json.dumps(x_filter)

        result, result_code = self.getTable('View_Node', xFilter=x_filter, pageSize=pageSize, verbose=verbose)

        return result, result_code

    ######################################################################################
    def getAssetTypesID(self, assetTypes, pageSize=None, verbose=False):
        assetTypeIDs = []
        for assetType in assetTypes:
            at_x_filter = {"where": [{"field": "Name", "value": assetType}]}
            at_x_filter = json.dumps(at_x_filter)
            result, result_code = self.getTable('Comp_Type', xFilter=at_x_filter,
                                                pageSize=pageSize, verbose=verbose)

            if len(result['rows']) != 0:
                assetTypeIDs.append(result['rows'][0]['CT_ID'])
            else:
                assetTypeIDs.append('Asset type does not exist in the database')

        return assetTypeIDs

    ######################################################################################
    def getTableDBNames(self, tableNames, tableType, pageSize=None, verbose=False):
        tableDBNames = []

        for tableIndex, tableName in enumerate(tableNames):
            x_filter = {"operator": "and",
                        "where": [{"field": "Name", "value": tableName},
                                  {"field": "Def_Type.Name", "value": tableType}]
                        }
            x_filter = json.dumps(x_filter)

            result, result_code = self.getTable('Table_Def', xFilter=x_filter,
                                                pageSize=pageSize, verbose=verbose)

            for row in result['rows']:
                tableDBNames.append(row['Table_Name'])

        return tableDBNames

    ######################################################################################
    def getAssetByFullLocation(self, fullLocation, assetView=None, pageSize=None, verbose=False):
        """
            Get Asset details from View_Node table using full location.

            :param fullLocation: (``string``) - Full location is specified the same way it is defined in a typical NEXUS import sheet (single column)
            :param assetView: (``string`` - optional) - Asset view name (default value None)
            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default NEXUS IC page size will be used (100).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code.
        """

        x_filter = {"operator": "and",
                    "where": [{'field': 'View_Node.Full_Location', 'value': fullLocation}]
                    }

        # Apply asset view filter
        if assetView != None:
            x_filter['where'].append({"field": "Comp_View.Name", "value": assetView})

        x_filter = json.dumps(x_filter)

        result, result_code = self.getTable('View_Node', xFilter=x_filter,
                                            pageSize=pageSize, verbose=verbose)

        return result, result_code

    ######################################################################################
    def getTableDefInfo(self, tableName, tableType, pageSize=None, verbose=False):
        x_filter = {"operator": "and",
                    "where": [{"field": "Name", "value": tableName},
                              {"field": "Def_Type.Name", "value": tableType}]
                    }
        x_filter = json.dumps(x_filter)

        result, result_code = self.getTable('Table_Def', xFilter=x_filter,
                                            pageSize=pageSize, verbose=verbose)

        return result, result_code

    ######################################################################################
    def getLookupListItem(self, LI_ID, verbose=False):
        """
            Gets lookup item ifnormation given a lookup item ID

            :param LI_ID: (``int``) - Lookup item ID in the database
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code.
        """

        x_filter = {'operator': 'and',
                    'where': [{'field': 'Lookup_Item.LI_ID', 'value': LI_ID}]
                    }
        x_filter = json.dumps(x_filter)
        result, result_code = self.getTable('Lookup_Item', xFilter=x_filter, verbose=verbose)
        return result, result_code

    ######################################################################################
    def createNewEvents(self, events, sameAsset=False, sameWorkpack=False,
                        sameEventType=False, sameSurveySet=False,
                        pageSize=None, verbose=False):
        """
            Imports new events in the NEXUS IC database. This function creates new event and doesn't update existing events

            :param events: (``list``) - Events to be imported. Must follow the following format:

                .. code-block:: python

                        events = [{'component_id': xxxx,
                                    'asset_full_location': 'xxxx / xxxx',
                                    'event_type': 'xxxx',
                                    'workpack_name': 'xxxx',
                                    'survey_set': 'xxxx',
                                    'start_clock': 'YYYY-MM-DDThh:mm:ss.ssssZ',
                                    'end_clock': 'YYYY-MM-DDThh:mm:ss.ssssZ',
                                    'comment': 'xxxxx',
                                    'fields': {'<Field Name 1>': xxx,
                                                '<Field Name 2>': xxx,
                                                '<Field Name 3>': xxx
                                                },
                                    'multimedia': [{'name': 'xxxx',
                                                    'filename': 'xxxx/xxxx',
                                                    'binary_data': b'xxxx'}
                                                  ]
                                    }
                                ]

                where:

                - component_id: Optional if asset_full_location is provided - Using component_id provides better performance
                - asset_full_location: Optional if component_id is provided - Follows the same format as the standard NEXUS import sheet (single column)
                - survey_set: Optional (default value is Raw Survey Data)
                - start_clock and end_clock: YYYY for years, MM for months, DD for days, hh for hours, mm for minutes, ss for seconds and .ssss for milliseconds
                - fields: NEXUS field names are the keys (as shown in NEXUS IC)
                - multimedia: Optional - List of multimedia to be imported with each event

            :param sameAsset: (``bool`` - optional) - Used when all events have the same asset.
            :param sameWorkpack: (``bool`` - optional) - Used when all events have the same workpack.
            :param sameEventType: (``bool`` - optional) - Used when all events have the same event type.
            :param sameSurveySet: (``bool`` - optional) - Used when all events have the same survey set.
            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default NEXUS IC page size will be used (100).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - list, list) - List of imported events and missed events.
        """

        imported_events = []
        missed_events = []
        prev_asset_full_location = None
        prev_workpack_name = None
        prev_event_type = None
        prev_survey_set = None

        for event_idx, event in enumerate(events):
            print('Importing new events...' + str(event_idx + 1) + ' of ' + str(len(events)))

            # Get Asset by Full Location
            # --------------------------
            if sameAsset and event_idx > 0:
                if component_id == None:
                    continue
            else:
                if 'component_id' in event.keys():
                    component_id = event['component_id']
                elif 'asset_full_location' in event.keys():
                    if event['asset_full_location'] != prev_asset_full_location:
                        prev_asset_full_location = event['asset_full_location']
                        result, result_code = self.getAssetByFullLocation(event['asset_full_location'], pageSize=pageSize,
                                                                          verbose=verbose)
                        if len(result['rows']) == 0:
                            component_id = None
                            missed_events.append({'Event': event,
                                                  'Reason': 'Asset was not found in database'})
                            continue
                        else:
                            component_id = result['rows'][0]['Component_ID']
                else:
                    component_id = None
                    missed_events.append({'Event': event,
                                          'Reason': 'asset_full_location key was not found in input dictionary'})
                    continue

            # Get Workpack ID
            # ---------------
            if sameWorkpack and event_idx > 0:
                if workpack_id == None:
                    continue
            else:
                if 'workpack_name' in event.keys():
                    if event['workpack_name'] != prev_workpack_name:
                        prev_workpack_name = event['workpack_name']
                        x_filter = {"operator": "and",
                                    "where": [{'field': 'Workpack.Name', 'value': event['workpack_name']}]
                                    }
                        x_filter = json.dumps(x_filter)
                        result, result_code = self.getTable('Workpack', xFilter=x_filter, pageSize=pageSize,
                                                            verbose=verbose)
                        if len(result['rows']) == 0:
                            workpack_id = None
                            missed_events.append({'Event': event,
                                                  'Reason': 'Workpack was not found in database'})
                            continue
                        else:
                            workpack_id = result['rows'][0]['Workpack_ID']
                else:
                    workpack_id = None
                    missed_events.append({'Event': event,
                                          'Reason': 'workpack_name key was not found in input dictionary'})
                    continue

            # Get event type table def information
            # ------------------------------------
            if sameEventType and event_idx > 0:
                if td_id == None:
                    continue
            else:
                if 'event_type' in event.keys():
                    if event['event_type'] != prev_event_type:
                        prev_event_type = event['event_type']
                        result, result_code = self.getTableDefInfo(event['event_type'], 'Event', pageSize=pageSize,
                                                                   verbose=verbose)

                        if len(result['rows']) == 0:
                            result, result_code = self.getTableDefInfo(event['event_type'], 'Continuous Event',
                                                                       pageSize=pageSize, verbose=verbose)

                            if len(result['rows']) == 0:
                                td_id = None
                                missed_events.append({'Event': event,
                                                      'Reason': 'Event type was not found in database'})
                                continue
                            else:
                                td_id = result['rows'][0]['TD_ID']
                                tableDBName = result['rows'][0]['Table_Name']
                        else:
                            td_id = result['rows'][0]['TD_ID']
                            tableDBName = result['rows'][0]['Table_Name']
                else:
                    td_id = None
                    missed_events.append({'Event': event,
                                          'Reason': 'event_type key was not found in input dictionary'})
                    continue

            # Get Survey Set ID
            # -----------------
            if sameSurveySet and event_idx > 0:
                if ss_id == None:
                    continue
            else:
                if 'survey_set' in event.keys():
                    survey_set = event['survey_set']
                else:
                    survey_set = 'Raw Survey Data'

                if prev_survey_set != survey_set:
                    prev_survey_set = survey_set
                    x_filter = {"operator": "and",
                                "where": [{'field': 'Survey_Set.Name', 'value': survey_set}]
                                }
                    x_filter = json.dumps(x_filter)
                    result, result_code = self.getTable('Survey_Set', xFilter=x_filter, pageSize=pageSize, verbose=verbose)

                    if (len(result['rows']) == 0) or (result_code != 200):
                        ss_id = None
                        missed_events.append({'Event': event,
                                              'Reason': 'can not find survey set in the database'})
                        continue

                    ss_id = result['rows'][0]['SS_ID']

            # Check if start_clock and end_clock is in input dictionary
            # ---------------------------------------------------------
            if not ('start_clock' in event.keys()):
                missed_events.append({'Event': event,
                                      'Reason': 'start_clock key was not found in input dictionary'})
                continue

            if not ('end_clock' in event.keys()):
                missed_events.append({'Event': event,
                                      'Reason': 'end_clock key was not found in input dictionary'})
                continue

            # Check event fields type and create event body
            # ---------------------------------------------
            event_body = {}
            for eventFieldName in event['fields'].keys():
                x_filter = {'operator': 'and',
                            'where': [{'field': 'Field_Def.Name', 'value': eventFieldName}]
                            }
                x_filter = json.dumps(x_filter)
                result, result_code = self.getTable('Field_Def', xFilter=x_filter, pageSize=pageSize,
                                                    verbose=verbose)

                if len(result['rows']) == 0:
                    if 'comment' in event.keys():
                        event['comment'] += '\nCheck this field: ' + eventFieldName + ': ' + str(
                            event['fields'][eventFieldName]) + ' '
                    else:
                        event['comment'] = eventFieldName + ': ' + str(event['fields'][eventFieldName]) + ' '
                else:
                    dbFieldName = result['rows'][0]['Field_Name']

                    # Check if field is lookup list type
                    if 'LL_ID' in result['rows'][0].keys():
                        x_filter = {'operator': 'and',
                                    'where': [{'field': 'Lookup_Item.LL_ID', 'value': result['rows'][0]['LL_ID']},
                                              {'field': 'Lookup_Item.Comments',
                                               'value': event['fields'][eventFieldName]}]
                                    }
                        x_filter = json.dumps(x_filter)
                        result, result_code = self.getTable('Lookup_Item', xFilter=x_filter, pageSize=pageSize,
                                                            verbose=verbose)

                        if len(result['rows']) == 0:
                            if 'comment' in event.keys():
                                event['comment'] += '\nCheck this field: ' + eventFieldName + ': ' + str(
                                    event['fields'][eventFieldName]) + ' '
                            else:
                                event['comment'] = eventFieldName + ': ' + str(
                                    event['fields'][eventFieldName]) + ' '
                        else:
                            event_body[dbFieldName] = result['rows'][0]['LI_ID']
                    else:
                        event_body[dbFieldName] = event['fields'][eventFieldName]

            # Create new header record
            # ------------------------
            header_body = {'TD_ID': td_id,
                           'Start_Clock': event['start_clock'],
                           'End_Clock': event['end_clock'],
                           'Workpack_ID': workpack_id,
                           'Component_ID': component_id,
                           'SS_ID': ss_id}

            result, result_code = self.createNewRecord('Header', header_body, verbose=verbose)
            event_body['Header_ID'] = result['rows'][0]['Header_ID']

            # Create new event record
            # -----------------------
            result, result_code = self.createNewRecord(tableDBName, event_body, verbose=verbose)

            # Create new commentary record
            # ----------------------------
            if 'comment' in event.keys():
                commentary_body = {'Header_ID': event_body['Header_ID'],
                                   'Notes': event['comment']}
                result, result_code = self.createNewRecord('Commentary', commentary_body, verbose=verbose)

            imported_events.append(event)

            # Import associated multimedia
            # ----------------------------
            if 'multimedia' in event.keys():
                for multimedia in event['multimedia']:
                    result, result_code = self.importMultimedia(event_body['Header_ID'], multimedia['name'],
                                                                multimedia['filename'], multimedia['binary_data'],
                                                                verbose=verbose)

        print('Imported ' + str(len(imported_events)) + ' new events...')
        print('Missed ' + str(len(missed_events)) + ' events from input...')
        return imported_events, missed_events

    ######################################################################################
    def createNewAssets(self, assets, pageSize=None, verbose=False):
        """
        Imports new assets in the NEXUS IC database. This function will create the assets in the Component and View_Node tables.

        :param assets: (``list``) - Assets to be imported. Must follow the following format:

                .. code-block:: python

                        assets = [{'asset_full_location': 'xxxx / xxxx',
                                    'asset_type': 'xxxx',
                                    'asset_view': 'xxxx'}]

                where:

                - asset_full_location: Follows the same format as the standard NEXUS import sheet (single column)
                - asset_type: Asset type name as listed in the NEXUS database
                - asset_view: Asset view name. If provided asset view does not exist, then first entry in the Comp_View table will be used

        :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default NEXUS IC page size will be used (100).
        :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

        :return: (``tuple`` - list, list) - List of imported events and missed events.
        """

        imported_assets = []
        missed_assets = []

        for asset_idx, asset in enumerate(assets):
            parent_assets = asset['asset_full_location'].split(' / ')
            asset['name'] = parent_assets[len(parent_assets) - 1]

            # Check asset type and get asset type ID
            # --------------------------------------
            x_filter = {"operator": "and",
                        "where": [{'field': 'Name', 'value': asset['asset_type']}]
                        }
            x_filter = json.dumps(x_filter)
            result, result_code = self.getTable('Comp_Type', xFilter=x_filter, pageSize=pageSize,
                                                verbose=verbose)
            if len(result['rows']) == 0:
                asset['error'] = 'Asset type does not exist in the database'
                missed_assets.append(asset)
                continue
            else:
                asset['ct_id'] = result['rows'][0]['CT_ID']

            # Check asset view and get asset view ID
            # --------------------------------------
            x_filter = {"operator": "and",
                        "where": [{'field': 'Name', 'value': asset['asset_view']}]
                        }
            x_filter = json.dumps(x_filter)
            result, result_code = self.getTable('Comp_View', xFilter=x_filter, pageSize=pageSize,
                                                verbose=verbose)
            if len(result['rows']) == 0:
                result, result_code = self.getTable('Comp_View', pageSize=pageSize, verbose=verbose)
                asset['cv_id'] = result['rows'][0]['CV_ID']
                asset['asset_view'] = result['rows'][0]['Name']
            else:
                asset['cv_id'] = result['rows'][0]['CV_ID']

            # Check if asset exist using full location
            # ----------------------------------------
            x_filter = {"operator": "and",
                        "where": [{'field': 'Full_Location', 'value': asset['asset_full_location']},
                                  {'field': 'CV_ID', 'value': asset['cv_id']}]
                        }
            x_filter = json.dumps(x_filter)
            result, result_code = self.getTable('View_node', xFilter=x_filter, pageSize=pageSize,
                                                verbose=verbose)

            if len(result['rows']) > 0:
                asset['error'] = 'Asset full location exist in the database'
                missed_assets.append(asset)
                continue

            # Checking parent assets and creating missing assets
            # --------------------------------------------------
            child_asset_location = ''
            parent_asset_vn_id = None
            include_type = False
            for child_asset_idx, child_asset in enumerate(parent_assets):
                if child_asset_location == '':
                    child_asset_location = child_asset
                else:
                    child_asset_location += ' / ' + child_asset

                if child_asset_idx < len(parent_assets) - 1:
                    x_filter = {"operator": "and",
                                "where": [{'field': 'Full_Location', 'value': child_asset_location},
                                          {'field': 'CV_ID', 'value': asset['cv_id']}]
                                }
                    x_filter = json.dumps(x_filter)
                    result, result_code = self.getTable('View_Node', xFilter=x_filter, pageSize=pageSize,
                                                        verbose=verbose)
                    if len(result['rows']) > 0:  # Child asset exist
                        include_type = False
                        parent_asset_vn_id = result['rows'][0]['VN_ID']
                        continue
                else:
                    include_type = True

                # Insert child asset in component table
                # -------------------------------------
                component_body = {'Name': child_asset}

                if include_type:
                    component_body['CT_ID'] = asset['ct_id']
                    import_asset_type = asset['asset_type']
                else:
                    import_asset_type = None

                comp_result, comp_result_code = self.createNewRecord('Component', component_body, verbose=verbose)
                component_body['Component_ID'] = comp_result['rows'][0]['Component_ID']

                # Insert child asset in view node table
                # -------------------------------------
                vn_body = {'Component_ID': component_body['Component_ID'],
                           'CV_ID': asset['cv_id']}

                if parent_asset_vn_id != None:
                    vn_body['Link_ID'] = parent_asset_vn_id

                vn_result, vn_result_code = self.createNewRecord('View_Node', vn_body, verbose=verbose)
                parent_asset_vn_id = vn_result['rows'][0]['VN_ID']

                import_asset_info = {'Component ID': component_body['Component_ID'],
                                     'VN ID': parent_asset_vn_id,
                                     'Asset Full Location': child_asset,
                                     'Asset Type': import_asset_type,
                                     'Asset View': asset['asset_view']}
                imported_assets.append(import_asset_info)

        print('Imported ' + str(len(imported_assets)) + ' new assets...')
        print('Missed ' + str(len(missed_assets)) + ' assets from input...')
        return imported_assets, missed_assets

    ######################################################################################
    def importMultimedia(self, header_id, mm_name, filename, binary_data,
                         is_image=True, verbose=False):
        """
        Import multimedia and attach it to a specific event

        :param header_id: (``int``) - Event header ID where the multimedia will be linked to
        :param mm_name: (``string``) - Multimedia name displayed in NEXUS IC
        :param filename: (``string``) - Name of the file to be imported
        :param binary_data: (``byte``) - The actual file as a byte variable
        :param is_image: (``bool` - optional) - Define whether the file is an image or AVI file (default value True)
        :param verbose: (``bool`` - optional) - Print internal messages if True (default value False)

        :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code
        """

        # Import image in repository
        result, result_code = self.importRepository(filename, binary_data, verbose=verbose)

        # Update multimedia information
        mm_body = {}
        mm_body['Repository_ID'] = result['rows'][0]['Repository_ID']
        mm_body['Header_ID'] = header_id
        mm_body['Name'] = str(mm_name)
        mm_body['Can_Report'] = True

        # Add multimedia type
        if is_image:
            x_filter = {'operator': 'and',
                        'where': [{'field': 'Name', 'value': 'Image'}]}
        else:
            x_filter = {'operator': 'and',
                        'where': [{'field': 'Name', 'value': 'AVI'}]}

        x_filter = json.dumps(x_filter)
        result, result_code = self.getTable('MM_Type', xFilter=x_filter)
        mm_body['MMT_ID'] = result['rows'][0]['MMT_ID']

        # Create new record in Multimedia table
        result, result_code = self.createNewRecord('Multimedia', body=mm_body, verbose=verbose)
        return result, result_code

    ######################################################################################
    def importLibrary(self, library_type, l_name, filename, binary_data,
                      ref_date=None, document_no=None, revision=None, description=None, location=None, hyperlink=None,
                      show_grayscale=False, show_caption=True, show_dimensions=True, can_report=True, force_2d=False,
                      background_color=None, verbose=False):
        """
        Import library item

        :param library_type: (``string``) - Library type name
        :param l_name: (``string``) - Library item name
        :param filename: (``string``) - Name of the file to be imported
        :param binary_data: (``byte``) - The actual file as a byte variable
        :param ref_date: (``datetime`` - optional) - Library item reference date (default value None)
        :param document_no: (``string`` - optional) - Library item document number (default value None)
        :param revision: (``string`` - optional) - Library item revision (default value None)
        :param description: (``string`` - optional) - Library item description (default value None)
        :param location: (``string`` - optional) - Library item physical location path (default value None)
        :param hyperlink: (``string`` - optional) - Library item hyperlink (default value None)
        :param show_grayscale: (``bool`` - optional) - Show library as grayscale (default value False)
        :param show_caption: (``bool`` - optional) - Show library captions (default value True)
        :param show_dimensions: (``bool`` - optional) - Show library dimensions (default value True)
        :param can_report: (``bool`` - optional) - Show library in reports (default value True)
        :param force_2d: (``bool`` - optional) - Used only for Autocad files (default value False)
        :param background_color: (``int`` - optional) - Background color (default value None)
        :param verbose: (``bool`` - optional) - Print internal messages if True (default value False)

        :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code
        """

        # Import image in repository
        result, result_code = self.importRepository(filename, binary_data, verbose=verbose)

        # Update multimedia information
        l_body = {}
        l_body['Repository_ID'] = result['rows'][0]['Repository_ID']
        l_body['Name'] = l_name

        if ref_date != None:
            l_body['Ref_Date'] = ref_date

        if document_no != None:
            l_body['Document_No'] = document_no

        if revision != None:
            l_body['Revision'] = revision

        if description != None:
            l_body['Description'] = description

        if location != None:
            l_body['Location'] = location

        if hyperlink != None:
            l_body['Hyperlink'] = hyperlink

        if background_color != None:
            l_body['Background_Colour'] = background_color

        l_body['Show_GrayScale'] = show_grayscale
        l_body['Show_Captions'] = show_caption
        l_body['Show_Dimensions'] =  show_dimensions
        l_body['Can_Report'] = can_report
        l_body['Force_2D'] = force_2d

        # Add library type
        x_filter = {'operator': 'and',
                    'where': [{'field': 'Name', 'value': library_type}]}

        x_filter = json.dumps(x_filter)
        result, result_code = self.getTable('Library_Type', xFilter=x_filter)
        l_body['LT_ID'] = result['rows'][0]['LT_ID']

        # Create new record in Multimedia table
        result, result_code = self.createNewRecord('Library', body=l_body, verbose=verbose)
        return result, result_code

    ######################################################################################
    def get_rt_id(self, report_name):
        """
        Gets the RT_ID value from the Report_Template table using a report's Name.
        :param report_name: (``string``) - Name of the Report as it appears in NEXUS.
        :return: (``int``) - RT_ID value.
        """

        xFilter = '{"where": [{"field": "Name", "value": "' + report_name + '"}]}'
        report_json, report_status = self.getTable('Report_Template', xFilter=xFilter)

        if report_status == 404:
            return str(report_status) + ': ' + str(report_json)
        else:
            rt_id = report_json['rows'][0]['RT_ID']
            print("RT_ID="+str(rt_id))
            return rt_id

######################################################################################
################################### Start Script #####################################
if __name__ == '__main__':
    baseURI = ''
    apiKey = ''

    startTime = datetime.datetime.now()

    ## Program start here
    print(NEXUSIC_REST.__doc__)
    ## End of program

    endTime = datetime.datetime.now()
    elapsedTime = endTime - startTime

    print('NEXUS IC REST API actions completed.....runtime: %s' % (str(elapsedTime)))



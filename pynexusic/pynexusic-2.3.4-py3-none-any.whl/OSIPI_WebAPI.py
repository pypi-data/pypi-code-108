import requests
import json
from requests.auth import HTTPBasicAuth
#from requests_kerberos import HTTPKerberosAuth
from requests_ntlm import HttpNtlmAuth

############################# OSI PI Web API Class ############################
class OSIPI_WebAPI():
    """
    OSI PI Web API class allows the user to communicate with OSI PI web API using python

    Prerequisites:
    -------------
        - Python > 3.7
        - OSI PI access

    OSI PI Documentation:
    --------------------
        The OSI PI Web API documentation can be found in the bellow link:
        https://techsupport.osisoft.com/Documentation/PI-Web-API/help.html
    """

    def __init__(self, piwebapi_url, username, password, authentication_type='basic',
                 max_attempts=1, timeout=None,
                 verbose=False, verify=True):
        """

            :param piwebapi_url: (``string``) - OSI PI base URL.
            :param username: (``string``) - OSI PI username.
            :param password: (``string``) - OSI PI password.
            :param authentication_type: (``string`` - optional) - This can be either ntlm or basic (default value basic).
            :param max_attempts: (``int`` - optional) - Maximum number of attempts if disconnected (default value 1).
            :param timeout: (``int`` - optional) - Timeout threshold in seconds (default value None).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).
            :param verify: (``bool`` - optional) - By pass SSL verification if True (default value True).

            :returns: None
        """
        assert authentication_type.lower() in ['ntlm', 'basic'], 'Incorrect security method'
        self.piwebapi_url = piwebapi_url
        self.authentication_type = authentication_type
        self.username = username
        self.password = password
        self.max_attempts = max_attempts   # TODO: Functionality to be added
        self.timeout = timeout  # TODO: Functionality to be added
        self.verbose = verbose
        self.verify = verify

        self.authentication_type = self.authenticate(self.authentication_type, self.username, self.password)
        self.sys_links = self.get_system_links()

    ########################################################################################################
    def authenticate(self, authentication_type, username, password, verbose=False):
        """
            Authenticate and create API call security method

            :param authentication_type: (``string``) - Authentication method to use:  basic or ntlm.
            :param username: (``string``) - The user's credentials name.
            :param password: (``string``) - The user's credentials password.
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :returns: (``HttpNtlmAuth`` or ``HTTpBasicAuth``)
        """
        assert authentication_type.lower() in ['basic', 'ntlm'], authentication_type + ' authentication type not supported'

        if self.verbose or verbose:
            print('Authenticating with OSI PI...')

        if authentication_type.lower() == 'basic':
            security_auth = HTTPBasicAuth(username, password)
        elif authentication_type.lower() == 'ntlm':
            security_auth = HttpNtlmAuth(username, password)
        #else:
        #    security_auth = HTTPKerberosAuth(mutual_authentication='REQUIRED',
        #                                     sanitize_mutual_error_response=False)

        return security_auth

    ######################################################################################
    def validate_and_return_response(self, response, message='', raw=False):
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

    ########################################################################################################
    def webapi_get_request(self, url, pageSize=None, message='', raw=False):
        """
            Execute get request and validate response.

            :param url: (``string``) - URL to be executed in the get request.
            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default OSI PI page size will be used (1000).
            :param message: (``string`` - optional) - Desired custom error message.
            :param raw: (``bool`` - optional) - Defines whether to return response raw format or json (default value False).

            :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code.
        """

        if pageSize != None:
            url = url + '/?maxCount=' + str(pageSize)

        response = requests.get(url, auth=self.authentication_type, verify=self.verify)

        resp, resp_status = self.validate_and_return_response(response, message=message, raw=raw)

        return resp, resp_status

    ########################################################################################################
    def get_system_links(self, pageSize=None, verbose=False):
        """
            Get OSI PI DataServers and AssetServers available databases

            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default OSI PI page size will be used (1000).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``dict``) - System links dictionary

                .. code-block:: python

                    {'<serverType>': [{'Name': 'xxx', 'Link': 'xxx', 'WebID': 'xxx'}]}

                **<serverType>** is either DataServers or AssetServers
        """

        if self.verbose or verbose:
            print('Getting OSI PI system links...')

        result = {}
        links, links_status = self.webapi_get_request(self.piwebapi_url, pageSize=pageSize)
        for link in links['Links']:
            if link in ['DataServers', 'AssetServers']:
                response, resp_status = self.webapi_get_request(links['Links'][link], pageSize=pageSize)
                itemsList = []
                for item in response['Items']:
                    itemsList.append({'Name': item['Name'],
                                    'Link': links['Links'][link],
                                    'WebID': item['WebId']})
                result[link] = itemsList
        return result

    ########################################################################################################
    def getPointsList(self, dataServerName=None, pageSize=None, verbose=False):
        """
            Get full point list (sensors) in a specified data server. If data server is None, then all points from all data servers will be returned

            :param dataServerName: (``string`` - optional) - Specific data server to retrieve data from (default value None).
            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default OSI PI page size will be used (1000).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict, None) - List of all points (sensors). The second argument of the tuple is always None

                .. code-block:: python

                    ([{'ServerName': 'xxx', 'Points': 'xxx', 'ResponseStatus': 'xxx'}], None)
        """

        if self.verbose or verbose:
            print('Getting OSI PI points list...')

        result = []
        for dataServer in self.sys_links['DataServers']:
            if dataServerName != None:
                if dataServerName != dataServer['Name']:
                    continue

            points_url = dataServer['Link'] + r'/' + \
                         dataServer['WebID'] + r'/points'

            points_resp, points_resp_status = self.webapi_get_request(points_url, pageSize=pageSize)

            if points_resp_status == 200:
                points = points_resp['Items']
            else:
                points = points_resp

            result.append({'ServerName': dataServer['Name'],
                           'Points': points,
                           'ResponseStatus': points_resp_status})

        return result, None

    ########################################################################################################
    def getStreamData(self, webID, searchType='end', parameters=None, pageSize=None, verbose=False):
        """
            Get stream data for a specified point (sensor) using point's webID. Search filter can be applied to narrow down the result

            :param webID: (``string``) - Point (sensor) web ID.
            :param searchType: (``string`` - optional) - Search type to be used, can be one of the following values (default value ``end``).

                .. code-block:: python

                        ['end', 'interpolated', 'recorded', 'plot', 'summary', 'value']

            :param parameters: (``string`` - optional) - Additional parameters to filter the query (default value None).
                See https://techsupport.osisoft.com/Documentation/PI-Web-API/help/controllers/stream.html for additional information for each search type.
            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default OSI PI page size will be used (1000).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        assert searchType.lower() in ['end', 'interpolated', 'recorded',
                                      'plot', 'summary', 'value'], searchType + ' search type not supported'

        if self.verbose or verbose:
            print('Getting OSI PI stream data...')

        if parameters == None:
            url = self.piwebapi_url + r'/streams/' + str(webID) + r'/' + searchType.lower()
        else:
            url = self.piwebapi_url + r'/streams/' + str(webID) + r'/' + searchType.lower() + '?' + parameters

        resp, resp_status = self.webapi_get_request(url, pageSize=pageSize)
        return resp, resp_status

    ########################################################################################################
    def getStreamDataSummary(self, webID, startTime=None, endTime=None, summaryType=None,
                             pageSize=None, verbose=False):
        """
            Get stream data summary for a specified point (sensor) using point's webID. Search filter can be applied to narrow down the result.

            For more details see https://techsupport.osisoft.com/Documentation/PI-Web-API/help/controllers/stream/actions/getsummary.html

            :param webID: (``string``) - Point (sensor) web ID.
            :param startTime: (``string`` - optional) -Start time filter (default vale None)
            :param endTime: (``string`` - optional) -End time filter (default vale None)
            :param summaryType: (``string`` - optional) - Summary type requested, can be one of the following values (default value None).

                .. code-block:: python

                        ['Total', 'Average', 'Minimum', 'Maximum', 'Range',
                        'StdDev', 'PopulationStdDev', 'Count', 'PercentGood',
                        'TotalWithUOM', 'All', 'AllForNonNumeric']

            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default OSI PI page size will be used (1000).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        assert summaryType in ['Total', 'Average', 'Minimum', 'Maximum', 'Range',
                               'StdDev', 'PopulationStdDev', 'Count', 'PercentGood',
                               'TotalWithUOM', 'All', 'AllForNonNumeric'], summaryType + ' summary type not supported'
        parameters = None
        if startTime != None:
            parameters = 'startTime=' + str(startTime)

        if endTime != None:
            if parameters == None:
                parameters = 'endTime=' + str(endTime)
            else:
                parameters += '&endTime=' + str(endTime)

        if summaryType != None:
            if parameters == None:
                parameters = 'summaryType=' + str(summaryType)
            else:
                parameters += '&summaryType=' + str(summaryType)

        resp, resp_status = self.getStreamData(webID, searchType='summary', parameters=parameters,
                                               pageSize=pageSize, verbose=verbose)
        return resp, resp_status

    ########################################################################################################
    def getPointAttributes(self, webID, pageSize=None, verbose=False):
        """
            Get point (sensor) system attributes

            For more details see https://techsupport.osisoft.com/Documentation/PI-Web-API/help/controllers/point/actions/getattributes.html

            :param webID: (``string``) - Point (sensor) web ID.
            :param pageSize: (``int`` - optional) - Page size for response (default value None). When default is used the default OSI PI page size will be used (1000).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Getting OSI PI point attributes...')

        url = self.piwebapi_url + r'/points/' + str(webID) + r'/attributes'
        resp, resp_status = self.webapi_get_request(url, pageSize=pageSize)
        return resp, resp_status

############################################################################################################
############################################################################################################
if __name__ == '__main__':
    pass
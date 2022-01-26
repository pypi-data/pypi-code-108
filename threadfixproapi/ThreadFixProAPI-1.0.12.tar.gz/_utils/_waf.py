#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Evan Schlesinger"
__copyright__ = "(C) 2019 Denim group"
__contributors__ = ["Evan Schlesinger"]
__status__ = "Production"
__license__ = "MIT"

import requests
import urllib3
import requests.exceptions
import requests.packages.urllib3

from ._utilities import ThreadFixProResponse

class WafsAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro WAFs API instance.
        :param host: The URL for the ThreadFix Pro server. (e.g., http://localhost:8080/threadfix/) NOTE: must include http:// TODO: make it so that it is required or implicitly added if forgotten
        :param api_key: The API key generated on the ThreadFix Pro API Key page.
        :param verify_ssl: Specify if API requests will verify the host's SSL certificate, defaults to true.
        :param timeout: HTTP timeout in seconds, default is 30.
        :param user_agent: HTTP user agent string, default is "threadfix_pro_api/[version]".
        :param cert: You can also specify a local cert to use as client side certificate, as a single file (containing
        the private key and the certificate) or as a tuple of both file’s path
        :param debug: Prints requests and responses, useful for debugging.
        """

        self.host = host
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        if not user_agent:
            self.user_agent = 'threadfix_pro_api/2.7.5' 
        else:
            self.user_agent = user_agent

        self.cert = cert
        self.debug = debug  # Prints request and response information.

        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Disabling SSL warning messages if verification is disabled.

    def create_waf(self, name, WAFtype):
        """
        Creates a WAF with the given name and type
        :param name: Name for the WAF
        :param WAFtype: Type of WAF you are creating
        """
        params = {'name' : name, 'type' : WAFtype}
        return self._request('POST', 'rest/wafs/new', params)

    def get_waf_by_id(self, waf_id):
        """
        Gets a WAF by the WAFId
        :param waf_id: WAF identifier
        """
        return self._request('GET', 'rest/wafs/' + str(waf_id))

    def get_waf_by_name(self, waf_name):
        """
        Gets a WAF by its name
        :param waf_name: The name of the WAF being gotten
        """
        return self._request('GET', 'rest/wafs/lookup?name=' + str(waf_name))

    def get_all_wafs(self):
        """
        Gets all WAFs in the system
        """
        return self._request('GET', 'rest/wafs')

    def get_waf_rules(self, waf_id, app_id):
        """
        Returns the WAF rule text for one or all applications a WAF is attached to. If the appId is -1, it will get rules for all apps. 
        If the appId is a valid application ID, rules will be generated for that application.'
        :param waf_id: WAF identifier
        :param app_id: Application identifier
        """
        return self._request('GET', 'rest/wafs/' + str(waf_id) + '/rules/app/' + str(app_id))

    def upload_waf_log(self, waf_id, file_path):
        """
        Uploads WAF log
        :param waf_id: WAF identifier
        :param file_path: Path to file to be uploaded
        """
        files = {'file' : open(file_path, 'rb')}
        return self._request('POST', 'rest/wafs/' + str(waf_id) + '/uploadLog', files=files)

    # Utility

    def _request(self, method, url, params=None, files=None):
        """Common handler for all HTTP requests."""
        if not params:
            params = {}

        headers = {
            'Accept': 'application/json',
            'Authorization': 'APIKEY ' + self.api_key
        }

        try:
            if self.debug:
                print(method + ' ' + self.host + url)
                print(params)

            response = requests.request(method=method, url=self.host + url, params=params, files=files, headers=headers,
                                        timeout=self.timeout, verify=self.verify_ssl, cert=self.cert)

            if self.debug:
                print(response.status_code)
                print(response.text)

            try:
                json_response = response.json()

                message = json_response['message']
                success = json_response['success']
                response_code = json_response['responseCode']
                data = json_response['object']

                return ThreadFixProResponse(message=message, success=success, response_code=response_code, data=data)
            except ValueError:
                return ThreadFixProResponse(message='JSON response could not be decoded.', success=False)
        except requests.exceptions.SSLError:
            return ThreadFixProResponse(message='An SSL error occurred.', success=False)
        except requests.exceptions.ConnectionError:
            return ThreadFixProResponse(message='A connection error occurred.', success=False)
        except requests.exceptions.Timeout:
            return ThreadFixProResponse(message='The request timed out after ' + str(self.timeout) + ' seconds.',
                                     success=False)
        except requests.exceptions.RequestException:
            return ThreadFixProResponse(message='There was an error while handling the request.', success=False)
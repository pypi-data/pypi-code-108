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

class PoliciesAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro Policies API instance.
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

    def get_policy(self, policy_id):
        """
        Get details for a policy
        :param policy_id: Policy identifier
        """
        return self._request('GET', 'rest/policies/' + str(policy_id))

    def get_all_policies(self):
        """
        Get a list of all policies in ThreadFix
        """
        return self._request('GET', 'rest/policies')

    def get_application_policy_status(self, application_id):
        """
        Get the status for all policies attached to the application with the provided appId
        :param application_id: Application identifier
        """
        return self._request('GET', 'rest/applications/' + str(application_id) + '/policyStatuses')

    def add_application_to_policy(self, policy_id, application_id):
        """
        Adds an application to a policy
        :param policy_id: Policy identifier
        :param application_id: Application identifier
        """
        return self._request('POST', 'rest/policies/' + str(policy_id) + '/application/' + str(application_id))

    def ad_hoc_policy_evaluation(self, application_id, policy_id):
        """
        Gets the status of a policy even if the policy is not attached to the application
        :param application_id: Application identifier
        :param policy_id: Policy identifier
        """
        return self._request('GET', 'rest/applications/' + str(application_id) + '/policy/eval?policyId=' + str(policy_id))

    def retrieve_all_policies(self, team_id):
        """
        Get details for all policies attached to a team
        :param team_id: Team identifier
        """
        return self._request('GET', 'rest/policies/team/' + str(team_id))

    def add_policy_to_team(self, policy_id, team_id):
        """
        Adds a policy to a team and any application associated with that team
        :param policy_id: Policy identifier
        :param team_id: Team identifier
        """
        return self._request('POST', 'rest/policies/' + str(policy_id) + '/team/' + str(team_id))

    def remove_policy_to_team(self, policy_id, team_id):
        """
        Removes a policy to a team and any application associated with that team
        :param policy_id: Policy identifier
        :param team_id: Team identifier
        """
        return self._request('DELETE', 'rest/policies/' + str(policy_id) + '/team/' + str(team_id) + '/remove')

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
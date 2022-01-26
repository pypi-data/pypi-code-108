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

class TeamsAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro Teams API instance.
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

    def create_team(self, name):
        """
        Creates a new team
        :param name: The name of the new team being created
        """
        params = {"name": name}
        return self._request('POST', 'rest/teams/new', params, debug=self.debug)

    def get_team_by_id(self, team_id):
        """
        Retrieves team with id of team_id'
        :param team_id: ID of the team being gotten
        """
        return self._request('GET', 'rest/teams/' + str(team_id))

    def get_team_by_name(self, team_name):
        """
        Retrieves team with name of team_name
        :param team_name: Name of the team being gotten
        """
        return self._request('GET', 'rest/teams/lookup?name=' + str(team_name))

    def get_all_teams(self):
        """
        Retrieves all the teams.
        """
        return self._request('GET', 'rest/teams')

    def update_team(self, team_id, name):
        """
        Updates team with teamId
        :param team_id: Team identifier
        :param name: New name to assign to the team
        """
        params = {'name' : name}
        return self._request('PUT', 'rest/teams/' + str(team_id) + '/update', params)

    def get_team_event_history(self, team_id, pages=None, page_size=None):
        """
        Lists event history for a team
        :param team_id: Team identifier
        :param pages: Number of events to return. By default this method will return up to 10 events
        :param page_size: Can be used to return a different page of events, with each page of events containing page_size events
        """
        params = {}
        if pages:
            params['page'] = pages
        if page_size:
            params['pageSize'] = page_size
        return self._request('POST', 'rest/events/organization/' + str(team_id), params)

    def delete_team(self, team_id):
        """
        Deletes a team by the provided teamId
        :param team_id: Team identifier
        """
        return self._request('DELETE', 'rest/teams/' + str(team_id) + '/delete')
    
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

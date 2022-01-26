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

class RemoteProvidersAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro Remote Providers API instance.
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

    def add_remote_provider_application_mapping(self, remote_provider_application_id, application_id, report_url=None):
        """
        Maps a ThreadFix application to the Remote Provider application
        :param remote_provider_application_id: Remote Provider Application identifier
        :param application_id: Application identifier
        :param report_url: The version URL to use for Black Duck remote provider application
        """
        params = {'applicationId' : application_id}
        if report_url:
            params['reportUrl'] = report_url
        return self._request('POST', 'rest/remoteprovider/remoteProviderApplication/' + str(remote_provider_application_id) + '/addMapping', params)

    def check_remote_provider_application_import_status(self, remote_provider_application_id):
        """
        Returns the status for the Remote Provider Application import
        :param remote_provider_application_id: Remote Provider Application identifier
        """
        return self._request('GET', 'rest/remoteprovider/remoteProviderApplication/' + str(remote_provider_application_id) + '/status')

    def get_remote_provider_application_versions(self, remote_provider_application_id):
        """
        Returns the status for the Remote Provider Application import
        :param remote_provider_application_id: Remote Provider Application identifier
        """
        return self._request('GET', 'rest/remoteprovider/remoteProviderApplication/' + str(remote_provider_application_id) + '/versions')

    def get_remote_provider_applications(self, team_id=None, remote_provider_id=None, application_id=None, hide_mapped=None, hide_unmapped=None):
        """
        Returns a list of Remote Provider applications as well as the applications they are mapped to
        :param team_id: Team identifier. Returns only results mapped to that team
        :param remote_provider_id: Remote Provider identifier. Return only results that belong to the specified Remote Provider
        :param application_id: Application identifier. Return only results that belong to the specified application
        :param hide_mapped: Does not return results that are already mapped to ThreadFix applications
        :param hide_unmapped: Does not return results that lack a ThreadFix application mapping
        """
        params = {}
        if team_id:
            params['teamId'] = team_id
        if remote_provider_id:
            params['remoteProviderId'] = remote_provider_id
        if application_id:
            params['applicationId'] = application_id
        if hide_mapped:
            params['hideMapped'] = hide_mapped
        if hide_unmapped:
            params['hideUnmapped'] = hide_unmapped
        return self._request('GET', 'rest/remoteprovider/remoteProviderApplication/list', params)

    def get_remote_provider_applications_by_name(self, name, remote_provider_id):
        """
        Gets list of Remote Provider Applications with the provided name
        :param name: Name of the Remote Provider Applications to return
        :param remote_provider_id: ID of a Remote Provider to restrict the search to
        """
        params = {'name' : name}
        if remote_provider_id:
            params['remoteProviderId'] = remote_provider_id
        return self._request('GET', 'rest/remoteprovider/remoteProviderApplication/search', params)

    def get_remote_providers(self):
        """
        Returns a list of Remote Providers
        """
        return self._request('GET', 'rest/remoteprovider/list')

    def import_remote_provider_scans(self, remote_provider_application_id):
        """
        Triggers a Remote Provider import for the specified Remote Provider Application
        :param remote_provider_application_id: Remote Provider Application identifier
        """
        return self._request('POST', 'rest/remoteprovider/remoteProviderApplication/' + str(remote_provider_application_id) + '/import')

    def import_remote_provider_all(self, remote_provider_id):
        """
        Triggers a Remote Provider import for all applications from the specified Remote Provide
        :param remote_provider_id: Remote Provider identifier
        """
        return self._request('POST', 'rest/remoteprovider/' + str(remote_provider_id) + '/import')

    #Queue Remote Provider Scan has been left out - https://denimgroup.atlassian.net/wiki/spaces/TDOC/pages/22914237/Queue+Remote+Provider+Scan+-+API

    def remove_remote_provider_application_mapping(self, remote_provider_application_id):
        """
        Removes the ThreadFix application mapping for a Remote Provider application
        :param remote_provider_application_id: Remote Provider Application identifier
        """
        return self._request('DELETE', 'rest/remoteprovider/remoteProviderApplication/' + str(remote_provider_application_id) + '/removeMapping')

    def sync_remote_provider_applications(self, remote_provider_id):
        """
        Syncs ThreadFix Remote Provider Applications for the specified Remote Provider adding new ones and removing any that are no longer present in the Remote Provide
        :param remote_provider_id: Remote Provider identifier
        """
        return self._request('POST', 'rest/remoteprovider/' + str(remote_provider_id) + '/sync')

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
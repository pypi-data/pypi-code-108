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

class TagsAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro Tags API instance.
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

    def create_tag(self, name, tag_type="APPLICATION"):
        """
        Creats a new tag with the given name
        :param name: Name to assign the new tag. 60 character limit
        :param tag_type: The type of tag to create
        """
        params = {'name' : name, 'tagType' : tag_type}
        return self._request('POST', 'rest/tags/new', params)

    def get_tag_by_id(self, tag_id):
        """
        Gets tag by the given tagId
        :param tag_id: Tag identifier
        """
        return self._request('GET', 'rest/tags/' + str(tag_id))

    def get_tag_by_name(self, tag_name):
        """
        Gets tag by the given name
        :param tag_name: The name of a tag to be gotten
        """
        return self._request('GET', 'rest/tags/lookup?name=' + str(tag_name))

    def get_tags_by_vulnerability(self, vuln_id):
        """
        Gets tags attached to a given vulnerability
        :param vuln_id: The identifier of the vulnerability to get the tags from
        """
        return self._request('GET', 'rest/tags/vulnerabilities' + str(vuln_id))

    def get_all_tags(self):
        """
        Returns a list of all tags and returns their JSON
        """
        return self._request('GET', 'rest/tags/index')

    def list_tags(self):
        """
        Retrieves a list of only tag names, ids, and types.
        """
        return self._request('GET', 'rest/tags/list')

    def update_tag(self, tag_id, name):
        """
        Updates the name of the tag with the given tagId
        :param tag_id: Tag identifier
        :param name: New name to assign the tag
        """
        params = {'name' : name}
        return self._request('POST', 'rest/tags/' + str(tag_id) + '/update', params)

    def add_tag_to_application(self, application_id, tag_id):
        """
        Attaches the tag with the given tagId to the app with the given appId
        :param application_id: Application identifier
        :param tag_id: Tag identifier
        """
        return self._request('POST', 'rest/applications/' + str(application_id) + '/tags/add/' + str(tag_id))

    def remove_tag_to_application(self, application_id, tag_id):
        """
        Removes the tag with the given tagId to the app with the given appId
        :param application_id: Application identifier
        :param tag_id: Tag identifier
        """
        return self._request('POST', 'rest/applications/' + str(application_id) + '/tags/remove/' + str(tag_id))

    def delete_tag(self, tag_id):
        """
        Deletes the tag with the given tagId
        :params tag_id: Tag identifier
        """
        return self._request('POST', 'rest/tags/' + str(tag_id) + '/delete')

    def list_applications_for_tag(self, tag_id):
        """
        Returns the JSON of the apps that have the tag with the given tagId
        :params tag_id: Tag identifier
        """
        return self._request('GET', 'rest/tags/' + str(tag_id) + '/listApplications')

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
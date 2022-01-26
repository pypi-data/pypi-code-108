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

class MiscellaneousAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro Miscellaneous API instance.
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

    def clear_global_fpr_filter_set_override(self):
        """
        Clears the Global FPR Filter Set Override.  The file is still available in the Scan Upload Location if you want to reuse it later.
        """
        return self._request('DELETE', 'rest/defaults/fprfilterset')

    def configure_email_settings(self, host, port, sender, user, password, tls, smtp_authorization, filters=None):
        """
        Sets values for the Email configuration fields
        :param host: Email server hostname
        :param port: Port for email server
        :param sender: Email address Thread Fix emails will be sent from
        :param user: User account to validate email server authorization
        :param password: Password for user account
        :param tls: Set to true to enable tls
        :param smtp_authorization: Set to true to enable SMTP authorization
        :param filters: Comma separated email filters, supports * wildcard. Non matching email addresses will be rejected at sending time for security reasons.
        """
        params = {'host' : host, 'port' : port, 'sender' : sender, 'user' : user, 'password' : password, 'tls' : tls, 'smtpAuthorization' : smtp_authorization}
        if filters:
            params['filter'] = filters
        return self._request('PUT', 'rest/systemsettings/email', params)

    def configure_ldap_settings(self, url, search_base, user_dn, password, name, login_filter=None, users_filter=None, groups_filter=None, users_groups_filter=None):
        """
        Sets the values for the LDAP configuration fields
        :param url: URL for LDAP server
        :param search_base: The point from which ThreadFix will search for LDAP users from
        :param user_dn: User domain name to use for LDAP queries
        :param password: Password for user domain name
        :param name: Name for LDAP server
        :param login_filter: Override filter to get the account of the person logging in
        :param users_filter: Override filter to get the list of users in the directory
        :param groups_filter: Override filter to get the list of groups in the directory
        :param users_groups_filter: Override filter to get the list of groups for a user
        """
        params = {'url' : url, 'searchBase' : search_base, 'userDn' : user_dn, 'password' : password, 'name' : name}
        if login_filter:
            params['loginFilter'] = login_filter
        if users_filter:
            params['usersFilter'] = users_filter
        if groups_filter:
            params['groupsFilter'] = groups_filter
        if users_groups_filter:
            params['usersGroupsFilter'] = users_groups_filter
        return self._request('PUT', 'rest/systemsettings/ldap', params)

    def get_email_confirmation_details(self):
        """
        Returns email configuration fields. Password will always be null
        """
        return self._request('GET', 'rest/systemsettings/email')

    def get_ldap_confirmation_details(self):
        """
        Returns LDAP configuration fields. Password will always be null
        """
        return self._request('GET', 'rest/systemsettings/ldap')

    def set_custom_cwe_text(self, cwe_id, custom_text):
        """
        Sets Custom CWE Text for the provided CWE
        :param cwe_id: CWE identifier
        :param custom_text: The custom text to display in filed defects
        """
        params = {'customText' : custom_text}
        return self._request('POST', 'rest/cwe/' + str(cwe_id) + '/setCustomText', params)

    def upload_global_fpr_filter_set_override(self, file_path):
        """
        Uploads a file to the Scan Upload Location, to be used as an override Filter Set for all Fortify Scans
        :param file_path: Path to scan to upload
        """
        files = {'file' : open(file_path)}
        return self._request('POST', 'rest/defaults/fprfilterset', files=files)

    def create_metadata_key(self, key, keytype, active=True):
        """
        Creates a new metadata key
        :param key: Name of metadata key
        :param keytype: Type of metadata key
        :param active: Whether or not the new key is immediately enabled
        """
        params = {'key' : key, 'type' : keytype, 'active' : active}
        return self._request('POST', 'rest/metadataKeys/new', params)

    def create_metadata_key(self, metadata_key_id, key=None, active=None):
        """
        Edits a new metadata key
        :param metadata_key_id: Metadat Key identifier
        :param key: Name of metadata key
        :param active: Whether or not the new key is immediately enabled
        """
        params = {}
        if key:
            params['key'] = key
        if active:
            params['active'] = active
        return self._request('POST', 'rest/metadataKeys/' + str(metadata_key_id) + '/update', params)

    def get_metadata_keys(self, keytype=None):
        """
        Returns all metadata keys
        :param keytype: Type of Metadata key to return
        """
        if keytype:
            return self._request('GET', 'rest/metadataKeys?type=' + str(keytype))
        else:
            return self._request('GET', 'rest/metadataKeys')

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

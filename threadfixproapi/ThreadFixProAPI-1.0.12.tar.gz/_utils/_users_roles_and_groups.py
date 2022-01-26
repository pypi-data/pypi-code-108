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

class UsersRolesAndGroupsAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro Users Roles and Groups API instance.
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

    def add_application_role_to_group(self, group_id, app_id, role_id):
        """
        Gives the group permissions in the provided role for the specified application
        :param group_id: Group identifier
        :param app_id: Application identifier
        :param role_id: Role identifier
        """
        params = {'appId' : app_id, 'roleId' : role_id}
        return self._request('POST', 'rest/groups/' + str(group_id) + '/role/app', params)

    def add_application_role_to_user(self, user_id, app_id, role_id):
        """
        Gives the user permissions in the provided role for the specified application
        :param user_id: User identifier
        :param app_id: Application identifier
        :param role_id: Role identifier
        """
        params = {'appId' : app_id, 'roleId' : role_id}
        return self._request('POST', 'rest/users/' + str(user_id) + '/role/app', params)

    def add_team_role_to_group(self, group_id, team_id, role_id):
        """
        Gives the group permissions in the provided role for the specified team and all its application
        :param group_id: Group identifier
        :param team_id: Team identifier
        :param role_id: Role identifier
        """
        params = {'teamId' : app_id, 'roleId' : role_id}
        return self._request('POST', 'rest/groups/' + str(group_id) + '/role/team', params)

    def add_team_role_to_user(self, user_id, team_id, role_id):
        """
        Gives the group permissions in the provided role for the specified team and all its application
        :param user_id: User identifier
        :param team_id: Team identifier
        :param role_id: Role identifier
        """
        params = {'teamId' : app_id, 'roleId' : role_id}
        return self._request('POST', 'rest/users/' + str(user_id) + '/role/team', params)

    def get_groups(self):
        """
        Returns a list of groups
        """
        return self._request('GET', 'rest/groups/list')

    def get_roles(self):
        """
        Returns a list of roles
        """
        return self._request('GET', 'rest/roles/list')

    def get_users(self):
        """
        Returns a list of users
        """
        return self._request('GET', 'rest/users/list')

    def edit_user(self, user_id, name=None, display_name=None, user_type=None, active_directory_id=None, password=None, confirm_password=None, global_role_id=None):
        """
        Updates user information
        :param user_id: User identifier
        :param name: New name for user
        :param display_name: New display name for user
        :param user_type: Updates a LOCAL user to LDAP/SAML, an LDAP user to LOCAL/SAML, or a SAML user to LOCAL/LDAP. Possible values are LOCAL, LDAP, and SAML
        :param active_directory_id: Updates a non-LDAP user to LDAP user with 'type' and 'activeDirectoryId' parameters. Required when 'type' is in the request body and its value is 'LDAP'
        :param password: New password for the existing user
        :param confirm_password: Must match password if supplied
        :param global_role_id: New global role for user
        """
        params = {}
        if name:
            params['name'] = name
        if display_name:
            params['displayName'] = display_name
        if user_type:
            params['type']  = user_type
        if active_directory_id:
            params['activeDirectoryId'] = active_directory_id
        if password:
            params['password'] = password
        if confirm_password:
            params['confirmPassword'] = confirm_password
        if global_role_id:
            params['globalRoleId'] = global_role_id
        return self._request('POST', 'rest/users/' + str(user_id) + '/update', params)

    def remove_application_role_from_group(self, group_id, app_id):
        """
        Removes the group permissions for the specified application
        :param group_id: Group identifier
        :param app_id: Application identifier
        """
        params = {'appId' : app_id}
        return self._request('POST', 'rest/groups/' + str(group_id) + '/role/app/delete', params)

    def remove_application_role_from_user(self, user_id, app_id):
        """
        Removes the user permissions for the specified application
        :param user_id: User identifier
        :param app_id: Application identifier
        """
        params = {'appId' : app_id}
        return self._request('POST', 'rest/users/' + str(user_id) + '/role/app/delete', params)

    def remove_team_role_from_group(self, group_id, team_id):
        """
        Removes the group permissions for the specified team
        :param group_id: Group identifier
        :param team_id: Team identifier
        """
        params = {'teamId' : team_id}
        return self._request('POST', 'rest/groups/' + str(group_id) + '/role/team/delete', params)

    def remove_team_role_from_user(self, user_id, team_id):
        """
        Removes the user permissions for the specified team
        :param user_id: User identifier
        :param team_id: Team identifier
        """
        params = {'teamId' : team_id}
        return self._request('POST', 'rest/users/' + str(user_id) + '/role/team/delete', params)

    def create_user(self, name, user_type, display_name=None, active_directory_id=None, password=None, confirm_password=None, global_role_id=None):
        """
        Updates user information
        :param name: Name for user
        :parm user_type: "Local" if adding a local user; "LDAP" if adding an LDAP user.
        :param display_name: Display name for user
        :param active_directory_id: Required when 'type' value is "LDAP".
        :param password: Password for the existing user
        :param confirm_password: Must match password if supplied
        :param global_role_id: Global role for user
        """
        params = {'name' : name, 'type' : user_type}
        if display_name:
            params['displayName'] = display_name
        if active_directory_id:
            params['activeDirectoryId'] = active_directory_id
        if password:
            params['password'] = password
        if confirm_password:
            params['confirmPassword'] = confirm_password
        if global_role_id:
            params['globalRoleId'] = global_role_id
        return self._request('POST', 'rest/users/new', params)

    def delete_user(self, user_id):
        """
        Deletes user from the system
        :param user_id: User identifier
        """
        return self._request('DELETE', 'rest/users/' + str(user_id) + '/delete')

    def create_group(self, name, active_directory_id=None, global_role_id=None):
        """
        Adds a group to the system
        :param name: Name of group being added
        :param active_directory_id: Required when adding an LDAP group
        :param global_role_id: Adds the group's global role
        """
        params = {'name' : name}
        if active_directory_id:
            params['activeDirectoryId'] = active_directory_id
        if global_role_id:
            params['globalRoleId'] = global_role_id
        return self._request('POST', 'rest/groups/new' , params)

    def edit_group(self, group_id, name, global_role_id=None):
        """
        Updates the specified group in the system
        :param group_id: Group identifier
        :param name: Updates name of group
        :param global_role_id: Adds or changes the group's global role
        """
        params = {'name' : name}
        if global_role_id:
            params['globalRoleId'] = global_role_id
        return self._request('POST', 'rest/groups/' + str(group_id) + '/update' , params)

    def delete_group(self, group_id):
        """
        Deletes the specified group from the system
        :param group_id: Group identifier
        """
        return self._request('DELETE', 'rest/groups/' + str(group_id) + '/delete')

    def import_ldap_users(self, active_directory_id, import_ldap_groups=None):
        """
        Adds LDAP users to system
        :param active_directory_id: Active directory from which to import
        :param import_ldap_groups: Enable to import groups from the active directory
        """
        params = {'activeDirectoryId' : active_directory_id}
        if import_ldap_groups:
            params['importLdapGroups'] = import_ldap_groups
        return self._request('POST', 'rest/users/importLdapUsers', params)

    def prune_ldap_users(self, active_directory_id):
        """
        Removes pruned LDAP users from the system
        :param active_directory_id: Active directory from which users are removed
        """
        params = {'activeDirectoryId' : active_directory_id}
        return self._request('POST', 'rest/users/pruneLdapUsers', params)

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
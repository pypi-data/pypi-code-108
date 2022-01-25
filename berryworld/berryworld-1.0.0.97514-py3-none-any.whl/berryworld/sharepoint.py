import requests
import json
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient
import msal
import urllib
import os
import traceback
from urllib.parse import unquote


class Sharepoint:
    """Class to connect to sharepoint
    """
    def __init__(self, sharepoint_creds):
        """ Initialize the class
                -----------------------------
                sharepoint_creds = {
                    'client_id': '',
                    'scopes': '',
                    'organisation_id': '',
                    'username': '',
                    'password': '',
                    'site_id': '',
                    'api_version': ''
                    }

                sharepoint = Sharepoint(Sharepoint)
                -----------------------------
        :param sharepoint_creds: Dictionary containing the info to authorize the app registration for sharepoint access
            client_id - is the exposed api id associated with the app registration
            site_id - is the id of the specific sharepoint site the user account is trying to connect to
        """
        self.client_id = sharepoint_creds['client_id']
        self.scopes = sharepoint_creds['scopes']
        self.organisation_id = sharepoint_creds['organisation_id']
        self.username = sharepoint_creds['username']
        self.password = sharepoint_creds['password']
        self.site_id = sharepoint_creds['site_id']
        self.api_version = sharepoint_creds['api_version']

        self.base_url = f'https://login.microsoftonline.com/{self.organisation_id}'
        self.auth_url = f'{self.base_url}/oauth2/v2.0/authorize'
        self.graph_url = f'https://graph.microsoft.com/{self.api_version}'
        try:
            oauth = OAuth2Session(client=MobileApplicationClient(self.client_id), scope=self.scopes)
            authorization_url, state = oauth.authorization_url(self.auth_url)
            authorization_link = oauth.get(authorization_url)

            requests.get(authorization_link.url)

        except Exception:
            raise Exception

    def bearer_token(self):
        try:
            pca = msal.PublicClientApplication(self.client_id, authority=self.base_url)
            token = pca.acquire_token_by_username_password(self.username, self.password, self.scopes)
            bearer_token = token['access_token']

            headers = {'Authorization': 'Bearer {}'.format(token['access_token'])}
        except ValueError:
            print(traceback.format_exc())

        return bearer_token, headers

    def list_sites(self, headers, site_name=None):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param site_name: Sharepoint site name, otherwise default will list all available sites
        """
        if site_name is None:
            site_name = '*'
        else:
            site_name = urllib.parse.quote(site_name)
        site_url = f'{self.graph_url}/sites?search={site_name}'

        site_values = []
        try:
            result = requests.get(site_url, headers=headers)
            site_values = result.json()['value']
        except ValueError:
            print(traceback.format_exc())

        return site_values

    def list_drives(self, headers, site_id):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param site_id: Sharepoint site id, retrieve id from the list_sites result
        """
        drive_url = f'{self.graph_url}/sites/{site_id}/drives'

        drive_ids = []
        try:
            result = requests.get(drive_url, headers=headers)
            drive_ids = result.json()['value']
        except ValueError:
            print(traceback.format_exc())

        return drive_ids

    def get_drive_content(self, headers, site_id, drive_name):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param site_id: Sharepoint site id, retrieve id from the list_sites result
           :param drive_name: Specific filter on available drives within the site based on name
        """
        drive_url = f'{self.graph_url}/sites/{site_id}/drives'

        drive_content = []
        try:
            result = requests.get(drive_url, headers=headers)
            drive_values = result.json()['value']

            drive_content = list(filter(lambda d: d['name'] == drive_name, drive_values))
            if len(drive_content) == 0:
                drive_content = list(filter(lambda d: d['name'] in drive_name, drive_values))
        except ValueError:
            print(traceback.format_exc())

        return drive_content

    def get_folder_id(self, headers, drive_id, folder_path=None):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param drive_id: Specific sharepoint drive id (base site directory), retrieve id from the list_drives result
           :param folder_path: Specific Sharepoint folder path, default to root if not provided
        """
        # Get Item ID/Folder ID
        if folder_path is None:
            request_url = f'{self.graph_url}/drives/{drive_id}/root'
        else:
            folder_path = urllib.parse.quote(folder_path)
            request_url = f'{self.graph_url}/drives/{drive_id}/root:/{folder_path}'

        folder_id = ''
        try:
            result = requests.get(request_url, headers=headers)
            folder_info = result.json()
            folder_id = folder_info['id']
        except ValueError:
            print(traceback.format_exc())

        return folder_id

    def list_files(self, headers, drive_id, folder_id):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param drive_id: Specific sharepoint drive id (base site directory), retrieve id from the list_drives result
           :param folder_id: Id of the folder, retrieve id from the get_folder_id result. Lists all files within it
        """
        files = []
        try:
            result = requests.get(f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/children',
                                  headers=headers)
            items = result.json()['value']
            for f in items:
                if 'file' in f:
                    files.append(f)
        except ValueError:
            print(traceback.format_exc())

        return files

    def list_folders(self, headers, drive_id, folder_id):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param drive_id: Specific sharepoint drive id (base site directory), retrieve id from the list_drives result
           :param folder_id: Id of the folder, retrieve id from the get_folder_id result. Lists all folders within it
        """
        folders = []
        try:
            result = requests.get(f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/children',
                                  headers=headers)
            items = result.json()['value']
            for f in items:
                if 'folder' in f:
                    folders.append(f)
        except ValueError:
            print(traceback.format_exc())

        return folders

    def get_file_content(self, headers, drive_id, file_id):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param drive_id: Specific sharepoint drive id (base site directory), retrieve id from the list_drives result
           :param file_id: Id of the file, retrieve id from the list_files result
        """
        file_content = ''
        try:
            result = requests.get(f'{self.graph_url}/drives/{drive_id}/items/{file_id}/content',
                                  headers=headers)

            file_content = result.content
        except ValueError:
            print(traceback.format_exc())

        return file_content

    def create_folder(self, headers, drive_id, folder_id, folder_path):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param drive_id: Specific sharepoint drive id (base site directory), retrieve id from the list_drives result
           :param folder_id: Id of the folder where you'd like to create the new folder within
           :param folder_path: Specific Sharepoint folder path
        """
        if folder_path is None:
            folder_path = 'General'
        else:
            folder_path = urllib.parse.quote(folder_path)

        if '/' in folder_path:
            folder_name = folder_path[folder_path.rindex('/') + 1:]
        else:
            folder_name = folder_path

        folder_name = unquote(folder_name)
        folder_content = ''
        try:
            result = requests.get(f'{self.graph_url}/drives/{drive_id}/root:/{folder_path}',
                                  headers=headers)

            if result.status_code == 200:
                folder_exists = 1
                folder_content = result.json()
            else:
                folder_exists = 0

            if folder_exists == 0:
                result = requests.post(f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/children',
                                       headers=headers,
                                       json={
                                           "name": folder_name,
                                           "folder": {},
                                           "@microsoft.graph.conflictBehavior": "rename"
                                       })
                folder_content = result.json()

        except ValueError:
            print(traceback.format_exc())

        return folder_content

    def create_file(self, headers, data, drive_id, filename, folder_id, overwrite=True):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param data: data content to upload either in bytes or string value format
           :param drive_id: Specific sharepoint drive id (base site directory), retrieve id from the list_drives result
           :param filename: Name of the file you'd like to create (including file extension)
           :param folder_id: Id of the folder where you'd like to create the new folder within
           :param overwrite: If True overwrite the existing file with the latest dataset
        """
        # Formatting filename
        filename = urllib.parse.quote(filename)

        # Check whether the file already exists
        file_content = ''
        try:
            result = requests.get(f"{self.graph_url}/drives/{drive_id}/items/{folder_id}/children?$filter=name eq '{filename}'",
                                  headers=headers)

            if len(result.json()['value']) > 0:
                file_exists = 1
                file_id = result.json()['value'][0]['id']
            else:
                file_exists = 0
                file_id = ''

            if file_exists == 1 and overwrite:
                result = requests.put(
                    f'{self.graph_url}/drives/{drive_id}/items/{file_id}/content',
                    headers=headers,
                    data=data
                )

                file_content = result.json()
            elif file_exists == 0:
                result = requests.put(
                    f'{self.graph_url}/drives/{drive_id}/items/{folder_id}:/{filename}:/content'
                    , headers=headers
                    , data=data
                )

                file_content = result.json()
        except ValueError:
            print(traceback.format_exc())

        return file_content

    def download_file(self, headers, drive_id, file_id, download_name, download_path=None):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param drive_id: Specific sharepoint drive id (base site directory), retrieve id from the list_drives result
           :param file_id: data content to upload either in bytes or string value format
           :param download_name: name for the downloaded file content
           :param download_path: location of where to download the file content
        """
        try:
            result = requests.get(f'{self.graph_url}/drives/{drive_id}/items/{file_id}/content',
                                  headers=headers)

            if download_path is None:
                open(download_name, 'wb').write(result.content)
            else:
                download_path = download_path + download_name
                with open(download_path, 'wb') as f:
                    f.write(result.content)
        except ValueError:
            print(traceback.format_exc())

    def delete_file(self, headers, drive_id, folder_path, filename):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param drive_id: Specific sharepoint drive id (base site directory), retrieve id from the list_drives result
           :param folder_path: Sharepoint folder path
           :param filename: Name of the file you'd like to delete (including file extension)
        """
        delete_output = ''
        try:
            rel_path = urllib.parse.quote(f'{folder_path}{filename}')
            result = requests.delete(f'{self.graph_url}/drives/{drive_id}/root:/{rel_path}',
                                     headers=headers)

            delete_output = result.status_code
        except ValueError:
            print(traceback.format_exc())

        return delete_output

    def delete_folder(self, headers, drive_id, folder_path):
        """:param headers: used for authentication, parsed from the result of the bearer_token function
           :param drive_id: Specific sharepoint drive id (base site directory), retrieve id from the list_drives result
           :param folder_path: Sharepoint folder path, the last folder within the path will be deleted
        """
        delete_output = ''
        try:
            rel_path = urllib.parse.quote(f'{folder_path}')
            result = requests.delete(f'{self.graph_url}/drives/{drive_id}/root:/{rel_path}',
                                     headers=headers)

            delete_output = result.status_code
        except ValueError:
            print(traceback.format_exc())

        return delete_output

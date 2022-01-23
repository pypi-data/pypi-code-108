'''
Client for gofile.io
See https://gofile.io/api for option descriptions
'''

from hashlib import sha256

import requests

class Gofile:
    '''
    Client for gofile.io
    '''
    def __init__(self, token: str = None):
        self.base_url = 'https://{}.gofile.io'
        if token is None:
            self.token = self.create_account()
        else:
            self.token = token

    def create_account(self) -> str:
        '''
        Create a new account.

        Returns:
            str: the token of the new account
        '''
        try:
            res = requests.get(f'{self.base_url.format("api")}/createAccount')
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] == 'ok':
                return res_json['data']['token']
            else:
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_server(self) -> str:
        '''
        Get the best server available to receive files.

        Returns:
            str: the server name
        '''
        try:
            res = requests.get(f'{self.base_url.format("api")}/getServer')
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] == 'ok':
                return res_json['data']['server']
            else:
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def upload_file(self, file: str, folder_id: str = None, description: str = None, password: str = None, tags: str = None, expire: str = None) -> dict:
        '''
        Upload one file on a specific server.
        If you specify a folderId, the file will be added to this folder.
        '''
        data = {
            'token': self.token,
            'file': open(file, 'rb'),
            'folderId': folder_id,
            'description': description,
            'password': password,
            'tags': tags,
            'expire': expire,
        }

        try:
            res = requests.post(f'{self.base_url.format(self.get_server())}/uploadFile', files=data)
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] == 'ok':
                return res_json['data']
            else:
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_content(self, content_id: str, password: str = None) -> dict:
        '''
        Get a specific content details.
        '''
        params = {
            'token': self.token,
            'contentId': content_id,
            'websiteToken': 'websiteToken',
        }

        if password:
            try:
                digest = sha256(password.encode('utf-8')).hexdigest()
            except:
                raise SystemExit(f'failed to generate digest from password: {password}')
            params['password'] = digest
        
        try:
            res = requests.get(f'{self.base_url.format("api")}/getContent', params=params)
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] == 'ok':
                return res_json['data']
            else:
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> None:
        '''
        Create a new folder.
        '''
        data = {
            'token': self.token,
            'parentFolderId': parent_folder_id or self.get_account_details()['rootFolder'],
            'folderName': folder_name,
        }

        try:
            res = requests.put(f'{self.base_url.format("api")}/createFolder', data=data)
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] != 'ok':
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def set_folder_option(self, folder_id: str, option: str, value: str) -> None:
        '''
        Set an option on a folder.
        '''
        data = {
            'token': self.token,
            'folderId': folder_id,
            'option': option,
            'value': value,
        }

        try:
            res = requests.put(f'{self.base_url.format("api")}/setFolderOption', data=data)
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] != 'ok':
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def copy_content(self, content_id: str, dest_folder_id: str) -> None:
        '''
        Copy one of multiple contents to another folder.
        '''
        data = {
            'token': self.token,
            'contentsId': content_id,
            'folderIdDest': dest_folder_id,
        }

        try:
            res = requests.put(f'{self.base_url.format("api")}/copyContent', data=data)
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] != 'ok':
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def delete_content(self, content_id: str) -> None:
        '''
        Delete one or multiple files/folders.
        '''
        data = {
            'token': self.token,
            'contentsId': content_id,
        }

        try:
            res = requests.delete(f'{self.base_url.format("api")}/deleteContent', data=data)
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] != 'ok':
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_account_details(self, all_details: bool = True) -> dict:
        '''
        Retrieving specific account information.
        '''
        params = {
            'token': self.token,
            'allDetails': all_details,
        }

        try:
            res = requests.get(f'{self.base_url.format("api")}/getAccountDetails', params=params)
            res.raise_for_status()
            res_json = res.json()
            if res_json['status'] == 'ok':
                return res_json['data']
            else:
                raise requests.exceptions.RequestException(f'status: {res_json["status"]}')
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

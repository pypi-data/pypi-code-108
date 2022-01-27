from .authenticator import Authenticator
from base64 import b64encode, b64decode
from urllib.parse import urlparse
from functools import lru_cache
import requests
import json


class StackService(Authenticator):
    def __init__(self, service_url, client_key_id, shared_secret, **kwargs):
        self.service_url = service_url
        self.service_token = 'StackService'
        self.timeout = kwargs.get('timeout', 300)
        super().__init__(client_key_id, shared_secret, **kwargs)

    @property
    def region(self):
        return(self.get_identity()['region'])

    @property
    def stackname(self):
        return(self.get_identity()['stackname'])


    def request_url(self, path, bearer_token, protocol='get', data=None):
        headers={'Content-Type': 'application/json', 'Authorization': bearer_token}
        url = self.service_url + path
        if protocol in ['post', 'POST']:
            r = requests.post(url, headers=headers, timeout=self.timeout)
        elif protocol in ['delete', 'DELETE'] and data is not None:
            r = requests.delete(url, data=json.dumps(data), headers=headers, timeout=self.timeout)
        else:
            r = requests.get(url, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        return json.loads(r.text)

    @lru_cache(maxsize=None)
    def get_identity(self):
        path = '/identity'
        bearer_token = self.get_service_bearer_token(self.service_token)
        return self.request_url(path, bearer_token, 'get')

    def get_server_status(self):
        path = '/status'
        bearer_token = self.get_service_bearer_token(self.service_token)
        return self.request_url(path, bearer_token, 'get')

    def webserver_list(self):
        status = self.get_server_status()
        return list(status)

    def get_installation_typo3_configuration(self, installation_name):
        path = '/installation-management/installations/%s/typo3config' % installation_name
        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.get(self.service_url + path, headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        data = json.loads(r.text)
        decoded_data = {}
        for file_entry, value in data.items():
            decoded_data[file_entry] = b64decode(value).decode('utf-8')
        return(decoded_data)

    def update_installation_typo3_configuration(self, installation_name, local_configuration, task_id, task_key):
        path = '/installation-management/installations/%s/typo3config' % installation_name
        encoded_localconfiguration = b64encode(local_configuration.encode())
        payload = {'LocalConfiguration': encoded_localconfiguration.decode(), 'task_id': task_id, 'task_key': task_key}
        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.put(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def create_installation(self, installation_name, context, fileserver_s3_url, database_s3_url, task_id, task_key):
        path = '/installation-management/installations/%s' % installation_name
        payload = {
                   'context': context,
                   'filedata_s3_url': fileserver_s3_url,
                   'database_s3_url': database_s3_url,
                   'task_id': task_id,
                   'task_key': task_key
                  }
        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.post(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def update_installation(self, installation_name, changeset, task_id, task_key):
        path = '/installation-management/installations/%s' % installation_name
        payload = {
                   'changeset': changeset,
                   'task_id': task_id,
                   'task_key': task_key
                  }

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.put(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def installations_list(self):
        path = '/installation-management/installations'
        bearer_token = self.get_service_bearer_token(self.service_token)
        return self.request_url(path, bearer_token, 'get')

    def logical_stacks_list(self):
        path = '/logical-stacks/'
        bearer_token = self.get_service_bearer_token(self.service_token)
        return self.request_url(path, bearer_token, 'get')

    def delete_installation(self, installation_name, task_id, task_key):
        payload = {'task_id': task_id, 'task_key': task_key}
        path = '/installation-management/installations/%s' % (installation_name)

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.delete(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def backup_installation_to_bucket(self, installation, metadata_url, filedata_url, dbdata_url, s3_access_key, s3_access_secret, s3_session_token, task_id, task_key):
        payload = {'filedata_s3_url': filedata_url, 'manifest_s3_url': metadata_url, 'database_s3_url': dbdata_url, 'task_id': task_id, 'task_key': task_key, 's3_access_key': s3_access_key, 's3_access_secret': s3_access_secret, 's3_session_token': s3_session_token}
        path = '/installation-management/installations/%s/backup' % installation

        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.post(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

    def web_server_status(self):
        path = '/status'
        bearer_token = self.get_service_bearer_token(self.service_token)
        return self.request_url(path, bearer_token, 'get')

    def web_server_reload(self):
        path = '/web/reload'
        bearer_token = self.get_service_bearer_token(self.service_token)
        return self.request_url(path, bearer_token, 'post')

    def app_server_reload(self):
        path = '/app/reload'
        bearer_token = self.get_service_bearer_token(self.service_token)
        return self.request_url(path, bearer_token, 'post')

    def maintenance_script_list(self):
        path = '/maintenance/list_scripts'
        bearer_token = self.get_service_bearer_token(self.service_token)
        return self.request_url(path, bearer_token, 'get')

    def maintenance_script_execute(self, installation_name, script, task_id, task_key):
        path = '/installation-management/installations/%s/execute_script' % (installation_name)

        if not isinstance(script, str):
            raise ValueError('Script argument must be a string')

        payload = {'script': script, 'task_id': task_id, 'task_key': task_key}
        bearer_token = self.get_service_bearer_token(self.service_token)
        r = requests.post(self.service_url + path, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'Authorization': bearer_token}, timeout=self.timeout)
        r.raise_for_status()
        return(json.loads(r.text))

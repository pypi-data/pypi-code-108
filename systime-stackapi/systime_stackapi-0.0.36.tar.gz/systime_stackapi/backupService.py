from .authenticator import Authenticator
from base64 import b64encode, b64decode
from urllib.parse import urlparse
import requests
import time
import json
from tenacity import retry, stop_after_delay, stop_after_attempt

class BackupService(Authenticator):
    def __init__(self, service_url, client_key_id, shared_secret, **kwargs):
        self.service_url = service_url
        self.service_token = 'BackupService'
        self.timeout = kwargs.get('timeout', 300)
        super().__init__(client_key_id, shared_secret, **kwargs)

    @retry(reraise=True, stop=(stop_after_delay(10) | stop_after_attempt(5)))
    def request_url(self, path, bearer_token, protocol='get'):
        headers={'Content-Type': 'application/json', 'Authorization': bearer_token}
        url = self.service_url + path
        if protocol in ['post', 'POST']:
            r = requests.post(url, headers=headers, timeout=self.timeout)
        else:
            r = requests.get(url, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        return r

    def create_signed_upload_links(self, backup_policy, backup_type, backup_name):
        path = '/backups/{}/{}/{}'.format(backup_policy, backup_type, backup_name)
        bearer_token = self.get_service_bearer_token(self.service_token)
        r = self.request_url(path, bearer_token, 'post')
        return json.loads(r.text)

    def get_signed_download_links(self, backup_policy, backup_type, backup_name, backup_id):
        path = '/backups/{}/{}/{}/{}'.format(backup_policy, backup_type, backup_name, backup_id)
        bearer_token = self.get_service_bearer_token(self.service_token)
        r = self.request_url(path, bearer_token, 'get')
        return json.loads(r.text)

    def list_backups(self, backup_policy, backup_type):
        path = '/backups/{}/{}'.format(backup_policy, backup_type)
        bearer_token = self.get_service_bearer_token(self.service_token)
        r = self.request_url(path, bearer_token, 'get')
        return json.loads(r.text)

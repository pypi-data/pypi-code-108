import os
import re
import time
from datetime import datetime, timedelta
import json
import logging
import getpass
import requests

DATA_TRANSFER_REMOTE=True


DEFAULT_TIMEOUT_S = 100
CONFIG_PATH = '.mlsteam'


class MyelindlApi(object):
    def __init__(self, address=None, username=None, data_port=9000):
        self.base_url = "http://{}/api".format(address) or 'http://localhost/api'
        self.address = address or 'localhost'
        if address and address.startswith('http'):
            raise MyelindlApiError('address has to be IP:Port format.')
        self.host = self.address.split(':')[0]
        self.username = username or getpass.getuser()
        self.config_path = os.path.join(os.getenv('HOME'), '.mlsteam')
        self.key_path = os.path.join(self.config_path, 'key')
        self.cred_file = os.path.join(self.config_path, 'cred')
        self.data_port = data_port
        self.access_token = None
        self.refresh_token = None
        self.access_token_acquire_time = None
        self.refresh_token_acquire_time = None

        if DATA_TRANSFER_REMOTE:
            if address is None or username is None:
                self.load_credential()

    def save_credential(self):
        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)
        if not self.address or not self.username:
            raise MyelindlApiError('Wrong input')

        with open(self.cred_file, encoding='utf-8', mode='w') as cred:
            json.dump({
                'address': self.address,
                'host': self.host,
                'username': self.username,
                'data_port': self.data_port,
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'access_token_acquire_time': str(self.access_token_acquire_time),
                'refresh_token_acquire_time': str(self.refresh_token_acquire_time),
            }, cred)

    def load_credential(self):
        if not os.path.exists(self.cred_file):
            raise MyelindlApiError('Login First')

        with open(self.cred_file, encoding='utf-8') as cred:
            data = json.load(cred)

        if 'address' not in data or 'username' not in data:
            raise MyelindlApiError('Login First')

        self.host = data['host']
        self.address = data['address']
        self.host = self.address.split(':')[0]
        self.base_url = "http://{}/api".format(self.address)
        self.username = data['username']
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.data_port = data['data_port']
        self.access_token_acquire_time = float(data['access_token_acquire_time'])
        self.refresh_token_acquire_time = float(data['refresh_token_acquire_time'])

    def is_access_token_expired(self):
        return datetime.now() > (datetime.fromtimestamp(self.access_token_acquire_time) + timedelta(minutes=30))

    def is_refresh_token_expired(self):
        return datetime.now() > (datetime.fromtimestamp(self.refresh_token_acquire_time) + timedelta(days=30))

    def clear_credential(self):
        if os.path.exists(self.cred_file):
            os.remove(self.cred_file)

    def login(self, password):
        self.request_token(password)
        self.save_credential()

    def request_token(self, password):
        auth_token = self._request('auth/login',
            method='post',
            data={'username': self.username, 'password': password},
            access_token=None
        )
        self.access_token = auth_token['access_token']
        self.refresh_token = auth_token['refresh_token']
        self.access_token_acquire_time = time.time()
        self.refresh_token_acquire_time = time.time()

    def renew_token(self):
        if self.is_refresh_token_expired():
            raise MyelindlApiError({'error', 'Token expired pleas login Again.'})
        auth_token = self._request('auth/refresh',
            method='post',
            access_token=self.refresh_token,
            check_token_expire=False,
        )
        self.access_token = auth_token['access_token']
        self.access_token_acquire_time = time.time()

    def version(self):
        return self._request('version',
            method='get',
        )

    ############################
    # Dataset API
    ############################
    def minio_api_key(self):
        return self._request('minio_key',
            method='get',
            access_token=self.access_token,
        )

    def bucket_add(self, name):
        return self._request('buckets',
            method='post',
            access_token=self.access_token,
            data={
                'name': name,
            }
        )

    def bucket_del(self, name):
        return self._request('buckets/{}'.format(name),
            method='delete',
            access_token=self.access_token,
        )

    def dataset_publish(self, _id, _type, name, description, data_dir):
        return self._request('datasets',
            method='post',
            access_token=self.access_token,
            data={
                'id': _id,
                'name': name,
                'type': _type,
                'description': description,
                'data_dir': data_dir,
            }
        )

    def dataset_unpublish(self, _id):
        return self._request('datasets/{}/publish'.format(_id),
            method='delete',
            access_token=self.access_token,
        )

    def dataset_list(self):
        return self._request('datasets',
            method='get',
            access_token=self.access_token,
        )

    def dataset_items(self, _id, _dir=''):
        return self._request('datasets/{}/items'.format(_id),
            method='get',
            access_token=self.access_token,
            data={'path': _dir}
        )

    def dataset_info(self, _id):
        return self._request('datasets/{}'.format(_id),
            method='get',
            access_token=self.access_token,
        )

    ############################
    # Model API
    ############################
    def process_model_tag(self, model_tag):

        user = self.username
        model = model_tag
        tag = 'latest'

        user_and_model = model.split('/')
        if len(user_and_model) >= 2:
            user = user_and_model[-2]
            model = user_and_model[-1]

        model_and_tag = model.split(':')
        if len(model_and_tag) >= 2:
            model = model_and_tag[-2]
            tag = model_and_tag[-1]

        return '{}/{}:{}'.format(user, model, tag)

    def model_list(self, offset=0, limit=None):
        return self._request('models',
            method='get',
            access_token=self.access_token,
            data={'offset':offset, 'limit':limit},
        )

    def model_versions(self, model_name, offset=0, limit=None):
        return self._request('models/{}'.format(model_name),
            method='get',
            access_token=self.access_token,
            data={'offset':offset, 'limit':limit},
        )

    def model_push(self, model_tag, data_dir, description='', _type='file'):
        model_tag = self.process_model_tag(model_tag)
        return self._request('models/{}'.format(model_tag),
            method='post',
            access_token=self.access_token,
            data={
                'model_dir': data_dir,
                'description': description,
                'type': _type,
            }
        )

    def model_delete(self, model_tag):
        model_tag = self.process_model_tag(model_tag)
        return self._request('models/{}'.format(model_tag),
            method='delete',
            access_token=self.access_token,
        )

    def model_pull(self, model_tag, output_dir=''):
        model_tag = self.process_model_tag(model_tag)
        return self._request('models/{}/blob'.format(model_tag),
            method='get',
            access_token=self.access_token,
            output_format='file',
            output_file_dir=output_dir,
        )

    def model_info(self, model_tag):
        model_tag = self.process_model_tag(model_tag)
        return self._request('models/{}'.format(model_tag),
            method='get',
            access_token=self.access_token,
        )

    ############################
    # Server API
    ############################
    def list_server(self):
        return self._request('servers',
            method='get',
            access_token=self.access_token,
        )

    def create_server(self, network):
        return self._request('servers',
            method='post',
            access_token=self.access_token,
            data={'network': network}
        )

    def stop_server(self, server_id):
        return self._request('servers/{}'.format(server_id),
            method='delete',
            access_token=self.access_token,
        )

    def server_inference(self, server_id , image_file, total):
        with open(image_file,'rb') as f:
            return self._request('servers/{}/inference'.format(server_id),
                method='post',
                access_token=self.access_token,
                data={'total':total},
                files={'image': f},
            )

    ###########################
    # Work
    ###########################
    def work_list(self):
        return self._request('works',
            method='get',
            access_token=self.access_token,
        )

    def work_create(self, container, dataset, num_gpu, port, user_args):
        return self._request('works',
            method='post',
            access_token=self.access_token,
            data={'container': container,
                  'num_gpu': num_gpu,
                  'dataset': dataset,
                  'port': port,
                  'user_args': user_args}
        )

    def work_delete(self, _id):
        return self._request('works/{}'.format(_id),
            method='delete',
            access_token=self.access_token,
        )

    def work_info(self, _id):
        return self._request('works/{}'.format(_id),
            method='get',
            access_token=self.access_token,
        )

    ###########################
    # Service
    ###########################
    def service_list(self):
        return self._request('services',
            method='get',
            access_token=self.access_token,
        )

    def service_create(self, _id):
        return self._request('services',
            method='post',
            access_token=self.access_token,
            data={'checkpoint': _id}
        )

    def service_delete(self, _id):
        return self._request('services/{}'.format(_id),
            method='delete',
            access_token=self.access_token,
        )

    ###########################
    # Checkpoint
    ###########################
    def checkpoint_list(self):
        return self._request('checkpoints',
            method='get',
            access_token=self.access_token,
        )

    def checkpoint_download(self, _id):
        return self._request('checkpoints/{}/download'.format(_id),
            method='get',
            access_token=self.access_token,
        )

    def checkpoint_delete(self, _id):
        self._request('checkpoints/{}'.format(_id),
            method='delete',
            access_token=self.access_token,
        )

    def checkpoint_info(self, _id):
        return self._request('checkpoints/{}'.format(_id),
            method='get',
            access_token=self.access_token,
        )

    ###########################
    # Projects
    ###########################
    def project_create(self, name, dataset):
        return self._request('projects',
            method='post',
            access_token=self.access_token,
            data={'name':name,
                  'dataset':dataset}
        )

    def project_delete(self, project_id):
        self._request('projects/{}'.format(project_id),
            method='delete',
            access_token=self.access_token,
        )

    def project_list(self):
        return self._request('projects',
            method='get',
            access_token=self.access_token,
        )

    def project_get_info(self, project_id):
        return self._request('projects/{}'.format(project_id),
            method='get',
            access_token=self.access_token,
        )
    ###########################
    # Jobs
    ###########################
    def job_create(self, project, image_tag, job_name,
                   pkg_path, parameters, num_gpu, user_args):
        return self._request('jobs',
            method='post',
            access_token=self.access_token,
            data={'username': self.username,
                'project': project,
                'image-tag': image_tag,
                'job-name': job_name,
                'pkg-path': pkg_path,
                'num-gpu': num_gpu,
                'user-args': user_args,
                'parameters': parameters,
            }
        )

    def job_clone(self, pkg_path, job_id):
        return self._request('jobs/{}/repoclone'.format(job_id),
            method='post',
            access_token=self.access_token,
            data={'repo-path': pkg_path}
        )

    def job_commit(self, job_id):
        return self._request('jobs/{}'.format(job_id),
            method='post',
            access_token=self.access_token,
        )

    def job_train(self, job_id):
        return self._request('jobs/{}/train'.format(job_id),
            method='post',
            access_token=self.access_token,
        )

    def job_list(self):
        return self._request('jobs',
            method='get',
            access_token=self.access_token,
        )

    def job_log(self, _id):
        return self._request('jobs/{}/log'.format(_id),
            method='get',
            output_format='plain',
            access_token=self.access_token,
        )

    def job_delete(self, _id):
        return self._request('jobs/{}'.format(_id),
            method='delete',
            access_token=self.access_token,
        )

    def job_abort(self, _id):
        return self._request('jobs/{}/abort'.format(_id),
            method='POST',
            access_token=self.access_token,
        )

    def job_download(self, _id):
        return self._request('jobs/{}/download'.format(_id),
            method='get',
            access_token=self.access_token,
            output_format='file',
        )

    ###########################
    # Container images
    ############################
    def image_list(self):
        return self._request('images',
            method='get',
            access_token=self.access_token,
        )

    def image_delete(self, _id):
        return self._request('images/{}'.format(_id),
            method='delete',
            access_token=self.access_token,
        )

    def image_pull(self, tag):
        return self._request('images',
            method='post',
            access_token=self.access_token,
            data={'tag': tag}
        )

    ###########################
    # Utils
    ############################
    def _request(self, path,
            method='get',
            data=None,
            files=None,
            output_format='json',
            output_file_dir='',
            timeout=DEFAULT_TIMEOUT_S,
            access_token=None,
            headers=None,
            check_token_expire=True,
        ):
        if headers is None:
            headers = {}
        url = '{0}/{1}'.format(self.base_url, path)
        func = getattr(requests, method)
        if access_token:
            if self.is_access_token_expired() and check_token_expire:
                logging.warning("token expire renew token")
                self.renew_token()
                self.save_credential()
                access_token = self.access_token
            headers.update({
                'Authorization': 'Bearer {}'.format(access_token)
            })

        response = func(
            url,
            data=data,
            files=files,
            stream=True if output_format == 'file' else False,
            timeout=timeout,
            headers=headers,
        )
        self._handle_error_msg(response, output_format)

        return self._process_output(response, output_format, output_file_dir)

    def _handle_error_msg(self, response, form):
        try:
            response.raise_for_status()
        except Exception as e :
            err_msg = ''
            if form == 'json':
                try:
                    result = json.loads(response.text)
                    if 'error' in result and result['error']:
                        err_msg = result['error']
                    elif 'msg' in result and result['msg']:
                        err_msg = result['msg']
                except ValueError:
                    err_msg = f'{e}, output: {response.text}'
            else:
                err_msg = str(e)
            raise MyelindlApiError({'error': f"{response.status_code}:{err_msg}"})

    def _process_output(self, response, form, output_file_dir=''):
        result = None
        if form == 'json':
            try:
                result = json.loads(response.text)
                if 'error' in result and result['error']:
                    raise MyelindlApiError(result)
            except ValueError:
                raise MyelindlApiError({
                    'error': f"API return value format error. output: {response.text}"
                })
        elif form == 'plan':
            result = response.text
        elif form == 'file':
            d = response.headers['content-disposition']
            fname = re.findall("filename=(.+)", d)[0]
            fname = os.path.join(output_file_dir, fname)
            if output_file_dir != '' and not os.path.exists(output_file_dir):
                os.makedirs(output_file_dir)
            with open(fname, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        else:
            raise MyelindlApiError({
                'error': f"Output format not supported {form}"
            })

        return result


class MyelindlApiError(Exception):
    def __init__(self, result):
        self.result = result
        if isinstance(result, dict):
            self.message = result['error']
        else:
            self.message = result
        Exception.__init__(self, self.message)

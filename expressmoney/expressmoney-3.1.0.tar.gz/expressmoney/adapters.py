import datetime
import json
from typing import Union

import requests
from google.protobuf import timestamp_pb2
from google.cloud import pubsub_v1, secretmanager, secretmanager_v1
from google.cloud import tasks_v2
from google.cloud import error_reporting
from rest_framework import status

report = error_reporting.Client()
client = secretmanager.SecretManagerServiceClient()
access_secret_version = secretmanager_v1.types.service.AccessSecretVersionRequest()


class PubSub:
    """ Google Cloud PubSub Adapter"""

    __publisher = pubsub_v1.PublisherClient()

    def __init__(self, topic_id: str, access_token: str = None, project='expressmoney'):
        self.__topic_path = self.__publisher.topic_path(project, topic_id)
        self.__access_token = str(access_token)

    def publish(self, payload: dict = None):
        attrs = {'topic': self.__topic_path, }

        if payload and not isinstance(payload, dict):
            raise TypeError('Payload should be dict type')

        if payload:
            if self.__access_token:
                payload.update({'access_token': self.__access_token})
        else:
            if self.__access_token:
                payload = {'access_token': self.__access_token}
        if payload:
            attrs.update({'data': json.dumps(payload, ensure_ascii=False).encode('UTF-8')})

        self.__publisher.publish(**attrs)


class Tasks:
    """ Google Cloud Tasks Adapter"""

    def __init__(self,
                 service: str = 'default',
                 path: str = '/',
                 access_token: str = None,
                 project: str = 'expressmoney',
                 queue: str = 'attempts-1',
                 location: str = 'europe-west1',
                 in_seconds: int = None,
                 ):
        """
        CloudTasks adapter
        Args:
            project: 'expressmoney'
            service: 'default'
            path: '/user'
            access_token: 'Bearer DFD4345345D'
            queue: 'my-appengine-queue'
            location: 'europe-west1'
            in_seconds: None
        """
        self._project = project
        self._service = service
        self._path = path
        self._access_token = access_token
        self._update = None
        self._in_seconds = in_seconds

        self._payload = None
        self._parent = self._client.queue_path(project, location, queue)

    _client = tasks_v2.CloudTasksClient()

    def run(self, payload: dict = None, update: bool = False):
        """
        Execution
        Args:
            payload: {'param': 'value'}
            update: tasks_v2.HttpMethod.PUT
        """
        self._update = update
        self._payload = payload
        task = self._create_task()
        task = self._add_payload(task)
        task = self._convert_in_seconds(task)
        task = self._add_authorization(task)
        task = self._remove_empty_headers(task)
        self._client.create_task(parent=self._parent, task=task)

    def _create_task(self):
        task = {
            'app_engine_http_request': {
                'http_method': self._http_method,
                'relative_uri': self._path,
                'headers': {},
                'app_engine_routing': {
                    'service': self._service,
                    'version': '',
                    'instance': '',
                    'host': '',

                }
            },
        }

        return task

    def _add_authorization(self, task):
        if self._access_token:
            task["app_engine_http_request"]["headers"]['X-Forwarded-Authorization'] = f'Bearer {self._access_token}'
        return task

    def _add_payload(self, task):
        if self._payload is not None:
            if not isinstance(self._payload, dict):
                raise TypeError('Payload should be dict type')
            payload = json.dumps(self._payload, ensure_ascii=False).encode('utf-8')
            task["app_engine_http_request"]["body"] = payload
            task["app_engine_http_request"]["headers"]['Content-Type'] = 'application/json'
        return task

    def _convert_in_seconds(self, task):
        if self._in_seconds is not None:
            d = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._in_seconds)
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)
            task['schedule_time'] = timestamp
        return task

    @staticmethod
    def _remove_empty_headers(task):
        if len(task['app_engine_http_request']['headers']) == 0:
            del task['app_engine_http_request']['headers']
        return task

    @property
    def _http_method(self):
        if self._update:
            return tasks_v2.HttpMethod.PUT
        else:
            return tasks_v2.HttpMethod.GET if self._payload is None else tasks_v2.HttpMethod.POST


class Request:
    """Sync http request"""

    requests = requests

    def __init__(self,
                 service: str = None,
                 path: str = '/',
                 access_token: Union[str, None] = None,
                 project: str = 'expressmoney',
                 timeout: tuple = (30, 30),
                 ):
        self.__project = project
        self.__service = service
        self.__path = path
        self.__access_token = access_token
        self.__timeout = timeout

    def run(self, payload: dict = None, update: bool = False):
        """
        Execution
        Args:
            payload: {'param': 'value'}
            update: requests.put()
        """
        if update:
            response = requests.put(self._uri, json=payload if payload else {}, headers=self._headers,
                                    timeout=self.__timeout)
        elif payload:
            response = requests.post(self._uri, json=payload, headers=self._headers, timeout=self.__timeout)
        else:
            response = requests.get(self._uri, headers=self._headers, timeout=self.__timeout)
        if not any((status.is_success(response.status_code), status.is_client_error(response.status_code))):
            try:
                raise Exception(f'{response.status_code}:{response.url}:{response.json()}')
            except Exception:
                raise Exception(f'{response.status_code}:{response.url}:{response.text}')
        return response

    @property
    def _uri(self):
        local_url = 'http://127.0.0.1:8000'
        url = f'https://{self.__service}-dot-{self.__project}.appspot.com' if self.__service else local_url
        return f'{url}{self.__path}'

    @property
    def _headers(self):
        headers = dict()
        headers.update(self._get_authorization())
        return headers

    def _get_authorization(self) -> dict:
        return {'X-Forwarded-Authorization': f'Bearer {self.__access_token}'} if self.__access_token else {}

    @property
    def _aud(self):
        secrets = {
            'expressmoney': 'projects/1086735462412/secrets/IAP_CLIENT_ID/versions/1',
            'expressmoney-dev': 'projects/13337168308/secrets/IAP_CLIENT_ID/versions/1',
            'loans-russia': 'projects/70455559151/secrets/IAP_CLIENT_ID/versions/1',
        }
        access_secret_version.name = secrets.get(self.__project, None)
        return client.access_secret_version(request=access_secret_version).payload.data.decode("utf-8")

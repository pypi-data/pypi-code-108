from functools import lru_cache

import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


class ESConnector:
    def __init__(self, cls):
        self.host = cls.endpoint
        self.local = self.host == 'localhost'
        self.port = cls.port
        self.authentication = cls.authentication
        self.user = cls.user
        self.password = cls.password

    @lru_cache(maxsize=128)
    def connect(self):
        config = self.__configure()
        connection = Elasticsearch(**config)
        return connection

    def __configure(self):
        if not self.port and self.local:
            self.port = 9200
        elif not self.port and not self.local:
            self.port = 443
        config = {
            'hosts':[
                {
                    'host': self.host,
                    'port': self.port
                }
            ],
            'use_ssl': not self.local,
            'verify_certs': not self.local,
            'connection_class': RequestsHttpConnection
        }
        if self.authentication == 'lambda':
            config['http_auth'] = self.__authenticate_lambda()
        if self.authentication == 'user-password':
            config['http_auth'] = (self.user, self.password)
        return config

    def __authenticate_lambda(self):
        session = boto3.Session()
        credentials = session.get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            session.region_name,
            'es',
            session_token=credentials.token
        )
        return awsauth

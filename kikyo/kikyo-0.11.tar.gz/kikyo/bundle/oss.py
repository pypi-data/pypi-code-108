import io
from typing import Any

import oss2
from kikyo import Kikyo
from kikyo.oss import OSS, Bucket
from minio import Minio


class MinioBasedOSS(OSS):
    def __init__(self, client: Kikyo):
        settings = client.settings.deep('minio')

        if not settings:
            return

        self.client = client
        self.bucket_prefix = settings.get('bucket_prefix', default='')
        self.minio = Minio(
            settings['endpoint'],
            access_key=settings['access_key'],
            secret_key=settings['secret_key'],
            secure=settings['secure'],
        )
        self.minio_address = f"{'https' if settings['secure'] else 'http'}://{settings['endpoint']}"

        client.add_component('minio_oss', self)

    def bucket(self, name: str) -> Bucket:
        if name.startswith(self.bucket_prefix):
            bucket_name = name
        else:
            bucket_name = f'{self.bucket_prefix}{name}'

        return MinioBucket(bucket_name, self)


class MinioBucket(Bucket):
    def __init__(self, name: str, oss: MinioBasedOSS):
        self._name = name
        self.minio = oss.minio
        self.minio_address = oss.minio_address

    def get_object_link(self, key: str) -> str:
        return f'{self.minio_address}/{self._name}/{key}'

    def put_object(self, key: str, data: Any):
        _data = None
        _length = None
        if isinstance(data, bytes):
            _length = len(data)
            _data = io.BytesIO(data)
        else:
            raise RuntimeError(f'Unsupported data type: {type(data)}')
        self.minio.put_object(self._name, key, _data, _length)

    def get_object(self, key: str) -> Any:
        resp = self.minio.get_object(self._name, key)
        return resp.data


class AliyunOSS(OSS):
    def __init__(self, client: Kikyo):
        settings = client.settings.deep('oss2')

        if not settings:
            return

        self.client = client
        self.bucket_prefix = settings.get('bucket_prefix', default='')

        self.auth = oss2.Auth(settings['access_key'], settings['access_key_secret'])
        self.endpoint = settings['endpoint']
        self.secure = settings.get('secure', False)

        client.add_component('aliyun_oss', self)

    def bucket(self, name: str) -> Bucket:
        if name.startswith(self.bucket_prefix):
            bucket_name = name
        else:
            bucket_name = f'{self.bucket_prefix}{name}'

        return AliyunBucket(bucket_name, self)


class AliyunBucket(Bucket):
    def __init__(self, name: str, oss: AliyunOSS):
        self.name = name
        self.oss = oss
        self.bucket = oss2.Bucket(
            self.oss.auth,
            self.oss.endpoint,
            self.name,
            connect_timeout=20,
        )

    def get_object_link(self, key: str) -> str:
        return f'{"https" if self.oss.secure else "http"}://{self.name}.{self.oss.endpoint}/{key}'

    def put_object(self, key: str, data: Any):
        self.bucket.put_object(key, data)

    def get_object(self, key: str) -> Any:
        resp = self.bucket.get_object(key)
        return resp.read()

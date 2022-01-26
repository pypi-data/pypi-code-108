import hashlib
import mimetypes
import os
from functools import partial
from io import BytesIO, SEEK_CUR

import backoff
import certifi
import urllib3
from minio import Minio
from minio.commonconfig import CopySource
from minio.error import S3Error

from . import path as io_path


def token_error_fallback(f, set_client):
    def _token_error_fallback(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except S3Error as ex:
            if ex.code == "ExpiredToken":
                client = set_client()

                # If put_object call and data is BytesIO seekable stream.
                # Move stream pointer back relatively to the content length before retrying
                if f.__name__ == "put_object":
                    data = kwargs.get("data", args[2])
                    length = kwargs.get("length", args[3])
                    if hasattr(data, "seek"):
                        data.seek(-length, SEEK_CUR)

                return getattr(client, f.__name__)(*args, **kwargs)
            raise ex

    return _token_error_fallback


class MinioIO:
    http_pool = urllib3.PoolManager(
        timeout=urllib3.Timeout.DEFAULT_TIMEOUT,
        maxsize=16,
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
        retries=urllib3.Retry(
            total=0,
            backoff_factor=0.2,
            status_forcelist=[500, 502, 503, 504]
        )
    )

    def __init__(self, cache_files: bool = True, credentials=None):
        self.routes = {}
        self.cache_files = cache_files

        if credentials is None:
            self.credentials = credentials

    def client_factory(self, prefix, credentials_func):
        def _update_client():
            client = Minio(**credentials_func(), secure=True, http_client=self.http_pool)

            # Decorate all functions on client with token error fallback to recursively create new client
            for name in dir(client):
                func = getattr(client, name)
                if not name.startswith("_") and callable(func):
                    setattr(client, name, token_error_fallback(func, _update_client))

            # Update routes
            self.routes[prefix] = client
            return client

        return _update_client()

    def resolve_access_rights(self, path, *args, **kwargs):
        self.set_route(path, *args, **kwargs)

    def set_route(self, prefix, resource_id, resource_type, mode='r'):
        credentials_func = partial(self.credentials.get_credentials,
                                   resource_id, resource_type=resource_type, mode=mode)
        client = self.client_factory(prefix=prefix,
                                     credentials_func=credentials_func)
        return client

    def get_client(self, path):
        try:
            return next(v for k, v in self.routes.items() if path.startswith(k))
        except StopIteration:
            raise KeyError(f"Not able to match path '{path}' to storage route")

    @backoff.on_exception(backoff.expo, (S3Error, urllib3.exceptions.MaxRetryError), max_tries=5)
    def read(self, path, *, client=None):
        try:
            file_path = path[5:] if path.startswith("s3://") else path
            bucket, obj = file_path.split("/", 1)
            client = client or self.get_client(path)
            return client.get_object(bucket, obj).data
        except S3Error as err:
            if err.code == "NoSuchKey":
                raise KeyError(err)
            else:
                raise err

    @backoff.on_exception(backoff.expo, (S3Error, urllib3.exceptions.MaxRetryError), max_tries=5)
    def write(self, path, content, *, client=None):
        file_path = path[5:] if path.startswith("s3://") else path
        bucket = file_path.split("/", 1)
        bucket, obj = tuple(bucket) if len(bucket) == 2 else ("", bucket[0])
        content_type = mimetypes.guess_type(obj)[0] or "application/octet"
        data = content.encode() if isinstance(content, str) else content
        data = BytesIO(data) if isinstance(data, bytes) else data
        length = data.seek(0, os.SEEK_END)
        client = client or self.get_client(path)
        data.seek(0)
        digest = hashlib.md5(data.getbuffer())
        return client.put_object(bucket, obj, data, length, content_type=content_type,
                                 metadata={"md5": digest.hexdigest()})

    def copy(self, src, dst, *args, **kwargs):
        srcclient = self.get_client(src)  # TODO what about cross origin copies?
        dstclient = self.get_client(dst)

        if srcclient == dstclient:
            src = src[5:] if src.startswith("s3://") else src
            dst = dst[5:] if dst.startswith("s3://") else dst

            bucket = dst.split("/", 1)
            bucketdst, dst = tuple(bucket) if len(bucket) == 2 else ("", bucket[0])

            bucket = src.split("/", 1)
            bucketsrc, src = tuple(bucket) if len(bucket) == 2 else ("", bucket[0])

            return srcclient.copy_object(bucketdst, dst, source=CopySource(bucketsrc, src), *args, **kwargs)
        else:
            return self.write(dst, client=dstclient, content=self.read(src, client=srcclient))

    def remove(self, path):
        client = self.get_client(path)
        file_path = path[5:] if path.startswith("s3://") else path
        bucket, obj = file_path.split("/", 1)
        return client.remove_object(bucket, obj)

    def move(self, src, dst, *args, **kwargs):
        self.copy(src, dst, *args, **kwargs)
        self.remove(src)

    def make_dirs(self, path, exist_ok=True):
        pass

    def isfile(self, path):
        try:
            self.stat_object(path)
            return True
        except S3Error as err:
            if err.code == "NoSuchKey":
                return False
            else:
                raise err

    def stat_object(self, path):
        obj_path = path[5:] if path.startswith("s3://") else path
        bucket = obj_path.split("/", 1)
        bucket, obj = tuple(bucket) if len(bucket) == 2 else ("", bucket[0])
        client = self.get_client(path)
        return client.stat_object(bucket, obj)

    def walk(self, path, prefix=None, recursive=True, include_object=False, exclude_hidden=False, **kwargs):
        folder_path = path.rstrip("/") + "/"
        folder_path = folder_path[5:] if folder_path.startswith("s3://") else folder_path
        bucket = folder_path.split("/", 1)
        prefix = bucket[1] if prefix is None else "/".join((bucket[1], prefix)) if len(bucket) == 2 else prefix
        bucket = bucket[0]

        if exclude_hidden:
            kwargs["start_after"] = prefix + ".\uFFFD"

        client = self.get_client(path)
        objects = client.list_objects(bucket, prefix=prefix,
                                      recursive=recursive, **kwargs)

        name_start = len(prefix) if len(prefix) else 0
        s3_path = "s3://" + folder_path
        yield from self._walk_objects(objects, name_start, s3_path, include_object)

    @staticmethod
    def _walk_objects(objects, name_start, s3_path, include_object):
        last, base = None, None
        files = []
        for p in objects:
            if not p.is_dir:
                _obj = p.object_name[name_start:].rsplit("/", 1)
                try:
                    base, file = _obj
                except ValueError:
                    base, file = (None, _obj[0])
                out = (file, p) if include_object else file
                if base == last:
                    files.append(out)
                else:
                    # Yield folder
                    yield io_path.safe_join(s3_path, last), [], files
                    # Clean state for next yield
                    last = base
                    files = [out]
        else:
            yield io_path.safe_join(s3_path, last), [], files

    def get_md5(self, path):
        fobj = self.stat_object(path)
        try:
            return fobj.metadata["x-amz-meta-md5"]
        except KeyError:
            md5 = self.calculate_md5(path)
            self.copy(src=path, dst=path, metadata={**fobj.metadata, "md5": md5})
            return md5

    def calculate_md5(self, path):
        digest = hashlib.md5(self.read(path)).hexdigest()
        return digest

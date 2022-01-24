import os
from . import path
from .local_io import LocalIO
from .minio_io import MinioIO
import urllib


class IoTools:
    def __init__(self, cache_root=None, localio=LocalIO(), minio=MinioIO(),
                 max_cache_usage_fraction=0.8, path=path):
        """
        TODO Abstract backends
        :param cache_path: common cache path
        :param localio: path to local file storage backend
        :param minio: path to minio backend
        :param max_cache_usage_fraction: stop caching when exeeding this usage fraction
        """
        self.minio = minio
        self.localio = localio
        self.cache_root = cache_root
        self.max_cache_usage_fraction = max_cache_usage_fraction
        self.path = path

    @staticmethod
    def factory(**kwargs):
        """
        Build IoTools with new backends
        :param args:
        :param kwargs:
        :return:
        """
        kwargs["minio"] = kwargs.get("minio", MinioIO())
        kwargs["localio"] = kwargs.get("localio", LocalIO())
        return IoTools(**kwargs)

    def set_cache_root(self, root):
        root = os.path.normpath(root)
        assert os.path.isdir(root), "Cache root must be a path to a directory"
        self.cache_root = root

    def get_backend(self, path):
        if path.startswith("s3://"):
            return self.minio
        else:
            return self.localio

    def resolve_access_rights(self, path, *args, **kwargs):
        backend = self.get_backend(path)
        backend.resolve_access_rights(path, *args, **kwargs)

    def read_file(self, path, cache=None, errors="raise"):
        try:
            path = path if isinstance(path, str) else str(path, "utf-8")
            backend = self.get_backend(path)

            cache_root = cache or self.cache_root
            if cache_root and backend.cache_files:
                return self.localio.file_cache(path, cache_root, backend.read, self.max_cache_usage_fraction)
            else:
                return backend.read(path)
        except Exception as ex:
            if errors == "raise":
                raise ex
            return None

    def write_file(self, path, content):
        return self.get_backend(path).write(path, content)

    def remove(self, path):
        return self.get_backend(path).remove(path)

    def copy(self, src, dst, *args, **kwargs):
        src_backend = self.get_backend(src)
        dst_backend = self.get_backend(dst)
        if src_backend == dst_backend:
            return src_backend.copy(src, dst, *args, **kwargs)
        else:
            return dst_backend.write(dst, src_backend.read(src))

    def move(self, src, dst, *args, **kwargs):
        if src == dst:
            return
        src_backend = self.get_backend(src)
        dst_backend = self.get_backend(dst)
        if src_backend == dst_backend:
            return src_backend.move(src, dst, *args, **kwargs)
        else:
            raise NotImplementedError("Cross origin move")

    def make_dirs(self, path):
        backend = self.get_backend(path)
        return backend.make_dirs(path)

    def walk(self, path, exclude_hidden=False, **kwargs):
        backend = self.get_backend(path)
        return backend.walk(path, exclude_hidden=exclude_hidden, **kwargs)

    def isfile(self, path):
        backend = self.get_backend(path)
        return backend.isfile(path)

    @staticmethod
    def get_uri(path):
        if path.startswith("gs://"):
            path = path[5:]
        elif path.startswith("s3://"):
            path = path[len(path[:5].split("/", 1)[0]) + 5:]
        return urllib.parse.quote(path, safe='')

    def get_md5(self, path):
        backend = self.get_backend(path)
        return backend.get_md5(path)
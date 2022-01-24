import hashlib
import os
import shutil
import tempfile
import hashlib


class safe_open:
    def __init__(self, path, mode="w+b"):
        """
        Temporary file backed storage for safely writing to cache
        :param path:
        :param mode:
        """
        self.path = path
        self.mode = mode

    def __enter__(self):
        self._file = tempfile.NamedTemporaryFile(self.mode, delete=False)
        return self._file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()
        try:
            if exc_type is None:
                os.rename(self._file.name, self.path)
        except OSError:
            os.remove(self._file.name)


class LocalIO:
    def __init__(self):
        self.cache_files = False

    def resolve_access_rights(self, *args, **kwargs):
        pass

    @staticmethod
    def file_cache(path, cache_root, data_getter, max_cache_usage_fraction):
        """
        Cache file data to local file
        :param path: source path
        :param cache_root: root of cache location
        :param data_getter: function getting the data from th
        :param max_cache_usage_fraction: do not fill disk more than this fraction
        :return:
        """
        # Target
        cp = os.path.join(cache_root,
                          os.path.normpath(path.replace(":", "", 1)))
        if len(cp) > 260 and os.name == "nt":
            cp = os.path.join(cache_root, "file_path_hash", hashlib.sha1(path.replace(":", "", 1).encode()).hexdigest() + "." + path.split(".")[-1])
        # Cache hit
        if os.path.isfile(cp):
            with open(cp, 'rb') as fp:
                output = fp.read()
            return output

        # Load data
        output = data_getter(path)

        # Cache Update
        total, used, free = shutil.disk_usage(cache_root)
        if used / total < max_cache_usage_fraction:
            os.makedirs(os.path.dirname(cp), exist_ok=True)
            with safe_open(cp, 'wb') as fp:
                fp.write(output)

        return output

    @staticmethod
    def read(path):
        with open(path, 'rb') as fp:
            return fp.read()

    @staticmethod
    def write(path, content):
        if isinstance(content, (bytes, bytearray)):
            with open(path, 'wb') as fp:
                return fp.write(content)
        elif isinstance(content, str):
            with open(path, 'w') as fp:
                return fp.write(content)
        else:
            with open(path, 'wb') as fp:
                return fp.write(content.read())


    @staticmethod
    def remove(path):
        if not os.path.exists(path):
            raise IOError("Path: '%s' does not exist" % path)
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

    @staticmethod
    def copy(src, dst, *args, **kwargs):
        return shutil.copyfile(src, dst, *args, **kwargs)

    @staticmethod
    def move(src, dst, *args, **kwargs):
        return shutil.move(src, dst, *args, **kwargs)

    @staticmethod
    def make_dirs(path, exist_ok=True):
        return os.makedirs(path, exist_ok=exist_ok)

    def walk(self, path, exclude_hidden=False, **kwargs):
        if exclude_hidden:
            yield from self.walk_visible(path)
        else:
            yield from os.walk(path)

    @staticmethod
    def walk_visible(path):
        for r, d, f in os.walk(path):
            d[:] = (x for x in d if not x.startswith("."))
            f[:] = (x for x in f if not x.startswith("."))
            yield r, d, f

    @staticmethod
    def isfile(path):
        return os.path.isfile(path)

    @staticmethod
    def get_md5(path):
        with open(path, "rb") as f:
            file_hash = hashlib.md5()
            buf = f.read(8192)
            while buf:
                file_hash.update(buf)
                buf = f.read(8192)
            return file_hash.hexdigest()

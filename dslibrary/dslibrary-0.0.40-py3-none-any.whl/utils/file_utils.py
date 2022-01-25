"""
File/stream related tools.
"""
import io
import os
import tempfile
import typing
import urllib.request

from dslibrary.engine_intf import FileSystemLocal, FileSystemReadOnly, S3Connection

try:
    import fsspec
except ImportError:
    fsspec = None


class FileOpener(object):
    """
    Opens read/write streams on a wide range of URIs.
    """
    def __init__(self, root_folder: str=None):
        """
        :param root_folder:   Default folder, in case relative local paths are given.
        """
        self._root = os.path.expanduser(root_folder or ".")

    def http_open(self, path: str, mode: str, **kwargs):
        """
        HTTP and FTP can be handled with the built-in urllib.

        :param path:        URI specifying an HTTP or FTP location.
        :param mode:        'r' and 'rb' are supported.
        :param kwargs:      'headers' can be specified.
        :return:        A stream, if the supplied arguments were supported, or None.
        """
        if path.startswith("https://") or path.startswith("http://") or path.startswith("ftp://"):
            if mode == "rb":
                request = urllib.request.Request(url=path, headers=kwargs.get("headers") or {})
                return urllib.request.urlopen(request, **kwargs)
            if mode == "r":
                byte_stream = self.http_open(path, mode, **kwargs)
                return io.TextIOWrapper(byte_stream)
            if mode in ("w", "wb"):
                # data can be sent to a REST service
                #  - set method to POST or PUT
                #  - set any needed authentication headers in 'headers'
                #  - path is URL plus any required arguments in the query string
                request = urllib.request.Request(url=path, headers=kwargs.get("headers") or {}, method=kwargs.get("method", "POST"))
                return write_stream_with_read_on_close(mode, r_mode='rb', on_close=lambda stream: urllib.request.urlopen(request, data=stream))
            raise ValueError(f"Append mode is not supported for {path}")

    def uri_open(self, path: str, mode: str, **kwargs):
        """
        Open specific/exotic URIs, like s3, abfs, adl, gs, etc..

        :param path:        The URI, usually of the form PROTO://BUCKET/PATH.
        :param mode:        'r', rb', 'w', etc.
        :param kwargs:      Additional options passed through to the target library (i.e. fsspec).
        :return:        A file stream, if a handler was found.
        """
        if "://" not in path:
            return
        if not fsspec:
            raise ImportWarning(f"The 'fsspec' package is required to open {path}")
        return fsspec.open(path, mode=mode, **kwargs)

    def local_open(self, path: str, mode: str, **kwargs):
        """
        Open local files.
        :param path:    A relative path, relative to self._root, or an absolute path.
        :param mode:    'r', 'rb', 'w', 'wb', 'a', 'ab'.
        :param kwargs:  No additional options are recognized.
        :return:    A file stream.
        """
        full_path = os.path.join(self._root, path)
        return open(full_path, mode)

    def open(self, path: str, mode: str, **kwargs):
        """
        Open files.

        :param path:    Path to file, or URI of file.
        :param mode:    Open mode (r, rb, w, wb, a, ab)
        :param kwargs:  Additional arguments to customize details of the operation.
        :return:    File-like object.
        """
        # some really simple external file access can be handled without fsspec
        stream = self.http_open(path, mode, **kwargs)
        if stream:
            return stream
        # URIs go through fsspec
        stream = self.uri_open(path, mode, **kwargs)
        if stream:
            return stream
        # local files
        return self.local_open(path, mode, **kwargs)


def write_stream_with_read_on_close(w_mode: str, r_mode: str, on_close: typing.Callable):
    """
    Open a write stream that saves data in a temporary file and sends a read stream for that data to a supplied method.
    :param w_mode:          'w' or 'wb'.
    :param r_mode:          'r' or 'rb'.
    :param on_close:        Method called with read stream
    :return:
    """
    fh = tempfile.NamedTemporaryFile(mode=w_mode, delete=False)
    def closer():
        if not fh.closed:
            fh.flush()
        with open(fh.name, r_mode) as f_r:
            on_close(f_r)
        os.remove(fh.name)
    fh.close = closer
    return fh


def connect_to_filesystem(uri: str, for_write: bool=False, **kwargs):
    """
    Generate an open(filename, mode) method based on a URI and credentials.
    :param uri:             A partial URI like "s3://bucket", or a local path.
    :param for_write:       Whether to allow write access.
    :param kwargs:          Additional arguments, namely credentials.
    :return:            A FileSystem instance that lets you work with files in the remote filesystem.
    """
    if "://" not in uri:
        # uri can just be a local path
        fs = FileSystemLocal(uri)
    else:
        # otherwise we assume the usual cloud format: protocol://bucket
        protocol, bucket = uri.strip("/").split("://", maxsplit=1)
        bucket = bucket.split("/")[0]
        if ":" in bucket:
            raise ValueError(f"Invalid URI for external filesystem: {uri}")
        if protocol == "s3":
            # fsspec does not support streaming upload or 'read_only' mode, so we have our own implementation
            return S3Connection(bucket=bucket, **kwargs)
        if not fsspec:
            raise ImportWarning(f"fsspec not installed, can't open filesystem: {uri}")
        fs = fsspec.filesystem(protocol, bucket=bucket, **kwargs)
    if not for_write:
        return FileSystemReadOnly(fs)
    return fs

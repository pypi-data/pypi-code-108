import pathlib
import typing
import zipfile
from io import BytesIO


class ZipWrapper:
    """ A wrapper around a :py:class:`~zipfile.ZipFile`.
    The zip file can be either located in the filesystem or in memory.

    Example usage::

        zip_wrapper = ZipWrapper('test.zip')
        with zip_wrapper as zip_file, zip_file.open() as f:
            # f is now an open zipfile.ZipFile object

    :param path: The path to the zip file, or
    :param content: A :py:class:`bytes` or :py:class:`memoryview` containing the data of the zip file
    """
    path: typing.Optional[pathlib.Path]
    content: typing.Union[bytes, memoryview, None]
    zip_file: typing.Optional[zipfile.ZipFile]

    def __init__(self, *, path: pathlib.Path = None, content: typing.Union[bytes, memoryview] = None):
        self.path = path
        self.content = content
        self.zip_file = None

    def __enter__(self):
        if self.zip_file is None:
            self.zip_file = zipfile.ZipFile(self.path if self.path else BytesIO(self.content), 'r')

        return self.zip_file

    def __exit__(self, *args, **kwargs):
        pass

    def close(self):
        """ Close the wrapped zip file """
        if self.zip_file:
            try:
                self.zip_file.close()
            except OSError:
                pass
            self.zip_file = None

    def __del__(self):
        self.close()

    def __getstate__(self):
        if self.path:
            return {'path': self.path}
        else:
            return {'content': bytes(self.content)}

    def __setstate__(self, state):
        if 'path' in state:
            self.path = state['path']
            self.content = None
        else:
            self.path = None
            self.content = state['content']

        self.zip_file = None

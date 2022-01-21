#!/usr/bin/env python3
# coding: utf-8

import base64
import hashlib
import mimetypes
import os.path
import tarfile
import urllib.parse
import zipfile
from functools import cached_property
from typing import Generator, List, Union, Iterable


def read_as_chunks(path: str, length=-1, offset=0, chunksize=65536) \
        -> Generator[bytes, None, None]:
    if length == 0:
        return
    if length < 0:
        length = float('inf')
    chunksize = min(chunksize, length)
    with open(path, 'rb') as fin:
        fin.seek(offset)
        while chunksize:
            chunk = fin.read(chunksize)
            if not chunk:
                break
            yield chunk
            length -= chunksize
            chunksize = min(chunksize, length)


def compute_checksum(path_or_chunks: Union[str, Iterable[bytes]], algo='sha1'):
    hashobj = hashlib.new(algo) if isinstance(algo, str) else algo
    # path_or_chunks:str - a path
    if isinstance(path_or_chunks, str):
        chunks = read_as_chunks(path_or_chunks)
    else:
        chunks = path_or_chunks
    for chunk in chunks:
        hashobj.update(chunk)
    return hashobj


def checksum(path: str, algo='sha1', length=-1, offset=0):
    chunks = read_as_chunks(path, length=length, offset=offset)
    return compute_checksum(chunks, algo=algo)


def checksum_hexdigest(path: str, algo='sha1', length=-1, offset=0):
    hashobj = checksum(path, algo=algo, length=-1, offset=0)
    return hashobj.hexdigest()


def b64_encode_data_url(mediatype: str, content: bytes):
    b64 = base64.b64encode(content).decode('ascii')
    return 'data:{};base64,{}'.format(mediatype, b64)


def b64_encode_local_file(path: str):
    mediatype = mimetypes.guess_type(path)[0]
    with open(path, 'rb') as fin:
        return b64_encode_data_url(mediatype, fin.read())


class Archive:
    @cached_property
    def inner_paths(self) -> List[str]:
        raise NotImplementedError

    @cached_property
    def entry_path(self) -> str:
        paths = [p for p in self.inner_paths if p.endswith('index.html')]
        if not paths:
            return ''
        return min(paths, key=lambda s: len(s))

    def extract_as_bytes(self, inner_path: str) -> bytes:
        raise NotImplementedError

    def open_inner_file(self, inner_path: str):
        raise NotImplementedError

    @staticmethod
    def open(path: str) -> 'Archive':
        if path.endswith('.zip'):
            return ZipArchive(path)
        tar_suffixes = ['.tar', '.tgz', '.tar.gz']
        for suffix in tar_suffixes:
            if path.endswith(suffix):
                return TarArchive(path)

    def __enter__(self):
        archive_file = getattr(self, 'archive_file', None)
        if hasattr(archive_file, '__enter__'):
            archive_file.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        archive_file = getattr(self, 'archive_file', None)
        if hasattr(archive_file, '__exit__'):
            archive_file.__exit__(exc_type, exc_val, exc_tb)
        return self


class TarArchive(Archive):
    def __init__(self, path: str):
        self.archive_file = tarfile.open(path)

    @cached_property
    def inner_paths(self) -> List[str]:
        return self.archive_file.getnames()

    def extract_as_bytes(self, inner_path: str) -> bytes:
        return self.archive_file.extractfile(inner_path).read()

    def open_inner_file(self, inner_path: str):
        return self.archive_file.extractfile(inner_path)


class ZipArchive(Archive):
    def __init__(self, path: str):
        self.archive_file = zipfile.ZipFile(path)

    def __enter__(self):
        self.archive_file.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.archive_file.__exit__(exc_type, exc_val, exc_tb)

    @cached_property
    def inner_paths(self) -> List[str]:
        return self.archive_file.namelist()

    def extract_as_bytes(self, inner_path: str) -> bytes:
        return self.archive_file.open(inner_path).read()

    def open_inner_file(self, inner_path: str):
        return self.archive_file.open(inner_path)


class Directory:
    def __init__(self, base_dir: str):
        self.base_dir = os.path.abspath(base_dir)

    def __repr__(self):
        c = self.__class__.__name__
        return '{}({!r})'.format(c, self.base_dir)

    def under(self, *paths):
        return os.path.join(self.base_dir, *paths)

    def relative_to_base_dir(self, path: str):
        path = os.path.abspath(path)
        return os.path.relpath(path, self.base_dir)

    under_base_dir = under

    def read_as_chunks(self, path: str, length=-1, offset=0, chunksize=65536) \
            -> Generator[bytes, None, None]:
        path = self.under_base_dir(path)
        return read_as_chunks(
            path, length=length,
            offset=offset, chunksize=chunksize,
        )

    def checksum_hexdigest(self, path: str, algo='sha1') -> str:
        path = self.under_base_dir(path)
        return checksum_hexdigest(path, algo=algo)

    def read_as_binary(self, path: str):
        path = self.under_base_dir(path)
        with open(path, 'rb') as fin:
            return fin.read()

    def read_as_base64_data_url(self, path: str):
        path = self.under_base_dir(path)
        return b64_encode_local_file(path)

    def save_as_file(self, path: str, chunks):
        path = self.under_base_dir(path)
        with open(path, 'wb') as fout:
            for chunk in chunks:
                fout.write(chunk)


class MappedDirectory(Directory):
    def __init__(self, base_dir: str, base_url: str):
        super().__init__(base_dir)
        # Note:
        # urllib.parse.urljoin('/a/b', 'c.jpg') => '/a/c.jpg'
        # urllib.parse.urljoin('/a/b/', 'c.jpg') => '/a/b/c.jpg'
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url

    def __repr__(self):
        c = self.__class__.__name__
        return '{}({!r}, {!r})'.format(c, self.base_dir, self.base_url)

    def join_url(self, path: str):
        return urllib.parse.urljoin(self.base_url, path)

    def relative_to_base_url(self, url: str):
        base_url_path = urllib.parse.urlparse(self.base_url).path
        url_path = urllib.parse.urlparse(url).path
        return os.path.relpath(url_path, base_url_path)

    def convert_local_path_to_url(self, path: str):
        path = os.path.abspath(path)
        path = self.relative_to_base_dir(path)
        return self.join_url(path)

    def convert_url_to_local_path(self, url: str):
        path = self.relative_to_base_url(url)
        return self.under(path)

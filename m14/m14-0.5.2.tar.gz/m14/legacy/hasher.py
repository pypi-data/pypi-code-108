#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import hashlib
import re
import zlib

import six

from joker.stream.utils import checksum


def guess_hash_algorithm(digest):
    algo_map = {
        ('bin', 16): 'md5',
        ('bin', 20): 'sha1',
        ('bin', 28): 'sha224',
        ('bin', 32): 'sha256',
        ('bin', 48): 'sha384',
        ('bin', 64): 'sha512',
        ('hex', 32): 'md5',
        ('hex', 40): 'sha1',
        ('hex', 56): 'sha224',
        ('hex', 64): 'sha256',
        ('hex', 96): 'sha384',
        ('hex', 128): 'sha512',
    }
    if isinstance(digest, six.binary_type):
        try:
            digest = digest.decode('utf-8')
        except Exception:
            return algo_map.get(('bin', len(digest)))
    if not re.match(r'[0-9A-Fa-f]+', digest):
        return
    return algo_map.get(('hex', len(digest)))


class HashedPath(object):
    """
    /data/web/config.ini;;f6da8154d73f954cdfebd04d6c76cff8
    for integrity-check purpose only
    """
    delimiter = ';;'

    def __init__(self, digest, algo, path):
        self.digest = digest
        self.algo = algo
        self.path = path

    @staticmethod
    def compute_hash(path, algo='md5'):
        try:
            return checksum(path, algo=algo).hexdigest()
        except IOError:
            return hashlib.new(algo, b'\0').hexdigest()

    @classmethod
    def generate(cls, path, algo='md5'):
        digest = cls.compute_hash(path, algo)
        return cls(digest, algo, path)

    @classmethod
    def parse(cls, h_path):
        if cls.delimiter not in h_path:
            return cls('', 'md5', h_path)
        path, digest = h_path.split(cls.delimiter, 2)
        algo = guess_hash_algorithm(digest)
        return cls(digest, algo, path)

    def __str__(self):
        return '{}{}{}'.format(self.path, self.delimiter, self.digest)

    def verify(self):
        if not self.digest:
            return True
        hx1 = self.generate(self.path, self.algo or 'md5')
        return hx1.digest == self.digest


class Hasher(object):
    """
    Unified interface for hashlib & zlib hash functions
    """
    __hfuncs__ = {
        'adler32': zlib.adler32,
        'crc32': zlib.crc32,
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha224': hashlib.sha224,
        'sha256': hashlib.sha256,
        'sha384': hashlib.sha384,
        'sha512': hashlib.sha512,
    }

    __hlens__ = {
        32: 'md5',
        40: 'sha1',
        56: 'sha224',
        64: 'sha256',
        96: 'sha384',
        128: 'sha512',
    }

    def __init__(self, name):
        self.name = name.lower()
        if self.name not in self.__hfuncs__:
            raise ValueError("hash func '{}' not found".format(name))
        if name in {'adl32', 'crc32'}:
            self.hash = getattr(zlib, name)  # a checksum function
            self.emulate = True
            self.result = self.hash(bytes())  # intermediate result
        else:
            self.hash = getattr(hashlib, name)()  # a hash object
            self.emulate = False
            self.result = 0  # not used for hashlib functions

    def __repr__(self):
        cn = self.__class__.__name__
        return '{}({})'.format(cn, repr(self.name))

    def _update_with_bytes(self, data):
        """
        :param data: (bytes)
        """
        # hashlib.md* / hashlib.sha*
        if not self.emulate:
            self.hash.update(data)
            return
        # zlib.adler32 / zlib.crc32
        if self.result is None:
            self.result = self.hash(data)
        else:
            self.result = self.hash(data, self.result)

    def _update_with_traverser(self, data):
        # from joker.nested.traverse import Traverser
        # traverser = Traverser(self, lambda x: self.update(x))
        # traverser()
        raise NotImplementedError

    def update(self, data):
        if isinstance(data, six.text_type):
            return self._update_with_bytes(data.encode())
        elif isinstance(data, six.binary_type):
            return self._update_with_bytes(data)
        self._update_with_traverser(data)

    def hexdigest(self):
        # hashlib funcs
        if not self.emulate:
            return self.hash.hexdigest()
        # zlib.adler32 / zlib.crc32
        return hex(self.result & 0xffffffff).replace('0x', '')

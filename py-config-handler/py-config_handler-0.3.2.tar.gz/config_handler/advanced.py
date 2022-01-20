#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MIT License
Copyright (c) 2020-2022 Chris1320

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import zlib
import base64

from . import ciphers


class Advanced():
    """
    A class that creates and manipulates an "advanced" configuration file.

    + This mode is for storing any datatype supported by the JSON data format.
    """

    def __init__(self, config_path: str, epass: str = None, readonly: bool = False):
        """
        The initialization method of Advanced() class.

        :param str config_path: The path of the configuration file to use.
        :param str epass: The encryption password.
        :param bool readonly: True if the configuration file is read-only.
        """

        self.VERSION = (0, 2, 0)  # Parser version

        self.config_path = config_path
        self.epass = epass
        self.__readonly = readonly

        self.__metadata = {}  # Metadata of the configuration file.
        self.__dictionary = {}  # The actual data of the configuration file.

        # All compression and encryption methods must accept and return `bytes` type.
        self.supported = {
            "compression": ("zlib",),
            "encryption": ("aes256",),
            "valuetypes": (str, int, float, bool, list, tuple, dict)
        }

    def __compress(self, data: bytes) -> bytes:
        """
        Compress <data>. Raises ValueError if the compression method is not supported.

        :param bytes data: The data to compress.

        :returns str: Unmodified data if compression is None.
        :returns bytes: The compressed data.
        """

        if self.__metadata["compression"] == "zlib":
            return zlib.compress(data)

        else:
            raise ValueError(f"Unsupported compression type `{self.__metadata['compression']}`")

    def __decompress(self, data: bytes) -> bytes:
        """
        Decompress <data>. Raises ValueError if the compression method is not supported.

        :param bytes data: The data to decompress.

        :returns str: Unmodified data if compression is None.
        :returns bytes: The decompressed data.
        """

        if self.__metadata["compression"] == "zlib":
            return zlib.decompress(data)

        else:
            raise ValueError(f"Unsupported compression type `{self.__metadata['compression']}`")

    def __encrypt(self, data: bytes) -> bytes:
        """
        Encryp <data>. Raises ValueError if the encryption method is not supported.

        :param bytes data: The data to be encrypted.

        :returns bytes: The encrypted data.
        """

        if self.__metadata["encryption"] == "aes256":
            if not ciphers.aes_support:
                raise ValueError("AES256 encryption is not supported in this system.")

            return ciphers.AES256(self.epass).encrypt(base64.b64encode(data).decode(self.__metadata["encoding"]))

        else:
            raise ValueError(f"Unsupported encryption type `{self.__metadata['encryption']}`")

    def __decrypt(self, data: bytes) -> bytes:
        """
        Decrypt <data>. Raises ValueError if the encryption method is not supported.

        :param bytes data: The data to decrypt.

        :returns bytes: The decrypted data.
        """

        if self.__metadata["encryption"] == "aes256":
            if not ciphers.aes_support:
                raise ValueError("AES256 encryption is not supported in this system.")

            return base64.b64decode(ciphers.AES256(self.epass).decrypt(data))

        else:
            raise ValueError(f"Unsupported encryption type `{self.__metadata['encryption']}`")

    def _check_key(self, key: str) -> bool:
        """
        Returns True if key is valid. Otherwise, raise ValueError.

        :param str key: The key to check

        :returns bool: True if key is valid.
        """

        if type(key) is not str:
            raise ValueError(f"Invalid key `{key}`")

        return True

    def new(self, name: str, author: str = None, compression: str = None, encryption: str = None, encoding: str = "utf-8") -> None:
        """
        Create a new configuration file.

        This method sets the metadata of the current configuration file.

        :param str name: The name of the configuration file.
        :param str author: The author of the configuration file.
        :param str compression: The compression method to use.
        :param str encryption: The encryption method to use.
        :param str encoding: The encoding to use when writing the configuration file.
        """

        if self.__readonly:
            raise PermissionError("The configuration file is read-only.")

        assert compression in self.supported["compression"] or compression is None
        assert encryption in self.supported["encryption"] or encryption is None
        assert "encoding test".encode(encoding)  # Check if the encoding is valid.

        self.__metadata["name"] = name
        self.__metadata["author"] = author
        self.__metadata["compression"] = compression
        self.__metadata["encryption"] = encryption
        self.__metadata["encoding"] = encoding
        self.__metadata["version"] = self.VERSION
        self.__metadata["dictionary"] = ""

        self.__dictionary = {}

        self.save()  # Save the new configuration file to `self.config_path`.

    def load(self) -> None:
        """
        Load the configuration file.

        Raises a `json.decoder.JSONDecodeError` if the AES encryption password is incorrect,
        or the configuration file is corrupt.
        Raises a `ValueError` if the password is not provided and the configuration file is encrypted.
        """

        # ? Decode (Base64)
        # ? Decompress
        # ? Decrypt
        # ? json to dict.decode()

        # Step 1: Load metadata.
        with open(self.config_path, 'r') as fopen:
            self.__metadata = json.load(fopen)

        # check if self.epass is not None.
        if self.epass is None and self.__metadata["encryption"] is not None:
            raise ValueError("The configuration file is encrypted but no password is provided.")

        # Step 2: Decode dictionary.
        dictionary = base64.b64decode(self.__metadata["dictionary"].encode(self.__metadata["encoding"]))

        # Step 3: If compression is used, decompress dictionary.
        if self.__metadata["compression"] is not None:
            dictionary = self.__decompress(dictionary)

        # Step 4: If encryption is used, decrypt dictionary.
        if self.__metadata["encryption"] is not None:
            dictionary = self.__decrypt(dictionary)

        # Step 5: Convert JSON to dictionary.
        self.__dictionary = json.loads(dictionary.decode(self.__metadata["encoding"]))

        return

    def save(self) -> None:
        """
        Save the configuration file.
        """

        # ? dict to json.encode()
        # ? Encrypt
        # ? Compress
        # ? Encode (Base64)

        # self.__metadata will be updated.
        self.__metadata["version"] = self.VERSION

        # Step 1: Convert the dictionary to JSON.
        dictionary = json.dumps(self.__dictionary).encode(self.__metadata["encoding"])

        # Step 2: If encryption is enabled, encrypt the dictionary.
        if self.__metadata["encryption"] is not None:
            dictionary = self.__encrypt(dictionary)

        # Step 3: If compression is enabled, compress the dictionary.
        if self.__metadata["compression"] is not None:
            dictionary = self.__compress(dictionary)

        # Step 4: Encode the dictionary to Base64.
        self.__metadata["dictionary"] = base64.b64encode(dictionary).decode(self.__metadata["encoding"])

        # Step 5: Write metadata to file.
        with open(self.config_path, 'w') as fopen:
            fopen.write(json.dumps(self.__metadata, indent=4))

        return

    # def verify(self, value) -> bool:
    #     """
    #     Check if the type of <value> is valid. Raises a TypeError if its type is not supported.

    #     :param value: The value to check.

    #     :returns bool: True if the type of <value> is valid.
    #     """

    #     if type(value) not in self.supported["valuetypes"]:
    #         raise TypeError(f"The type of <value> is not supported.")

    #     return True

    def set(self, key, value) -> None:
        """
        Set value of a key on `self.__dictionary`.
        """

        self._check_key(key)
        self.__dictionary[key] = value

    def get(self, key):
        """
        Get the value of <key>. Raises a KeyError if the key is not found.
        """

        return self.__dictionary[key]

    def remove(self, key) -> None:
        """
        Remove a key from `self.__dictionary`.
        """

        self.__dictionary.pop(key)

    def keys(self) -> list:
        """
        Get all the keys in `self.__dictionary`.

        :returns list: The list of keys.
        """

        return self.__dictionary.keys()

    def metadata(self) -> dict:
        """
        Return the metadata of the configuration file.
        """

        metadata = self.__metadata.copy()
        metadata.pop("dictionary")
        return metadata

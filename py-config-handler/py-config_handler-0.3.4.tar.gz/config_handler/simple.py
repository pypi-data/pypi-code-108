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

import base64


class Simple():
    """
    A class the creates and manipulates a "simple" configuration file.

    + This mode is for storing string, integer, and decimals only.
    + Comments are supported by appending `#` at the beginning of the line.
    + Each line of the file contains one key-value pair separated by an equal (=) sign.
    """

    def __init__(self, config_path: str, isbase64: bool = False, encoding: str = "utf-8", readonly: bool = False):
        """
        The initialization method for Simple() class.

        :param str config_path: The path of the configuration file to use.
        :param bool isbase64: True if the configuration file is encoded via Base64.
        :param str encoding: The encoding to be used.
        :param bool readonly: True if the configuration file is read-only.
        """

        self.VERSION = (0, 2, 0)  # Parser version

        self.isbase64 = isbase64
        self.encoding = encoding

        self._config_path = config_path
        self.__readonly = readonly
        self.__data = {}  # We will put the contents of the configuration file here.

    def _parseKey(self, key: str) -> None:
        """
        Check if the key is valid. Raises a ValueError if the key is invalid.

        :param str key: The key to check.
        """

        if type(key) is not str:  # Separate this check from other checks to avoid TypeError when key is not a str.
            raise ValueError(f"Invalid key `{key}`")

        if '=' in key or key.startswith('#') or '\n' in key:
            raise ValueError(f"Invalid key `{key}`")

        return

    def load(self) -> None:
        """
        Read the config file and store it to self.__data as a dictionary.
        Call this method when you want to read the configuration file.
        If you save without calling load(), the configuration file will be overwritten.

        :returns void:
        """

        with open(self._config_path, 'r') as fopen:
            if self.isbase64:  # Decode data if it is Base64 encoded.
                config_data = base64.b64decode(fopen.read()).decode(self.encoding)

            else:
                config_data = fopen.read()

        for line in config_data.splitlines():
            if line.startswith('#'):
                continue  # Skip comments.

            data = line.partition('=')  # * data[0] is the key, data[1] is the separator, data[2] is the value.

            # Write the key-value pair to `self.__data`.
            if data[2].partition('.')[0].isdigit() and data[2].partition('.')[2].isdigit():
                self.__data[data[0]] = float(data[2])

            elif data[2].isdigit():
                self.__data[data[0]] = int(data[2])

            elif data[2].lower() in ("true", "false"):
                if data[2].lower() == "true":
                    self.__data[data[0]] = True

                else:
                    self.__data[data[0]] = False

            else:
                self.__data[data[0]] = str(data[2])

    def save(self) -> None:
        """
        Save the config file. Raises a PermissionError if the configuration file is read-only.

        :returns void:
        """

        if self.__readonly:
            raise PermissionError("The configuration file is read-only.")

        config_data = ""  # Let's initialize it as an empty string first.
        for key in self.__data:
            config_data += f"{key}={self.__data[key]}\n"  # Write the key-value pair to the config file.

        with open(self._config_path, 'w') as fopen:
            if self.isbase64:
                fopen.write(base64.b64encode(config_data.encode(self.encoding)).decode(self.encoding))

            else:
                fopen.write(config_data)

        return

    def get(self, key: str) -> str:
        """
        Get the value of <key> from `self.__data`.
        """

        return self.__data[key]  # Will raise a KeyError exception if the key is not found.

    def set(self, key: str, value) -> None:
        """
        Add or update a new key-value pair to `self.__data`.

        :param str key: The key to add.
        :param value: The value to add.
        """

        self._parseKey(key)  # Check if the key is valid.
        self.__data[key] = value
        return

    def remove(self, key: str) -> None:
        """
        Remove a key-value pair from `self.__data`.

        :param str key: The key to remove.
        """

        self.__data.pop(key)
        return

    def keys(self) -> list:
        """
        Get all the keys in `self.__data`.

        :returns list: The list of keys.
        """

        return self.__data.keys()

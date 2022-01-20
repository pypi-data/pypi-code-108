#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Package exceptions classes
"""


class MalformedInputException(Exception):
    """Exception thrown when input data are malformed"""


class InvalidDataException(Exception):
    """Exception thrown when validated data are not valid"""


class FileNotFoundException(Exception):
    """Exception thrown when resource file could not be found"""


class InvalidArgumentException(Exception):
    """Exception thrown when invalid argument was provided to method"""


class LogicException(Exception):
    """Exception thrown when logic error occur"""


class InvalidStateException(Exception):
    """Exception thrown when invalid state occur"""

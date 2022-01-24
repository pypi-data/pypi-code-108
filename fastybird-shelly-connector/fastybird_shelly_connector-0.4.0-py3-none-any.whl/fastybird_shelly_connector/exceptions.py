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
Shelly connector exceptions module
"""


class InvalidStateException(Exception):
    """
    Service state is not valid

    @package        FastyBird:ShellyConnector!
    @module         exceptions

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class ParsePayloadException(Exception):
    """
    Parsing payload failed

    @package        FastyBird:ShellyConnector!
    @module         exceptions

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class LogicException(Exception):
    """
    Exception thrown when logic error occur

    @package        FastyBird:ShellyConnector!
    @module         exceptions

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """


class FileNotFoundException(Exception):
    """
    Exception thrown when resource file could not be found

    @package        FastyBird:ShellyConnector!
    @module         exceptions

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """

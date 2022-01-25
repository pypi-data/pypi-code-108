"""
This module will host all the exceptions which are raised by fl components
"""


#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

class FLException(Exception):
    pass


class DuplicateRouteException(FLException):
    pass


class InvalidConfigurationException(FLException):
    pass


class InvalidServerConfigurationException(InvalidConfigurationException):
    pass


class NotFoundException(FLException):
    pass


class LocalTrainingException(FLException):
    pass


class TCPMessageOutOfOrder(FLException):
    pass


class GlobalTrainingException(FLException):
    pass


class ModelException(FLException):
    pass


class ModelInitializationException(FLException):
    pass


class ModelUpdateException(FLException):
    pass


class HyperparamsException(FLException):
    pass


class CryptoKeyGenerationException(FLException):
    pass


class CryptoException(FLException):
    pass


class AuthorityException(FLException):
    pass


class KeyManagerException(FLException):
    pass


class WarmStartException(FLException):
    pass


class FusionException(FLException):
    pass


class QuorumException(FLException):
    pass

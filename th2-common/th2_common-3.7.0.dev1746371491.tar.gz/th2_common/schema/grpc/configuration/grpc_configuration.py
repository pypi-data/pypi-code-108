#   Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import json

from th2_common.schema.configuration.abstract_configuration import AbstractConfiguration

from typing import List

from th2_common.schema.message.configuration.message_configuration import FieldFilterConfiguration, \
    RouterFilterConfiguration


class GrpcRawRobinStrategy:

    def __init__(self, endpoints, name) -> None:
        self.endpoints = endpoints
        self.name = name


class GrpcServiceConfiguration(AbstractConfiguration):
    pass


class GrpcServerConfiguration(AbstractConfiguration):

    def __init__(self, attributes, host, port, workers, **kwargs) -> None:
        self.attributes = attributes
        self.host = host
        self.port = port
        self.workers = workers
        self.check_unexpected_args(kwargs)


class GrpcEndpointConfiguration(AbstractConfiguration):

    def __init__(self, host, port, attributes, **kwargs) -> None:
        self.host = host
        self.port = port
        self.attributes = attributes
        self.check_unexpected_args(kwargs)


class GrpcConfiguration(AbstractConfiguration):

    def __init__(self, services, server=None, **kwargs) -> None:
        self.services = services
        if server is not None:
            self.serverConfiguration = GrpcServerConfiguration(**server)
        self.check_unexpected_args(kwargs)


class GrpcRouterFilterConfiguration(RouterFilterConfiguration):

    def __init__(self, endpoint: str, metadata, message, **kwargs) -> None:
        self.metadata = metadata
        self.message = message
        self.endpoint = endpoint
        self.check_unexpected_args(kwargs)

    def get_metadata(self) -> List[FieldFilterConfiguration]:
        return self.metadata

    def get_message(self) -> List[FieldFilterConfiguration]:
        return self.message


class GrpcRawFilterStrategy:

    def __init__(self, filters) -> None:
        self.filters = [GrpcRouterFilterConfiguration(**filter_configuration) for filter_configuration in filters]


class GrpcRouterConfiguration(AbstractConfiguration):

    def __init__(self, workers=5, **kwargs):
        self.workers = int(workers)
        self.check_unexpected_args(kwargs)


class GrpcRetryPolicy:

    def __init__(self, max_attempts=5, initial_backoff=0.1, max_backoff=1., backoff_multiplier=2, status_codes=None, services=None):
        self.max_attempts = max_attempts
        self.initial_backoff = initial_backoff  # Duration in seconds before first retry
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier  # Every consequent backoff time will be multiplied by this
        self.status_codes = status_codes  # List of status code strings on which retry will be attempted
        self.services = services  # List of dictionaries with keys 'service' and 'method', to which policy will apply. Empty one means it will apply to every one.

    @property
    def options(self):
        if self.services is None:
            self.services = [{}]
        if self.status_codes is None:
            self.status_codes = ["UNAVAILABLE"]
        service_config_json = {
            'methodConfig': [{
                'name': self.services,
                'retryPolicy': {
                    'maxAttempts': self.max_attempts,
                    'initialBackoff': str(self.initial_backoff) + 's',
                    'maxBackoff': str(self.max_backoff) + 's',
                    'backoffMultiplier': self.backoff_multiplier,
                    'retryableStatusCodes': self.status_codes,
                },
            }]
        }
        return [("grpc.enable_retries", 1), ("grpc.service_config", json.dumps(service_config_json))]

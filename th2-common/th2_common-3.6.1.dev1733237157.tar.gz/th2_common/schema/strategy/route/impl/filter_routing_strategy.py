#   Copyright 2020-2020 Exactpro (Exactpro Systems Limited)
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


from google.protobuf.message import Message

from th2_common.schema.filter.strategy.impl.default_filter_strategy import DefaultFilterStrategy
from th2_common.schema.grpc.configuration.grpc_configuration import GrpcRawFilterStrategy
from th2_common.schema.strategy.route.routing_strategy import RoutingStrategy


class FilterRoutingStrategy(RoutingStrategy):

    def __init__(self, configuration: GrpcRawFilterStrategy) -> None:
        self.__filter_strategy = DefaultFilterStrategy()
        self.__grpc_configuration = configuration

    def get_endpoint(self, message: Message):
        endpoint: set = self.__filter(message)
        if len(endpoint) != 1:
            raise Exception('Wrong size of endpoints for send. Should be equal to 1')
        return endpoint.__iter__().__next__()

    def __filter(self, message: Message) -> {str}:
        endpoints = set()
        for fields_filter in self.__grpc_configuration.filters:
            if len(fields_filter.message) == 0 and len(fields_filter.metadata) == 0 \
                    or self.__filter_strategy.verify(message=message, router_filter=fields_filter):
                endpoints.add(fields_filter.endpoint)
        return endpoints

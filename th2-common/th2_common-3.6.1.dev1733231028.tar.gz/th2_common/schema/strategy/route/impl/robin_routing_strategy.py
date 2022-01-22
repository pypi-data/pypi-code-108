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


from threading import Lock

from th2_common.schema.grpc.configuration.grpc_configuration import GrpcRawRobinStrategy
from th2_common.schema.strategy.route.routing_strategy import RoutingStrategy


class Robin(RoutingStrategy):

    def __init__(self, configuration) -> None:
        self.endpoints = GrpcRawRobinStrategy(**configuration).endpoints
        self.index = 0
        self.lock = Lock()

    def get_endpoint(self, request):
        with self.lock:
            result = self.endpoints[self.index % len(self.endpoints)]
            self.index = self.index + 1
            return result

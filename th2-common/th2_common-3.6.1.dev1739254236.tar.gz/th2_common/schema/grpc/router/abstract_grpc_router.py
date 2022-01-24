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


from abc import ABC
from concurrent.futures.thread import ThreadPoolExecutor

import grpc

from th2_common.schema.grpc.configuration.grpc_configuration import GrpcConfiguration, GrpcRouterConfiguration
from th2_common.schema.grpc.router.grpc_router import GrpcRouter


class AbstractGrpcRouter(GrpcRouter, ABC):

    def __init__(self, grpc_configuration: GrpcConfiguration,
                 grpc_router_configuration: GrpcRouterConfiguration) -> None:
        self.grpc_configuration = grpc_configuration
        self.grpc_router_configuration = grpc_router_configuration
        self.servers = []
        self.channels = {}

    def start_server(self, *services) -> grpc.Server:
        server = grpc.server(ThreadPoolExecutor(max_workers=self.grpc_router_configuration.workers))

        if self.grpc_configuration.serverConfiguration.host is None:
            server.add_insecure_port(f'[::]:{self.grpc_configuration.serverConfiguration.port}')
        else:
            server.add_insecure_port(
                f'{self.grpc_configuration.serverConfiguration.host}:{self.grpc_configuration.serverConfiguration.port}')

        self.servers.append(server)

        return server

    def close(self, grace=None):
        for server in self.servers:
            server.stop(grace)

        for channel in self.channels.values():
            channel.close()

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


from abc import ABC, abstractmethod

import grpc


class GrpcRouter(ABC):

    @abstractmethod
    def get_service(self, cls):
        pass

    @property
    @abstractmethod
    def server(self) -> grpc.Server:
        pass

    @property
    @abstractmethod
    def async_server(self) -> grpc.aio.Server:
        pass

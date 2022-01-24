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


class SubscribeTarget:

    def __init__(self, queue: str, routing_key: str) -> None:
        self.__queue = queue
        self.__routing_key = routing_key

    def set_queue(self, queue: str):
        self.__queue = queue

    def set_routing_key(self, routing_key: str):
        self.__routing_key = routing_key

    def get_queue(self):
        return self.__queue

    def get_routing_key(self):
        return self.__routing_key

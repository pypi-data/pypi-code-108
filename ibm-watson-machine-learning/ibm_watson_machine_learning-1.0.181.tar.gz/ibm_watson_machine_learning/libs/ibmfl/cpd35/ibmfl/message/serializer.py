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

from abc import ABC, abstractmethod


class Serializer(ABC):
    """
    Abstract class for Serializer
    """
    @abstractmethod
    def serialize(self, msg):
        """
        Serialize a message

        :param msg: message to serialize
        :type msg: `Message`
        :return: serialized byte stream
        :rtype: `b[]`
        """
        pass

    @abstractmethod
    def deserialize(self, serialized_byte_stream):
        """
        Deserialize a byte stream to a message

        :param serialized_byte_stream: byte stream
        :type serialized_byte_stream: `b[]`
        :return: deserialized message
        :rtype: `Message`
        """
        pass

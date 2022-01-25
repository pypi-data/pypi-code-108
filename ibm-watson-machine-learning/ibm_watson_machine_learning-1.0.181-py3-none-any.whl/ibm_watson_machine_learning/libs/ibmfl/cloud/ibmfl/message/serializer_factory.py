"""
Serialization factory provides a way to create a serializer
and deserializer to convert byte streams to a message and
vice versa
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

from ibmfl.message.json_serializer import JSONSerializer
from ibmfl.message.pickle_serializer import PickleSerializer
from ibmfl.message.serializer_types import SerializerTypes


class SerializerFactory(object):
    """
    Class for a factory to serialize and deserialize
    """
    def __init__(self, serializer_type):
        """
        Creates an object of `SerializerFactory` class

        :param serializer_type: type of seriaze and deserialize
        :type serializer_type: `Enum`
        """
        self.serializer = None
        if serializer_type is SerializerTypes.PICKLE:
            self.serializer = PickleSerializer()
        elif serializer_type is SerializerTypes.JSON_PICKLE:
            self.serializer = JSONSerializer()

    def build(self):
        """
        Returns a serializer

        :param: None
        :return: serializer
        :rtype: `Serializer`
        """
        return self.serializer

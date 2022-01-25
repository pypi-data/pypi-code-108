"""
Pickle based serialization
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

import pickle
from ibmfl.message.message import Message
from ibmfl.message.serializer import Serializer


class PickleSerializer(Serializer):
    """
    Class for Pickle based serialization
    """

    def serialize(self, msg):
        """
        Serialize a message using pickle

        :param msg: message to serialize
        :type msg: `Message`
        :return: serialize byte stream
        :rtype: `b[]`
        """
        msg_header = msg.get_header()
        serialized_data = msg.get_data()  # need to serialize the data
        return pickle.dumps({'header': msg_header,
                             'data': serialized_data,
                             })

    def deserialize(self, serialized_byte_stream):
        """
        Deserialize a byte stream to a message

        :param serialized_byte_stream: byte stream
        :type serialized_byte_stream: `b[]`
        :return: deserialized message
        :rtype: `Message`
        """
        data_dict = pickle.loads(serialized_byte_stream)
        if 'MSG_LEN|' in data_dict:
            msg_length = int(data_dict.split('|')[1])
            return msg_length

        msg = Message(data=data_dict['data'])
        msg.set_header(data_dict['header'])

        return msg

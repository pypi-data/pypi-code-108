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


import th2_grpc_common.common_pb2
from google.protobuf.message import Message

from th2_common.schema.strategy.field_extraction.abstract_th2_msg_field_extraction import AbstractTh2MsgFieldExtraction


class Th2BatchMsgFieldExtraction(AbstractTh2MsgFieldExtraction):

    def parse_message(self, message: Message) -> th2_grpc_common.common_pb2.Message:
        return message

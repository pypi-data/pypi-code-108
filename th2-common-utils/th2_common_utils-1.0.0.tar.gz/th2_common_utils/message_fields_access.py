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


from pprint import pformat

from th2_common_utils.converters import message_to_dict, ValueType
from th2_grpc_common.common_pb2 import Value, ListValue, Message


# =========================
# Value
# =========================

def _value_get(self, item):
    try:
        return getattr(self, self.WhichOneof(ValueType.WHICH_ONE_OF))
    except TypeError:
        # If you request protobuf class Value without the item inside, you will get TypeError.
        # Occurs when requesting a non-existent key in the dict.
        raise KeyError(item)


Value.__get__ = _value_get


# =========================
# ListValue
# =========================

def listvalue_getitem(self, index):
    value = self.values[index]
    return value.__get__(index)


def listvalue_len(self):
    return len(self.values)


ListValue.__getitem__ = listvalue_getitem
ListValue.__len__ = listvalue_len


# =========================
# Message
# =========================

def message_getitem(self, item):
    value = self.fields[item]
    return value.__get__(item)


def message_contains(self, item):
    return item in self.fields


def message_repr(self):
    return pformat(message_to_dict(self))


Message.__getitem__ = message_getitem
Message.__contains__ = message_contains
Message.__repr__ = message_repr

# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Contains generated Protobuf objects and Protobuf utilities.

"""

from __future__ import unicode_literals

from appdynamics.lang import bytes, items, long, str
from appdynamics_bindeps.google.protobuf.descriptor import FieldDescriptor
from appdynamics_bindeps.pb import *


def serialize_message(message):
    """Serialize a Protobuf message for transport over ZeroMQ.

    Parameters
    ----------
    message : google.protobuf.message.Message
        The message to serialize

    Returns
    -------
    serialized_data : bytes
        The serialized message

    """
    serialized_data = bytes(message.SerializeToString())
    return serialized_data


def parse_message(message, serialized_data):
    """Deserialize a Protobuf message from a ZeroMQ bytes/Frame.

    Parameters
    ----------
    message : google.protobuf.message.Message
        The Protobuf message to mutate with the data from serialized_data
    serialized_data : zmq.Frame, str, or bytes
        The serialized data to deserialize and load into the message

    """
    if hasattr(serialized_data, 'bytes'):
        serialized_data = serialized_data.bytes

    message.ParseFromString(bytes(serialized_data))
    return message


def pb_from_dict(message, fields):
    """Merge fields from a dict into a Protobuf message.

    Parameters
    ----------
    message : google.protobuf.message.Message
        The Protobuf message to load the data from the dict into
    fields : mapping
        A mapping of the name of attributes of the given message to the
        value to give that attribute. Values can be lists, dictionaries (in
        which case they are recursively converted into the appropriate
        Protobuf message), strings, bytes, or numbers.

    Returns
    -------
    message : google.protobuf.message.Message
        The first argument, `message`, is returned for convenience

    Raises
    ------
    TypeError
        If setting an attribute of `message` fails due to the value being of
        the wrong type (or due to a validation rule on the Protobuf otherwise
        failing), a `TypeError` is raised.

    """

    def from_list(m, vals):
        if not vals:
            return

        if isinstance(vals[0], dict):
            for val in vals:
                child = m.add()
                from_dict(child, val)
        else:
            m.extend(vals)

    def from_dict(m, vals):
        for k, v in items(vals):
            if isinstance(v, dict):
                from_dict(getattr(m, k), v)
            elif isinstance(v, list):
                from_list(getattr(m, k), v)
            elif v is not None:
                try:
                    setattr(m, k, v)
                except TypeError as exc:
                    raise TypeError("%s: %s" % (k, str(exc)))

    from_dict(message, fields)
    return message


pb_serializers = {
    FieldDescriptor.TYPE_DOUBLE: float,
    FieldDescriptor.TYPE_FLOAT: float,
    FieldDescriptor.TYPE_INT32: int,
    FieldDescriptor.TYPE_INT64: long,
    FieldDescriptor.TYPE_UINT32: int,
    FieldDescriptor.TYPE_UINT64: long,
    FieldDescriptor.TYPE_SINT32: int,
    FieldDescriptor.TYPE_SINT64: long,
    FieldDescriptor.TYPE_FIXED32: int,
    FieldDescriptor.TYPE_FIXED64: long,
    FieldDescriptor.TYPE_SFIXED32: int,
    FieldDescriptor.TYPE_SFIXED64: long,
    FieldDescriptor.TYPE_BOOL: bool,
    FieldDescriptor.TYPE_STRING: str,
    FieldDescriptor.TYPE_BYTES: bytes,
    FieldDescriptor.TYPE_ENUM: int,
}


def pb_to_dict(message):
    """Convert a Protobuf message to a dict.

    Parameters
    ----------
    message : google.protobuf.message.Message
        The message to convert to a Python dict

    Returns
    -------
    dict
        A dictionary containing the data from the Protobuf message.

    """
    result = {}

    for k, v in message.ListFields():
        if k.type == FieldDescriptor.TYPE_MESSAGE:
            serializer = pb_to_dict
        elif k.type in pb_serializers:
            serializer = pb_serializers[k.type]
        else:
            serializer = str

        if k.label == FieldDescriptor.LABEL_REPEATED:
            result[k.name] = [serializer(i) for i in v]
        else:
            result[k.name] = serializer(v)

    return result

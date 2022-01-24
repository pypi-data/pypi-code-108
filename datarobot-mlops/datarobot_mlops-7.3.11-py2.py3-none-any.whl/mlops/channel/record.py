#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2021.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
import uuid

import binascii
import json
import struct

from datarobot.mlops.common.enums import DataFormat, DataType
from datarobot.mlops.common.exception import DRSpoolerException
from datarobot.mlops.constants import Constants

MLOPS_RECORD_VERSION = 2

# Serialize format for record header
SERIALIZE_FORMAT_RECORD_HEADER = "!I{}s5I{}sI{}sI{}s"
# Deserialize format for any string with its length
DESERIALIZE_FORMAT_STRING_LEN = "!I"
DESERIALIZE_FORMAT_STRING = "!{}s"
# Deserialize format for data type, data format, data len, version
DESERIALIZE_FORMAT_DATA_INFO = "!4I"


class RecordHeader(object):
    """
    Pack format rules:
    ! - network byte order (big-endian)
    I - unsigned int
    {}s - will be formatted with actual deployment id length
    e.g. 5s - 5 symbol string
    3I - three unsigned ints
    """

    def __init__(
            self,
            deployment_id,
            data_type,
            data_format,
            data_len,
            version=MLOPS_RECORD_VERSION,
            language="python",
            lib_version=Constants.MLOPS_VERSION,
            reserved="",
    ):
        self._id = str(uuid.uuid4())
        self._deployment_id = deployment_id
        self._data_type = data_type
        self._data_format = data_format
        self._data_len = data_len
        self._version = version
        self._language = language
        self._lib_version = lib_version
        self._reserved = reserved

    def serialize(self):
        deployment_id_len = len(self._deployment_id)
        language_len = len(self._language)
        lib_version_len = len(self._lib_version)
        reserved_len = len(self._reserved)
        pack_struct = struct.Struct(
            SERIALIZE_FORMAT_RECORD_HEADER.format(
                deployment_id_len, language_len, lib_version_len, reserved_len
            )
        )
        buf = bytearray(pack_struct.size)

        pack_struct.pack_into(
            buf,
            0,
            deployment_id_len,
            self._deployment_id.encode("utf8"),
            self._data_type.ordinal(),
            self._data_format.ordinal(),
            self._data_len,
            self._version,
            language_len,
            self._language.encode("utf8"),
            lib_version_len,
            self._lib_version.encode("utf8"),
            reserved_len,
            self._reserved.encode("utf8"),
        )
        return buf

    def to_json(self):
        content = {
            "id": self._id,
            "deploymentId": self._deployment_id,
            "dataType": self._data_type.name,
            "dataFormat": self._data_format.name.lower(),
            "dataLen": self._data_len,
            "version": self._version,
            "language": self._language,
            "libVersion": self._lib_version,
            "reserved": self._reserved,
        }
        return content

    def equals(self, obj):
        if not isinstance(obj, RecordHeader):
            return False
        if self._deployment_id != obj._deployment_id:
            return False
        if self._data_len != obj._data_len:
            return False
        if self._data_format != obj._data_format:
            return False
        if self._data_type != obj._data_type:
            return False
        if self._version != obj._version:
            return False
        if self._lib_version != obj._lib_version:
            return False
        if self._language != obj._language:
            return False
        return True

    @classmethod
    def _get_string(cls, byte_array, offset):
        (string_length,) = struct.unpack_from(
            DESERIALIZE_FORMAT_STRING_LEN, byte_array, offset=offset
        )
        offset += struct.calcsize(DESERIALIZE_FORMAT_STRING_LEN)
        (string,) = struct.unpack_from(
            DESERIALIZE_FORMAT_STRING.format(string_length), byte_array, offset
        )
        offset += len(string)
        return string.decode("utf8"), offset

    @classmethod
    def deserialize(cls, byte_array):
        if not isinstance(byte_array, (bytearray, bytes)):
            raise ValueError("Record header is not a byte array")

        offset = 0
        deployment_id, offset = cls._get_string(byte_array, offset)

        (data_type, data_format, data_len, version) = struct.unpack_from(
            DESERIALIZE_FORMAT_DATA_INFO, byte_array, offset=offset
        )

        offset += struct.calcsize(DESERIALIZE_FORMAT_DATA_INFO)
        language, offset = cls._get_string(byte_array, offset)
        lib_version, offset = cls._get_string(byte_array, offset)
        reserved, offset = cls._get_string(byte_array, offset)

        return RecordHeader(
            deployment_id,
            DataType.from_ordinal(data_type),
            DataFormat.from_ordinal(data_format),
            data_len,
            version=version,
            language=language,
            lib_version=lib_version,
            reserved=reserved
        )

    def get_deployment_id(self):
        return self._deployment_id

    def get_data_type(self):
        return self._data_type

    def get_data_format(self):
        return self._data_format

    def get_data_len(self):
        return self._data_len

    def get_version(self):
        return self._version

    def get_language(self):
        return self._language

    def get_lib_version(self):
        return self._lib_version

    def get_reserved(self):
        return self._reserved

    def __str__(self):
        return "deployment-id: {}, data-format: {}, data-type: {}, payload-len: {}".format(
            self._deployment_id, self._data_format, self._data_type, self._data_len
        )


class Record(object):

    def __init__(
            self,
            deployment_id,
            data_type,
            data_format,
            payload,
            version=MLOPS_RECORD_VERSION,
            language="python",
            lib_version=Constants.MLOPS_VERSION,
            reserved=""
    ):
        if data_format == DataFormat.BYTE_ARRAY:
            isinstance(payload, (bytearray, bytes))
            data_len = len(payload)
        elif data_format == DataFormat.JSON:
            data_len = len(json.dumps(payload))
        else:
            raise DRSpoolerException("Record class does not support data format {}"
                                     .format(data_format))
        self._record_header = RecordHeader(
            deployment_id,
            data_type,
            data_format,
            data_len,
            version=version,
            language=language,
            lib_version=lib_version,
            reserved=reserved
        )

        self._payload = payload

    def serialize(self):
        if not isinstance(self._payload, (bytearray, bytes)):
            raise ValueError("Record payload is not in byte array format")

        return self._serialize_improved()

    # This serialize improves performance by 20-30%.
    # In this call record_header and record are serialized together.
    def _serialize_improved(self):
        # Record structure:
        # < record_header_len, deployment_id_len, deployment_id,
        #   data_type, data_format, data_len, version, language_len, language, lib_version_len,
        #   lib_version, reserved_len, reserved, payload >
        # Format: "!2I{}s5I{}sI{}sI{}sI{}s"

        deployment_id_len = len(self._record_header.get_deployment_id())
        language_len = len(self._record_header.get_language())
        lib_version_len = len(self._record_header.get_lib_version())
        reserved_len = len(self._record_header.get_reserved())

        record_header_len = struct.calcsize(DESERIALIZE_FORMAT_STRING_LEN) + deployment_id_len + \
            struct.calcsize(DESERIALIZE_FORMAT_DATA_INFO) + \
            struct.calcsize(DESERIALIZE_FORMAT_STRING_LEN) + language_len + \
            struct.calcsize(DESERIALIZE_FORMAT_STRING_LEN) + lib_version_len + \
            struct.calcsize(DESERIALIZE_FORMAT_STRING_LEN) + reserved_len

        record_format = "!2I{}s5I{}sI{}sI{}s{}s".format(
            deployment_id_len, language_len, lib_version_len, reserved_len, len(self._payload)
        )
        buf = bytearray(struct.calcsize(record_format))
        struct.pack_into(
            record_format,
            buf,
            0,
            record_header_len,
            deployment_id_len,
            self._record_header.get_deployment_id().encode("utf8"),
            self._record_header.get_data_type().ordinal(),
            self._record_header.get_data_format().ordinal(),
            self._record_header.get_data_len(),
            self._record_header.get_version(),
            language_len,
            self._record_header.get_language().encode("utf8"),
            lib_version_len,
            self._record_header.get_lib_version().encode("utf8"),
            reserved_len,
            self._record_header.get_reserved().encode("utf8"),
            bytes(self._payload)
        )

        return buf

    def to_json(self):
        content = {
            "header": self._record_header.to_json(),
            "data": json.dumps(self._payload)
        }
        return json.dumps(content)

    def equals(self, obj):
        if not isinstance(obj, Record):
            return False
        if not self._record_header.equals(obj._record_header):
            return False

        # Check payload content
        for key in self._payload.keys():
            if not self._payload[key] == obj._payload[key]:
                return False

        return True

    @classmethod
    def deserialize(cls, byte_array):
        if not isinstance(byte_array, (bytearray, bytes)):
            raise ValueError("Record data is not a byte array")

        offset = 0
        (record_header_len,) = struct.unpack_from(
            DESERIALIZE_FORMAT_STRING_LEN, byte_array, offset=offset
        )

        offset += struct.calcsize(DESERIALIZE_FORMAT_STRING_LEN)
        (record_header_bytearray,) = struct.unpack_from(
            "{}s".format(record_header_len), byte_array, offset=offset
        )

        record_header = RecordHeader.deserialize(record_header_bytearray)
        offset += record_header_len
        (payload_bytes_or_bytearray,) = struct.unpack_from(
            "{}s".format(record_header.get_data_len()), byte_array, offset=offset
        )

        return Record(
            record_header.get_deployment_id(),
            record_header.get_data_type(),
            record_header.get_data_format(),
            payload_bytes_or_bytearray,
            version=record_header.get_version(),
            language=record_header.get_language(),
            lib_version=record_header.get_lib_version(),
            reserved=record_header.get_reserved()
        )

    @classmethod
    def from_json(cls, content):
        json_format_record = json.loads(content)
        deployment_id = json_format_record["header"]["deploymentId"]
        data_type = DataType[json_format_record["header"]["dataType"]]
        data_format = DataFormat[json_format_record["header"]["dataFormat"].upper()]
        payload = json.loads(json_format_record["data"])
        version = json_format_record["header"]["version"]
        language = json_format_record["header"]["language"]
        lib_version = json_format_record["header"]["libVersion"]
        reserved = json_format_record["header"]["reserved"]
        return Record(
            deployment_id,
            data_type,
            data_format,
            payload,
            version=version,
            language=language,
            lib_version=lib_version,
            reserved=reserved
        )

    def get_deployment_id(self):
        return self._record_header.get_deployment_id()

    def get_payload(self):
        return self._payload

    def get_data_type(self):
        return self._record_header.get_data_type()

    def __str__(self):
        if isinstance(self._payload, (bytearray, bytes)):
            return "{}, payload: {}".format(
                self._record_header, binascii.hexlify(self._payload)
            )
        return "{}, payload: {}".format(self._record_header, self._payload)

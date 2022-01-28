from google.protobuf import json_format
import json
from io import BytesIO as StringIO
import os
import re
import struct
from .util import read_uint32, decode_str, unpack_uint8,\
    unpack_uint32, unpack_uint64, unpack_time, read_time, Time
import logging
from .profile_pb2 import Profile
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OP_MESSAGE_DATA = 0x02
OP_BAG_HEADER = 0x03
OP_INDEX_DATA = 0x04
OP_CHUNK = 0x05
OP_CHUNK_INFO = 0x06
OP_CONNECTION = 0x07


class Bag():
    def __init__(self, file_obj):
        self._file = file_obj
        self._file_size = 0
        self._version = {}
        self._bag_header = {}
        self._chunk = {}
        self._connection = []
        self._conns = {}
        self._max_topic_str_len = 0
        self._max_type_str_len = 0
        self._chunk_pos = []
        self._chunk_info = []

        self.profiling()
        self._file.close()

    def profiling(self):
        self._file.seek(0)
        self._read_version()
        self._read_bag_header()

        self._file.seek(self._bag_header['index_pos'])
        self._read_bag_connection()
        self._read_bag_chunk_info()
        self._file_size = self._file.tell()

        self._read_bag_chunk()

    @property
    def profile_json(self):
        return {
            'version': self._version,
            'bag_header': self._bag_header,
            'connection': self._connection,
            'meta': {
                'file_size': self._file_size,
            },
            'chunk': list(self._chunk.values()),
            'chunk_info': self._chunk_info,
        }

    @property
    def profile(self):
        p = self.profile_json
        return json_format.Parse(json.dumps(p), Profile())

    def _read_version(self):
        version_line = self._file.readline().rstrip().decode()
        matches = re.match("#ROS(.*) V(\d).(\d)", version_line)
        end = self._file.tell()
        version_type, major_version, minor_version = matches.groups()
        self._version = {
            'version_type': version_type,
            'major_version': major_version,
            'minor_version': minor_version,
            '_start': 0,
            '_end': end,
        }
        return

    def _read_bag_header(self):
        start = self._file.tell()
        header = self._read_header(self._file)
        end = self._file.tell()
        index_pos = unpack_uint64(header['index_pos'])
        chunk_count = unpack_uint32(header['chunk_count'])
        conn_count = unpack_uint32(header['conn_count'])
        encryptor = ""
        try:
            encryptor = decode_str(header['encryptor'])
        except Exception:
            pass

        self._bag_header = {
            'index_pos': index_pos,
            'chunk_count': chunk_count,
            'conn_count': conn_count,
            'encryptor': encryptor,
            '_start': start,
            '_end': end,
            '_op': OP_BAG_HEADER,
        }
        return

    def _read_bag_connection(self):
        for i in range(self._bag_header['conn_count']):
            start = self._file.tell()
            conn, topic, type_, md5sum, msg_def = self._read_connection(
                self._file)
            end = self._file.tell()
            self._connection.append({'conn': conn, 'topic': topic,
                                     'type': type_, 'md5sum': md5sum,
                                     'message_definition': msg_def,
                                     '_start': start,
                                     '_end': end, '_op': OP_CONNECTION})
            if conn not in self._conns:
                self._conns[conn] = {'conn': conn,
                                     'message_definition': msg_def,
                                     'type': type_}
            self._max_topic_str_len = max(self._max_topic_str_len, len(topic))
            self._max_type_str_len = max(self._max_type_str_len, len(type_))

        return

    def _read_connection(self, f):
        conn, topic = self._read_connection_header(f)
        type_, md5sum, msg_def, topic2 = self._read_connection_data(f)
        if topic is not None and topic2 is not None and topic != topic2:
            raise Exception()

        return (conn, topic, type_, md5sum, msg_def)

    def _read_connection_header(self, f):
        header = self._read_header(f)
        conn = unpack_uint32(header['conn'])
        topic = decode_str(header['topic'])
        return (conn, topic)

    def _read_connection_data(self, f):
        header = self._read_header(f)
        type_, md5sum, message_definition, topic = None, None, None, None
        if 'type' in header:
            type_ = decode_str(header['type'])
        if 'md5sum' in header:
            md5sum = decode_str(header['md5sum'])
        if 'message_definition' in header:
            message_definition = decode_str(header['message_definition'])
        if 'topic' in header:
            topic = decode_str(header['topic'])
        return (type_, md5sum, message_definition, topic)

    def _read_bag_chunk_info(self):
        for i in range(self._bag_header['chunk_count']):
            start = self._file.tell()
            header = self._read_header(self._file)
            chunk_pos = unpack_uint64(header['chunk_pos'])
            start_time = Time(*unpack_time(header['start_time']))
            end_time = Time(*unpack_time(header['end_time']))
            data_count = unpack_uint32(header['count'])
            ver = unpack_uint32(header['ver'])
            msg_count = []
            size = read_uint32(self._file)
            for i in range(data_count):
                conn = read_uint32(self._file)
                count = read_uint32(self._file)
                msg_count.append({'conn': conn, 'count': count})
            end = self._file.tell()
            c = {
                'chunk_pos': chunk_pos,
                'start_time': start_time,
                'end_time': end_time,
                'count': data_count,
                'ver': ver,
                'msg_count': msg_count,
                '_start': start,
                '_end': end,
                '_op': OP_CHUNK_INFO
            }
            self._chunk_info.append(c)
            self._chunk_pos.append(chunk_pos)
        self._chunk_pos.sort()

    def _read_bag_chunk(self):
        for pos in self._chunk_pos:
            self._file.seek(pos)
            c = {'_start': pos}

            # 1. read chunk header
            compression, compressed_size, op = self._read_chunk_header(
                self._file)
            chunk_header_end = self._file.tell()
            c['chunk_header'] = {
                '_start': pos,
                '_end': chunk_header_end,
                '_op': op,
                'compression': compression,
                'compressed_size': compressed_size
            }

            # 2. read chunk data
            chunk_data_start = chunk_header_end
            chunk_data = self._read_sized(self._file)
            # chunk_data_end = self._file.tell()
            # c['data'] = {
            #     '_start': chunk_header_end,
            #     # '_end': chunk_data_end,
            #     'connection': [],
            #     'message_data': [],
            # }

            # 3. read index data
            c['index_data'] = []
            offset_check_dict = {}
            while True:
                op = self._peek_next_header_op(self._file)
                if op != OP_INDEX_DATA:
                    break
                start = self._file.tell()
                ver, conn, count, offsets = self._read_index_data()
                end = self._file.tell()
                c['index_data'].append({
                    '_start': start,
                    '_end': end,
                    '_op': op,
                    'version': ver,
                    'conn': conn,
                    'count': count,
                    # 'offsets': offsets# this is measured from chunk_data_start + 4
                })
                for o in offsets:
                    offset_check_dict[o['offset']] = {
                        'conn': conn, 'time': o['time']}

            # re-read chunk_data, exclude first 4 bit
            c['connection'] = []
            c['message_data'] = []
            chunk_data_io = StringIO(chunk_data)

            offset = chunk_data_io.tell()
            while offset < compressed_size:
                # a safe approach to read chunk data
                # avoid bug when connection is not correctly written
                op = self._peek_next_header_op(chunk_data_io)

                if op == OP_CONNECTION:
                    start = chunk_data_io.tell()
                    conn, topic, t, md5sum, msg_def = self._read_connection(
                        chunk_data_io)
                    end = chunk_data_io.tell()
                    c['connection'].append({
                        '_start': start + chunk_data_start+4,
                        '_end': end + chunk_data_start+4,
                        '_op': op,
                        'conn': conn,
                        'topic': topic,
                        'type': t,
                        'md5sum': md5sum,
                        # 'message_definition': msg_def
                    })
                elif op == OP_MESSAGE_DATA:
                    start = chunk_data_io.tell()
                    conn, time, op = self._read_message_data_header(
                        chunk_data_io)

                    # check if message data in chunk_data match
                    # those offsets in index data
                    # if not, bag reindex is usually needed
                    if start not in offset_check_dict:
                        raise Exception('index mismatch: data at %d(offset % d) is missing. Need reindex.' % (
                            start + chunk_data_start+4, start))
                    elif conn != offset_check_dict[start]['conn']:
                        raise Exception('conn mismatch: %d != %d. Need reindex.' % (
                            conn, offset_check_dict[start]['conn']))
                    elif str(time) != str(offset_check_dict[start]['time']):
                        raise Exception('time mismatch: %s != %s. Need reindex.' % (
                            time, offset_check_dict[start]['time']))

                    self._skip_sized(chunk_data_io)
                    end = chunk_data_io.tell()

                    c['message_data'].append({
                        '_start': start + chunk_data_start+4,
                        '_end': end + chunk_data_start+4,
                        '_op': op,
                        'time': time,
                        'conn': conn,
                    })

                elif op is None:
                    self._skip_record(chunk_data_io)
                offset = chunk_data_io.tell()

            c['_end'] = self._file.tell()
            self._chunk[pos] = c

    def _read_header(self, f):
        header = self._read_sized(f)
        _dict = {}
        while header != b'':
            (size,) = struct.unpack('<L', header[:4])
            header = header[4:]

            (name, sep, value) = header[:size].partition(b'=')
            name = name.decode()
            _dict[name] = value

            header = header[size:]

        return _dict

    def _read_chunk_header(self, f):
        header = self._read_header(f)
        compression = decode_str(header['compression'])
        if compression != "none":
            raise Exception()
        compressed_size = unpack_uint32(header['size'])
        op = unpack_uint8(header['op'])
        return (compression, compressed_size, op)

    def _read_message_data_header(self, f):
        header = self._read_header(f)
        conn = unpack_uint32(header['conn'])
        time = Time(*unpack_time(header['time']))
        op = unpack_uint8(header['op'])
        return (conn, time, op)

    def _read_sized(self, f):
        size = read_uint32(f)
        return f.read(size)

    def _skip_sized(self, f):
        size = read_uint32(f)
        f.seek(size, os.SEEK_CUR)

    def _skip_record(self, f):
        # skip header
        self._skip_sized(f)
        # skip data
        self._skip_sized(f)

    def _peek_next_header_op(self, f):
        pos = f.tell()
        # avoid empty record error
        try:
            header = self._read_header(f)
            op = unpack_uint8(header['op'])
        except Exception:
            op = None
        f.seek(pos)
        return op

    def _read_index_data(self):
        header = self._read_header(self._file)
        ver = unpack_uint32(header['ver'])
        conn = unpack_uint32(header['conn'])
        count = unpack_uint32(header['count'])
        read_uint32(self._file)
        offsets = []
        for i in range(count):
            time = read_time(self._file)
            offset = read_uint32(self._file)
            offsets.append({'time': time, 'offset': offset})

        offsets.sort(key=lambda x: x['offset'])
        return (ver, conn, count, offsets)

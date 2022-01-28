import io
import json
import warnings
import zlib
from typing import Union

import avro.io
import avro.datafile
import avro.schema
import numpy

warnings.filterwarnings('ignore', category=DeprecationWarning, module='avro')


class BinaryEncoder(avro.io.BinaryEncoder):
    def write_float(self, datum):
        # A `numpy.float32` will call this function and be stored as
        # 4-byte `float` of `C`.
        assert type(datum) is numpy.float32
        super().write_float(datum)

    def write_double(self, datum):
        assert type(datum) is float or type(datum) is numpy.float64
        super().write_double(datum)

    def write_int(self, datum):
        # Although Python `int` has unlimited bits,
        # we'll treat it as `int` of `C`, i.e. 4 bytes.
        # If you know the numbers can be large, use `numpy.int64`,
        # which will be treated as `long` of `C`.
        # This `int` is the common `int32`.
        #
        # Python `int` and `numpy.int32` will call this function and be stored
        # as 4-byte `int` of `C`.
        assert type(datum) is int or type(datum) is numpy.int32
        assert -2147483648 < datum < 2147483647
        datum = (datum << 1) ^ (datum >> 31)
        while (datum & ~0x7f) != 0:
            self.WriteByte((datum & 0x7f) | 0x80)
            datum >>= 7
        self.WriteByte(datum)

    def write_long(self, datum):
        super().write_long(datum)


class DatumWriter(avro.io.DatumWriter):
    def write(self, datum, encoder):
        # skip schema validation
        self.write_data(self.writer_schema, datum, encoder)

    def write_fixed(self, writer_schema, datum, encoder):
        if not isinstance(datum, bytes):
            datum = datum.tobytes()  # works if `datum` is a Numpy object
        super().write_fixed(writer_schema, datum, encoder)


class DataFileWriter(avro.datafile.DataFileWriter):
    def __init__(self, writer, writer_schema=None, codec='null'):
        if isinstance(writer_schema, dict):
            writer_schema = json.dumps(writer_schema)
        if isinstance(writer_schema, str):
            writer_schema = avro.schema.Parse(writer_schema)
        datum_writer = DatumWriter()
        super().__init__(writer, datum_writer, writer_schema, codec)
        self._encoder = BinaryEncoder(writer)
        self._buffer_encoder = BinaryEncoder(self._buffer_writer)


class BinaryDecoder(avro.io.BinaryDecoder):
    # `read_double` will read into Python `float`.

    def read_float(self):
        return numpy.float32(super().read_float())

    # `read_int` and `read_long` will both read into Python `int`.
    # The resultant number will then be put into `numpy` if
    # the schema specifies `pytype` as `numpy`.


class DatumReader(avro.io.DatumReader):
    def read_data(self, writer_schema, reader_schema, decoder):
        z = super().read_data(writer_schema, reader_schema, decoder)
        if writer_schema.props.get('pytype', None) == 'numpy':
            if writer_schema.type == 'long':
                z = numpy.int64(z)
            elif writer_schema.type == 'int':
                z = numpy.int32(z)
            elif writer_schema.type == 'double':
                z = numpy.float64(z)
            elif writer_schema.type == 'float':
                z = numpy.float32(z)
            elif writer_schema.type == 'array':
                z = numpy.array(z)
            elif writer_schema.type == 'fixed':
                assert type(z) is bytes
                dtype = numpy.dtype(writer_schema.props['logical_type'])
                z = numpy.frombuffer(z, dtype)[0]
        return z


class DataFileReader(avro.datafile.DataFileReader):
    def __init__(self, reader):
        # Same as superclass, except for replacing `avro.io.BinaryDecoder`
        # by `BinaryDecoder` (the custom version above).

        self._reader = reader
        self._raw_decoder = BinaryDecoder(reader)
        self._datum_decoder = None  # Maybe reset at every block.
        self._datum_reader = DatumReader()

        # read the header: magic, meta, sync
        self._read_header()

        # ensure codec is valid
        avro_codec_raw = self.GetMeta('avro.codec')
        if avro_codec_raw is None:
            self.codec = "null"
        else:
            self.codec = avro_codec_raw.decode('utf-8')
        if self.codec not in avro.datafile.VALID_CODECS:
            raise avro.datafile.DataFileException(
                'Unknown codec: %s.' % self.codec)

        self._file_length = self._GetInputFileLength()

        # get ready to read
        self._block_count = 0
        self.datum_reader.writer_schema = (avro.schema.Parse(
            self.GetMeta(avro.datafile.SCHEMA_KEY).decode('utf-8')))

    def _read_block_header(self):
        # Replace `avro_io.BinaryDecoder` in original implementation
        # by `BinaryDecoder` (our custom version above).
        # No other changes.

        self._block_count = self.raw_decoder.read_long()
        if self.codec == "null":
            # Skip a long; we don't need to use the length.
            self.raw_decoder.skip_long()
            self._datum_decoder = self._raw_decoder
        elif self.codec == 'deflate':
            # Compressed data is stored as (length, data), which
            # corresponds to how the "bytes" type is encoded.
            data = self.raw_decoder.read_bytes()
            # -15 is the log of the window size; negative indicates
            # "raw" (no zlib headers) decompression.  See zlib.h.
            uncompressed = zlib.decompress(data, -15)
            self._datum_decoder = BinaryDecoder(io.BytesIO(uncompressed))
        elif self.codec == 'snappy':
            import snappy  # Import here b/c we don't expect this to be used.

            # Compressed data includes a 4-byte CRC32 checksum
            length = self.raw_decoder.read_long()
            data = self.raw_decoder.read(length - 4)
            uncompressed = snappy.decompress(data)
            self._datum_decoder = BinaryDecoder(io.BytesIO(uncompressed))
            self.raw_decoder.check_crc32(uncompressed)
        else:
            raise avro.datafile.DataFileException(
                "Unknown codec: %r" % self.codec)


def _make_schema(x, name: str) -> Union[str, dict]:
    assert isinstance(name, str)

    if isinstance(x, numpy.float32):
        return {'name': name, 'type': 'float', 'pytype': 'numpy'}
    if isinstance(x, numpy.float64):
        return {'name': name, 'type': 'double', 'pytype': 'numpy'}
    if isinstance(x, numpy.int32):
        return {'name': name, 'type': 'int', 'pytype': 'numpy'}
    if isinstance(x, numpy.int64):
        return {'name': name, 'type': 'long', 'pytype': 'numpy'}
    if isinstance(x, (numpy.int8, numpy.int16, numpy.uint8, numpy.uint16,
                      numpy.uint32, numpy.uint64)):
        return {
            'name': name,
            'type': 'fixed',
            'size': x.itemsize,
            'pytype': 'numpy',
            'logical_type': x.dtype.name
        }
    if isinstance(x, numpy.ndarray):
        assert len(
            x.shape
        ) == 1, ("Multi-dimensional Numpy arrays are not supported. "
                 "Please convert to a 1-D Numpy array "
                 "and store it dimensionality info as another datum")
        z = _make_schema(x.dtype.type(), name + '_item')
        return {'name': name, 'type': 'array', 'items': z, 'pytype': 'numpy'}

    if isinstance(x, int):
        return {'name': name, 'type': "int"}
    if isinstance(x, float):
        return {'name': name, 'type': 'double'}
    if isinstance(x, str):
        return {'name': name, 'type': 'string'}
    if isinstance(x, dict):
        fields = []
        for key, val in x.items():
            z = _make_schema(val, key)
            if len(z) < 3:
                fields.append(z)
            else:
                fields.append({'name': key, 'type': z})
        return {'name': name, 'type': 'record', 'fields': fields}
    if isinstance(x, list):
        assert len(x) > 0, \
                ("empty list is not supported, "
                 "because its type can not be inferred")
        z0 = _make_schema(x[0], name + '_item')
        if len(x) > 1:
            for v in x[1:]:
                z1 = _make_schema(v, name + '_item')
                assert z1 == z0, \
                    'schema for x[0] ({}): {}; schema for x[?] ({}): {}'.format(  # noqa: E501
                        x[0], z0, v, z1)
        if len(z0) < 3:
            items = z0['type']
        else:
            items = z0
        return {'name': name, 'type': 'array', 'items': items}

    raise Exception('unrecognized value of type "' + type(x).__name__ + '"')


def make_schema(value, name: str,
                namespace: str) -> str:
    '''
    `value` is a `dict` whose members are either 'simple types' or 'compound types'.

    'simple types' include:
        int, float, str (python types)
        numpy.{int8, int16, int32, int64, uint8, uint16, uint32, uint64, float32, float64}  (numpy types)  # noqa: E501

    'compound types' include:
        dict: whose elements are simple or compound types
        list: whose elements are all the same simple or compound type
        numpy.ndarray: must be 1-d, with `dtype` being one of the numpy 'simple' type.  # noqa: E501
    '''
    sch = {'namespace': namespace, **_make_schema(value, name)}
    return json.dumps(sch)


# Using `DataFileWriter` instead of the barebone `DatumWriter`,
# the schema is included in the resultant byte array.
def dump_bytes(value,
               name: str,
               namespace: str) -> bytes:
    schema = make_schema(value, name, namespace)
    buffer = io.BytesIO()
    with DataFileWriter(buffer, schema) as writer:
        writer.append(value)
        writer.flush()
        buffer.seek(0)
        return buffer.getvalue()


def load_bytes(b: bytes, return_schema=False):
    with DataFileReader(io.BytesIO(b)) as reader:
        # We know the stream contains only one record.
        value = list(reader)
        if len(value) == 1:
            value = value[0]
        if return_schema:
            schema = reader.meta['avro.schema'].decode()
            return value, schema
        return value

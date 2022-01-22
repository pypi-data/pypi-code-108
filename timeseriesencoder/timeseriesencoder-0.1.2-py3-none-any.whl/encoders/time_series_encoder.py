
import ciso8601
from .numeric_encoder import NumericEncoder
import numpy as np
import datetime
from copy import deepcopy
import gzip
import base64
import json
from numpyencoder import NumpyEncoder

__all__ = ['TimeSeriesEncoder']

def precision_and_scale_np(x, max_magnitude):
    max_magnitude = max(max_magnitude, 1)
    int_part = np.abs(x).astype(np.uint64)
    magnitudes = np.ones_like(int_part)
    magnitudes[int_part != 0] = np.log10(int_part[int_part != 0]) + 1
   
    frac_part = np.abs(x) - int_part
    multiplier = 10 ** (max_magnitude - magnitudes)
    frac_digits = multiplier + (multiplier * frac_part + 0.5).astype(np.uint64)

    while np.any(frac_digits % 10 == 0):
        frac_digits[frac_digits % 10 == 0] = frac_digits[frac_digits % 10 == 0] / 10
    scale = np.log10(frac_digits).astype(np.uint64)
    return np.max(scale)

class TimeSeriesEncoder:
    regular = False

    @staticmethod
    def gzip_str(string_: str) -> bytes:
        return gzip.compress(string_.encode())

    @staticmethod
    def gunzip_bytes_obj(bytes_obj: bytes) -> str:
        return gzip.decompress(bytes_obj).decode()

    @staticmethod
    def get_character_set(encoding_size):
        # Check encoding size
        if encoding_size == 16:
            character_set = NumericEncoder.get_base_16()
        elif encoding_size == 64:
            character_set = NumericEncoder.get_base_64()
        elif encoding_size == 91:
            character_set = NumericEncoder.get_base_91()
        else:
            raise ValueError(f'Unsupported encoding size: {encoding_size}, currently we only support base 16, 64, and 90.')
        return character_set

    @staticmethod
    def encode_json(json_data, ts_key, ts_value, sort_values = False, encoding_size = 64, inplace=False, gzip=False):
        if inplace == False:
            json_data = deepcopy(json_data)
        encoded = TimeSeriesEncoder._encode_json(json_data, ts_key, ts_value, sort_values, encoding_size)

        if gzip:
            jstr = json.dumps(encoded, cls=NumpyEncoder)
            bytes = TimeSeriesEncoder.gzip_str(jstr)
            b64bytes = base64.b64encode(bytes)
            encoded = b64bytes.decode("utf-8")
        return encoded
            
    @staticmethod
    def decode_json(json_data, inplace=False, gzip=False):
        if gzip:
            b = base64.b64decode(json_data)
            json_data = TimeSeriesEncoder.gunzip_bytes_obj(b)
            json_data = json.loads(json_data)

        if inplace == False:
            json_data = deepcopy(json_data)
        decoded = TimeSeriesEncoder._decode_json(json_data)
        return decoded

    @staticmethod
    def _encode_json(json_data, ts_key, ts_value, sort_values = False, encoding_size = 64):
        if type(json_data) == dict:
            for key in json_data:
                json_data[key] = TimeSeriesEncoder._encode_json(json_data[key], ts_key, ts_value, sort_values, encoding_size)
            return json_data
        elif type(json_data) == list:
            is_ts = False
            expected_keys = set([ts_key, ts_value])
            for item in json_data:
                if type(item) == dict:
                    if expected_keys == set(item.keys()):
                        is_ts = True
                else:
                    is_ts = False
                
            if is_ts == False:
                for i, j in enumerate(json_data):
                    json_data[i] = TimeSeriesEncoder._encode_json(j, ts_key, ts_value, sort_values, encoding_size)
            else:
                if sort_values:
                    json_data.sort(key = lambda x: x[ts_key])

                encoder = TimeSeriesEncoder(json_data, encoding_size = encoding_size)

                # Add encoded information to the json
                json_data = {
                    "encoder" : "TimeSeriesEncoder",
                    "start" : encoder.start,
                    "ts_key": ts_key,
                    "ts_value": ts_value,
                    "encoding_size": encoding_size,
                    "data" : encoder.encode(json_data)
                }

                # Add encoding metadata for decoding later
                if encoder.regular:
                    json_data['interval'] = encoder.interval
                else:
                    json_data['time_encoding_depth'] = encoder.timeEncoder.encoding_depth
                
                if encoder.static is not None:
                    json_data['static_value'] = encoder.static['value']
                    json_data['static_count'] = encoder.static['count']
                    
                    if encoder.regular:
                        del json_data['data']
                        del json_data['encoding_size']
                else:
                    json_data["encoding_depth"] = encoder.encoder.encoding_depth
                    json_data["float_precision"] = encoder.encoder.float_precision
                    json_data["signed"] = encoder.encoder.signed
            
            return json_data
        else:
            return json_data

    @staticmethod
    def _decode_json(json_data):
        if type(json_data) != dict:
            if type(json_data) == list:
                for i, j in enumerate(json_data):
                    json_data[i] = TimeSeriesEncoder._decode_json(j)
            return json_data
        else:
            encoded_ts = False
            if 'encoder' in json_data:
                if json_data['encoder'] == 'TimeSeriesEncoder':
                    encoded_ts = True
                    
            if encoded_ts == False:
                for k in json_data:
                    json_data[k] = TimeSeriesEncoder._decode_json(json_data[k])
                return json_data
            else:
                encoder = TimeSeriesEncoder()
                encoder.start = json_data['start']
                encoder.ts_key = json_data['ts_key']
                encoder.ts_value = json_data['ts_value']

                if 'static_value' not in json_data:
                    character_set = TimeSeriesEncoder.get_character_set(json_data['encoding_size'])
                    encoder.signed = json_data['signed']
                    if json_data['float_precision'] == 0:
                        numeric_type = 'int'
                    else:
                        numeric_type = 'float'

                    encoder.encoder = NumericEncoder(encoding_depth = json_data['encoding_depth'], signed=json_data['signed'], numeric_type=numeric_type, float_precision=json_data['float_precision'], character_set = character_set)
                else:
                    encoder.static = { 'value' : json_data['static_value'], 'count' : json_data['static_count']}

                if 'time_encoding_depth' in json_data:
                    character_set = TimeSeriesEncoder.get_character_set(json_data['encoding_size'])
                    encoder.timeEncoder = NumericEncoder(encoding_depth = json_data['time_encoding_depth'], signed=False, numeric_type='int', character_set = character_set)
                    encoder.regular = False
                else:
                    encoder.regular = True
                    encoder.interval = json_data['interval']

                if 'data' in json_data:
                    json_data = encoder.decode(json_data['data'])
                else:
                    json_data = encoder.decode()
                return json_data


    def __init__(self, timeseries = None, encoding_size = 64):
        # Save raw timeseries
        self.timeseries = timeseries
        self.encoding_size = encoding_size
        self.ts_key = 'UTC'
        self.ts_value = 'Value'
        self.static = None

        if timeseries is not None:
            # Check encoding size
            character_set = TimeSeriesEncoder.get_character_set(encoding_size)

            # Create the optimal encoder
            self.np_timeseries = self.get_np_timeseries(timeseries)
            self.start = np.min(self.np_timeseries[0, 0])

            # Determine regularity of data
            gaps = np.diff(self.np_timeseries[:, 0], axis=0)
            if np.all(gaps == gaps[0]):
                # Series is regular
                self.regular = True
                self.interval = gaps[0]
            else:
                self.regular = False
                offsets = self.np_timeseries[:, 0] - self.start
                largest_offset = np.max(offsets)

                timebitsize = 0
                while largest_offset >= 1:
                    largest_offset /= encoding_size
                    timebitsize += 1

            # Determine value bounds
            values = self.np_timeseries[:, 1]
            max_value = np.max(values)
            min_value = np.min(values)

            # Determine data precision
            longest_input_length = len(values.astype(np.str_)[np.argmax(values.astype(np.str_))])
            maximum_precision = precision_and_scale_np(values, longest_input_length)

            max_value = max(abs(max_value), abs(min_value))

            signed = False
            if min_value < 0:
                signed = True
                max_value *= 2

            if maximum_precision == 0:
                numeric_type = 'int'
            else:
                numeric_type = 'float'
                max_value *= 10 ** maximum_precision

            valuebitsize = 0
            while max_value >= 1:
                max_value /= encoding_size
                valuebitsize += 1

            # Create encoders
            if self.regular == False:
                self.timeEncoder = NumericEncoder(encoding_depth = timebitsize, signed=False, numeric_type='int', character_set = character_set)

            if valuebitsize != 0:
                self.encoder = NumericEncoder(encoding_depth = valuebitsize, signed=signed, numeric_type=numeric_type, float_precision=maximum_precision, character_set = character_set)
            else:
                self.static = {}
                self.static['value'] = max_value
                self.static['count'] = self.np_timeseries.shape[0]

    def get_np_timeseries(self, timeseries):
        raw = np.zeros((len(timeseries), 2))
        for i, k in enumerate(timeseries):
            unix_time = ciso8601.parse_datetime(k['UTC']).timestamp()
            raw[i][0] = unix_time
            raw[i][1] = k['Value']
        return raw

    def encode(self, timeseries):
        raw = self.get_np_timeseries(timeseries)
        encoded = None

        if self.regular == False:
            data = np.copy(raw)
            data[:, 0] = data[:, 0] - self.start

            encoded_time = self.timeEncoder.encode(data[:, 0])
            if self.static is None:
                encoded_data = self.encoder.encode(raw[:, 1])

                # Zip together the two encodings
                encoded = ''
                encoded_length = len(encoded_time)+len(encoded_data)
                word_size = self.timeEncoder.encoding_depth + self.encoder.encoding_depth
                for idx, s in enumerate(range(0, encoded_length, word_size)):
                    encoded_time_byte = encoded_time[idx*self.timeEncoder.encoding_depth:(idx+1)*self.timeEncoder.encoding_depth]
                    encoded_data_byte = encoded_data[idx*self.encoder.encoding_depth:(idx+1)*self.encoder.encoding_depth]
                    encoded = encoded + encoded_time_byte + encoded_data_byte
            else:
                encoded = encoded_time
        else:
            if self.static is None:
                encoded_data = self.encoder.encode(raw[:, 1])
                encoded = encoded_data

        return encoded or ''


    def __decode_regular(self, data, time_index):
        decoded = self.encoder.decode(data)
        json_values = [''] * len(decoded)
        for i, datum in enumerate(decoded):
            utc = datetime.datetime.utcfromtimestamp(time_index)
            json_values[i] = {
                self.ts_key: '%02d-%02d-%02dT%02d:%02d:%02dZ' % (utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second),
                self.ts_value : datum
            }
            time_index += self.interval
        return json_values

    def __decode_regular_static(self, time_index):
        json_values = [''] * self.static['count']
        for d in range(0, self.static['count']):
            utc = datetime.datetime.utcfromtimestamp(time_index)
            json_values[d] = {
                self.ts_key: '%02d-%02d-%02dT%02d:%02d:%02dZ' % (utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second),
                self.ts_value : self.static['value']
            }
            time_index += self.interval
        return json_values

    def __decode_nonregular_static(self, data):
        decoded = self.timeEncoder.decode(data)
        json_values = [''] * len(decoded)
        for i, datum in enumerate(decoded):
            timestamp = datum + self.start
            utc = datetime.datetime.utcfromtimestamp(timestamp)
            json_values[i] = {
                self.ts_key: '%02d-%02d-%02dT%02d:%02d:%02dZ' % (utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second),
                self.ts_value : self.static['value']
            }
        return json_values

    def __decode_nonregular(self, data):
        wordsize = self.timeEncoder.encoding_depth + self.encoder.encoding_depth
        offsets = ''
        words = ''
        for idx in range(0, len(data), wordsize):
            offsets += data[idx:idx+self.timeEncoder.encoding_depth]
            words += data[idx+self.timeEncoder.encoding_depth:idx+wordsize]

        decoded_offsets = self.timeEncoder.decode(offsets)
        decoded_words = self.encoder.decode(words)

        json_values = [''] * len(decoded_words)
        for i, (o, w) in enumerate(zip(decoded_offsets, decoded_words)):
            timestamp = o + self.start
            utc = datetime.datetime.utcfromtimestamp(timestamp)
            json_values[i] = {
                self.ts_key: '%02d-%02d-%02dT%02d:%02d:%02dZ' % (utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second),
                self.ts_value : w
            }
        return json_values

    def decode(self, data = None):
        if self.regular == True:
            if self.static is None:
                json_values = self.__decode_regular(data, self.start)
            else:
                json_values = self.__decode_regular_static(self.start)
        else:
            if self.static is None:
                json_values = self.__decode_nonregular(data)
            else:
                json_values = self.__decode_nonregular_static(data)
        return json_values

if __name__ == '__main__':
    pass
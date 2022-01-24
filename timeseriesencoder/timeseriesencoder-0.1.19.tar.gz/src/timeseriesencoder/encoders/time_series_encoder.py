
import copy
import ciso8601
from .numeric_encoder import NumericEncoder
import numpy as np
import datetime
import gzip
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
    def encode_json(json_data, ts_key, ts_value, sort_values = False, encoding_size = 64, inplace=False, gzip=False):
        if inplace == False:
            json_data = copy.copy(json_data)
        encoded = TimeSeriesEncoder._encode_json(json_data, ts_key, ts_value, sort_values, encoding_size)
        if gzip:
            jstr = json.dumps(encoded, cls=NumpyEncoder)
            bytes = TimeSeriesEncoder.gzip_str(jstr)
            return bytes
        return encoded


    @staticmethod
    def encode_csv(csv, time_column, key_columns, sort_values = False, encoding_size = 64, gzip=False):
        return csv

    @staticmethod
    def decode_csv(encoded_data, gzip=False):
        return encoded_data
            
    @staticmethod
    def decode_json(json_data, inplace=False, gzip=False):
        if gzip:
            json_data = TimeSeriesEncoder.gunzip_bytes_obj(json_data)
            json_data = json.loads(json_data)

        if inplace == False and gzip == False:
            json_data = copy.copy(json_data)
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
                encoder = TimeSeriesEncoder(json_data, ts_key=ts_key, ts_value=ts_value, sort_values=sort_values, encoding_size = encoding_size)
                encoded_json = TimeSeriesEncoder.serialize(encoder)
                encoded_data = encoder.encode(json_data)
                if len(encoded_data) > 0:
                    encoded_json["data"] = encoded_data
                json_data = encoded_json
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
            if 'encoding_start' in json_data:
                encoded_ts = True
                    
            if encoded_ts == False:
                for k in json_data:
                    json_data[k] = TimeSeriesEncoder._decode_json(json_data[k])
                return json_data
            else:
                encoder = TimeSeriesEncoder.deserialize(json_data)
                if 'data' in json_data:
                    json_data = encoder.decode(json_data['data'])
                else:
                    json_data = encoder.decode()
                return json_data


    def __init__(self, timeseries = None, ts_key='UTC', ts_value='Value', sort_values=False, encoding_size = 64):
        # Save raw timeseries
        self.timeseries = timeseries
        self.encoding_size = encoding_size
        self.ts_key = ts_key
        self.ts_value = ts_value
        self.sort_values = sort_values
        self.static = None

        if timeseries is not None:
            # Create the optimal encoder
            self.np_timeseries = self.get_np_timeseries(timeseries)
            self.encoding_start = np.min(self.np_timeseries[0, 0])

            # Determine regularity of data
            gaps = np.diff(self.np_timeseries[:, 0], axis=0)
            if np.all(gaps == gaps[0]):
                # Series is regular
                self.regular = True
                self.interval = gaps[0]
            else:
                self.regular = False
                offsets = self.np_timeseries[:, 0] - self.encoding_start
                largest_offset = np.max(offsets)

                timebitsize = 0
                while largest_offset >= 1:
                    largest_offset /= encoding_size
                    timebitsize += 1
                
                self.timeEncoder = NumericEncoder(encoding_depth = timebitsize, signed=False, numeric_type='int', encoding_size=encoding_size)

            # Determine value bounds
            values = self.np_timeseries[:, 1]

            # Determine data precision
            if np.std(values) == 0:
                # Series is static
                self.static = {}
                self.static['value'] = values[0].item()
                self.static['count'] = self.np_timeseries.shape[0]
            else:
                # Determine data precision
                longest_input_length = len(values.astype(np.str_)[np.argmax(values.astype(np.str_))])
                maximum_precision = precision_and_scale_np(values, longest_input_length)

                max_value = np.max(values)
                min_value = np.min(values)

                max_value = max(abs(max_value), abs(min_value))

                if maximum_precision == 0:
                    numeric_type = 'int'
                else:
                    numeric_type = 'float'
                    max_value *= 10 ** maximum_precision

                signed = False
                if min_value < 0:
                    signed = True
                    max_value *= 2

                valuebitsize = 0
                while max_value >= 1:
                    max_value /= encoding_size
                    valuebitsize += 1

                if valuebitsize != 0:
                    self.encoder = NumericEncoder(encoding_depth = valuebitsize, signed=signed, numeric_type=numeric_type, float_precision=maximum_precision, encoding_size=encoding_size)


    def get_np_timeseries(self, timeseries):
        raw = np.zeros((len(timeseries), 2))
        for i, k in enumerate(timeseries):
            unix_time = ciso8601.parse_datetime(k['UTC']).timestamp()
            raw[i][0] = unix_time
            raw[i][1] = k['Value']

        if self.sort_values:
            raw = raw[raw[:, 0].argsort()]
        return raw

    def encode(self, timeseries):
        raw = self.get_np_timeseries(timeseries)
        encoded = None

        if self.regular == False:
            data = np.copy(raw)
            if self.sort_values:
                data[:, 0] = np.insert(np.diff(data[:, 0], axis=0), 0, 0)
            else:
                data[:, 0] = data[:, 0] - self.encoding_start

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
            timestamp = datum + self.encoding_start
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
            timestamp = o + self.encoding_start
            utc = datetime.datetime.utcfromtimestamp(timestamp)
            json_values[i] = {
                self.ts_key: '%02d-%02d-%02dT%02d:%02d:%02dZ' % (utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second),
                self.ts_value : w
            }
        return json_values

    def decode(self, data = None):
        if self.regular == True:
            if self.static is None:
                json_values = self.__decode_regular(data, self.encoding_start)
            else:
                json_values = self.__decode_regular_static(self.encoding_start)
        else:
            if self.static is None:
                json_values = self.__decode_nonregular(data)
            else:
                json_values = self.__decode_nonregular_static(data)
        return json_values

    @staticmethod
    def serialize(tse):
        vsl = copy.copy(tse.__dict__)
        defaults = {
            "static" : None,
            "regular" : True,
            "encoding_size": 64,
            "sort_values": True
        }

        if "timeseries" in vsl:
            del vsl["timeseries"]
        if "np_timeseries" in vsl:
            del vsl["np_timeseries"]
        if "encoder" in vsl:
            vsl["encoder"] = NumericEncoder.serialize(vsl["encoder"])
        if "timeEncoder" in vsl:
            vsl["timeEncoder"] = NumericEncoder.serialize(vsl["timeEncoder"])

        for key in defaults:
            if vsl[key] == defaults[key]:
                del vsl[key]
        return vsl

    @staticmethod
    def deserialize(msg):
        defaults = {
            "static" : None,
            "encoding_size": 64,
            "sort_values": True
        }
        
        for key in defaults:
            msg[key] = msg.get(key) or defaults[key]

        tse = TimeSeriesEncoder()
        for key in msg:
            tse.__dict__[key] = msg[key]

        tse.regular = ("interval" in msg)

        if "encoder" in msg:
            tse.encoder = NumericEncoder.deserialize(msg["encoder"])
        if "timeEncoder" in msg:
            tse.timeEncoder = NumericEncoder.deserialize(msg["timeEncoder"])
        return tse

if __name__ == '__main__':
    pass
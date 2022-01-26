
import copy
from io import StringIO
import ciso8601
from .numeric_encoder import NumericEncoder
import numpy as np
import datetime
import gzip
import json
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from numpyencoder import NumpyEncoder

__all__ = ['TimeSeriesEncoder', 'JSONEncoder', 'CSVEncoder']

class EncoderHelpers:
    @staticmethod
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

    @staticmethod
    def gzip_str(string_: str) -> bytes:
        return gzip.compress(string_.encode())

    @staticmethod
    def gunzip_bytes_obj(bytes_obj: bytes) -> str:
        return gzip.decompress(bytes_obj).decode()

    @staticmethod
    def _calculate_bit_depth(max_val, encoding_size):
        bitdepth = 0
        while max_val >= 1:
            max_val /= encoding_size
            bitdepth += 1
        return bitdepth

    @staticmethod
    def calculate_bit_depth(values, encoding_size):
        longest_input_length = np.max(np.vectorize(len)(values.astype(np.str_)))
        maximum_precision = EncoderHelpers.precision_and_scale_np(values, longest_input_length)

        max_value = np.max(values)
        min_value = np.min(values)

        max_value = max(abs(max_value), abs(min_value))
        if maximum_precision != 0:
            numeric_type = "float"
            max_value *= 10 ** maximum_precision
        else:
            numeric_type = "int"

        if min_value < 0:
            signed = True
            max_value *= 2
        else:
            signed = False
        valuebitsize = EncoderHelpers._calculate_bit_depth(max_value, encoding_size)
        return valuebitsize, maximum_precision, numeric_type, signed

    @staticmethod
    def create_lookup_table(values, encoding_size=64):
        values = list(set(values))
        for i, _ in enumerate(values):
            if isinstance(values[i], np.generic):
                values[i] = values[i].item()
        num_vals = len(values)
        encoding_depth, max_prec, num_type, signed = EncoderHelpers.calculate_bit_depth(np.arange(1, num_vals+1), encoding_size=encoding_size)
        encoder = NumericEncoder(numeric_type=num_type, signed=signed, float_precision=max_prec, encoding_depth=encoding_depth, encoding_size=encoding_size)
        encoded = encoder.encode(np.arange(0, num_vals))
        encoded_states = [encoded[i:i+encoding_depth] for i in range(0, len(encoded), encoding_depth)]
        lookup = {}
        for i, s in enumerate(values):
            lookup[s] = encoded_states[i]
        return lookup, encoding_depth

class TimeSeriesEncoder:
    def __init__(self, timeseries = None, ts_key='UTC', ts_value='Value', sort_values=False, encoding_size = 64):
        # Save raw timeseries
        self.timeseries = timeseries
        self.encoding_size = encoding_size
        self.ts_key = ts_key
        self.ts_value = ts_value
        self.sort_values = sort_values
        self.static = None
        self.regular = False

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
                valuebitsize, maximum_precision, numeric_type, signed = EncoderHelpers.calculate_bit_depth(values, encoding_size)
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

class JSONEncoder(TimeSeriesEncoder):
    @staticmethod
    def encode_json(json_data, ts_key, ts_value, sort_values = False, encoding_size = 64, inplace=False, gzip=False):
        if inplace == False:
            json_data = copy.copy(json_data)
        encoded = JSONEncoder._encode_json(json_data, ts_key, ts_value, sort_values, encoding_size)
        if gzip:
            jstr = json.dumps(encoded, cls=NumpyEncoder)
            bytes = EncoderHelpers.gzip_str(jstr)
            return bytes
        return encoded
            
    @staticmethod
    def decode_json(json_data, inplace=False, gzip=False):
        if gzip:
            json_data = EncoderHelpers.gunzip_bytes_obj(json_data)
            json_data = json.loads(json_data)

        if inplace == False and gzip == False:
            json_data = copy.copy(json_data)
        decoded = JSONEncoder._decode_json(json_data)
        return decoded

    @staticmethod
    def _encode_json(json_data, ts_key, ts_value, sort_values = False, encoding_size = 64):
        if type(json_data) == dict:
            for key in json_data:
                json_data[key] = JSONEncoder._encode_json(json_data[key], ts_key, ts_value, sort_values, encoding_size)
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
                    json_data[i] = JSONEncoder._encode_json(j, ts_key, ts_value, sort_values, encoding_size)
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
                    json_data[i] = JSONEncoder._decode_json(j)
            return json_data
        else:
            encoded_ts = False
            if 'encoding_start' in json_data:
                encoded_ts = True
                    
            if encoded_ts == False:
                for k in json_data:
                    json_data[k] = JSONEncoder._decode_json(json_data[k])
                return json_data
            else:
                encoder = TimeSeriesEncoder.deserialize(json_data)
                if 'data' in json_data:
                    json_data = encoder.decode(json_data['data'])
                else:
                    json_data = encoder.decode()
                return json_data

class CSVEncoder(TimeSeriesEncoder):
    def _set_time_params(self, col_name = None, start = None, lookup=None, encoder=None):
        if col_name is not None:
            self.time["name"] = col_name        
        if start is not None:
            self.time["start"] = start
        if lookup is not None:
            self.time["lookup"] = lookup
        if encoder is not None:
            self.time["encoder"] = NumericEncoder.serialize(encoder)

    def _set_key_params(self, col_names, lookup):
        self.keys["columns"] = col_names
        self.keys["lookup"] = lookup
    
    def _set_static_column(self, column_name, column_value):
        if isinstance(column_value, np.generic):
            column_value = column_value.item()
        self.value_columns[column_name] = {
                "column_value": column_value
            }

    def _set_lookup_column(self, column_name, lookup):
        if column_name in self.value_columns:
            self.value_columns[column_name]["lookup"] = lookup
        else:
            self.value_columns[column_name] = {
                "lookup": lookup
            }

    def _set_encoded_column(self, column_name, encoder):
        if column_name in self.value_columns:
            self.value_columns[column_name]["encoder"] = encoder
        else:
            self.value_columns[column_name] = {
                "encoder": NumericEncoder.serialize(encoder)
            }
    
    def _set_functional_column(self, column_name, model):
        if column_name in self.value_columns:
            self.value_columns[column_name]["function"] = model.coef_
        else:
            self.value_columns[column_name] = {
                "function": [x.item() for x in model.coef_]
            }

    def _set_value_column_fmt(self, csv):
        data = csv.split('\n')[0:2]
        headers = data[0]
        rows = data[1]
        df = pd.DataFrame([rows.split(',')], columns=headers.split(','))
        for col in self.value_columns:
            try:
                float(df[col][0])
                deci_count = len(df[col][0].split('.')[1])
                self.value_columns[col]["format"] = f'.{deci_count}f'
            except:
                continue
            

    def encode_time(self, df, time_column):

        times = [x.timestamp() for x in np.vectorize(ciso8601.parse_datetime)(df[time_column].values)]
        self.times = times
        self._set_time_params(col_name=time_column, start=min(times))
        gaps = np.insert(np.diff(times), 0, 0).astype(np.int64)

        # Calculate encoder params
        encoding_depth, max_prec, num_type, signed = EncoderHelpers.calculate_bit_depth(gaps, encoding_size=self.encoding_size)
        # Do direct encoding
        encoder = NumericEncoder(numeric_type=num_type, signed=signed, float_precision=max_prec, encoding_depth=encoding_depth, encoding_size=self.encoding_size)
        encoded = encoder.encode(gaps)
        self._set_time_params(encoder=encoder)
        words = [encoded[i:i+encoding_depth] for i in range(0, len(encoded), encoding_depth)]

        # Decided if we encode the values directly, or use a lookup table
        states = set(words)
        num_states = len(states)
        str_len_states = len(str(states))
        lookup_bit_depth = EncoderHelpers._calculate_bit_depth(num_states, self.encoding_size)

        if lookup_bit_depth * len(words) + str_len_states < len(encoded):
            # Do lookup table
            lookup, encoding_depth = EncoderHelpers.create_lookup_table(words)
            encoded = ''
            for i in words:
                encoded += lookup[i]
            self._set_time_params(lookup=lookup)
            words = [encoded[i:i+encoding_depth] for i in range(0, len(encoded), encoding_depth)]

        return np.asarray(words).reshape(-1, 1)
    
    def encode_keys(self, df, key_columns):
        #Build unique aggregate key
        df = df[key_columns]
        aggregate_keys = df[key_columns].astype(str).agg('|'.join, axis=1)

        lookup, encoding_depth = EncoderHelpers.create_lookup_table(aggregate_keys, self.encoding_size)
        self._set_key_params(col_names=key_columns, lookup=lookup)
        encoded = ''
        for i in aggregate_keys:
            encoded += lookup[i]

        words = [encoded[i:i+encoding_depth] for i in range(0, len(encoded), encoding_depth)]
        return np.asarray(words).reshape(-1, 1)
    
    def encode_value(self, df, value_column):
        vals = df[value_column].values
        if np.all(vals[0] == vals):
           # Static column
           self._set_static_column(column_name=value_column, column_value=vals[0])
           return
        
        if vals.dtype != object:
            # Check functional column
            x_ = PolynomialFeatures(degree=1, include_bias=True).fit_transform(np.asarray(self.times).reshape(-1, 1))
            model = LinearRegression(fit_intercept=False).fit(x_, vals)
            if model.score(x_, vals) == 1.0:
                self._set_functional_column(column_name=value_column, model=model)
                return
        
            # Calculate encoder params
            encoding_depth, max_prec, num_type, signed = EncoderHelpers.calculate_bit_depth(vals, encoding_size=self.encoding_size)
            # Do direct encoding
            encoder = NumericEncoder(numeric_type=num_type, signed=signed, float_precision=max_prec, encoding_depth=encoding_depth, encoding_size=self.encoding_size)
            encoded = encoder.encode(vals)
            self._set_encoded_column(column_name=value_column, encoder=encoder)
            words = [encoded[i:i+encoding_depth] for i in range(0, len(encoded), encoding_depth)]
        else:
            words = vals
            encoded = ''.join(vals)

        # Decided if we encode the values directly, or use a lookup table
        states = set(words)
        num_states = len(states)
        str_len_states = len(str(states))
        lookup_bit_depth = EncoderHelpers._calculate_bit_depth(num_states, self.encoding_size)
        if lookup_bit_depth * len(words) + str_len_states < len(encoded):
            # Do lookup table
            lookup, encoding_depth = EncoderHelpers.create_lookup_table(words)
            encoded = ''
            for i in words:
                encoded += lookup[i]
            self._set_lookup_column(column_name=value_column, lookup=lookup)
            words = [encoded[i:i+encoding_depth] for i in range(0, len(encoded), encoding_depth)]
        
        return np.asarray(words).reshape(-1, 1)

    @staticmethod
    def encode_csv(csv, time_column, key_columns, sort_values = True, encoding_size = 64, gzip=False):
        df = pd.read_csv(StringIO(csv))
        if sort_values:
            df = df.sort_values(time_column, ascending=True)

        encoder = CSVEncoder(encoding_size=encoding_size)
        encoder.columns = list(df.columns)

        ndf = pd.DataFrame(encoder.encode_time(df, time_column), columns=[time_column])
        ndf["keys"] = encoder.encode_keys(df, key_columns)
        tscols = set(df.columns) - set([time_column] + key_columns)
        for col in tscols:
            encoded = encoder.encode_value(df, value_column=col)
            if encoded is not None:
                # Static columns will be omit from the dataframe and added to metadata, so this can be None
                ndf[col] = encoded
        
        encoder._set_value_column_fmt(csv)

        packet = encoder.__dict__
        del packet["times"]
        data = ndf.astype(str).agg(''.join, axis=1)
        packet["data"] = ''.join(data)
        encoded = json.dumps(packet)
        if gzip:
            encoded = EncoderHelpers.gzip_str(encoded)

        return encoded

    def decode_calculate_token_size(self, json_data):
        timesize = 0
        keysize = 0
        valuesize = 0

        t = json_data["time"]
        if "lookup" in t:
            for k in t["lookup"]:
                token = t["lookup"][k]
                timesize += len(token)
                break
        elif "encoder" in t:
            timesize += t["encoder"]["encoding_depth"]
        
        for k in json_data["keys"]["lookup"]:
            token = json_data["keys"]["lookup"][k]
            keysize += len(token)
            break

        for col in json_data["value_columns"]:
            c = json_data["value_columns"][col]
            if "lookup" in c:
                for k in c["lookup"]:
                    token = c["lookup"][k]
                    valuesize += len(token)
                    break
            elif "encoder" in c:
                valuesize += c["encoder"]["encoding_depth"]
        return timesize, keysize, valuesize

    def decode_time(self, json_data, tokens):
        time_vals = json_data["time"]
        start = time_vals["start"]
        if 'lookup' in time_vals:
            lookup = time_vals["lookup"]
            lookup =  {v: k for k, v in lookup.items()}
            tokens = np.vectorize(lookup.get)(tokens)

        if 'encoder' in time_vals:
            encoder = NumericEncoder.deserialize(time_vals["encoder"])
            tokens = encoder.decode(''.join(tokens))
        
        cumulative_time = np.cumsum(np.asarray(tokens))
        time = cumulative_time + start
        self.time = time
        fmttimes = np.vectorize(datetime.datetime.utcfromtimestamp)(time)
        fmttimes = ['%02d-%02d-%02dT%02d:%02d:%02dZ' % (x.year, x.month, x.day, x.hour, x.minute, x.second) for x in fmttimes]
        return fmttimes

    
    def decode_key(self, json_data, tokens):
        columns = json_data["keys"]["columns"]
        lookup = json_data["keys"]["lookup"]
        lookup =  {v: k for k, v in lookup.items()}
        new_tokens = np.vectorize(lookup.get)(tokens)
        new_tokens = np.char.split(new_tokens, sep="|")
        new_tokens = np.array([x for x in new_tokens])
        key_data = pd.DataFrame(new_tokens, columns=columns)
        return key_data

    def decode_values(self, json_data, tokens):
        value_columns = json_data["value_columns"]
        df = pd.DataFrame(np.ones((len(tokens), len(json_data["value_columns"]))))
        df.columns = [col for col in value_columns]
        for col in value_columns:
            if "function" in value_columns[col]:
                coefs = value_columns[col]["function"]
                x = self.time
                model = LinearRegression()
                model.intercept_ = np.array([coefs[0]])
                model.coef_ = np.array([coefs[1]])
                df[col] = model.predict(x.reshape(-1, 1))
            elif "column_value" in value_columns[col]:
                df[col] = value_columns[col]["column_value"]
            else:
                col_json = value_columns[col]
                if 'lookup' in col_json:
                    lookup = col_json["lookup"]
                    lookup =  {v: k for k, v in lookup.items()}
                    token_size = len(list(lookup.keys())[0])
                    tokens = [(x[:token_size], x[token_size:]) for x in tokens]
                    col_tokens = np.vectorize(lookup.get)([x[0] for x in tokens])
                    if 'encoder' in col_json:
                        encoder = NumericEncoder.deserialize(col_json["encoder"])
                        col_tokens = encoder.decode(''.join(col_tokens))
                    df[col] = col_tokens
                    tokens = [x[1] for x in tokens]
                elif 'encoder' in col_json:
                    encoder = NumericEncoder.deserialize(col_json["encoder"])
                    tokens = [(x[:token_size], x[token_size:]) for x in tokens]
                    col_tokens = encoder.decode(''.join([x[0] for x in tokens]))
                    df[col] = col_tokens
                    tokens = [x[1] for x in tokens]

            if "format" in value_columns[col]:
                fmt = value_columns[col]["format"]
                df[col] = df[col].apply(lambda x: f"{x:{fmt}}")
            

        return df

    def tokenize(self, data, time_size, key_size, value_size):
        num_tokens = len(data) / (time_size + key_size + value_size)
        num_tokens = int(num_tokens)
        times = np.zeros(num_tokens).astype(np.str_)
        keys = np.zeros(num_tokens).astype(np.str_)
        values = np.zeros(num_tokens).astype(np.str_)
        for token, i in enumerate(range(0, len(data), (time_size + key_size + value_size))):
            times[token] = data[i:i+time_size]
            keys[token] = data[i+time_size:i+time_size+key_size]
            values[token] = data[i+time_size+key_size:i+time_size+key_size+value_size]
        return times, keys, values

    @staticmethod
    def decode_csv(encoded_data, gzip=False):
        if gzip:
            encoded_data = EncoderHelpers.gunzip_bytes_obj(encoded_data)
        
        json_data = json.loads(encoded_data)
        decoder = CSVEncoder(encoding_size=json_data["encoding_size"])
        time_size, key_size, value_size = decoder.decode_calculate_token_size(json_data)
        data = json_data["data"]
        times, keys, values = decoder.tokenize(data, time_size, key_size, value_size)
        ndf = pd.DataFrame(decoder.decode_time(json_data, times), columns=[json_data["time"]["name"]])
        ndf = ndf.join(decoder.decode_key(json_data, keys))
        ndf = ndf.join(decoder.decode_values(json_data, values))
        ndf = ndf[json_data["columns"]]
        return ndf.to_csv(index=False)

    def __init__(self, encoding_size=64):
        self.encoding_size = encoding_size
        self.value_columns = {}
        self.time = {}
        self.keys = {}



if __name__ == '__main__':
    pass
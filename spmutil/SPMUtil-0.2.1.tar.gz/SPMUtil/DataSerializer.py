import json
import os
import pickle

import numpy as np


class NdarrayEncoder(json.JSONEncoder):
    """
    - Serializes python/Numpy objects via customizing json encoder.
    - **Usage**
        - `json.dumps(python_dict, cls=EncodeFromNumpy)` to get json string.
        - `json.dump(*args, cls=EncodeFromNumpy)` to create a file.json.
    """

    def default(self, obj):
        import numpy
        if isinstance(obj, numpy.ndarray):
            return {
                "_kind_": "ndarray",
                "_value_": obj.tolist()
            }
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, range):
            value = list(obj)
            return {
                "_kind_": "range",
                "_value_": [value[0], value[-1] + 1]
            }
        return super(NdarrayEncoder, self).default(obj)



class NdarrayDecoder(json.JSONDecoder):
    """
    - Deserilizes JSON object to Python/Numpy's objects.
    - **Usage**
        - `json.loads(json_string,cls=DecodeToNumpy)` from string, use `json.load()` for file.
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        import numpy
        if '_kind_' not in obj:
            return obj
        kind = obj['_kind_']
        if kind == 'ndarray':
            return numpy.array(obj['_value_'])
        elif kind == 'range':
            value = obj['_value_']
            return range(value[0],value[-1])
        return obj






class DataSerializer:

    def __init__(self, path, custom_ext=".pkl"):
        self.path = path
        self._ext = custom_ext
        self.header = None
        self.data_dict = {}

    @property
    def header_key(self):
        return "data_main_header"

    def set_header(self, header):
        self.data_dict[self.header_key] = header

    def save(self):
        if self.header_key not in self.data_dict:
            raise ValueError("Save file need a header, use set_header(type(dict)) function")
        filename, file_extension = os.path.splitext(self.path)
        with open(filename + self._ext, "wb") as f:
            pickle.dump(self.data_dict, f, pickle.HIGHEST_PROTOCOL)
            print("save to", filename + self._ext)

    def load(self):
        filename, file_extension = os.path.splitext(self.path)
        if file_extension != self._ext:
            filename = self.path
        with open(filename + self._ext, "rb") as f:
            self.data_dict = pickle.load(f)
            self.header = self.data_dict[self.header_key]

    def deep_load(self, jsonDecoder=NdarrayDecoder, reload=True):
        if reload:
            self.load()
        self.data_dict = self._deep_load_tree(self.data_dict, jsonDecoder)

    def _deep_load_tree(self, target_dict, jsonDecoder=NdarrayDecoder):
        if target_dict is dict:
            for it in target_dict.keys():
                if self._is_json(target_dict[it]):
                    target_dict[it] = json.loads(target_dict[it], cls=jsonDecoder)
                    target_dict[it] = self._deep_load_tree(target_dict[it], jsonDecoder)
        return target_dict

    def add_data(self, key, data, overwrite=False, save=False):
        if key in self.data_dict:
            if overwrite:
                self.data_dict.pop(key)
                self.data_dict[key] = data
        else:
            self.data_dict[key] = data

        if save:
            self.save()

    def remove_data(self, key, save=False):
        if key in self.data_dict:
            self.data_dict.pop(key)
        if save:
            self.save()

    @staticmethod
    def to_matrix_buffer(ndarray):
        return ndarray.tobytes()

    @staticmethod
    def from_matrix_buffer(buffer):
        return np.frombuffer(buffer)

    @staticmethod
    def _is_json(json_str):
        try:
            json.loads(json_str)
        except ValueError as e:
            return False
        return True




# class NdarrayEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, np.integer):
#             return int(obj)
#         elif isinstance(obj, np.floating):
#             return float(obj)
#         elif isinstance(obj, np.ndarray):
#             return obj.tolist()
#         else:
#             return super(NdarrayEncoder, self).default(obj)


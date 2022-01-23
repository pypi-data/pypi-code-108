from .var_spec import VarSpec
import tensorflow as tf


class VarType:
    def __init__(self, type_spec, num=200,):
        self._var_type = []
        self._num = num
        self._type_spec = type_spec
        self._data = dict() 

    def __call__(self, *char_lst):
        len_lst = len(char_lst)
        result = []

        try:
            if len_lst == 0:
                result = [data for data in self._data.values()]
                return tf.concat(result, axis=1)
            elif len_lst == 1:
                return self._data[char_lst[0]]
        except:
            return 0

    def _generate_one_spec(self, var_spec):
        character = var_spec.character
        type_cond = self._type_spec[character]

        if type_cond == character:
            self._data[character] = var_spec.random(self._num) 
        elif isinstance(type_cond, int) or isinstance(type_cond, float):
            self._data[character] = var_spec.random(self._num, random_type=float(type_cond))

    def generate_data(self, var_pool):
        if len(self._type_spec.keys()) == len(var_pool):
            for var_spec in var_pool:
                self._generate_one_spec(var_spec)
        else:
            raise RuntimeError(f"You must implement for all VarSpec")

    def update_data(self, index):
        if index != None:
            index = index[0]
            for key, data in self._data.items(): 
                self._data[key] = tf.concat([data, data[index:index+1]], axis=0)

    @staticmethod
    def encode_key(var_spec):
        result = ""
        key_value = var_spec.items()
        for index, (key, value) in enumerate(key_value):
            if isinstance(value, int):
                value = float(value)
            result += str(key) + "_" + str(value)
            if index != len(key_value) - 1:
                result += "_"
        return result

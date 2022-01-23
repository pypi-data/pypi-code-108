import tensorflow as tf
from .grad import Grad
from .var_type import VarType


class VarContainer:
    def __init__(self, variables):
        self._var_types = []
        self._grads = dict()
        self._var_pool = variables

    def add_var_type(self, num, type_spec):
        var_type = VarType(type_spec, num=num)
        self._var_types.append(var_type)
        key = VarType.encode_key(type_spec)
        self._grads[key] = Grad(var_type)
    
    def __call__(self, num=200, **type_spec):
        key = VarType.encode_key(type_spec)

        if key not in self._grads.keys():
            self.add_var_type(num, type_spec)

        return self._grads[key]

    def iterate_grads(self):
        return [grad for key, grad in self._grads.items()]

    def generate(self):
        for var_type in self._var_types:
            var_type.generate_data(self._var_pool)

    def update(self, indexes):
        for index, var_type in zip(indexes, self._var_types):
            var_type.update_data(index)

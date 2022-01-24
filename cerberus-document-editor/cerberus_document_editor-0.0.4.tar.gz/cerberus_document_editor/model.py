import json

class ObjectModel:
    def __new__(cls, value=None):
        if isinstance(value, dict):
            instance = object.__new__(DictModel)
        else:
            instance = object.__new__(GenericModel)
        instance.__init__(value)
        return instance

    def __init__(self, v=None):
        self._type = type(v)
        
    @property
    def type(self):
        return self._type

class GenericModel(ObjectModel):
    def __init__(self, v=None):
        super(GenericModel, self).__init__(v)
        self.value = v
        
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self._type = type(v)

    def __repr__(self):
        return str(self._value)

class DictModel(ObjectModel):
    def __init__(self, v={}):
        super(DictModel, self).__init__(v)
        if not isinstance(v, dict): 
            raise TypeError(f'Not support type [{type(v)}]')
        self._type = dict
        self._value = {} 
        for k in v: self.__setitem__(k, v[k])

    @property
    def keys(self):
        return self._value.keys()

    def __getitem__(self, key):
        return self._value[key]

    def __setitem__(self, key, value):
        if not isinstance(value, ObjectModel):
            value = ObjectModel(value)
        self._value[key] = value

    def __repr__(self):
        return json.dumps(self._value, default=lambda x: x._value)
import json
from .util import check_type, unique_string
from datetime import datetime
import requests
from os import path

class classorinstancemethod(classmethod):

    def __get__(self, instance, type_):
        descr_get = super().__get__ if instance is None else self.__func__.__get__
        return descr_get(instance, type_)


class JsonDate:
    date_format = '%Y-%m-%d %H:%M:%S.%f'


class JsonObject:

    def __init__(self, **kwargs):
        if type(self) is JsonObject:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __str__(self):
        s = ""
        v = vars(self)
        for k in v:
            if k[0] == "_":
                continue
            if s:
                s += ","
            s += "\"%s\":" % k
            if isinstance(v[k], str):
                s += "%s" % json.dumps(v[k])
            elif isinstance(v[k], datetime):
                s += "\"%s\"" % v[k].strftime(JsonDate.date_format)
            elif isinstance(v[k], bool):
                s += "%s" % str(v[k]).lower()
            else:
                s += "%s" % str(v[k])
        return "{%s}" % s

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        v = vars(self)
        vo = vars(other)
        for k in v:
            if k[0] == "_":
                continue
            if v[k] != vo[k]:
                return False
        return True

    def copy(self):
        return type(self).parse(str(self))

    def format(self, format_string: str):
        v = vars(self)
        for k in v:
            if not isinstance(v[k], JsonObject):
                continue
            pos = format_string.find("{"+k+":")
            if pos >= 0:
                sub_format_start = format_string.find(":", pos) + 1
                sub_format_end = sub_format_start
                bracket_count = 1
                while bracket_count and sub_format_end < len(format_string):
                    c = format_string[sub_format_end]
                    if c == '{':
                        bracket_count += 1
                    if c == '}':
                        bracket_count -= 1
                    sub_format_end += 1
                sub_format = format_string[sub_format_start:sub_format_end-1]
                sub_str = v[k].format(sub_format)
                format_string = format_string[:pos] + sub_str + format_string[sub_format_end:]
        return format_string.format(**vars(self))

    @classorinstancemethod
    def parse(cls_or_self, json_string: str = "", json_dictionary: dict=None):
        if json_string:
            json_dictionary = json.loads(json_string)

        if type(cls_or_self) is type:
            new_object = cls_or_self()
        else:
            new_object = cls_or_self
        for key in json_dictionary:
            member = getattr(new_object, key)
            it = type(member)
            if issubclass(it, JsonObject):
                av = it.parse(json_dictionary=json_dictionary[key])
                setattr(new_object, key, av)
            elif issubclass(it, JsonList):
                member.parse(json_list=json_dictionary[key])
            elif it is datetime:
                av = datetime.strptime(json_dictionary[key], JsonDate.date_format)
                setattr(new_object, key, av)
            else:
                av = it(json_dictionary[key])
                setattr(new_object, key, av)
        return new_object

    @staticmethod
    def load(json_string: str = "", json_dictionary_or_list=None) -> type:
        if json_string:
            check_type(json_string, str, "wrong type for json_string")
            json_dictionary_or_list = json.loads(json_string)
        class_name = "Json_object_" + unique_string()
        constructor_string = "def " + class_name + "__init__ (self):"
        if isinstance(json_dictionary_or_list, list):
            new_list = JsonList(list_type=None)
            for item in json_dictionary_or_list:
                if isinstance(item, list) or isinstance(item, dict):
                    new_item = JsonObject.load(json_dictionary_or_list=item)
                else:
                    new_item = item
                new_list.append(new_item)
            return new_list
        elif isinstance(json_dictionary_or_list, dict):
            for key in json_dictionary_or_list.keys():
                if isinstance(json_dictionary_or_list[key], dict) or isinstance(json_dictionary_or_list[key], list):
                    constructor_string += "\n\tself." + key + " = self.load(json_string='" + json.dumps(json_dictionary_or_list[key]) + "')"
                else:
                    constructor_string += "\n\tself." + key + " = " + json_dictionary_or_list[key].__repr__()
            d = {}
            exec(constructor_string, d)
            new_type = type(class_name, (JsonObject, ), {"__init__": d[class_name + "__init__"]})
            return new_type()
        else:
            raise TypeError("wrong type for json_dictionary_or_list")

    def save(self, file_path: str):
        with open(file_path, 'w') as f:
            f.write(str(self))

    @classmethod
    def load_from_file(cls, file_path: str):
        if not path.exists(file_path):
            return None
        json_content = ""
        with open(file_path) as f:
            json_content = f.read()
        if cls is JsonObject:
            return cls.load(json_content)
        else:
            return cls.parse(json_content)

    @classmethod
    def load_from_url(cls, uri: str):
        req = requests.get(uri)
        if req.status_code == 200:
            if cls is JsonObject:
                return cls.load(req.text)
            else:
                return cls.parse(req.text)
        return None


class JsonList(list):

    def __init__(self, iterable=None, list_type=None):
        iterable = list() if not iterable else iterable
        iter(iterable)
        map(self._typeCheck, iterable)
        list.__init__(self, iterable)
        self.list_type = list_type

    def _typeCheck(self, val):
        if self.list_type:
            check_type(val, self.list_type, "Wrong type %s, this list can hold only instances of %s" % (type(val), str(self.list_type)))
        else:
            if not (issubclass(type(val), JsonObject) or isinstance(val, (str, int, float, bool, JsonList))):
                raise TypeError("Wrong type %s, this list can hold only str, int, float, bool, JsonObject or JsonList" % (type(val),))

    def __iadd__(self, other):
        map(self._typeCheck, other)
        list.__iadd__(self, other)
        return self

    def __add__(self, other):
        iterable = [item for item in self] + [item for item in other]
        return JsonList(iterable, self._allowedType)

    def __radd__(self, other):
        iterable = [item for item in other] + [item for item in self]
        if isinstance(other, JsonList):
            return self.__class__(iterable, other.list_type)
        return JsonList(iterable, self.list_type)

    def __setitem__(self, key, value):
        itervalue = (value,)
        if isinstance(key, slice):
            iter(value)
            itervalue = value
        map(self._typeCheck, itervalue)
        list.__setitem__(self, key, value)

    def __setslice__(self, i, j, iterable):
        iter(iterable)
        map(self._typeCheck, iterable)
        list.__setslice__(self, i, j, iterable)

    def append(self, val):
        self._typeCheck(val)
        list.append(self, val)

    def extend(self, iterable):
        iter(iterable)
        map(self._typeCheck, iterable)
        list.extend(self, iterable)

    def insert(self, i, val):
        self._typeCheck(val)
        list.insert(self, i, val)

    def __str__(self):
        return "[" + ",".join([json.dumps(x) if type(x) is str else str(x) for x in self]) + "]"

    def get(self, m):
        l = JsonList()
        for i in self:
            if m in vars(i):
                l.append(vars(i)[m])
        return l

    def where(self, m, v, o="=="):
        nl = type(self)()
        for i in self:
            if type(vars(i)[m]) is str or issubclass(type(vars(i)[m]), JsonObject):
                e = "'%s' %s '%s'" % (str(vars(i)[m]), o, str(v))
            else:
                e = "%s %s %s" % (str(vars(i)[m]), o, str(v))
            if eval(e):
                nl.append(i)
        return nl

    def copy(self):
        return type(self).parse(str(self))

    @classorinstancemethod
    def parse(cls_or_self, json_string="", json_list=None):
        if json_string:
            check_type(json_string, str, "wrong type for json_string")
            json_list = json.loads(json_string)
        check_type(json_list, list, "wrong type for json_list")
        if type(cls_or_self) is type:
            new_list = cls_or_self()
        else:
            new_list = cls_or_self
        it = new_list.list_type
        ic = it().__class__
        for i in json_list:
            if issubclass(ic, JsonObject):
                new_list.append(it.parse(json_dictionary=i))
            elif issubclass(ic, JsonList):
                new_list.append(it.parse(json_list=i))
            else:
                new_list.append(i)
        return new_list

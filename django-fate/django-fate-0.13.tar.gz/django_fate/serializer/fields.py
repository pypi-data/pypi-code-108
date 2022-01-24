import json
from json.decoder import JSONDecodeError


class Field:
    def __init__(self, field=None):
        self.field = field

    def __get__(self, instance, owner):
        return self.call_back

    def call_back(self, value):
        # 整型和None类型不转换，布尔类型也是整型
        if isinstance(value, int) or value is None:
            return value
        else:
            return str(value)

    # 当字段未定义描述符时调用该默认函数
    @classmethod
    def default(cls, value):
        # 整型和None类型不转换，布尔类型也是整型
        if isinstance(value, int) or value is None:
            return value
        else:
            return str(value)


class Foreignkey(Field):
    def __init__(self, serialize_class=None, field=None):
        self.owner = None
        self.serialize_class = serialize_class
        super().__init__(field)

    def __get__(self, instance, owner):
        self.owner = owner
        return self.call_back

    def call_back(self, value):
        if not value:
            return None
        if self.serialize_class:
            serialize_class = self.serialize_class
        else:
            serialize_class = self.owner
        return serialize_class(value)


class JsonTextField(Field):

    def call_back(self, value):
        if not value:
            return None
        try:
            return json.loads(value)
        except JSONDecodeError:
            TypeError('json loads发生错误,字段:{} ！'.format(self.field))


class ImgField(Field):
    def __init__(self, host, media_url, field=None):
        self.host, self.media_url = host, media_url
        super().__init__(field=field)

    def call_back(self, value):
        if not value:
            return None
        return self.host + self.media_url + str(value)


class DateTimeField(Field):

    def call_back(self, value):
        if not value:
            return value
        return str(value)[0:19]


class ManyToManyField(Field):
    def __init__(self, serialize_class, field=None):
        self.instance = None
        self.serialize_class = serialize_class
        super().__init__(field)

    def __get__(self, instance, owner):
        self.instance = instance
        return self.call_back

    def call_back(self, model_obj):
        hook_name = '_'.join(('hook', self.field))
        hook_func = getattr(self.instance, hook_name, None)
        if hook_func:
            query_set = hook_func(model_obj)
        else:
            many_obj = getattr(model_obj, self.field, None)
            query_set = many_obj.all() if many_obj else ()
        return self.serialize_class(query_set)


class CrossTable(ManyToManyField):
    def call_back(self, model_obj):
        hook_name = '_'.join(('hook', self.field))
        hook_func = getattr(self.instance, hook_name, None)
        if hook_func:
            query_set = hook_func(model_obj)
        else:
            cross_obj = getattr(model_obj, '_'.join((self.field, 'set')), None)
            query_set = cross_obj.all() if cross_obj else ()
        return self.serialize_class(query_set)

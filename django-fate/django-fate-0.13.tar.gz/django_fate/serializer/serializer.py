from .fields import Field, ManyToManyField, CrossTable
from django.db.models import QuerySet, Model
from collections import Iterable


class SerializerMeta(type):
    def __new__(mcs, name, bases, act):
        parents = [b for b in bases if isinstance(b, SerializerMeta)]
        if not parents:
            return super().__new__(mcs, name, bases, act)

        # 当filed被设置为None时，使用属性名作为filed的值
        for attr_name, attr in act.items():
            if isinstance(attr, Field) and not attr.field:
                attr.field = attr_name

        # 记录多对多字段和跨表
        many_or_cross = []
        for attr_name, attr in act.items():
            if isinstance(attr, ManyToManyField) or isinstance(attr, CrossTable):
                many_or_cross.append(attr_name)
        # 操作和添加Meta
        attr_meta = act.pop('Meta', None)  # pop掉Meta是为了拿到父类的Meta信息
        new_class = super().__new__(mcs, name, bases, act)
        meta = attr_meta or getattr(new_class, 'Meta', None)
        only, defer = getattr(meta, 'only', []), getattr(meta, 'defer', [])
        meta_many_cross = getattr(meta, '_many_or_cross', [])
        meta_attr = {'only': only, 'defer': defer, '_many_or_cross': many_or_cross + meta_many_cross}
        new_class.Meta = type('Meta', (), meta_attr)  # 给每个类动态生成一个新的Meta类
        return new_class

    def __call__(cls, set_or_obj):
        self = super().__call__()
        results = self._serialize(set_or_obj)
        return results


class Serializer(metaclass=SerializerMeta):

    def _serialize(self, set_or_obj):
        """序列化queryset或model_obj"""
        if isinstance(set_or_obj, Iterable):
            return [self._to_dict(obj) for obj in set_or_obj]

        elif isinstance(set_or_obj, Model):
            return self._to_dict(set_or_obj)

        else:
            raise TypeError('{}类型不支持序列化'.format(type(set_or_obj)))

    # model_obj处理成字典
    def _to_dict(self, model_obj):
        obj_dict = {}

        for field in model_obj._meta.fields:
            # only被定义时，忽略only以外的全部字段
            if self.Meta.only and field.name not in self.Meta.only:
                continue
            # 只在没定义only时defer生效，only一旦定义defer失效
            if not self.Meta.only and field.name in self.Meta.defer:
                continue
            field_value = getattr(model_obj, field.name)  # 获取字段的值
            handle = getattr(self, field.name, Field.default)  # 获取（在描述符中）字段的处理方法
            if field.choices:  # 获取该字段的display
                obj_dict[field.name + '_display'] = dict(field.choices).get(field_value, None)
            obj_dict[field.name] = handle(field_value)
        # 处理多对多字段以及跨表
        for many_or_table_name in self.Meta._many_or_cross:
            handle = getattr(self, many_or_table_name)
            obj_dict[many_or_table_name] = handle(model_obj)

        return obj_dict

    class Meta:
        """如果外键没有定义序列化类，那么only和defer对外键同样生效,如序列化多对多字段一定要设置序列化类"""
        _many_or_cross = []
        only = []  # 当定义了only时defer失效
        # 本次序列化排除的字段
        defer = []

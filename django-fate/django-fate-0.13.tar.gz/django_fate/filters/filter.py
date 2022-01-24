from .fields import Field
from django.db.models import QuerySet


class FilterMeta(type):
    def __new__(mcs, name, bases, act):
        # 命名规范和设置field默认值
        for attr_name, attr in act.items():
            if isinstance(attr, Field):

                if attr_name.startswith('_') or attr_name[0].isupper():
                    raise TypeError('{}中的{},不能为下划线开头，不能大写字母开头'.format(name, attr_name))

                # 当filed被设置为None时，使用属性名作为filed的值
                if not attr._field:
                    attr._field = attr_name
        return super().__new__(mcs, name, bases, act)

    def __init__(cls, name, bases, act):
        super().__init__(name, bases, act)
        # 约束类的定义
        cls.const(name, bases, act)

    def __call__(cls, *args, **kwargs):
        self = super().__call__(*args, **kwargs)
        return self._queryset

    def const(cls, name, bases, act):
        if '_base' in act and act['_base']:
            return
        # Filter中的class Meta 必须定义model
        meta = getattr(cls, 'Meta', None)
        if not getattr(meta, 'model', None):
            raise TypeError('{}的Meta.model不能为None'.format(name))


class Filter(metaclass=FilterMeta):
    _base = True  # _base=True意味着该类只作被继承使用，不会在业务中直接使用

    def __init__(self, request, queryset=None):
        query = request.POST or request.GET
        # queryset为None时取Meta.model.objects
        # 这里不能用or运算，or运算会将空queryset认为None
        if queryset is None:
            self._queryset = self.Meta.model.objects
        elif isinstance(queryset, QuerySet):
            self._queryset = queryset
        else:
            raise ValueError('{} queryset必须是QuerySet Object'.format(self.__class__.__name__))
        self._query = {}
        for key, value in query.items():
            if not isinstance(getattr(self, key, None), dict):
                continue
            setattr(self, key, value)
            self._query.update(getattr(self, key))

        self._queryset = self._queryset.filter(**self._query)

    class Meta:
        model = None

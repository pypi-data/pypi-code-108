from sqlalchemy.ext.declarative import declarative_base

class BaseSerialize:
    def __init__(self):
        self.Meta = getattr(self,'Meta',None)
        self.model = self.Meta.model

    def get_default_fields(self):
        default_fields = list(self.model.__mapper__.c._keys())
        return {self.model.__class__.__name__:default_fields}

    def serialize_fields(self):
        if self.Meta.serialize_fields is None:
            self.Meta.serialize_fields = self.get_default_fields()
        return {self.model.__class__.__name__:self.Meta.serialize_fields}

    def deserialization_fields(self):
        if self.Meta.deserialization_fields is None:
            self.Meta.deserialization_fields = self.get_default_fields()
        return {self.model.__class__.__name__:self.Meta.deserialization_fields}

    def raise_errors_on_fields(self):

        for field in self.serialize_fields().values():
            assert self.serialize_fields().values() not in self.model.__mapper__.c.keys(), (
                'The Serialization field:`.{Fields}`be not in`.{ModelClass}`table'.format(
                    Fields=field,
                    ModelClass=self.model.__class__.__name__
                )
            )

        for field in self.deserialization_fields().values():
            assert field not in self.model.__mapper__.c.keys(), (
                'The Deserialization field:`.{Fields}`be not in`.{ModelClass}`table'.format(
                    Fields=field,
                    ModelClass=self.model.__class__.__name__
                )
            )

    def raise_errors_on_nested_writes(self,method_name,validated_data):
        pass

    def validate(self,attr):
        """
        用户可在此函数内部做一些有关自己的业务校验
        """
        return attr




class SerializeMixin(BaseSerialize):
    """
    暂定此类用作数据库对象转为字典
    """

    def _obj_to_dict(self,ven:object) -> dict:
        """
        多条数据或单条数据从数据库读取的数据转换为一个字典(根据所定义的序列化字段)
        """
        super().raise_errors_on_fields()

        d = {}
        for key in list(self.serialize_fields().values())[0]:
            if getattr(ven, key) is not None:
                d[key] = str(getattr(ven, key))
            else:
                d[key] = getattr(ven, key)

        if hasattr(ven,'cname'):
            for k,v in ven.cname.items():
                if k in d:
                    d[v] = d.pop(k)
        return d

    def data(self, vendors: list or object) -> list:
        """
        此接口对外开放，获取序列化后的数据
        """
        if isinstance(vendors, list):
            result = [self._obj_to_dict(ven) for ven in vendors]
            return result
        elif isinstance(vendors, declarative_base()):
            result = [self._obj_to_dict(vendors)]
            return result
        else:
            # 防止以后出现其他情况
            pass


class ModelSerialize(SerializeMixin):

    def get(self):
        pass

    def create(self,validated_data):
        pass

    def update(self,validated_data):
        pass


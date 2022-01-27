from typing import TypeVar, Generic, Type, Union
from bson import ObjectId, DBRef
from bson.errors import InvalidId
from pydantic.fields import ModelField


T = TypeVar("T")

class ObjectIdStr(str):
    """Field for validate string like ObjectId"""

    type_ = ObjectId
    required = False
    default = None
    validate_always = False
    alias = ''

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError(f"invalid ObjectId - {v}")


class RefrerenceType(Generic[T]):
    def __init__(self, ref: DBRef, model_class: Type[T]):
        self.ref = ref
        self.model_class = model_class
        
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Union[DBRef, T], field: ModelField):
        model_class = field.sub_fields[0].type_  # type: ignore
        if isinstance(v, DBRef):
            return cls(ref=v, model_class=model_class).to_ref()
        if isinstance(v, model_class):
            ref = DBRef(model_class.set_collection_name(), model_class._id)
            return cls(ref=ref, model_class=model_class).to_ref()
        return model_class.validate(v)

    def to_ref(self):
        return self.ref
    
    @classmethod
    async def find_one_async(cls):
        pass
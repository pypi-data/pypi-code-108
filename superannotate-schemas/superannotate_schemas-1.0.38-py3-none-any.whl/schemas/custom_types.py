from typing import Any
from typing import TypeVar

from superannotate_schemas.schemas.base import BaseModel
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper


class CustomFieldMeta(type):
    def __getitem__(self, key_value_type: Any):
        return type('CustomFieldValue', (self,), {'key_value_type': key_value_type})


T = TypeVar("T")


#
# class Strict(Generic[T]):
#     __type_like__: T
#
#     @staticmethod
#     def _display_type(v: Any) -> str:
#         try:
#             return v.__name__
#         except AttributeError:
#             return str(v).replace("typing.", "")
#
#     @classmethod
#     def __class_getitem__(cls, type_like: T) -> T:
#         new_cls = new_class(
#             f"Strict[{cls._display_type(type_like)}]",
#             (cls,),
#             {},
#             lambda ns: ns.update({"__type_like__": type_like}),
#         )
#         return cast(T, new_cls)
#
#     @classmethod
#     def __get_validators__(cls) -> Generator[Callable[..., Any], None, None]:
#         yield cls.validate
#
#     @classmethod
#     def validate(cls, value: Any) -> T:
#         if not isinstancex(value, cls.__type_like__):
#             raise TypeError(f"{value!r} is not of valid type")
#         return value

class StrictType(BaseModel):
    class Config:
        key_field = "type"


class StrictDict(metaclass=CustomFieldMeta):
    key_value_type: Any = None

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):

        if not isinstance(v, dict):
            raise TypeError("type dict expected")

        key_type, value_type = cls.key_value_type
        errors = []

        for key in v:
            try:
                key_type.validate(key)
            except TypeError as e:
                errors.append(ErrorWrapper(exc=e, loc=""))

            try:
                value_type.validate((v[key]))
            except TypeError as e:
                errors.append(ErrorWrapper(exc=e, loc=""))

        if errors:
            raise ValidationError(errors=errors, model=cls)
        return v


class BaseDiscriminatedInstances(BaseModel):
    __root__: Any

    class Config:
        DISCRIMINATOR = "type"

    @classmethod
    def __get_validators__(cls):
        yield cls.return_instance

    @classmethod
    def return_instance(cls, values):
        try:
            discriminator = values[cls.Config.DISCRIMINATOR]
        except KeyError:
            raise TypeError(
                f"Missing required 'type' field for instance: {values}"
            )
        try:
            for instance in cls.__fields__["__root__"].type_.__dict__["__args__"]:
                if discriminator in instance.__fields__.get(cls.Config.DISCRIMINATOR).type_.__dict__["__args__"]:
                    return instance(**values)
            raise TypeError(f"Incorrect type: {discriminator}")
        except KeyError:
            raise TypeError(f"Incorrect type: {discriminator}")

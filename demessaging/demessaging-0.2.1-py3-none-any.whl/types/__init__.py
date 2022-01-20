"""Custom types module.

This module contains several convenience types to be used with pydantic.
"""


class TypeMixin:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate  # pylint: disable=no-member

    @classmethod
    def __modify_schema__(cls, field_schema):
        type_ = cls.__module__ + "." + cls.__name__
        field_schema["custom_type"] = type_


class TypeMixinSlots:
    """Alternative way for TypeMixin, because xarray objects need __slots__."""

    __slots__ = ()

    @classmethod
    def __get_validators__(cls):
        yield cls.validate  # pylint: disable=no-member

    @classmethod
    def __modify_schema__(cls, field_schema):
        type_ = cls.__module__ + "." + cls.__name__
        field_schema["custom_type"] = type_

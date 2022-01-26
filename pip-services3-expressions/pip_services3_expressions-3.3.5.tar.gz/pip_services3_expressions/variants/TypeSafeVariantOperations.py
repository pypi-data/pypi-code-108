# -*- coding: utf-8 -*-

from .AbstractVariantOperations import AbstractVariantOperations
from .Variant import Variant
from .VariantType import VariantType


class TypeSafeVariantOperations(AbstractVariantOperations):
    """
    Implements a strongly typed (type safe) variant operations manager object.
    """

    def convert(self, value: Variant, new_type: VariantType) -> Variant:
        """
        Converts variant to specified type
        
        :param value: A variant value to be converted.
        :param new_type: A type of object to be returned.
        :return: A converted Variant value.
        """
        if new_type == VariantType.Null:
            result = Variant()
            return result

        if new_type == value.type or new_type == VariantType.Object:
            return value

        if value.type == VariantType.Integer:
            return self.__convert_from_integer(value, new_type)
        if value.type == VariantType.Long:
            return self.__convert_from_long(value, new_type)
        if value.type == VariantType.Float:
            return self.__convert_from_float(value, new_type)
        if value.type == VariantType.Object:
            return value
        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f"to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_integer(self, value: Variant, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Long:
            result.as_long = value.as_integer
            return result
        elif new_type == VariantType.Float:
            result.as_float = value.as_integer
            return result
        elif new_type == VariantType.Double:
            result.as_double = value.as_integer
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f" to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_long(self, value: Variant, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Float:
            result.as_float = value.as_long
            return result
        elif new_type == VariantType.Double:
            result.as_double = value.as_long
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f" to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_float(self, value: Variant, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Double:
            result.as_double = value.as_float
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f" to {self._type_to_string(new_type)} is not supported.")

# -*- coding: utf-8 -*-

import math
from datetime import datetime

from pip_services3_commons.convert import StringConverter, IntegerConverter, LongConverter, FloatConverter, \
    DateTimeConverter, BooleanConverter, DoubleConverter

from .AbstractVariantOperations import AbstractVariantOperations
from .Variant import Variant
from .VariantType import VariantType


class TypeUnsafeVariantOperations(AbstractVariantOperations):
    """
    Implements a type unsafe variant operations manager object.
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
        if new_type == VariantType.String:
            result = Variant()
            result.as_string = StringConverter.to_string(value.as_object)
            return result

        if value.type == VariantType.Null:
            return self.__convert_from_null(new_type)
        elif value.type == VariantType.Integer:
            return self.__convert_from_integer(value, new_type)
        elif value.type == VariantType.Long:
            return self.__convert_from_long(value, new_type)
        elif value.type == VariantType.Float:
            return self.__convert_from_float(value, new_type)
        elif value.type == VariantType.Double:
            return self.__convert_from_double(value, new_type)
        elif value.type == VariantType.DateTime:
            return self.__convert_from_datetime(value, new_type)
        elif value.type == VariantType.TimeSpan:
            return self.__convert_from_time_span(value, new_type)
        elif value.type == VariantType.String:
            return self.__convert_from_string(value, new_type)
        elif value.type == VariantType.Boolean:
            return self.__convert_from_boolean(value, new_type)

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f"to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_null(self, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Integer:
            result.as_integer = 0
            return result
        elif new_type == VariantType.Long:
            result.as_long = 0
            return result
        elif new_type == VariantType.Float:
            result.as_float = 0
            return result
        elif new_type == VariantType.Double:
            result.as_double = 0
            return result
        elif new_type == VariantType.DateTime:
            result.as_datetime = datetime.min
            return result
        elif new_type == VariantType.TimeSpan:
            result.as_time_span = 0
            return result
        elif new_type == VariantType.String:
            result.as_string = "null"
            return result
        elif new_type == VariantType.Boolean:
            result.as_boolean = False
            return result
        elif new_type == VariantType.Object:
            result.as_object = None
            return result
        elif new_type == VariantType.Array:
            result.as_array = None
            return result

        raise Exception(f"Variant convertion from Null to {self._type_to_string(new_type)} is not supported.")

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
        elif new_type == VariantType.DateTime:
            result.as_datetime = datetime.fromtimestamp(value.as_integer)
            return result
        elif new_type == VariantType.TimeSpan:
            result.as_time_span = value.as_integer
            return result
        elif new_type == VariantType.Boolean:
            result.as_boolean = value.as_integer != 0
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f"to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_long(self, value: Variant, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Integer:
            result.as_long = value.as_long
            return result
        elif new_type == VariantType.Float:
            result.as_float = value.as_long
            return result
        elif new_type == VariantType.Double:
            result.as_double = value.as_long
            return result
        elif new_type == VariantType.DateTime:
            result.as_datetime = datetime.fromtimestamp(value.as_long)
            return result
        elif new_type == VariantType.TimeSpan:
            result.as_time_span = value.as_long
            return result
        elif new_type == VariantType.Boolean:
            result.as_boolean = value.as_long != 0
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f"to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_float(self, value: Variant, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Integer:
            result.as_integer = math.trunc(value.as_float)
            return result
        elif new_type == VariantType.Boolean:
            result.as_boolean = value.as_float != 0
            return result
        elif new_type == VariantType.Double:
            result.as_double = value.as_float
            return result
        elif new_type == VariantType.Long:
            result.as_long = math.trunc(value.as_float)
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)}" +
                        f" to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_double(self, value: Variant, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Integer:
            result.as_integer = math.trunc(value.as_double)
            return result
        elif new_type == VariantType.Long:
            result.as_long = math.trunc(value.as_double)
            return result
        elif new_type == VariantType.Float:
            result.as_float = value.as_double
            return result
        elif new_type == VariantType.Boolean:
            result.as_boolean = value.as_double != 0
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f"to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_string(self, value: Variant, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Integer:
            result.as_long = IntegerConverter.to_integer(value.as_string)
            return result
        elif new_type == VariantType.Long:
            result.as_long = LongConverter.to_long(value.as_string)
            return result
        elif new_type == VariantType.Float:
            result.as_float = FloatConverter.to_float(value.as_string)
            return result
        elif new_type == VariantType.Double:
            result.as_double = DoubleConverter.to_double(value.as_string)
            return result
        elif new_type == VariantType.DateTime:
            result.as_datetime = DateTimeConverter.to_datetime(value.as_string)
            return result
        elif new_type == VariantType.TimeSpan:
            result.as_time_span = LongConverter.to_long(value.as_string)
            return result
        elif new_type == VariantType.Boolean:
            result.as_boolean = BooleanConverter.to_boolean(value.as_string)
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f"to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_boolean(self, value: Variant, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Integer:
            result.as_long = 1 if value.as_boolean else 0
            return result
        elif new_type == VariantType.Long:
            result.as_long = 1 if value.as_boolean else 0
            return result
        elif new_type == VariantType.Float:
            result.as_float = 1 if value.as_boolean else 0
            return result
        elif new_type == VariantType.Double:
            result.as_double = 1 if value.as_boolean else 0
            return result
        elif new_type == VariantType.String:
            result.as_string = "true" if value.as_boolean else "false"
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f"to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_datetime(self, value: Variant, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Integer:
            result.as_long = value.as_datetime.timestamp()
            return result
        elif new_type == VariantType.Long:
            result.as_long = value.as_datetime.timestamp()
            return result
        elif new_type == VariantType.String:
            result.as_string = StringConverter.to_string(value.as_datetime.timestamp())
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)} " +
                        f"to {self._type_to_string(new_type)} is not supported.")

    def __convert_from_time_span(self, value: Variant, new_type: VariantType) -> Variant:
        result = Variant()

        if new_type == VariantType.Integer:
            result.as_long = value.as_time_span
            return result
        elif new_type == VariantType.Long:
            result.as_long = value.as_time_span
            return result
        elif new_type == VariantType.String:
            result.as_string = StringConverter.to_string(value.as_time_span)
            return result

        raise Exception(f"Variant convertion from {self._type_to_string(value.type)}" +
                        f"to {self._type_to_string(new_type)} is not supported.")

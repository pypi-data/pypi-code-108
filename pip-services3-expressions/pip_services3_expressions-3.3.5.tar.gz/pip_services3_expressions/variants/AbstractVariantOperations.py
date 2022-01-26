# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

from .IVariantOperations import IVariantOperations
from .Variant import Variant
from .VariantType import VariantType


class AbstractVariantOperations(IVariantOperations, ABC):
    """
    Implements an abstract variant operations manager object.
    """

    def _type_to_string(self, value: VariantType) -> str:
        """
        Convert variant type to string representation

        :param value: a variant type to be converted.
        :return: a string representation of the type.
        """
        types = {
            VariantType.Null: 'Null',
            VariantType.Integer: 'Integer',
            VariantType.Long: 'Long',
            VariantType.Float: 'Float',
            VariantType.Double: 'Double',
            VariantType.String: 'String',
            VariantType.Boolean: 'Boolean',
            VariantType.DateTime: 'DateTime',
            VariantType.TimeSpan: 'TimeSpan',
            VariantType.Object: 'Object',
            VariantType.Array: 'Array'
        }
        try:
            return types[value]
        except KeyError as e:
            return 'Unknown'

    @abstractmethod
    def convert(self, value: Variant, new_type: VariantType) -> Variant:
        """
        Converts variant to specified type

        :param value: A variant value to be converted.
        :param new_type: A type of object to be returned.
        :return: A converted Variant value.
        """

    def add(self, value1: Variant, value2: Variant) -> Variant:
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer + value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long + value2.as_long
            return result
        elif value1.type == VariantType.Float:
            result.as_float = value1.as_float + value2.as_float
            return result
        elif value1.type == VariantType.Double:
            result.as_double = value1.as_double + value2.as_double
            return result
        elif value1.type == VariantType.String:
            result.as_string = value1.as_string + value2.as_string
            return result
        elif value1.type == VariantType.TimeSpan:
            result.as_time_span = value1.as_time_span + value2.as_time_span
            return result

        raise Exception(f"Operation '+' is not supported for type {self._type_to_string(value1.type)}")

    def sub(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '-' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer - value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long - value2.as_long
            return result
        elif value1.type == VariantType.Float:
            result.as_float = value1.as_float - value2.as_float
            return result
        elif value1.type == VariantType.Double:
            result.as_double = value1.as_double - value2.as_double
            return result
        elif value1.type == VariantType.DateTime:
            result.as_string = value1.as_datetime - value2.as_datetime
            return result
        elif value1.type == VariantType.TimeSpan:
            result.as_time_span = value1.as_time_span - value2.as_time_span
            return result

        raise Exception(f"Operation '-' is not supported for type {self._type_to_string(value1.type)}")

    def mul(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '*' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer * value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long * value2.as_long
            return result
        elif value1.type == VariantType.Float:
            result.as_float = value1.as_float * value2.as_float
            return result
        elif value1.type == VariantType.Double:
            result.as_double = value1.as_double * value2.as_double
            return result

        raise Exception(f"Operation '*' is not supported for type {self._type_to_string(value1.type)}")

    def div(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '/' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = int(value1.as_integer / value2.as_integer)
            return result
        elif value1.type == VariantType.Long:
            result.as_long = int(value1.as_long / value2.as_long)
            return result
        elif value1.type == VariantType.Float:
            result.as_float = value1.as_float / value2.as_float
            return result
        elif value1.type == VariantType.Double:
            result.as_double = value1.as_double / value2.as_double
            return result

        raise Exception(f"Operation '/' is not supported for type {self._type_to_string(value1.type)}")

    def mod(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '%' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer % value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long % value2.as_long
            return result

        raise Exception(f"Operation '%' is not supported for type {self._type_to_string(value1.type)}")

    def pow(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '^' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Performs operation.
        if value1.type in [VariantType.Integer, VariantType.Long, VariantType.Float, VariantType.Double]:
            # Converts second operand to the type of the first operand.
            value1 = self.convert(value1, VariantType.Float)
            value2 = self.convert(value2, VariantType.Float)
            result.as_float = value1.as_float + value2.as_float

        raise Exception(f"Operation '^' is not supported for type {self._type_to_string(value1.type)}")

    def and_(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs AND operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer and value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long and value2.as_long
            return result
        elif value1.type == VariantType.Boolean:
            result.as_boolean = value1.as_boolean and value2.as_boolean
            return result

        raise Exception(f"Operation 'AND' is not supported for type {self._type_to_string(value1.type)}")

    def or_(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs OR operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer or value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long or value2.as_long
            return result
        elif value1.type == VariantType.Boolean:
            result.as_boolean = value1.as_boolean or value2.as_boolean
            return result

        raise Exception(f"Operation 'OR' is not supported for type {self._type_to_string(value1.type)}")

    def xor(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs XOR operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer ^ value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long ^ value2.as_long
            return result
        elif value1.type == VariantType.Boolean:
            result.as_boolean = value1.as_boolean ^ value2.as_boolean
            return result

        raise Exception(f"Operation 'XOR' is not supported for type {self._type_to_string(value1.type)}")

    def lsh(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '<<' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer << value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long << value2.as_long
            return result

        raise Exception(f"Operation '<<' is not supported for type {self._type_to_string(value1.type)}")

    def rsh(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '>>' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer >> value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long >> value2.as_long
            return result

        raise Exception(f"Operation '>>' is not supported for type {self._type_to_string(value1.type)}")

    def not_(self, value: Variant) -> Variant:
        """
        Performs NOT operation for a variant.

        :param value: The operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value.type == VariantType.Null:
            return result

        # Performs operation.
        if value.type == VariantType.Integer:
            result.as_integer = ~value.as_integer
            return result
        elif value.type == VariantType.Long:
            result.as_long = ~value.as_long
            return result
        elif value.type == VariantType.Boolean:
            result.as_boolean = ~value.as_boolean
            return result

        raise Exception(f"Operation NOT is not supported for type {self._type_to_string(value.type)}")

    def negative(self, value: Variant) -> Variant:
        """
        Performs unary '-' operation for a variant.

        :param value: The operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value.type == VariantType.Null:
            return result

        # Performs operation.
        if value.type == VariantType.Integer:
            result.as_integer = -value.as_integer
            return result
        elif value.type == VariantType.Long:
            result.as_long = -value.as_long
            return result
        elif value.type == VariantType.Float:
            result.as_float = -value.as_float
            return result
        elif value.type == VariantType.Double:
            result.as_double = -value.as_double
            return result

        raise Exception(f"Operation '-' is not supported for type {self._type_to_string(value.type)}")

    def equal(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '=' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null and value2.type == VariantType.Null:
            result.as_boolean = True
            return result

        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            result.as_boolean = False
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_boolean = value1.as_integer == value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_boolean = value1.as_long == value2.as_long
            return result
        elif value1.type == VariantType.Float:
            result.as_boolean = value1.as_float == value2.as_float
            return result
        elif value1.type == VariantType.Double:
            result.as_boolean = value1.as_double == value2.as_double
            return result
        elif value1.type == VariantType.String:
            result.as_boolean = value1.as_string.rstrip('.0') == value2.as_string.rstrip('.0')
            return result
        elif value1.type == VariantType.TimeSpan:
            result.as_boolean = value1.as_time_span == value2.as_time_span
            return result
        elif value1.type == VariantType.DateTime:
            result.as_boolean = value1.as_datetime == value2.as_datetime
            return result
        elif value1.type == VariantType.Boolean:
            result.as_boolean = value1.as_boolean == value2.as_boolean
            return result
        elif value1.type == VariantType.Object:
            result.as_boolean = value1.as_object == value2.as_object
            return result

        raise Exception(f"Operation '==' is not supported for type {self._type_to_string(value1.type)}")

    def not_equal(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '<>' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null and value2.type == VariantType.Null:
            result.as_boolean = True
            return result

        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            result.as_boolean = False
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer != value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long != value2.as_long
            return result
        elif value1.type == VariantType.Float:
            result.as_float = value1.as_float != value2.as_float
            return result
        elif value1.type == VariantType.Double:
            result.as_double = value1.as_double != value2.as_double
            return result
        elif value1.type == VariantType.String:
            result.as_string = value1.as_string != value2.as_string
            return result
        elif value1.type == VariantType.TimeSpan:
            result.as_time_span = value1.as_time_span != value2.as_time_span
            return result
        elif value1.type == VariantType.DateTime:
            result.as_datetime = value1.as_datetime != value2.as_datetime
            return result
        elif value1.type == VariantType.Boolean:
            result.as_boolean = value1.as_boolean != value2.as_boolean
            return result
        elif value1.type == VariantType.Object:
            result.as_object = value1.as_object != value2.as_object
            return result

        raise Exception(f"Operation '<>' is not supported for type {self._type_to_string(value1.type)}")

    def more(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '>' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            result.as_boolean = False
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_boolean = value1.as_integer > value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_boolean = value1.as_long > value2.as_long
            return result
        elif value1.type == VariantType.Float:
            result.as_boolean = value1.as_float > value2.as_float
            return result
        elif value1.type == VariantType.Double:
            result.as_boolean = value1.as_double > value2.as_double
            return result
        elif value1.type == VariantType.String:
            result.as_boolean = value1.as_string > value2.as_string
            return result
        elif value1.type == VariantType.TimeSpan:
            result.as_boolean = value1.as_time_span > value2.as_time_span
            return result
        elif value1.type == VariantType.DateTime:
            result.as_boolean = value1.as_datetime.timestamp() > value2.as_datetime.timestamp()
            return result

        raise Exception(f"Operation '>' is not supported for type {self._type_to_string(value1.type)}")

    def less(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '<' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            result.as_boolean = False
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer < value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long < value2.as_long
            return result
        elif value1.type == VariantType.Float:
            result.as_float = value1.as_float < value2.as_float
            return result
        elif value1.type == VariantType.Double:
            result.as_double = value1.as_double < value2.as_double
            return result
        elif value1.type == VariantType.String:
            result.as_string = value1.as_string < value2.as_string
            return result
        elif value1.type == VariantType.TimeSpan:
            result.as_time_span = value1.as_time_span < value2.as_time_span
            return result
        elif value1.type == VariantType.DateTime:
            result.as_datetime = value1.as_datetime.timestamp() < value2.as_datetime.timestamp()
            return result

        raise Exception(f"Operation '<' is not supported for type {self._type_to_string(value1.type)}")

    def more_equal(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '>=' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            result.as_boolean = False
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer >= value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long >= value2.as_long
            return result
        elif value1.type == VariantType.Float:
            result.as_float = value1.as_float >= value2.as_float
            return result
        elif value1.type == VariantType.Double:
            result.as_double = value1.as_double >= value2.as_double
            return result
        elif value1.type == VariantType.String:
            result.as_string = value1.as_string >= value2.as_string
            return result
        elif value1.type == VariantType.TimeSpan:
            result.as_time_span = value1.as_time_span >= value2.as_time_span
            return result
        elif value1.type == VariantType.DateTime:
            result.as_datetime = value1.as_datetime.timestamp() >= value2.as_datetime.timestamp()
            return result

        raise Exception(f"Operation '>=' is not supported for type {self._type_to_string(value1.type)}")

    def less_equal(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '<=' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            result.as_boolean = False
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, value1.type)

        # Performs operation.
        if value1.type == VariantType.Integer:
            result.as_integer = value1.as_integer <= value2.as_integer
            return result
        elif value1.type == VariantType.Long:
            result.as_long = value1.as_long <= value2.as_long
            return result
        elif value1.type == VariantType.Float:
            result.as_float = value1.as_float <= value2.as_float
            return result
        elif value1.type == VariantType.Double:
            result.as_double = value1.as_double <= value2.as_double
            return result
        elif value1.type == VariantType.String:
            result.as_string = value1.as_string <= value2.as_string
            return result
        elif value1.type == VariantType.TimeSpan:
            result.as_time_span = value1.as_time_span <= value2.as_time_span
            return result
        elif value1.type == VariantType.DateTime:
            result.as_datetime = value1.as_datetime.timestamp() <= value2.as_datetime.timestamp()
            return result

        raise Exception(f"Operation '<=' is not supported for type {self._type_to_string(value1.type)}")

    def in_(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs IN operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            result.as_boolean = False
            return result

        # Processes null arrays.
        if value1.as_object is None:
            result.as_boolean = False
            return result

        if value1.type == VariantType.Array:
            array = value1.as_array
            for element in array:
                eq = self.equal(value2, element)
                if eq.type == VariantType.Boolean and eq.as_boolean:
                    result.as_boolean = True
                    return result

            result.as_boolean = False
            return result

        return self.equal(value1, value2)

    def get_element(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs [] operation for two variants.
        
        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """
        result = Variant()

        # Processes VariantType.Null values.
        if value1.type == VariantType.Null or value2.type == VariantType.Null:
            return result

        # Converts second operand to the type of the first operand.
        value2 = self.convert(value2, VariantType.Integer)

        if value1.type == VariantType.Array:
            return value1.get_by_index(value2.as_integer)
        elif value1.type == VariantType.String:
            result.as_string = value1.as_string[value2.as_integer]
            return result

        raise Exception(f"Operation '[]' is not supported for type {self._type_to_string(value1.type)}")

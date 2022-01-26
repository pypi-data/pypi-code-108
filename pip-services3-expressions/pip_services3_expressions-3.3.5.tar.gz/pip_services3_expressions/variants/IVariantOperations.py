# -*- coding: utf-8 -*-

from abc import ABC

from pip_services3_expressions.variants.Variant import Variant
from pip_services3_expressions.variants.VariantType import VariantType


class IVariantOperations(ABC):
    """
    Defines an interface for variant operations manager.
    """

    def convert(self, value: Variant, new_type: VariantType) -> Variant:
        """
        Converts variant to specified type

        :param value: A variant value to be converted.
        :param new_type: A type of object to be returned.
        :return: A converted Variant value.
        """

    def add(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '+' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def sub(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '-' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def mul(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '*' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def div(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '/' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def mod(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '%' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def pow(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '^' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def and_(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs AND operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def or_(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs OR operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def xor(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs XOR operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def lsh(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs << operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def rsh(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs >> operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def not_(self, value: Variant) -> Variant:
        """
        Performs NOT operation for two variants.

        :param value: The operand for this operation.
        :return: A result variant object.
        """

    def negative(self, value: Variant) -> Variant:
        """
        Performs unary '-' operation for a variant.

        :param value: The operand for this operation.
        :return: A result variant object.
        """

    def equal(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '=' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def not_equal(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '<>' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def more(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '<' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def less(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '>' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def more_equal(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '<=' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def less_equal(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs '>=' operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def in_(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs IN operation for two variants.

        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

    def get_element(self, value1: Variant, value2: Variant) -> Variant:
        """
        Performs [] operation for two variants.
        
        :param value1: The first operand for this operation.
        :param value2: The second operand for this operation.
        :return: A result variant object.
        """

# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import inspect
import collections

import numpy as np


class ArithmeticFunctions:

    @staticmethod
    def add(a, b):
        """
        Add a and b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            The sum of a and b.

        Examples
        --------
        >>> 3 + 2
        5
        >>> 3 + 4
        7
        """
        return a + b

    @staticmethod
    def subtract(a, b):
        """
        Subtract b from a.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            The difference of a and b.

        Examples
        --------
        >>> 3 - 2
        1
        >>> 3 - 4
        -1
        """
        return a - b

    @staticmethod
    def multiply(a, b):
        """
        Multiply a and b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            The product of a and b.

        Examples
        --------
        >>> 3 * 2
        6
        >>> 3 * 4
        12
        """
        return a * b

    @staticmethod
    def power(a, b):
        """
        Raise a to the b-th power.

        Parameters
        ----------
        a : np.array or scalar
            base
        b : np.array or scalar
            exponent

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            a raised to the b-th power.

        Examples
        --------
        >>> 3 ** 2
        9
        >>> 3 ** 4
        81
        """
        return a ** b

    @staticmethod
    def divide(a, b):
        """
        Divide a by b (true division).

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            Quotent of a divided by b.

        Examples
        --------
        >>> 3 / 2
        1.5
        >>> 3 / 4
        0.75
        """
        return a / b

    @staticmethod
    def divide_floor(a, b):
        """
        Divide a by b (floor division or integer division).
        Floor divison produces integral results similar to computing np.floor(a / b)
        and converting the result to integer.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            Quotent of a divided by b.

        Examples
        --------
        >>> 3 // 2
        1
        >>> 3 // 4
        0
        """
        return a // b

    @staticmethod
    def modulo(a, b):
        """
        Modulo of a and b (remainder of the division of a and b).
        The result has the same sign as the divisor, b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            Remainder of a divided by b.

        Examples
        --------
        >>> 3 % 2
        1
        >>> 3 % 4
        3
        """
        return a % b

    @staticmethod
    def divide_modulo(a, b):
        """
        Division and Modulo of a and b.
        Similar to combining (a // b, a % b).

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        tuple of np.array or scalar
            (Floor division of a and b, Remainder of a divided by b)

        Examples
        --------
        >>> divmod(3, 2)
        (1, 1)
        >>> divmod(3, 4)
        (0, 3)
        """
        return a % b


class ComparatorFunctions:

    @staticmethod
    def equal(a, b):
        """
        Test equality of a and b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when a is equal to b and False otherwise.

        Examples
        --------
        >>> 3 == 2
        False
        >>> 3 == 3
        True
        >>> 3 == 4
        False
        """
        return a == b

    @staticmethod
    def not_equal(a, b):
        """
        Test NOT (negated) equality of a and b.
        Equivalent to not (a == b).

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when a is not equal to b and False otherwise.

        Examples
        --------
        >>> 3 != 2
        True
        >>> 3 != 3
        False
        >>> 3 != 4
        True
        """
        return a != b

    @staticmethod
    def greater(a, b):
        """
        Test if a is greater than b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when a is greater than b and False otherwise.

        Examples
        --------
        >>> 3 > 2
        True
        >>> 3 > 3
        False
        >>> 3 > 4
        False
        """
        return a > b

    @staticmethod
    def less(a, b):
        """
        Test if a is less than b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when a is less than b and False otherwise.

        Examples
        --------
        >>> 3 < 2
        False
        >>> 3 < 3
        False
        >>> 3 < 4
        True
        """
        return a < b

    @staticmethod
    def greater_or_equal(a, b):
        """
        Test if a is greater than or equal to b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when a is greater than or equal to b and False otherwise.

        Examples
        --------
        >>> 3 >= 2
        True
        >>> 3 >= 3
        True
        >>> 3 >= 4
        False
        """
        return a >= b

    @staticmethod
    def less_or_equal(a, b):
        """
        Test if a is less than or equal to b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when a is less than or equal to b and False otherwise.

        Examples
        --------
        >>> 3 <= 2
        False
        >>> 3 <= 3
        True
        >>> 3 <= 4
        True
        """
        return a <= b


class LogicFunctions:

    @staticmethod
    def not_(a):
        """
        Compute truth value of NOT (negated) a.

        Parameters
        ----------
        a : np.array or scalar

        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when bool(a) is False and False otherwise.

        Examples
        --------
        >>> np.logical_not(True)
        False
        >>> np.logical_not(False)
        True
        """
        return np.logical_not(a)

    @staticmethod
    def and_(a, b):
        """
        Compute truth value of logical AND of a and b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when bool(a) and bool(b) are both True and False otherwise.

        Examples
        --------
        >>> np.logical_and(False, False)
        False
        >>> np.logical_and(False, True)
        False
        >>> np.logical_and(True, False)
        False
        >>> np.logical_and(True, True)
        True
        """
        return np.logical_and(a, b)

    @staticmethod
    def nand(a, b):
        """
        Compute truth value of logical NAND of a and b.
        Equivalent to np.logical_not(np.logical_and(a, b))

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when bool(a) and bool(b) are both False and True otherwise.

        Examples
        --------
        >>> np.logical_not(np.logical_and(False, False))
        True
        >>> np.logical_not(np.logical_and(False, True))
        True
        >>> np.logical_not(np.logical_and(True, False))
        True
        >>> np.logical_not(np.logical_and(True, True))
        False
        """
        return np.logical_not(np.logical_and(a, b))

    @staticmethod
    def or_(a, b):
        """
        Compute truth value of logical OR of a and b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when bool(a) or bool(b) is True and False otherwise.

        Examples
        --------
        >>> np.logical_or(False, False)
        False
        >>> np.logical_or(False, True)
        True
        >>> np.logical_or(True, False)
        True
        >>> np.logical_or(True, True)
        True
        """
        return np.logical_or(a, b)

    @staticmethod
    def nor(a, b):
        """
        Compute truth value of logical NOR of a and b.
        Equivalent to np.logical_not(np.logical_or(a, b))

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when bool(a) or bool(b) is False and True otherwise.

        Examples
        --------
        >>> np.logical_not(np.logical_or(False, False))
        True
        >>> np.logical_not(np.logical_or(False, True))
        False
        >>> np.logical_not(np.logical_or(True, False))
        False
        >>> np.logical_not(np.logical_or(True, True))
        False
        """
        return np.logical_not(np.logical_or(a, b))

    @staticmethod
    def xor(a, b):
        """
        Compute truth value of logical XOR of a and b.

        Parameters
        ----------
        a : np.array or scalar
        b : np.array or scalar

        If both a and b are arrays they need to have the same dimensions.
        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            True when one but not both of of bool(a) and bool(b) are True and
            False otherwise.

        Examples
        --------
        >>> np.logical_xor(False, False)
        False
        >>> np.logical_xor(False, True)
        True
        >>> np.logical_xor(True, False)
        True
        >>> np.logical_xor(True, True)
        False
        """
        return np.logical_xor(a, b)

    @staticmethod
    def any_(a):
        """
        True if any value in sequence a is truthy.

        Parameters
        ----------
        a : sequence

        Returns
        -------
        bool
            True when bool(x) is True for any x in sequence a and
            False otherwise.

        Examples
        --------
        >>> any([])
        False
        >>> any([False, False])
        False
        >>> any([False, True])
        True
        >>> any([True, False])
        True
        >>> any([True, True])
        True
        """
        return any(a)

    @staticmethod
    def all_(a):
        """
        True if all values in sequence a are truthy.

        Parameters
        ----------
        a : sequence

        Returns
        -------
        bool
            True when bool(x) is True for all x in sequence a and
            False otherwise.

        Examples
        --------
        >>> all([])
        True
        >>> all([False, False])
        False
        >>> all([False, True])
        False
        >>> all([True, False])
        False
        >>> all([True, True])
        True
        """
        return all(a)


class BitwiseFunctions:

    @staticmethod
    def not_(a):
        """
        Compute bitwise NOT (negated) a.

        Bitwise operations considers numeric values as sequences of bits and
        applies the operation to each bit.

        Signed integers are interpreted according to the two's complement.
        Numpy booleans are considered as single bit (0, 1).

        Parameters
        ----------
        a : np.array or scalar

        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            1 in each bit position where a is 0 and 1 in the others.

        Examples
        --------
        # 00000000
        >>> ~np.array([0], dtype=np.uint8)
        # 11111111
        np.array([255], dtype=np.uint8)
        # 10101010
        >>> ~np.array([170], dtype=np.uint8)
        # 01010101
        np.array([85], dtype=np.uint8)

        >>> ~np.array([False])
        np.array([True])
        >>> ~np.array([True])
        np.array([False])
        """
        return ~a

    @staticmethod
    def and_(a, b):
        """
        Compute bitwise AND of a and b.

        Bitwise operations considers numeric values as sequences of bits and
        applies the operation to each bit.

        Parameters
        ----------
        a : np.array or scalar

        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            1 in each bit position where a and b are both 1 and 0 in the
            others.

        Examples
        --------
        # 00000001 & 11111111
        >>> 1 & 255
        # 00000001
        1
        # 01010110 & 10010001
        >>> 86 & 145
        # 00010000
        16

        >>> False & False
        False
        >>> False & True
        False
        >>> True & False
        False
        >>> True & True
        True
        """
        return a & b

    @staticmethod
    def or_(a, b):
        """
        Compute bitwise OR of a and b.

        Bitwise operations considers numeric values as sequences of bits and
        applies the operation to each bit.

        Parameters
        ----------
        a : np.array or scalar

        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            1 in each bit position where either a or b are 1 and 0 in the
            others.

        Examples
        --------
        # 00000001 | 11111111
        >>> 1 | 255
        # 11111111
        255
        # 01010110 & 10010001
        >>> 86 & 145
        # 11010111
        215

        >>> False | False
        False
        >>> False | True
        True
        >>> True | False
        True
        >>> True | True
        True
        """
        return a | b

    @staticmethod
    def xor(a, b):
        """
        Compute bitwise XOR of a and b.

        Bitwise operations considers numeric values as sequences of bits and
        applies the operation to each bit.

        Parameters
        ----------
        a : np.array or scalar

        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            1 in each bit position where either a or b but not both are 1 and 0
            in the others.

        Examples
        --------
        # 00000001 ^ 11111111
        >>> 1 ^ 255
        # 11111110
        254
        # 01010110 & 10010001
        >>> 86 & 145
        # 11000111
        215

        >>> False ^ False
        False
        >>> False ^ True
        True
        >>> True ^ False
        True
        >>> True ^ True
        False
        """
        return a ^ b

    @staticmethod
    def left_shift(a, b):
        """
        Compute bitwise left shift of a by b.

        Bitwise operations considers numeric values as sequences of bits
        applies the operation to each bit.

        Parameters
        ----------
        a : np.array or scalar

        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            Shifted a to the left by b bit positions.

        Examples
        --------
        # 00000001 << 1
        >>> 1 << 1
        # 00000010
        2
        # 01010110 << 2
        >>> 86 << 2
        # 0101011000
        344
        # 01010110 << 2
        >>> np.array([86], dtype=np.uint8) << 2
        # 01011000
        >> np.array([88], dtype=np.uint8)
        """
        return a << b

    @staticmethod
    def right_shift(a, b):
        """
        Compute bitwise right shift of a by b.

        Bitwise operations considers numeric values as sequences of bits
        applies the operation to each bit.

        Signed integers are interpreted according to the two's complement
        and the sign bit is preserved when shifting.

        Parameters
        ----------
        a : np.array or scalar

        Operates element-wise for arrays.

        Returns
        -------
        np.array or scalar
            Shifted a to the right by b bit positions.

        Examples
        --------
        # 00000001 >> 1
        >>> 1 >> 1
        # 00000000
        2
        # 01010110 << 2
        >>> 86 >> 2
        # 00010101
        21

        # 10000000 >> 2
        >>> np.array([-128], dtype=np.int8) << 2
        # 11100000
        np.array([-32], dtype=int8)
        """
        return a >> b


class StatisticFunctions:

    @staticmethod
    def sum_(a):
        """
        Sum sequence a.

        Parameters
        ----------
        a : sequence

        Returns
        -------
        scalar
            Sum of elements in sequence a.

        Examples
        --------
        >>> sum([])
        0
        >>> sum([1, 2, 3, 4])
        10
        """
        return sum(a)

    @staticmethod
    def min_(a):
        """
        Compute minimum value of non-empty sequence a.

        Parameters
        ----------
        a : sequence

        Returns
        -------
        scalar
            Minimum value of elements in sequence a.

        Examples
        --------
        >>> min([1])
        1
        >>> min([1, 2, 3, 4])
        1
        >>> min([4, 2, 1, 4])
        1
        """
        return min(a)

    @staticmethod
    def max_(a):
        """
        Compute maximum value of non-empty sequence a.

        Parameters
        ----------
        a : sequence

        Returns
        -------
        scalar
            Maximum value of elements in sequence a.

        Examples
        --------
        >>> max([1])
        1
        >>> max([1, 2, 3, 4])
        4
        >>> max([4, 2, 1, 4])
        4
        """
        return max(a)

    @staticmethod
    def mean(a):
        """
        Compute mean value of non-empty sequence a.

        Parameters
        ----------
        a : sequence

        Returns
        -------
        scalar
            Mean value of elements in sequence a.

        Examples
        --------
        >>> np.mean([1])
        1
        >>> np.mean([1, 2, 3, 4])
        2.5
        >>> np.mean([4, 2, 1, 4])
        3.25
        """
        return np.mean(a)

    @staticmethod
    def median(a):
        """
        Compute median value of non-empty sequence a.

        Parameters
        ----------
        a : sequence

        Returns
        -------
        scalar
            Median value of elements in sequence a.

        Examples
        --------
        >>> np.median([1])
        1.0
        >>> np.median([1, 2, 3, 4])
        2.5
        >>> np.median([1, 2, 3, 4, 5])
        3.0
        """
        res = np.ma.median(a)
        if res is np.ma.masked:
            res = np.float64('nan')
        return res

    @staticmethod
    def std(a):
        """
        Compute standard deviation of non-empty sequence a.

        Parameters
        ----------
        a : sequence

        Returns
        -------
        scalar
            Standard deviation of sequence a.

        Examples
        --------
        >>> np.std([1])
        0.0
        >>> np.std([1, 1, 1, 1, 1])
        0.0
        >>> np.std([1, 2, 3, 2, 1])
        0.7483314773547883
        >>> np.std([1, 2, 3, 4, 5])
        1.4142135623730951
        """
        return np.std(a)

    @staticmethod
    def percentile(a, b):
        """
        Compute the value of the b-th percentile of sequence a.

        Parameters
        ----------
        a : sequence
        b : scalar
            Percentile value, 0-100.

        Returns
        -------
        scalar
            b-th percentile of input sequence a.

        Examples
        --------
        >>> np.percentile(range(1000), 50)
        499.5
        >>> np.percentile(range(1000), 90)
        899.1
        >>> np.percentile(range(1000), 99)
        989.1
        """
        return np.percentile(a, b)


ARITHMETICS_OPS = [
    ("+ (add)", "a + b",
     inspect.getdoc(ArithmeticFunctions.add)),
    ("- (subtract)", "a - b",
     inspect.getdoc(ArithmeticFunctions.subtract)),
    ("* (multiply)", "a * b",
     inspect.getdoc(ArithmeticFunctions.multiply)),
    ("** (power)", "a ** b",
     inspect.getdoc(ArithmeticFunctions.power)),
    ("/ (true divide)", "a / b",
     inspect.getdoc(ArithmeticFunctions.divide)),
    ("// (floor divide)", "a // b",
     inspect.getdoc(ArithmeticFunctions.divide_floor)),
    ("% (modulo)", "a % b",
     inspect.getdoc(ArithmeticFunctions.modulo)),
     ("divmod (floor divide, modulo)", "divmod(a, b)",
      inspect.getdoc(ArithmeticFunctions.divide_modulo)),
]


COMPARATORS = [
    ("== (equal)", "a == b",
     inspect.getdoc(ComparatorFunctions.equal)),
    ("!= (not equal)", "a != b",
     inspect.getdoc(ComparatorFunctions.not_equal)),
    ("> (greater than)", "a > b",
     inspect.getdoc(ComparatorFunctions.greater)),
    ("< (less than)", "a < b",
     inspect.getdoc(ComparatorFunctions.less)),
    (">= (greater or equal)", "a >= b",
     inspect.getdoc(ComparatorFunctions.greater_or_equal)),
    ("<= (less or equal)", "a <= b",
     inspect.getdoc(ComparatorFunctions.less_or_equal)),
]


LOGIC_OPS = [
    ("not", "np.logical_not(a)",
     inspect.getdoc(LogicFunctions.not_)),
    ("and", "np.logical_and(a, b)",
     inspect.getdoc(LogicFunctions.and_)),
    ("nand", "ca.nand(a, b)",
     inspect.getdoc(LogicFunctions.nand)),
    ("or", "np.logical_or(a, b)",
     inspect.getdoc(LogicFunctions.or_)),
    ("xor", "np.logical_xor(a, b)",
     inspect.getdoc(LogicFunctions.xor)),
    ("nor", "ca.nor(a, b)",
     inspect.getdoc(LogicFunctions.nor)),
    ("all", "all(a)",
     inspect.getdoc(LogicFunctions.all_)),
    ("any", "any(a)",
     inspect.getdoc(LogicFunctions.any_)),
]


BITWISE = [
    ("~ (not)", "~a",
     inspect.getdoc(BitwiseFunctions.not_)),
    ("& (and)", "a & b",
     inspect.getdoc(BitwiseFunctions.and_)),
    ("| (or)", "a | b",
     inspect.getdoc(BitwiseFunctions.or_)),
    ("^ (xor)", "a ^ b",
     inspect.getdoc(BitwiseFunctions.xor)),
    ("<< (left shift)", "a << b",
     inspect.getdoc(BitwiseFunctions.left_shift)),
    (">> (right shift)", "a >> b",
     inspect.getdoc(BitwiseFunctions.right_shift)),
]


OPERATORS = collections.OrderedDict([
    ("Arithmetics", ARITHMETICS_OPS),
    ("Comparators", COMPARATORS),
    ("Logics", LOGIC_OPS),
    ("Bitwise", BITWISE),
])


STATISTICS = [
    ("Sum", "sum(a)",
     inspect.getdoc(StatisticFunctions.sum_)),
    ("Min", "min(a)",
     inspect.getdoc(StatisticFunctions.min_)),
    ("Max", "max(a)",
     inspect.getdoc(StatisticFunctions.max_)),
    ("Mean", "np.mean(a)",
     inspect.getdoc(StatisticFunctions.mean)),
    ("Standard deviation", "np.std(a)",
     inspect.getdoc(StatisticFunctions.std)),
    ("Median", "ca.median(a)",
     inspect.getdoc(StatisticFunctions.median)),
    ("Percentile", "np.percentile(a, value)",
     inspect.getdoc(StatisticFunctions.percentile)),
]


GUI_DICT = collections.OrderedDict([
        ("Operators", OPERATORS),
        ("Statistics", STATISTICS),
    ])


class LogicOperator(object):
    nand = LogicFunctions.nand
    nor = LogicFunctions.nor


class Statistics(object):
    median = StatisticFunctions.median

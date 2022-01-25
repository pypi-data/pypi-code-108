"""
description: this module provide the class AssertThat.
"""

import inspect
import math
import os
import re

from collections.abc import Iterable
from _pistar.utilities.exceptions import AssertionContainsDuplicatesException
from _pistar.utilities.exceptions import AssertionContainsException
from _pistar.utilities.exceptions import AssertionDoesNotContainDuplicatesException
from _pistar.utilities.exceptions import AssertionDoesNotContainException
from _pistar.utilities.exceptions import AssertionDoesNotExistException
from _pistar.utilities.exceptions import AssertionDoesNotMatchRegexException
from _pistar.utilities.exceptions import AssertionEndsWithException
from _pistar.utilities.exceptions import AssertionExistException
from _pistar.utilities.exceptions import AssertionIsAfterException
from _pistar.utilities.exceptions import AssertionIsAlphaException
from _pistar.utilities.exceptions import AssertionIsBeforeException
from _pistar.utilities.exceptions import AssertionIsBetweenException
from _pistar.utilities.exceptions import AssertionIsCloseToException
from _pistar.utilities.exceptions import AssertionIsDigitException
from _pistar.utilities.exceptions import AssertionIsDirectoryException
from _pistar.utilities.exceptions import AssertionIsEmptyException
from _pistar.utilities.exceptions import AssertionIsEqualToException
from _pistar.utilities.exceptions import AssertionIsFileException
from _pistar.utilities.exceptions import AssertionIsGreaterThanException
from _pistar.utilities.exceptions import AssertionIsGreaterThanOrEqualToException
from _pistar.utilities.exceptions import AssertionIsInException
from _pistar.utilities.exceptions import AssertionIsInfException
from _pistar.utilities.exceptions import AssertionIsInstanceOfException
from _pistar.utilities.exceptions import AssertionIsIterableException
from _pistar.utilities.exceptions import AssertionIsLengthException
from _pistar.utilities.exceptions import AssertionIsLessThanException
from _pistar.utilities.exceptions import AssertionIsLessThanOrEqualToException
from _pistar.utilities.exceptions import AssertionIsLowerException
from _pistar.utilities.exceptions import AssertionIsNanException
from _pistar.utilities.exceptions import AssertionIsNegativeException
from _pistar.utilities.exceptions import AssertionIsNonStrictlyDecreasingException
from _pistar.utilities.exceptions import AssertionIsNonStrictlyIncreasingException
from _pistar.utilities.exceptions import AssertionIsNoneException
from _pistar.utilities.exceptions import AssertionIsNotAlphaException
from _pistar.utilities.exceptions import AssertionIsNotBetweenException
from _pistar.utilities.exceptions import AssertionIsNotCloseToException
from _pistar.utilities.exceptions import AssertionIsNotDigitException
from _pistar.utilities.exceptions import AssertionIsNotDirectoryException
from _pistar.utilities.exceptions import AssertionIsNotEmptyException
from _pistar.utilities.exceptions import AssertionIsNotEqualToException
from _pistar.utilities.exceptions import AssertionIsNotFileException
from _pistar.utilities.exceptions import AssertionIsNotInException
from _pistar.utilities.exceptions import AssertionIsNotInfException
from _pistar.utilities.exceptions import AssertionIsNotInstanceOfException
from _pistar.utilities.exceptions import AssertionIsNotIterableException
from _pistar.utilities.exceptions import AssertionIsNotLengthException
from _pistar.utilities.exceptions import AssertionIsNotNanException
from _pistar.utilities.exceptions import AssertionIsNotNoneException
from _pistar.utilities.exceptions import AssertionIsNotSameAsException
from _pistar.utilities.exceptions import AssertionIsNotTypeOfException
from _pistar.utilities.exceptions import AssertionIsNotZeroException
from _pistar.utilities.exceptions import AssertionIsPositiveException
from _pistar.utilities.exceptions import AssertionIsSameAsException
from _pistar.utilities.exceptions import AssertionIsStrictlyDecreasingException
from _pistar.utilities.exceptions import AssertionIsStrictlyIncreasingException
from _pistar.utilities.exceptions import AssertionIsTypeOfException
from _pistar.utilities.exceptions import AssertionIsUpperException
from _pistar.utilities.exceptions import AssertionIsZeroException
from _pistar.utilities.exceptions import AssertionMatchesRegexException
from _pistar.utilities.exceptions import AssertionMatchesSchemaException
from _pistar.utilities.exceptions import AssertionStartsWithException
from _pistar.utilities.exceptions import AssertionTypeMismatchException
from _pistar.utilities.function_tools import get_and_text
from _pistar.utilities.function_tools import get_or_text
from _pistar.utilities.match_schema import match_schema


class AssertThat:
    """
    description: assert class, and all assert method will use in testcase
    attribute:
        __value:
            description: object to assert.
            permission: private
        file_name:
            type: str
            description: name of the file in which assertion is made.
            permission: public
        line_number:
            type: str
            description: line number in which assertion is made.
    """

    __value = None

    file_name = None
    line_number = None

    def assert_type(self, *args):
        if not isinstance(self.__value, args):
            raise AssertionTypeMismatchException(
                self,
                f"the value {self.__value} except type is {get_or_text([item.__name__ for item in args])}, but its "
                f"type is '{type(self.__value).__name__}' "
            )

    def assert_args_empty(self, args):
        if not args:
            raise AssertionTypeMismatchException(self, "the args should contains one type name at least")

    def __init__(self, value):
        self.__value = value
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        self.file_name = caller.filename
        self.line_number = caller.lineno

    def is_none(self):
        """
        description: assert the object is None.
        """

        if self.__value is None:
            return self

        raise AssertionIsNoneException(assertion=self, assert_value=repr(self.__value))

    def is_not_none(self):
        """
        description: assert the object is not None.
        """

        if self.__value is not None:
            return self

        raise AssertionIsNotNoneException(assertion=self, assert_value=repr(self.__value))

    def is_lower(self):
        """
        description: assert whether all letters in object are in lower case.
        """
        self.assert_type(str)

        if self.__value.islower():
            return self

        raise AssertionIsLowerException(assertion=self, assert_value=repr(self.__value))

    def is_upper(self):
        """
        description: assert whether all letters in object are in upper case.
        """

        self.assert_type(str)

        if self.__value.isupper():
            return self

        raise AssertionIsUpperException(assertion=self, assert_value=repr(self.__value))

    def is_length(self, expect_length):
        """
        description: assert the length of object is equal to `expect_length`.
        """
        try:
            real_length = len(self.__value)
            if real_length == expect_length:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsLengthException(
            assertion=self, assert_value=repr(self.__value), expect_length=expect_length, real_length=real_length
        )

    def is_not_length(self, expect_length):
        """
        description: assert the length of object is not equal to
                     `expect_length`.
        """
        try:
            real_length = len(self.__value)
            if not real_length == expect_length:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsNotLengthException(
            assertion=self, assert_value=repr(self.__value), expect_length=expect_length, real_length=real_length
        )

    def contains(self, *args):
        """
        description: assert object contains all elements of the `args`.
        """
        self.assert_type(Iterable)
        for expect_value in args:
            if expect_value not in self.__value:
                break
        else:
            return self

        raise AssertionContainsException(
            assertion=self, assert_value=repr(self.__value), expect_value=get_and_text(args)
        )

    def does_not_contain(self, *args):
        """
        description: assert object does not contain all element of the `args`.
        """
        self.assert_type(Iterable)

        for expect_value in args:
            if expect_value in self.__value:
                break
        else:
            return self

        raise AssertionDoesNotContainException(
            assertion=self, assert_value=repr(self.__value), expect_value=get_or_text(args)
        )

    def is_equal_to(self, expect_value):
        """
        description: assert object is equal to `expect_value`.
        """

        if self.__value == expect_value:
            return self

        raise AssertionIsEqualToException(
            assertion=self, assert_value=repr(self.__value), expect_value=repr(expect_value)
        )

    def is_not_equal_to(self, expect_value):
        """
        description: assert object is not equal to `expect_value`.
        """

        if not self.__value == expect_value:
            return self

        raise AssertionIsNotEqualToException(
            assertion=self, assert_value=repr(self.__value), expect_value=repr(expect_value)
        )

    def is_greater_than(self, expect_value):
        """
        description: assert object is greater than `expect_value`.
        """
        try:
            if self.__value > expect_value:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsGreaterThanException(
            assertion=self, assert_value=repr(self.__value), expect_value=repr(expect_value)
        )

    def is_greater_than_or_equal_to(self, expect_value):
        """
        description: assert object is greater than or equal to `expect_value`.
        """
        try:
            if self.__value >= expect_value:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsGreaterThanOrEqualToException(
            assertion=self, assert_value=repr(self.__value), expect_value=repr(expect_value)
        )

    def is_less_than(self, expect_value):
        """
        description: assert object is less than `expect_value`.
        """
        try:
            if self.__value < expect_value:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsLessThanException(
            assertion=self, assert_value=repr(self.__value), expect_value=repr(expect_value)
        )

    def is_less_than_or_equal_to(self, expect_value):
        """
        description: assert object is less than or equal to `expect_value`.
        """
        try:
            if self.__value <= expect_value:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsLessThanOrEqualToException(
            assertion=self, assert_value=repr(self.__value), expect_value=repr(expect_value)
        )

    def is_true(self):
        """
        description: assert object is True.
        """

        if self.__value is True:
            return self

        raise AssertionIsEqualToException(assertion=self, assert_value=repr(self.__value), expect_value=repr(True))

    def is_false(self):
        """
        description: assert object is False.
        """

        if self.__value is False:
            return self

        raise AssertionIsEqualToException(assertion=self, assert_value=repr(self.__value), expect_value=repr(False))

    def is_type_of(self, *args):
        """
        description: assert the type of object is in `args`.
        """
        self.assert_args_empty(args)

        if type(self.__value) in args:
            return self

        raise AssertionIsTypeOfException(
            assertion=self,
            assert_value=self.__value,
            expect_type=get_or_text([_type.__name__ for _type in args], represent=lambda x: x),
            real_type=self.__value.__class__.__name__,
        )

    def is_not_type_of(self, *args):
        """
        description: assert the type of object is not in `args`.
        """
        self.assert_args_empty(args)

        if type(self.__value) not in args:
            return self

        raise AssertionIsNotTypeOfException(
            assertion=self,
            assert_value=self.__value,
            expect_type=get_or_text([_type.__name__ for _type in args], represent=lambda x: x),
            real_type=self.__value.__class__.__name__,
        )

    def is_instance_of(self, *args):
        """
        description: assert object is instance of any type in `args`.
        """
        self.assert_args_empty(args)

        if isinstance(self.__value, args):
            return self

        raise AssertionIsInstanceOfException(
            assertion=self,
            assert_value=self.__value,
            expect_type=get_or_text([_type.__name__ for _type in args], represent=lambda x: x),
            real_type=self.__value.__class__.__name__,
        )

    def is_not_instance_of(self, *args):
        """
        description: assert object is not instance of any type in `args`.
        """
        self.assert_args_empty(args)

        if not isinstance(self.__value, args):
            return self

        raise AssertionIsNotInstanceOfException(
            assertion=self,
            assert_value=self.__value,
            expect_type=get_or_text([_type.__name__ for _type in args], represent=lambda x: x),
            real_type=self.__value.__class__.__name__,
        )

    def matches_schema(self, schema):
        """
        description: assert object is match the `schema`.
        """

        exception = match_schema(value=self.__value, schema=schema)
        if exception is None:
            return self

        raise AssertionMatchesSchemaException(assertion=self, message=str(exception))

    def is_strictly_increasing(self):
        """
        description: assert object is strictly increasing.
        """
        try:
            if all(x < y for x, y in zip(self.__value, self.__value[1:])):
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsStrictlyIncreasingException(assertion=self, assert_value=self.__value)

    def is_strictly_decreasing(self):
        """
        description: assert object is strictly decreasing.
        """
        try:
            if all(x > y for x, y in zip(self.__value, self.__value[1:])):
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsStrictlyDecreasingException(assertion=self, assert_value=self.__value)

    def is_non_strictly_increasing(self):
        """
        description: assert object is non-strictly increase.
        return:
            type: bool
        """
        try:
            if all(x <= y for x, y in zip(self.__value, self.__value[1:])):
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsNonStrictlyIncreasingException(assertion=self, assert_value=self.__value)

    def is_non_strictly_decreasing(self):
        """
        description: assert object is non-strictly decrease.
        """
        try:
            if all(x >= y for x, y in zip(self.__value, self.__value[1:])):
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsNonStrictlyDecreasingException(assertion=self, assert_value=self.__value)

    def is_close_to(self, expect_value, delta):
        """
        description: assert the absolute delta of object and
                     `expect_value` is less than `delta`.
        """
        try:
            if abs(self.__value - expect_value) < delta:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsCloseToException(
            assertion=self,
            assert_value=self.__value,
            expect_value=expect_value,
            delta=abs(self.__value - expect_value),
            expect_delta=delta,
        )

    def is_not_close_to(self, expect_value, delta):
        """
        description: assert the absolute delta of object and
                     `expect_value` is greater than or equal to `delta`.
        """
        try:
            if abs(self.__value - expect_value) >= delta:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsNotCloseToException(
            assertion=self,
            assert_value=self.__value,
            expect_value=expect_value,
            real_delta=abs(self.__value - expect_value),
            expect_delta=delta,
        )

    def is_before(self, expect_time):
        """
        description: assert time object is earlier than the `expect_time`.
        """
        try:
            if self.__value < expect_time:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsBeforeException(assertion=self, assert_time=self.__value, expect_time=expect_time)

    def is_after(self, expect_time):
        """
        description: assert time object is later than the `expect_time`.
        """
        try:
            if self.__value > expect_time:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsAfterException(assertion=self, assert_time=self.__value, expect_time=expect_time)

    def is_file(self):
        """
        description: assert the object is a file.
        """
        self.assert_type(str)
        if os.path.isfile(self.__value):
            return self

        raise AssertionIsFileException(assertion=self, assert_value=repr(self.__value))

    def is_not_file(self):
        """
        description: assert the object is not a file.
        """
        self.assert_type(str)
        if not os.path.isfile(self.__value):
            return self

        raise AssertionIsNotFileException(assertion=self, assert_value=repr(self.__value))

    def is_directory(self):
        """
        description: assert the object is a directory.
        """
        self.assert_type(str)
        if os.path.isdir(self.__value):
            return self

        raise AssertionIsDirectoryException(assertion=self, assert_value=self.__value)

    def is_not_directory(self):
        """
        description: assert the object is not a directory.
        """
        self.assert_type(str)
        if not os.path.isdir(self.__value):
            return self

        raise AssertionIsNotDirectoryException(assertion=self, assert_value=self.__value)

    def does_not_exist(self):
        """
        description: assert the file or directory does not exist.
        """
        self.assert_type(str, int)
        if not os.path.exists(self.__value):
            return self

        raise AssertionDoesNotExistException(assertion=self, assert_value=self.__value)

    def exists(self):
        """
        description: assert the file or directory does exist.
        """
        self.assert_type(str, int)
        if os.path.exists(self.__value):
            return self

        raise AssertionExistException(assertion=self, assert_value=self.__value)

    def is_in(self, expect_value):
        """
        description: assert object exists in the `expect_value`.
        """
        if not isinstance(expect_value, Iterable):
            raise AssertionTypeMismatchException(self, "expect_value should be Iterable")
        if self.__value in expect_value:
            return self

        raise AssertionIsInException(assertion=self, assert_value=repr(self.__value), expect_value=repr(expect_value))

    def is_not_in(self, expect_value):
        """
        description: assert object does not exist in the `expect_value`.
        """
        if not isinstance(expect_value, Iterable):
            raise AssertionTypeMismatchException(self, "expect_value should be Iterable")
        if self.__value not in expect_value:
            return self

        raise AssertionIsNotInException(
            assertion=self, assert_value=repr(self.__value), expect_value=repr(expect_value)
        )

    def is_iterable(self):
        """
        description: assert object is iterable.
        """

        if isinstance(self.__value, Iterable):
            return self

        raise AssertionIsIterableException(assertion=self, assert_value=self.__value)

    def is_not_iterable(self):
        """
        description: assert object is not iterable.
        """

        if not isinstance(self.__value, Iterable):
            return self

        raise AssertionIsNotIterableException(assertion=self, assert_value=self.__value)

    def is_inf(self):
        """
        description: assert object is infinite float.
        """

        if self.__value == math.inf:
            return self

        raise AssertionIsInfException(assertion=self, assert_value=self.__value)

    def is_not_inf(self):
        """
        description: assert object is not infinite float.
        """

        if not self.__value == math.inf:
            return self

        raise AssertionIsNotInfException(assertion=self, assert_value=self.__value)

    def is_nan(self):
        """
        description: assert object is an NaN.
        """

        if math.isnan(self.__value):
            return self

        raise AssertionIsNanException(assertion=self, assert_value=self.__value)

    def is_not_nan(self):
        """
        description: assert object is not an NaN.
        """

        if not math.isnan(self.__value):
            return self

        raise AssertionIsNotNanException(assertion=self, assert_value=self.__value)

    def is_same_as(self, expect_value):
        """
        description: assert the address of object is equal to
                     the address of `expect_value`.
        """

        if self.__value is expect_value:
            return self

        raise AssertionIsSameAsException(assertion=self, assert_value=self.__value, expect_value=expect_value)

    def is_not_same_as(self, expect_value):
        """
        description: assert the address of object is not equal to
                     the address of `expect_value`.
        """

        if self.__value is not expect_value:
            return self

        raise AssertionIsNotSameAsException(assertion=self, assert_value=self.__value, expect_value=expect_value)

    def matches_regex(self, pattern):
        """
        description: assert object matches the regex `pattern`.
        """
        self.assert_type(str)
        try:
            if re.match(pattern, self.__value):
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionMatchesRegexException(assertion=self, assert_value=repr(self.__value), expect_value=pattern)

    def does_not_match_regex(self, pattern):
        """
        description: assert object does not match the regex `pattern`.
        """
        self.assert_type(str)
        try:
            if not re.search(pattern, self.__value):
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionDoesNotMatchRegexException(assertion=self, assert_value=repr(self.__value), expect_value=pattern)

    def is_between(self, lower_limit, higher_limit):
        """
        description: assert object value is between the `lower_limit` and
                     `higher_limit`.
        """
        try:
            if lower_limit <= self.__value <= higher_limit:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsBetweenException(
            assertion=self, assert_value=self.__value, lower_limit=lower_limit, higher_limit=higher_limit
        )

    def is_not_between(self, lower_limit, higher_limit):
        """
        description: assert object is less than `lower_limit` or
                     is greater than `higher_limit`.
        return:
            type: bool
        """
        try:
            if (self.__value < lower_limit) or (self.__value > higher_limit):
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsNotBetweenException(
            assertion=self, assert_value=self.__value, lower_limit=lower_limit, higher_limit=higher_limit
        )

    def is_alpha(self):
        """
        description: assert all elements in string object are alphabets.
        """
        self.assert_type(str)

        if self.__value.isalpha():
            return self

        raise AssertionIsAlphaException(assertion=self, assert_value=self.__value)

    def is_not_alpha(self):
        """
        description: assert not all elements in string object are alphabets.
        """
        self.assert_type(str)

        if not self.__value.isalpha():
            return self

        raise AssertionIsNotAlphaException(assertion=self, assert_value=self.__value)

    def is_digit(self):
        """
        description: assert all elements in string  object are numbers.
        """
        self.assert_type(str)
        if self.__value.isdigit():
            return self

        raise AssertionIsDigitException(assertion=self, assert_value=self.__value)

    def is_not_digit(self):
        """
        description: assert not all elements in string  object are numbers.
        """
        self.assert_type(str)
        if not self.__value.isdigit():
            return self

        raise AssertionIsNotDigitException(assertion=self, assert_value=self.__value)

    def is_negative(self):
        """
        description: assert object is less than `0`.
        """
        self.assert_type(int, float)
        if self.__value < 0:
            return self

        raise AssertionIsNegativeException(assertion=self, assert_value=self.__value)

    def is_positive(self):
        """
        description: assert object is greater than `0`.
        """
        self.assert_type(int, float)
        if self.__value > 0:
            return self

        raise AssertionIsPositiveException(assertion=self, assert_value=self.__value)

    def is_zero(self):
        """
        description: assert object is equal to `0`.
        """
        self.assert_type(int, float)
        if self.__value == 0:
            return self

        raise AssertionIsZeroException(assertion=self, assert_value=self.__value)

    def is_not_zero(self):
        """
        description: assert object is not equal to `0`.
        """
        self.assert_type(int, float)
        if not self.__value == 0:
            return self

        raise AssertionIsNotZeroException(assertion=self, assert_value=self.__value)

    def is_empty(self):
        """
        description: assert the length of object is `0`.
        """
        try:
            if len(self.__value) == 0:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsEmptyException(assertion=self, assert_value=self.__value)

    def is_not_empty(self):
        """
        description: assert the length of object is not `0`.
        """
        try:
            if not len(self.__value) == 0:
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionIsNotEmptyException(assertion=self, assert_value=self.__value)

    def starts_with(self, expect_value):
        """
        description: assert string object starts with the `expect_value`.
        """
        self.assert_type(str)
        try:
            if self.__value.startswith(expect_value):
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionStartsWithException(assertion=self, assert_value=self.__value, expect_value=expect_value)

    def ends_with(self, expect_value):
        """
        description: assert string object starts with the `expect_value`.
        """
        self.assert_type(str)
        try:
            if self.__value.endswith(expect_value):
                return self
        except BaseException as exception:
            raise AssertionTypeMismatchException(self, str(exception)) from exception

        raise AssertionEndsWithException(assertion=self, assert_value=self.__value, expect_value=expect_value)

    def contains_duplicates(self):
        """
        description: assert object contains duplicated elements.
        """
        self.assert_type(Iterable)
        if len(set(self.__value)) != len(self.__value):
            return self

        raise AssertionContainsDuplicatesException(assertion=self, assert_value=self.__value)

    def does_not_contain_duplicates(self):
        """
        description: assert object does not contain duplicated elements.
        """
        self.assert_type(Iterable)
        if len(set(self.__value)) == len(self.__value):
            return self

        raise AssertionDoesNotContainDuplicatesException(assertion=self, assert_value=self.__value)

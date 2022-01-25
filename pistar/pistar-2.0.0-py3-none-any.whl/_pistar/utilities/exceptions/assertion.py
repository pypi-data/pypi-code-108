"""
description: this module provides exceptions of assertion.
"""
from typing import Optional


class AssertionBaseException(Exception):
    """
    description: this is the base exception of assertion exceptions.
    """

    message: Optional[str] = None

    def __init__(self, assertion, **kwargs):
        self.count = getattr(assertion, "count", 0)
        super().__init__(self.message.format(**kwargs))


class AssertionTypeMismatchException(AssertionBaseException):
    """
    description: type mismatch exception.
    """
    message = None

    def __init__(self, assertion, message):
        self.message = message
        super().__init__(assertion)


class AssertionIsNoneException(AssertionBaseException):
    """
    description: is none exception.
    """

    message = 'expect {assert_value} to be None, but it was not'


class AssertionIsNotNoneException(AssertionBaseException):
    """
    description: is not non exception.
    """

    message = 'expect {assert_value} to be not None, but it was'


class AssertionIsLowerException(AssertionBaseException):
    """
    description: is lower exception.
    """

    message = 'expect {assert_value} to be lower case, but it did not'


class AssertionIsUpperException(AssertionBaseException):
    """
    description: is upper exception.
    """

    message = 'expect {assert_value} to be upper cass, but it did not'


class AssertionIsLengthException(AssertionBaseException):
    """
    description: is length exception.
    """

    message = 'expect {assert_value} to be of length {expect_length}, ' \
              'but it was {real_length}'


class AssertionIsNotLengthException(AssertionBaseException):
    """
    description: is not length exception.
    """

    message = 'expect {assert_value} to be not of length {expect_length},' \
              ' but it was {real_length}'


class AssertionContainsException(AssertionBaseException):
    """
    description: contains exception.
    """

    message = 'expect {assert_value} to contain {expect_value}, but it did not'


class AssertionDoesNotContainException(AssertionBaseException):
    """
    description: does not contain exception.
    """

    message = 'expect {assert_value} to do not contain {expect_value},' \
              ' but it did'


class AssertionIsEqualToException(AssertionBaseException):
    """
    description: is equal to exception.
    """

    message = 'expect {assert_value} is equal to {expect_value},' \
              ' but it did not'


class AssertionIsNotEqualToException(AssertionBaseException):
    """
    description: is not equal to exception.
    """

    message = 'expect {assert_value} to be not equal to {expect_value},' \
              ' but it did'


class AssertionIsGreaterThanException(AssertionBaseException):
    """
    description: is greater than exception.
    """

    message = 'expect {assert_value} to be greater than {expect_value},' \
              ' but it did not'


class AssertionIsGreaterThanOrEqualToException(AssertionBaseException):
    """
    description: is greater than or equal to exception.
    """

    message = 'expect {assert_value} to be greater than or equal to' \
              ' {expect_value}, but it did not'


class AssertionIsLessThanException(AssertionBaseException):
    """
    description: is less than exception.
    """

    message = 'expect {assert_value} to be less than {expect_value},' \
              ' but it did not'


class AssertionIsLessThanOrEqualToException(AssertionBaseException):
    """
    description: is less than or equal to exception.
    """

    message = 'expect {assert_value} to be less than or equal to' \
              ' {expect_value}, but it did not'


class AssertionIsTypeOfException(AssertionBaseException):
    """
    description: is type of exception.
    """

    message = 'expect {assert_value} to be of type {expect_type},' \
              ' but it was {real_type}'


class AssertionIsNotTypeOfException(AssertionBaseException):
    """
    description: is not type of exception.
    """

    message = 'expect {assert_value} to be not of type {expect_type},' \
              ' but it was {real_type}'


class AssertionIsInstanceOfException(AssertionBaseException):
    """
    description: is instance of exception.
    """

    message = 'expect {assert_value} to be instance of {expect_type},' \
              ' but it was {real_type}'


class AssertionIsNotInstanceOfException(AssertionBaseException):
    """
    description: is not instance of exception.
    """

    message = 'expect {assert_value} to be not instance of {expect_type},' \
              ' but it was {real_type}'


class AssertionMatchesSchemaException(AssertionBaseException):
    """
    description: matches schema exception.
    """

    message = '{message}'


class AssertionIsStrictlyIncreasingException(AssertionBaseException):
    """
    description: is strictly increasing exception.
    """

    message = 'expect {assert_value} to be strictly increasing, but it was not'


class AssertionIsStrictlyDecreasingException(AssertionBaseException):
    """
    description: is strictly decreasing exception.
    """

    message = 'expect {assert_value} to be strictly decreasing, but it was not'


class AssertionIsNonStrictlyIncreasingException(AssertionBaseException):
    """
    description: is non strictly increasing exception.
    """

    message = 'expect {assert_value} to be non-strictly increasing,' \
              ' but it was not'


class AssertionIsNonStrictlyDecreasingException(AssertionBaseException):
    """
    description: is non strictly decreasing exception.
    """

    message = 'expect {assert_value} to be non-strictly decreasing,' \
              ' but it was not'


class AssertionIsCloseToException(AssertionBaseException):
    """
    description: is close exception.
    """

    message = 'expect {assert_value} to be close to {expect_value} ' \
              'with delta < {expect_delta}, but the delta = {delta}'


class AssertionIsNotCloseToException(AssertionBaseException):
    """
    description: is not close exception.
    """

    message = 'expect {assert_value} to not be close to {expect_value}' \
              'with delta >= {expect_delta}, ' + 'but the delta = {real_delta}'


class AssertionIsBeforeException(AssertionBaseException):
    """
    description: is before exception.
    """

    message = 'expect time {assert_time} to be before to {expect_time},' \
              ' but it did not'


class AssertionIsAfterException(AssertionBaseException):
    """
    description: is after exception.
    """

    message = 'expect time {assert_time} to be after to {expect_time}, ' \
              'but it did not'


class AssertionIsFileException(AssertionBaseException):
    """
    description: is file exception.
    """

    message = 'expect {assert_value} is a file, but it did not'


class AssertionIsNotFileException(AssertionBaseException):
    """
    description: is not file exception.
    """

    message = 'expect {assert_value} is not a file, but it did not'


class AssertionIsInException(AssertionBaseException):
    """
    description: is in exception.
    """

    message = 'expect {assert_value} is in {expect_value}, but it did not'


class AssertionIsNotInException(AssertionBaseException):
    """
    description: is not in exception.
    """

    message = 'expect {assert_value} is not in {expect_value}, but it was'


class AssertionIsIterableException(AssertionBaseException):
    """
    description: is iterable exception.
    """

    message = 'expect {assert_value} is iterable, but it did not'


class AssertionIsNotIterableException(AssertionBaseException):
    """
    description: is not iterable exception.
    """

    message = 'expect {assert_value} is not iterable, but it was'


class AssertionIsInfException(AssertionBaseException):
    """
    description: is infinity exception.
    """

    message = 'expect {assert_value} to be infinity, but it did not'


class AssertionIsNotInfException(AssertionBaseException):
    """
    description: is not infinity exception.
    """

    message = 'expect {assert_value} to not be infinity, but it did'


class AssertionIsSameAsException(AssertionBaseException):
    """
    description: is same as exception.
    """

    message = 'expect {assert_value} is same as {expect_value}, but it did not'


class AssertionIsNotSameAsException(AssertionBaseException):
    """
    description: is not same as exception.
    """

    message = 'expect {assert_value} is not same as {expect_value}, but it was'


class AssertionMatchesRegexException(AssertionBaseException):
    """
    description: matches regex exception.
    """

    message = 'expect {assert_value} to match pattern {expect_value},' \
              ' but it did not'


class AssertionDoesNotMatchRegexException(AssertionBaseException):
    """
    description: does not match regex exception.
    """

    message = 'expect {assert_value} to not match pattern {expect_value},' \
              ' but it did'


class AssertionIsBetweenException(AssertionBaseException):
    """
    description: is between exception.
    """

    message = 'expect {assert_value} is betweent [{lower_limit},' \
              ' {higher_limit}], but it did not'


class AssertionIsNotBetweenException(AssertionBaseException):
    """
    description: is not between exception.
    """

    message = 'expect {assert_value} is not betweent [{lower_limit}, ' \
              '{higher_limit}], but it was'


class AssertionIsAlphaException(AssertionBaseException):
    """
    description: is alpha exception.
    """

    message = 'expect {assert_value} are all alphabetic, but it were not'


class AssertionIsNotAlphaException(AssertionBaseException):
    """
    description: is not alpha exception.
    """

    message = 'expect {assert_value} are not all alphabetic, but it were'


class AssertionIsDigitException(AssertionBaseException):
    """
    description: is digit exception.
    """

    message = 'expect {assert_value} are all digit, but it were not'


class AssertionIsNotDigitException(AssertionBaseException):
    """
    description: is not digit exception.
    """

    message = 'expect {assert_value} are not all digit, but it were'


class AssertionIsNegativeException(AssertionBaseException):
    """
    description: is negative exception.
    """

    message = 'expect {assert_value} is negative, but it did not'


class AssertionIsPositiveException(AssertionBaseException):
    """
    description: is positivie exception.
    """

    message = 'expect {assert_value} is positive, but it did not'


class AssertionIsZeroException(AssertionBaseException):
    """
    description: is zero exception.
    """

    message = 'expect {assert_value} is zero, but it did not'


class AssertionIsNotZeroException(AssertionBaseException):
    """
    description: is not zero exception.
    """

    message = 'expect {assert_value} is not zero, but it was'


class AssertionIsEmptyException(AssertionBaseException):
    """
    description: is empty exception.
    """

    message = 'expect {assert_value} is empty, but it did not'


class AssertionIsNotEmptyException(AssertionBaseException):
    """
    description: is not empty exception.
    """

    message = 'expect {assert_value} is not empty, but it was'


class AssertionIsNanException(AssertionBaseException):
    """
    description: is nan (not a number) exception.
    """

    message = 'expect {assert_value} is NaN, but it did not'


class AssertionIsNotNanException(AssertionBaseException):
    """
    description: is not nan (not a number) exception.
    """

    message = 'expect {assert_value} is not NaN, but it was'


class AssertionStartsWithException(AssertionBaseException):
    """
    description: starts with exception.
    """

    message = 'expect {assert_value} is start with {expect_value},' \
              ' but it did not'


class AssertionContainsDuplicatesException(AssertionBaseException):
    """
    description: contains duplicates exception.
    """

    message = 'expect {assert_value} to contain duplicates, but did not.'


class AssertionDoesNotContainDuplicatesException(AssertionBaseException):
    """
    description: does not contain duplicates exception.
    """

    message = 'expect {assert_value} to not contain duplicates, but it did.'


class AssertionEndsWithException(AssertionBaseException):
    """
    description: ends with exception.
    """

    message = 'expect {assert_value} is end with {expect_value},' \
              ' but it did not'


class AssertionDoesNotExistException(AssertionBaseException):
    """
    description: does not exist exception.
    """

    message = 'expect {assert_value} to not exist, but it was found.'


class AssertionExistException(AssertionBaseException):
    """
    description: exist exception.
    """

    message = 'expect {assert_value} to exist, but it was not found.'


class AssertionIsDirectoryException(AssertionBaseException):
    """
    description: is directory exception.
    """

    message = 'expect {assert_value} to be a directory, but it was not.'


class AssertionIsNotDirectoryException(AssertionBaseException):
    """
    description: is not directory exception.
    """

    message = 'expect {assert_value} to not be a directory, but it was.'

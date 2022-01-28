#
# Copyright 2020 Nebulon, Inc.
# All Rights Reserved.
#
# DISCLAIMER: THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#


class StringFilter:
    """A filter object to filter items based on str values."""

    def __init__(
            self,
            equals: str = None,
            not_equals: str = None,
            contains: str = None,
            not_contains: str = None,
            begins_with: str = None,
            ends_with: str = None,
            regex: str = None,
            in_list: [str] = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object for str values

        Allows filtering on ``str`` value types. The filter allows only one
        property to be specified. If filtering on multiple properties is
        needed, use the ``and_filter`` and ``or_filter`` options to concatenate
        multiple filters.

        :param equals: does a `==` comparison with the provided value
        :type equals: str, optional
        :param not_equals: does a `!=` comparison with the provided value
        :type not_equals: str, optional
        :param contains: checks if the provided value is part of the ``str`` value
        :type contains: str, optional
        :param not_contains: checks if the provided value is not part of the
            ``str`` value
        :type not_contains: str, optional
        :param begins_with: checks if the ``str`` value starts with the provided
            value
        :type begins_with: str, optional
        :param ends_with: checks if the ``str`` value ends with the provided
            value
        :type ends_with: str, optional
        :param regex: interprets the provided value as a regular expression
            and does a pattern match with the ``str`` value.
        :type regex: str, optional
        :param in_list: checks if the ``str`` value is in the provided list of
            ``str`` values.
        :type in_list: [str], optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: StringFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: StringFilter, optional
        """

        self.__equals = equals
        self.__not_equals = not_equals
        self.__contains = contains
        self.__not_contains = not_contains
        self.__begins_with = begins_with
        self.__ends_with = ends_with
        self.__regex = regex
        self.__in = in_list
        self.__and = and_filter
        self.__or = or_filter

    @property
    def equals(self) -> str:
        """ Filters strings by an exact match"""
        return self.__equals

    @property
    def not_equals(self) -> str:
        """Filters strings by not being an exact match"""
        return self.__not_equals

    @property
    def contains(self) -> str:
        """Matches if a string contains a provided value"""
        return self.__contains

    @property
    def not_contains(self) -> str:
        """ Matches if a string does not contain a provided value"""
        return self.__not_contains

    @property
    def begins_with(self) -> str:
        """Matches if a string begins with a provided value"""
        return self.__begins_with

    @property
    def ends_with(self) -> str:
        """Matches if a string ends with a provided value"""
        return self.__ends_with

    @property
    def regex(self) -> str:
        """Matches by use of a regular expression"""
        return self.__regex

    @property
    def in_filter(self) -> list:
        """Matches if a string is on of a provided list of values"""
        return self.__in

    @property
    def and_filter(self):
        """Allows concatenation with another string filter with a logical AND"""
        return self.__and

    @property
    def or_filter(self):
        """Allows concatenation with another string filter with a logical OR"""
        return self.__or

    @property
    def as_dict(self):
        result = dict()
        result["equals"] = self.equals
        result["notEquals"] = self.not_equals
        result["contains"] = self.contains
        result["notContains"] = self.not_contains
        result["beginsWith"] = self.begins_with
        result["endsWith"] = self.ends_with
        result["regex"] = self.regex
        result["in"] = self.in_filter
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class IntFilter:
    """A filter object to filter items based on ``int`` values."""

    def __init__(
            self,
            equals: int = None,
            not_equals: int = None,
            less_than: int = None,
            less_than_equals: int = None,
            greater_than: int = None,
            greater_than_equals: int = None,
            in_list: [int] = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        Allows filtering on ``int`` value types. The filter allows only one
        property to be specified. If filtering on multiple properties is
        needed, use the ``and_filter`` and ``or_filter`` options to concatenate
        multiple filters.

        :param equals: does a `==` comparison with the provided value
        :type equals: int, optional
        :param not_equals: does a `!=` comparison with the provided value
        :type not_equals: int, optional


        :param less_than: does a `<` comparison with the provided value
        :type less_than: int, optional
        :param less_than_equals: does a `<=` comparison with the provided value
        :type less_than_equals: int, optional
        :param greater_than: does a `>` comparison with the provided value
        :type greater_than: int, optional
        :param greater_than_equals: does a `>=` comparison with the provided
            value
        :type greater_than_equals: int, optional
        :param in_list: checks if the ``int`` value is in the provided list
        :type in_list: [int], optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: IntFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: IntFilter, optional
        """

        self.__equals = equals
        self.__not_equals = not_equals
        self.__less_than = less_than
        self.__less_than_equals = less_than_equals
        self.__greater_than = greater_than
        self.__greater_than_equals = greater_than_equals
        self.__in = in_list
        self.__and = and_filter
        self.__or = or_filter

    @property
    def equals(self) -> int:
        """Filters values with a `==` comparison"""
        return self.__equals

    @property
    def not_equals(self) -> int:
        """Filters values with a `!=` comparison"""
        return self.__not_equals

    @property
    def less_than(self) -> int:
        """Filters values with a `<` comparison"""
        return self.__less_than

    @property
    def less_than_equals(self) -> int:
        """Filters values with a `<=` comparison"""
        return self.__less_than_equals

    @property
    def greater_than(self) -> int:
        """Filters values with a `>` comparison"""
        return self.__greater_than

    @property
    def greater_than_equals(self) -> int:
        """Filters values with a `>=` comparison"""
        return self.__greater_than_equals

    @property
    def in_filter(self) -> list:
        """Matches if an ``int`` is on of a provided list of values"""
        return self.__in

    @property
    def and_filter(self):
        """Allows concatenation with another int filter with a logical AND"""
        return self.__and

    @property
    def or_filter(self):
        """Allows concatenation with another int filter with a logical OR"""
        return self.__or

    @property
    def as_dict(self):
        result = dict()
        result["equals"] = self.equals
        result["notEquals"] = self.not_equals
        result["lessThan"] = self.less_than
        result["lessThanEquals"] = self.less_than_equals
        result["greaterThan"] = self.greater_than
        result["greaterThanEquals"] = self.greater_than_equals
        result["in"] = self.in_filter
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class UuidFilter:
    """A filter object to filter on UUID values"""

    def __init__(
            self,
            equals: str = None,
            not_equals: str = None,
            in_filter: [str] = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new ``UUID`` filter object

        Allows filtering on ``UUID`` (str) value types. The filter allows only one
        property to be specified. If filtering on multiple properties is
        needed, use the ``and_filter`` and ``or_filter`` options to concatenate
        multiple filters.

        :param equals: does a `==` comparison with the provided value
        :type equals: str, optional
        :param not_equals: does a `!=` comparison with the provided value
        :type not_equals: str, optional
        :param in_filter: checks if the ``str`` value is in the provided list
        :type in_filter: [str], optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: UuidFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: UuidFilter, optional
        """

        self.__equals = equals
        self.__not_equals = not_equals
        self.__in = in_filter
        self.__and = and_filter
        self.__or = or_filter

    @property
    def equals(self) -> str:
        """Filters UUIDs by being an exact match"""
        return self.__equals

    @property
    def not_equals(self) -> str:
        """Filters UUIDs by not being an exact match"""
        return self.__not_equals

    @property
    def in_filter(self) -> [str]:
        """Matches if a UUID is on of a provided list of values"""
        return self.__in

    @property
    def and_filter(self):
        """Allows concatenation with another UUID filter with a logical AND"""
        return self.__and

    @property
    def or_filter(self):
        """Allows concatenation with another UUID filter with a logical OR"""
        return self.__or

    @property
    def as_dict(self):
        result = dict()
        result["equals"] = self.equals
        result["notEquals"] = self.not_equals
        result["in"] = self.in_filter
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result

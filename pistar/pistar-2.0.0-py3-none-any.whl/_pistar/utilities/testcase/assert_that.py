"""
description: this module provides the function process_assert_that.
"""
from _pistar.utilities.assertion import AssertThat as OriginAssertThat
from _pistar.utilities.exceptions import HasNoAttributeException


def process_assert_that(origin_assert_that):
    """
    description: package assert_that class for base testcase
    arguments:
        origin_assert_that:
            type: assert_that, class define in assertion
    """

    class AssertThat:
        """
        description: new assert_that class for testcase
        attribute:
            value:
                type: same type of asserted object
                description: value of object that will to assert
                permission: private
            testcase:
                type: testcase, derive from BaseTestcase
                description: actual testcase to test
                permission: public
        """

        def __init__(self, value, testcase=None):
            self.__value = value
            self.testcase = testcase
            self.count = 0

        def __getattr__(self, attribute):
            raise HasNoAttributeException(
                class_name=self.__class__.__name__,
                attribute_name=attribute
            )

    methods = {
        key: value
        for key, value in origin_assert_that.__dict__.items()
        if not key.startswith("_") and callable(value)
    }

    for method_name, method in methods.items():
        def generate_method(_method):
            """
            description: decorator of actual assert method
            arguments:
                method:
                    type: str
                    description: method name
            """

            def wrapper(self, *args, **kwargs):
                self.count += 1
                _method(self, *args, **kwargs)
                return self

            return wrapper

        setattr(AssertThat, method_name, generate_method(method))
    return AssertThat


assert_that = process_assert_that(OriginAssertThat)

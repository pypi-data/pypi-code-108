"""
This is inspired by our old glibs.sherman and django.test
"""

import datadriven
import unittest
import sys

from glibs.test import _mixins

__all__ = ["TestCase", "datadriven"]


class TestCase(_mixins._AssertsMixin, unittest.TestCase):
    def _pre_setup(self):
        """This is our custom test setup. Since we're not using setUp(), they should
        work correctly even if users don't include a call to super().setUp()

        This method does not work with raising unittest.SkipTest to skip tests.
        """
        pass

    def _post_teardown(self):
        """This is our custom test teardown. Since we're not using tearDown(), they should
        work correctly even if users don't include a call to super().tearDown()"""
        pass

    def run(self, result=None):
        testMethod = getattr(self, self._testMethodName)
        skipped = getattr(self.__class__, "__unittest_skip__", False) or getattr(
            testMethod, "__unittest_skip__", False
        )

        if not result:  # pragma: no cover
            result = unittest.TestResult()

        if not skipped:
            try:
                self._pre_setup()
            except Exception:
                result.addError(self, sys.exc_info())

        super(TestCase, self).run(result)

        if not skipped:
            try:
                self._post_teardown()
            except Exception:
                result.addError(self, sys.exc_info())

    def debug(self):
        testMethod = getattr(self, self._testMethodName)
        skipped = getattr(self.__class__, "__unittest_skip__", False) or getattr(
            testMethod, "__unittest_skip__", False
        )

        if not skipped:
            self._pre_setup()

        super(TestCase, self).debug()

        if not skipped:
            self._post_teardown()

    def run_patch(self, patcher):
        """
        This is a helper function so that you can run many patches in a
        non-repulsive way. Instead of doing something like this:

        ```python
        @mock.patch(a)
        @mock.patch(b)
        # ...
        @mock.patch(z)
        def test_something(a, b, ..., z):
            # ... after a gajillion variables in the function declaration
        ```

        Or even this:

        ```python
        def test_something(a, b, ..., z):
            with mock.patch(a) as am:
                with mock.patch(b) as bm:
                    # ...
                        with mock.patch(z) as zm:
                            # ... in the zillionth indentation level
        ```

        You can do this:

        ```python
        def test_something():
            mock_a = self.run_patch(mock.patch(a))
            mock_b = self.run_patch(mock.patch(b))
            # ...
            mock_z = self.run_patch(mock.patch(z))
            # way nicer, isn't it?
        ```
        """
        patched_object = patcher.start()
        self.addCleanup(patcher.stop)
        return patched_object

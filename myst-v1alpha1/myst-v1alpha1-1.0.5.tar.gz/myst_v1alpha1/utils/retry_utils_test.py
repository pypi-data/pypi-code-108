import unittest

import mock
from tenacity import RetryError
from tenacity import wait_none

from myst_v1alpha1.utils.retry_utils import retry


def call_counter(func):
    def mock_function_wrapper(*args, **kwargs):
        mock_function_wrapper.calls += 1
        return func(*args, **kwargs)

    mock_function_wrapper.calls = 0
    return mock_function_wrapper


class RetryUtilsTest(unittest.TestCase):
    @mock.patch("myst_v1alpha1.utils.retry_utils._retry_wait")
    def test_retry(self, _retry_wait_function_mock):
        # Mock tenacity's wait function so we don't actually sleep during tests.
        _retry_wait_function_mock.return_value = wait_none()

        @call_counter
        def mock_function():
            raise ValueError("An error.")

        # Create a mock function to wrap in retry logic
        def retryable_mock_function():
            # Construct the retry decorator.
            retry_decorator = retry(num_max_retries=5)

            # Decorate the function to add retry logic.
            decorated_function = retry_decorator(mock_function)

            result = decorated_function()
            return result

        # It should retry 5 times and then raise the exception.
        self.assertRaises(ValueError, retryable_mock_function)
        self.assertEqual(5, mock_function.calls)

        # Reset number of calls to mock function.
        mock_function.calls = 0

        # Create a mock function to wrap in retry logic, with a different number of retries.
        def retryable_mock_function():
            # Construct the retry decorator.
            retry_decorator = retry(num_max_retries=2)

            # Decorate the function to add retry logic.
            decorated_function = retry_decorator(mock_function)

            result = decorated_function()
            return result

        # It should retry 2 times and then raise the exception.
        self.assertRaises(ValueError, retryable_mock_function)
        self.assertEqual(2, mock_function.calls)

        # Reset number of calls to mock function.
        mock_function.calls = 0

        # Create a mock function to wrap in retry logic, with a different set of exceptions to catch.
        def retryable_mock_function():
            # Construct the retry decorator.
            retry_decorator = retry(retryable_exceptions=[IOError, ValueError])

            # Decorate the function to add retry logic.
            decorated_function = retry_decorator(mock_function)

            result = decorated_function()
            return result

        # It should retry 4 times and then raise the exception.
        self.assertRaises(ValueError, retryable_mock_function)
        self.assertEqual(4, mock_function.calls)

        # Reset number of calls to mock function..
        mock_function.calls = 0

        # Change the exception list to mean the method will not be retried.
        def retryable_mock_function():
            # Construct the retry decorator.
            retry_decorator = retry(retryable_exceptions=[IOError])

            # Decorate the function to add retry logic.
            decorated_function = retry_decorator(mock_function)

            result = decorated_function()
            return result

        self.assertRaises(ValueError, retryable_mock_function)
        self.assertEqual(1, mock_function.calls)

        # Reset number of calls to mock function.
        mock_function.calls = 0

        # Use tenacity's kwargs.
        def retryable_mock_function():
            # Construct the retry decorator.
            retry_decorator = retry(retryable_exceptions=[ValueError], reraise=False)

            # Decorate the function to add retry logic.
            decorated_function = retry_decorator(mock_function)

            result = decorated_function()
            return result

        # Note that now, at the end, it will raise the tenacity-specific `RetryError` due to `reraise=False`
        self.assertRaises(RetryError, retryable_mock_function)
        self.assertEqual(4, mock_function.calls)

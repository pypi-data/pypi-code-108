from unittest.mock import Mock

from django.test import TestCase

from djaws import decorators
from djaws.cognito.exceptions import CognitoError, CognitoUserNotFoundError
from djaws.s3.exceptions import S3Error, BucketAlreadyExists


class WrapAndReraiseS3ErrorsTests(TestCase):
    def test_s3_pass_thru(self):
        func = Mock(side_effect=BucketAlreadyExists)
        decorated_function = decorators.wrap_and_reraise_s3_errors(func)
        with self.assertRaises(BucketAlreadyExists):
            decorated_function()
        self.assertEquals(func.call_count, 1)

    def test_exception(self):
        func = Mock(side_effect=Exception)
        decorated_function = decorators.wrap_and_reraise_s3_errors(func)
        with self.assertRaises(S3Error):
            decorated_function()
        self.assertEquals(func.call_count, 1)


class WrapAndReraiseCognitoErrorsTests(TestCase):
    def test_cognito_pass_thru(self):
        func = Mock(side_effect=CognitoUserNotFoundError)
        decorated_function = decorators.wrap_and_reraise_cognito_errors(func)
        with self.assertRaises(CognitoUserNotFoundError):
            decorated_function()
        self.assertEquals(func.call_count, 1)

    def test_exception(self):
        func = Mock(side_effect=Exception)
        decorated_function = decorators.wrap_and_reraise_cognito_errors(func)
        with self.assertRaises(CognitoError):
            decorated_function()
        self.assertEquals(func.call_count, 1)

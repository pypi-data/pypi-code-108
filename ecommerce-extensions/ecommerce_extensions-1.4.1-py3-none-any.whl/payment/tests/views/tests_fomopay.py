"""Test file for the fomopay views file.

Classes:
    FomopayPaymentResponseViewTest: FomopayPaymentResponseView tests class.
"""
import logging

from django.contrib.auth.models import User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from mock import Mock, patch
from oscar.apps.payment.exceptions import PaymentError, TransactionDeclined, UserCancelled
from oscar.core.loading import get_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from testfixtures import LogCapture

from ecommerce_extensions.payment.tests.exceptions import (
    AuthorizationError,
    DuplicateReferenceNumber,
    InvalidSignatureError,
)
from ecommerce_extensions.payment.views.fomopay import FomopayPaymentResponseView

MODULE = FomopayPaymentResponseView.__module__
Basket = get_model('basket', 'Basket')
Country = get_model('address', 'Country')
Order = get_model('order', 'Order')


class FomopayPaymentResponseViewTest(TestCase):
    """This class includes the tests for the view FomopayPaymentResponseView."""

    def setUp(self):
        """
        Setup.
        """
        self.transaction = 1
        self.basket = Basket.objects.create(id=self.transaction)
        Country.objects.create(iso_3166_1_a2='SG')
        self.factory = RequestFactory()
        self.url = reverse("fomopay:notify")

    @patch.object(FomopayPaymentResponseView, "payment_processor")
    @patch("ecommerce_extensions.payment.views.fomopay.OrderNumberGenerator")
    def test_post_basket_not_found(self, order_generator_mock, _):
        """
        Test post request when the basket is not found.

        Expected behavior:
            - response status code is 200.
            - generator called with the referenceCode value.
        """
        order_generator_mock.return_value.basket_id.return_value = 2
        data = {
            "payment_id": "22",
            "transaction": "nonce$2",
        }
        request = self.factory.post(self.url, data=data)

        response = FomopayPaymentResponseView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        order_generator_mock().basket_id.assert_called_with("2")

    @patch.object(FomopayPaymentResponseView, "payment_processor")
    @patch.object(Basket, "owner")
    @patch("ecommerce_extensions.payment.views.fomopay.OrderNumberGenerator")
    def test_post_basket_found(self, order_generator_mock, owner_mock, _):
        """
        Test post request when the basket is found.

        Expected behavior:
            - response status code is 200.
            - generator called with the referenceCode value.
            - handle_payment is called with the request data and basket object.
            - handle_post_order is called with the value returned by handle_order_placement.
        """
        order_generator_mock.return_value.basket_id.return_value = 1
        data = {
            "payment_id": "20",
            "transaction": "nonce${}".format(self.transaction),
        }
        owner_mock.full_name = "Harry Potter"
        handle_payment_mock = Mock()
        handle_post_order_mock = Mock()
        handle_order_placement_mock = Mock()
        setattr(FomopayPaymentResponseView, "handle_payment", handle_payment_mock)
        setattr(FomopayPaymentResponseView, "handle_post_order", handle_post_order_mock)
        setattr(FomopayPaymentResponseView, "handle_order_placement", handle_order_placement_mock)
        request = self.factory.post(self.url, data=data)

        response = FomopayPaymentResponseView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        order_generator_mock().basket_id.assert_called_with("1")
        handle_payment_mock.assert_called_once_with(data, self.basket)
        handle_post_order_mock.assert_called_once_with(handle_order_placement_mock.return_value)

    @patch.object(FomopayPaymentResponseView, "payment_processor")
    @patch("ecommerce_extensions.payment.views.fomopay.OrderNumberGenerator")
    def test_post_create_order_exception(self, order_generator_mock, _):
        """
        Test post request the method create_order raise any exception.

        Expected behavior:
            - response status code is 200.
            - generator called with the referenceCode value.
            - handle_payment is called with the request data and basket object.
        """
        order_generator_mock.return_value.basket_id.return_value = 1
        data = {
            "payment_id": "20",
            "transaction": "nonce${}".format(self.transaction),
        }
        handle_payment_mock = Mock()
        setattr(FomopayPaymentResponseView, "handle_payment", handle_payment_mock)
        request = self.factory.post(self.url, data=data)

        response = FomopayPaymentResponseView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        order_generator_mock().basket_id.assert_called_with("1")
        handle_payment_mock.assert_called_once_with(data, self.basket)

    def test_post_invalid_signature(self):
        """
        Test post request when the exception InvalidSignatureError is raised.

        Expected behavior:
            - The log message is the right for the exception.
            - response status code is 200.
            - generator called with the referenceCode value.
        """
        log = (
            "Received an invalid signature in the FOMO Pay response for basket [{transaction}]."
            "The payment response was recorded in entry [{transaction}]."
        ).format(transaction=self.transaction)

        response = self._test_log_exceptions(  # pylint: disable=no-value-for-parameter
            log,
            logging.ERROR,
            InvalidSignatureError,
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_post_user_cancelled(self):
        """
        Test post request when the exception UserCancelled is raised.

        Expected behavior:
            - The log message is the right for the exception.
            - response status code is 200.
            - generator called with the referenceCode value.
        """
        log = (
            "FOMO Pay payment did not complete for basket [{transaction}] because [{}]. "
            "The payment response [{}] was recorded in entry [{transaction}]."
        ).format(UserCancelled.__name__, "Unknown Error", transaction=self.transaction)

        response = self._test_log_exceptions(  # pylint: disable=no-value-for-parameter
            log,
            logging.INFO,
            UserCancelled,
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_post_transaction_declined(self):
        """
        Test post request when the exception TransactionDeclined is raised.

        Expected behavior:
            - The log message is the right for the exception.
            - response status code is 200.
            - generator called with the referenceCode value.
        """
        log = (
            "FOMO Pay payment did not complete for basket [{transaction}] because [{}]. "
            "The payment response [{}] was recorded in entry [{transaction}]."
        ).format(TransactionDeclined.__name__, "Unknown Error", transaction=self.transaction)

        response = self._test_log_exceptions(  # pylint: disable=no-value-for-parameter
            log,
            logging.INFO,
            TransactionDeclined,
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_post_duplicate_reference_number(self):
        """
        Test post request when the exception DuplicateReferenceNumber is raised.

        Expected behavior:
            - The log message is the right for the exception.
            - response status code is 200.
            - generator called with the referenceCode value.
        """
        log = (
            "Received FOMO Pay payment notification for basket [{transaction}] which is associated "
            "with existing order [{transaction}]. No payment was collected, and no new order will be created."
        ).format(transaction=self.transaction)

        response = self._test_log_exceptions(  # pylint: disable=no-value-for-parameter
            log,
            logging.INFO,
            DuplicateReferenceNumber,
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_post_authorization_error(self):
        """
        Test post request when the exception AuthorizationError is raised.

        Expected behavior:
            - The log message is the right for the exception.
            - response status code is 200.
            - generator called with the referenceCode value.
        """
        log = (
            "Payment Authorization was declined for basket [{transaction}]. The payment response was "
            "recorded in entry [{transaction}]."
        ).format(transaction=self.transaction)

        response = self._test_log_exceptions(  # pylint: disable=no-value-for-parameter
            log,
            logging.INFO,
            AuthorizationError,
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_post_payment_error(self):
        """
        Test post request when the exception PaymentError is raised.

        Expected behavior:
            - The log message is the right for the exception.
            - response status code is 200.
            - generator called with the referenceCode value.
        """
        log = (
            "FOMO Pay payment failed for basket [{transaction}]. "
            "The payment response [{}] was recorded in entry [{transaction}]."
        ).format("Unknown Error", transaction=self.transaction)

        response = self._test_log_exceptions(  # pylint: disable=no-value-for-parameter
            log,
            logging.ERROR,
            PaymentError,
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_post_general_error(self):
        """
        Test post request when a general exception is raised.

        Expected behavior:
            - The log message is the right for the exception.
            - response status code is 200.
            - generator called with the referenceCode value.
        """
        log = (
            "Attempts to handle payment for basket [{transaction}] failed. The payment response [{}] was recorded in"
            " entry [{transaction}]."
        ).format("Unknown Error", transaction=self.transaction)

        response = self._test_log_exceptions(  # pylint: disable=no-value-for-parameter
            log,
            logging.ERROR,
            Exception,
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @patch.object(FomopayPaymentResponseView, "payment_processor")
    @patch("ecommerce_extensions.payment.views.fomopay.OrderNumberGenerator")
    def _test_log_exceptions(self, log, level, exception, order_generator_mock, _):
        """This verifies the expected log for the given exception.

        Args:
            log: expected log. String.
            level: logging level. int
            exception: exception which will be raised. Exception class

        Returns:
            response : Response for the view FomopayPaymentResponseView.
        """
        order_generator_mock.return_value.basket_id.return_value = self.transaction
        data = {
            "payment_id": "23",
            "transaction": "nonce${}".format(self.transaction),
        }
        handle_payment_mock = Mock()
        handle_payment_mock.side_effect = exception()
        setattr(FomopayPaymentResponseView, "handle_payment", handle_payment_mock)
        request = self.factory.post(self.url, data=data)

        with LogCapture(level=level) as log_capture:
            response = FomopayPaymentResponseView.as_view()(request)

            log_capture.check_present(
                (MODULE, logging.getLevelName(level), log),
            )
            order_generator_mock().basket_id.assert_called_with(str(self.transaction))
            handle_payment_mock.assert_called_once_with(data, self.basket)

        return response


class FomopayPaymentStatusViewTest(TestCase):
    """This class includes the tests for the view FomopayPaymentStatusView."""

    def setUp(self):
        """
        Setup.
        """
        self.client = Client()
        self.user = User.objects.create_user(username="draco_malfoy")
        self.basket_id = 1
        self.basket = Basket.objects.create(id=self.basket_id, owner=self.user)
        self.url = reverse("fomopay:status")

    @patch.object(IsAuthenticated, "has_permission", return_value=True)
    @patch("ecommerce_extensions.payment.views.fomopay.OrderNumberGenerator")
    def test_get_in_progress(self, order_generator_mock, _):
        """Test get request the expected status is in progress.

        Expected behavior:
            - response status code is 200.
            - response status is 'in progress'.
        """
        order_generator_mock.return_value.basket_id.return_value = self.basket_id
        self.client.force_login(self.user)
        data = {"order_id": 5}

        response = self.client.get(self.url, data=data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual({"status": "in progress"}, response.json())

    @patch.object(IsAuthenticated, "has_permission", return_value=True)
    @patch("ecommerce_extensions.payment.views.fomopay.OrderNumberGenerator")
    def test_get_error(self, order_generator_mock, _):
        """Test get request the expected status is error.

        Expected behavior:
            - response status code is 200.
            - response status is 'error'.
        """
        order_generator_mock.return_value.basket_id.return_value = self.basket_id
        self.client.force_login(self.user)
        self.basket.status = "CLOSED"
        self.basket.save()
        data = {"order_id": 5}

        response = self.client.get(self.url, data=data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual({"status": "error"}, response.json())

    @patch.object(IsAuthenticated, "has_permission", return_value=True)
    @patch("ecommerce_extensions.payment.views.fomopay.OrderNumberGenerator")
    def test_get_success(self, order_generator_mock, _):
        """Test get request the expected status is success.

        Expected behavior:
            - response status code is 200.
            - response status is 'success'.
        """
        order_generator_mock.return_value.basket_id.return_value = self.basket_id
        self.client.force_login(self.user)
        order = Order.objects.create(number=5, total_incl_tax=0, total_excl_tax=0, status="Complete")
        data = {"order_id": order.number}

        response = self.client.get(self.url, data=data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual({"status": "success"}, response.json())

    @patch.object(IsAuthenticated, "has_permission", return_value=True)
    def test_get_forbidden(self, _):
        """Test get when the user is no the basket owner.

        Expected behavior:
            - response status code is 403.
        """
        response = self.client.get(self.url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

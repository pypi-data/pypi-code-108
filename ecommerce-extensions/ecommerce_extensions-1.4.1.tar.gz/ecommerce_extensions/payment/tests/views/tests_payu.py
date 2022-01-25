"""Test file for the views file.

Classes:
    PayuViewTest: PayuView tests class.
"""
from importlib import import_module

from django.test import RequestFactory, TestCase
from django.urls import reverse
from mock import Mock, patch
from rest_framework import status

from ecommerce_extensions.payment.views.payu import PayUPaymentResponseView


class PayuViewTest(TestCase):
    """This class includes the tests for the view PayuViewTest."""

    def setUp(self):
        """
        Setup.
        """
        self.factory = RequestFactory()
        self.url = reverse("payu:notify")

    @patch("ecommerce_extensions.payment.views.payu.reverse")
    @patch("ecommerce_extensions.payment.views.payu.OrderNumberGenerator")
    def test_get_raise_exception(self, order_generator_mock, reverse_mock):
        """
        Test get request when an exception is raised.

        Expected behavior:
            - response status code is 302.
            - reverse is called with payment_error
            - generator called with None value.
        """
        order_generator_mock.return_value.basket_id.side_effect = Exception()
        reverse_mock.return_value = "http://fake-redirect.com"
        request = self.factory.get(self.url)

        response = PayUPaymentResponseView.as_view()(request)

        self.assertEqual(status.HTTP_302_FOUND, response.status_code)
        reverse_mock.assert_called_once_with("payment_error")
        order_generator_mock().basket_id.assert_called_once_with(None)

    @patch("ecommerce_extensions.payment.views.payu.reverse")
    @patch("ecommerce_extensions.payment.views.payu.OrderNumberGenerator")
    def test_get_basket_not_found(self, order_generator_mock, reverse_mock):
        """
        Test get request when the basket is not found.

        Expected behavior:
            - response status code is 302.
            - reverse is called with payment_error
            - generator called with the referenceCode value.
        """
        order_generator_mock.return_value.basket_id.return_value = 1
        reverse_mock.return_value = "http://fake-redirect.com"
        data = {
            "transactionId": 20,
            "referenceCode": "1",
        }
        request = self.factory.get(self.url, data=data)

        response = PayUPaymentResponseView.as_view()(request)

        self.assertEqual(status.HTTP_302_FOUND, response.status_code)
        reverse_mock.assert_called_once_with("payment_error")
        order_generator_mock().basket_id.assert_called_once_with(data["referenceCode"])

    @patch.object(PayUPaymentResponseView, "_get_basket")
    @patch("ecommerce_extensions.payment.views.payu.OrderNumberGenerator")
    def test_get_basket_found(self, order_generator_mock, get_basket_mock):
        """
        Test get request when the basket is found.

        Expected behavior:
            - response status code is 302.
            - get_receipt_page_url is called with the expected values.
            - generator called with the referenceCode value.
        """
        module = import_module("ecommerce_extensions.payment.views.payu")
        get_receipt_page_url_mock = Mock()
        get_receipt_page_url_mock.return_value = "http://fake-redirect.com"
        setattr(module, "get_receipt_page_url", get_receipt_page_url_mock)
        get_basket_mock.return_value = Mock()
        order_generator_mock.return_value.basket_id.return_value = "1"
        data = {
            "transactionId": 20,
            "referenceCode": "1",
        }
        request = self.factory.get(self.url, data=data)

        response = PayUPaymentResponseView.as_view()(request)

        self.assertEqual(status.HTTP_302_FOUND, response.status_code)
        get_receipt_page_url_mock.assert_called_once_with(
            order_number=get_basket_mock().order_number,
            site_configuration=get_basket_mock().site.siteconfiguration,
        )
        order_generator_mock().basket_id.assert_called_once_with(data["referenceCode"])

    @patch.object(PayUPaymentResponseView, "payment_processor")
    @patch("ecommerce_extensions.payment.views.payu.OrderNumberGenerator")
    def test_post_basket_not_found(self, order_generator_mock, _):
        """
        Test post request when the basket is not found.

        Expected behavior:
            - response status code is 400.
            - generator called with the referenceCode value.
        """
        order_generator_mock.return_value.basket_id.return_value = 1
        data = {
            "transaction_id": 20,
            "reference_sale": "1",
        }
        request = self.factory.post(self.url, data=data)

        response = PayUPaymentResponseView.as_view()(request)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        order_generator_mock().basket_id.assert_called_once_with(data["reference_sale"])

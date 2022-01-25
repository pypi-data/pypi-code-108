"""Test file for the views file.

Classes:
    EdnxPaymentProcessorViewTest: EdnxPView tests class.
"""
from importlib import import_module  # pylint: disable=unused-import

from django.test import RequestFactory, TestCase
from django.urls import reverse
from mock import Mock, patch  # pylint: disable=unused-import
from rest_framework import status

from ecommerce_extensions.payment.views.edupay import EdnxPaymentResponseView


class EdnxPaymentProcessorViewTest(TestCase):
    """This class includes the tests for the view EdnxPaymentProcessorViewTest."""

    def setUp(self):
        """
        Setup.
        """
        self.factory = RequestFactory()
        self.url_notify = reverse("edupay:notify")

    @patch.object(EdnxPaymentResponseView, "payment_processor")
    @patch("ecommerce_extensions.payment.views.edupay.OrderNumberGenerator")
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
        request = self.factory.post(self.url_notify, data=data)

        response = EdnxPaymentResponseView.as_view()(request)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        order_generator_mock().basket_id.assert_called_once_with(data["reference_sale"])
